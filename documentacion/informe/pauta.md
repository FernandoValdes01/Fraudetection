# Pauta de trabajo y aceptación

Fuente: [`IA_2026_P2.pdf`](../../IA_2026_P2.pdf), "Problema 2: Detección de fraude usando técnicas de aprendizaje supervisado", INFO1185, 9 de octubre de 2026. Este documento convierte la consigna en comprobaciones de trabajo. El PDF manda si hay diferencias. La carpeta se llama `informe` para organizar la documentación; **no se solicita informe escrito**.

**Estado del repositorio al 9 de octubre de 2026:** el pipeline, las ocho comparaciones, las métricas, los gráficos y la presentación Beamer están preparados. Quedan tareas de la dupla que requieren participación personal: ensayar la exposición de 10–12 minutos y entregar el material en Blackboard antes del plazo.

## Encargo y condiciones generales

- [x] Implementar un procedimiento reproducible de clasificación supervisada para detectar transacciones fraudulentas.
- [x] Comparar k-NN, árbol de decisión, SVM y un Random Forest implementado para el proyecto.
- [x] Priorizar la sensibilidad del fraude, o equivalentemente minimizar la tasa de falsos negativos. Usar la precisión del fraude para desempatar al seleccionar configuraciones.
- [x] Preparar diapositivas con metodología, resultados y análisis.
- [ ] Ensayar y defender oralmente el trabajo con participación de ambos integrantes.

### Datos de entrada

| Dato | Exigencia o contexto del enunciado | Criterio de aceptación |
| --- | --- | --- |
| Fuente | Credit Card Fraud Detection, Kaggle. | Se identifica la fuente y se usa su archivo de transacciones. |
| Tamaño | 284 807 registros; usar al menos 10 000. | La muestra analizada tiene 10 000 filas o más. Si se usa una muestra, se documenta cómo se obtuvo y cuántos fraudes conserva. Usar el conjunto completo es preferible para preservar los 492 fraudes disponibles. |
| Desbalance | 492 fraudes, aproximadamente 0,172 % del total. | Se cuentan filas y proporciones reales de `Class = 0` y `Class = 1` antes de entrenar. No se supone que la proporción de una muestra coincide exactamente con la cifra global. |
| Predictores | `Time`, `Amount`, `V1` a `V28`. | `Class` se excluye de `X`; no se agregan variables derivadas del objetivo. |
| Objetivo | `Class`: 0 legítima, 1 fraude. | Todas las métricas y matrices de confusión tratan el fraude como clase positiva. |
| PCA | `V1` a `V28` ya provienen de una transformación PCA y no tienen significado semántico directo disponible. | No se aplica una nueva reducción de dimensionalidad con PCA; sí se hace selección de características. |

## Pauta técnica

### 1. Exploración, limpieza y partición

- [x] Registrar número de filas, predictores, valores faltantes y posibles duplicados. Explicar las decisiones de limpieza con cifras antes y después.
- [x] Registrar cantidad y proporción de transacciones legítimas y fraudulentas. Mostrar el desbalance en la presentación.
- [x] Separar `X` e `y` y comprobar que `Class` no está entre las columnas predictoras.
- [x] Hacer una sola partición estratificada de 70 % entrenamiento y 30 % prueba con semilla fija. Guardar y reutilizar la misma partición en todos los experimentos.
- [x] Mantener en prueba la distribución original de clases. Reservar ese conjunto hasta la evaluación final; ninguna decisión de modelado se toma con él.
- [x] Escalar o normalizar donde corresponda y justificarlo según el clasificador. Ajustar cualquier transformación solo con los datos de entrenamiento disponibles en el pliegue.

### 2. Selección de características

- [x] Aplicar una técnica estadística de selección de características y justificarla.
- [x] Incluir la selección en cada pliegue de validación cruzada. No seleccionar columnas usando todos los datos antes de validar.
- [x] Tras elegir la configuración, volver a ajustar la selección con todo el entrenamiento y registrar los nombres de las características seleccionadas.

### 3. Random Forest propio

La dupla puede usar `DecisionTreeClassifier` como árbol base. No puede usar `RandomForestClassifier` ni `BaggingClassifier` para construir el ensamble solicitado. No hace falta programar la construcción interna de cada árbol.

- [x] Para cada árbol, extraer con reemplazo una muestra bootstrap del mismo tamaño que el entrenamiento disponible en esa condición y ese pliegue.
- [x] Entrenar un árbol independiente por muestra, con una semilla propia derivada de la semilla general.
- [x] Usar `max_features` del árbol para elegir aleatoriamente un subconjunto de características en **cada división**. Esto diferencia al bosque del bagging de árboles que consideran todas las variables.
- [x] Combinar las predicciones por votación mayoritaria y documentar que un empate favorece fraude.
- [x] Poder configurar número de árboles, profundidad máxima, cantidad de características por división y semilla general.
- [x] Separar claramente entrenamiento y predicción. La búsqueda de hiperparámetros evalúa esta implementación.
- [x] Explicar en código, documentación y diapositivas el bootstrap, la repetición posible de filas y la votación final.

