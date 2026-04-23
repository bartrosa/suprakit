# SPDX-License-Identifier: Apache-2.0
"""Small molecule I/O helpers built on RDKit."""

from __future__ import annotations

from pathlib import Path

from rdkit import Chem


def read_smiles(smiles: str, *, sanitize: bool = True) -> Chem.Mol:
    """Parse SMILES into an RDKit molecule."""

    mol = Chem.MolFromSmiles(smiles, sanitize=sanitize)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles!r}")
    return mol


def to_smiles(mol: Chem.Mol, *, canonical: bool = True) -> str:
    """Serialize an RDKit molecule to SMILES."""

    return Chem.MolToSmiles(mol, canonical=canonical)


def read_sdf_mol(path: str | Path, *, idx: int = 0) -> Chem.Mol:
    """Read the ``idx``-th molecule from an SD file."""

    supplier = Chem.SDMolSupplier(str(path), sanitize=False)
    mol = supplier[idx]
    if mol is None:
        raise ValueError(f"Could not read molecule index {idx} from {path}")
    Chem.SanitizeMol(mol)
    return mol
