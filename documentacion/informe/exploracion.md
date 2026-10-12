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

La búsqueda de hiperparámetros tomará una submuestra estratificada y fija de **50.000 filas** desde estas 198.608 filas de entrenamiento. La submuestra contiene las dos clases y permite ejecutar cinco pliegues para comparar k-NN sin apartarse de la distribución natural. Los ocho experimentos reutilizarán exactamente los mismos pliegues.

La submuestra tiene **49.917 legítimas y 83 fraudes**. En cada pliegue se aplica submuestreo aleatorio con `sampling_strategy=0.1`: en los dos primeros pliegues se pasa de 39.933 legítimas y 67 fraudes a 670 y 67; en los otros tres, de 39.934 y 66 a 660 y 66. Al reajustar sobre todo el entrenamiento, quedan **3.310 legítimas y 331 fraudes**. La validación conserva su prevalencia natural.

Cada configuración ganadora se reajustará con las 198.608 filas completas de entrenamiento. La evaluación final utilizará las 85.118 filas de prueba sin remuestreo. El escalado, selección estadística por ANOVA (`f_classif`, mejores 20 de 30 variables) y submuestreo se ajustan dentro de cada pliegue durante la búsqueda.

## Búsqueda y evaluación ejecutadas

Se compararon cuatro clasificadores con y sin submuestreo: k-NN (`n_neighbors` 3, 5 o 7; pesos por distancia), árbol (`max_depth` 5, 10 o sin límite; `min_samples_leaf` 1 o 5), SVM lineal (`C` 0,1; 1 o 10) y Random Forest propio (`n_estimators` 11 o 21; `max_depth` 6 o 12; `max_features=√p`). El escalado estándar se usa para k-NN y SVM. La selección ANOVA y el remuestreo están dentro de una tubería de `imbalanced-learn` para evitar fuga entre pliegues.

La configuración se elige maximizando sensibilidad media en validación y usando precisión media como desempate. La elegida fue **Random Forest propio con submuestreo 1:10**, con 21 árboles y profundidad máxima 6: sensibilidad **87,9 % ± 5,5 %** y precisión **45,0 %** en validación. Los resultados exactos de las ocho configuraciones están en [`../../resultados/cv_resumen.csv`](../../resultados/cv_resumen.csv).

La prueba fija contiene 84.976 transacciones legítimas y 142 fraudes. Cada modelo se reajustó cinco veces con las semillas 42, 101, 202, 303 y 404, sin cambiar la prueba ni tomar decisiones a partir de sus resultados. La configuración elegida obtuvo sensibilidad **80,4 % ± 0,3 %**, especificidad **99,935 % ± 0,014 %**, precisión **67,5 % ± 4,6 %**, F1 **73,3 % ± 2,8 %**, exactitud **99,902 % ± 0,014 %** y FNR **19,6 % ± 0,3 %**. La matriz del primer ajuste (semilla 42) es TN=84.923, FP=53, FN=27 y TP=115. Las medias y desviaciones de las ocho condiciones están en [`../../resultados/test_resumen.csv`](../../resultados/test_resumen.csv); cada repetición está en [`../../resultados/test_repeticiones.csv`](../../resultados/test_repeticiones.csv).
