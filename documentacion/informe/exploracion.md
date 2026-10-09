# Exploración inicial del dataset

Ejecutada con `uv run --locked fraudetection-inspect` sobre `creditcard.csv` del conjunto [Credit Card Fraud Detection de Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud). El archivo local no se sube al repositorio. SHA-256 del CSV usado:

```text
76274b691b16a6c49d3f159c883398e03ccd6d1ee12d9d8ee38f4b4b98551a89
```

## Antes de limpiar

| Medida | Resultado |
| --- | ---: |
| Registros | 284.807 |
| Variables predictoras | 30: `Time`, `Amount`, `V1` a `V28` |
| Valores faltantes | 0 |
| Filas duplicadas exactas | 1.081 |
| Legítimas (`Class = 0`) | 284.315, 99,827 % |
| Fraudes (`Class = 1`) | 492, 0,173 % |

De las 1.081 filas repetidas, 1.062 pertenecen a la clase 0 y 19 a la clase 1. No aparecen filas con los mismos 30 predictores y distinta clase.

## Decisión de limpieza

Se eliminan las filas idénticas **antes** de la partición. Así se evita que una copia exacta quede en entrenamiento y otra en prueba. No se imputan datos porque no hay faltantes. El CSV no contiene un identificador de transacción que permita comprobar si dos filas iguales representan operaciones distintas; esta incertidumbre debe mencionarse como limitación.

| Medida tras quitar duplicados | Resultado |
| --- | ---: |
| Registros | 283.726 |
| Legítimas | 283.253, 99,833 % |
| Fraudes | 473, 0,167 % |

La prevalencia cambia ligeramente, de 0,173 % a 0,167 %. No se balancea la muestra completa ni el conjunto de prueba.

## Partición fija

`split_dataset` usa semilla 42 y partición estratificada 70/30 sobre las filas limpias. La misma partición deberá usarse en los ocho experimentos.

| Partición | Filas | Fraudes |
| --- | ---: | ---: |
| Entrenamiento | 198.608 | 331 |
| Prueba reservada | 85.118 | 142 |

El comando solo inspecciona y divide. Aún no ajusta transformaciones, selecciona características ni entrena modelos con el test. La validación cruzada de cinco pliegues se hará dentro del entrenamiento.
