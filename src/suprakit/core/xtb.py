# SPDX-License-Identifier: Apache-2.0
"""Thin wrappers around semi-empirical xTB drivers (tblite).

This module intentionally stays minimal for bootstrap; expand alongside ESP workflows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

TBLITE_IMPORT_ERROR: Exception | None
try:
    import tblite  # noqa: F401

    TBLITE_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - environment dependent
    tblite = None
    TBLITE_IMPORT_ERROR = exc

EV_PER_HARTREE: float = 27.211386024998045
ANGSTROM_TO_BOHR: float = 1.8897261246257702


@dataclass(frozen=True)
class SinglePointResult:
    """Single-point xTB evalation quantities in atomic units where noted."""

    energy_hartree: float
    charges: np.ndarray  # shape (n_atoms,), Mulliken charges in units of the elementary charge (e)
    charges_method: str  # "mulliken"
    positions_bohr: np.ndarray  # shape (n_atoms, 3)
    atomic_numbers: np.ndarray  # shape (n_atoms,)


class GFN2Backend:
    """Thin wrapper over tblite GFN2-xTB with optional ALPB solvation.

    All energies are returned in Hartree atomic units. Positions are returned in Bohr.
    """

    def __init__(
        self,
        solvent: str | None = "thf",
        *,
        charge: int = 0,
        uhf: int = 0,
    ) -> None:
        self._solvent = solvent
        self._charge = charge
        self._uhf = uhf

    def _tblite_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "method": "GFN2-xTB",
            "charge": self._charge,
            "verbosity": 0,
        }
        # tblite ASE docs: multiplicity is supported; map a simple "uhf electrons" knob to
        # multiplicity. For closed-shell molecules (default), leave multiplicity unset.
        if self._uhf != 0:
            kwargs["multiplicity"] = self._uhf + 1
        if self._solvent:
            kwargs["solvation"] = ("alpb", str(self._solvent).lower())
        return kwargs

    def singlepoint(
        self,
        atomic_numbers: np.ndarray,
        positions_angstrom: np.ndarray,
    ) -> SinglePointResult:
        """Evaluate energy + Mulliken charges at the provided geometry (Å)."""

        if not is_tblite_available():
            raise ImportError(
                "tblite is not available. Install suprakit with the `xtb` extra.",
            ) from TBLITE_IMPORT_ERROR

        from ase import Atoms
        from tblite.ase import TBLite

        atoms = Atoms(
            numbers=np.asarray(atomic_numbers, dtype=int),
            positions=np.asarray(positions_angstrom, dtype=float),
        )
        atoms.calc = TBLite(**self._tblite_kwargs())

        energy_ev = float(atoms.get_potential_energy())  # type: ignore[no-untyped-call]
        charges = np.asarray(atoms.get_charges(), dtype=np.float64)  # type: ignore[no-untyped-call]
        positions_angstrom = np.asarray(atoms.get_positions(), dtype=np.float64)  # type: ignore[no-untyped-call]
        positions_bohr = positions_angstrom * ANGSTROM_TO_BOHR

        return SinglePointResult(
            energy_hartree=energy_ev / EV_PER_HARTREE,
            charges=charges,
            charges_method="mulliken",
            positions_bohr=positions_bohr,
            atomic_numbers=np.asarray(atomic_numbers, dtype=int),
        )

    def optimize(
        self,
        atomic_numbers: np.ndarray,
        positions_angstrom: np.ndarray,
        *,
        fmax: float = 0.05,
    ) -> SinglePointResult:
        """Relax geometry using ASE + tblite (LBFGS preferred; BFGS fallback)."""

        if not is_tblite_available():
            raise ImportError(
                "tblite is not available. Install suprakit with the `xtb` extra.",
            ) from TBLITE_IMPORT_ERROR

        from ase import Atoms
        from tblite.ase import TBLite

        atoms = Atoms(
            numbers=np.asarray(atomic_numbers, dtype=int),
            positions=np.asarray(positions_angstrom, dtype=float),
        )
        atoms.calc = TBLite(**self._tblite_kwargs())

        from ase import optimize as ase_opt

        opt_cls = getattr(ase_opt, "LBFGS", ase_opt.BFGS)
        opt_cls(atoms).run(fmax=fmax)
        relaxed = np.asarray(atoms.get_positions(), dtype=np.float64)  # type: ignore[no-untyped-call]
        return self.singlepoint(atomic_numbers, relaxed)


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


__all__ = [
    "ANGSTROM_TO_BOHR",
    "EV_PER_HARTREE",
    "GFN2Backend",
    "SinglePointResult",
    "is_tblite_available",
    "xtb_optimize",
    "xtb_singlepoint",
]
