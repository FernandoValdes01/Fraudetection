# Preparación de la defensa

Ambos integrantes deben poder explicar el procedimiento completo y relacionar sus respuestas con el código y los resultados propios. El profesor hará cinco preguntas en total, distribuidas entre los dos, con posibles repreguntas.

La [nota sobre el Random Forest propio](random-forest.md) explica el bootstrap, la diversidad entre árboles y la votación implementada.

## Preguntas para practicar

1. ¿Por qué un clasificador que siempre predice transacciones legítimas logra aproximadamente 99,828 % de exactitud y 0 % de sensibilidad al fraude en el conjunto completo?
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
