# SPDX-License-Identifier: Apache-2.0
"""Runtime device/backend detection for accelerator-aware workflows."""

from __future__ import annotations

import logging
import os
import platform
from dataclasses import dataclass
from typing import Any, Literal, cast

import numpy as np

Backend = Literal["cpu", "mps", "cuda"]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeviceInfo:
    backend: Backend
    torch_device: str
    label: str
    supports_float64: bool
    supports_jax: bool


_logged_backend: Backend | None = None


def _validate_backend(value: str) -> Backend:
    lowered = value.strip().lower()
    if lowered not in {"cpu", "mps", "cuda"}:
        raise ValueError(f"Invalid backend {value!r}; expected cpu|mps|cuda.")
    return lowered  # type: ignore[return-value]


def _infer_default_backend(prefer: Backend | None) -> Backend:
    if prefer is not None:
        return prefer

    try:
        import torch
    except ImportError:
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"

    if torch.backends.mps.is_available() and platform.machine() == "arm64":
        return "mps"

    return "cpu"


def _supports_jax(backend: Backend) -> bool:
    if backend == "mps":
        return False

    import importlib.util

    return importlib.util.find_spec("jax") is not None


def detect_device(prefer: Backend | None = None) -> DeviceInfo:
    """Detect compute backend preference for Torch-oriented workloads.

    Selection order:

    - ``SUPRAKIT_DEVICE`` explicit override (`cpu`|`mps`|`cuda`)
    - ``prefer`` argument when provided and env override absent
    - CUDA if ``torch.cuda.is_available()``
    - MPS if available on arm64 macOS
    - CPU otherwise

    If Torch is not installed, ``SUPRAKIT_DEVICE`` / ``prefer`` still determine the reported backend so tests can
    validate routing without installing accelerators.
    """

    env_raw = os.environ.get("SUPRAKIT_DEVICE")
    if env_raw is not None:
        backend = _validate_backend(env_raw)
    else:
        backend = _infer_default_backend(prefer)

    global _logged_backend
    if _logged_backend is None:
        logger.info("suprakit backend selected: %s", backend)
        _logged_backend = backend

    if backend == "cuda":
        torch_device = "cuda:0"
        label = "CUDA GPU (CUDA)"
        supports_float64 = True
    elif backend == "mps":
        torch_device = "mps"
        label = "Apple Silicon (MPS)"
        supports_float64 = False
    else:
        torch_device = "cpu"
        label = "CPU"
        supports_float64 = True

    return DeviceInfo(
        backend=backend,
        torch_device=torch_device,
        label=label,
        supports_float64=supports_float64,
        supports_jax=_supports_jax(backend),
    )


def default_numpy_dtype(device_info: DeviceInfo) -> np.dtype[np.float64 | np.float32]:
    """Return NumPy floating dtype respecting device capabilities and overrides."""

    override = os.environ.get("SUPRAKIT_DTYPE")
    if override:
        dtype = np.dtype(override)
        return cast(np.dtype[np.float64 | np.float32], dtype)

    return np.dtype(np.float64 if device_info.supports_float64 else np.float32)


def default_dtype(device_info: DeviceInfo) -> Any:
    """Return Torch dtype best suited to ``device_info``."""

    numpy_dtype = default_numpy_dtype(device_info)

    try:
        import torch
    except ImportError:
        raise ImportError(
            "`default_dtype()` requires PyTorch (`torch`) to be installed "
            "(optional extra `cpu`/`mps`/`cuda`)."
        ) from None

    mapping = {
        np.dtype(np.float64): torch.float64,
        np.dtype(np.float32): torch.float32,
    }

    mapped = mapping.get(numpy_dtype)
    if mapped is None:
        raise ValueError(f"Unsupported SUPRAKIT_DTYPE={numpy_dtype!r} for Torch mapping.")

    return mapped
