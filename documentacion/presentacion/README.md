# Guion de la presentación

El enunciado sugiere entre 10 y 12 diapositivas principales. La defensa dura 10 a 12 minutos por dupla y participan ambas personas. Los resultados y su análisis deben aparecer aquí; los comentarios del código no los reemplazan. El archivo [`defensa_fraude.pptx`](defensa_fraude.pptx) contiene 12 diapositivas principales, una tabla de respaldo con los parámetros y resultados de validación de los ocho experimentos, y otra con las seis métricas de prueba.

| Diapositivas | Contenido |
| --- | --- |
| 1 | Portada, integrantes, objetivo y prioridad de minimizar falsos negativos. |
| 2 | Tamaño del dataset, variables, clases y desbalance. |
| 3 a 4 | División 70/30, limpieza, escalado, selección, compensación, cinco pliegues y prevención de fuga. |
| 5 | Random Forest propio: bootstrap, árboles independientes, `max_features`, votación y parámetros. |
| 6 a 7 | Selección por sensibilidad, configuración ganadora y resultados de validación. |
| 8 a 10 | Resultados de prueba, comparación de métricas y matriz de confusión. |
| 11 | Efecto de compensar el desbalance, falsas alarmas y comparación árbol frente a ensamble. |
| 12 | Configuración elegida, resultados finales, límites y conclusión. |
| 13 a 14 | Respaldo: parámetros y métricas de CV, y métricas completas de prueba. |

Se pueden añadir diapositivas de respaldo para tablas extensas, matrices de confusión y otras métricas. Todas las métricas exigidas deben aparecer en las diapositivas principales o de respaldo. Mantener separados los resultados de validación y los de prueba. La tabla de prueba presenta media y desviación estándar de cinco reajustes con distintas semillas sobre el mismo test; las repeticiones no son muestras independientes.

Entregar PowerPoint o equivalente. Si la presentación se crea con una herramienta en línea, adjuntar también un PDF exportado. Reservar tiempo para preguntas y para mostrar o ejecutar el código durante la defensa.

Para regenerar tablas, gráficos y diapositivas después de ejecutar los experimentos, usar `uv run --locked fraudetection-report`. Antes de la entrega, completar los nombres de integrantes en la portada y practicar la exposición de ambos integrantes.
