# Análisis de resultados

Elegido por validación: Árbol · con compensación. Sensibilidad CV 87.14 ± 2.87 %; sensibilidad test 75.33 ± 4.62 %; precisión test 7.02 ± 0.55 %.

k-NN: compensar cambia los fraudes detectados en +9.33 y las falsas alarmas en +125.33, medias de los tres ajustes.

Árbol: compensar cambia los fraudes detectados en +4.67 y las falsas alarmas en +493.33, medias de los tres ajustes.

SVM: compensar cambia los fraudes detectados en +8.00 y las falsas alarmas en +124.33, medias de los tres ajustes.

Bosque propio: compensar cambia los fraudes detectados en +8.00 y las falsas alarmas en +25.00, medias de los tres ajustes.

Sin compensación: bosque frente a árbol cambia la sensibilidad en -1.33 puntos porcentuales y las falsas alarmas en -4.67.

Con compensación: bosque frente a árbol cambia la sensibilidad en +5.33 puntos porcentuales y las falsas alarmas en -473.00.

El test contiene 50 fraudes. Pocos positivos hacen sensibles las métricas a cada error individual.

La desviación en test mide variación del ajuste sobre un test fijo; no estima incertidumbre sobre otras muestras ni es un intervalo de confianza.

La muestra reduce el costo computacional, pero descarta fraudes y limita la comparación. El submuestreo también elimina legítimas potencialmente informativas.

La partición aleatoria exigida no valida cambios temporales ni otros bancos. ANOVA es un criterio marginal y puede descartar interacciones útiles.

El bosque reduce correlación al combinar bootstrap y variables aleatorias; sus beneficios deben juzgarse por los resultados, sin suponer una mejora automática.