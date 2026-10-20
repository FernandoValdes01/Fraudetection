# Integración de los avances del remoto

El 12 de octubre de 2026 se integraron los diez commits que ya estaban en GitHub con el desarrollo local revisado. Se conservan los dos protocolos y sus resultados, porque emplean muestras, modelos y semillas diferentes.

| Protocolo | Código y comandos | Resultados y presentación |
| --- | --- | --- |
| Principal, procedente del remoto | `src/fraudetection/`; `fraudetection-inspect`, `fraudetection-run`, `fraudetection-report`. Busca sobre 50.000 filas de train, reajusta con todo el entrenamiento y usa cinco semillas. | Tablas en la raíz de `resultados/`; presentación principal Beamer `defensa_fraude.pdf` y su fuente `.tex`. |
| Independiente, revisado en esta conversación | `src/fraudetection/reproduction/`; `fraudetection download/run/report/audit/predict`. Muestra estratificada de 100.000 filas y tres semillas finales. | `resultados/ejecucion/`; `fraudetection.pptx`, `fraudetection.pdf` y guion de defensa. |

Los módulos del protocolo independiente se movieron a un subpaquete para conservar los comandos e interfaces del remoto sin mezclar constantes, clasificadores ni resultados. No se retocaron hiperparámetros ni decisiones a partir de prueba. La migración a Beamer y los archivos de esa presentación se conservaron tal como estaban en el remoto.

La suite combinada contiene 40 pruebas. La auditoría independiente sigue comprobando sus ocho condiciones y 24 reajustes. El empaquetado incorpora el código, documentación, resultados y presentaciones de ambos protocolos, sin dataset ni modelos binarios locales.

Para preparar la defensa principal, seguir el README de la raíz y `documentacion/presentacion/README.md`. Para reproducir o auditar el segundo protocolo, seguir `documentacion/reproduccion.md`. No combinar métricas de las dos ejecuciones en una tabla como si compartieran partición o espacio de búsqueda.
