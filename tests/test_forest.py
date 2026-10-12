import numpy as np
import pytest
from sklearn.base import clone
from sklearn.datasets import make_classification
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from fraudetection.forest import BootstrapRandomForest


@pytest.fixture
def sample_data():
    return make_classification(
        n_samples=180,
        n_features=8,
        n_informative=4,
        n_redundant=0,
        weights=[0.8, 0.2],
        random_state=7,
    )


def test_forest_uses_distinct_bootstraps_and_repeats_with_same_seed(sample_data):
    X, y = sample_data
    forest = BootstrapRandomForest(n_estimators=9, max_depth=4, random_state=42).fit(X, y)
    repeat = clone(forest).fit(X, y)

    assert len(forest.estimators_) == 9
    assert len(set(forest.tree_seeds_)) == 9
    assert all(count < len(X) for count in forest.bootstrap_unique_counts_)
    assert all(tree.max_features_ < X.shape[1] for tree in forest.estimators_)
    assert forest.tree_seeds_ == repeat.tree_seeds_
    np.testing.assert_array_equal(forest.predict(X), repeat.predict(X))


def test_forest_works_in_stratified_hyperparameter_search(sample_data):
    X, y = sample_data
    search = GridSearchCV(
        BootstrapRandomForest(random_state=42),
        {"n_estimators": [3, 5], "max_depth": [2, 4]},
        scoring="recall",
        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
    ).fit(X, y)

    assert isinstance(search.best_estimator_, BootstrapRandomForest)
    assert search.best_estimator_.predict(X).shape == (len(X),)


def test_even_vote_ties_favor_fraud(sample_data):
    X, y = sample_data
    forest = BootstrapRandomForest(n_estimators=2).fit(X, y)

    class FixedTree:
        def __init__(self, prediction):
            self.prediction = prediction

        def predict(self, rows):
            return np.full(len(rows), self.prediction)

    forest.estimators_ = [FixedTree(0), FixedTree(1)]
    np.testing.assert_array_equal(forest.predict(X[:3]), [1, 1, 1])


def test_forest_rejects_using_all_features_at_each_split(sample_data):
    X, y = sample_data
    with pytest.raises(ValueError, match="menos variables"):
        BootstrapRandomForest(max_features=X.shape[1], n_estimators=1).fit(X, y)
