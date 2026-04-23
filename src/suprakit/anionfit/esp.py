# SPDX-License-Identifier: Apache-2.0
"""Electrostatic potential (ESP) probes for resorcin[4]arene bowls.

This module evaluates an approximate molecular ESP at an in-bowl probe using **Mulliken partial
charges** from a GFN2-xTB ``tblite`` calculation (via ASE) and a classical point-charge potential:

.. math::

    \\phi(\\mathbf{r}) = \\sum_i \\frac{q_i}{|\\mathbf{r} - \\mathbf{r}_i|}

with :math:`q_i` given by Mulliken partitioning (as reported by ``tblite.ase.TBLite`` through ASE),
and coordinates expressed in **Bohr** for consistency with atomic units of electrostatic potential.

The ``tblite`` documented ASE calculator surfaces **do not** expose an explicit “evaluate exact
Hartree–Fock/xTB density ESP on an arbitrary grid/probe” API (see ``context/tblite-api-discovery.txt``).
This point-charge approximation is standard for rapid host–guest screening and tracks correlated
trends used in linear ESP→binding metrics; any additive offset is largely absorbed when recalibrating
the linear model.

Probe geometry (stable, versioned defaults):
    The bowl centroid :math:`\\mathbf{C}` is the mean position of the four upper-rim aromatic carbons.
    The bowl axis :math:`\\hat{\\mathbf{n}}` points from the lower-rim centroid :math:`\\mathbf{L}`
    (ipso carbons for supported substituents) to :math:`\\mathbf{C}`, normalized:

    .. math::
        \\hat{\\mathbf{n}} = \\frac{\\mathbf{C}-\\mathbf{L}}{\\|\\mathbf{C}-\\mathbf{L}\\|}

    The probe point is:

    .. math::
        \\mathbf{P} = \\mathbf{C} + r_{\\mathrm{probe}} \\hat{\\mathbf{n}}

    where :math:`r_{\\mathrm{probe}}` defaults to ``PROBE_OFFSET_BOHR``. Changing offsets or axis
    conventions is a **breaking change** for fitted correlation models (re-fit required).
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem

from suprakit.anionfit.receptors import lower_rim_ipso_atom_indices, upper_rim_atom_indices
from suprakit.core.parallel import molecule_map_parallel
from suprakit.core.xtb import ANGSTROM_TO_BOHR, GFN2Backend, SinglePointResult, is_tblite_available

logger = logging.getLogger(__name__)

_DEFAULT_AXIS_NORM_MIN: float = 1e-8

DEFAULT_PROBE_OFFSET_ANGSTROM: float = 2.0
PROBE_OFFSET_BOHR: float = DEFAULT_PROBE_OFFSET_ANGSTROM * ANGSTROM_TO_BOHR


@dataclass(frozen=True)
class EspResult:
    esp_au: float
    probe_xyz_bohr: np.ndarray
    bowl_centroid_xyz_bohr: np.ndarray
    bowl_axis: np.ndarray
    charges: np.ndarray
    charges_method: str
    energy_hartree: float
    n_atoms: int


def esp_point_charge_atomic_units(
    charges: np.ndarray,
    positions_bohr: np.ndarray,
    probe_bohr: np.ndarray,
    *,
    eps: float = 1e-12,
) -> float:
    """Evaluate the Mulliken point-charge ESP at ``probe_bohr`` (atomic units)."""

    vectors = positions_bohr - probe_bohr[None, :]
    distances = np.linalg.norm(vectors, axis=1)
    distances = np.maximum(distances, eps)
    return float(np.sum(charges / distances))


def bowl_probe_vectors(
    upper_xyz_bohr: np.ndarray,
    lower_xyz_bohr: np.ndarray,
    *,
    probe_offset_bohr: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute bowl centroid (upper rim), axis (lower→upper), and probe point."""

    centroid_up = np.mean(upper_xyz_bohr, axis=0)
    centroid_lo = np.mean(lower_xyz_bohr, axis=0)
    axis_vec = centroid_up - centroid_lo
    axis_norm = float(np.linalg.norm(axis_vec))
    if axis_norm < _DEFAULT_AXIS_NORM_MIN:
        raise RuntimeError("Degenerate bowl axis (upper/lower centroids coincide).")

    axis_hat = axis_vec / axis_norm
    probe_bohr = centroid_up + probe_offset_bohr * axis_hat
    return centroid_up.astype(float), axis_hat.astype(float), probe_bohr.astype(float)


