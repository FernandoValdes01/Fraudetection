# Presentación de Canva

La versión final es [Detección de fraude_FINAL.pdf](Detección%20de%20fraude_FINAL.pdf), descargada de Canva por el usuario el 25 de octubre de 2026. Tiene 22 páginas, 18 principales y cuatro de respaldo. Es la única presentación incluida en el repositorio y se entrega como `Presentacion.pdf` en la raíz del ZIP.

- [Diseño editable](https://canva.link/g838er8qsmu3bic).
- [Metadatos y SHA256 del PDF](canva.json).
- [Recursos gráficos](recursos/README.md).

La presentación usa los resultados principales de `resultados/`: sensibilidad de validación del bosque compensado de 87,9 % y sensibilidad en prueba de 80,4 %. Los resultados auxiliares no corresponden a esta presentación.

Para actualizar la entrega, descargar el diseño completo como PDF, reemplazar `Detección de fraude_FINAL.pdf` y ejecutar desde la raíz:

```bash
uv run --locked python scripts/package_delivery.py
```
