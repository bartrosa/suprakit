"""`QCJobSpec` — quantum-chemistry job IR variant."""

from __future__ import annotations

import warnings
from typing import Annotated, Literal

from pydantic import Field, model_validator

from suprakit.ir.base import Phase, PositiveInt, QCEngine, StrictModel, TaskKind
from suprakit.ir.complex import ComplexSpec
from suprakit.ir.molecule import MoleculeSpec

QCTarget = Annotated[
    MoleculeSpec | ComplexSpec,
    Field(discriminator="kind"),
]


class PBCParameters(StrictModel):
    """Periodic boundary cell parameters (Angstrom / degrees)."""

    cell_a: float
    cell_b: float
    cell_c: float
    alpha: float = 90.0
    beta: float = 90.0
    gamma: float = 90.0
    periodic_dimensions: int = Field(default=3, ge=1, le=3)


class QCJobSpec(StrictModel):
    """A single QC job description: target + engine + task + method."""

    kind: Literal["qc_job"] = "qc_job"

    name: str | None = None
    description: str | None = None

    target: QCTarget

    engine: QCEngine
    task: TaskKind
    method: str

    basis_set: str | None = None
    solvent_model: str | None = None
    solvent: str | None = None

    phase: Phase = Phase.GAS
    pbc: PBCParameters | None = None

    charge_override: int | None = None
    multiplicity_override: PositiveInt | None = None

    extra_keywords: dict[str, str | float | int | bool] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_qc(self) -> QCJobSpec:
        if self.phase == Phase.SOLID and self.pbc is None:
            raise ValueError("QCJobSpec with phase='solid' requires `pbc` parameters.")

        if self.engine == QCEngine.CP2K and self.phase != Phase.SOLID:
            warnings.warn(
                "Engine 'cp2k' is typically used with solid (PBC) systems; "
                f"phase={self.phase.value!r} is non-solid.",
                stacklevel=2,
            )

        if self.engine in {QCEngine.XTB, QCEngine.CREST} and self.basis_set is not None:
            warnings.warn(
                f"Engine {self.engine.value!r} does not use basis sets; "
                "`basis_set` will be ignored by downstream renderers.",
                stacklevel=2,
            )

        return self
