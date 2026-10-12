"""Búsqueda completa en entrenamiento antes de abrir el test reservado."""

import importlib.metadata
import json
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from imblearn.pipeline import Pipeline
from imblearn.under_sampling import RandomUnderSampler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

from fraudetection.reproduction.config import FEATURES, FINAL_SEEDS, RANDOM_SEED, SELECTED_FEATURES
from fraudetection.reproduction.data import class_counts, prepare_data
from fraudetection.reproduction.forest import OwnRandomForestClassifier
from fraudetection.reproduction.metrics import METRIC_NAMES, best_candidate, binary_metrics, scoring

MODEL_LABELS = {"knn": "k-NN", "tree": "Árbol", "svm": "SVM", "forest": "Bosque propio"}


def model_specs(seed=RANDOM_SEED):
    """Dos candidatos por modelo; todos prefijados antes de evaluar.

    Se comparan vecindades pequeña/mayor, profundidad limitada/libre y
    regularización SVM moderada/menor. El bosque fija 31 árboles impares
    y sqrt variables por división. El resto se mantiene constante.
    """
    return {
        "knn": (KNeighborsClassifier(n_jobs=1), {"model__n_neighbors": [3, 7]}),
        "tree": (
            DecisionTreeClassifier(min_samples_leaf=2, random_state=seed),
            {"model__max_depth": [6, None]},
        ),
        "svm": (
            SVC(kernel="rbf", gamma="scale", cache_size=512, random_state=seed),
            {"model__C": [1.0, 10.0]},
        ),
        "forest": (
            OwnRandomForestClassifier(n_estimators=31, min_samples_leaf=2, random_state=seed),
            {"model__max_depth": [8, None]},
        ),
    }


