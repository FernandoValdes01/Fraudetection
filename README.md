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
  <img alt="python-pptx" src="https://img.shields.io/badge/PYTHON--PPTX-1B2638?style=for-the-badge&amp;logo=python&amp;logoColor=9FB0C8">
  <img alt="Docker" src="https://img.shields.io/badge/DOCKER-1B2638?style=for-the-badge&amp;logo=docker&amp;logoColor=9FB0C8">
  <img alt="LaTeX Beamer" src="https://img.shields.io/badge/LATEX%20%2F%20BEAMER-1B2638?style=for-the-badge">
  <img alt="pytest" src="https://img.shields.io/badge/PYTEST-1B2638?style=for-the-badge&amp;logo=pytest&amp;logoColor=9FB0C8">
</p>

Python 3.12 y `uv` 0.12 gestionan el entorno. El proyecto usa NumPy 2, pandas 3, scikit-learn 1, imbalanced-learn 0.14 y Matplotlib 3. `python-pptx` genera una copia alternativa; Beamer compila la presentación principal. [`uv.lock`](uv.lock) fija las versiones exactas.

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
<p align="center">
  <img alt="ANOVA F-test" src="https://img.shields.io/badge/ANOVA%20F--TEST-1B2638?style=for-the-badge">
  <img alt="Submuestreo aleatorio 1 a 10" src="https://img.shields.io/badge/SUBMUESTREO%20ALEATORIO%201%3A10-1B2638?style=for-the-badge">
  <img alt="Sensibilidad y tasa de falsos negativos" src="https://img.shields.io/badge/SENSIBILIDAD%20%2F%20FNR-1B2638?style=for-the-badge">
</p>

Se compararon **ocho experimentos**: cuatro clasificadores, cada uno con y sin compensación del desbalance. La selección utilizó cinco pliegues estratificados y eligió la mayor sensibilidad media del fraude; la precisión del fraude resolvió empates. La tasa de falsos negativos se calcula como `FNR = FN / (TP + FN) = 1 − sensibilidad`.

El [Random Forest propio](src/fraudetection/forest.py) usa árboles `DecisionTreeClassifier`, bootstrap, selección aleatoria de variables por división y votación. Un empate favorece la clase fraude. El ensamble no utiliza `RandomForestClassifier` ni `BaggingClassifier`. Las variables se filtran con ANOVA F-test (`f_classif`); el submuestreo aleatorio mantiene una proporción de 1:10 entre fraude y transacciones legítimas.

## Avance

- [x] Pauta del PDF con criterios de aceptación y rúbrica.
- [x] Inspección del CSV real: 284.807 filas, 492 fraudes, 0 faltantes y 1.081 duplicados exactos.
- [x] Limpieza explícita de duplicados y partición estratificada 70/30 con semilla 42.
- [x] Random Forest propio compatible con búsqueda de hiperparámetros; pruebas con datos sintéticos.
- [x] Ocho búsquedas con selección ANOVA y submuestreo dentro de cinco pliegues compartidos.
- [x] Evaluación de prueba con los ocho modelos reajustados con todo el entrenamiento.
- [x] Tablas, gráficos y presentación Beamer de 12 diapositivas principales y cuatro de respaldo.

Los datos y la decisión de limpieza están en la [exploración inicial](documentacion/informe/exploracion.md). Los resultados completos están en [`resultados/`](resultados/) y el conjunto de prueba permaneció reservado hasta la evaluación final. El PDF Beamer es la presentación principal; el PowerPoint queda como formato alternativo.

## Resultado actual

La validación eligió **Random Forest propio con submuestreo 1:10** (`max_depth=6`, `n_estimators=21`), con sensibilidad **87,9 % ± 5,5 %** y precisión **45,0 %**. En los cinco reajustes sobre la misma prueba, obtuvo sensibilidad **80,4 % ± 0,3 %**, FNR **19,6 % ± 0,3 %** y precisión **67,5 % ± 4,6 %**. En la matriz del primer ajuste detectó 115 fraudes, omitió 27 y generó 53 falsas alarmas. Ver [métricas de los ocho experimentos](resultados/test_resumen.csv) y [predicciones para la matriz](resultados/predicciones_configuracion_cv.csv).

