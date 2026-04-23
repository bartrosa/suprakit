# SPDX-License-Identifier: Apache-2.0
"""Electrostatic potential (ESP) probes for resorcin[4]arene bowls (tblite-backed)."""

from __future__ import annotations

from collections.abc import Sequence

from rdkit import Chem

from suprakit.core.parallel import molecule_map_parallel


def compute_esp_at_bowl_center(mol: Chem.Mol, *, solvent: str = "thf") -> float:
    """Compute ESP (atomic units) at an in-bowl probe for a receptor.

    This function is intentionally not implemented in the bootstrap release; see
    ``context/TODO-anionfit-esp-implementation.md`` for the investigation plan.

    Intended steps (future work):

    - RDKit ETKDG embedding
    - ``tblite`` GFN2-xTB + polarizable continuum / ALPB-style solvation consistent with solvent string
    - Identify four upper-rim aromatic carbons, form a bowl centroid, offset a probe slightly along the inward normal
    - Evaluate ESP at that point

    Raises:
        NotImplementedError: always, until tblite ESP extraction is verified end-to-end.
    """

    _ = (mol, solvent)
    raise NotImplementedError(
        "ESP evaluation is deferred; see context/TODO-anionfit-esp-implementation.md for status and API notes."
    )


def compute_esp_batch(
    mols: Sequence[Chem.Mol],
    *,
    solvent: str = "thf",
    n_jobs: int = -1,
) -> list[float]:
    """Batch driver for :func:`compute_esp_at_bowl_center` (placeholder)."""

    def _fn(m: Chem.Mol) -> float:
        return compute_esp_at_bowl_center(m, solvent=solvent)

    return molecule_map_parallel(_fn, list(mols), n_jobs=n_jobs)


__all__ = ["compute_esp_at_bowl_center", "compute_esp_batch"]
