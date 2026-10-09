# Fraudetection

Proyecto de INFO1185 para detectar transacciones fraudulentas en el conjunto [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud). La clase positiva es `Class = 1`; la prioridad es **aumentar la sensibilidad y reducir los falsos negativos**.

## Tech stack

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/PYTHON-1B2638?style=for-the-badge&amp;logo=python&amp;logoColor=9FB0C8">
  <img alt="uv" src="https://img.shields.io/badge/UV-1B2638?style=for-the-badge&amp;logo=uv&amp;logoColor=9FB0C8">
  <img alt="NumPy" src="https://img.shields.io/badge/NUMPY-1B2638?style=for-the-badge&amp;logo=numpy&amp;logoColor=9FB0C8">
  <img alt="pandas" src="https://img.shields.io/badge/PANDAS-1B2638?style=for-the-badge&amp;logo=pandas&amp;logoColor=9FB0C8">
</p>
<p align="center">
  <img alt="scikit-learn" src="https://img.shields.io/badge/SCIKIT--LEARN-1B2638?style=for-the-badge&amp;logo=scikitlearn&amp;logoColor=9FB0C8">
  <img alt="imbalanced-learn" src="https://img.shields.io/badge/IMBALANCED--LEARN-1B2638?style=for-the-badge&amp;logo=python&amp;logoColor=9FB0C8">
  <img alt="Matplotlib" src="https://img.shields.io/badge/MATPLOTLIB-1B2638?style=for-the-badge&amp;logo=python&amp;logoColor=9FB0C8">
</p>

Python 3.12 y `uv` 0.12 gestionan el entorno. El proyecto usa NumPy 2, pandas 3, scikit-learn 1, imbalanced-learn 0.14 y Matplotlib 3; [`uv.lock`](uv.lock) fija las versiones exactas.

## Métodos

<p align="center">
  <img alt="k-NN" src="https://img.shields.io/badge/K--NN-1B2638?style=for-the-badge">
  <img alt="Árbol de decisión" src="https://img.shields.io/badge/%C3%81RBOL%20DE%20DECISI%C3%93N-1B2638?style=for-the-badge">
  <img alt="SVM" src="https://img.shields.io/badge/SVM-1B2638?style=for-the-badge">
  <img alt="Random Forest propio" src="https://img.shields.io/badge/RANDOM%20FOREST%20PROPIO-1B2638?style=for-the-badge">
</p>
<p align="center">
  <img alt="Bootstrap" src="https://img.shields.io/badge/BOOTSTRAP-1B2638?style=for-the-badge">
  <img alt="Bagging" src="https://img.shields.io/badge/BAGGING-1B2638?style=for-the-badge">
  <img alt="Selección de variables" src="https://img.shields.io/badge/SELECCI%C3%93N%20DE%20VARIABLES-1B2638?style=for-the-badge">
  <img alt="Validación estratificada" src="https://img.shields.io/badge/CV%20ESTRATIFICADA-1B2638?style=for-the-badge">
</p>
<p align="center">
  <img alt="Compensación del desbalance" src="https://img.shields.io/badge/COMPENSACI%C3%93N%20DEL%20DESBALANCE-1B2638?style=for-the-badge">
  <img alt="Búsqueda de hiperparámetros" src="https://img.shields.io/badge/B%C3%9ASQUEDA%20DE%20HIPERPAR%C3%81METROS-1B2638?style=for-the-badge">
</p>

Se compararán **ocho experimentos**: cuatro clasificadores, cada uno con y sin compensación del desbalance. La selección usará cinco pliegues estratificados y elegirá la mayor sensibilidad media del fraude; la precisión del fraude resolverá empates. La tasa de falsos negativos se calculará como `FNR = FN / (TP + FN) = 1 − sensibilidad`.

El [Random Forest propio](src/fraudetection/forest.py) usa árboles `DecisionTreeClassifier`, bootstrap, selección aleatoria de variables por división y votación. Un empate favorece la clase fraude. El ensamble no utiliza `RandomForestClassifier` ni `BaggingClassifier`.

## Avance

- [x] Pauta del PDF con criterios de aceptación y rúbrica.
- [x] Inspección del CSV real: 284.807 filas, 492 fraudes, 0 faltantes y 1.081 duplicados exactos.
- [x] Limpieza explícita de duplicados y partición estratificada 70/30 con semilla 42.
- [x] Random Forest propio compatible con búsqueda de hiperparámetros; pruebas con datos sintéticos.
- [ ] Selección de características y compensación dentro de cinco pliegues de validación.
- [ ] Comparación de los ocho experimentos, evaluación final y presentación.

Los datos y la decisión de limpieza están en la [exploración inicial](documentacion/informe/exploracion.md). El conjunto de prueba permanece reservado para la evaluación final.

## Ejecutar lo disponible

1. Instala [`uv`](https://docs.astral.sh/uv/getting-started/installation/) y descarga `creditcard.csv` desde [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud). Guarda el CSV en `data/raw/creditcard.csv`; Git lo ignora.
2. Desde la raíz del repositorio, ejecuta:

   ```bash
   uv sync --locked
   uv run --locked fraudetection-inspect
   uv run --locked pytest -q
   ```

El comando muestra filas, características, faltantes, duplicados, clases y tamaños de la partición. Aún no entrena los cuatro clasificadores ni utiliza el test para comparar modelos. La configuración compartida está en [`config.py`](src/fraudetection/config.py).

## Documentación

| Archivo | Contenido |
| --- | --- |
| [Enunciado](IA_2026_P2.pdf) | PDF original. |
| [Pauta](documentacion/informe/pauta.md) | Requisitos, criterios de aceptación y puntajes. |
| [Exploración](documentacion/informe/exploracion.md) | Cifras del dataset y limpieza. |
| [Presentación](documentacion/presentacion/README.md) | Guion de diapositivas. |
| [Estudio](documentacion/estudio/README.md) | Preguntas para la defensa. |

La carpeta `documentacion/informe/` contiene material interno; el enunciado no pide informe escrito. La entrega final será por Blackboard e incluirá código, README y presentación. Ambos integrantes participarán en la defensa.
