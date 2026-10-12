"""Búsqueda CV y evaluación final de los ocho experimentos del proyecto."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from imblearn.pipeline import Pipeline
from imblearn.under_sampling import RandomUnderSampler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

from fraudetection.config import (
    CV_FOLDS,
    FEATURE_SELECTION_K,
    FINAL_SEEDS,
    PREDICTION_BATCH_SIZE,
    RANDOM_SEED,
    SEARCH_SAMPLE_SIZE,
    UNDERSAMPLE_RATIO,
)
from fraudetection.data import (
    inspect_dataset,
    load_dataset,
    remove_exact_duplicates,
    split_dataset,
)
from fraudetection.forest import BootstrapRandomForest

MODEL_LABELS = {
    "knn": "k-NN",
    "tree": "Árbol de decisión",
    "svm": "SVM lineal",
    "forest": "Random Forest propio",
}
MODEL_ORDER = tuple(MODEL_LABELS)
COMPENSATION_ORDER = (False, True)
METRIC_NAMES = ("sensitivity", "specificity", "precision", "f1", "accuracy", "fnr")

PARAMETER_GRIDS = {
    "knn": {"model__n_neighbors": [3, 5, 7]},
    "tree": {
        "model__max_depth": [5, 10, None],
        "model__min_samples_leaf": [1, 5],
    },
    "svm": {"model__C": [0.1, 1.0, 10.0]},
    "forest": {
        "model__n_estimators": [11, 21],
        "model__max_depth": [6, 12],
    },
}


def make_classifier(model_name: str, seed: int):
    if model_name == "knn":
        return KNeighborsClassifier(n_neighbors=5, weights="distance", n_jobs=4)
    if model_name == "tree":
        return DecisionTreeClassifier(random_state=seed)
    if model_name == "svm":
        return LinearSVC(C=1.0, dual="auto", max_iter=10_000, random_state=seed)
    if model_name == "forest":
        return BootstrapRandomForest(random_state=seed)
    raise ValueError(f"Clasificador desconocido: {model_name}")


def make_pipeline(model_name: str, compensate: bool, seed: int, parameters=None):
    scale = "passthrough" if model_name in {"tree", "forest"} else StandardScaler()
    sampler = (
        RandomUnderSampler(sampling_strategy=UNDERSAMPLE_RATIO, random_state=seed)
        if compensate
        else "passthrough"
    )
    selector = SelectKBest(
        score_func=f_classif,
        k=FEATURE_SELECTION_K,
    )
    estimator = make_classifier(model_name, seed)
    if parameters:
        estimator.set_params(**parameters)
    return Pipeline(
        [
            ("scale", scale),
            ("sampler", sampler),
            ("select", selector),
            ("model", estimator),
        ]
    )


def choose_by_sensitivity_then_precision(cv_results: dict[str, np.ndarray]) -> int:
    """Elige sensibilidad media y desempata por precisión media de fraude."""
    sensitivity = np.asarray(cv_results["mean_test_sensitivity"], dtype=float)
    precision = np.asarray(cv_results["mean_test_precision"], dtype=float)
    best_sensitivity = np.nanmax(sensitivity)
    candidates = np.flatnonzero(sensitivity == best_sensitivity)
    best_precision = np.nanmax(precision[candidates])
    return int(candidates[np.flatnonzero(precision[candidates] == best_precision)[0]])


def take_search_sample(X: pd.DataFrame, y: pd.Series, size: int):
    if size < 10_000:
        raise ValueError("La búsqueda debe utilizar al menos 10 000 filas")
    if size > len(y):
        raise ValueError(f"La muestra solicitada ({size}) excede el entrenamiento ({len(y)})")
    split = train_test_split(
        X,
        y,
        train_size=size,
        stratify=y,
        random_state=RANDOM_SEED,
    )
    return split[0], split[2]


def run_searches(X_search, y_search, output_dir: Path) -> pd.DataFrame:
    splits = list(
        StratifiedKFold(
            n_splits=CV_FOLDS,
            shuffle=True,
            random_state=RANDOM_SEED,
        ).split(X_search, y_search)
    )
    scorers = {
        "sensitivity": make_scorer(recall_score, pos_label=1, zero_division=0),
        "precision": make_scorer(precision_score, pos_label=1, zero_division=0),
    }
    rows = []

    for model_name in MODEL_ORDER:
        for compensate in COMPENSATION_ORDER:
            condition = "submuestreo" if compensate else "sin_compensacion"
            experiment = f"{model_name}_{condition}"
            print(f"CV {experiment}: iniciando búsqueda", flush=True)
            search = GridSearchCV(
                estimator=make_pipeline(model_name, compensate, RANDOM_SEED),
                param_grid=PARAMETER_GRIDS[model_name],
                scoring=scorers,
                refit=choose_by_sensitivity_then_precision,
                cv=splits,
                n_jobs=1,
                error_score="raise",
                return_train_score=False,
            )
            search.fit(X_search, y_search)
            index = search.best_index_
            model_parameters = {
                name.removeprefix("model__"): value
                for name, value in search.cv_results_["params"][index].items()
            }
            rows.append(
                {
                    "experiment": experiment,
                    "model": model_name,
                    "model_label": MODEL_LABELS[model_name],
                    "compensation": "submuestreo 1:10" if compensate else "ninguna",
                    "compensated": compensate,
                    "search_rows": len(X_search),
                    "cv_folds": CV_FOLDS,
                    "best_parameters": json.dumps(model_parameters, ensure_ascii=False),
                    "cv_sensitivity_mean": float(
                        search.cv_results_["mean_test_sensitivity"][index]
                    ),
                    "cv_sensitivity_std": float(search.cv_results_["std_test_sensitivity"][index]),
                    "cv_precision_mean": float(search.cv_results_["mean_test_precision"][index]),
                }
            )
            current = pd.DataFrame(rows)
            current["selected_by_cv"] = False
            best_index = max(
                current.index,
                key=lambda row_index: (
                    current.loc[row_index, "cv_sensitivity_mean"],
                    current.loc[row_index, "cv_precision_mean"],
                ),
            )
            current.loc[best_index, "selected_by_cv"] = True
            current.to_csv(output_dir / "cv_resumen.csv", index=False)
            print(
                f"CV {experiment}: sensibilidad {rows[-1]['cv_sensitivity_mean']:.3f} "
                f"± {rows[-1]['cv_sensitivity_std']:.3f}; "
                f"precisión {rows[-1]['cv_precision_mean']:.3f}; "
                f"parámetros {model_parameters}",
                flush=True,
            )

    results = pd.DataFrame(rows)
    best_index = max(
        results.index,
        key=lambda index: (
            results.loc[index, "cv_sensitivity_mean"],
            results.loc[index, "cv_precision_mean"],
        ),
    )
    results["selected_by_cv"] = False
    results.loc[best_index, "selected_by_cv"] = True
    results.to_csv(output_dir / "cv_resumen.csv", index=False)
    return results


def predict_in_batches(estimator, X: pd.DataFrame) -> np.ndarray:
    predictions = []
    for start in range(0, len(X), PREDICTION_BATCH_SIZE):
        stop = start + PREDICTION_BATCH_SIZE
        predictions.append(estimator.predict(X.iloc[start:stop]))
    return np.concatenate(predictions)


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float | int]:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sensitivity = recall_score(y_true, y_pred, pos_label=1, zero_division=0)
    specificity = tn / (tn + fp) if tn + fp else 0.0
    return {
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "precision": float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "fnr": float(1.0 - sensitivity),
    }


def run_final_evaluations(
    cv_results: pd.DataFrame,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    output_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], dict[str, list[str]]]:
    rows = []
    feature_rows = []
    primary_predictions = {}
    feature_sets = {}

    for result in cv_results.to_dict(orient="records"):
        model_name = result["model"]
        compensate = bool(result["compensated"])
        parameters = json.loads(result["best_parameters"])
        experiment = result["experiment"]
        print(f"Prueba {experiment}: reajustando con todo el entrenamiento", flush=True)

        deterministic_knn = model_name == "knn" and not compensate
        run_seeds = FINAL_SEEDS[:1] if deterministic_knn else FINAL_SEEDS
        for repeat, seed in enumerate(run_seeds, start=1):
            pipeline = make_pipeline(model_name, compensate, seed, parameters)
            pipeline.fit(X_train, y_train)
            predictions = predict_in_batches(pipeline, X_test)
            rows.append(
                {
                    "experiment": experiment,
                    "model": model_name,
                    "model_label": MODEL_LABELS[model_name],
                    "compensation": result["compensation"],
                    "repeat": repeat,
                    "seed": seed,
                    **calculate_metrics(y_test.to_numpy(), predictions),
                }
            )
            selected = pipeline.named_steps["select"]
            feature_names = list(X_train.columns[selected.get_support()])
            feature_rows.append(
                {
                    "experiment": experiment,
                    "repeat": repeat,
                    "seed": seed,
                    "selected_features": ", ".join(feature_names),
                }
            )
            if seed == FINAL_SEEDS[0]:
                primary_predictions[experiment] = predictions
                feature_sets[experiment] = feature_names
            print(
                f"Prueba {experiment}, repetición {repeat}: "
                f"sensibilidad {rows[-1]['sensitivity']:.3f}, "
                f"FNR {rows[-1]['fnr']:.3f}, precisión {rows[-1]['precision']:.3f}",
                flush=True,
            )

        if deterministic_knn:
            base = rows[-1].copy()
            for repeat, seed in enumerate(FINAL_SEEDS[1:], start=2):
                rows.append({**base, "repeat": repeat, "seed": seed})
            base_features = feature_rows[-1].copy()
            for repeat, seed in enumerate(FINAL_SEEDS[1:], start=2):
                feature_rows.append({**base_features, "repeat": repeat, "seed": seed})

        pd.DataFrame(rows).to_csv(output_dir / "test_repeticiones.csv", index=False)
        pd.DataFrame(feature_rows).to_csv(
            output_dir / "caracteristicas_seleccionadas.csv", index=False
        )

    repetitions = pd.DataFrame(rows)
    summary_rows = []
    for experiment, group in repetitions.groupby("experiment", sort=False):
        summary = {
            "experiment": experiment,
            "model": group.iloc[0]["model"],
            "model_label": group.iloc[0]["model_label"],
            "compensation": group.iloc[0]["compensation"],
            "compensated": group.iloc[0]["compensation"] != "ninguna",
            "test_repeats": len(group),
        }
        for metric in METRIC_NAMES:
            summary[f"{metric}_mean"] = group[metric].mean()
            summary[f"{metric}_std"] = group[metric].std(ddof=1) if len(group) > 1 else 0.0
        for count in ("tn", "fp", "fn", "tp"):
            summary[f"{count}_mean"] = group[count].mean()
            summary[f"{count}_std"] = group[count].std(ddof=1) if len(group) > 1 else 0.0
        summary_rows.append(summary)

    summary = pd.DataFrame(summary_rows).merge(
        cv_results[
            [
                "experiment",
                "best_parameters",
                "cv_sensitivity_mean",
                "cv_sensitivity_std",
                "cv_precision_mean",
                "selected_by_cv",
            ]
        ],
        on="experiment",
        how="left",
    )
    summary.to_csv(output_dir / "test_resumen.csv", index=False)
    repetitions.to_csv(output_dir / "test_repeticiones.csv", index=False)
    pd.DataFrame(feature_rows).to_csv(output_dir / "caracteristicas_seleccionadas.csv", index=False)

    chosen_experiment = cv_results.loc[cv_results["selected_by_cv"], "experiment"].iloc[0]
    pd.DataFrame(
        {
            "dataset_index": X_test.index.to_numpy(),
            "class_true": y_test.to_numpy(),
            "class_predicted": primary_predictions[chosen_experiment],
        }
    ).to_csv(output_dir / "predicciones_configuracion_cv.csv", index=False)
    (output_dir / "seleccion_cv.json").write_text(
        json.dumps(
            {
                "selected_experiment": chosen_experiment,
                "selected_features_seed_42": feature_sets[chosen_experiment],
                "selection_criterion": "sensibilidad media CV; precisión media como desempate",
                "test_seed_for_confusion_matrix": FINAL_SEEDS[0],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    return repetitions, summary, primary_predictions, feature_sets


def save_plots(
    raw_report,
    clean_report,
    cv_results: pd.DataFrame,
    test_summary: pd.DataFrame,
    y_test: pd.Series,
    primary_predictions: dict[str, np.ndarray],
    output_dir: Path,
) -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#ffffff",
            "axes.facecolor": "#ffffff",
            "axes.edgecolor": "#cbd5e1",
            "axes.labelcolor": "#475569",
            "text.color": "#263238",
            "xtick.color": "#475569",
            "ytick.color": "#475569",
            "grid.color": "#dbe3eb",
        }
    )
    blue = "#2e6f9e"
    gray = "#a8b4c0"
    plot_dir = output_dir / "graficos"
    plot_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for axis, report, title in zip(
        axes,
        (raw_report, clean_report),
        ("CSV original", "Después de eliminar duplicados"),
        strict=False,
    ):
        axis.bar(
            ["Legítimas", "Fraudes"],
            [report.class_counts[0], report.class_counts[1]],
            color=[gray, blue],
        )
        axis.set_title(title)
        axis.set_ylabel("Transacciones")
        axis.ticklabel_format(axis="y", style="plain")
        for index, value in enumerate((report.class_counts[0], report.class_counts[1])):
            axis.text(
                index,
                value,
                f"{value:,}".replace(",", "."),
                ha="center",
                va="bottom",
                fontsize=9,
            )
    fig.suptitle("El desbalance se conserva en los datos de evaluación")
    fig.savefig(plot_dir / "distribucion_clases.png", dpi=180)
    plt.close(fig)

    short_model_labels = {"knn": "k-NN", "tree": "Árbol", "svm": "SVM", "forest": "Bosque"}
    labels = [
        f"{short_model_labels[row.model]}\n{'subm.' if row.compensated else 'sin comp.'}"
        for row in cv_results.itertuples()
    ]
    positions = np.arange(len(cv_results))
    fig, axis = plt.subplots(figsize=(11, 5), constrained_layout=True)
    axis.bar(
        positions,
        cv_results["cv_sensitivity_mean"],
        yerr=cv_results["cv_sensitivity_std"],
        capsize=4,
        color=[blue if row.compensated else gray for row in cv_results.itertuples()],
    )
    axis.set_xticks(positions, labels, fontsize=9)
    axis.set_ylim(0, 1.05)
    axis.set_ylabel("Sensibilidad media ± DE")
    axis.set_title("Validación cruzada: detección de fraude")
    axis.grid(axis="y", alpha=0.2)
    fig.savefig(plot_dir / "sensibilidad_validacion.png", dpi=180)
    plt.close(fig)

    metric_titles = {
        "sensitivity": "Sensibilidad",
        "specificity": "Especificidad",
        "precision": "Precisión",
        "f1": "F1-score",
        "accuracy": "Exactitud",
        "fnr": "FNR",
    }
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True)
    for axis, metric in zip(axes.flat, METRIC_NAMES, strict=False):
        axis.bar(
            positions,
            test_summary[f"{metric}_mean"],
            yerr=test_summary[f"{metric}_std"],
            capsize=3,
            color=[blue if row.compensated else gray for row in test_summary.itertuples()],
        )
        axis.set_title(metric_titles[metric])
        axis.set_xticks(positions, labels, fontsize=7)
        axis.grid(axis="y", alpha=0.2)
        axis.set_ylim(0, 1.05)
    fig.suptitle("Prueba reservada: media y desviación estándar entre semillas")
    fig.savefig(plot_dir / "metricas_prueba.png", dpi=180)
    plt.close(fig)

    for filename, metrics, titles in (
        (
            "sensibilidad_fnr_prueba.png",
            ("sensitivity", "fnr"),
            ("Sensibilidad", "Tasa de falsos negativos"),
        ),
        (
            "precision_especificidad_prueba.png",
            ("precision", "specificity"),
            ("Precisión", "Especificidad"),
        ),
    ):
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), constrained_layout=True)
        for axis, metric, title in zip(axes, metrics, titles, strict=False):
            axis.bar(
                positions,
                test_summary[f"{metric}_mean"],
                yerr=test_summary[f"{metric}_std"],
                capsize=3,
                color=[blue if row.compensated else gray for row in test_summary.itertuples()],
            )
            axis.set_title(title)
            axis.set_xticks(positions, labels, fontsize=9)
            axis.grid(axis="y", alpha=0.2)
            axis.set_ylim(0, 1.05)
            if metric == "specificity":
                axis.set_ylim(0.99, 1.001)
                axis.set_ylabel("Zoom 99–100 %")
        fig.savefig(plot_dir / filename, dpi=180)
        plt.close(fig)

    selected_row = cv_results.loc[cv_results["selected_by_cv"]].iloc[0]
    selected = selected_row["experiment"]
    tn, fp, fn, tp = confusion_matrix(y_test, primary_predictions[selected], labels=[0, 1]).ravel()
    matrix = np.array([[tn, fp], [fn, tp]])
    fig, axis = plt.subplots(figsize=(5, 4), constrained_layout=True)
    axis.imshow(matrix, cmap="Blues")
    axis.set_xticks([0, 1], ["Predice legítima", "Predice fraude"])
    axis.set_yticks([0, 1], ["Real legítima", "Real fraude"])
    axis.set_title(f"Matriz de confusión, semilla {FINAL_SEEDS[0]}")
    for (row, col), value in np.ndenumerate(matrix):
        text_color = "#ffffff" if value > matrix.max() * 0.35 else "#102030"
        axis.text(
            col,
            row,
            f"{value:,}".replace(",", "."),
            ha="center",
            va="center",
            fontsize=13,
            color=text_color,
        )
    fig.savefig(plot_dir / "matriz_confusion_seleccion_cv.png", dpi=180)
    plt.close(fig)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Busca hiperparámetros y evalúa los ocho experimentos de fraude"
    )
    parser.add_argument("--dataset", type=Path, default=Path("data/raw/creditcard.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("resultados"))
    parser.add_argument("--search-sample-size", type=int, default=SEARCH_SAMPLE_SIZE)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    frame = load_dataset(args.dataset)
    raw_report = inspect_dataset(frame)
    clean_frame = remove_exact_duplicates(frame)
    clean_report = inspect_dataset(clean_frame)
    X_train, X_test, y_train, y_test = split_dataset(clean_frame)
    X_search, y_search = take_search_sample(X_train, y_train, args.search_sample_size)

    print(
        f"Búsqueda: {len(X_search):,} filas estratificadas del entrenamiento; "
        f"partición de prueba reservada: {len(X_test):,} filas.",
        flush=True,
    )
    cv_results = run_searches(X_search, y_search, args.output_dir)
    _, test_summary, predictions, _ = run_final_evaluations(
        cv_results, X_train, y_train, X_test, y_test, args.output_dir
    )
    save_plots(
        raw_report,
        clean_report,
        cv_results,
        test_summary,
        y_test,
        predictions,
        args.output_dir,
    )
    metadata = {
        "dataset": str(args.dataset),
        "dataset_sha256": sha256(args.dataset),
        "rows_raw": raw_report.records,
        "duplicates_removed": raw_report.duplicate_rows,
        "rows_after_cleaning": clean_report.records,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "search_sample_rows": len(X_search),
        "search_sample_fraud": int(y_search.sum()),
        "cv_folds": CV_FOLDS,
        "cv_seed": RANDOM_SEED,
        "final_seeds": list(FINAL_SEEDS),
        "feature_selection": f"ANOVA F-test, top {FEATURE_SELECTION_K}",
        "compensation": f"RandomUnderSampler ratio 1:{int(1 / UNDERSAMPLE_RATIO)}",
        "test_repetitions": len(FINAL_SEEDS),
    }
    (args.output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
    )
    print("Resultados guardados en", args.output_dir, flush=True)
    print("Configuración elegida por validación:")
    print(
        cv_results.loc[
            cv_results["selected_by_cv"],
            [
                "experiment",
                "best_parameters",
                "cv_sensitivity_mean",
                "cv_sensitivity_std",
                "cv_precision_mean",
            ],
        ].to_string(index=False)
    )
    print("Resumen de prueba:")
    print(
        test_summary[
            [
                "experiment",
                "sensitivity_mean",
                "sensitivity_std",
                "specificity_mean",
                "precision_mean",
                "f1_mean",
                "accuracy_mean",
                "fnr_mean",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