## Ejecutar lo disponible

1. Instala [`uv`](https://docs.astral.sh/uv/getting-started/installation/) y descarga `creditcard.csv` desde [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud). Guarda el CSV en `data/raw/creditcard.csv`; Git lo ignora.
2. Desde la raíz del repositorio, ejecuta:

   ```bash
   uv sync --locked
   uv run --locked fraudetection-inspect
   uv run --locked fraudetection-run
   uv run --locked fraudetection-report
   uv run --locked pytest -q
   ```

`fraudetection-run` ejecuta las búsquedas y la evaluación, guarda tablas y gráficos en `resultados/`. La búsqueda toma 50.000 filas estratificadas del entrenamiento para limitar el costo de k-NN; luego cada modelo se reajusta con las 198.608 filas completas de entrenamiento. `fraudetection-report` genera gráficos y el PowerPoint alternativo. El PDF principal se compila desde [`defensa_fraude.tex`](documentacion/presentacion/defensa_fraude.tex) con Docker y `blang/latex:ubuntu`; ver [instrucciones de presentación](documentacion/presentacion/README.md). La configuración está en [`config.py`](src/fraudetection/config.py).

La partición, la submuestra de búsqueda y los cinco pliegues usan semilla 42. Los ajustes finales usan 42, 101, 202, 303 y 404 sobre el mismo test. `fraudetection-report` conserva los metadatos de ejecución y obtiene el tamaño efectivo de búsqueda desde `cv_resumen.csv`, también al utilizar `--search-sample-size` con un valor personalizado.

## Documentación

| Archivo | Contenido |
| --- | --- |
| [Enunciado](IA_2026_P2.pdf) | PDF original. |
| [Pauta](documentacion/informe/pauta.md) | Requisitos, criterios de aceptación y puntajes. |
| [Exploración](documentacion/informe/exploracion.md) | Cifras del dataset y limpieza. |
| [Presentación](documentacion/presentacion/README.md) | Guion de diapositivas. |
| [Estudio](documentacion/estudio/README.md) | Preguntas para la defensa. |
| [Resultados de prueba](resultados/test_resumen.csv) | Seis métricas para los ocho experimentos, media y desviación estándar. |
| [Presentación Beamer (PDF)](documentacion/presentacion/defensa_fraude.pdf) | 12 diapositivas principales y cuatro de respaldo: CV, prueba, metodología/búsqueda y análisis crítico. |
| [Fuente Beamer](documentacion/presentacion/defensa_fraude.tex) | Archivo editable que genera el PDF. |
| [PowerPoint alternativo](documentacion/presentacion/defensa_fraude.pptx) | Versión editable del mismo protocolo y resultados; organización distinta de la presentación Beamer. |

La carpeta `documentacion/informe/` contiene material interno; el enunciado no pide informe escrito. La entrega final será por Blackboard e incluirá código, README y presentación. Ambos integrantes participarán en la defensa.

## Verificación independiente y entrega

Se conserva además una ejecución independiente con una muestra estratificada de 100.000 filas, tres semillas finales y resultados auditables en [`resultados/ejecucion/`](resultados/ejecucion/). Este protocolo tiene su propia selección por validación y su propia presentación `fraudetection.pptx`/`fraudetection.pdf`; sus métricas se mantienen separadas de la ejecución principal y de Beamer. El código está en [`src/fraudetection/reproduction/`](src/fraudetection/reproduction/).

```bash
uv run --locked fraudetection audit
uv run --locked fraudetection run --output resultados/reproduccion --sample-size 100000 --jobs 2
uv run --locked fraudetection report
uv run --locked python scripts/package_delivery.py
```

Para generar documentos del nuevo directorio, añadir `--input resultados/reproduccion` a `audit` y `report`. El comando de empaquetado reúne ambas ejecuciones, sus resultados y las presentaciones, sin incluir el CSV ni los modelos locales. Ver [instrucciones de reproducción](documentacion/reproduccion.md) y [revisión del protocolo independiente](documentacion/revision_final.md).
