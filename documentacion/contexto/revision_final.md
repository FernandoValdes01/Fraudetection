# Revisión final contra el enunciado

Este documento corresponde exclusivamente al protocolo independiente de 100.000 filas de `src/fraudetection/reproduction/`, con resultados en `resultados/ejecucion/`. El protocolo principal y sus presentaciones se documentan en el README de la raíz.

Revisión del 22 de octubre de 2026. Fuente de requisitos: [IA_2026_P2.pdf](../../IA_2026_P2.pdf). Integrantes: Fernando Alonso Valdés Gómez y Juan Francisco Muñoz Veloso.

El cumplimiento descrito aquí corresponde al protocolo auxiliar. Sus tres reajustes están prefijados; la consigna exige media y desviación estándar, sin fijar un número de semillas.

El desarrollo técnico y los documentos de entrega están completos. La exposición oral, la reserva de cita y la subida a Blackboard son acciones pendientes de la dupla.

## Cumplimiento técnico

| Apartado del PDF | Comprobación | Evidencia |
| --- | --- | --- |
| 3, datos | Dataset original de 284.807 filas y 492 fraudes; muestra real de 100.000, superior al mínimo de 10.000. | Descarga verificada, `exploracion.json` y SHA256 en `protocolo.json`. |
| 4.1.1, exploración y limpieza | 30 predictores, sin faltantes ni infinitos; se eliminan 1.081 duplicados exactos antes de dividir. Quedan 283.726 filas y 473 fraudes. | `data.py`, `exploracion.json`, `descriptivos.csv`. |
| 4.1.2, distribución | Recuentos y proporciones de original, conjunto limpio, muestra, train y test. Muestra con 167 fraudes; train 117, test 50. | `proporciones_clases.csv` y diapositiva 2. |
| 4.1.3, objetivo | X contiene Time, Amount y V1–V28; Class se excluye. Fraude es siempre positivo. | `config.py`, `data.py`, `metrics.py`. |
| 4.1.4, partición | Una partición estratificada 70/30, semilla 42, común a los ocho experimentos. Test conserva la prevalencia del conjunto limpio muestreado. | `particiones.npz`, auditoría y reproducción exacta. |
| 4.1.5, escalado | StandardScaler para k-NN y SVM, ajustado solo en train de cada pliegue. Árboles sin escalado. | `make_pipeline`, pruebas de las ocho tuberías y diapositiva 4. |
| 4.2, selección | ANOVA F, 20 variables, sin un nuevo PCA. Selección dentro de cada pliegue; se registran variables del reajuste final. | `experiments.py`, `caracteristicas.json` y diapositivas 4, 15 y 16. |
| 4.3.1, bootstrap | n índices con reemplazo para cada árbol, desde el train disponible en cada condición. | `forest.py`, pruebas de bootstrap y `bosque_diagnostico.json`. |
| 4.3.2 y 4.3.6, independencia | Árboles diferentes, con semillas distintas derivadas de la general. | Prueba de árboles independientes y semillas exportadas. |
| 4.3.3, características por división | DecisionTreeClassifier usa max_features=sqrt en cada división. | `forest.py` y prueba contra árboles base independientes. |
| 4.3.4, voto | Mayoría de etiquetas de 31 árboles impares, sin promediar sus probabilidades. | `predict`, prueba de votación y diapositiva 5. |
| 4.3.5 y 4.3.7, interfaz | Árboles, profundidad, max_features y semilla configurables; métodos fit y predict separados. | `OwnRandomForestClassifier`, integración con clone, Pipeline y GridSearchCV. |
| 4.3, restricciones | No se usa RandomForestClassifier ni BaggingClassifier para construir el ensamble. | Importaciones y código revisados. |
| 4.4, compensación | Cuatro modelos con y sin RandomUnderSampler, razón fraude/legítima 0,1; solo se remuestrea train. | Ocho resultados, `remuestreo_pliegues.csv` y `caracteristicas.json`. |
| 4.5.1–3, comparación y CV | Ocho condiciones, cinco pliegues estratificados compartidos dentro del 70 % de entrenamiento. | `validacion_pliegues.csv`, índices guardados y auditoría. |
| 4.5.4–5, búsqueda | Dos candidatos por modelo; vecindad, profundidad o regularización. 80 ajustes de CV; grilla acotada y justificada. | Ocho CSV de `busquedas/`, README y diapositiva 6. |
| 4.5.6, selección | Mayor sensibilidad media; empate por precisión; empate completo por orden estable. | `best_candidate`, pruebas manuales, auditoría contra cada búsqueda y `seleccion.json`. |
| 4.5.7, registros | Hiperparámetros elegidos y sensibilidad media con desviación entre pliegues. | `validacion.csv` y diapositiva 7. |
| 4.5, aislamiento de test | Las ocho búsquedas terminan y se guarda la selección antes de la primera evaluación de test. No se cambian grillas ni umbrales por test. | Orden de fases en `run_experiments` y protocolo de reproducción. |
| 4.6, ajuste y evaluación | Tres reajustes prefijados con semillas 42, 43 y 44 sobre el train completo de cada condición, mismo test. | 24 registros en `prueba_repeticiones.csv`. |
| 4.6, métricas | Sensibilidad, especificidad, precisión, F1, exactitud y FNR, con media y desviación. Fraude positivo. | `prueba_resumen.csv`, auditoría independiente de predicciones y diapositivas 8–9. |
| 4.6, separación CV/test | CV usa desviación entre cinco pliegues, ddof=0. Test usa desviación entre tres ajustes, ddof=1. No se presenta como incertidumbre poblacional. | README, HTML, guion y diapositivas 3, 8–9 y 12. |
| 4.7.1, exactitud | Se muestran los clasificadores triviales siempre legítimo y siempre fraude. | `referencias_triviales.json` y diapositiva 11. |
| 4.7.2, efectos del desbalance | Se comparan fraudes detectados y falsas alarmas con y sin compensación. | `costos.png`, análisis y diapositiva 10. |
| 4.7.3, árbol y bosque | Se cuantifican diferencias por condición y se explica bagging y aleatoriedad de variables. | `analisis.md` y diapositivas 5 y 11. |
| 4.7.4, ganador | Árbol compensado elegido por CV; se conserva aunque otras condiciones tengan más sensibilidad en test. | `seleccion.json` y diapositiva 12. |
| 4.7.5, límites | Pocos fraudes, pérdida de datos, ANOVA marginal, grilla pequeña y falta de validación temporal. Se muestran mejoras futuras. | Análisis y diapositiva 12. |
| 5, código e instrucciones | Python ejecutable, dependencias fijadas, dataset, orden de ejecución y semillas documentados. | README, `uv.lock`, comandos download/run/report/audit/predict. |
| 5–6, presentación | PPTX editable y PDF, nombres de ambos integrantes, 12 diapositivas principales y cuatro de respaldo. | Archivos de presentación revisados visualmente. |

