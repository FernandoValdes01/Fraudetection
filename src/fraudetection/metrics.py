"""Métricas binarias con fraude como clase positiva."""

import numpy as np
from sklearn.metrics import confusion_matrix, make_scorer, precision_score, recall_score

METRIC_NAMES = ("sensitivity", "specificity", "precision", "f1", "accuracy", "fnr")


def specificity(y_true, y_pred):
    tn, fp, _, _ = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return float(tn / (tn + fp)) if tn + fp else 0.0


def false_negative_rate(y_true, y_pred):
    return 1.0 - recall_score(y_true, y_pred, pos_label=1, zero_division=0)


def binary_metrics(y_true, y_pred):
    tn, fp, fn, tp = (int(x) for x in confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel())
    sensitivity = tp / (tp + fn) if tp + fn else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    return {
        "sensitivity": sensitivity,
        "specificity": tn / (tn + fp) if tn + fp else 0.0,
        "precision": precision,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
        "accuracy": (tp + tn) / (tp + tn + fp + fn),
        "fnr": 1 - sensitivity,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
    }


def scoring():
    return {
        "sensitivity": make_scorer(recall_score, pos_label=1, zero_division=0),
        "specificity": make_scorer(specificity),
        "precision": make_scorer(precision_score, pos_label=1, zero_division=0),
        "f1": "f1",
        "accuracy": "accuracy",
        "fnr": make_scorer(false_negative_rate),
    }


def best_candidate(results):
    """Máxima sensibilidad; empate exacto por precisión y luego orden de la grilla."""
    recall = np.asarray(results["mean_test_sensitivity"])
    precision = np.asarray(results["mean_test_precision"])
    if not np.isfinite(recall).all() or not np.isfinite(precision).all():
        raise ValueError("Hay resultados de validación no finitos.")
    return max(range(len(recall)), key=lambda i: (recall[i], precision[i], -i))
