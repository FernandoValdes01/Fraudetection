# Cómo funciona el Random Forest propio

La implementación está en [`forest.py`](../../src/fraudetection/forest.py). Usa `DecisionTreeClassifier` como árbol base, tal como permite el enunciado. El muestreo, la creación de árboles y la votación pertenecen al código del proyecto.

## Bootstrap

Si el entrenamiento disponible tiene `n` filas, cada árbol recibe `n` extracciones aleatorias **con reemplazo**. Una fila puede salir varias veces y otra puede no salir. La probabilidad de que una fila concreta no aparezca es `(1 - 1/n)^n`, que se aproxima a `e^-1`. Por eso suele haber cerca de un 63,2 % de filas distintas en cada muestra.

El entrenamiento de cada condición experimental llega al bosque mediante `fit(X, y)`. En la condición compensada, la tubería aplica primero RandomUnderSampler y el bosque obtiene su bootstrap de esa salida de entrenamiento, nunca de validación ni de prueba.

## Diversidad de árboles

Cada árbol recibe una muestra bootstrap propia y una semilla distinta derivada de la semilla general. `max_features` limita las variables candidatas en **cada división** del árbol. El código rechaza valores que hagan usar todas las variables, porque eso convertiría el mecanismo en bagging sin la selección aleatoria exigida.

## Votación

Cada árbol predice `0` o `1`. La clase final es la mayoría de votos. Si hay un número par de árboles y se empata, la regla documentada elige `1`, fraude. Esto favorece la prioridad de sensibilidad, aunque puede aumentar las falsas alarmas; ese costo deberá medirse en la evaluación final.

## Parámetros y comprobación

Se pueden ajustar `n_estimators`, `max_depth`, `max_features` y `random_state`. El estimador implementa `fit` y `predict` y es compatible con `GridSearchCV`. Las pruebas comprueban semillas distintas, bootstrap con repeticiones, límite de variables, reproducibilidad y la regla de empate. La búsqueda seleccionó 21 árboles de profundidad máxima 6; con submuestreo, el modelo detectó en promedio 80,4 % de los fraudes en la prueba y obtuvo 67,5 % de precisión. La matriz de confusión del primer ajuste (semilla 42) contiene 115 TP, 27 FN, 53 FP y 84.923 TN.
