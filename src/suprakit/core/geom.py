# SPDX-License-Identifier: Apache-2.0
"""Geometry helpers for 3D coordinates and simple molecular metrics."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem


def centroid_coords(mol: Chem.Mol, atom_indices: Sequence[int], conf_id: int = -1) -> np.ndarray:
    """Return centroid for selected atoms (shape ``(3,)``)."""

    if not atom_indices:
        raise ValueError("atom_indices must be non-empty.")

    conf = mol.GetConformer(conf_id)
    pts = np.array(
        [
            [conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z]
            for i in atom_indices
        ],
        dtype=float,
    )
    return np.asarray(np.mean(pts, axis=0), dtype=float)


def embed_mol(mol: Chem.Mol, *, random_seed: int = 42) -> Chem.Mol:
    """Embed 3D coordinates using ETKDG."""

    mh = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()  # type: ignore[attr-defined]
    params.randomSeed = random_seed
    status = AllChem.EmbedMolecule(mh, params)  # type: ignore[attr-defined]
    if status != 0:
        raise RuntimeError("RDKit ETKDG embedding failed for the provided molecule.")
    AllChem.MMFFOptimizeMolecule(mh)  # type: ignore[attr-defined]
    return mh


def pairwise_distances(coords: np.ndarray) -> np.ndarray:
    """Return pairwise distances for Nx3 coordinate array."""

    diff = coords[:, None, :] - coords[None, :, :]
    return np.asarray(np.sqrt(np.sum(diff * diff, axis=-1)), dtype=float)
