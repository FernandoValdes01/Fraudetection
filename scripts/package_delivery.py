"""Empaquetar el proyecto y sus resultados principales para revisión académica."""

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
FINAL_PDF = Path("documentacion/presentacion/canva/Detección de fraude_FINAL.pdf")
DELIVERY_PDF = "Presentacion.pdf"


def build_delivery(root: Path = ROOT) -> Path:
    files = {
        "README.md": root / "documentacion/ejecucion.md",
        DELIVERY_PDF: root / FINAL_PDF,
    }
    for name in ("pyproject.toml", "uv.lock", ".python-version", ".gitignore"):
        files[name] = root / name
    for directory in ("src", "tests"):
        for path in (root / directory).rglob("*"):
            relative = path.relative_to(root)
            if (
                path.is_file()
                and not any(
                    part.startswith(".") or part == "__pycache__" for part in relative.parts
                )
                and relative.as_posix() != "tests/test_delivery.py"
                and path.suffix in {".py", ".typed"}
            ):
                files[relative.as_posix()] = path
    files["scripts/build_minimal_presentation.py"] = root / "scripts/build_minimal_presentation.py"
    for path in (root / "resultados").glob("*"):
        if path.is_file() and path.suffix in {".csv", ".json"}:
            files[path.relative_to(root).as_posix()] = path
    for path in (root / "resultados/graficos").glob("*"):
        if path.is_file() and path.suffix == ".png":
            files[path.relative_to(root).as_posix()] = path

    for path in files.values():
        if not path.is_file():
            raise FileNotFoundError(f"Falta un archivo de entrega: {path}")
    manifest = {
        name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sorted(files.items())
    }
    destination = root / "entrega"
    destination.mkdir(exist_ok=True)
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    archive_path = destination / "fraudetection_entrega.zip"
    temporary = archive_path.with_suffix(".zip.tmp")
    try:
        with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as archive:
            for name, path in sorted(files.items()):
                archive.write(path, arcname=name)
            archive.writestr("manifest.json", manifest_text)
        temporary.replace(archive_path)
    finally:
        temporary.unlink(missing_ok=True)
    (destination / "manifest.json").write_text(manifest_text, encoding="utf-8")
    print(f"Entrega: {archive_path} ({len(files)} archivos; sin dataset)")
    return archive_path


if __name__ == "__main__":
    build_delivery()
