"""Comando de inspección inicial del dataset."""

import argparse
from pathlib import Path

from fraudetection.data import (
    inspect_dataset,
    load_dataset,
    remove_exact_duplicates,
    split_dataset,
)

DEFAULT_DATASET = Path("data/raw/creditcard.csv")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspecciona el dataset y comprueba la partición 70/30"
    )
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET, help="ruta de creditcard.csv"
    )
    args = parser.parse_args()

    try:
        frame = load_dataset(args.dataset)
        report = inspect_dataset(frame)
        clean_frame = remove_exact_duplicates(frame)
        clean_report = inspect_dataset(clean_frame)
        X_train, X_test, y_train, y_test = split_dataset(clean_frame)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error al inspeccionar {args.dataset}: {error}\n")

    print(f"Registros: {report.records:,} | Características: {report.features}")
    print(
        f"Duplicados exactos: {report.duplicate_rows:,} "
        f"(clase 0: {report.duplicates_by_class[0]:,}; clase 1: {report.duplicates_by_class[1]:,})"
    )
    if report.missing_by_column:
        print(
            "Faltantes: "
            + ", ".join(
                f"{name}={count}" for name, count in report.missing_by_column.items()
            )
        )
    else:
        print("Faltantes: 0")
    for label in (0, 1):
        print(
            f"Clase {label}: {report.class_counts[label]:,} ({report.class_proportions[label]:.3%})"
        )
    print(f"Tras quitar duplicados: {clean_report.records:,} registros")
    for label in (0, 1):
        print(
            f"Clase {label} limpia: {clean_report.class_counts[label]:,} ({clean_report.class_proportions[label]:.3%})"
        )
    print(f"Entrenamiento: {len(X_train):,} filas, {int(y_train.sum()):,} fraudes")
    print(f"Prueba reservada: {len(X_test):,} filas, {int(y_test.sum()):,} fraudes")
    if report.records < 10_000:
        print("Aviso: el enunciado exige utilizar al menos 10 000 registros.")


if __name__ == "__main__":
    main()
