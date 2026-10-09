# Pauta de trabajo y aceptación

Fuente: [`IA_2026_P2.pdf`](../../IA_2026_P2.pdf), "Problema 2: Detección de fraude usando técnicas de aprendizaje supervisado", INFO1185, 9 de octubre de 2026. Este documento convierte la consigna en comprobaciones de trabajo. El PDF manda si hay diferencias. La carpeta se llama `informe` para organizar la documentación; **no se solicita informe escrito**.

## Encargo y condiciones generales

- [ ] Trabajar en pareja e implementar un procedimiento reproducible de clasificación supervisada para detectar transacciones fraudulentas.
- [ ] Comparar k-NN, árbol de decisión, SVM y un Random Forest implementado por la dupla.
- [ ] Priorizar la sensibilidad del fraude, o equivalentemente minimizar la tasa de falsos negativos. Usar la precisión del fraude para desempatar al seleccionar configuraciones.
- [ ] Presentar metodología, resultados y análisis en diapositivas, y defender oralmente el trabajo con participación de ambos integrantes.

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

- [ ] Registrar número de filas, predictores, valores faltantes y posibles duplicados. Explicar las decisiones de limpieza con cifras antes y después.
- [ ] Registrar cantidad y proporción de transacciones legítimas y fraudulentas. Mostrar el desbalance en la presentación.
- [ ] Separar `X` e `y` y comprobar que `Class` no está entre las columnas predictoras.
- [ ] Hacer una sola partición estratificada de 70 % entrenamiento y 30 % prueba con semilla fija. Guardar y reutilizar la misma partición en todos los experimentos.
- [ ] Mantener en prueba la distribución original de clases. Reservar ese conjunto hasta la evaluación final; ninguna decisión de modelado se toma con él.
- [ ] Escalar o normalizar donde corresponda y justificarlo según el clasificador. Ajustar cualquier transformación solo con los datos de entrenamiento disponibles en el pliegue.

### 2. Selección de características

- [ ] Aplicar al menos una técnica basada en modelo, criterio estadístico o búsqueda, y justificarla. La consigna menciona información mutua, importancia de variables y Sequential Forward Selection como ejemplos.
- [ ] Incluir la selección en cada pliegue de validación cruzada. No seleccionar columnas usando todos los datos antes de validar.
- [ ] Tras elegir la configuración, volver a ajustar la selección con todo el entrenamiento y registrar los nombres de las características seleccionadas.

### 3. Random Forest propio

La dupla puede usar `DecisionTreeClassifier` como árbol base. No puede usar `RandomForestClassifier` ni `BaggingClassifier` para construir el ensamble solicitado. No hace falta programar la construcción interna de cada árbol.

- [ ] Para cada árbol, extraer con reemplazo una muestra bootstrap del mismo tamaño que el entrenamiento disponible en esa condición y ese pliegue.
- [ ] Entrenar un árbol independiente por muestra, con una semilla propia derivada de la semilla general.
- [ ] Usar `max_features` del árbol para elegir aleatoriamente un subconjunto de características en **cada división**. Esto diferencia al bosque del bagging de árboles que consideran todas las variables.
- [ ] Combinar las predicciones por votación mayoritaria. Usar un número impar de árboles o programar y documentar una regla de empate.
- [ ] Poder configurar número de árboles, profundidad máxima, cantidad de características por división y semilla general.
- [ ] Separar claramente las funciones o métodos de entrenamiento y predicción. La búsqueda de hiperparámetros debe evaluar esta implementación.
- [ ] Explicar en código y defensa el bootstrap, la repetición posible de filas y la votación final.

### 4. Desbalance y matriz experimental

Para **cada** clasificador se comparan dos condiciones. La matriz completa tiene ocho configuraciones experimentales finales:

| Clasificador | Sin compensación | Con compensación |
| --- | --- | --- |
| k-NN | [ ] | [ ] |
| Árbol de decisión | [ ] | [ ] |
| SVM | [ ] | [ ] |
| Random Forest propio | [ ] | [ ] |

- [ ] Implementar al menos una estrategia explícita de compensación. Son válidos el submuestreo, sobremuestreo aleatorio, datos sintéticos o ponderación de clases cuando el modelo lo permita.
- [ ] Si se usa la misma estrategia para los cuatro modelos, documentarla; si se usan estrategias distintas, justificar el motivo.
- [ ] Documentar sus parámetros y, cuando aplique, los recuentos por clase antes y después de aplicarla.
- [ ] Aplicar cualquier remuestreo **solo** al entrenamiento de cada pliegue de validación. No balancear validación ni prueba. Una tubería de `imbalanced-learn` puede mantener este orden.
- [ ] En el Random Forest propio, generar los bootstrap desde el conjunto de entrenamiento que corresponde a cada condición experimental, ya compensado cuando corresponda.

