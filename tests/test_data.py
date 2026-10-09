import numpy as np
import pandas as pd
import pytest

from fraudetection.data import (
    FEATURE_COLUMNS,
    inspect_dataset,
    load_dataset,
    remove_exact_duplicates,
    split_dataset,
)


def make_frame() -> pd.DataFrame:
    frame = pd.DataFrame(
        {name: np.arange(100, dtype=float) for name in FEATURE_COLUMNS}
    )
    frame["Class"] = [0] * 90 + [1] * 10
    return frame


def test_inspection_reports_quality_and_class_balance(tmp_path):
    frame = make_frame()
    frame.loc[0, "V1"] = np.nan
    frame.loc[2] = frame.loc[1]
    path = tmp_path / "creditcard.csv"
    frame.to_csv(path, index=False)

    loaded = load_dataset(path)
    report = inspect_dataset(loaded)

    assert report.records == 100
    assert report.features == 30
    assert report.missing_by_column == {"V1": 1}
    assert report.duplicate_rows == 1
    assert report.duplicates_by_class == {0: 1, 1: 0}
    assert report.class_counts == {0: 90, 1: 10}
    assert report.class_proportions[1] == pytest.approx(0.1)

    clean = remove_exact_duplicates(loaded)
    assert len(clean) == 99
    assert not clean.duplicated().any()


def test_split_is_stratified_reproducible_and_keeps_target_out_of_features():
    frame = make_frame()
    first = split_dataset(frame)
    second = split_dataset(frame)
    X_train, X_test, y_train, y_test = first

    assert len(X_train) == 70 and len(X_test) == 30
    assert int(y_train.sum()) == 7 and int(y_test.sum()) == 3
    assert "Class" not in X_train.columns
    assert set(X_train.index).isdisjoint(X_test.index)
    pd.testing.assert_frame_equal(first[0], second[0])
    pd.testing.assert_frame_equal(first[1], second[1])


def test_loader_rejects_wrong_schema(tmp_path):
    frame = make_frame().drop(columns="V28")
    path = tmp_path / "creditcard.csv"
    frame.to_csv(path, index=False)

    with pytest.raises(ValueError, match="Columnas faltantes"):
        load_dataset(path)
