# Bloques de la edición Canva

Estos SVG conservan el contenido editable de los dos bloques vectoriales incorporados a Canva para mejorar su alineación:

- `busqueda.svg`: espacio de hiperparámetros de la diapositiva 7.
- `prueba.svg`: comparación de sensibilidad y FNR de la diapositiva 9, basada en `resultados/test_resumen.csv`.

En Canva se importaron copias con las letras convertidas a trazados para conservar su aspecto. Para cambiar sus cifras o su texto, editar estos SVG y reemplazar el recurso correspondiente. El resto de las seis diapositivas corregidas utiliza texto y formas del diseño de Canva.

Estos bloques pertenecen a la edición Canva. No modifican automáticamente la composición del PDF/PPTX local, que sigue siendo una versión reproducible distinta.

La ampliación didáctica conserva `cv-rf-ganador.svg` y `.png`, generados con Matplotlib a partir de `resultados/cv_resumen.csv`. La gráfica ordena las ocho condiciones por sensibilidad media y usa azul exclusivamente para la seleccionada por CV. La desviación del ganador se muestra aparte en Canva. `busqueda-rf.svg` y `prueba-rf.svg` mantienen las cifras y sustituyen el nombre abreviado por RF (Random Forest). Estos recursos corresponden al borrador, aún pendiente de guardar.
