"""`ComplexSpec` — supramolecular host/guest assembly IR variant."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from suprakit.ir.base import ComponentRole, Phase, PositiveInt, StrictModel
from suprakit.ir.molecule import MoleculeSpec

MIN_COMPONENTS = 2


class ComplexComponent(StrictModel):
    """One molecular building block of a `ComplexSpec`."""

    molecule: MoleculeSpec
    count: PositiveInt = 1
    role: ComponentRole = ComponentRole.OTHER


class ComplexSpec(StrictModel):
    """A multi-component supramolecular system (host/guest, ion pair, …)."""

    kind: Literal["complex"] = "complex"

    name: str | None = None
    description: str | None = None

    components: list[ComplexComponent]
    phase: Phase = Phase.GAS

    total_charge: int = 0
    total_multiplicity: PositiveInt = 1

    expected_geometry: str | None = None
    non_covalent_hints: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_components(self) -> ComplexSpec:
        if len(self.components) < MIN_COMPONENTS:
            raise ValueError(f"ComplexSpec requires at least {MIN_COMPONENTS} components.")
        if "total_charge" in self.model_fields_set:
            computed = sum(c.count * c.molecule.charge for c in self.components)
            if computed != self.total_charge:
                raise ValueError(
                    f"total_charge={self.total_charge} does not match the sum of "
                    f"component charges (computed: {computed})."
                )
        return self