def make_pipeline(model_name, balanced, seed=RANDOM_SEED):
    model, grid = model_specs(seed)[model_name]
    pipeline = Pipeline(
        [
            ("scale", StandardScaler() if model_name in ("knn", "svm") else "passthrough"),
            # ANOVA F selecciona diferencias marginales de medias. No aprende sobre test.
            ("select", SelectKBest(score_func=f_classif, k=SELECTED_FEATURES)),
            # 0.1 = un fraude por diez legítimas. Solo elimina ejemplos mayoritarios.
            (
                "balance",
                RandomUnderSampler(sampling_strategy=0.1, random_state=seed)
                if balanced
                else "passthrough",
            ),
            ("model", model),
        ]
    )
    return pipeline, grid


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def run_experiments(dataset, output, sample_size=100_000, jobs=2, final_seeds=FINAL_SEEDS):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if len(final_seeds) < 2 or len(set(final_seeds)) != len(final_seeds):
        raise ValueError("Se requieren al menos dos semillas finales distintas.")
    if (output / "protocolo.json").exists():
        raise FileExistsError("El directorio ya contiene una ejecución. Use otro --output.")
    started = time.monotonic()
    protocol = {
        "status": "running",
        "started_utc": datetime.now(UTC).isoformat(),
        "sample_size_requested": sample_size,
        "random_seed": RANDOM_SEED,
        "test_size": 0.3,
        "cv_folds": 5,
        "cv_shuffle": True,
        "final_seeds": list(final_seeds),
        "selection": "SelectKBest ANOVA F, k=20, ajustado dentro de cada pliegue",
        "compensation": "RandomUnderSampler, ratio minoritaria/mayoritaria=0.1",
        "selection_rule": "Sensibilidad media, precisión media en empate exacto, orden estable",
        "cv_std_ddof": 0,
        "test_std_ddof": 1,
        "test_protocol": "Tres reajustes prefijados, mismo test; ninguna selección por test",
        "python": platform.python_version(),
        "versions": {
            name: importlib.metadata.version(name)
            for name in (
                "fraudetection",
                "numpy",
                "pandas",
                "scikit-learn",
                "imbalanced-learn",
                "matplotlib",
            )
        },
        "jobs": jobs,
    }
    write_json(output / "protocolo.json", protocol)
    X_train, X_test, y_train, y_test, test_ids, folds, exploration = prepare_data(
        dataset,
        sample_size,
        output,
    )
    selected, cv_rows, cv_fold_rows, sampling_rows = [], [], [], []
    (output / "busquedas").mkdir()
    # Primera fase: buscar TODAS las configuraciones sin evaluar X_test.
    for name in MODEL_LABELS:
        for balanced in (False, True):
            condition = "con_compensacion" if balanced else "sin_compensacion"
            print(f"Validación: {name} / {condition}", flush=True)
            pipeline, grid = make_pipeline(name, balanced)
            search = GridSearchCV(
                pipeline,
                grid,
                scoring=scoring(),
                cv=folds,
                refit=False,
                n_jobs=jobs,
                error_score="raise",
                return_train_score=False,
            )
            with joblib.parallel_backend("loky", inner_max_num_threads=1):
                search.fit(X_train, y_train)
            index = best_candidate(search.cv_results_)
            params = search.cv_results_["params"][index]
            result = {
                "model": name,
                "condition": condition,
                "balanced": balanced,
                "params": params,
                "candidate_index": index,
            }
            cv_row = {"model": name, "condition": condition, "params": json.dumps(params)}
            for metric in METRIC_NAMES:
                cv_row[f"{metric}_mean"] = float(search.cv_results_[f"mean_test_{metric}"][index])
                cv_row[f"{metric}_std"] = float(search.cv_results_[f"std_test_{metric}"][index])
            for fold_id, (train_ids, valid_ids) in enumerate(folds):
                cv_fold_rows.append(
                    {
                        "model": name,
                        "condition": condition,
                        "fold": fold_id,
                        **{
                            m: float(search.cv_results_[f"split{fold_id}_test_{m}"][index])
                            for m in METRIC_NAMES
                        },
                    }
                )
                before = class_counts(y_train[train_ids])
                after = before.copy()
                if balanced:
                    _, balanced_y = RandomUnderSampler(
                        sampling_strategy=0.1,
                        random_state=RANDOM_SEED,
                    ).fit_resample(X_train[train_ids], y_train[train_ids])
                    after = class_counts(balanced_y)
                sampling_rows.append(
                    {
                        "model": name,
                        "condition": condition,
                        "fold": fold_id,
                        "train_rows": len(train_ids),
                        "validation_rows": len(valid_ids),
                        "before_0": before["0"],
                        "before_1": before["1"],
                        "after_0": after["0"],
                        "after_1": after["1"],
                    }
                )
            pd.DataFrame(search.cv_results_).to_csv(
                output / "busquedas" / f"{name}_{condition}.csv",
                index=False,
            )
            cv_rows.append(cv_row)
            selected.append(result)
    cv = pd.DataFrame(cv_rows)
    cv.to_csv(output / "validacion.csv", index=False)
    pd.DataFrame(cv_fold_rows).to_csv(output / "validacion_pliegues.csv", index=False)
    pd.DataFrame(sampling_rows).to_csv(output / "remuestreo_pliegues.csv", index=False)
    winner_index = max(
        range(len(cv_rows)),
        key=lambda i: (
            cv_rows[i]["sensitivity_mean"],
            cv_rows[i]["precision_mean"],
            -i,
        ),
    )
    write_json(
        output / "seleccion.json",
        {
            "experiments": selected,
            "winner": selected[winner_index],
            "frozen_before_test": True,
        },
    )
    # Segunda fase: configuraciones congeladas; no cambiar grillas ni umbrales.
    test_rows, feature_rows, forest_diagnostics = [], [], []
    predictions = pd.DataFrame({"row_id": test_ids, "Class": y_test})
    for experiment_index, experiment in enumerate(selected):
        name, balanced = experiment["model"], experiment["balanced"]
        condition = experiment["condition"]
        for seed in final_seeds:
            print(f"Prueba final: {name} / {condition} / semilla {seed}", flush=True)
            pipeline, _ = make_pipeline(name, balanced, seed)
            pipeline.set_params(**experiment["params"])
            with threadpool_limits(limits=1):
                pipeline.fit(X_train, y_train)
                prediction = pipeline.predict(X_test)
            row = {
                "model": name,
                "condition": condition,
                "seed": seed,
                **binary_metrics(y_test, prediction),
            }
            test_rows.append(row)
            predictions[f"{name}_{condition}_{seed}"] = prediction
            support = pipeline.named_steps["select"].get_support()
            features = np.asarray(FEATURES)[support].tolist()
            sampler = pipeline.named_steps["balance"]
            after = (
                class_counts(y_train[sampler.sample_indices_])
                if balanced
                else class_counts(y_train)
            )
            feature_rows.append(
                {
                    "model": name,
                    "condition": condition,
                    "seed": seed,
                    "selected_features": features,
                    "before": class_counts(y_train),
                    "after": after,
                }
            )
            if name == "forest":
                forest = pipeline.named_steps["model"]
                forest_diagnostics.append(
                    {
                        "condition": condition,
                        "seed": seed,
                        "bootstrap_size": forest.bootstrap_size_,
                        "tree_seeds": forest.tree_seeds_,
                        "unique_counts": forest.bootstrap_unique_counts_,
                    }
                )
            if experiment_index == winner_index and seed == final_seeds[0]:
                joblib.dump(pipeline, output / "modelo_elegido.joblib")
    test = pd.DataFrame(test_rows)
    test.to_csv(output / "prueba_repeticiones.csv", index=False)
    summary_rows = []
    for (name, condition), group in test.groupby(["model", "condition"], sort=False):
        summary_row = {"model": name, "condition": condition, "repetitions": len(group)}
        for metric in (*METRIC_NAMES, "tn", "fp", "fn", "tp"):
            summary_row[f"{metric}_mean"] = float(group[metric].mean())
            summary_row[f"{metric}_std"] = float(group[metric].std(ddof=1))
        summary_rows.append(summary_row)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(output / "prueba_resumen.csv", index=False)
    predictions.to_csv(output / "predicciones.csv.gz", index=False, compression="gzip")
    write_json(output / "caracteristicas.json", feature_rows)
    write_json(output / "bosque_diagnostico.json", forest_diagnostics)
    baselines = {
        "always_legitimate": binary_metrics(y_test, np.zeros_like(y_test)),
        "always_fraud": binary_metrics(y_test, np.ones_like(y_test)),
    }
    write_json(output / "referencias_triviales.json", baselines)
    protocol.update(
        status="complete",
        elapsed_seconds=time.monotonic() - started,
        dataset_sha256=exploration["dataset_sha256"],
    )
    write_json(output / "protocolo.json", protocol)
    return output
