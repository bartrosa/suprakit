"""`SupraSpec` — root discriminated union over all IR variants."""

from typing import Annotated, Any

from pydantic import Field, RootModel, TypeAdapter

from suprakit.ir.complex import ComplexSpec
from suprakit.ir.molecule import MoleculeSpec
from suprakit.ir.qcjob import QCJobSpec
from suprakit.ir.reaction import ReactionSystemSpec

SupraSpecVariant = Annotated[
    MoleculeSpec | ComplexSpec | ReactionSystemSpec | QCJobSpec,
    Field(discriminator="kind"),
]


class SupraSpec(RootModel[SupraSpecVariant]):
    """Root container for any IR variant. Discriminated by the `kind` field."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SupraSpec":
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        dumped = self.model_dump(mode="json", exclude_none=True)
        assert isinstance(dumped, dict)
        return dumped


SupraSpecAdapter: TypeAdapter[Any] = TypeAdapter(SupraSpecVariant)


def get_json_schema() -> dict[str, Any]:
    """Return the full JSON Schema covering every `SupraSpec` variant."""

    return SupraSpecAdapter.json_schema()
