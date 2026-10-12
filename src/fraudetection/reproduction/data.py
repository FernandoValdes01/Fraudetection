"""Lectura, limpieza determinista y particiones reproducibles."""

import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split

from fraudetection.reproduction.config import CV_FOLDS, DATA_URL, FEATURES, RANDOM_SEED, TEST_SIZE


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_dataset(path):
    """Descarga pública utilizada por TensorFlow; no requiere credenciales de Kaggle."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Ya existe {path}; no se sobrescribe el dataset.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".download")
    try:
        with urlopen(DATA_URL, timeout=60) as response, temporary.open("wb") as handle:
            while block := response.read(1024 * 1024):
                handle.write(block)
        frame = pd.read_csv(temporary)
        validate_frame(frame)
        if len(frame) != 284_807 or int(frame["Class"].sum()) != 492:
            raise ValueError("La descarga no corresponde a los recuentos del dataset original.")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return sha256_file(path)


def validate_frame(frame):
    expected = set(FEATURES) | {"Class"}
    if set(frame.columns) != expected:
        raise ValueError(f"Columnas inválidas. Se esperan: {sorted(expected)}")
    if not all(pd.api.types.is_numeric_dtype(frame[c]) for c in frame):
        raise ValueError("Todas las columnas deben ser numéricas.")
    if not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError(
            "Hay valores faltantes o no finitos; se requiere una política de limpieza."
        )
    if set(frame["Class"].unique()) != {0, 1}:
        raise ValueError("Class debe contener las clases 0 y 1.")


def class_counts(y):
    return {str(c): int(np.count_nonzero(np.asarray(y) == c)) for c in (0, 1)}


def prepare_data(path, sample_size, output):
    """Deduplica antes de dividir para impedir copias exactas entre train y test.

    No se aprende ninguna transformación en esta limpieza. La muestra conserva
    la prevalencia, sin retener artificialmente todos los fraudes originales.
    """
    path, output = Path(path), Path(output)
    raw = pd.read_csv(path)
    validate_frame(raw)
    clean = raw.drop_duplicates().copy()
    if sample_size is not None:
        if sample_size < 10_000 or sample_size > len(clean):
            raise ValueError(f"La muestra debe tener entre 10.000 y {len(clean)} filas.")
        if sample_size < len(clean):
            clean, _ = train_test_split(
                clean,
                train_size=sample_size,
                stratify=clean["Class"],
                random_state=RANDOM_SEED,
            )
    if len(clean) < 10_000:
        raise ValueError("Se requieren al menos 10.000 filas después de limpiar.")
    X = clean.loc[:, FEATURES].to_numpy(dtype=np.float64)
    y = clean["Class"].to_numpy(dtype=np.int64)
    train, test = train_test_split(
        np.arange(len(y)),
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_SEED,
    )
    if min(class_counts(y[train]).values()) < CV_FOLDS:
        raise ValueError("El entrenamiento requiere al menos cinco ejemplos de cada clase.")
    folds = list(
        StratifiedKFold(
            n_splits=CV_FOLDS,
            shuffle=True,
            random_state=RANDOM_SEED,
        ).split(X[train], y[train])
    )
    partition_arrays = {
        "sample_row_ids": clean.index.to_numpy(),
        "train_positions": train,
        "test_positions": test,
    }
    for i, (fold_train, fold_valid) in enumerate(folds):
        partition_arrays[f"fold_{i}_train"] = fold_train
        partition_arrays[f"fold_{i}_validation"] = fold_valid
    np.savez_compressed(output / "particiones.npz", **partition_arrays)
    exploration = {
        "raw_rows": len(raw),
        "predictors": len(FEATURES),
        "missing_by_column": raw.isna().sum().to_dict(),
        "raw_class_counts": class_counts(raw["Class"]),
        "duplicate_rows_removed": len(raw) - len(raw.drop_duplicates()),
        "clean_rows": len(raw.drop_duplicates()),
        "clean_class_counts": class_counts(raw.drop_duplicates()["Class"]),
        "sample_rows": len(y),
        "sample_class_counts": class_counts(y),
        "train_rows": len(train),
        "test_rows": len(test),
        "train_class_counts": class_counts(y[train]),
        "test_class_counts": class_counts(y[test]),
        "sample_fraud_fraction": float(y.mean()),
        "dataset_sha256": sha256_file(path),
        "cleaning": "Eliminar duplicados exactos antes de muestrear y dividir; sin imputación.",
        "sampling": "Muestra estratificada sin reemplazo con prevalencia original y semilla 42.",
    }
    (output / "exploracion.json").write_text(
        json.dumps(exploration, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    raw.describe().to_csv(output / "descriptivos.csv")
    return X[train], X[test], y[train], y[test], clean.index.to_numpy()[test], folds, exploration
