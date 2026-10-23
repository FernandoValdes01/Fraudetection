# Ejecución independiente de 100.000 filas

Este documento corresponde al protocolo auxiliar de 100.000 filas y tres semillas, con resultados exclusivamente en `resultados/ejecucion/`. El principal usa el conjunto limpio completo, cinco semillas y resultados en la raíz de `resultados/`. La consigna no fija una cantidad de semillas; no deben mezclarse las métricas de ambos protocolos.

Proyecto de INFO1185 de **Fernando Alonso Valdés Gómez** y **Juan Francisco Muñoz Veloso**. Compara k-NN, árbol de decisión, SVM y un Random Forest propio para detectar fraude en tarjetas de crédito. Se elige por sensibilidad del fraude y se desempata por precisión, conforme a [la consigna](../IA_2026_P2.pdf).

El procedimiento está implementado y ejecutado con datos reales. Se incluyen los ocho experimentos, búsquedas, métricas, gráficos, análisis y presentación. No se necesita informe escrito.

## Ejecución

Requiere Python 3.12 y `uv`. La ejecución original se preparó con Python 3.12.12 y uv 0.9.18; esta revisión usa Python 3.12.6 y uv 0.12.6. `protocolo.json` conserva Python 3.12.12 como dato histórico. `uv.lock` fija las dependencias, incluidas pandas 3.0.6, NumPy 2.5.3, scikit-learn 1.9.1, imbalanced-learn 0.14.2, Matplotlib 3.11.2 y python-pptx 1.0.2.

Desde la raíz del repositorio:

```bash
uv sync --locked
# Omitir download si data/raw/creditcard.csv ya existe.
uv run --locked fraudetection download
uv run --locked fraudetection run --output resultados/reproduccion --sample-size 100000 --jobs 2
uv run --locked fraudetection audit --input resultados/reproduccion
uv run --locked fraudetection report --input resultados/reproduccion --presentation documentacion/presentacion/reproduccion.pptx
```

