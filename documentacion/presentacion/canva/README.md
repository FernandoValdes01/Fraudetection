# Presentación Canva y archivos locales

La versión final tiene 22 diapositivas: 18 principales y cuatro respaldos. El PDF nativo exportado el 25 de octubre de 2026 corresponde al diseño `DAHYyRf5M6A` e incorpora la ampliación didáctica aprobada. Es el PDF incluido en la entrega.

- [Editar en Canva](https://canva.link/g838er8qsmu3bic).
- [PDF final exportado de Canva](Detección%20de%20fraude.pdf).
- [Guion principal](../../estudio/guion_defensa_principal.md), con reparto y tiempos para 11 minutos.
- [Metadatos y SHA256 del PDF](canva.json).
- [Recursos de las figuras](recursos/README.md).

## Contenido de la versión final

| Páginas | Tema |
| --- | --- |
| 1 a 3 | Integrantes, objetivo, distribución de clases y limpieza. |
| 4 y 5 | Partición, validación interna, pipeline, ocho condiciones y recuentos del submuestreo. |
| 6 a 10 | Explicaciones de k-NN, árbol de decisión, SVM lineal, RF y ANOVA. |
| 11 a 13 | Implementación propia de RF, búsqueda de parámetros y selección por CV. |
| 14 a 18 | Evaluación final, interpretación de métricas, falsas alarmas, matriz y conclusión. |
| 19 a 22 | Parámetros/CV, seis métricas sin y con compensación, clasificadores triviales y decisiones. |

La matriz de la página 17 corresponde al primer ajuste, semilla 42: TN 84.923, FP 53, FN 27 y TP 115. Su sensibilidad es 81,0 %. Las tablas y la conclusión promedian cinco ajustes sobre el mismo test, con semillas 42, 101, 202, 303 y 404: sensibilidad 80,4 % ± 0,3 pp. La desviación describe variación del ajuste.

La pauta sugiere 10 a 12 diapositivas principales y exige una exposición de 10 a 12 minutos. El guion propone un recorrido de 11 minutos por las 18 principales, con explicaciones breves de los métodos. Hay que comprobar su duración mediante ensayo con cronómetro; los respaldos se reservan para preguntas.

## Actualizar la entrega

Después de modificar el diseño, descargar sus 22 páginas mediante Compartir → Descargar → PDF estándar. Reemplazar `Detección de fraude.pdf`, actualizar su SHA256 y estado en `canva.json` y regenerar el paquete desde la raíz:

```bash
uv run --locked python scripts/package_delivery.py
```

## Respaldos automáticos

Los archivos [presentacion.pdf](presentacion.pdf) y [presentacion.pptx](presentacion.pptx) son respaldos anteriores de 16 páginas. Se generan con Python y LibreOffice, tienen otra composición y no se sincronizan con Canva. El generador no sobrescribe el PDF nativo final. Estos respaldos quedan fuera del ZIP.

Para regenerarlos desde la raíz, con Python 3.12, `uv` y LibreOffice instalados:

```bash
uv sync --locked
uv run --locked python scripts/build_minimal_presentation.py
libreoffice -env:UserInstallation=file:///tmp/fraudetection-presentacion-office \
  --headless --convert-to pdf --outdir documentacion/presentacion/canva \
  documentacion/presentacion/canva/presentacion.pptx
```

El generador usa `resultados/cv_resumen.csv`, `test_resumen.csv`, `predicciones_configuracion_cv.csv` y `metadata.json`. Los registros de las revisiones y de las páginas insertadas se conservan en `canva.json` y `ampliacion_didactica.json`; el historial de Git conserva los borradores anteriores.
