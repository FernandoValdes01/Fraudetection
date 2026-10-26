"""La entrega contiene el código, resultados principales y presentación para el profesor."""

import hashlib
import json
import runpy
from pathlib import Path
from zipfile import ZipFile

import pytest

PACKAGE = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/package_delivery.py"))


def prepare_files(root):
    names = (
        "documentacion/ejecucion.md",
        PACKAGE["FINAL_PDF"].as_posix(),
        "pyproject.toml",
        "uv.lock",
        ".python-version",
        ".gitignore",
        "src/fraudetection/forest.py",
        "src/fraudetection/reproduction/cli.py",
        "tests/test_forest.py",
        "tests/test_results.py",
        "tests/test_delivery.py",
        "scripts/build_minimal_presentation.py",
        "scripts/package_delivery.py",
        "resultados/test_resumen.csv",
        "resultados/graficos/matriz_confusion.png",
        "resultados/ejecucion/analisis.md",
        "resultados/ejecucion/graficos/prueba.png",
        "resultados/ejecucion/modelo.joblib",
        "documentacion/estudio/guion.md",
        "documentacion/estudio/apuntes.pdf",
        "documentacion/presentacion/canva/presentacion.pdf",
        "resultados/notas.md",
        "resultados/graficos/apuntes.pdf",
    )
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name, encoding="utf-8")


def test_delivery_contains_main_results_root_pdf_and_verified_manifest(tmp_path):
    prepare_files(tmp_path)
    archive_path = PACKAGE["build_delivery"](tmp_path)
    with ZipFile(archive_path) as archive:
        names = set(archive.namelist())
        assert "Presentacion.pdf" in names
        assert "documentacion/presentacion/canva/Detección de fraude.pdf" not in names
        assert "src/fraudetection/reproduction/cli.py" in names
        assert "tests/test_forest.py" in names
        assert "tests/test_results.py" in names
        assert "scripts/build_minimal_presentation.py" in names
        assert "scripts/package_delivery.py" not in names
        assert "tests/test_delivery.py" not in names
        assert "resultados/test_resumen.csv" in names
        assert "resultados/graficos/matriz_confusion.png" in names
        assert not any(name.startswith("resultados/ejecucion/") for name in names)
        assert not any(name.startswith("documentacion/") for name in names)
        assert not any("apuntes" in name or "guion" in name for name in names)
        assert "resultados/notas.md" not in names
        assert archive.read("README.md").decode() == "documentacion/ejecucion.md"
        manifest = json.loads(archive.read("manifest.json"))
        assert set(manifest) == names - {"manifest.json"}
        for name, digest in manifest.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
        assert json.loads((tmp_path / "entrega/manifest.json").read_text()) == manifest


def test_missing_pdf_preserves_previous_delivery(tmp_path):
    prepare_files(tmp_path)
    archive_path = PACKAGE["build_delivery"](tmp_path)
    previous = archive_path.read_bytes()
    (tmp_path / PACKAGE["FINAL_PDF"]).unlink()
    with pytest.raises(FileNotFoundError, match="Falta un archivo"):
        PACKAGE["build_delivery"](tmp_path)
    assert archive_path.read_bytes() == previous