def compute_esp_at_bowl_center(  # noqa: PLR0913
    mol: Chem.Mol,
    *,
    solvent: str | None = "thf",
    charge: int = 0,
    optimize: bool = True,
    probe_offset_bohr: float = PROBE_OFFSET_BOHR,
    random_seed: int = 42,
) -> EspResult:
    """Compute Mulliken point-charge ESP at the bowl probe for ``mol``."""

    if not is_tblite_available():
        raise ImportError(
            "tblite is required for ESP evaluation. Install suprakit with the `xtb` extra "
            "(see docs/installation.md)."
        )

    mh = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = random_seed
    status = AllChem.EmbedMolecule(mh, params)
    if status != 0:
        raise RuntimeError("RDKit ETKDG embedding failed for the provided molecule.")

    nums = np.array(
        [mh.GetAtomWithIdx(i).GetAtomicNum() for i in range(mh.GetNumAtoms())], dtype=int
    )
    conf = mh.GetConformer()
    positions_angstrom = np.array(
        [
            [conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z]
            for i in range(mh.GetNumAtoms())
        ],
        dtype=float,
    )

    backend = GFN2Backend(solvent=solvent, charge=charge)
    result: SinglePointResult
    if optimize:
        result = backend.optimize(nums, positions_angstrom)
    else:
        result = backend.singlepoint(nums, positions_angstrom)

    upper_idx = upper_rim_atom_indices(mh)
    lower_idx = lower_rim_ipso_atom_indices(mh)

    upper_coord_bohr = np.stack([result.positions_bohr[i] for i in upper_idx], axis=0)
    lower_coord_bohr = np.stack([result.positions_bohr[i] for i in lower_idx], axis=0)

    centroid_up, axis_hat, probe_bohr = bowl_probe_vectors(
        upper_coord_bohr,
        lower_coord_bohr,
        probe_offset_bohr=probe_offset_bohr,
    )

    esp = esp_point_charge_atomic_units(result.charges, result.positions_bohr, probe_bohr)

    return EspResult(
        esp_au=esp,
        probe_xyz_bohr=np.asarray(probe_bohr, dtype=float),
        bowl_centroid_xyz_bohr=np.asarray(centroid_up, dtype=float),
        bowl_axis=np.asarray(axis_hat, dtype=float),
        charges=np.asarray(result.charges, dtype=float),
        charges_method=result.charges_method,
        energy_hartree=float(result.energy_hartree),
        n_atoms=int(result.atomic_numbers.shape[0]),
    )


def compute_esp_batch(
    mols: Sequence[Chem.Mol],
    *,
    solvent: str | None = "thf",
    n_jobs: int = -1,
    **kwargs: Any,
) -> list[EspResult | Exception]:
    """Compute ESP for many molecules in parallel.

    Exceptions are captured **per molecule** and returned in-place (order-preserving).
    """

    def _worker(mol: Chem.Mol) -> EspResult | Exception:
        try:
            return compute_esp_at_bowl_center(mol, solvent=solvent, **kwargs)
        except Exception as exc:
            return exc

    results = molecule_map_parallel(_worker, list(mols), n_jobs=n_jobs)
    failures = sum(1 for item in results if isinstance(item, Exception))
    if failures:
        logger.warning("ESP batch finished with %s/%s failures", failures, len(results))

    return results


__all__ = [
    "DEFAULT_PROBE_OFFSET_ANGSTROM",
    "PROBE_OFFSET_BOHR",
    "EspResult",
    "bowl_probe_vectors",
    "compute_esp_at_bowl_center",
    "compute_esp_batch",
    "esp_point_charge_atomic_units",
]