## Comprobaciones ejecutadas

- `ruff check` y `ruff format --check` sin errores.
- 41 pruebas pasaron en el repositorio; tres de ellas demuestran rechazo de artefactos inconsistentes: semillas duplicadas, condición ausente reemplazada por duplicado y parámetros distintos de la búsqueda.
- Auditoría de las métricas de las 24 repeticiones a partir de las predicciones guardadas, con cálculos independientes de scikit-learn.
- Nueva ejecución completa con el mismo protocolo: coincidencia exacta de particiones, candidatos y selección, métricas de los ocho experimentos, características, diagnóstico del bosque y todas las predicciones. Solo difieren los tiempos de ejecución y las marcas temporales. Evidencia en `resultados/ejecucion/verificacion_reproduccion.json`.
- Descarga desde cero usando la función del proyecto: esquema, 284.807 filas, 492 fraudes y SHA256 idéntico al archivo utilizado.
- Revisión del PPTX y PDF, de sus tablas de resultados y de las diapositivas modificadas para comprobar legibilidad.
- ZIP actualizado con código, resultados y documentos; sin CSV original, entorno virtual ni modelos locales. El manifiesto permite comprobar todos los archivos.

## Correcciones de esta revisión

Las búsquedas y resultados originales eran correctos. Se hicieron visibles en las diapositivas las proporciones de clases, el espacio completo de búsqueda, la función del bagging y las mejoras futuras. La auditoría antes comprobaba cantidades y métricas, pero podía aceptar semillas duplicadas de modelos deterministas o una selección JSON inconsistente. Ahora valida identidades, semillas, pliegues, parámetros y resúmenes contra las búsquedas guardadas.

No se cambiaron modelos, variables seleccionadas, estrategias, parámetros, semillas ni reglas de decisión por observar el test. La repetición tuvo como fin verificar reproducibilidad.

## Pendientes de los integrantes

- Comprender todo el código, revisar el guion y ensayar una exposición de 10–12 minutos con participación de ambos.
- Reservar la defensa entre el 27 y el 28 de octubre.
- Subir la entrega a Blackboard antes del 26 de octubre a las 23:59.

La revisión técnica no puede acreditar una defensa que todavía no ocurre ni una entrega que aún no se ha enviado.
