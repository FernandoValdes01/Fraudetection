# Versión Canva y copias locales

**Estado actual: ampliación aprobada y guardada, 22 diapositivas.** Las páginas 6–10 explican k-NN, árbol de decisión, SVM lineal, RF y ANOVA; la página 15 enseña a leer las métricas. La comparación CV destaca RF con submuestreo y87,9 % de sensibilidad; la conclusión distingue el 80,4 %en test. Se verificaron el recuento y el orden mediante lectura del diseño guardado. Los apartados anteriores sobre 16 páginas y borradores se conservan como antecedentes. **El PDF nativo local y las copias automáticas aún no incorporan esta ampliación.**

**Revisión del 24 de octubre:** las correcciones de claridad de las páginas 4, 5, 6 y 8 están guardadas en Canva y en el PDF nativo. Se verificaron las 16 páginas y el contenido de las otras 12 permanece igual. Las copias automáticas incorporan las mismas aclaraciones con una composición diferente.

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

## Revisión aprobada del 25 de octubre de 2026

Los cambios de las páginas 3, 5 y 6 están guardados y verificados en Canva. Aclaran la limpieza, los recuentos y el orden del submuestreo, y la repetición de filas en bootstrap. **El PDF local y el ZIP aún corresponden a la versión anterior.** El conector no dispone de exportación y el navegador solicita iniciar sesión al abrir Compartir. Para sincronizar la entrega, descargar las 16 páginas como PDF estándar, reemplazar `Detección de fraude.pdf`, actualizar su SHA256 en `canva.json` y ejecutar `uv run --locked python scripts/package_delivery.py`.

## Nombres completos de los métodos

Las copias automáticas locales, Beamer y los SVG fuente usan «Árbol de decisión» y «Random Forest». El PDF nativo de Canva aún no incorpora este cambio. Se preparó un borrador remoto, pendiente de aprobación para guardar; las tablas importadas siguen pendientes porque su sustitución no se reflejó en la vista previa y la carga directa devolvió HTTP 403. No confundir este borrador con una versión publicada o exportada.

## Revisión de particiones y validación interna

Se revisó el contenido guardado del [enlace compartido](https://canva.link/0rrplm2hwj3u7u6), que resuelve al diseño `DAHYyRf5M6A`, el 25 de octubre de 2026. La página 4 dice «CV estratificada · 5 pliegues comunes», «Búsqueda: 50.000 filas · 83 fraudes» y «Reajuste final: 198.608 filas de train». La página 5 aclara que cada pliegue aprende solo del train y que validación y prueba conservan su desbalance. La página 9 distingue los cinco reajustes sobre el mismo test.

La validación interna está mencionada, pero falta explicar explícitamente cuatro bloques para entrenar y uno para validar, 40.000/10.000 antes del submuestreo, y la rotación cinco veces. No hay un tercer conjunto fijo de validación. README, ejecución, guion principal y teach desarrollan esa explicación. Esta revisión no modifica ni guarda el diseño remoto ni acredita una nueva exportación del PDF.

Texto propuesto para explicar oralmente la página 4: «Primero separamos entrenamiento y test. Dentro del entrenamiento tomamos 50.000 filas y hacemos cinco rondas: 40.000 para aprender y 10.000 para validar, rotando el bloque. Elegimos parámetros con esa validación interna, reajustamos con todo el entrenamiento y evaluamos en el test reservado».

## Borrador de mejora pedagógica

Se preparó una revisión con Impeccable y Unslop conservando la composición blanca, negra y azul y las 16 páginas. Aclara el reparto inicial entrenamiento/test, la validación interna de 40.000/10.000 por ronda, el submuestreo, la pipeline, ANOVA, GridSearchCV y la diferencia entre pliegues y semillas. Las tablas importadas de búsqueda y prueba ahora usan los nombres completos de los métodos en el borrador. Se revisaron las vistas previas y se corrigieron un título solapado y un recorte heredado en la tabla de búsqueda.

[Borrador para revisión](https://www.canva.com/d/FXjFEzVnVUj3xFH). Sigue pendiente de aprobación explícita antes de guardar, requisito de la herramienta de Canva. No se exportó el PDF ni se regeneró la entrega. `canva.json` conserva la referencia de la transacción y el alcance del borrador.

## Ampliación didáctica propuesta: 22 diapositivas

Se prepararon seis láminas adicionales con las plantillas originales: k-NN, árbol de decisión, SVM lineal, RF (Random Forest), ANOVA y lectura de métricas. El plan inserta las primeras cinco después de la página 5 actual y la de métricas después de la página 9 actual, conservando las 16 existentes. Las páginas y posiciones concretas están en `ampliacion_didactica.json`.

El nuevo borrador usa RF en los textos y tablas, ordena la comparación CV de mayor a menor y resalta en azul al ganador histórico: RF con submuestreo, 87,9 % de sensibilidad media. La lámina de lectura del test destaca 80,4 % y distingue sensibilidad, precisión, FNR y dispersión. Las figuras proceden de los CSV guardados; no se reentrenó.

[Borrador principal](https://www.canva.com/d/6g8PTnED_7hGQhi) · [Seis láminas adicionales](https://www.canva.com/d/8bqdKKIwQwJWI8R). Ambos están pendientes de aprobación para guardar e insertar las páginas. El borrador anterior ya no estaba disponible; esta revisión lo sustituye. El diseño guardado y el PDF nativo aún tienen 16 páginas y no incorporan esta ampliación.

## Aplicación confirmada de la ampliación

El usuario aprobó guardar ambos borradores e insertar las seis láminas. Las transacciones terminaron como committed. El diseño `DAHYyRf5M6A` contiene 22 páginas, con las nuevas en 6, 7, 8, 9, 10 y 15. Se corrigió la inversión de orden que produjo Canva al insertar varias páginas. El conector no dispone de exportación PDF: queda pendiente descargar la versión actual desde Canva y sincronizar el archivo de entrega.
