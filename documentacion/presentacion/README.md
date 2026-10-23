# Presentación y defensa

La presentación utiliza exclusivamente los resultados del protocolo principal: 283.726 filas limpias, 198.608 de entrenamiento y 85.118 de prueba. Tiene 12 diapositivas principales y cuatro respaldos. El [guion](guion_defensa_principal.md) propone una exposición de 11 minutos entre ambos integrantes.

## Versión nueva

- [PDF local](presentacion.pdf), listo para abrir sin conexión.
- [PowerPoint local editable](presentacion.pptx).
- [Edición Canva](https://canva.link/g838er8qsmu3bic), con su referencia en [canva.json](canva.json).

Las últimas correcciones de Canva están pendientes de aprobación para guardarse. El PDF y el PPTX locales ya incorporan las correcciones.

Las dos versiones siguen el mismo contenido académico y una paleta editorial blanca, negra y azul. El PDF y el PPTX locales se generan desde los CSV mediante Python y LibreOffice; **no son exportaciones nativas de Canva ni copias exactas de su composición**. La extensión disponible permite crear y editar Canva, pero no exportar PDF/PPTX en esta sesión.

Para obtener una copia exacta del diseño de Canva, abrir su enlace con la cuenta conectada y usar Compartir → Descargar → PDF estándar o Microsoft PowerPoint. Si se entrega la versión en línea, incluir también el PDF exportado, como exige el enunciado. El PDF local ya permite entregar una presentación completa sin depender de la versión en línea.

## Regenerar la versión local

Desde la raíz, con Python 3.12, `uv` y LibreOffice instalados:

```bash
uv sync --locked
uv run --locked python scripts/build_minimal_presentation.py
libreoffice -env:UserInstallation=file:///tmp/fraudetection-presentacion-office \
  --headless --convert-to pdf --outdir documentacion/presentacion \
  documentacion/presentacion/presentacion.pptx
```

El [generador](../../scripts/build_minimal_presentation.py) usa `resultados/cv_resumen.csv`, `test_resumen.csv`, `predicciones_configuracion_cv.csv` y `metadata.json`. Las tablas deben regenerarse si cambian los resultados. Las ediciones hechas en Canva no se sincronizan automáticamente con estos archivos.

## Contenido

| Páginas | Tema |
| --- | --- |
| 1–3 | Problema, integrantes, datos y limpieza. |
| 4–6 | Partición, prevención de fuga, ocho condiciones y bosque propio. |
| 7–9 | Búsqueda, selección por CV y prueba reservada. |
| 10–12 | Falsas alarmas, matriz del ganador, conclusión y límites. |
| 13–16 | Parámetros/CV, seis métricas sin y con compensación, referencias triviales y decisiones. |

La matriz corresponde al primer ajuste, semilla 42. Los resúmenes de prueba son medias y desviaciones de cinco ajustes sobre el mismo test, con semillas 42, 101, 202, 303 y 404. La desviación describe variación del ajuste, no cinco conjuntos de prueba independientes.

## Versiones anteriores y protocolo auxiliar

Se conservan las fuentes anteriores para reproducibilidad:

| Archivos | Uso |
| --- | --- |
| [defensa_fraude.pdf](defensa_fraude.pdf), [fuente Beamer](defensa_fraude.tex), [PowerPoint automático](defensa_fraude.pptx) | Alternativas anteriores del protocolo principal. `fraudetection-report` regenera el PPTX automático, sin sobrescribir `presentacion.pptx`. |
| [fraudetection.pdf](fraudetection.pdf), [PPTX](fraudetection.pptx), [guion auxiliar](guion_defensa.md) | Protocolo independiente de 100.000 filas y tres semillas, con resultados exclusivos en `resultados/ejecucion/`. |

Para reconstruir el Beamer anterior, ver la fuente y usar Docker con `blang/latex:ubuntu`:

```bash
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$(pwd)":/work -w /work/documentacion/presentacion \
  blang/latex:ubuntu \
  latexmk -pdf -interaction=nonstopmode -halt-on-error defensa_fraude.tex
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$(pwd)":/work -w /work/documentacion/presentacion \
  blang/latex:ubuntu latexmk -c defensa_fraude.tex
```

El protocolo auxiliar se regenera con `uv run --locked fraudetection report`; ver [reproducción](../reproduccion.md). Sus métricas no deben mezclarse con las del principal.
