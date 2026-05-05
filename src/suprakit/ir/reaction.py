"""`ReactionSystemSpec` — kinetic / reaction-network IR variant (SBML-shaped)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from suprakit.ir.base import NonNegativeFloat, PositiveInt, StrictModel
from suprakit.ir.molecule import MoleculeSpec


class StoichiometryItem(StrictModel):
    """A single reactant/product entry inside a `Reaction`."""

    species_id: str
    coefficient: PositiveInt = 1


class Compartment(StrictModel):
    """A spatial compartment hosting species (cytoplasm, vesicle, …)."""

    id: str
    name: str | None = None
    size: float = 1.0


class SystemConditions(StrictModel):
    """Environmental conditions applied to the reaction system."""

    temperature_kelvin: float | None = None
    ph: float | None = None
    ionic_strength_molar: float | None = None


class Species(StrictModel):
    """A chemical species participating in reactions."""

    id: str
    name: str | None = None
    molecule: MoleculeSpec | None = None
    initial_concentration: NonNegativeFloat = 0.0
    boundary: bool = False
    compartment_id: str | None = None


class Reaction(StrictModel):
    """A reaction step described by a symbolic rate law."""

    id: str
    name: str | None = None
    reactants: list[StoichiometryItem]
    products: list[StoichiometryItem]
    rate_law: str
    parameters: dict[str, float] = Field(default_factory=dict)
    reversible: bool = False


class ReactionSystemSpec(StrictModel):
    """A network of species and reactions (typically rendered to SBML later)."""

    kind: Literal["reaction_system"] = "reaction_system"

    name: str | None = None
    description: str | None = None

    species: list[Species]
    reactions: list[Reaction]
    compartments: list[Compartment] = Field(default_factory=list)
    conditions: SystemConditions | None = None

    @model_validator(mode="after")
    def _validate_references(self) -> ReactionSystemSpec:
        species_ids = [s.id for s in self.species]
        if len(species_ids) != len(set(species_ids)):
            raise ValueError("Species ids must be unique.")

        reaction_ids = [r.id for r in self.reactions]
        if len(reaction_ids) != len(set(reaction_ids)):
            raise ValueError("Reaction ids must be unique.")

        species_set = set(species_ids)
        for r in self.reactions:
            for item in (*r.reactants, *r.products):
                if item.species_id not in species_set:
                    raise ValueError(
                        f"Reaction {r.id!r} references unknown species_id {item.species_id!r}."
                    )

        compartment_ids = {c.id for c in self.compartments}
        for s in self.species:
            if s.compartment_id is not None and s.compartment_id not in compartment_ids:
                raise ValueError(
                    f"Species {s.id!r} references unknown compartment_id {s.compartment_id!r}."
                )
        return self
