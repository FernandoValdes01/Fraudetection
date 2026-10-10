# Guion de la presentación

El enunciado sugiere entre 10 y 12 diapositivas principales. La defensa dura 10 a 12 minutos por dupla y participan ambas personas. La presentación principal es [`defensa_fraude.pdf`](defensa_fraude.pdf), creada desde [`defensa_fraude.tex`](defensa_fraude.tex) con Beamer. Tiene 12 diapositivas principales y dos de respaldo: parámetros y resultados de CV para las ocho condiciones, y las seis métricas completas de prueba. Usa una paleta de blanco, azul y gris. [`defensa_fraude.pptx`](defensa_fraude.pptx) se conserva como formato alternativo.

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

Entregar la presentación Beamer en PDF junto con su fuente `.tex`. Reservar tiempo para preguntas y para mostrar o ejecutar el código durante la defensa.

Para regenerar los gráficos y el PowerPoint alternativo después de ejecutar los experimentos, usar `uv run --locked fraudetection-report`. Para recompilar el PDF desde la raíz del repositorio, ejecutar:

```bash
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$(pwd)":/work -w /work/documentacion/presentacion \
  blang/latex:ubuntu \
  latexmk -pdf -interaction=nonstopmode -halt-on-error defensa_fraude.tex
```

La portada ya incluye los nombres de ambos integrantes. Antes de la entrega, practicar la exposición de ambos.
