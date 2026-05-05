"""Tests for `suprakit.ir.molecule.MoleculeSpec`."""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from suprakit.ir import MoleculeSpec


def test_molecule_minimal_valid_with_smiles() -> None:
    m = MoleculeSpec(smiles="CCO")
    assert m.kind == "molecule"
    assert m.smiles == "CCO"
    assert m.charge == 0
    assert m.multiplicity == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("smiles", "CCO"),
        ("inchi", "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"),
        ("name", "ethanol"),
        ("iupac_name", "ethan-1-ol"),
        ("formula", "C2H6O"),
    ],
)
def test_molecule_minimal_valid_per_identifier(field: str, value: str) -> None:
    m = MoleculeSpec(**{field: value})
    assert getattr(m, field) == value


def test_molecule_invalid_no_identifier() -> None:
    with pytest.raises(PydanticValidationError) as exc:
        MoleculeSpec()
    assert "at least one identifier" in str(exc.value)


def test_molecule_invalid_only_inchi_key_no_id() -> None:
    with pytest.raises(PydanticValidationError):
        MoleculeSpec(inchi_key="LFQSCWFLJHTTHZ-UHFFFAOYSA-N", description="ethanol-ish")


def test_molecule_kind_literal_rejects_other() -> None:
    with pytest.raises(PydanticValidationError):
        MoleculeSpec(kind="not_a_molecule", smiles="CCO")  # type: ignore[arg-type]


def test_molecule_kind_default() -> None:
    assert MoleculeSpec(smiles="CCO").kind == "molecule"


def test_molecule_extra_field_forbidden() -> None:
    with pytest.raises(PydanticValidationError):
        MoleculeSpec(smiles="CCO", unknown_field="x")  # type: ignore[call-arg]


def test_molecule_str_strip_whitespace() -> None:
    m = MoleculeSpec(smiles="  CCO  ", name="  ethanol  ")
    assert m.smiles == "CCO"
    assert m.name == "ethanol"


def test_molecule_multiplicity_must_be_positive() -> None:
    with pytest.raises(PydanticValidationError):
        MoleculeSpec(smiles="CCO", multiplicity=0)


def test_molecule_charge_can_be_negative() -> None:
    m = MoleculeSpec(smiles="[Cl-]", charge=-1)
    assert m.charge == -1


def test_molecule_validate_assignment_enforces_identifier() -> None:
    m = MoleculeSpec(smiles="CCO")
    with pytest.raises(PydanticValidationError):
        m.smiles = None
        m.name = None
        m.formula = None
