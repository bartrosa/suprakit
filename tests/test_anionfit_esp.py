# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import numpy as np
import pytest
from rdkit import Chem

from suprakit.anionfit import receptors as receptors_mod
from suprakit.anionfit.esp import (
    EspResult,
    bowl_probe_vectors,
    compute_esp_at_bowl_center,
    compute_esp_batch,
    esp_point_charge_atomic_units,
)
from suprakit.anionfit.receptors import (
    UPPER_RIM_PRIMARY_SMARTS,
    build_resorcin4arene,
    upper_rim_atom_indices,
)
from suprakit.core.xtb import ANGSTROM_TO_BOHR, GFN2Backend, is_tblite_available

_tblite_available = is_tblite_available


def test_upper_rim_smarts_matches_four_atoms_on_reference_receptor() -> None:
    mol = Chem.MolFromSmiles(receptors_mod._PARENT_CALIX_RESORCINARENE_SMILES)
    assert mol is not None
    mol_h = Chem.RemoveHs(Chem.AddHs(mol))
    primary = Chem.MolFromSmarts(UPPER_RIM_PRIMARY_SMARTS)
    matches = mol_h.GetSubstructMatches(primary)
    assert len(matches) == 4
    ordered = upper_rim_atom_indices(mol_h)
    assert ordered == tuple(sorted(ordered))


def test_bowl_axis_points_outward() -> None:
    upper = np.tile(np.array([0.0, 0.0, 2.0], dtype=float), (4, 1))
    lower = np.zeros((4, 3), dtype=float)
    _centroid_up, axis_hat, _probe = bowl_probe_vectors(
        upper,
        lower,
        probe_offset_bohr=1.0,
    )
    assert axis_hat[2] > 0.0


@pytest.mark.skipif(not _tblite_available(), reason="tblite / xtb extra required")
def test_compute_esp_water_dimer_reference() -> None:
    """Sanity-check Mulliken charges + point-charge ESP sum against a tiny water dimer."""

    try:
        from ase.build import molecule  # noqa: PLC0415
    except ImportError:
        pytest.skip("ase.build.molecule not available")

    left = molecule("H2O")
    right = molecule("H2O")
    right.translate([5.5, 0.0, 0.0])
    atoms = left + right
    nums = np.asarray(atoms.get_atomic_numbers(), dtype=int)
    pos = np.asarray(atoms.get_positions(), dtype=float)

    backend = GFN2Backend(solvent=None)
    res = backend.singlepoint(nums, pos)

    probe_a = np.array([-3.0, 0.0, 0.0], dtype=float) * ANGSTROM_TO_BOHR
    probe_b = np.array([8.5, 0.0, 0.0], dtype=float) * ANGSTROM_TO_BOHR

    esp_neg_side = esp_point_charge_atomic_units(res.charges, res.positions_bohr, probe_a)
    esp_pos_side = esp_point_charge_atomic_units(res.charges, res.positions_bohr, probe_b)

    assert np.isfinite(esp_neg_side)
    assert np.isfinite(esp_pos_side)
    assert esp_neg_side < esp_pos_side


@pytest.mark.skipif(not _tblite_available(), reason="tblite / xtb extra required")
def test_compute_esp_at_bowl_center_returns_finite_au() -> None:
    mol = build_resorcin4arene(["NO2"] * 4, upper_rim="hydroxyl")
    out = compute_esp_at_bowl_center(mol, solvent="thf", optimize=False, random_seed=7)

    assert np.isfinite(out.esp_au)
    assert -1.0 < out.esp_au < 1.0
    assert out.probe_xyz_bohr.shape == (3,)
    assert out.bowl_centroid_xyz_bohr.shape == (3,)
    assert out.bowl_axis.shape == (3,)
    assert out.charges.shape == (out.n_atoms,)
    assert out.charges_method == "mulliken"


@pytest.mark.skipif(not _tblite_available(), reason="tblite / xtb extra required")
def test_compute_esp_batch_captures_exceptions() -> None:
    ok = build_resorcin4arene(["NO2"] * 4, upper_rim="hydroxyl")
    bad = Chem.MolFromSmiles("CC")
    assert bad is not None

    results = compute_esp_batch([ok, bad, ok, ok], optimize=False, n_jobs=1, random_seed=0)
    assert len(results) == 4
    assert isinstance(results[0], EspResult)
    assert isinstance(results[1], Exception)
    assert isinstance(results[2], EspResult)
    assert isinstance(results[3], EspResult)


@pytest.mark.skipif(not _tblite_available(), reason="tblite / xtb extra required")
def test_probe_offset_invariance_of_ranking() -> None:
    mol_no2 = build_resorcin4arene(["NO2"] * 4, upper_rim="hydroxyl")
    mol_cn = build_resorcin4arene(["CN"] * 4, upper_rim="hydroxyl")

    base = {"solvent": "thf", "optimize": False, "random_seed": 99}
    a_lo = compute_esp_at_bowl_center(mol_no2, probe_offset_bohr=3.5, **base)
    b_lo = compute_esp_at_bowl_center(mol_cn, probe_offset_bohr=3.5, **base)
    a_hi = compute_esp_at_bowl_center(mol_no2, probe_offset_bohr=4.0, **base)
    b_hi = compute_esp_at_bowl_center(mol_cn, probe_offset_bohr=4.0, **base)

    diff_lo = a_lo.esp_au - b_lo.esp_au
    diff_hi = a_hi.esp_au - b_hi.esp_au
    assert diff_lo * diff_hi > 0.0


@pytest.mark.skipif(
    _tblite_available(),
    reason="tblite installed: ESP entry point is implemented (no ImportError)",
)
def test_compute_esp_import_error_without_tblite() -> None:
    mol = build_resorcin4arene(["NO2"] * 4, upper_rim="hydroxyl")
    with pytest.raises(ImportError, match="tblite"):
        compute_esp_at_bowl_center(mol)
