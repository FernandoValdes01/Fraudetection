# Preparación de la defensa

Ambos integrantes deben poder explicar el procedimiento completo y relacionar sus respuestas con el código y los resultados propios. El profesor hará cinco preguntas en total, distribuidas entre los dos, con posibles repreguntas.

La [nota sobre el Random Forest propio](random-forest.md) explica el bootstrap, la diversidad entre árboles y la votación implementada.

## Guiones y respuestas

- [Guion principal](guion_defensa_principal.md): versión Canva y copias locales, protocolo principal.
- [Guion auxiliar](guion_defensa.md): protocolo independiente de 100.000 filas.
- [Respuestas del protocolo auxiliar](respuestas.md): cifras exclusivas de esa ejecución.

La guía de esta carpeta es material de preparación personal. No forma parte de la entrega comprimida. Para la exposición y las preguntas, usa como referencia principal el guion y las respuestas de abajo; las cifras del protocolo auxiliar son antecedentes y no deben mezclarse con la presentación Canva.

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

## Respuestas del protocolo principal

Estas respuestas corresponden a la presentación Canva, al protocolo de `src/fraudetection/` y a los archivos `resultados/cv_resumen.csv` y `resultados/test_resumen.csv`.

1. **¿Por qué la exactitud engaña?** El conjunto original contiene 284.807 transacciones y 492 fraudes. Predecir siempre legítimo obtiene `284807-492 = 284315` aciertos, es decir, 99,827 % de exactitud, pero sensibilidad 0 %. En el test limpio hay 84.976 legítimas y 142 fraudes: la misma regla logra 99,833 % y sigue detectando cero fraudes. Por eso la selección prioriza sensibilidad de la clase positiva, `Class=1`.
2. **¿Qué significan las celdas de la matriz?** `TP` es fraude detectado, `FN` fraude omitido, `FP` legítima marcada como fraude y `TN` legítima reconocida. Con fraude positivo: sensibilidad `TP/(TP+FN)`, especificidad `TN/(TN+FP)`, precisión `TP/(TP+FP)`, F1 `2·precisión·sensibilidad/(precisión+sensibilidad)`, exactitud `(TP+TN)/N` y `FNR=FN/(TP+FN)=1-sensibilidad`. La matriz de la diapositiva 11 es una corrida con semilla 42: TN 84.923, FP 53, FN 27 y TP 115.
3. **¿Cómo se evitó fuga de información y por qué estratificar?** Se quitaron 1.081 duplicados exactos antes de partir los datos. Se hizo una sola división estratificada 70/30 con semilla 42. La estratificación conserva la prevalencia y deja 331 fraudes en train y 142 en test. Para la búsqueda se usa una muestra estratificada fija de 50.000 filas de train, con 83 fraudes, dividida en los mismos cinco pliegues para los ocho experimentos. En cada pliegue, escalado, ANOVA y submuestreo se ajustan dentro de la tubería usando solo el train del pliegue. Validación y test mantienen su prevalencia. Tras elegir, se reajusta con las 198.608 filas completas de entrenamiento. Ver `make_pipeline`, `take_search_sample`, `run_searches` y `run_final_evaluations` en [`experiments.py`](../../src/fraudetection/experiments.py).
4. **¿Qué selecciona ANOVA y qué limitación tiene?** El test F univariado ordena las variables por evidencia de diferencias de medias entre clases y conserva las 20 mejores. Es barato y se ajusta dentro de cada pliegue. Puede pasar por alto interacciones entre variables. `V1`–`V28` ya son componentes PCA del dataset; no se aplica otro PCA. `Class` no entra a `X`.
5. **¿Qué cambia con la compensación?** Se usa `RandomUnderSampler(sampling_strategy=0.1)`: conserva todos los fraudes disponibles y reduce las legítimas hasta diez por cada fraude. Al reajustar con todo el train, mantiene 331 fraudes y baja las legítimas de 198.277 a 3.310. Solo cambia el train; no se balancean pliegues de validación ni test. El costo es descartar legítimas que podrían aportar información.
6. **¿Cómo funciona el bosque propio?** Para cada árbol se extraen con reemplazo tantas filas como hay en el entrenamiento recibido. Algunas se repiten y otras quedan fuera. Cada árbol usa una semilla distinta y `max_features='sqrt'` propone un subconjunto de variables en cada división. Se vota por etiquetas y, si hay empate, gana fraude. El bosque implementa `fit` y `predict` con `DecisionTreeClassifier`; no usa `RandomForestClassifier` ni `BaggingClassifier`. Ver [`forest.py`](../../src/fraudetection/forest.py).
7. **¿Qué grillas se probaron y cómo se eligió?** k-NN: `n_neighbors` 3, 5 y 7. Árbol: profundidad 5, 10 o ilimitada y hoja mínima 1 o 5. SVM lineal: `C` 0,1, 1 o 10. Bosque: 11 o 21 árboles y profundidad 6 o 12. Se maximiza la sensibilidad media en CV; solo ante igualdad exacta se usa la precisión media. El ganador fue bosque con submuestreo, 21 árboles y profundidad 6, con sensibilidad CV 87,9 % ± 5,5 pp y precisión CV 45,0 %.
8. **¿Qué dio la evaluación final?** En el mismo test de 85.118 transacciones y 142 fraudes, el bosque compensado tuvo sensibilidad 80,4 % ± 0,3 pp, FNR 19,6 % ± 0,3 pp, precisión 67,5 % ± 4,6 pp, especificidad 99,935 % ± 0,014 pp, F1 73,3 % ± 2,8 pp y exactitud 99,902 % ± 0,014 pp. Las medias y desviaciones resumen cinco reajustes con semillas 42, 101, 202, 303 y 404 sobre los mismos casos. No son cinco tests independientes ni intervalos de confianza. La diapositiva 11 muestra solo la primera corrida, semilla 42.
9. **¿Qué efecto tuvo compensar el desbalance?** Para el bosque, la sensibilidad promedio subió de 76,2 % a 80,4 %, equivalente a unos 6 fraudes adicionales detectados por corrida promedio (114,2 frente a 108,2 de 142). La precisión bajó de 94,6 % a 67,5 % y las falsas alarmas promedio subieron de 6,2 a 55,6. El árbol compensado detectó 83,1 % de fraudes, unos 27,8 más que el árbol sin compensación (118,0 frente a 90,2), pero produjo 261,6 falsas alarmas promedio y precisión 33,6 %. Aun cuando otro modelo resulte mejor en test para una métrica, se conserva el ganador fijado por CV: elegir mirando test sesgaría la evaluación.
10. **¿Qué aporta combinar árboles y cuáles son los límites?** Bootstrap y variables aleatorias buscan árboles diversos; el voto puede reducir variabilidad, aunque no garantiza superar a un árbol en toda métrica. El resultado se limita a 142 fraudes en test, una búsqueda acotada, variables PCA con interpretación limitada y una partición aleatoria que no mide cambios temporales. Un estudio futuro podría evaluar más datos, otro período y validación temporal, con un nuevo test reservado.
11. **¿Qué ocurriría si todo se clasificara como fraude?** Se detectarían todos los 142 fraudes (sensibilidad 100 %, FNR 0 %), pero las 84.976 transacciones legítimas serían falsas alarmas y la especificidad sería 0 %. La precisión sería `142/85118 = 0,167 %`, porque se marcarían como fraude las 85.118 transacciones de prueba. Sensibilidad sola no describe el costo operativo.

Para practicar, cada integrante debería poder ubicar la explicación en el código y reconstruir de memoria las métricas y el criterio de selección. Practiquen la ejecución de partes del código sin usar el test para hacer nuevos ajustes.
