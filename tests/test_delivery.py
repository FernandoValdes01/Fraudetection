"""La entrega incluye una única presentación y excluye los apuntes personales."""

import hashlib
import json
import runpy
from pathlib import Path
from zipfile import ZipFile

import pytest

PACKAGE = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/package_delivery.py"))


def prepare_files(root):
    for name in (
        "documentacion/ejecucion.md",
        PACKAGE["FINAL_PDF"].as_posix(),
        "pyproject.toml",
        "uv.lock",
        ".python-version",
        ".gitignore",
        "src/fraudetection/forest.py",
        "resultados/test_resumen.csv",
        "documentacion/estudio/guion.md",
        "documentacion/estudio/apuntes.pdf",
        "documentacion/contexto/antecedentes.md",
        "documentacion/presentacion/canva/presentacion.pdf",
        "resultados/ejecucion/analisis.md",
        "resultados/ejecucion/modelo.joblib",
    ):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name, encoding="utf-8")


def test_delivery_excludes_study_and_old_presentations_and_hashes_contents(tmp_path):
    prepare_files(tmp_path)
    archive_path = PACKAGE["build_delivery"](tmp_path)
    with ZipFile(archive_path) as archive:
        names = set(archive.namelist())
        assert {name for name in names if name.startswith("documentacion/")} == {
            PACKAGE["FINAL_PDF"].as_posix()
        }
        assert "src/fraudetection/forest.py" in names
        assert "resultados/test_resumen.csv" in names
        assert not any("estudio" in name or "guion" in name for name in names)
        assert not any(name.endswith(".joblib") for name in names)
        assert "resultados/ejecucion/analisis.md" not in names
        assert archive.read("README.md").decode() == "documentacion/ejecucion.md"
        manifest = json.loads(archive.read("manifest.json"))
        assert set(manifest) == names - {"manifest.json"}
        for name, digest in manifest.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
        assert json.loads((tmp_path / "entrega/manifest.json").read_text()) == manifest


def test_missing_canva_export_preserves_previous_delivery(tmp_path):
    prepare_files(tmp_path)
    archive_path = PACKAGE["build_delivery"](tmp_path)
    previous = archive_path.read_bytes()
    (tmp_path / PACKAGE["FINAL_PDF"]).unlink()
    with pytest.raises(FileNotFoundError, match="Falta un archivo"):
        PACKAGE["build_delivery"](tmp_path)
    assert archive_path.read_bytes() == previous
