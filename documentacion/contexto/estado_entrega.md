# Estado de la entrega

Este documento resume el estado de ambos protocolos. El principal está implementado en `src/fraudetection/` y sus resultados están en `resultados/`. El protocolo auxiliar de 100.000 filas está en `src/fraudetection/reproduction/`, con resultados separados en `resultados/ejecucion/`.

Integrantes: Fernando Alonso Valdés Gómez y Juan Francisco Muñoz Veloso.

## Desarrollo verificado del protocolo auxiliar

- [x] Dataset real identificado, descargado y validado; huella en `resultados/ejecucion/protocolo.json`.
- [x] Exploración, duplicados y recuentos antes y después de limpieza.
- [x] Muestra estratificada de 100.000 filas, superior al mínimo exigido.
- [x] Partición 70/30 y cinco pliegues estratificados compartidos, semilla fija.
- [x] Exclusión de Class y transformaciones aprendidas solo dentro del train de cada pliegue.
- [x] Selección estadística de características y registro del ajuste final.
- [x] Random Forest propio con bootstrap, variables por división, semillas independientes y mayoría.
- [x] Cuatro clasificadores con y sin compensación: ocho experimentos.
- [x] Búsqueda de hiperparámetros, prioridad de sensibilidad y desempate por precisión.
- [x] Configuraciones congeladas antes de evaluar prueba.
- [x] Seis métricas con media y desviación, CV y test separados.
- [x] Matrices de confusión y predicciones de las tres repeticiones.
- [x] Análisis de exactitud, fraude, falsas alarmas, árbol frente a bosque y límites.
- [x] README ejecutable, pruebas y auditoría de los artefactos reales.
- [x] PPTX, PDF y guion con 12 diapositivas principales y cuatro de respaldo.

La fuente de requisitos sigue siendo `IA_2026_P2.pdf`; `contexto/pauta.md` conserva la pauta original. Los resultados del protocolo principal están en `resultados/`; los del protocolo auxiliar están en `resultados/ejecucion/`.

## Acciones de los integrantes

- [ ] Revisar los resultados y personalizar la exposición.
- [ ] Ambos deben conocer toda la implementación y practicar respuestas.
- [ ] Ensayar la duración real de 10–12 minutos.
- [ ] Reservar la cita de defensa del 27–28 de octubre.
- [ ] Subir el ZIP a Blackboard antes del 26 de octubre a las 23:59.

El desarrollo y los archivos están preparados. La defensa, la reserva y la subida requieren acciones de la dupla.

## Verificación final

La [revisión requisito por requisito](revision_final.md) confirma el desarrollo técnico del protocolo independiente. La suite del repositorio pasa 41 pruebas. El número 24 corresponde a los reajustes finales de sus ocho experimentos con tres semillas cada uno, no a pruebas automatizadas. Una nueva ejecución reprodujo exactamente las particiones, parámetros, métricas y predicciones. La entrega conserva ese protocolo auxiliar separado del principal, que usa cinco semillas.
