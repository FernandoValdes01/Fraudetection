# Versión Canva y copias locales

- [Editar en Canva](https://canva.link/g838er8qsmu3bic). La referencia del diseño está en [canva.json](canva.json).
- [PDF final exportado de Canva](Detección%20de%20fraude.pdf), listo para abrir sin conexión y usado en la entrega.
- [PDF automático de respaldo](presentacion.pdf), con composición diferente.
- [PowerPoint local editable](presentacion.pptx).
- [Recursos vectoriales de Canva](recursos/README.md).
- [Guion principal](../../estudio/guion_defensa_principal.md), con reparto y minutado para ambos integrantes.

El diseño de Canva conserva las correcciones de contenido y los ajustes visuales aprobados de las páginas 3, 5, 7, 9, 12 y 16. Los SVG conservan las fuentes de los bloques de búsqueda y prueba.

El PDF automático `presentacion.pdf` y el PPTX local siguen el mismo contenido académico y una paleta blanca, negra y azul, pero se generan con Python y LibreOffice. **No son exportaciones nativas de Canva ni copias exactas de su composición.** Las ediciones de Canva no se sincronizan con ellos.

El PDF final `Detección de fraude.pdf` sí es una exportación nativa de Canva del diseño `DAHYyRf5M6A`, con 16 páginas. Para actualizarlo, abrir el diseño y usar Compartir → Descargar → PDF estándar, reemplazar ese PDF y regenerar el ZIP. El generador automático no lo sobrescribe. Si se entrega la versión en línea, incluir también un PDF, como exige el enunciado.

## Regenerar las copias locales

Desde la raíz, con Python 3.12, `uv` y LibreOffice instalados:

```bash
uv sync --locked
uv run --locked python scripts/build_minimal_presentation.py
libreoffice -env:UserInstallation=file:///tmp/fraudetection-presentacion-office \
  --headless --convert-to pdf --outdir documentacion/presentacion/canva \
  documentacion/presentacion/canva/presentacion.pptx
```

El [generador](../../../scripts/build_minimal_presentation.py) usa `resultados/cv_resumen.csv`, `test_resumen.csv`, `predicciones_configuracion_cv.csv` y `metadata.json`. Regenerar las tablas si cambian los resultados.

## Contenido

| Páginas | Tema |
| --- | --- |
| 1–3 | Problema, integrantes, datos y limpieza. |
| 4–6 | Partición, prevención de fuga, ocho condiciones y bosque propio. |
| 7–9 | Búsqueda, selección por CV y prueba reservada. |
| 10–12 | Falsas alarmas, matriz del ganador, conclusión y límites. |
| 13–16 | Parámetros/CV, seis métricas sin y con compensación, referencias triviales y decisiones. |

La matriz corresponde al primer ajuste, semilla 42. Los resúmenes de prueba son medias y desviaciones de cinco ajustes sobre el mismo test, con semillas 42, 101, 202, 303 y 404. La desviación describe variación del ajuste, no cinco conjuntos de prueba independientes.
