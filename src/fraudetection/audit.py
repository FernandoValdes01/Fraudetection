"""Recalcular métricas con scikit-learn y comprobar las particiones exportadas."""

import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from fraudetection.metrics import METRIC_NAMES
from fraudetection.reporting import load_json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def require_keys(frame, columns, expected, message):
    keys = list(frame.loc[:, columns].itertuples(index=False, name=None))
    require(len(keys) == len(set(keys)) and set(keys) == expected, message)


def audit_results(output):
    output = Path(output)
    protocol = load_json(output / "protocolo.json")
    selected = load_json(output / "seleccion.json")
    exploration = load_json(output / "exploracion.json")
    repetitions = pd.read_csv(output / "prueba_repeticiones.csv")
    summary = pd.read_csv(output / "prueba_resumen.csv")
    cv = pd.read_csv(output / "validacion.csv")
    predictions = pd.read_csv(output / "predicciones.csv.gz")
    require(protocol["status"] == "complete", "Experimentos incompletos")
    require(len(summary) == len(cv) == len(selected["experiments"]) == 8, "Faltan experimentos")
    require(len(repetitions) == 8 * len(protocol["final_seeds"]), "Faltan repeticiones")
    experiments = {
        (model, condition)
        for model in ("knn", "tree", "svm", "forest")
        for condition in ("sin_compensacion", "con_compensacion")
    }
    for frame in (summary, cv, pd.DataFrame(selected["experiments"])):
        require_keys(
            frame,
            ["model", "condition"],
            experiments,
            "Faltan experimentos o existen experimentos duplicados",
        )
    seeds = protocol["final_seeds"]
    require(len(seeds) >= 2 and len(seeds) == len(set(seeds)), "Semillas finales inválidas")
    require_keys(
        repetitions,
        ["model", "condition", "seed"],
        {(model, condition, seed) for model, condition in experiments for seed in seeds},
        "Faltan semillas o existen repeticiones duplicadas",
    )
    fold_scores = pd.read_csv(output / "validacion_pliegues.csv")
    require_keys(
        fold_scores,
        ["model", "condition", "fold"],
        {(model, condition, fold) for model, condition in experiments for fold in range(5)},
        "Faltan pliegues o existen pliegues duplicados",
    )
    expected_columns = {"row_id", "Class"} | {
        f"{model}_{condition}_{seed}" for model, condition in experiments for seed in seeds
    }
    require(set(predictions.columns) == expected_columns, "Columnas de predicciones inconsistentes")
    for experiment in selected["experiments"]:
        model, condition = experiment["model"], experiment["condition"]
        search = pd.read_csv(output / "busquedas" / f"{model}_{condition}.csv")
        require(
            np.isfinite(search[["mean_test_sensitivity", "mean_test_precision"]]).all().all(),
            "Resultados de búsqueda no finitos",
        )
        candidate = max(
            range(len(search)),
            key=lambda i: (
                search.iloc[i].mean_test_sensitivity,
                search.iloc[i].mean_test_precision,
                -i,
            ),
        )
        require(candidate == experiment["candidate_index"], "Candidato elegido incorrectamente")
        params = ast.literal_eval(search.iloc[candidate]["params"])
        row = cv[(cv.model == model) & (cv.condition == condition)].iloc[0]
        require(
            params == experiment["params"] == json.loads(row.params),
            "Los parámetros seleccionados no coinciden con la búsqueda",
        )
        require(
            experiment["balanced"] == (condition == "con_compensacion"),
            "Condición de compensación inconsistente",
        )
        for metric in METRIC_NAMES:
            for statistic in ("mean", "std"):
                np.testing.assert_allclose(
                    row[f"{metric}_{statistic}"],
                    search.iloc[candidate][f"{statistic}_test_{metric}"],
                    atol=1e-14,
                )
    require(predictions.row_id.is_unique, "Se repiten filas en test")
    require(len(predictions) == exploration["test_rows"], "Tamaño de test inconsistente")
    require(
        int(predictions.Class.sum()) == exploration["test_class_counts"]["1"],
        "Cantidad de fraudes inconsistente",
    )
    for _, row in repetitions.iterrows():
        truth = predictions.Class
        prediction = predictions[f"{row['model']}_{row['condition']}_{row['seed']}"]
        require(set(prediction.unique()).issubset({0, 1}), "Predicciones inválidas")
        tn, fp, fn, tp = confusion_matrix(truth, prediction, labels=[0, 1]).ravel()
        expected = {
            "sensitivity": recall_score(truth, prediction),
            "specificity": tn / (tn + fp),
            "precision": precision_score(truth, prediction, zero_division=0),
            "f1": f1_score(truth, prediction, zero_division=0),
            "accuracy": accuracy_score(truth, prediction),
            "fnr": fn / (tp + fn),
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
        }
        for metric, value in expected.items():
            np.testing.assert_allclose(row[metric], value, rtol=1e-12, atol=1e-14)
    for frame, details, ddof in [
        (summary, repetitions, 1),
        (cv, fold_scores, 0),
    ]:
        for _, row in frame.iterrows():
            group = details[
                (details.model == row["model"]) & (details.condition == row["condition"])
            ]
            expected_count = len(protocol["final_seeds"]) if ddof else 5
            require(len(group) == expected_count, "Número de repeticiones o pliegues inválido")
            metrics = (*METRIC_NAMES, "tn", "fp", "fn", "tp") if ddof else METRIC_NAMES
            for metric in metrics:
                np.testing.assert_allclose(row[f"{metric}_mean"], group[metric].mean(), atol=1e-14)
                np.testing.assert_allclose(
                    row[f"{metric}_std"], group[metric].std(ddof=ddof), atol=1e-14
                )
    winner = cv.sort_values(
        ["sensitivity_mean", "precision_mean"], ascending=False, kind="stable"
    ).iloc[0]
    require(
        winner.model == selected["winner"]["model"]
        and winner.condition == selected["winner"]["condition"],
        "Selección de ganador inválida",
    )
    winner_record = next(
        item
        for item in selected["experiments"]
        if item["model"] == winner.model and item["condition"] == winner.condition
    )
    require(selected["winner"] == winner_record, "Parámetros del ganador inconsistentes")
    require(selected["frozen_before_test"] is True, "No se registró la selección previa al test")
    with np.load(output / "particiones.npz") as partitions:
        train, test = partitions["train_positions"], partitions["test_positions"]
        require(
            len(np.unique(partitions["sample_row_ids"])) == exploration["sample_rows"],
            "Hay filas originales duplicadas en la muestra",
        )
        require(not np.intersect1d(train, test).size, "Fuga entre train y test")
        np.testing.assert_array_equal(
            np.sort(np.concatenate((train, test))),
            np.arange(exploration["sample_rows"]),
        )
        np.testing.assert_array_equal(
            partitions["sample_row_ids"][test],
            predictions.row_id.to_numpy(),
        )
        validation_ids = []
        for i in range(5):
            fold_train = partitions[f"fold_{i}_train"]
            fold_valid = partitions[f"fold_{i}_validation"]
            require(not np.intersect1d(fold_train, fold_valid).size, "Fuga dentro de un pliegue")
            np.testing.assert_array_equal(
                np.sort(np.concatenate((fold_train, fold_valid))),
                np.arange(len(train)),
            )
            validation_ids.extend(fold_valid)
        np.testing.assert_array_equal(np.sort(validation_ids), np.arange(len(train)))
    return {
        "experiments": 8,
        "repetitions": len(repetitions),
        "test_rows": len(predictions),
        "metrics_recomputed": True,
        "partitions_disjoint": True,
    }
