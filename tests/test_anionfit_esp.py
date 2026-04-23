# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest
from rdkit import Chem

from suprakit.anionfit.esp import compute_esp_at_bowl_center


def test_esp_stub_points_to_context() -> None:
    mol = Chem.MolFromSmiles("CC")
    with pytest.raises(NotImplementedError) as excinfo:
        compute_esp_at_bowl_center(mol)
    message = str(excinfo.value)
    assert "context/TODO-anionfit-esp-implementation.md" in message
