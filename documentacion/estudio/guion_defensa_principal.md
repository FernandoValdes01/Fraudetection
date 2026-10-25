# Guion de la defensa principal

Este guion conserva la numeración de la versión de 16 diapositivas. La edición actual de Canva tiene 22: las nuevas páginas 6–10 desarrollan los modelos y ANOVA, y la 15 explica las métricas. Consultar el [estado de las presentaciones](../presentacion/README.md) antes de usar el reparto y los tiempos de esta versión.

La presentación usa exclusivamente el protocolo principal: 283.726 filas limpias, 198.608 de entrenamiento y 85.118 de prueba, con 142 fraudes. Los archivos [fraudetection.pdf](../contexto/presentaciones_anteriores/fraudetection.pdf) y [guion_defensa.md](guion_defensa.md) corresponden al protocolo auxiliar de 100.000 filas; sus cifras no se mezclan.

La nueva presentación tiene 12 diapositivas principales y cuatro respaldos. El siguiente reparto propone 11 minutos y debe comprobarse mediante ensayo con cronómetro. Ambos integrantes deben conocer todo el código.

| Página | Expone | Tiempo sugerido | Qué explicar |
| --- | --- | --- | --- |
| 1 · Portada | Fernando | 20 s | Integrantes, clasificación supervisada y prioridad de minimizar falsos negativos. |
| 2 · Problema | Fernando | 45 s | Siempre legítimo alcanza 99,827 % de exactitud original, pero detecta cero fraudes. |
| 3 · Datos | Fernando | 55 s | Fuente, 30 predictores, Class fuera de X, duplicados eliminados antes de dividir y ausencia de un nuevo PCA. |
| 4 · Partición | Fernando | 70 s | Estratificación 70/30 con semilla 42; CV de cinco pliegues compartidos sobre 50.000 filas de train. Test reservado; reajuste con todo el entrenamiento. |
| 5 · Método | Fernando | 65 s | Ocho condiciones; escalado, ANOVA y submuestreo aprendidos solo en train del pliegue. Justificar sus beneficios y límites. |
| 6 · Random Forest propio | Fernando | 80 s | Bootstrap con reemplazo del tamaño disponible, semillas distintas, variables por división y voto; explicar bagging y parámetros configurables. |
| 7 · Selección | Juan Francisco | 60 s | Grilla prefijada; maximizar sensibilidad CV y desempatar por precisión. Ganador: Random Forest compensado de 21 árboles, profundidad 6. |
| 8 · Validación | Juan Francisco | 50 s | Comparar las ocho sensibilidades CV. El ganador obtiene 87,9 % ± 5,5 pp. |
| 9 · Prueba | Juan Francisco | 55 s | Cinco reajustes sobre el mismo test con semillas 42, 101, 202, 303 y 404. La desviación mide variación del ajuste. |
| 10 · Alertas | Juan Francisco | 60 s | El Random Forest compensado detecta menos fraude que el árbol compensado, pero genera menos falsas alarmas. Mantener el ganador de CV. |
| 11 · Matriz | Juan Francisco | 50 s | Semilla 42: TN 84.923, FP 53, FN 27, TP 115. Esta matriz es un ajuste; los resúmenes promedian cinco. |
| 12 · Conclusión | Juan Francisco | 50 s | Sensibilidad 80,4 %, FNR 19,6 %, precisión 67,5 %. Límites y mejoras que requieren un test nuevo. |

Las páginas 13–16 son respaldos para preguntas: parámetros y CV; seis métricas sin compensación; seis métricas con compensación; clasificadores triviales y decisiones. No consumir el tiempo principal leyendo todas las celdas.

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
