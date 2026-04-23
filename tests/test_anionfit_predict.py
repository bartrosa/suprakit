# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import numpy as np

from suprakit.anionfit.predict import ESPLogKaModel


def test_model_recovers_training_exactly() -> None:
    model = ESPLogKaModel.from_priyadarshini_2025()
    esp = model.esp_train
    assert esp is not None
    preds = model.predict(esp)
    np.testing.assert_allclose(preds, model.logka_train, rtol=1e-12, atol=1e-12)


def test_prediction_interval_contains_training() -> None:
    model = ESPLogKaModel.from_priyadarshini_2025()
    esp = model.esp_train
    assert esp is not None
    mid, lower, upper = model.predict_with_ci(esp)
    truth = model.logka_train
    assert truth is not None
    assert np.all(lower <= mid)
    assert np.all(mid <= upper)


def test_model_generalization_monotone() -> None:
    model = ESPLogKaModel.from_priyadarshini_2025()
    esp_grid = np.linspace(0.1, 0.25, num=11)
    preds = model.predict(esp_grid)
    assert np.all(np.diff(preds) > 0)
