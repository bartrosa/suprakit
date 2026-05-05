"""Tests for `suprakit.ir.complex.ComplexSpec`."""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from suprakit.ir import (
    ComplexComponent,
    ComplexSpec,
    ComponentRole,
    MoleculeSpec,
    Phase,
)


def _two_components() -> list[ComplexComponent]:
    return [
        ComplexComponent(
            molecule=MoleculeSpec(name="18-crown-6", smiles="C1COCCOCCOCCOCCOCCO1"),
            role=ComponentRole.HOST,
        ),
        ComplexComponent(
            molecule=MoleculeSpec(name="K+", smiles="[K+]", charge=1),
            role=ComponentRole.GUEST,
        ),
    ]


def test_complex_minimal_valid_two_components() -> None:
    c = ComplexSpec(components=_two_components())
    assert c.kind == "complex"
    assert len(c.components) == 2
    assert c.phase == Phase.GAS
    assert c.non_covalent_hints == []


def test_complex_invalid_too_few_components() -> None:
    with pytest.raises(PydanticValidationError) as exc:
        ComplexSpec(
            components=[
                ComplexComponent(molecule=MoleculeSpec(smiles="CCO")),
            ]
        )
    assert "at least 2 components" in str(exc.value)


def test_complex_invalid_zero_components() -> None:
    with pytest.raises(PydanticValidationError):
        ComplexSpec(components=[])


def test_complex_charge_consistency_explicit_match() -> None:
    c = ComplexSpec(components=_two_components(), total_charge=1)
    assert c.total_charge == 1


def test_complex_charge_consistency_explicit_mismatch_raises() -> None:
    with pytest.raises(PydanticValidationError) as exc:
        ComplexSpec(components=_two_components(), total_charge=0)
    assert "does not match" in str(exc.value)


def test_complex_charge_implicit_default_skips_check() -> None:
    c = ComplexSpec(components=_two_components())
    assert c.total_charge == 0


def test_complex_kind_literal_rejects_other() -> None:
    with pytest.raises(PydanticValidationError):
        ComplexSpec(kind="bad", components=_two_components())  # type: ignore[arg-type]


def test_complex_extra_field_forbidden() -> None:
    with pytest.raises(PydanticValidationError):
        ComplexSpec(components=_two_components(), foo="bar")  # type: ignore[call-arg]


def test_complex_phase_solid_accepted() -> None:
    c = ComplexSpec(components=_two_components(), phase=Phase.SOLID, total_charge=1)
    assert c.phase == Phase.SOLID


def test_complex_component_role_default_is_other() -> None:
    comp = ComplexComponent(molecule=MoleculeSpec(smiles="CCO"))
    assert comp.role == ComponentRole.OTHER
    assert comp.count == 1


def test_complex_component_count_must_be_positive() -> None:
    with pytest.raises(PydanticValidationError):
        ComplexComponent(molecule=MoleculeSpec(smiles="CCO"), count=0)


def test_complex_charge_uses_count_multiplier() -> None:
    components = [
        ComplexComponent(molecule=MoleculeSpec(smiles="[Na+]", charge=1), count=2),
        ComplexComponent(molecule=MoleculeSpec(smiles="[Cl-]", charge=-1), count=2),
    ]
    c = ComplexSpec(components=components, total_charge=0)
    assert c.total_charge == 0


def test_complex_charge_count_multiplier_mismatch() -> None:
    components = [
        ComplexComponent(molecule=MoleculeSpec(smiles="[Na+]", charge=1), count=2),
        ComplexComponent(molecule=MoleculeSpec(smiles="[Cl-]", charge=-1), count=1),
    ]
    with pytest.raises(PydanticValidationError):
        ComplexSpec(components=components, total_charge=0)
