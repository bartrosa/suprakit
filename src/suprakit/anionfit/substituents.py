# SPDX-License-Identifier: Apache-2.0
"""Substituent dictionaries and enumerators for EWG-pattern screening."""

from __future__ import annotations

import itertools
from collections.abc import Iterable, Sequence

from rdkit import Chem

# Keys are short labels used in CLI (`4xNO2`) and notebooks.
EWG_SMILES: dict[str, str] = {
    "NO2": "[*]N(=O)=O",
    "CN": "[*]C#N",
    "CHO": "[*]C=O",
    "CF3": "[*]C(F)(F)F",
    "SO2CH3": "[*]S(=O)(=O)C",
    "COCH3": "[*]C(=O)C",
    "CONH2": "[*]C(=O)N",
    "Br": "[*]Br",
    "Cl": "[*]Cl",
    "C6F5": "[*]c1c(F)c(F)c(F)c(F)c1F",
}


def fragment_mol(code: str) -> Chem.Mol:
    """Return RDKit mol for substituent ``code`` with a leading dummy attachment atom."""

    smiles = EWG_SMILES[code]
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid fragment SMILES for {code}: {smiles!r}")
    return mol


def enumerate_patterns(
    ewg_codes: Iterable[str],
    *,
    symmetric_only: bool = True,
) -> list[tuple[str, ...]]:
    """Enumerate lower-rim substitution patterns (length four).

    Args:
        ewg_codes: Pool of substituent labels (must exist in ``EWG_SMILES``).
        symmetric_only: If ``True``, only return uniform ``4×X`` combinations.

    Returns:
        Distinct 4-tuples of substituent codes.
    """

    pool = list(dict.fromkeys(ewg_codes))
    unknown = sorted({c for c in pool if c not in EWG_SMILES})
    if unknown:
        raise KeyError(f"Unknown substituent codes: {unknown}")

    if symmetric_only:
        return [(code,) * 4 for code in pool]

    combos = tuple(itertools.product(pool, repeat=4))
    # Represent distinct combinations under cyclic symmetry would need extra logic; bootstrap keeps cartesian product.
    return sorted(set(combos))


def smiles_combo(pattern: Sequence[str]) -> str:
    """Human-readable descriptor for a substitution pattern."""

    parts = []
    counts: dict[str, int] = {}
    for code in pattern:
        counts[code] = counts.get(code, 0) + 1
    for code, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        parts.append(f"{n}x{code}")
    return "+".join(parts)
