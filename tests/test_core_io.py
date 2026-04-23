# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from suprakit.core.io import read_smiles, to_smiles


def test_read_smiles_roundtrip() -> None:
    mol = read_smiles("CCO")
    assert mol.GetNumAtoms() == 3
    smiles = to_smiles(mol)
    assert "C" in smiles


def test_read_smiles_invalid() -> None:
    with pytest.raises(ValueError):
        read_smiles("ZZZINVALID")
