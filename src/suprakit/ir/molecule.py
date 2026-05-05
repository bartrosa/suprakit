"""`MoleculeSpec` — single-molecule IR variant."""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from suprakit.ir.base import PositiveInt, StrictModel


class MoleculeSpec(StrictModel):
    """A single chemical species described by one or more identifiers.

    At least one of ``smiles``, ``inchi``, ``name``, ``iupac_name`` or ``formula``
    must be present; everything else is optional metadata.
    """

    kind: Literal["molecule"] = "molecule"

    name: str | None = None
    description: str | None = None

    smiles: str | None = None
    inchi: str | None = None
    inchi_key: str | None = None
    iupac_name: str | None = None
    formula: str | None = None

    charge: int = 0
    multiplicity: PositiveInt = 1

    @model_validator(mode="after")
    def _at_least_one_identifier(self) -> MoleculeSpec:
        if not any(
            v is not None
            for v in (self.smiles, self.inchi, self.name, self.iupac_name, self.formula)
        ):
            raise ValueError(
                "MoleculeSpec requires at least one identifier: "
                "smiles, inchi, name, iupac_name or formula."
            )
        return self
