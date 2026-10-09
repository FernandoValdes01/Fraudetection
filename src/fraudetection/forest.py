"""Random Forest binario propio construido con árboles de scikit-learn."""

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.validation import check_is_fitted, validate_data

from fraudetection.config import RANDOM_SEED


class BootstrapRandomForest(ClassifierMixin, BaseEstimator):
    """Bagging de árboles con bootstrap, `max_features` por división y voto.

    Los empates se resuelven a favor del fraude (clase 1). `max_features`
    debe escoger menos columnas que el total para mantener aleatoriedad por
    división. La clase acepta las etiquetas 0 y 1 del conjunto del proyecto.
    """

    def __init__(
        self,
        *,
        n_estimators: int = 31,
        max_depth: int | None = None,
        max_features: float | str = "sqrt",
        random_state: int | None = RANDOM_SEED,
    ) -> None:
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.max_features = max_features
        self.random_state = random_state

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BootstrapRandomForest":
        if (
            isinstance(self.n_estimators, bool)
            or not isinstance(self.n_estimators, int)
            or self.n_estimators < 1
        ):
            raise ValueError("n_estimators debe ser un entero positivo")
        if self.max_features is None:
            raise ValueError(
                "max_features debe seleccionar un subconjunto de variables"
            )

        X_checked, y_checked = validate_data(self, X, y, dtype=np.float64)
        if X_checked.shape[1] < 2:
            raise ValueError("El bosque requiere al menos dos variables")
        classes = np.unique(y_checked)
        if not np.array_equal(classes, np.array([0, 1])):
            raise ValueError("Las clases de entrenamiento deben ser 0 y 1")

        rng = np.random.default_rng(self.random_state)
        estimators: list[DecisionTreeClassifier] = []
        tree_seeds: list[int] = []
        bootstrap_unique_counts: list[int] = []
        used_seeds: set[int] = set()
        n_samples = len(y_checked)

        for _ in range(self.n_estimators):
            indices = rng.integers(0, n_samples, size=n_samples)
            tree_seed = int(rng.integers(0, 2**31 - 1))
            while tree_seed in used_seeds:
                tree_seed = int(rng.integers(0, 2**31 - 1))
            used_seeds.add(tree_seed)

            tree = DecisionTreeClassifier(
                max_depth=self.max_depth,
                max_features=self.max_features,
                random_state=tree_seed,
            )
            tree.fit(X_checked[indices], y_checked[indices])
            if tree.max_features_ >= X_checked.shape[1]:
                raise ValueError(
                    "max_features debe considerar menos variables que el total en cada división"
                )

            estimators.append(tree)
            tree_seeds.append(tree_seed)
            bootstrap_unique_counts.append(int(np.unique(indices).size))

        self.classes_ = classes
        self.estimators_ = estimators
        self.tree_seeds_ = tree_seeds
        self.bootstrap_unique_counts_ = bootstrap_unique_counts
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        check_is_fitted(self, "estimators_")
        X_checked = validate_data(self, X, reset=False, dtype=np.float64)
        votes_for_fraud = np.zeros(X_checked.shape[0], dtype=np.int32)
        for tree in self.estimators_:
            votes_for_fraud += tree.predict(X_checked) == 1
        return (2 * votes_for_fraud >= len(self.estimators_)).astype(np.int8)
