# Preparación de la defensa

Ambos integrantes deben poder explicar el procedimiento completo y relacionar sus respuestas con el código y los resultados propios. El profesor hará cinco preguntas en total, distribuidas entre los dos, con posibles repreguntas.

La [nota sobre el Random Forest propio](random-forest.md) explica el bootstrap, la diversidad entre árboles y la votación implementada.

## Preguntas para practicar

1. ¿Por qué un clasificador que siempre predice transacciones legítimas logra aproximadamente 99,827 % de exactitud y 0 % de sensibilidad al fraude en el conjunto completo?
2. ¿Qué significan TP, FN, FP y TN para una transacción? ¿Cómo se calcula `FNR = FN / (TP + FN)`?
3. ¿Qué decisiones se toman antes de abrir el test? ¿Dónde se ajustan el escalado, la selección y el remuestreo en cada pliegue?
4. ¿Por qué se estratifica la partición 70/30 y la validación de cinco pliegues? ¿Qué cambia si se utiliza una muestra de solo 10 000 filas?
5. ¿Cómo se obtiene cada muestra bootstrap, por qué hay filas repetidas y cómo se decide la predicción final del ensamble?
6. ¿Qué hace `max_features` en cada división y por qué el ensamble dejaría de cumplir el requisito si todos los árboles usaran siempre todas las variables?
7. ¿Qué hiperparámetros se buscaron para k-NN, árbol, SVM y bosque propio? ¿Cómo se resolvieron empates en sensibilidad media?
8. ¿Qué estrategia de compensación se usó, con qué parámetros y cuántos ejemplos de cada clase quedaron en los datos de entrenamiento?
9. ¿Cuántos fraudes adicionales se detectaron al compensar el desbalance y cuántas falsas alarmas aparecieron? ¿Qué cambia entre árbol y bosque?
10. ¿Qué ocurriría si se clasificara todo como fraude? ¿Qué limitaciones tiene la solución con este conjunto de datos?

Para cada pregunta, preparar una respuesta con una referencia al archivo o función correspondiente y, cuando aplique, a una tabla o figura de la presentación. Practicar la ejecución de partes del código sin usar el test para hacer nuevos ajustes.

## Respuestas con los resultados del proyecto

1. En el dataset original, predecir todo como legítimo logra 99,827 % de exactitud y 0 % de sensibilidad. En el conjunto limpio y en la partición de prueba, la exactitud sería 99,833 %. En ambos casos no se detecta ningún fraude; ver [exploración](../informe/exploracion.md).
2. `TP` son fraudes detectados, `FN` fraudes omitidos, `FP` transacciones legítimas marcadas como fraude y `TN` legítimas reconocidas. `FNR = FN / (TP + FN)` mide la fracción de fraudes que se escapan.
3. Se limpia antes de dividir para evitar copias idénticas entre train y test. La selección ANOVA, el escalado y RandomUnderSampler viven dentro de la tubería de cada pliegue en [`experiments.py`](../../src/fraudetection/experiments.py); el test queda intacto.
4. La estratificación conserva ejemplos de fraude en cada partición. El entrenamiento tiene 331 fraudes; se usa una submuestra estratificada de 50.000 filas (83 fraudes) para que la búsqueda de k-NN sea viable y comparable con los mismos cinco pliegues.
5. Cada árbol extrae con reemplazo tantas filas como haya en su entrada de entrenamiento. Algunas filas se repiten y otras no aparecen. Después los árboles votan; un empate favorece fraude. Ver [la implementación](../../src/fraudetection/forest.py).
6. `max_features=√p` limita las variables candidatas en cada división; los árboles pueden escoger particiones distintas incluso con la misma entrada.
7. La tabla [CV](../../resultados/cv_resumen.csv) registra mejores parámetros, sensibilidad media y desviación estándar para las ocho condiciones. La selección compara primero sensibilidad y luego precisión media.
8. RandomUnderSampler usa `sampling_strategy=0.1`. Al reajustar con todo el entrenamiento conserva 331 fraudes y reduce las legítimas de 198.277 a 3.310. Validación y prueba mantienen la distribución natural.
9. En el test, el bosque pasó de 76,2 % a 80,4 % de sensibilidad al submuestrear; su precisión pasó de 94,6 % a 67,5 %. El árbol compensado detectó 83,1 % de fraudes y tuvo 33,6 % de precisión; en promedio, generó 261,6 falsas alarmas frente a 55,6 del bosque compensado. Los valores de los ocho experimentos están en [`test_resumen.csv`](../../resultados/test_resumen.csv).
10. Predecir todo como fraude daría sensibilidad 100 %, pero también marcaría las 84.976 legítimas de prueba como falsas alarmas. La solución tiene un test fijo con solo 142 fraudes, no incluye identificador de transacción y usa una búsqueda acotada; esos límites se explican en la presentación.