La descarga obtiene la copia pública del dataset Kaggle usada por [TensorFlow](https://www.tensorflow.org/tutorials/structured_data/imbalanced_data), comprueba columnas y recuentos y no sobrescribe archivos. También se puede descargar `creditcard.csv` desde [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) y guardarlo en `data/raw/creditcard.csv`. No hace falta una cuenta de Kaggle para el comando de descarga. El CSV no se adjunta a la entrega ni se versiona.

Cada ejecución necesita un directorio de salida nuevo para conservar los experimentos anteriores. `--sample-size 0` utiliza todo el conjunto limpio, con mayor costo. La ejecución entregada de 100.000 filas tardó unos 2,4 minutos en esta máquina; el tiempo depende del equipo. `--jobs 1` reduce el paralelismo.

Los resultados ya obtenidos están en [resultados/ejecucion](../resultados/ejecucion/). Para inspeccionarlos sin reentrenar:

```bash
uv run --locked fraudetection audit
uv run --locked fraudetection report
```

El segundo comando regenera los gráficos, `analisis.html`, `analisis.md`, la presentación y el guion de defensa. Para exportar las diapositivas a PDF se requiere LibreOffice, disponible en el equipo donde se preparó la entrega:

```bash
libreoffice -env:UserInstallation=file:///tmp/fraudetection-office --headless --convert-to pdf --outdir documentacion/presentacion documentacion/presentacion/fraudetection.pptx
```

También se puede abrir el PPTX en PowerPoint o LibreOffice y exportarlo manualmente.

## Metodología

1. Validar los 30 predictores numéricos y `Class`, sin valores faltantes ni infinitos. El dataset original tiene 284.807 filas y 492 fraudes. Se eliminan 1.081 duplicados exactos antes de dividir para evitar copias entre train y test; quedan 283.726 filas y 473 fraudes. Esta limpieza no aprende parámetros.
2. Obtener una muestra estratificada sin reemplazo de 100.000 filas, semilla 42. Conserva 167 fraudes, sin enriquecer artificialmente la prevalencia. El tamaño acota el costo de SVM y k-NN, a cambio de perder positivos.
3. Separar una sola vez 70.000 filas de entrenamiento y 30.000 de prueba, con estratificación y semilla 42. Quedan 117 y 50 fraudes respectivamente. Guardar los índices originales y reutilizar los mismos cinco pliegues estratificados para los ocho experimentos.
4. Dentro de cada pliegue, ajustar `StandardScaler` para k-NN/SVM y `SelectKBest(f_classif, k=20)` para todos. ANOVA detecta diferencias marginales entre clases, tiene bajo costo y no aplica un PCA nuevo. El número 20 se prefijó para reducir variables conservando dos tercios; no se eligió usando test. Árboles y bosque no requieren escalado.
5. Comparar sin compensación y con `RandomUnderSampler(sampling_strategy=0.1)`. La condición compensada conserva todos los fraudes del train disponible y diez legítimas por fraude. Se seleccionan variables antes de remuestrear. Validación y prueba nunca se balancean. Los recuentos por pliegue y por reajuste están guardados.
6. Buscar dos candidatos por modelo en cinco pliegues. Maximizar sensibilidad media, desempatar por precisión media y, en empate completo, conservar el primer candidato de la grilla. El ganador entre las ocho condiciones usa la misma regla y el orden documentado k-NN, árbol, SVM, bosque, primero sin y luego con compensación.
7. Terminar las ocho búsquedas y congelar todas las configuraciones antes de evaluar test. Reajustar cada una con semillas 42, 43 y 44, definidas de antemano. No cambiar parámetros, compensación ni umbrales tras observar prueba.

| Modelo | Búsqueda | Parámetros fijos y motivo |
| --- | --- | --- |
| k-NN | `n_neighbors`: 3, 7 | Vecindades pequeña y mayor para comparar suavidad; distancia euclídea y pesos uniformes. |
| Árbol | `max_depth`: 6, libre | Comparar complejidad acotada y libre; `min_samples_leaf=2` evita hojas de un solo ejemplo. |
| SVM | `C`: 1, 10 | Kernel RBF, `gamma='scale'`; comparar regularización moderada y menor. |
| Bosque propio | `max_depth`: 8, libre | 31 árboles impares, `max_features='sqrt'` y `min_samples_leaf=2`; diversidad y costo acotado. |

Son 80 ajustes de validación y 24 reajustes finales. La grilla es deliberadamente pequeña y constituye una limitación. No se reutiliza prueba para ampliarla.

## Random Forest propio

[forest.py](../src/fraudetection/reproduction/forest.py) implementa `fit`, `predict` y proporciones de votos. Por árbol genera una semilla distinta derivada de la general y una muestra bootstrap de igual tamaño que el entrenamiento disponible, con reemplazo. Ajusta un `DecisionTreeClassifier` independiente que selecciona variables aleatorias en cada división mediante `max_features`. Combina etiquetas por mayoría, sin promediar probabilidades de los árboles. Exige un número impar de árboles y dos clases en el entrenamiento; admite bootstrap que omitan una clase.

El número de árboles, profundidad, variables por división, tamaño mínimo de hoja y semilla son configurables. Es compatible con `clone`, `Pipeline` y `GridSearchCV`. No usa `RandomForestClassifier` ni `BaggingClassifier`. Las fracciones de votos no son probabilidades calibradas. Las semillas y cantidades de filas únicas por bootstrap se exportan en `bosque_diagnostico.json`.

## Resultados principales

Se eligió **árbol con compensación**, profundidad libre y hoja mínima 2, por sensibilidad de validación de **87,14 ± 2,87 %**. En test obtuvo sensibilidad **75,33 ± 4,62 %**, precisión **7,02 ± 0,55 %** y **500,33 ± 42,44 falsas alarmas** por ajuste. La selección se conserva aunque otro modelo tenga mayor sensibilidad en test.

Las seis métricas para las ocho condiciones están en [prueba_resumen.csv](../resultados/ejecucion/prueba_resumen.csv); los conteos enteros de cada repetición están en [prueba_repeticiones.csv](../resultados/ejecucion/prueba_repeticiones.csv). La compensación aumentó la sensibilidad en los cuatro modelos, con más falsas alarmas. El bosque compensado obtuvo sensibilidad 80,67 ± 2,31 % y precisión 60,42 ± 8,07 %, con 27,33 ± 9,07 falsas alarmas, sin sustituir al ganador de validación.

La desviación de CV usa `ddof=0` entre cinco pliegues. La de test usa `ddof=1` entre tres ajustes sobre un mismo test. Esta última mide variación del ajuste, no incertidumbre de muestreo ni un intervalo de confianza; modelos deterministas pueden tener desviación cero. El test solo contiene 50 fraudes, por lo que cada error representa dos puntos de sensibilidad por repetición. La muestra, la grilla acotada, ANOVA marginal y la partición aleatoria limitan las conclusiones. No se valida generalización temporal ni a otros bancos.

## Archivos y verificaciones

- `exploracion.json`, `descriptivos.csv`, `proporciones_clases.csv`: recuentos, limpieza, proporciones y resumen numérico.
- `particiones.npz`: IDs originales, train/test y los cinco pliegues. Los índices de pliegue se refieren a posiciones dentro del train.
- `busquedas/`, `validacion.csv`, `validacion_pliegues.csv`: candidatos, configuraciones y las seis métricas de CV.
- `remuestreo_pliegues.csv`, `caracteristicas.json`: recuentos y variables seleccionadas.
- `seleccion.json`, `protocolo.json`: ganador, semillas, versiones, huella SHA256 del CSV y duración.
- `prueba_repeticiones.csv`, `prueba_resumen.csv`, `predicciones.csv.gz`: valores individuales, agregados y predicciones auditables.
- `graficos/`, `analisis.html`, `analisis.md`: gráficos, matrices y análisis derivados de esos datos.
- `modelo_elegido.joblib`: pipeline local del ganador con semilla 42, generado por `run`, excluido de Git y del ZIP.
- [Presentación PPTX](../documentacion/presentacion/fraudetection.pptx), [PDF](../documentacion/presentacion/fraudetection.pdf) y [guion](../documentacion/presentacion/guion_defensa.md): 12 diapositivas principales y cuatro de respaldo, con nombres de ambos integrantes.

```bash
uv run --locked ruff check src tests scripts
uv run --locked ruff format --check src tests scripts
uv run --locked pytest -q
uv run --locked fraudetection audit
```

Las pruebas comprueban bootstrap, independencia, votación, reproducibilidad, entradas inválidas, particiones, métricas manuales y las ocho tuberías. La auditoría recalcula todas las métricas de test con scikit-learn a partir de las predicciones exportadas, comprueba las ocho condiciones, las semillas sin duplicados, los parámetros contra las búsquedas, resúmenes, ganador de validación y ausencia de solapamientos.

Para predecir otro CSV con los 30 predictores sin reajustar:

```bash
uv run --locked fraudetection predict --data ruta/transacciones.csv --output resultados/predicciones_nuevas.csv
```

La [revisión final](../documentacion/revision_final.md) documenta el cumplimiento de la consigna para este protocolo independiente. Una segunda ejecución con el mismo protocolo reprodujo exactamente las métricas, parámetros, particiones y predicciones; la evidencia está en `verificacion_reproduccion.json`. La suite completa del repositorio pasó 41 pruebas.

## Entrega

```bash
uv run --locked python scripts/package_delivery.py
```

Crea `entrega/fraudetection_entrega.zip` con código, dependencias, pruebas, resultados, documentación, PPTX, PDF y un manifiesto SHA256. Excluye el CSV, el entorno y los modelos binarios locales. Para reproducirlo, descomprimir, abrir una terminal en esa carpeta y seguir los comandos de ejecución. La descarga y el entrenamiento regeneran el modelo.

La entrega es por Blackboard el 26 de octubre de 2026 a las 23:59. La reserva de defensa corresponde al 27–28 de octubre. Ambos integrantes deben estudiar el código y practicar una exposición de 10–12 minutos; la ejecución automática no reemplaza la defensa. No se ha subido ningún archivo a Blackboard.

Fuentes técnicas: [estimadores de scikit-learn](https://scikit-learn.org/stable/developers/develop.html), [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html), [StratifiedKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html) y [prevención de fuga al remuestrear](https://imbalanced-learn.org/stable/common_pitfalls.html).
