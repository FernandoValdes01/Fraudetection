# Fraudetection: instrucciones de ejecución y entrega

Proyecto INFO1185 de Fernando Alonso Valdés Gómez y Juan Francisco Muñoz Veloso. Compara k-NN, árbol, SVM lineal y Random Forest propio, con y sin submuestreo 1:10. Se selecciona por sensibilidad de fraude en validación y se desempata por precisión.

## Contenido

El ZIP incluye código en `src/`, pruebas en `tests/`, scripts, dependencias fijadas en `uv.lock`, resultados y una única presentación final en `documentacion/presentacion/canva/Detección de fraude.pdf`. Es una exportación nativa del [diseño Canva](https://canva.link/g838er8qsmu3bic), con 18 diapositivas principales y cuatro de respaldo. No incluye material de estudio, guiones, antecedentes, dataset ni modelos binarios. `manifest.json` contiene las huellas SHA256 de los archivos entregados; este documento se incluye como `README.md` en la raíz del ZIP.

## Preparar el entorno

Descomprimir el ZIP y ejecutar los comandos desde su raíz. Se requiere Python 3.12 y `uv`. Las dependencias principales son NumPy 2, pandas 3, scikit-learn 1, imbalanced-learn 0.14, Matplotlib 3 y python-pptx 1; `uv.lock` fija sus versiones exactas.

```bash
uv sync --locked
```

Descargar [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) y guardar `creditcard.csv` en `data/raw/`. Como alternativa, este comando descarga la copia pública usada por TensorFlow y verifica estructura y recuentos:

```bash
uv run --locked fraudetection download
```

No sobrescribe un dataset existente. El conjunto original tiene 284.807 filas y 492 fraudes; se eliminan 1.081 duplicados exactos y quedan 283.726 filas y 473 fraudes.

## Reproducir el protocolo de la presentación

```bash
uv run --locked fraudetection-inspect
uv run --locked fraudetection-run
uv run --locked fraudetection-report
```

El primer comando inspecciona el CSV. El segundo realiza las ocho búsquedas y evaluaciones; puede requerir tiempo según el equipo. El tercero regenera gráficos y una presentación automática de respaldo. Esa presentación generada no reemplaza ni sincroniza el PDF nativo de Canva entregado.

La partición estratificada 70/30 usa semilla 42: 198.608 filas de entrenamiento y 85.118 de prueba, con 142 fraudes en prueba. La búsqueda usa una submuestra estratificada fija de 50.000 filas de entrenamiento, con 83 fraudes, y cinco pliegues comunes. Escalado, ANOVA F de 20 variables y submuestreo se ajustan exclusivamente sobre el entrenamiento de cada pliegue. Las configuraciones seleccionadas se reajustan con todo el entrenamiento usando las semillas 42, 101, 202, 303 y 404, sobre el mismo test reservado.

El submuestreo aleatorio usa `RandomUnderSampler(sampling_strategy=0.1)`: conserva todos los fraudes y selecciona diez transacciones legítimas por cada fraude. La submuestra de búsqueda contiene 49.917 legítimas y 83 fraudes. Los recuentos de entrenamiento antes y después de compensar son los mismos para los cuatro clasificadores:

| Datos de entrenamiento | Legítimas antes | Fraudes antes | Legítimas después | Fraudes después |
| --- | ---: | ---: | ---: | ---: |
| Pliegues 1 y 2, cada uno | 39.933 | 67 | 670 | 67 |
| Pliegues 3, 4 y 5, cada uno | 39.934 | 66 | 660 | 66 |
| Reajuste final con todo el entrenamiento | 198.277 | 331 | 3.310 | 331 |

Las condiciones sin compensación conservan los recuentos de las columnas «antes». Validación y prueba no se remuestrean; el test mantiene sus 84.976 legítimas y 142 fraudes. Las semillas cambian qué legítimas se seleccionan, pero no estos recuentos.

Los resultados principales están en `resultados/cv_resumen.csv`, `test_resumen.csv`, `test_repeticiones.csv`, `caracteristicas_seleccionadas.csv`, `seleccion_cv.json`, `predicciones_configuracion_cv.csv` y `metadata.json`. Las figuras están en `resultados/graficos/`. Se pueden consultar sin descargar el dataset.

El ganador de CV es el bosque compensado de 21 árboles y profundidad 6, con sensibilidad de validación 87,9 % ± 5,5 pp. En prueba obtiene sensibilidad 80,4 % ± 0,3 pp, FNR 19,6 % ± 0,3 pp y precisión 67,5 % ± 4,6 pp. La desviación en prueba describe cinco ajustes sobre un mismo test, no cinco tests independientes.

## Verificar

```bash
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
```

Las pruebas comprueban datos, bosque propio, tuberías y coherencia de resultados. No sustituyen una repetición completa del entrenamiento.

Para verificar la integridad de una entrega descomprimida, desde su raíz:

```bash
python - <<'PY'
import hashlib
import json
from pathlib import Path
manifest = json.loads(Path('manifest.json').read_text(encoding='utf-8'))
for name, expected in manifest.items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
print('Integridad SHA256 correcta')
PY
```

## Protocolo auxiliar separado

`src/fraudetection/reproduction/` y `resultados/ejecucion/` conservan una ejecución independiente de 100.000 filas, SVM RBF y tres semillas. Sus métricas y su ganador no corresponden a la presentación final. Para auditar sus resultados guardados:

```bash
uv run --locked fraudetection audit
```

Para repetirlo en un directorio nuevo:

```bash
uv run --locked fraudetection run --output resultados/reproduccion --sample-size 100000 --jobs 2
uv run --locked fraudetection audit --input resultados/reproduccion
```

Esta auditoría comprueba exclusivamente el protocolo auxiliar. No usar su salida como auditoría del protocolo principal.

## Regenerar el ZIP desde el repositorio

```bash
uv run --locked python scripts/package_delivery.py
```

El empaquetado se ejecuta desde el repositorio completo, que conserva este documento en `documentacion/ejecucion.md`. Genera `entrega/fraudetection_entrega.zip` y `entrega/manifest.json` a partir de una lista explícita de entradas. Los cambios realizados en Canva requieren una nueva exportación PDF antes de empaquetar.

## Entrenamiento, validación interna y test

La separación inicial tiene solo dos conjuntos: 198.608 filas de entrenamiento y 85.118 de test reservado. No se crea un tercer conjunto fijo de validación. Dentro del entrenamiento se seleccionan 50.000 filas para la búsqueda; esas filas ya pertenecen a las 198.608. La validación cruzada estratificada divide la muestra en cinco bloques de 10.000. En cada ronda se ajusta una pipeline nueva con cuatro bloques, 40.000 filas antes del submuestreo opcional, y se evalúa con el bloque restante de 10.000. El bloque de validación rota cinco veces: una fila valida en una ronda y entrena en otras cuatro, siempre con modelos reajustados por separado. Ninguna transformación aprende del bloque de validación en su propia ronda. El test de 85.118 filas queda fuera de toda la búsqueda.

Elegidos los parámetros, cada configuración se reajusta desde cero con el entrenamiento disponible. Sin compensación, el clasificador recibe 198.608 filas; con submuestreo 1:10 recibe 331 fraudes y 3.310 legítimas, 3.641 filas. Los cinco reajustes finales con semillas 42, 101, 202, 303 y 404 son distintos de los cinco pliegues: se evalúan sobre el mismo test reservado. Estos conteos describen el protocolo principal y sus artefactos históricos; no una ejecución nueva.
