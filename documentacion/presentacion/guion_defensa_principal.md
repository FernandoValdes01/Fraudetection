# Guion de defensa de la presentación principal

Guion de [`defensa_fraude.pdf`](defensa_fraude.pdf): 12 diapositivas principales y cuatro de respaldo, dentro de los 10–12 minutos que pide el enunciado. Integrantes: **Fernando Alonso Valdés Gómez** y **Juan Francisco Muñoz Veloso**. Reparto sugerido: 5–6 minutos por persona.

Las cifras de este guion son las del protocolo principal (283.726 filas limpias, 198.608 de entrenamiento, 85.118 de prueba, 142 fraudes de prueba). [guion_defensa.md](guion_defensa.md) corresponde a otra ejecución, la independiente de 100.000 filas: **no mezclar sus cifras con las de este deck**.

## Preparación antes de la defensa

- Ensayar con cronómetro: 10–12 minutos sin contar preguntas.
- Repartir las preguntas: el profesor hace cinco y las distribuye entre ambos.
- Poder abrir `src/fraudetection/forest.py` y `src/fraudetection/experiments.py` si pide revisar código.
- Tener a mano [`resultados/cv_resumen.csv`](../../resultados/cv_resumen.csv) y [`resultados/test_resumen.csv`](../../resultados/test_resumen.csv) para responder con cifras.

## Diapositivas principales

### 1. Portada

**Integrante 1.** Presentación del equipo y del objetivo. La prioridad es minimizar falsos negativos: un fraude clasificado como legítimo es el error que cuesta más. En 10–12 minutos mostraremos método, resultados y qué significa operativamente cada alarma.

### 2. El reto

**Integrante 1.** 0,173 % de las transacciones son fraude. Si el modelo se equivoca en un fraude, ese fraude pasa; por eso la métrica de decisión es la sensibilidad del fraude y no la exactitud. La exactitud se usa solo para describir el problema.

### 3. Los datos

**Integrante 1.** 284.807 transacciones, 492 fraudes, 30 predictores (`Time`, `Amount`, `V1`–`V28`). Sin valores faltantes. Se eliminaron 1.081 duplicados exactos **antes** de dividir, para que una copia de una fila no quede en entrenamiento y otra en prueba: quedan 283.726 filas y 473 fraudes. `Class` nunca entra en `X`. `V1`–`V28` ya vienen de un PCA del proveedor y no se aplica otro PCA; el trabajo con variables es selección.

### 4. Preparación y partición

**Integrante 1.** Una sola partición estratificada 70/30 con semilla 42, compartida por los ocho experimentos: 198.608 filas de entrenamiento y 85.118 de prueba reservada. La prevalencia de la prueba es la natural y el test no participa de ninguna decisión. Para acotar el costo de k-NN, la búsqueda usa una submuestra estratificada fija de 50.000 filas de entrenamiento, con los mismos cinco pliegues para todos los modelos. Lo importante: escalado, selección ANOVA y submuestreo se ajustan **solo** con el entrenamiento de cada pliegue, nunca con validación ni prueba.

### 5. Diseño experimental

**Integrante 1.** Cuatro modelos (k-NN, árbol, SVM lineal y bosque propio) por dos condiciones (sin compensación y con submuestreo 1:10) = ocho experimentos. Estándar para k-NN y SVM porque usan distancias; ANOVA F-test para quedarse con 20 de 30 variables; submuestreo solo al entrenar.

### 6. Bosque aleatorio propio

**Integrante 2.** Tres pasos: bootstrap con reemplazo del tamaño del entrenamiento disponible (por eso pueden repetirse filas), un árbol `DecisionTreeClassifier` independiente por muestra con su propia semilla derivada de la general, y votación mayoritaria con empate a favor del fraude. `max_features=√p` hace que cada división considere un subconjunto aleatorio de variables: es lo que distingue el bosque del bagging que usa todas. El código no usa `RandomForestClassifier` ni `BaggingClassifier`. La configuración elegida fue 21 árboles con profundidad 6.

### 7. Selección del modelo

**Integrante 2.** Se maximiza la sensibilidad media en los cinco pliegues y, ante empate exacto, la precisión del fraude. El espacio de búsqueda está acotado y prefijado: k-NN con 3, 5 o 7 vecinos; árbol con profundidad 5, 10 o libre y hoja mínima 1 o 5; SVM lineal con `C` de 0,1, 1 o 10; bosque con 11 o 21 árboles y profundidad 6 o 12. Ganó el bosque propio con submuestreo: 87,9 % ± 5,5 % de sensibilidad y 45,0 % de precisión en validación.

### 8. Validación cruzada

**Integrante 2.** Lectura del gráfico: sensibilidad media ± desviación entre pliegues de las ocho condiciones. La compensación sube la sensibilidad en los cuatro modelos. Recordar que la desviación entre pliegues mide variación de la estimación, no incertidumbre sobre datos nuevos.

