# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typer.testing import CliRunner

from suprakit.cli import app


def test_anionfit_predict_with_placeholder_table() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["anionfit", "predict", "4xNO2", "--use-placeholder-table"])
    assert result.exit_code == 0
    assert "log10 Ka" in result.stdout


def test_anionfit_predict_requires_esp_when_missing() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["anionfit", "predict", "4xCN"])
    assert result.exit_code == 2
