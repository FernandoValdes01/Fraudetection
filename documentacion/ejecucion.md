# Detección de fraude con tarjetas

Proyecto de INFO1185 de Fernando Alonso Valdés Gómez y Juan Francisco Muñoz Veloso. Compara k-NN, árbol de decisión, SVM lineal y un bosque aleatorio propio, con y sin submuestreo. La métrica para elegir el modelo es la sensibilidad al fraude en validación cruzada.

## Contenido

- `src/`: código del proyecto.
- `resultados/`: tablas y métricas principales; `resultados/graficos/` contiene las figuras.
- `Presentacion.pdf`: presentación final del proyecto.
- `tests/`: pruebas del código incluido.
- `pyproject.toml` y `uv.lock`: dependencias y versiones fijadas.

El ZIP incluye el código fuente, las pruebas, los resultados principales, los gráficos y una presentación. No incluye el dataset.

## Preparación

Se requiere Python 3.12 y `uv`. Versiones utilizadas: NumPy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1, imbalanced-learn 0.14.2, Matplotlib 3.11.2 y python-pptx 1.0.2. `uv.lock` fija las dependencias exactas.

```bash
uv sync --locked
```

Descargue [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) y ubique `creditcard.csv` en `data/raw/`. También puede descargar y validar una copia pública con:

```bash
uv run --locked fraudetection download
```

## Ejecución principal

Ejecute desde la raíz del proyecto. Estos tres comandos inspeccionan los datos, ejecutan la evaluación y generan gráficos y una presentación automática de respaldo. El PDF entregado se consulta directamente y no se regenera con estos comandos:

```bash
uv run --locked fraudetection-inspect
uv run --locked fraudetection-run
uv run --locked fraudetection-report
```

Tras eliminar 1.081 duplicados quedan 283.726 transacciones, 473 fraudulentas. La partición estratificada 70/30 usa semilla 42: 198.608 filas para entrenamiento y 85.118 para test. La búsqueda compara los cuatro clasificadores con y sin submuestreo aleatorio 1:10, mediante cinco pliegues comunes sobre una muestra de 50.000 filas del entrenamiento. El escalado, la selección ANOVA F de 20 características y el submuestreo se ajustan dentro de cada pliegue. Se elige por sensibilidad de validación y, en empate, por precisión. Los reajustes finales usan todo el entrenamiento y las semillas 42, 101, 202, 303 y 404 sobre el mismo test reservado.

El submuestreo usa `RandomUnderSampler(sampling_strategy=0.1)` y conserva todos los fraudes disponibles. En el reajuste final, el entrenamiento pasa de 198.277 legítimas y 331 fraudes a 3.310 legítimas y 331 fraudes. En los pliegues 1 y 2, cada entrenamiento pasa de 39.933 legítimas y 67 fraudes a 670 y 67; en los pliegues 3, 4 y 5, de 39.934 y 66 a 660 y 66. Estos recuentos son comunes a los cuatro clasificadores. Sin compensación se conservan los recuentos originales; validación y test nunca se remuestrean.

Para revisar los resultados sin entrenar, abra `resultados/cv_resumen.csv` y `resultados/test_resumen.csv`. `test_repeticiones.csv` contiene los cinco reajustes y `caracteristicas_seleccionadas.csv`, las variables seleccionadas.

El ganador de validación es el bosque compensado de 21 árboles y profundidad 6, con sensibilidad de 87,9 % ± 5,5 puntos porcentuales. En el test obtiene sensibilidad de 80,4 % ± 0,3 pp y precisión de 67,5 % ± 4,6 pp. Las variaciones corresponden a cinco reajustes sobre el mismo test.

## Pruebas

```bash
uv run --locked pytest -q
```

Las pruebas verifican los datos, los modelos, el protocolo y la generación de la presentación.
