# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from suprakit.core import device


@pytest.fixture(autouse=True)
def _reset_device_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPRAKIT_DEVICE", raising=False)
    device._logged_backend = None


def test_suprakit_device_env_override_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPRAKIT_DEVICE", "cpu")
    info = device.detect_device()
    assert info.backend == "cpu"


def test_suprakit_device_infer_cuda(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(device, "_infer_default_backend", lambda prefer: "cuda")  # type: ignore[arg-type]
    info = device.detect_device()
    assert info.backend == "cuda"
    assert info.supports_float64 is True


def test_suprakit_device_infer_mps(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(device, "_infer_default_backend", lambda prefer: "mps")  # type: ignore[arg-type]
    info = device.detect_device()
    assert info.backend == "mps"
    assert info.supports_float64 is False


def test_suprakit_device_invalid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPRAKIT_DEVICE", "not-a-backend")
    with pytest.raises(ValueError):
        device.detect_device()
