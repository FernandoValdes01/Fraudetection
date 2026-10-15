# Guion de la presentación

El enunciado sugiere entre 10 y 12 diapositivas principales. La defensa dura 10 a 12 minutos por dupla y participan ambas personas. La presentación principal es [`defensa_fraude.pdf`](defensa_fraude.pdf), creada desde [`defensa_fraude.tex`](defensa_fraude.tex) con Beamer. Tiene 12 diapositivas principales y cuatro de respaldo: validación, métricas completas de prueba, metodología y búsqueda, y análisis crítico de árbol/bosque y clasificadores triviales. Usa una paleta de blanco, azul y gris, textos breves y una guía visual discreta que recorre seis fases del proyecto. [`defensa_fraude.pptx`](defensa_fraude.pptx) se conserva como formato alternativo del mismo protocolo y resultados, con una organización diferente.

| Diapositivas | Contenido |
| --- | --- |
| 1 | Portada e integrantes. |
| 2 a 4 | Reto, datos, limpieza y partición de entrenamiento, validación y prueba. |
| 5 a 6 | Diseño de experimentos y bosque aleatorio propio. |
| 7 a 8 | Criterio de selección y validación cruzada. |
| 9 a 11 | Prueba reservada, costo de alertas y matriz de confusión. |
| 12 | Resultados, limitaciones, mejoras y conclusión. |
| 13 a 14 | Respaldo: parámetros y métricas de CV, y métricas completas de prueba. |
| 15 | Respaldo: rangos de búsqueda y justificación de escalado, ANOVA y submuestreo. |
| 16 | Respaldo: comparación árbol/bosque y consecuencias de clasificar todo como legítimo o fraude. |

Se pueden añadir diapositivas de respaldo para tablas extensas, matrices de confusión y otras métricas. Todas las métricas exigidas deben aparecer en las diapositivas principales o de respaldo. Mantener separados los resultados de validación y los de prueba. La tabla de prueba presenta media y desviación estándar de cinco reajustes con distintas semillas sobre el mismo test; las repeticiones no son muestras independientes.

Entregar la presentación Beamer en PDF junto con su fuente `.tex`. Reservar tiempo para preguntas y para mostrar o ejecutar el código durante la defensa.

Para regenerar los gráficos y el PowerPoint alternativo después de ejecutar los experimentos, usar `uv run --locked fraudetection-report`. Para recompilar el PDF desde la raíz del repositorio, ejecutar:

```bash
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$(pwd)":/work -w /work/documentacion/presentacion \
  blang/latex:ubuntu \
  latexmk -pdf -interaction=nonstopmode -halt-on-error defensa_fraude.tex
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$(pwd)":/work -w /work/documentacion/presentacion \
  blang/latex:ubuntu latexmk -c defensa_fraude.tex
```

La portada ya incluye los nombres de ambos integrantes. Antes de la entrega, practicar la exposición de ambos.

## Presentación del protocolo independiente

La ejecución independiente de 100.000 filas y tres semillas conserva [fraudetection.pptx](fraudetection.pptx), [fraudetection.pdf](fraudetection.pdf) y [guion_defensa.md](guion_defensa.md), con 12 diapositivas principales y cuatro de respaldo. Usa exclusivamente `resultados/ejecucion/`. Estos archivos corresponden a un protocolo distinto del de la presentación principal Beamer `defensa_fraude.pdf`; no mezclar sus métricas.

Para regenerarlos, ejecutar `uv run --locked fraudetection report`. El PDF se exporta con LibreOffice según la [guía de reproducción](../reproduccion.md).
