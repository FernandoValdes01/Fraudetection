"""Verificaciones del algoritmo propio, independientes de su rendimiento estadístico."""

import numpy as np
import pytest
from sklearn.base import clone, is_classifier
from sklearn.datasets import make_classification
from sklearn.exceptions import NotFittedError
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import check_random_state

from fraudetection.forest import OwnRandomForestClassifier


@pytest.fixture
def data():
    return make_classification(n_samples=150, n_features=8, random_state=8)


def test_bootstrap_and_independent_trees_match_reference(data):
    X, y = data
    forest = OwnRandomForestClassifier(n_estimators=5, max_depth=3, random_state=42).fit(X, y)
    assert len(set(forest.tree_seeds_)) == 5
    assert forest.bootstrap_size_ == len(y)
    assert len({id(t) for t in forest.estimators_}) == 5
    votes = []
    for seed, actual_tree, unique_count in zip(
        forest.tree_seeds_,
        forest.estimators_,
        forest.bootstrap_unique_counts_,
        strict=True,
    ):
        indices = check_random_state(seed).randint(0, len(y), size=len(y))
        assert len(np.unique(indices)) == unique_count < len(y)
        expected_tree = DecisionTreeClassifier(max_depth=3, max_features="sqrt", random_state=seed)
        expected_tree.fit(X[indices], y[indices])
        np.testing.assert_array_equal(actual_tree.predict(X), expected_tree.predict(X))
        votes.append(expected_tree.predict(X))
    expected = (np.sum(votes, axis=0) > 2).astype(int)
    np.testing.assert_array_equal(forest.predict(X), expected)
    np.testing.assert_allclose(forest.predict_proba(X).sum(axis=1), 1)


def test_clone_reproducibility_refit_and_arbitrary_binary_labels(data):
    X, y = data
    y = np.where(y, "fraude", "legitima")
    forest = OwnRandomForestClassifier(n_estimators=7, random_state=8)
    assert is_classifier(forest)
    first = forest.fit(X, y).predict(X)
    np.testing.assert_array_equal(first, clone(forest).fit(X, y).predict(X))
    forest.fit(X, y)
    assert len(forest.estimators_) == 7
    np.testing.assert_array_equal(first, forest.predict(X))


@pytest.mark.parametrize("count", [0, 2, -3, 2.5, True])
def test_reject_invalid_tree_count(data, count):
    with pytest.raises(ValueError, match="impar"):
        OwnRandomForestClassifier(n_estimators=count).fit(*data)


def test_binary_bootstrap_can_omit_minority():
    X = np.arange(120).reshape(30, 4)
    y = np.zeros(30, dtype=int)
    y[-1] = 1
    forest = OwnRandomForestClassifier(n_estimators=31, random_state=42).fit(X, y)
    assert any(len(t.classes_) == 1 for t in forest.estimators_)
    assert forest.predict_proba(X).shape == (30, 2)


def test_unfitted_and_all_features_rejected(data):
    with pytest.raises(NotFittedError):
        OwnRandomForestClassifier().predict(data[0])
    with pytest.raises(ValueError, match="subconjunto"):
        OwnRandomForestClassifier(max_features=None).fit(*data)
    # El entero 1 significa una característica, no la fracción 100 %.
    OwnRandomForestClassifier(n_estimators=3, max_features=1).fit(*data)
