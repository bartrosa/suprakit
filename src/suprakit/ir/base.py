"""Common IR primitives shared across spec variants."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base for IR models: forbids extra fields, strips strings, validates on assignment."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class Phase(StrEnum):
    """Physical phase of the system."""

    GAS = "gas"
    SOLUTION = "solution"
    SOLID = "solid"


class ComponentRole(StrEnum):
    """Role of a molecular component inside a `ComplexSpec`."""

    HOST = "host"
    GUEST = "guest"
    COUNTERION = "counterion"
    SOLVENT_EXPLICIT = "solvent_explicit"
    OTHER = "other"


class TaskKind(StrEnum):
    """High-level task an external QC engine should perform."""

    SINGLE_POINT = "single_point"
    OPTIMIZATION = "optimization"
    FREQUENCIES = "frequencies"
    CONFORMER_SEARCH = "conformer_search"
    MOLECULAR_DYNAMICS = "molecular_dynamics"


class QCEngine(StrEnum):
    """External quantum-chemistry engines that suprakit can target."""

    XTB = "xtb"
    CREST = "crest"
    PSI4 = "psi4"
    PYSCF = "pyscf"
    CP2K = "cp2k"


NonNegativeFloat = Annotated[float, Field(ge=0.0)]
PositiveInt = Annotated[int, Field(ge=1)]
