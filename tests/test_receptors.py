# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from suprakit.anionfit.receptors import build_resorcin4arene


def test_build_resorcin4arene_nitro_symmetric() -> None:
    mol = build_resorcin4arene(["NO2", "NO2", "NO2", "NO2"], upper_rim="hydroxyl")
    assert mol.GetNumHeavyAtoms() == 48


def test_build_multiple_substituents() -> None:
    mol = build_resorcin4arene(["NO2", "CN", "CHO", "Br"], upper_rim="hydroxyl")
    assert mol.GetNumHeavyAtoms() > 40
