import json

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from fraudetection.reproduction.config import FEATURES
from fraudetection.reproduction.data import prepare_data, validate_frame
from fraudetection.reproduction.experiments import make_pipeline
from fraudetection.reproduction.metrics import best_candidate, binary_metrics, scoring


def test_metrics_hand_calculated_and_tie_break():
    metrics = binary_metrics([0, 0, 0, 1, 1], [0, 0, 1, 0, 1])
    assert metrics == {
        "sensitivity": 0.5,
        "specificity": 2 / 3,
        "precision": 0.5,
        "f1": 0.5,
        "accuracy": 0.6,
        "fnr": 0.5,
        "tn": 2,
        "fp": 1,
        "fn": 1,
        "tp": 1,
    }
    results = {
        "mean_test_sensitivity": [0.8, 0.9, 0.9, 0.9],
        "mean_test_precision": [1.0, 0.1, 0.4, 0.4],
    }
    assert best_candidate(results) == 2
    assert binary_metrics([0, 1], [0, 0])["precision"] == 0


def test_partition_deduplication_and_saved_folds(tmp_path):
    X, y = make_classification(
        n_samples=10_000, n_features=30, weights=[0.98, 0.02], random_state=9
    )
    frame = pd.DataFrame(X, columns=FEATURES).assign(Class=y)
    frame = pd.concat([frame, frame.iloc[:20]], ignore_index=True)
    csv = tmp_path / "data.csv"
    frame.to_csv(csv, index=False)
    train_X, test_X, train_y, test_y, _, folds, info = prepare_data(csv, 10_000, tmp_path)
    assert info["duplicate_rows_removed"] == 20
    assert len(train_y) == 7000 and len(test_y) == 3000
    assert train_X.shape[1] == test_X.shape[1] == 30
    saved = np.load(tmp_path / "particiones.npz")
    assert not set(saved["train_positions"]) & set(saved["test_positions"])
    all_validation = []
    for i, (train, valid) in enumerate(folds):
        assert not set(train) & set(valid)
        np.testing.assert_array_equal(valid, saved[f"fold_{i}_validation"])
        assert set(train_y[valid]) == {0, 1}
        all_validation.extend(valid)
    assert sorted(all_validation) == list(range(len(train_y)))
    assert json.loads((tmp_path / "exploracion.json").read_text())["raw_rows"] == 10_020


@pytest.mark.parametrize("name", ["knn", "tree", "svm", "forest"])
@pytest.mark.parametrize("balanced", [False, True])
def test_all_eight_pipelines_search_and_predict_without_resampling_validation(name, balanced):
    X, y = make_classification(n_samples=300, n_features=30, weights=[0.95, 0.05], random_state=3)
    # Centinela: los valores de test no deben modificar el escalador ajustado.
    pipeline, grid = make_pipeline(name, balanced)
    if name == "forest":
        pipeline.set_params(model__n_estimators=3)
    folds = list(StratifiedKFold(5, shuffle=True, random_state=42).split(X[:240], y[:240]))
    search = GridSearchCV(
        pipeline, grid, scoring=scoring(), cv=folds, refit=best_candidate, error_score="raise"
    )
    search.fit(X[:240], y[:240])
    best = search.best_estimator_
    assert len(best.predict(X[240:] + 1000)) == 60
    assert best.named_steps["select"].get_support().sum() == 20
    if name in ("knn", "svm"):
        np.testing.assert_allclose(best.named_steps["scale"].mean_, X[:240].mean(axis=0))
    if balanced:
        sampled_y = y[:240][best.named_steps["balance"].sample_indices_]
        assert np.count_nonzero(sampled_y == 1) == np.count_nonzero(y[:240] == 1)
        assert np.count_nonzero(sampled_y == 0) == 10 * np.count_nonzero(sampled_y == 1)


def test_validate_input_schema():
    with pytest.raises(ValueError, match="Columnas"):
        validate_frame(pd.DataFrame({"Class": [0, 1]}))
