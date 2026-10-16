import json

import pandas as pd
import pytest

from fraudetection import presentation


@pytest.mark.parametrize("existing_metadata", [False, True])
def test_build_report_uses_cv_metadata_and_preserves_protocol(
    tmp_path, monkeypatch, existing_metadata
):
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    dataset = tmp_path / "dataset.csv"
    dataset.write_text("synthetic dataset")

    pd.DataFrame(
        {
            "experiment": ["exp-1", "exp-2"],
            "selected_by_cv": [True, False],
            "search_rows": [10_000, 10_000],
            "cv_folds": [4, 4],
        }
    ).to_csv(results_dir / "cv_resumen.csv", index=False)
    pd.DataFrame(
        {
            "experiment": ["exp-1"],
            "compensation": ["ninguna"],
            "sensitivity_mean": [0.8],
            "fnr_mean": [0.2],
        }
    ).to_csv(results_dir / "test_resumen.csv", index=False)
    pd.DataFrame({"class_true": [0, 1], "class_predicted": [0, 1]}).to_csv(
        results_dir / "predicciones_configuracion_cv.csv", index=False
    )
    original_metadata = {
        "cv_seed": 42,
        "search_sample_fraud": 17,
        "otrosprotocolo": {"test_repetitions": 3},
    }
    if existing_metadata:
        (results_dir / "metadata.json").write_text(json.dumps(original_metadata))

    frame = pd.DataFrame({"Class": [0, 0, 1, 1]})
    monkeypatch.setattr(presentation, "load_dataset", lambda _: frame)
    monkeypatch.setattr(
        presentation,
        "split_dataset",
        lambda clean: (None, pd.DataFrame(index=range(2)), None, None),
    )
    monkeypatch.setattr(presentation, "save_plots", lambda *args: None)
    monkeypatch.setattr(
        presentation,
        "create_deck",
        lambda cv, test, results, deck: (cv.iloc[0], test.iloc[0]),
    )

    metadata = presentation.build_report(dataset, results_dir, tmp_path / "deck.pptx")
    persisted = json.loads((results_dir / "metadata.json").read_text())

    assert metadata["search_sample_rows"] == 10_000
    assert metadata["cv_folds"] == 4
    assert persisted == metadata
    if existing_metadata:
        assert {key: persisted[key] for key in original_metadata} == original_metadata


@pytest.mark.parametrize("search_rows", [[10_000, 20_000], [10_000, None], [0, 0]])
def test_build_report_rejects_inconsistent_search_protocol(tmp_path, monkeypatch, search_rows):
    pd.DataFrame({"search_rows": search_rows, "cv_folds": [5, 5]}).to_csv(
        tmp_path / "cv_resumen.csv", index=False
    )
    frame = pd.DataFrame({"Class": [0, 1]})
    monkeypatch.setattr(presentation, "load_dataset", lambda _: frame)
    monkeypatch.setattr(presentation, "split_dataset", lambda _: (None, frame, None, None))
    with pytest.raises(ValueError, match="search_rows"):
        presentation.build_report(tmp_path / "dataset.csv", tmp_path, tmp_path / "deck.pptx")
    assert not (tmp_path / "metadata.json").exists()
    assert not (tmp_path / "deck.pptx").exists()
