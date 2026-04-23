# SPDX-License-Identifier: Apache-2.0
"""Thin wrappers around semi-empirical xTB drivers (tblite).

This module intentionally stays minimal for bootstrap; expand alongside ESP workflows.
"""

from __future__ import annotations

from typing import Any

TBLITE_IMPORT_ERROR: Exception | None
try:
    import tblite  # noqa: F401

    TBLITE_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - environment dependent
    tblite = None
    TBLITE_IMPORT_ERROR = exc


def is_tblite_available() -> bool:
    """Return ``True`` if ``tblite`` imports successfully."""

    return TBLITE_IMPORT_ERROR is None


def xtb_singlepoint(mol_ase: Any, *, method: str = "GFN2-xTB") -> dict[str, float]:
    """Run a single-point energy evaluation using tblite's ASE calculator."""

    if not is_tblite_available():
        raise ImportError(
            "tblite is not available in this environment. Install suprakit with the `xtb` extra."
        ) from TBLITE_IMPORT_ERROR

    try:
        from tblite.ase import TBLite
    except ImportError as exc:  # pragma: no cover - version dependent
        raise ImportError(
            "Could not import `tblite.ase`. Ensure an `xtb`-compatible tblite build is installed."
        ) from exc

    calculator = TBLite(method=method)
    mol_ase.calc = calculator
    energy = float(mol_ase.get_potential_energy())
    return {"energy": energy}


def xtb_optimize(mol_ase: Any, *, method: str = "GFN2-xTB", fmax: float = 0.05) -> dict[str, float]:
    """Relax a structure with ASE + tblite."""

    if not is_tblite_available():
        raise ImportError(
            "tblite is not available in this environment. Install suprakit with the `xtb` extra."
        ) from TBLITE_IMPORT_ERROR

    try:
        from tblite.ase import TBLite
    except ImportError as exc:  # pragma: no cover - version dependent
        raise ImportError(
            "Could not import `tblite.ase`. Ensure an `xtb`-compatible tblite build is installed."
        ) from exc

    from ase.optimize import BFGS

    mol_ase.calc = TBLite(method=method)
    optimizer = BFGS(mol_ase)
    optimizer.run(fmax=fmax)  # type: ignore[no-untyped-call]
    return {"energy": float(mol_ase.get_potential_energy())}
