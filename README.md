# Fraudetection

Base del proyecto de INFO1185 para comparar clasificadores supervisados en la detección de fraude con el conjunto [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud). La prioridad del enunciado es detectar fraudes, medida por la sensibilidad de la clase `Class = 1` y su tasa de falsos negativos.

Esta versión contiene la pauta, la estructura y el entorno reproducible. Los experimentos, resultados y diapositivas aún no están implementados.

## Tecnologías

| Herramienta | Uso previsto |
| --- | --- |
| Python 3.12 y `uv` 0.12 | Código, entorno y dependencias fijadas en `uv.lock`. |
| pandas 3 y NumPy 2 | Lectura, exploración y manejo de datos. |
| scikit-learn 1 | k-NN, árbol de decisión, SVM, árboles base del Random Forest propio, selección de características, validación y métricas. |
| imbalanced-learn 0.14 | Remuestreo dentro de los pliegues mediante `Pipeline`. |
| Matplotlib 3 | Gráficos y matrices de confusión. |
| LibreOffice Impress o PowerPoint | Presentación final; exportación a PDF si se usa una herramienta en línea. |

Las versiones exactas de las bibliotecas están en `uv.lock`. El Random Forest evaluado se implementará en este repositorio con árboles `DecisionTreeClassifier`; no se usará `RandomForestClassifier` ni `BaggingClassifier` para construirlo.

## Preparación y orden de ejecución

1. Instalar [`uv`](https://docs.astral.sh/uv/getting-started/installation/) y ejecutar `uv sync --locked` en la raíz del repositorio. `uv` utilizará Python 3.12 según `.python-version`.
2. Descargar el archivo `creditcard.csv` desde Kaggle y dejarlo en `data/raw/creditcard.csv`. El conjunto de datos no forma parte del repositorio.
3. Ejecutar el flujo de exploración, validación cruzada y evaluación cuando se incorpore a `src/fraudetection/`. Esta versión inicial todavía no ofrece un comando de experimentación.
4. Guardar tablas y gráficos obtenidos en `resultados/` y las diapositivas finales en `documentacion/presentacion/`.

Las constantes iniciales para el futuro flujo están en `src/fraudetection/config.py`: semilla 42, partición estratificada 70/30, cinco pliegues y clase positiva 1. El test debe conservar la distribución original y quedar reservado hasta la evaluación final.

## Estructura

```text
IA_2026_P2.pdf                 Enunciado original
documentacion/
  informe/pauta.md             Requisitos y criterios de aceptación
  presentacion/README.md       Guion y comprobaciones de las diapositivas
  estudio/README.md            Temas y preguntas para la defensa
data/raw/                      Ubicación local del CSV, ignorado por Git
src/fraudetection/             Código Python del proyecto
resultados/                    Tablas y gráficos que se generen
tests/                         Pruebas de la implementación futura
```

La carpeta `documentacion/informe/` contiene una pauta interna. El enunciado no pide entregar un informe escrito. La entrega final se hará en Blackboard e incluirá código, README y presentación; ambos integrantes deberán defender el trabajo.

## Fuentes técnicas

La configuración de `uv` sigue su [guía de proyectos](https://docs.astral.sh/uv/guides/projects/). La separación estratificada y la búsqueda corresponden a la documentación de [StratifiedKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html) y [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html). Para evitar fuga de información al remuestrear se seguirá la [guía de imbalanced-learn](https://imbalanced-learn.org/stable/common_pitfalls.html).
