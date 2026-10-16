# Auditoría de la actividad INFO1185

Fecha: 15 de octubre de 2026. Commit auditado: `543bebea74d605fc1b62ef5d5584ab9d87a98b88`, rama `main`.

**Cierre de correcciones, 15 de octubre:** H1, H2 y H3 resueltos en el checkout. El PDF Beamer ahora conserva 12 diapositivas principales y dispone de cuatro respaldos. Incluye comparación árbol/bosque, bagging, clasificadores triviales, límites, control de fuga, rangos y justificación metodológica. El README distingue la organización de PDF y PowerPoint. El generador toma tamaño de búsqueda/pliegues del CSV y conserva campos previos de metadatos. Se añadieron cinco casos de regresión; la suite completa pasa 36 pruebas, Ruff y formato. Se regeneraron el PDF con Docker `blang/latex:ubuntu` y `latexmk`, el PowerPoint alternativo, el manifiesto y el ZIP de entrega. Los CSV de resultados experimentales se conservan. Defensa, reserva y envío a Blackboard siguen siendo acciones personales.

El resto de este documento conserva la evidencia y el dictamen de la auditoría inicial, anteriores a estas correcciones.

Se ejecutaron `git fetch origin` y `git pull --ff-only` antes de auditar. El remoto ya estaba actualizado y el checkout no tenía cambios locales. La referencia de requisitos fue el PDF original [IA_2026_P2.pdf](../IA_2026_P2.pdf), páginas 1–9, contrastado con la pauta interna. No se modificaron código, resultados ni presentaciones.

**Dictamen inicial: la implementación y los resultados de las ejecuciones entregadas satisfacen los requisitos técnicos revisados. La presentación PDF identificada como principal tiene omisiones de contenido exigido y no coincide completamente con su PowerPoint alternativo. Por eso no corresponde declarar toda la actividad lista al 100 %.** Se encontró además un defecto de metadatos al generar reportes de ejecuciones principales con tamaño de muestra personalizado. Ambos aspectos se corrigieron según el cierre anterior.

Se revisaron por separado los dos protocolos existentes. Sus distintas muestras, SVM, orden de selección/remuestreo, semillas y ganadores están documentados y no constituyen por sí mismos un error.

| Dato | Protocolo principal | Protocolo independiente |
| --- | --- | --- |
| Código | `src/fraudetection/` | `src/fraudetection/reproduction/` |
| Datos utilizados | 283.726 filas limpias | Muestra estratificada de 100.000 filas limpias |
| Entrenamiento / prueba | 198.608 / 85.118 | 70.000 / 30.000 |
| Fraudes en entrenamiento / prueba | 331 / 142 | 117 / 50 |
| Búsqueda | Submuestra fija de 50.000 filas de entrenamiento, con 83 fraudes | Todo su entrenamiento de 70.000 filas |
| Validación | Cinco pliegues estratificados compartidos | Cinco pliegues estratificados compartidos |
| Semillas finales | 42, 101, 202, 303, 404 | 42, 43, 44 |
| Ganador de validación | Bosque propio compensado, 21 árboles, profundidad 6 | Árbol compensado, profundidad libre, hoja mínima 2 |
| Sensibilidad CV del ganador | 87,8676 % ± 5,5221 puntos | 87,1377 % ± 2,8712 puntos |
| Sensibilidad test del ganador | 80,4225 % ± 0,3149 puntos | 75,3333 % ± 4,6188 puntos |
| Presentación | `defensa_fraude.pdf`, Beamer, 14 páginas; PPTX alternativo | `fraudetection.pdf` / `.pptx`, 16 diapositivas |

Los valores porcentuales se redondean en las diapositivas. La desviación en prueba mide variación entre ajustes sobre un mismo test, no incertidumbre poblacional ni conjuntos de prueba independientes.

## Hallazgos confirmados

| Prioridad | Hallazgo | Efecto | Esfuerzo de corrección | Riesgo de corrección | Confianza |
| --- | --- | --- | --- | --- | --- |
| Alta | H1. Falta parte del análisis exigido en el PDF principal | Cumplimiento parcial de las preguntas 4.7.3 y 4.7.5 y de la rúbrica de presentación | S | Bajo | Alta |
| Media | H2. La metodología y búsqueda del PDF principal no explicitan elementos requeridos | Menor evidencia de control de fuga y de las decisiones de modelado en la presentación evaluada | S | Bajo | Alta |
| Media | H3. El reporte principal sobrescribe el tamaño real de búsqueda en los metadatos | Un reporte de una ejecución personalizada puede declarar un protocolo distinto del ejecutado | S | Bajo | Alta |