### 5. Validación y búsqueda

- [ ] Usar validación cruzada estratificada de **cinco pliegues** dentro del 70 % de entrenamiento.
- [ ] Reutilizar exactamente los mismos pliegues para comparar los cuatro modelos y ambas condiciones.
- [ ] Buscar hiperparámetros con Grid Search, Random Search o un método propio equivalente. Acotar y justificar el espacio para cada clasificador.
- [ ] En cada pliegue, ajustar escalado, selección y tratamiento del desbalance solo con su parte de entrenamiento. El modelo se evalúa en la parte de validación sin balancearla.
- [ ] Elegir por **mayor sensibilidad media de la clase 1**. Si hay empate, usar la **precisión de la clase 1** como segundo criterio. Dejar el procedimiento de desempate reproducible.
- [ ] Para cada una de las ocho configuraciones, registrar hiperparámetros elegidos, sensibilidad media y desviación estándar entre pliegues.
- [ ] No usar prueba para elegir características, hiperparámetros, estrategia de compensación ni umbral de decisión.

### 6. Evaluación final y métricas

Después de seleccionar las configuraciones con validación, reajustarlas sobre el entrenamiento completo y evaluarlas una vez en la partición de prueba reservada. Mostrar validación y prueba por separado. No retocar modelos después de mirar el test.

| Métrica exigida | Interpretación o cálculo con fraude positivo |
| --- | --- |
| Sensibilidad | `TP / (TP + FN)`; fraudes detectados. |
| Especificidad | `TN / (TN + FP)`; legítimas correctamente descartadas. |
| Precisión | `TP / (TP + FP)`; proporción de alertas que son fraude. |
| F1-score | Media armónica de precisión y sensibilidad. |
| Exactitud | `(TP + TN) / (TP + TN + FP + FN)`. |
| Tasa de falsos negativos | `FN / (TP + FN) = 1 - sensibilidad`. |

- [ ] Reportar las seis métricas para **cada modelo y condición**, con media y desviación estándar según solicita el apartado 4.6 del PDF, y mostrar los conteos de la matriz de confusión que sustentan el análisis.
- [ ] Si se usa una única partición de prueba, explicar el protocolo que produce media y desviación estándar en test. Por ejemplo, repetir el ajuste final con varias semillas predefinidas, manteniendo fijo el mismo test, sin seleccionar por ese resultado. Reportar también cada valor del test o dejar claro el número de repeticiones. Una sola evaluación no tiene desviación estándar estimable.
- [ ] Distinguir las desviaciones entre pliegues de validación de las desviaciones de cualquier repetición en prueba. No usar los cinco pliegues como si fueran cinco conjuntos de prueba independientes.

### 7. Análisis que debe responder la presentación

- [ ] Explicar por qué la exactitud engaña con esta prevalencia. Un clasificador que siempre predice legítimo tendría aproximadamente 99,828 % de exactitud en el conjunto completo y 0 % de sensibilidad al fraude.
- [ ] Comparar cuántos fraudes se detectan con y sin compensación y cuántas falsas alarmas se generan en cada caso.
- [ ] Comparar el árbol individual con el Random Forest propio y explicar qué aporta combinar árboles.
- [ ] Identificar la configuración elegida por validación y su desempeño final en prueba.
- [ ] Explicar limitaciones y la consecuencia de clasificar todo como fraude: sensibilidad perfecta pero todas las transacciones legítimas se convierten en falsas alarmas.
- [ ] Mantener la minimización de falsos negativos como prioridad. El análisis de falsos positivos sirve para explicar el costo operativo de las alertas.

## Entrega y presentación

| Entregable | Criterio de aceptación |
| --- | --- |
| Código | Notebook o archivos Python que reproduzcan exploración, entrenamiento, búsqueda, evaluación y Random Forest propio. |
| README | Dependencias y versiones principales, ubicación esperada del dataset, orden de ejecución y semillas. El dataset no necesita adjuntarse. |
| Presentación | PowerPoint o equivalente con metodología, resultados, análisis y conclusiones. Si se usa una herramienta en línea, adjuntar además PDF exportado. |
| Defensa | Exposición de 10 a 12 minutos por dupla, seguida de preguntas. Ambos participan y conocen todo el desarrollo. Se puede pedir ejecutar o revisar código. |

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
