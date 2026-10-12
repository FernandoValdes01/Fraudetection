"""Carga, inspección y partición del conjunto Credit Card Fraud Detection."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from fraudetection.config import RANDOM_SEED, TEST_SIZE

FEATURE_COLUMNS = ("Time", *(f"V{i}" for i in range(1, 29)), "Amount")
TARGET_COLUMN = "Class"
EXPECTED_COLUMNS = (*FEATURE_COLUMNS, TARGET_COLUMN)


@dataclass(frozen=True)
class DatasetReport:
    records: int
    features: int
    missing_by_column: dict[str, int]
    duplicate_rows: int
    duplicates_by_class: dict[int, int]
    class_counts: dict[int, int]

    @property
    def class_proportions(self) -> dict[int, float]:
        return {label: count / self.records for label, count in self.class_counts.items()}


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Lee el CSV y comprueba su esquema sin modificar ni limpiar filas."""
    frame = pd.read_csv(path)
    missing = sorted(set(EXPECTED_COLUMNS) - set(frame.columns))
    unexpected = sorted(set(frame.columns) - set(EXPECTED_COLUMNS))
    if missing or unexpected:
        raise ValueError(f"Columnas faltantes: {missing}; columnas inesperadas: {unexpected}")
    if frame.empty:
        raise ValueError("El dataset está vacío")
    if not frame[TARGET_COLUMN].isin((0, 1)).all():
        raise ValueError("Class debe contener solo 0 y 1, sin valores faltantes")
    if frame[TARGET_COLUMN].nunique() != 2:
        raise ValueError("El dataset debe contener ambas clases")
    non_numeric = [
        name for name in FEATURE_COLUMNS if not pd.api.types.is_numeric_dtype(frame[name])
    ]
    if non_numeric:
        raise ValueError(f"Las variables predictoras deben ser numéricas: {non_numeric}")
    return frame.loc[:, list(EXPECTED_COLUMNS)]


def inspect_dataset(frame: pd.DataFrame) -> DatasetReport:
    """Cuenta faltantes, duplicados y clases antes de tomar decisiones de limpieza."""
    counts = frame[TARGET_COLUMN].value_counts().to_dict()
    duplicate_mask = frame.duplicated()
    duplicate_counts = frame.loc[duplicate_mask, TARGET_COLUMN].value_counts().to_dict()
    return DatasetReport(
        records=len(frame),
        features=len(FEATURE_COLUMNS),
        missing_by_column={name: int(count) for name, count in frame.isna().sum().items() if count},
        duplicate_rows=int(duplicate_mask.sum()),
        duplicates_by_class={label: int(duplicate_counts.get(label, 0)) for label in (0, 1)},
        class_counts={label: int(counts.get(label, 0)) for label in (0, 1)},
    )


def remove_exact_duplicates(frame: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas idénticas antes de separar entrenamiento y prueba."""
    return frame.drop_duplicates().reset_index(drop=True)


def split_dataset(
    frame: pd.DataFrame, *, random_state: int = RANDOM_SEED
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Reserva el 30 % como test estratificado sin ajustar transformaciones."""
    X = frame.loc[:, list(FEATURE_COLUMNS)]
    y = frame[TARGET_COLUMN].astype("int8")
    return train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=random_state,
    )
