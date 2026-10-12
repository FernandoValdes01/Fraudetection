import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

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