### 4. Desbalance y matriz experimental

Para **cada** clasificador se comparan dos condiciones. La matriz completa tiene ocho configuraciones experimentales finales:

| Clasificador | Sin compensación | Con compensación |
| --- | --- | --- |
| k-NN | [ ] | [ ] |
| Árbol de decisión | [ ] | [ ] |
| SVM | [ ] | [ ] |
| Random Forest propio | [ ] | [ ] |

- [x] Implementar submuestreo aleatorio para los cuatro modelos compensados.
- [x] Usar la misma estrategia para los cuatro modelos y documentarla.
- [x] Documentar `sampling_strategy=0.1` y los recuentos de clase antes y después en [la exploración](exploracion.md).
- [x] Aplicar cualquier remuestreo **solo** al entrenamiento de cada pliegue de validación. No balancear validación ni prueba.
- [x] En el Random Forest propio, generar los bootstrap desde el conjunto de entrenamiento de la condición experimental, ya compensado cuando corresponda.

### 5. Validación y búsqueda

- [x] Usar validación cruzada estratificada de **cinco pliegues** dentro del 70 % de entrenamiento.
- [x] Reutilizar exactamente los mismos pliegues para comparar los cuatro modelos y ambas condiciones.
- [x] Buscar hiperparámetros con Grid Search y mantener un espacio acotado para cada clasificador.
- [x] En cada pliegue, ajustar escalado, selección y tratamiento del desbalance solo con su parte de entrenamiento. El modelo se evalúa en la parte de validación sin balancearla.
- [x] Elegir por **mayor sensibilidad media de la clase 1**. Si hay empate, usar la **precisión de la clase 1** como segundo criterio.
- [x] Registrar para las ocho configuraciones parámetros elegidos, sensibilidad media y desviación estándar entre pliegues en `resultados/cv_resumen.csv` y en la diapositiva de respaldo.
- [x] No usar prueba para elegir características, hiperparámetros, estrategia de compensación ni umbral de decisión.

**Decisión de implementación en este repositorio:** la búsqueda toma una submuestra estratificada de 50.000 filas desde el entrenamiento completo para acotar el costo de k-NN. Los ocho experimentos comparten esos mismos pliegues. Después, cada configuración elegida se reajusta con todo el entrenamiento y se evalúa en toda la partición de prueba.

### 6. Evaluación final y métricas

Después de seleccionar las configuraciones con validación, reajustarlas sobre el entrenamiento completo y evaluarlas en la fase final con semillas predefinidas. Mostrar validación y prueba por separado. No retocar modelos después de mirar el test.

| Métrica exigida | Interpretación o cálculo con fraude positivo |
| --- | --- |
| Sensibilidad | `TP / (TP + FN)`; fraudes detectados. |
| Especificidad | `TN / (TN + FP)`; legítimas correctamente descartadas. |
| Precisión | `TP / (TP + FP)`; proporción de alertas que son fraude. |
| F1-score | Media armónica de precisión y sensibilidad. |
| Exactitud | `(TP + TN) / (TP + TN + FP + FN)`. |
| Tasa de falsos negativos | `FN / (TP + FN) = 1 - sensibilidad`. |

- [x] Reportar las seis métricas para **cada modelo y condición**, con media y desviación estándar, y mostrar conteos de la matriz de confusión de la configuración elegida.
- [x] Repetir el ajuste final con cinco semillas, mantener fijo el mismo test y reportar cada repetición en `resultados/test_repeticiones.csv`.
- [x] Distinguir las desviaciones entre pliegues de validación de las desviaciones de las repeticiones en prueba. No usar los cinco pliegues como si fueran cinco conjuntos de prueba independientes.

### 7. Análisis que debe responder la presentación

- [x] Explicar por qué la exactitud engaña con esta prevalencia. Un clasificador que siempre predice legítimo tiene aproximadamente 99,827 % de exactitud en el conjunto original y 0 % de sensibilidad al fraude.
- [x] Comparar detección de fraudes y falsas alarmas con y sin compensación.
- [x] Comparar el árbol individual con el Random Forest propio y explicar qué aporta combinar árboles.
- [x] Identificar la configuración elegida por validación y su desempeño final en prueba.
- [x] Explicar limitaciones y la consecuencia de clasificar todo como fraude: sensibilidad perfecta, pero todas las transacciones legítimas se convierten en falsas alarmas.
- [x] Mantener la minimización de falsos negativos como prioridad y usar el análisis de falsos positivos para explicar el costo de las alertas.

## Entrega y presentación

