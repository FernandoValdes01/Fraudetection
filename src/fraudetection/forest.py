"""Random Forest propio: bootstrap independiente y votación de etiquetas.

Solo se delega la construcción de cada árbol a scikit-learn. Cada árbol
elige variables en cada división con max_features. No se promedian sus
probabilidades: la predicción final es la mayoría de sus votos duros.
"""

from numbers import Integral

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import check_random_state
from sklearn.utils.multiclass import check_classification_targets
from sklearn.utils.validation import check_is_fitted, validate_data


class OwnRandomForestClassifier(ClassifierMixin, BaseEstimator):
    """Bosque compatible con clone, Pipeline y GridSearchCV.

    Se exige un número impar de árboles y clasificación binaria. Esto
    evita empates sin introducir un umbral elegido a partir del test.
    Las proporciones de votos no son probabilidades calibradas.
    """

    def __init__(
        self,
        n_estimators=31,
        max_depth=None,
        max_features="sqrt",
        min_samples_leaf=1,
        random_state=None,
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.max_features = max_features
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state

    def fit(self, X, y):
        if (
            not isinstance(self.n_estimators, Integral)
            or isinstance(self.n_estimators, bool)
            or self.n_estimators < 1
            or self.n_estimators % 2 == 0
        ):
            raise ValueError("n_estimators debe ser un entero positivo impar.")
        X, y = validate_data(self, X, y, dtype=np.float64)
        check_classification_targets(y)
        self.classes_ = np.unique(y)
        if len(self.classes_) != 2:
            raise ValueError("El bosque requiere exactamente dos clases en el entrenamiento.")
        if self.max_features is None or (
            isinstance(self.max_features, float) and self.max_features == 1.0
        ):
            raise ValueError("max_features debe seleccionar un subconjunto de características.")
        if isinstance(self.max_features, Integral) and self.max_features >= X.shape[1]:
            raise ValueError("max_features debe ser menor que el número de características.")
        rng = check_random_state(self.random_state)
        self.estimators_ = []
        self.tree_seeds_ = []
        self.bootstrap_unique_counts_ = []
        self.bootstrap_size_ = len(y)
        used_seeds = set()
        for _ in range(self.n_estimators):
            seed = int(rng.randint(np.iinfo(np.int32).max))
            while seed in used_seeds:
                seed = int(rng.randint(np.iinfo(np.int32).max))
            used_seeds.add(seed)
            # Muestrear n índices con reemplazo permite repetir observaciones.
            indices = check_random_state(seed).randint(0, len(y), size=len(y))
            tree = DecisionTreeClassifier(
                max_depth=self.max_depth,
                max_features=self.max_features,
                min_samples_leaf=self.min_samples_leaf,
                random_state=seed,
            )
            tree.fit(X[indices], y[indices])
            self.estimators_.append(tree)
            self.tree_seeds_.append(seed)
            self.bootstrap_unique_counts_.append(int(np.unique(indices).size))
        return self

    def predict_proba(self, X):
        """Fracción de votos por clase, incluso si un bootstrap contiene una sola clase."""
        check_is_fitted(self, "estimators_")
        X = validate_data(self, X, reset=False, dtype=np.float64)
        positive_votes = np.zeros(len(X), dtype=np.float64)
        for tree in self.estimators_:
            positive_votes += tree.predict(X) == self.classes_[1]
        fraction = positive_votes / self.n_estimators
        return np.column_stack((1 - fraction, fraction))

    def predict(self, X):
        check_is_fitted(self, "estimators_")
        return self.classes_[self.predict_proba(X).argmax(axis=1)]
