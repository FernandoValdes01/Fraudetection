"""Comandos de descarga, experimentación, presentación y predicción."""

import argparse
from pathlib import Path

import joblib
import pandas as pd

from fraudetection.reproduction.config import FEATURES, SAMPLE_SIZE
from fraudetection.reproduction.data import download_dataset
from fraudetection.reproduction.experiments import run_experiments


def main():
    parser = argparse.ArgumentParser(description="Comparación reproducible de detección de fraude")
    commands = parser.add_subparsers(dest="command", required=True)
    download = commands.add_parser(
        "download", help="Descargar el CSV público utilizado por TensorFlow"
    )
    download.add_argument("--destination", type=Path, default=Path("data/raw/creditcard.csv"))
    run = commands.add_parser("run", help="Ejecutar búsquedas y evaluación final")
    run.add_argument("--data", type=Path, default=Path("data/raw/creditcard.csv"))
    run.add_argument("--output", type=Path, default=Path("resultados/ejecucion"))
    run.add_argument(
        "--sample-size",
        type=int,
        default=SAMPLE_SIZE,
        help="Filas de la muestra estratificada; 0 utiliza todo el conjunto limpio",
    )
    run.add_argument("--jobs", type=int, default=2)
    report = commands.add_parser("report", help="Generar gráficos, análisis HTML y presentación")
    report.add_argument("--input", type=Path, default=Path("resultados/ejecucion"))
    report.add_argument(
        "--presentation", type=Path, default=Path("documentacion/presentacion/fraudetection.pptx")
    )
    audit = commands.add_parser("audit", help="Verificar resultados guardados sin reentrenar")
    audit.add_argument("--input", type=Path, default=Path("resultados/ejecucion"))
    predict = commands.add_parser("predict", help="Predecir sin reajustar el modelo elegido")
    predict.add_argument(
        "--model", type=Path, default=Path("resultados/ejecucion/modelo_elegido.joblib")
    )
    predict.add_argument("--data", type=Path, required=True)
    predict.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "download":
        print(f"Descarga verificada. SHA256: {download_dataset(args.destination)}")
    elif args.command == "run":
        if args.jobs == 0 or args.jobs < -1:
            parser.error("--jobs debe ser positivo o -1")
        output = run_experiments(
            args.data,
            args.output,
            sample_size=args.sample_size or None,
            jobs=args.jobs,
        )
        print(f"Experimentos completos: {output}")
    elif args.command == "report":
        from fraudetection.reproduction.reporting import generate_report

        generate_report(args.input, args.presentation)
        print(f"Resultados: {args.input / 'analisis.html'}; presentación: {args.presentation}")
    elif args.command == "audit":
        from fraudetection.reproduction.audit import audit_results

        print(audit_results(args.input))
    elif args.command == "predict":
        frame = pd.read_csv(args.data)
        if not set(FEATURES).issubset(frame.columns):
            parser.error("El CSV requiere los 30 predictores originales")
        model = joblib.load(args.model)
        prediction = model.predict(frame.loc[:, FEATURES].to_numpy(dtype=float))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"Class_predicted": prediction}).to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