### 9. Prueba reservada

**Integrante 2.** Gráfico de sensibilidad y FNR en prueba. Se muestra la media de los cinco reajustes (semillas 42, 101, 202, 303, 404) sobre el **mismo** test fijo: 80,4 % de sensibilidad y 19,6 % de falsos negativos para el ganador. La desviación entre semillas mide cuánto cambia el ajuste, no cinco pruebas distintas.

### 10. El costo de detectar más

**Integrante 2.** El submuestreo compra sensibilidad a costa de precisión: el bosque pasa de 76,2 % a 80,4 % de sensibilidad, pero su precisión baja de 94,6 % a 67,5 %. El árbol compensado detecta 83,1 % con 33,6 % de precisión; el bosque compensado detecta 80,4 % con 67,5 %. El bosque deja pasar más fraude pero genera muchas menos falsas alarmas: 261,6 frente a 55,6 por ajuste. Analizar las falsas alarmas no cambia la prioridad; explica el costo operativo.

### 11. Casos del modelo elegido

**Integrante 2.** Matriz del primer ajuste (semilla 42): 115 fraudes detectados, 27 omitidos, 53 falsas alarmas y 84.923 legítimas reconocidas sobre 85.118 filas. Aclarar que la matriz es de una semilla y las métricas del deck son medias de cinco.

### 12. Cierre

**Integrante 2 y ambos.** Configuración elegida: bosque propio con submuestreo 1:10, 21 árboles, profundidad 6. Desempeño final: 80,4 % de sensibilidad, 19,6 % de FNR y 67,5 % de precisión. Límites: solo 142 fraudes de prueba, partición aleatoria sin validación temporal, ANOVA marginal, grilla acotada, sin identificador de transacción para comprobar duplicados. Mejoras: más positivos, validar otro período con un test nuevo y ampliar las grillas.

## Diapositivas de respaldo

- **13 · Validación:** tabla con los mejores parámetros, sensibilidad ± desviación y precisión de las ocho condiciones.
- **14 · Métricas de prueba:** las seis métricas pedidas (sensibilidad, especificidad, precisión, F1, exactitud y FNR) con media y desviación para las ocho condiciones.
- **15 · Metodología y búsqueda:** rangos de búsqueda con su motivo, escalado, ANOVA y submuestreo.
- **16 · Árbol, bosque y falsas alarmas:** comparación por condición y consecuencias de clasificar todo como legítimo o todo como fraude.

## Preguntas probables y dónde está la respuesta

| Pregunta | Respuesta corta | Evidencia |
| --- | --- | --- |
| ¿Por qué la exactitud engaña? | Predecir siempre legítimo da 99,827 % de exactitud en el conjunto original, con 0 % de sensibilidad; en el conjunto limpio y en la partición de prueba, 99,833 %. | Diapositiva 16, `documentacion/informe/exploracion.md` |
| ¿Qué pasa si se clasifica todo como fraude? | Sensibilidad 100 % y especificidad 0 %: las 84.976 legítimas del test serían falsas alarmas. | Diapositivas 16 y 11 |
| ¿Cómo se genera el bootstrap? | `rng.integers` con reemplazo, del tamaño del entrenamiento disponible; por eso hay filas repetidas y ausentes. | `src/fraudetection/forest.py`, diapositiva 6 |
| ¿Por qué `max_features`? | Limita las variables candidatas en cada división y reduce la correlación entre árboles; el código rechaza usarlo sobre todas. | `src/fraudetection/forest.py`, diapositiva 6 |
| ¿Cómo se eligen los hiperparámetros? | Grid Search sobre los mismos cinco pliegues; se maximiza la sensibilidad media y desempata la precisión. | `src/fraudetection/experiments.py`, diapositivas 7 y 13 |
| ¿Dónde se ajustan escalado, selección y remuestreo? | Dentro de la tubería de cada pliegue, solo con su entrenamiento. | `src/fraudetection/experiments.py`, diapositiva 4 |
| ¿Por qué una submuestra de 50.000 filas? | Acota el costo de k-NN; el reajuste final usa las 198.608 filas completas. | Diapositivas 4 y 6 |
| ¿La desviación en prueba mide incertidumbre? | No: mide variación del ajuste sobre un test fijo; no son cinco conjuntos independientes. | Diapositivas 9 y 14 |
| ¿Qué pasa con el bosque frente al árbol? | Sin compensación el bosque mejora; con compensación intercambia sensibilidad por menos falsas alarmas. El ganador de CV se conserva igual. | Diapositiva 16 |
| ¿Por qué no usaron `RandomForestClassifier`? | El enunciado exige implementación propia; el bootstrap, las semillas y la votación están en el código del proyecto. | Diapositiva 6, `src/fraudetection/forest.py` |
