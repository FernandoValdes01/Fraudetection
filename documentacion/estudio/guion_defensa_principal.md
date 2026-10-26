# Guion de la defensa principal

Este guion sigue las 22 páginas del PDF nativo de Canva exportado el 25 de octubre de 2026: 18 principales y cuatro respaldos. Usa exclusivamente el protocolo principal, con 283.726 filas limpias, 198.608 de entrenamiento y 85.118 de prueba, que contienen 142 fraudes. El [guion auxiliar](guion_defensa.md) corresponde a otra ejecución y sus cifras no se mezclan con esta presentación.

El recorrido propone 11 minutos, 660 segundos, y deja un minuto de margen hasta el máximo de 12. Fernando presenta las páginas 1 a 10 en 5 minutos y 35 segundos; Juan Francisco, las páginas 11 a 18 en 5 minutos y 25 segundos. Los tiempos incluyen las transiciones y deben comprobarse con cronómetro. Ambos deben conocer todo el desarrollo y poder responder preguntas de cualquier página.

| Página | Expone | Tiempo sugerido | Qué explicar |
| --- | --- | --- | --- |
| 1 · Portada | Fernando | 15 s | Integrantes, clasificación supervisada y prioridad de minimizar falsos negativos. |
| 2 · Problema | Fernando | 30 s | Siempre legítimo obtiene 99,827 % de exactitud en el original, pero sensibilidad 0 %. |
| 3 · Datos | Fernando | 35 s | 30 predictores, Class fuera de X, cero faltantes y duplicados eliminados antes de dividir para evitar copias entre train y test. No se aplica otro PCA. |
| 4 · Partición y validación | Fernando | 55 s | Separación estratificada 70/30, semilla 42. Dentro de train, muestra de 50.000: cinco rondas de 40.000 para ajustar y 10.000 para validar. El test queda fuera de la búsqueda. |
| 5 · Ocho condiciones | Fernando | 40 s | Cuatro métodos con y sin submuestreo. Escalado para k-NN/SVM y ANOVA dentro del pliegue. Ajuste final compensado con 331 fraudes y 3.310 legítimas; validación y test no se remuestrean. |
| 6 · k-NN | Fernando | 30 s | Predice con vecinos cercanos y pesos por distancia. En el ejemplo, un vecino legítimo de peso 10 supera dos fraudes de peso total 2. Se comparan k=3, 5 y 7. |
| 7 · Árbol de decisión | Fernando | 30 s | Preguntas sobre variables hasta llegar a una hoja. Profundidad y tamaño mínimo de hoja controlan complejidad. El umbral V14 ilustrado es didáctico. |
| 8 · SVM lineal | Fernando | 30 s | Frontera y margen; C controla la penalización de errores y casos dentro del margen. Se comparan 0,1, 1 y 10 con validación. |
| 9 · Idea de RF | Fernando | 35 s | Combinar árboles diversos mediante voto mayoritario. Nuestro código organiza muestras, semillas y votos; DecisionTreeClassifier construye cada árbol. El ejemplo de votos es didáctico. |
| 10 · ANOVA | Fernando | 35 s | Compara diferencias entre medias con dispersión dentro de clases. Conserva 20 de 30 variables, ajustadas solo con train. Es marginal y puede perder interacciones. Ceder la palabra a Juan Francisco. |
| 11 · Implementación propia | Juan Francisco | 50 s | Bootstrap con reemplazo y tamaño del train disponible, ya submuestreado cuando corresponde. Filas repetidas, semillas distintas, variables aleatorias por división y mayoría; empate a favor de fraude. Relacionar con fit y predict de forest.py. |
| 12 · Grid Search | Juan Francisco | 35 s | Grillas acotadas, cinco pliegues compartidos. Maximizar sensibilidad media y desempatar por precisión. Ganador: RF compensado, 21 árboles y profundidad 6. |
| 13 · Resultado de CV | Juan Francisco | 40 s | Sensibilidad CV 87,9 % ± 5,5 pp. Es la mayor media observada; la desviación entre pliegues no prueba superioridad estadística ni garantiza resultados futuros. |
| 14 · Evaluación final | Juan Francisco | 35 s | Parámetros elegidos antes de test. Cinco reajustes con semillas 42, 101, 202, 303 y 404 sobre el mismo test. Distinguir semillas finales de pliegues de CV. |
| 15 · Lectura de métricas | Juan Francisco | 45 s | Sensibilidad 80,4 % de los fraudes detectados; precisión 67,5 % de las alertas que son fraude; FNR 19,6 % de fraudes omitidos. ±0,3 pp mide variación de sensibilidad entre ajustes. |
| 16 · Falsas alarmas | Juan Francisco | 40 s | Compensar mejora detección y aumenta FP. RF compensado: 80,4 % y 55,6 FP promedio; árbol compensado: 83,1 % y 261,6 FP. Mantener el ganador de CV aunque otro modelo detecte más en test. |
| 17 · Matriz del ganador | Juan Francisco | 45 s | Semilla 42: TN 84.923, FP 53, FN 27 y TP 115. 115/142 equivale a 81,0 % de sensibilidad en ese ajuste; 80,4 % es la media de cinco. |
| 18 · Conclusión | Juan Francisco | 35 s | RF con submuestreo detecta cerca de cuatro de cada cinco fraudes. Límites: 142 fraudes en test, ANOVA marginal, grilla acotada y falta de validación temporal. Proponer más datos y otro período con un nuevo test. |

