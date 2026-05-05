"""Abstract protocols for Translator, Renderer, Validator (PR 1 contracts)."""

from __future__ import annotations

from typing import Literal, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel, ConfigDict

NLT_contra = TypeVar("NLT_contra", contravariant=True)
IRT_co = TypeVar("IRT_co", covariant=True)
IRT_contra = TypeVar("IRT_contra", contravariant=True)
OutT_co = TypeVar("OutT_co", covariant=True)

Severity = Literal["error", "warning", "info"]


class ValidationIssue(BaseModel):
    """A single semantic validation finding produced by a `Validator`."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    severity: Severity
    code: str
    message: str
    path: str | None = None


class ValidationReport(BaseModel):
    """Aggregate of validation issues with convenience filters."""

    model_config = ConfigDict(extra="forbid")

    ok: bool
    issues: list[ValidationIssue] = []

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def infos(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "info"]


@runtime_checkable
class Translator(Protocol[NLT_contra, IRT_co]):
    """Translates input (typically natural language) into a suprakit IR value."""

    def translate(self, source: NLT_contra) -> IRT_co: ...


@runtime_checkable
class Renderer(Protocol[IRT_contra, OutT_co]):
    """Renders an IR value into a concrete output format (SMILES, SBML, QC input, …)."""

    def render(self, ir: IRT_contra) -> OutT_co: ...


@runtime_checkable
class Validator(Protocol[IRT_contra]):
    """Performs semantic checks on an IR value beyond pydantic structural validation."""

    def validate(self, ir: IRT_contra) -> ValidationReport: ...