| Entregable | Criterio de aceptación |
| --- | --- |
| Código | Notebook o archivos Python que reproduzcan exploración, entrenamiento, búsqueda, evaluación y Random Forest propio. |
| README | Dependencias y versiones principales, ubicación esperada del dataset, orden de ejecución y semillas. El dataset no necesita adjuntarse. |
| Presentación | PowerPoint o equivalente con metodología, resultados, análisis y conclusiones. Si se usa una herramienta en línea, adjuntar además PDF exportado. |
| Defensa | Exposición de 10 a 12 minutos por dupla, seguida de preguntas. Ambos participan y conocen todo el desarrollo. Se puede pedir ejecutar o revisar código. |

**Estado de entrega:** código, README, fuente Beamer, PDF y copia PowerPoint están en el repositorio. Pendientes antes de la fecha de entrega: ensayar la defensa y subir el material final a Blackboard.

La entrega es por **Blackboard el 26 de octubre de 2026 a las 23:59 horas**. La defensa requiere reservar cita entre el **27 y el 28 de octubre de 2026**. El PDF no pide informe escrito.

### Estructura sugerida de las diapositivas

El enunciado sugiere entre 10 y 12 diapositivas principales:

1. Portada y objetivo, con prioridad de falsos negativos, una diapositiva.
2. Exploración y distribución de clases, una diapositiva.
3. Metodología, partición, preprocesamiento, selección, compensación, validación y control de fuga, una o dos diapositivas.
4. Random Forest propio, bootstrap, árboles, características aleatorias, votación, bagging y parámetros, una o dos diapositivas.
5. Espacio de hiperparámetros, elecciones y sensibilidad media con desviación estándar de validación, una diapositiva.
6. Resultados de prueba de los ocho experimentos con las métricas pedidas, apoyados por gráficos o matrices de confusión, dos diapositivas.
7. Análisis crítico de compensación, falsas alarmas, árbol frente a bosque y exactitud, una diapositiva.
8. Conclusiones, configuración seleccionada, desempeño final, limitaciones y mejoras, una diapositiva.

Las tablas extensas, matrices restantes y otros resultados pueden ir en diapositivas de respaldo. Todas las métricas exigidas deben estar en las principales o en las de respaldo.

## Rúbrica de evaluación

### Código, máximo 40 puntos

| Criterio | Máximo |
| --- | ---: |
| Preprocesamiento y selección correctos, sin fuga. | 8 |
| Random Forest propio: bootstrap, aleatoriedad de características, árboles independientes, votación y parámetros. | 14 |
| Cuatro clasificadores, dos condiciones, validación y búsqueda. | 12 |
| Organización, documentación técnica, ejecución y reproducibilidad. | 6 |
| **Total código** | **40** |

### Presentación, máximo 60 puntos

| Criterio | Máximo |
| --- | ---: |
| Problema, objetivo, distribución de clases y desafíos. | 5 |
| Justificación de preprocesamiento, selección, compensación y validación. | 10 |
| Random Forest propio, bootstrap, bagging y votación. | 10 |
| Hiperparámetros y resultados completos de validación y prueba. | 15 |
| Análisis de falsos negativos, falsas alarmas, desbalance y árbol frente a ensamble. | 10 |
| Conclusiones fundamentadas y límites. | 5 |
| Claridad visual, organización, tiempo y participación de ambos. | 5 |
| **Total presentación** | **60** |

En cada criterio de código y presentación se aplica uno de estos factores al máximo correspondiente:

| Nivel | Factor | Descripción |
| --- | ---: | --- |
| Excelente | 1,00 | Completo, correcto y fundamentado. |
| Satisfactorio | 0,66 | Aspectos principales cumplidos con omisiones menores. |
| Insuficiente | 0,33 | Desarrollo parcial, errores relevantes o justificación limitada. |
| Deficiente | 0,00 | Ausente o incorrecto. |

### Defensa y puntaje final

El profesor realiza cinco preguntas, de hasta 10 puntos cada una, para un máximo de **50 puntos** de defensa. Evalúa explicaciones, relación con el código y fundamento de los resultados.

| Nivel de respuesta | Puntos por pregunta |
| --- | ---: |
| Excelente: correcta, fundamentada y vinculada con implementación y resultados. | 9 a 10 |
| Muy bueno: aspectos principales correctos, con omisiones menores. | 7 a 8 |
| Satisfactorio: comprensión básica, parcial o con conexiones limitadas. | 5 a 6 |
| Insuficiente: vaga o con errores conceptuales relevantes. | 3 a 4 |
| Deficiente: no responde o desconoce el procedimiento y sus fundamentos. | 0 a 2 |

Si `PC` es código sobre 40, `PP` presentación sobre 60 y `PD` defensa sobre 50, el factor de defensa es `FP = PD / 50` y el puntaje final de la dupla es `Pfinal = (PC + PP) × FP`. El puntaje de 0 a 100 se convierte a nota según la escala de la asignatura.