Las páginas 19 a 22 son respaldos para preguntas: parámetros y CV, seis métricas sin compensación, seis métricas con compensación, y clasificadores triviales. Las seis métricas y sus desviaciones están disponibles para los ocho experimentos. No leer todas las celdas durante la exposición principal.

La pauta sugiere 10 a 12 diapositivas principales; las 18 actuales requieren un recorrido breve. Durante el ensayo, comprobar el minuto 5:35 al cambiar de expositor y el minuto 11:00 al terminar. Si se exceden los tiempos, resumir los ejemplos didácticos de las páginas 6 a 10 y evitar repetir la explicación de RF entre las páginas 9 y 11. Conservar la explicación del protocolo, el bosque propio, los resultados y el análisis.

## Entrenamiento, validación interna y test

La separación inicial tiene solo dos conjuntos: 198.608 filas de entrenamiento y 85.118 de test reservado. No se crea un tercer conjunto fijo de validación. Dentro del entrenamiento se seleccionan 50.000 filas para la búsqueda; esas filas ya pertenecen a las 198.608. La validación cruzada estratificada divide la muestra en cinco bloques de 10.000. En cada ronda se ajusta una pipeline nueva con cuatro bloques, 40.000 filas antes del submuestreo opcional, y se evalúa con el bloque restante de 10.000. El bloque de validación rota cinco veces: una fila valida en una ronda y entrena en otras cuatro, siempre con modelos reajustados por separado. Ninguna transformación aprende del bloque de validación en su propia ronda. El test de 85.118 filas queda fuera de toda la búsqueda.

Elegidos los parámetros, cada configuración se reajusta desde cero con el entrenamiento disponible. Sin compensación, el clasificador recibe 198.608 filas; con submuestreo 1:10 recibe 331 fraudes y 3.310 legítimas, 3.641 filas. Los cinco reajustes finales con semillas 42, 101, 202, 303 y 404 son distintos de los cinco pliegues: se evalúan sobre el mismo test reservado. Estos conteos describen el protocolo principal y sus artefactos históricos; no una ejecución nueva.

## Preguntas para preparar

| Pregunta | Evidencia para responder |
| --- | --- |
| ¿Dónde se evita fuga entre pliegues? | `make_pipeline` en `src/fraudetection/experiments.py`: cada ajuste aprende transformaciones sobre su train. |
| ¿Por qué bootstrap y max_features? | `src/fraudetection/forest.py`: filas con reemplazo, árboles independientes y subconjunto de variables por división. |
| ¿Por qué se eligió un modelo que no tiene la mejor sensibilidad en test? | El ganador se fija con CV. Cambiarlo mirando prueba invalidaría esa evaluación. |
| ¿Qué significa la desviación estándar? | CV describe diferencias entre pliegues; prueba describe diferencias entre ajustes sobre los mismos casos. |
| ¿Qué pasa al predecir todo como fraude? | Sensibilidad 100 %, especificidad 0 % y 84.976 falsas alarmas en el test principal. |

Para ejecutar o mostrar código, tener preparados `forest.py`, `experiments.py`, `resultados/cv_resumen.csv` y `resultados/test_resumen.csv`. La [exploración](../contexto/exploracion.md) explica los recuentos y las decisiones de limpieza.