S significa un cambio acotado en los archivos citados. No se asigna una nota: tiempo, respuestas y participación de la defensa son parte de la evaluación y no se comprueban con los archivos.

### H1. Completar el análisis del PDF principal

El enunciado, página 5, exige comparar árbol y bosque, explicar qué aporta combinar árboles y analizar las consecuencias de clasificar todo como fraude. El PDF principal muestra bootstrap, voto, curvas, una matriz y el resultado final, pero no desarrolla esas dos respuestas. Su única limitación explícita es la incertidumbre por disponer de 142 fraudes de prueba.

Evidencia revisada directamente:

- [defensa_fraude.tex:173](../documentacion/presentacion/defensa_fraude.tex#L173), página 6 del PDF: esquema bootstrap, árboles y voto; no explica el aporte del bagging al comportamiento observado.
- [defensa_fraude.tex:238](../documentacion/presentacion/defensa_fraude.tex#L238), páginas 11–12: matriz del ganador y cierre, sin comparación explícita árbol/bosque ni escenario de predecir todo fraude.
- [presentation.py:604](../src/fraudetection/presentation.py#L604), diapositiva 11 del PPTX alternativo: sí presenta la comparación y las 84.976 falsas alarmas del clasificador siempre fraude.
- [presentation.py:640](../src/fraudetection/presentation.py#L640), diapositiva 12 del PPTX: sí añade límites sobre duplicados, SVM lineal, ANOVA y búsqueda acotada.
- [README.md:96](../README.md#L96): describe el PPTX como una copia con el mismo contenido. Esa equivalencia no se cumple.

La comparación puede usar los resultados ya existentes: árbol compensado con sensibilidad 83,10 % y precisión 33,58 %, frente a bosque compensado con sensibilidad 80,42 % y precisión 67,51 %. El bosque no supera al árbol compensado en sensibilidad de prueba; se mantiene como ganador porque fue seleccionado por CV. Clasificar todo como fraude produciría sensibilidad 100 %, especificidad 0 % y 84.976 falsas alarmas en ese test.

Corrección propuesta: incorporar esas respuestas y el papel del bagging a las diapositivas principales o de respaldo de Beamer, añadir limitaciones/metas de mejora y alinear la descripción del PPTX. No requiere nuevos experimentos ni cambiar el ganador por observar prueba. Verificar después el PDF exportado y su correspondencia con la fuente y los CSV.

### H2. Explicitar metodología, control de fuga y búsqueda en el PDF

El enunciado, páginas 3–4 y 6, pide justificar selección e hiperparámetros y explicar cómo se evitó la fuga. En el PDF principal aparecen las etiquetas de escalado, ANOVA y submuestreo, y se afirma que el test está reservado. No se explica expresamente que las tres transformaciones se ajustan únicamente con el entrenamiento de cada pliegue. La tabla de respaldo presenta parámetros ganadores, pero omite los candidatos evaluados.

Evidencia:

- [defensa_fraude.tex:154](../documentacion/presentacion/defensa_fraude.tex#L154), página 5: enumera escalado, ANOVA y razón 1:10, sin justificación de la selección ni explicación del ajuste dentro del pliegue.
- [defensa_fraude.tex:269](../documentacion/presentacion/defensa_fraude.tex#L269), página 13: muestra parámetros seleccionados y sensibilidad ± desviación, sin rangos de búsqueda.
- [experiments.py:55](../src/fraudetection/experiments.py#L55): la grilla sí existe en el código principal.
- [experiments.py:81](../src/fraudetection/experiments.py#L81): la tubería implementa correctamente el aislamiento de las transformaciones.
- [presentation.py:353](../src/fraudetection/presentation.py#L353) y [presentation.py:713](../src/fraudetection/presentation.py#L713): el PPTX alternativo sí explica el procesamiento dentro de cada pliegue y enumera los rangos.

Corrección propuesta: trasladar al PDF los rangos de k, profundidad, hoja mínima, C y número de árboles; justificar brevemente los rangos y ANOVA; explicar que ninguna transformación se aprende sobre validación o prueba. Distinguir reservar el test de prevenir fuga entre entrenamiento y validación. El defecto está en la evidencia presentada, no en una fuga encontrada en el código.

### H3. Conservar los metadatos reales al generar el reporte

[experiments.py:542](../src/fraudetection/experiments.py#L542) admite `--search-sample-size`. La ejecución registra el tamaño real y otros datos de protocolo en [experiments.py:571](../src/fraudetection/experiments.py#L571). Después, [presentation.py:818](../src/fraudetection/presentation.py#L818) reconstruye `metadata.json` y fija `search_sample_rows` desde la constante global, 50.000, en lugar de conservar el valor de la ejecución o leer `search_rows` del CSV. También elimina campos como `search_sample_fraud` y `cv_seed`.

La comprobación aislada se ejecutó en un directorio temporal, con datos sintéticos y renderizado simulado. Un CSV y metadatos con búsqueda de 10.000 filas terminaron con `search_sample_rows = 50000`; `cv_seed` dejó de existir. No se alteraron resultados del repositorio.

Los artefactos actuales usan realmente 50.000 filas, de modo que este defecto no invalida sus cifras. Sí afecta la reproducibilidad declarada al emplear una opción admitida por el comando. Corrección propuesta: preservar y actualizar los metadatos existentes, tomando el tamaño efectivo de la ejecución, y comprobar el caso no predeterminado con una prueba pequeña.

## Matriz contra el PDF original

“Cumple” corresponde al código y los artefactos presentes. “Parcial” indica contenido faltante en el PDF principal; no se atribuye ese defecto al protocolo independiente.

| Apartado | Requisito | Estado y evidencia |
| --- | --- | --- |
| 3 | Dataset indicado y al menos 10.000 registros | Cumple. CSV real con 284.807 filas y 492 fraudes; ambos protocolos superan el mínimo. Huella contrastada con los metadatos. |
| 3 | Time, Amount y V1–V28; fraude como clase positiva | Cumple. `data.py:11`, `reproduction/config.py:9`, funciones de métricas y etiquetas de predicciones. |
| 3 | No aplicar una nueva reducción PCA | Cumple. Selección ANOVA de 20 variables; sin importaciones PCA en Python. |
| 4.1.1 | Explorar filas, características, faltantes y duplicados; justificar limpieza | Cumple. `data.py:51`, `documentacion/informe/exploracion.md:24`, `reproduction/data.py:62`. Se verificaron 0 faltantes y 1.081 duplicados, 19 de fraude. |
| 4.1.2 | Cantidad y proporción de clases | Cumple. CLI de inspección y tablas de exploración; presentación muestra el desbalance. |
| 4.1.3 | Excluir Class de X | Cumple. `data.py:75`, `reproduction/data.py:84`; reconstrucción y pruebas. |
| 4.1.4 | Partición estratificada 70/30, semilla fija y compartida | Cumple. `data.py:71`, `reproduction/data.py:86`; índices y etiquetas cotejados con el CSV. |
| 4.1 | Test reservado y sin balancear | Cumple en código y artefactos. La selección precede la evaluación; las etiquetas conservan prevalencia natural después de la limpieza. |
| 4.1.5 | Escalado cuando corresponde y justificación | Implementación correcta para k-NN/SVM; árboles sin escalado. Explicación del PDF principal parcial, H2. |
| 4.2 | Técnica de selección, justificación, registro de variables finales | ANOVA dentro de tuberías y variables exportadas. Falta desarrollar la justificación en el PDF principal, H2. |
| 4.2 | Selección integrada dentro de la validación | Cumple en ambos códigos. No se seleccionan columnas con el test. |
| 4.3.1 | Bootstrap con reemplazo y tamaño igual al entrenamiento disponible | Cumple. `forest.py:56`, `reproduction/forest.py:63`; pruebas y diagnósticos. |
| 4.3.2 | Árbol independiente por muestra | Cumple. Se construye un DecisionTreeClassifier por iteración. |
| 4.3.3 | Subconjunto aleatorio por división mediante max_features | Cumple. Ambos bosques usan sqrt sobre las variables seleccionadas. |
| 4.3.4 | Mayoría y regla de empate o número impar | Cumple. Principal resuelve empate hacia fraude; independiente exige cantidad impar. |
| 4.3.5 | Configurar número de árboles, profundidad, características y semilla | Cumple en las dos interfaces de estimador. |
| 4.3.6 | Semillas diferentes por árbol derivadas de una general | Cumple. Generadores con semilla y control de unicidad; pruebas de reproducibilidad. |
| 4.3.7 | Métodos de entrenamiento y predicción identificados | Cumple. `fit` y `predict`, compatibles con clone y GridSearchCV. |
| 4.3 | No construir el ensamble con RandomForestClassifier o BaggingClassifier | Cumple. No se encontraron importaciones de esas clases en los 23 archivos Python revisados. |
| 4.3 / 6 | Explicar bootstrap, bagging y predicción del ensamble | PDF principal explica reemplazo y voto; aporte del bagging y comparación observada insuficientemente desarrollados, H1. |
| 4.4 | Comparar con y sin compensación para cada modelo | Cumple. Ocho experimentos en cada protocolo. |
| 4.4 | Documentar estrategia, parámetros y cantidades antes/después | Cumple. Razón 0,1; exploración principal y `remuestreo_pliegues.csv` / `caracteristicas.json` independientes. |
| 4.4 | Remuestrear solo train de cada pliegue; bootstrap desde esa condición | Cumple. RandomUnderSampler dentro de la tubería, antes del clasificador; validación/test no se remuestrean. |
| 4.5.1–3 | Cuatro modelos, dos condiciones, cinco pliegues compartidos | Cumple. Listas de pliegues reutilizadas; ocho filas de resumen por protocolo. |
| 4.5.4–5 | Búsqueda acotada y justificada, sobre el bosque propio | Cumple en implementación. Rangos ausentes en el PDF principal, H2. |
| 4.5.6 | Máxima sensibilidad media; precisión como desempate | Cumple. `experiments.py:105`, `reproduction/metrics.py:47`; ganador conservado aunque otro modelo obtenga más sensibilidad en test. |
| 4.5.7 | Parámetros elegidos, sensibilidad media y desviación CV | Cumple. `cv_resumen.csv`, `validacion.csv` y respaldos de ambas presentaciones. |
| 4.5 | Transformaciones solo en train del pliegue y sin seleccionar con test | Cumple en código. Explicación del PDF principal parcial, H2. |
| 4.6 | Reajustar configuraciones con todo el entrenamiento | Cumple. Principal usa 198.608 filas, independiente 70.000; mismo test para las repeticiones de cada protocolo. |
| 4.6 | Seis métricas con media y desviación por modelo/condición | Cumple. Sensibilidad, especificidad, precisión, F1, exactitud y FNR; tablas de las ocho condiciones en ambos PDF. |
| 4.6 | Separar validación y prueba, sin ajustes posteriores por test | Cumple en el flujo de código y las tablas. Ganador por CV, semillas finales fijas. |
| 4.7.1 | Exactitud engañosa y clasificador siempre legítimo | Cumple. PDF principal p. 12: 99,833 % sobre datos limpios y sensibilidad 0 %. Independiente incluye sus referencias triviales. |
| 4.7.2 | Detección y falsas alarmas al compensar | Cumple. Gráficos, métricas y análisis de cada protocolo. |
| 4.7.3 | Árbol frente a bosque y aporte del ensamble | Parcial en el PDF principal, H1. Comparación explícita presente en el PPTX alternativo y en la presentación independiente. |
| 4.7.4 | Ganador por validación y desempeño final | Cumple. No se mezclaron ganadores o resultados de protocolos distintos. |
| 4.7.5 | Límites y consecuencia de clasificar todo fraude | Parcial en el PDF principal, H1. El segundo escenario está ausente allí; sí está en el PPTX alternativo y en el protocolo independiente. |
| 5.1 | Código que reproduzca todo el procedimiento | Cumple para las ejecuciones entregadas. Defecto de metadatos en el caso personalizado, H3. |
| 5.2 | README, dependencias/versiones, dataset, orden y semillas | Cumple mediante README y documentación enlazada/configuración. Lock consistente; H3 afecta metadatos de futuras ejecuciones personalizadas. |
| 5.3 / 6 | Presentación con metodología, resultados, análisis y conclusiones | Archivos presentes. PDF principal con 12 diapositivas principales y 2 respaldos; independiente 12 + 4. Omisiones H1/H2. |
| 5.4 / 6 | Exposición de 10–12 minutos y ambos conocen el desarrollo | Pendiente de acreditación personal. El repositorio contiene guiones/material de estudio. |
| 5 | Entregar por Blackboard el 26 de octubre, 23:59; reserva 27–28 | Acciones externas; no se verificaron en esta auditoría. |
| 5 | Informe escrito | No exigido. Su ausencia no se considera un incumplimiento. |

## Comprobaciones ejecutadas en esta auditoría

| Comprobación | Resultado real |
| --- | --- |
| `git fetch origin`; `git pull --ff-only` | Correctos; ya actualizado, sin divergencia de `main`. |
| `uv lock --check --offline` | Correcto; 32 paquetes resueltos sin modificar el lock. |
| `PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider` | 31 pruebas pasaron. |
| Ruff 0.17.0, `check --no-cache .` | Sin errores. Se usó el ejecutable ya existente en la caché local, sin instalar herramientas. |
| Ruff 0.17.0, `format --check --no-cache .` | 37 archivos ya formateados; ningún cambio aplicado. |
| AST de todos los Python versionados | 23 archivos parseados; sin importaciones prohibidas de PCA/RandomForestClassifier/BaggingClassifier. |
| Inspección del CSV real con el módulo CLI | Reprodujo 284.807 filas, 492 fraudes, 1.081 duplicados, 0 faltantes; 283.726 filas y 473 fraudes tras limpiar. |
| Integridad de resultados principales | Huella del dataset, índices y etiquetas del test correctos; fórmulas de las 40 filas de métricas recalculadas desde TN/FP/FN/TP y ocho medias/desviaciones verificadas. |
| Repetición de las ocho búsquedas principales, sin escribir artefactos | Coincidieron los parámetros ganadores, sensibilidad media/desviación y precisión media con `cv_resumen.csv`. Se recorrió la grilla completa de cada condición, 160 ajustes CV, más sus refits. |
| Reajuste del bosque principal elegido, cinco semillas | Coincidieron todas sus métricas y conteos. Para semilla 42, coincidió cada predicción exportada y la matriz TN=84.923, FP=53, FN=27, TP=115. |
| `PYTHONPATH=src .venv/bin/python -m fraudetection audit` | Ocho experimentos, 24 repeticiones, 30.000 filas de test, métricas recalculadas desde predicciones y particiones disjuntas. |
| Reconstrucción independiente desde el CSV | Coincidieron exactamente muestra, identificadores originales, train/test, etiquetas y los cinco pliegues guardados. |
| Repetición de las ocho búsquedas independientes, sin escribir artefactos | Coincidieron candidatos y parámetros; las seis métricas de CV por media/desviación difirieron como máximo en 1,11 × 10⁻¹⁶. Son dos candidatos por condición y cinco pliegues, 80 ajustes CV. |
| Reajuste del ganador independiente, semillas 42/43/44 | Cero diferencias en sus tres predicciones completas guardadas. |
| Manifiesto de entrega | 100 entradas, cero archivos faltantes, cero hashes distintos. El único versionado fuera del manifiesto original es `data/raw/.gitkeep`, que no es un entregable necesario. |
| Lectura de PDF y PPTX | Extracción de ambos PDF y PPTX; cotejo de cifras, tablas y contenidos con los resultados propios de cada protocolo. |
| Verificación visual acotada | Se renderizaron la tabla completa principal p. 14, el cierre principal p. 12 y la tabla independiente p. 8; sin desbordamientos evidentes en esas páginas. Las cajas de texto extraídas de ambos PDF no exceden sus páginas. |
| Caso sintético de metadatos personalizados | Confirmó H3, con salidas únicamente en un directorio temporal. |

## Entrega, límites y siguiente acción

El script `scripts/package_delivery.py` reúne código, dependencias, documentación, resultados y presentaciones, excluyendo dataset, entorno y modelos `.joblib`. El manifiesto existente coincide con los archivos. El ZIP `entrega/fraudetection_entrega.zip` no existe actualmente en este checkout; está ignorado por Git y debe generarse al preparar el envío. El enunciado no exige un ZIP en particular, por lo que esto es un pendiente operativo, no la ausencia de un requisito técnico. Las afirmaciones históricas de que se generó no demuestran que el archivo siga presente.

No se hizo una instalación desde un entorno vacío, una descarga nueva del dataset, compilación de Beamer ni exportación de PowerPoint. Tampoco se volvió a entrenar cada una de las 40 filas finales del protocolo principal: se comprobaron sus fórmulas y resúmenes y se reprodujeron los cinco ajustes del ganador. En el protocolo independiente se recalcularon las métricas de las 24 predicciones guardadas y se reajustaron las tres del ganador; no se reajustaron las otras siete condiciones finales. La revisión visual fue acotada a las páginas descritas. No se ejecutó un escáner externo de vulnerabilidades de dependencias. Esas limitaciones no se presentan como pruebas aprobadas.

La defensa oral, el tiempo real, la participación de ambos, la reserva y el envío a Blackboard requieren comprobación de los integrantes. No se publicaron revisiones, no se crearon commits y no se subió material.

La siguiente acción con mayor impacto es completar el PDF Beamer principal con el análisis y la metodología identificados en H1/H2. Después corresponde regenerar el PDF y el paquete. H3 puede corregirse sin volver a seleccionar modelos ni cambiar los resultados entregados.
