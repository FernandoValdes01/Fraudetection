# Guion de defensa

12 diapositivas principales y cuatro de respaldo. Fernando Alonso Valdés Gómez y Juan Francisco Muñoz Veloso. Distribuir 5–6 minutos por persona.

## 1. Detectar fraude: minimizar lo que se pierde

Integrante 1: presentar el objetivo. La sensibilidad de fraude es el criterio prioritario; las falsas alarmas ayudan a entender el costo. Duración prevista de las principales: 10–12 minutos.

## 2. Pocos fraudes, muchas transacciones

Integrante 1: fuente Kaggle, descarga pública TensorFlow. Eliminamos 1081 duplicados exactos para impedir copias entre train y test. No hay faltantes. Los V1–V28 ya vienen de PCA; no aplicamos otro PCA. La muestra estratificada reduce el costo de los modelos.

## 3. El test se abre después de decidir

Integrante 1: explicar que validación y test no se balancean. Cada pliegue ajusta sus transformaciones solo en su entrenamiento. Las ocho búsquedas terminan y seleccion.json se guarda antes de evaluar prueba. Ninguna decisión usa test.

## 4. Seleccionar variables y compensar dentro del pliegue

Integrante 1: ANOVA detecta diferencias marginales de medias, pero no todas las interacciones. k=20 se fijó antes de evaluar. Escalamos k-NN y SVM porque usan distancias; árboles no lo necesitan. Ratio 0.1 retiene diez legítimas por fraude y todos los fraudes del entrenamiento del pliegue. Los recuentos están guardados.

## 5. Un bosque construido por la dupla

Integrante 2: recorrer forest.py. Cada árbol recibe n índices con reemplazo, por eso hay repeticiones. Usamos semillas distintas y max_features=sqrt en cada división. El bootstrap parte del train disponible, ya compensado si corresponde. No usamos RandomForestClassifier ni BaggingClassifier. Los votos son etiquetas.

## 6. Espacios de búsqueda fijados antes de evaluar

Integrante 2: comparar vecindades, profundidad y regularización. Se fijan 31 árboles y selección de 20 variables para acotar el costo. La grilla es pequeña, por lo que no se afirma haber encontrado el óptimo global. Ningún valor se eligió mirando test.

## 7. Búsqueda acotada, selección por sensibilidad

Integrante 2: k-NN compara k=3/7; árbol profundidad 6/libre; SVM RBF C=1/10; bosque profundidad 8/libre. Árbol y bosque fijan dos ejemplos por hoja. Estos espacios exploran suavidad, complejidad y regularización a costo acotado. La tabla usa sensibilidad media y desviación entre pliegues. Empate por precisión.

## 8. Prueba: detectar fraude y controlar las alertas

Integrante 2: valores calculados con fraude como positivo. Sensibilidad=TP/(TP+FN), especificidad=TN/(TN+FP), precisión=TP/(TP+FP), F1=2TP/(2TP+FP+FN), exactitud=(TP+TN)/N y FNR=1-sensibilidad. Desviación cero puede indicar un procedimiento determinista; no certeza poblacional.

## 9. Prueba: F1, exactitud y falsos negativos

Integrante 2: valores calculados con fraude como positivo. Sensibilidad=TP/(TP+FN), especificidad=TN/(TN+FP), precisión=TP/(TP+FP), F1=2TP/(2TP+FP+FN), exactitud=(TP+TN)/N y FNR=1-sensibilidad. Desviación cero puede indicar un procedimiento determinista; no certeza poblacional.

## 10. El costo de detectar más

Integrante 2: comparar fraudes detectados con falsas alarmas. k-NN: compensar cambia los fraudes detectados en +9.33 y las falsas alarmas en +125.33, medias de los tres ajustes. Árbol: compensar cambia los fraudes detectados en +4.67 y las falsas alarmas en +493.33, medias de los tres ajustes. SVM: compensar cambia los fraudes detectados en +8.00 y las falsas alarmas en +124.33, medias de los tres ajustes. Bosque propio: compensar cambia los fraudes detectados en +8.00 y las falsas alarmas en +25.00, medias de los tres ajustes.

## 11. Árbol frente a bosque; exactitud frente a sensibilidad

Integrante 2: Sin compensación: bosque frente a árbol cambia la sensibilidad en -1.33 puntos porcentuales y las falsas alarmas en -4.67. Con compensación: bosque frente a árbol cambia la sensibilidad en +5.33 puntos porcentuales y las falsas alarmas en -473.00. El bagging busca reducir la variación y max_features reduce la correlación. La exactitud oculta el desbalance; nunca decide la selección.

## 12. Configuración elegida y límites de la evidencia

Ambos integrantes: Elegido por validación: Árbol · con compensación. Sensibilidad CV 87.14 ± 2.87 %; sensibilidad test 75.33 ± 4.62 %; precisión test 7.02 ± 0.55 %. El test contiene 50 fraudes. Pocos positivos hacen sensibles las métricas a cada error individual. La desviación en test mide variación del ajuste sobre un test fijo; no estima incertidumbre sobre otras muestras ni es un intervalo de confianza. La muestra reduce el costo computacional, pero descarta fraudes y limita la comparación. El submuestreo también elimina legítimas potencialmente informativas. La partición aleatoria exigida no valida cambios temporales ni otros bancos. ANOVA es un criterio marginal y puede descartar interacciones útiles. El bosque reduce correlación al combinar bootstrap y variables aleatorias; sus beneficios deben juzgarse por los resultados, sin suponer una mejora automática. Mejoras futuras: más datos y fraudes, validación temporal y grillas más amplias; esas mejoras requieren un nuevo protocolo y un test aún no utilizado.

## 13. Respaldo: matrices de confusión

Usar si se solicita explicar TP, FN, FP o TN. Las otras semillas y conteos individuales están en prueba_repeticiones.csv y predicciones.csv.gz.

## 14. Respaldo: matrices de confusión

Usar si se solicita explicar TP, FN, FP o TN. Las otras semillas y conteos individuales están en prueba_repeticiones.csv y predicciones.csv.gz.

## 15. Respaldo: características y recuentos finales

ANOVA se ajusta antes de remuestrear. Con el mismo train y k=20, la selección puede ser idéntica para todos los modelos. Las tres semillas están registradas.

## 16. Respaldo: características y recuentos finales

ANOVA se ajusta antes de remuestrear. Con el mismo train y k=20, la selección puede ser idéntica para todos los modelos. Las tres semillas están registradas.
