"""Tests for `suprakit.ir.reaction.ReactionSystemSpec`."""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from suprakit.ir import (
    Compartment,
    Reaction,
    ReactionSystemSpec,
    Species,
    StoichiometryItem,
    SystemConditions,
)


def _mm_species() -> list[Species]:
    return [
        Species(id="E", initial_concentration=1e-6),
        Species(id="S", initial_concentration=1e-3),
        Species(id="ES"),
        Species(id="P"),
    ]


def _mm_reactions() -> list[Reaction]:
    return [
        Reaction(
            id="r1",
            reactants=[
                StoichiometryItem(species_id="E"),
                StoichiometryItem(species_id="S"),
            ],
            products=[StoichiometryItem(species_id="ES")],
            rate_law="k1 * E * S",
            parameters={"k1": 1e6},
        ),
        Reaction(
            id="r2",
            reactants=[StoichiometryItem(species_id="ES")],
            products=[
                StoichiometryItem(species_id="E"),
                StoichiometryItem(species_id="P"),
            ],
            rate_law="kcat * ES",
            parameters={"kcat": 100.0},
        ),
    ]


def test_reaction_system_minimal_valid() -> None:
    rs = ReactionSystemSpec(species=_mm_species(), reactions=_mm_reactions())
    assert rs.kind == "reaction_system"
    assert len(rs.species) == 4
    assert len(rs.reactions) == 2


def test_reaction_system_duplicate_species_id_raises() -> None:
    species = [Species(id="A"), Species(id="A")]
    with pytest.raises(PydanticValidationError) as exc:
        ReactionSystemSpec(species=species, reactions=[])
    assert "Species ids must be unique" in str(exc.value)


def test_reaction_system_duplicate_reaction_id_raises() -> None:
    reactions = [
        Reaction(
            id="r1",
            reactants=[StoichiometryItem(species_id="E")],
            products=[StoichiometryItem(species_id="P")],
            rate_law="k * E",
        ),
        Reaction(
            id="r1",
            reactants=[StoichiometryItem(species_id="P")],
            products=[StoichiometryItem(species_id="E")],
            rate_law="k * P",
        ),
    ]
    with pytest.raises(PydanticValidationError) as exc:
        ReactionSystemSpec(
            species=[Species(id="E"), Species(id="P")],
            reactions=reactions,
        )
    assert "Reaction ids must be unique" in str(exc.value)


def test_reaction_system_unknown_species_in_reactants_raises() -> None:
    reactions = [
        Reaction(
            id="r1",
            reactants=[StoichiometryItem(species_id="MISSING")],
            products=[StoichiometryItem(species_id="E")],
            rate_law="k * MISSING",
        )
    ]
    with pytest.raises(PydanticValidationError) as exc:
        ReactionSystemSpec(species=[Species(id="E")], reactions=reactions)
    assert "unknown species_id 'MISSING'" in str(exc.value)


def test_reaction_system_unknown_species_in_products_raises() -> None:
    reactions = [
        Reaction(
            id="r1",
            reactants=[StoichiometryItem(species_id="E")],
            products=[StoichiometryItem(species_id="MISSING")],
            rate_law="k * E",
        )
    ]
    with pytest.raises(PydanticValidationError):
        ReactionSystemSpec(species=[Species(id="E")], reactions=reactions)


def test_reaction_system_unknown_compartment_raises() -> None:
    species = [Species(id="E", compartment_id="cytoplasm")]
    with pytest.raises(PydanticValidationError) as exc:
        ReactionSystemSpec(species=species, reactions=[])
    assert "unknown compartment_id 'cytoplasm'" in str(exc.value)


def test_reaction_system_with_compartments_ok() -> None:
    rs = ReactionSystemSpec(
        species=[Species(id="E", compartment_id="cyto")],
        reactions=[],
        compartments=[Compartment(id="cyto", name="cytoplasm")],
    )
    assert rs.species[0].compartment_id == "cyto"


def test_reaction_system_kind_literal_rejects_other() -> None:
    with pytest.raises(PydanticValidationError):
        ReactionSystemSpec(  # type: ignore[arg-type]
            kind="bad",
            species=[Species(id="E")],
            reactions=[],
        )


def test_reaction_system_extra_field_forbidden() -> None:
    with pytest.raises(PydanticValidationError):
        ReactionSystemSpec(species=[Species(id="E")], reactions=[], foo=1)  # type: ignore[call-arg]


def test_stoichiometry_coefficient_must_be_positive() -> None:
    with pytest.raises(PydanticValidationError):
        StoichiometryItem(species_id="E", coefficient=0)


def test_species_initial_concentration_must_be_non_negative() -> None:
    with pytest.raises(PydanticValidationError):
        Species(id="E", initial_concentration=-1.0)


def test_reaction_system_with_conditions() -> None:
    rs = ReactionSystemSpec(
        species=_mm_species(),
        reactions=_mm_reactions(),
        conditions=SystemConditions(temperature_kelvin=298.15, ph=7.4),
    )
    assert rs.conditions is not None
    assert rs.conditions.temperature_kelvin == 298.15
