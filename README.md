# Fraudetection

Proyecto de INFO1185 · Inteligencia Artificial, de Fernando Alonso Valdés Gómez y Juan Francisco Muñoz Veloso. Compara k-NN, árbol de decisión, SVM y un Random Forest propio sobre [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud).

La prioridad es minimizar falsos negativos de fraude, `Class = 1`. La selección maximiza sensibilidad media en validación y desempata por precisión.

## Ejecutar

Requiere Python 3.12 y [uv](https://docs.astral.sh/uv/getting-started/installation/). `uv.lock` fija las versiones; las dependencias principales son NumPy 2, pandas 3, scikit-learn 1, imbalanced-learn 0.14, Matplotlib 3 y python-pptx 1.

1. Ejecuta `uv sync --locked` desde la raíz.
2. Descarga `creditcard.csv` de Kaggle en `data/raw/`, o usa `uv run --locked fraudetection download`.
3. Ejecuta el protocolo principal:

   ```bash
   uv run --locked fraudetection-inspect
   uv run --locked fraudetection-run
   uv run --locked fraudetection-report
   ```

`fraudetection-report` regenera los gráficos y el PowerPoint automático de respaldo; la edición de Canva se gestiona por separado. No hace falta descargar el dataset para consultar las tablas y presentaciones ya incluidas.

## Método y resultado

Se eliminan 1.081 duplicados exactos del CSV original de 284.807 filas y 492 fraudes. Quedan 283.726 filas y 473 fraudes. La partición estratificada 70/30, con semilla 42, reserva 85.118 filas y 142 fraudes para prueba.

Los ocho experimentos comparten cinco pliegues estratificados sobre 50.000 filas de entrenamiento para acotar el costo de búsqueda. Las tuberías ajustan escalado, selección ANOVA F de 20 variables y, cuando corresponde, submuestreo 1:10 solo con el entrenamiento de cada pliegue. Validación y prueba conservan su prevalencia. Cada configuración elegida se reajusta con las 198.608 filas completas de entrenamiento y las semillas 42, 101, 202, 303 y 404 sobre el mismo test.

El [Random Forest propio](src/fraudetection/forest.py) implementa bootstrap, árboles independientes, características aleatorias por división y voto mayoritario, con empate a favor de fraude. Usa `DecisionTreeClassifier`; no construye el ensamble con `RandomForestClassifier` ni `BaggingClassifier`.

La validación seleccionó el Random Forest compensado, con 21 árboles y profundidad 6: sensibilidad **87,9 % ± 5,5 pp**. En prueba obtuvo sensibilidad **80,4 % ± 0,3 pp**, FNR **19,6 % ± 0,3 pp** y precisión **67,5 % ± 4,6 pp**. Las desviaciones en prueba describen variación del ajuste sobre un mismo test. Ver [validación](resultados/cv_resumen.csv), [prueba](resultados/test_resumen.csv) y [metadatos](resultados/metadata.json).

## Entrenamiento, validación interna y test

La separación inicial tiene solo dos conjuntos: 198.608 filas de entrenamiento y 85.118 de test reservado. No se crea un tercer conjunto fijo de validación. Dentro del entrenamiento se seleccionan 50.000 filas para la búsqueda; esas filas ya pertenecen a las 198.608. La validación cruzada estratificada divide la muestra en cinco bloques de 10.000. En cada ronda se ajusta una pipeline nueva con cuatro bloques, 40.000 filas antes del submuestreo opcional, y se evalúa con el bloque restante de 10.000. El bloque de validación rota cinco veces: una fila valida en una ronda y entrena en otras cuatro, siempre con modelos reajustados por separado. Ninguna transformación aprende del bloque de validación en su propia ronda. El test de 85.118 filas queda fuera de toda la búsqueda.

Elegidos los parámetros, cada configuración se reajusta desde cero con el entrenamiento disponible. Sin compensación, el clasificador recibe 198.608 filas; con submuestreo 1:10 recibe 331 fraudes y 3.310 legítimas, 3.641 filas. Los cinco reajustes finales con semillas 42, 101, 202, 303 y 404 son distintos de los cinco pliegues: se evalúan sobre el mismo test reservado. Estos conteos describen el protocolo principal y sus artefactos históricos; no una ejecución nueva.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `src/fraudetection/` | Protocolo principal, Random Forest y comandos. |
| `src/fraudetection/reproduction/` | Protocolo auxiliar independiente. |
| `tests/` | Pruebas automatizadas de datos, modelos y artefactos. |
| `data/raw/` | CSV local, excluido de Git y de la entrega. |
| `resultados/` | Resultados y gráficos del protocolo principal. |
| `resultados/ejecucion/` | Resultados separados del protocolo auxiliar. |
| `documentacion/contexto/` | Pauta, exploración, reproducción y antecedentes de entrega. |
| `documentacion/presentacion/` | Presentación final de Canva. |
| `documentacion/estudio/` | Material para preparar la defensa. |
| `scripts/package_delivery.py` | Generación del ZIP y manifiesto SHA256. |
| `entrega/` | Manifiesto versionado y ZIP local regenerable. |

El [enunciado original](IA_2026_P2.pdf) exige código, README, presentación y defensa de ambos integrantes de 10–12 minutos. **No exige informe escrito.** Consultar la [pauta](documentacion/contexto/pauta.md) y la [documentación](documentacion/README.md).

## Presentación

La presentación editable está en [Canva](https://canva.link/g838er8qsmu3bic). El [PDF final exportado de Canva](documentacion/presentacion/canva/Detección%20de%20fraude_FINAL.pdf), de 22 páginas, es la presentación de entrega. Ver [presentaciones, copias locales y guiones](documentacion/presentacion/README.md). Los resultados del protocolo principal y del auxiliar tienen muestras, modelos y ganadores distintos; cada presentación identifica su protocolo.

## Verificar y empaquetar

```bash
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked fraudetection audit
uv run --locked python scripts/package_delivery.py
```

La auditoría del comando `fraudetection audit` verifica los artefactos auxiliares. El ZIP incluye código, dependencias, pruebas, resultados principales, el PDF final de Canva de 22 páginas como `Presentacion.pdf` y un README de [ejecución](documentacion/ejecucion.md). Excluye resultados auxiliares, material de estudio, guiones, antecedentes, presentaciones anteriores, archivos internos de empaquetado, dataset, entorno virtual y modelos binarios locales. `entrega/manifest.json` registra exclusivamente los archivos del ZIP.

El protocolo auxiliar conserva una muestra estratificada de 100.000 filas y tres semillas. La consigna no fija el número de repeticiones. Sus instrucciones están en [reproducción](documentacion/contexto/reproduccion.md) y la separación de protocolos en [integración](documentacion/contexto/integracion.md).

Entrega en Blackboard: **26 de octubre de 2026, 23:59**. Reserva de defensa: **27–28 de octubre**. La subida, la reserva y el ensayo de ambos integrantes siguen siendo acciones personales.
