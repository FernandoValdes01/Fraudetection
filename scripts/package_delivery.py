"""Empaquetar código y resultados con instrucciones y una única presentación final."""

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
FINAL_PDF = Path("documentacion/presentacion/canva/Detección de fraude.pdf")


def build_delivery(root: Path = ROOT) -> Path:
    # Lista explícita: los apuntes y antecedentes nunca se recorren al empaquetar.
    files = {
        "README.md": root / "documentacion/ejecucion.md",
        FINAL_PDF.as_posix(): root / FINAL_PDF,
    }
    for name in ("pyproject.toml", "uv.lock", ".python-version", ".gitignore"):
        files[name] = root / name
    for directory in ("src", "tests", "scripts", "resultados"):
        for path in (root / directory).rglob("*"):
            if (
                path.is_file()
                and not any(
                    part.startswith(".") or part == "__pycache__"
                    for part in path.relative_to(root).parts
                )
                and path.suffix not in (".pyc", ".joblib", ".md", ".html")
            ):
                files[path.relative_to(root).as_posix()] = path
    # Comprobar entradas antes de reemplazar una entrega previa.
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
    print(f"Entrega: {archive_path} ({len(files)} archivos; sin material de estudio ni dataset)")
    return archive_path


if __name__ == "__main__":
    build_delivery()
