# SPDX-License-Identifier: Apache-2.0
"""ESP→log(Ka) linear calibration models for anion-binding calix frameworks."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from importlib import resources
from typing import ClassVar

import numpy as np
from scipy import stats


@dataclass
class ESPLogKaModel:
    """Ordinary least-squares ESP→log(Ka) mapper with optional Gaussian CI bands."""

    slope: float
    intercept: float
    esp_train: np.ndarray | None = None
    logka_train: np.ndarray | None = None
    dof: int | None = None
    mse: float | None = None

    _training_csv: ClassVar[str] = "priyadarshini_2025.csv"

    @classmethod
    def from_priyadarshini_2025(cls) -> ESPLogKaModel:
        """Instantiate a model fitted on bundled placeholder CSV data.

        Warning:
            Values are **explicit placeholders** for CI/testing. The bundled CSV is constructed so that
            ``logKa_THF`` is an exact affine function of ``esp_au`` (enabling numerical regression tests).
        """

        esp, logka = cls._load_training_arrays()
        model = cls(slope=0.0, intercept=0.0)
        model.fit(esp, logka)
        return model

    @classmethod
    def _load_training_arrays(cls) -> tuple[np.ndarray, np.ndarray]:
        csv_path = resources.files("suprakit.anionfit.data").joinpath(cls._training_csv)
        raw = csv_path.read_text(encoding="utf-8")
        filtered = "\n".join(
            line for line in raw.splitlines() if line.strip() and not line.strip().startswith("#")
        )
        reader = csv.DictReader(io.StringIO(filtered))
        esp_list: list[float] = []
        logka_list: list[float] = []
        for row in reader:
            esp_list.append(float(row["esp_au"]))
            logka_list.append(float(row["logKa_THF"]))
        return np.asarray(esp_list, dtype=float), np.asarray(logka_list, dtype=float)

    def fit(self, esp: np.ndarray, logka: np.ndarray) -> ESPLogKaModel:
        """Fit using ordinary least squares."""

        if esp.shape != logka.shape:
            raise ValueError("esp and logka must share the same shape.")

        design = np.vstack([esp, np.ones_like(esp)]).T
        coef, _residuals, rank, _s = np.linalg.lstsq(design, logka, rcond=None)
        if rank < 2:
            raise ValueError("Design matrix is rank-deficient.")

        self.slope = float(coef[0])
        self.intercept = float(coef[1])

        pred = design @ coef
        rss = float(np.sum((logka - pred) ** 2))

        n = esp.shape[0]
        self.dof = max(n - 2, 1)
        self.mse = rss / self.dof

        self.esp_train = esp
        self.logka_train = logka
        return self

    def predict(self, esp: np.ndarray) -> np.ndarray:
        """Predict log(Ka) from ESP values."""

        return self.slope * esp + self.intercept

    def predict_with_ci(
        self,
        esp: np.ndarray,
        *,
        alpha: float = 0.05,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return prediction with simple OLS confidence intervals on the mean response."""

        esp = np.asarray(esp, dtype=float)
        pred = self.predict(esp)

        if self.esp_train is None or self.logka_train is None or self.mse is None:
            raise RuntimeError("Model is not fitted; cannot compute intervals.")

        n = self.esp_train.shape[0]
        x_mean = float(np.mean(self.esp_train))
        sxx = float(np.sum((self.esp_train - x_mean) ** 2))
        if sxx == 0:
            raise ValueError("Training ESP values are degenerate.")

        q = stats.t.ppf(1 - alpha / 2, df=self.dof or max(n - 2, 1))
        half_width = []
        for x in esp:
            leverage = 1.0 / n + (x - x_mean) ** 2 / sxx
            se = float(np.sqrt(self.mse * leverage))
            half_width.append(q * se)

        band = np.asarray(half_width, dtype=float)

        return pred, pred - band, pred + band


__all__ = ["ESPLogKaModel"]
