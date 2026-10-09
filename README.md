# Fraudetection

Proyecto de INFO1185 para detectar fraude en transacciones con el conjunto [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud).

> **Objetivo:** detectar la mayor cantidad posible de fraudes (`Class = 1`). La medida principal será la sensibilidad; minimizar la tasa de falsos negativos (`FNR = FN / (TP + FN)`) es equivalente.

**Estado actual:** estructura, pauta y entorno listos. El entrenamiento, los resultados y las diapositivas todavía no están implementados.

## Tecnologías

![Python 3.12](https://img.shields.io/badge/Python-3.12-475569?style=flat-square)
![uv 0.12](https://img.shields.io/badge/uv-0.12-475569?style=flat-square)
![pandas 3](https://img.shields.io/badge/pandas-3-475569?style=flat-square)
![NumPy 2](https://img.shields.io/badge/NumPy-2-475569?style=flat-square)
![scikit-learn 1](https://img.shields.io/badge/scikit--learn-1-475569?style=flat-square)
![imbalanced-learn 0.14](https://img.shields.io/badge/imbalanced--learn-0.14-475569?style=flat-square)
![Matplotlib 3](https://img.shields.io/badge/Matplotlib-3-475569?style=flat-square)

- `uv` administra Python y las dependencias; [`uv.lock`](uv.lock) fija las versiones exactas.
- pandas y NumPy procesarán el CSV. scikit-learn aportará modelos, árboles, selección y validación.
- imbalanced-learn permitirá remuestrear dentro de cada pliegue. Matplotlib servirá para los gráficos.

La presentación se preparará en LibreOffice Impress o PowerPoint. Si se usa una herramienta en línea, también se entregará una copia en PDF.

## Métodos previstos

![k-NN](https://img.shields.io/badge/k--NN-64748B?style=flat-square)
![Árbol de decisión](https://img.shields.io/badge/%C3%81rbol%20de%20decisi%C3%B3n-64748B?style=flat-square)
![SVM](https://img.shields.io/badge/SVM-64748B?style=flat-square)
![Random Forest propio](https://img.shields.io/badge/Random%20Forest%20propio-64748B?style=flat-square)

![Bootstrap y bagging](https://img.shields.io/badge/Bootstrap%20y%20bagging-64748B?style=flat-square)
![Selección de variables](https://img.shields.io/badge/Selecci%C3%B3n%20de%20variables-64748B?style=flat-square)
![Validación estratificada](https://img.shields.io/badge/Validaci%C3%B3n%20estratificada-64748B?style=flat-square)
![Compensación del desbalance](https://img.shields.io/badge/Compensaci%C3%B3n%20del%20desbalance-64748B?style=flat-square)
![Búsqueda de hiperparámetros](https://img.shields.io/badge/B%C3%BAsqueda%20de%20hiperpar%C3%A1metros-64748B?style=flat-square)

Se compararán **ocho experimentos**: cada uno de los cuatro clasificadores, con y sin compensación del desbalance. La elección de hiperparámetros usará cinco pliegues estratificados y priorizará la sensibilidad media del fraude; en caso de empate, decidirá la precisión del fraude.

El Random Forest se programará en este repositorio con árboles `DecisionTreeClassifier`, muestras bootstrap y votación mayoritaria. No se utilizarán `RandomForestClassifier` ni `BaggingClassifier` para construir ese ensamble.

## Preparar el proyecto

1. Instala [`uv`](https://docs.astral.sh/uv/getting-started/installation/) y, desde la raíz, ejecuta:

   ```bash
   uv sync --locked
   ```

2. Descarga `creditcard.csv` desde [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) y ubícalo en `data/raw/creditcard.csv`. El CSV está excluido de Git.
3. Cuando se incorpore el flujo de experimentación, ejecútalo en este orden: exploración, validación cruzada y evaluación final. La versión inicial aún no tiene un comando para entrenar.
4. Guarda tablas y gráficos en `resultados/` y la presentación en `documentacion/presentacion/`.

La configuración inicial está en [`config.py`](src/fraudetection/config.py): **semilla 42**, partición estratificada **70/30**, **cinco pliegues** y fraude como clase positiva. El conjunto de prueba conservará la distribución original y se reservará hasta la evaluación final.

## Dónde está cada cosa

| Ruta | Contenido |
| --- | --- |
| [`IA_2026_P2.pdf`](IA_2026_P2.pdf) | Enunciado original. |
| [`documentacion/informe/pauta.md`](documentacion/informe/pauta.md) | Requisitos, criterios de aceptación y rúbrica. |
| [`documentacion/presentacion/`](documentacion/presentacion/) | Guion y futura presentación. |
| [`documentacion/estudio/`](documentacion/estudio/) | Preguntas para preparar la defensa. |
| `data/raw/` | Ubicación local del dataset. |
| `src/fraudetection/` | Código Python del proyecto. |
| `resultados/` | Tablas y gráficos por generar. |

La carpeta `documentacion/informe/` contiene una pauta de trabajo. **El enunciado no pide un informe escrito.** La entrega final es por Blackboard e incluye código, README y presentación; ambos integrantes participan en la defensa.

## Referencias técnicas

- [Proyectos con uv](https://docs.astral.sh/uv/guides/projects/).
- [Validación estratificada](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html) y [búsqueda de hiperparámetros](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html) en scikit-learn.
- [Cómo evitar fuga de información al remuestrear](https://imbalanced-learn.org/stable/common_pitfalls.html) en imbalanced-learn.
