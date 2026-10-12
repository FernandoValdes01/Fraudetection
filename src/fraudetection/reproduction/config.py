"""Protocolo fijado antes de observar el conjunto de prueba."""

RANDOM_SEED = 42
TEST_SIZE = 0.30
CV_FOLDS = 5
POSITIVE_CLASS = 1
SAMPLE_SIZE = 100_000
FINAL_SEEDS = (42, 43, 44)
FEATURES = ("Time", *(f"V{i}" for i in range(1, 29)), "Amount")
SELECTED_FEATURES = 20
DATA_URL = "https://storage.googleapis.com/download.tensorflow.org/data/creditcard.csv"
AUTHORS = ("Fernando Alonso Valdés Gómez", "Juan Francisco Muñoz Veloso")
