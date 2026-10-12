"""Crear la entrega sin dataset, entorno virtual ni modelos binarios locales."""

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
files = [
    ROOT / name
    for name in (
        "README.md",
        "pyproject.toml",
        "uv.lock",
        ".python-version",
        ".gitignore",
        "IA_2026_P2.pdf",
    )
]
for directory in ("src", "tests", "scripts", "documentacion", "resultados/ejecucion"):
    files.extend(
        path
        for path in (ROOT / directory).rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix not in (".pyc", ".joblib")
    )
files = sorted(set(files))
destination = ROOT / "entrega"
destination.mkdir(exist_ok=True)
manifest = {
    str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files
}
(destination / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
archive_path = destination / "fraudetection_entrega.zip"
with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, arcname=str(path.relative_to(ROOT)))
    archive.write(destination / "manifest.json", arcname="manifest.json")
print(f"Entrega: {archive_path} ({len(files)} archivos; sin dataset)")
