import json
import shutil
from pathlib import Path

import pandas as pd
import pytest
from imblearn.pipeline import Pipeline
from sklearn.datasets import make_classification

from fraudetection.config import FINAL_SEEDS
from fraudetection.data import FEATURE_COLUMNS
from fraudetection.experiments import run_final_evaluations
from fraudetection.reproduction.audit import audit_results


@pytest.mark.skipif(
    not Path("resultados/ejecucion/protocolo.json").exists(),
    reason="No hay resultados reales locales",
)
def test_saved_real_experiments_are_internally_consistent():
    result = audit_results("resultados/ejecucion")
    assert result["experiments"] == 8
    assert result["repetitions"] == 24


@pytest.fixture
def copied_results(tmp_path):
    source = Path("resultados/ejecucion")
    if not (source / "protocolo.json").exists():
        pytest.skip("No hay resultados reales locales")
    shutil.copytree(source, tmp_path / "results", ignore=shutil.ignore_patterns("*.joblib"))
    return tmp_path / "results"


def test_audit_rejects_duplicate_deterministic_seed(copied_results):
    path = copied_results / "prueba_repeticiones.csv"
    frame = pd.read_csv(path)
    # k-NN sin compensación produce métricas idénticas para las tres semillas.
    # Duplicar la 42 y omitir la 43 preserva medias y desviaciones, pero es inválido.
    frame.loc[1, "seed"] = frame.loc[0, "seed"]
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="semillas|duplicad"):
        audit_results(copied_results)


def test_audit_rejects_missing_experiment_replaced_with_duplicate(copied_results):
    path = copied_results / "seleccion.json"
    selection = json.loads(path.read_text())
    selection["experiments"][-1] = selection["experiments"][0]
    path.write_text(json.dumps(selection))
    with pytest.raises(ValueError, match="experimentos|duplicad"):
        audit_results(copied_results)


def test_audit_checks_selected_hyperparameters_against_search(copied_results):
    path = copied_results / "seleccion.json"
    selection = json.loads(path.read_text())
    selection["experiments"][0]["params"]["model__n_neighbors"] = 999
    path.write_text(json.dumps(selection))
    with pytest.raises(ValueError, match="parámetros"):
        audit_results(copied_results)


def test_uncompensated_knn_fits_once_for_each_final_seed(tmp_path, monkeypatch):
    X, y = make_classification(
        n_samples=80,
        n_features=len(FEATURE_COLUMNS),
        n_informative=8,
        n_redundant=2,
        weights=[0.8, 0.2],
        random_state=17,
    )
    X_train = pd.DataFrame(X[:60], columns=FEATURE_COLUMNS)
    y_train = pd.Series(y[:60])
    X_test = pd.DataFrame(X[60:], columns=FEATURE_COLUMNS)
    y_test = pd.Series(y[60:])
    cv_results = pd.DataFrame(
        [
            {
                "experiment": "knn_sin_compensacion",
                "model": "knn",
                "compensation": "ninguna",
                "compensated": False,
                "best_parameters": "{}",
                "cv_sensitivity_mean": 0.5,
                "cv_sensitivity_std": 0.1,
                "cv_precision_mean": 0.5,
                "selected_by_cv": True,
            }
        ]
    )
    fit_calls = []
    original_fit = Pipeline.fit

    def count_fit(pipeline, *args, **kwargs):
        fit_calls.append(pipeline)
        return original_fit(pipeline, *args, **kwargs)

    monkeypatch.setattr(Pipeline, "fit", count_fit)
    repetitions, _, _, _ = run_final_evaluations(
        cv_results, X_train, y_train, X_test, y_test, tmp_path
    )

    assert len(fit_calls) == len(FINAL_SEEDS) == 5
    assert repetitions["seed"].tolist() == list(FINAL_SEEDS)
    assert repetitions["repeat"].tolist() == [1, 2, 3, 4, 5]
    saved_features = pd.read_csv(tmp_path / "caracteristicas_seleccionadas.csv")
    assert saved_features["seed"].tolist() == list(FINAL_SEEDS)
