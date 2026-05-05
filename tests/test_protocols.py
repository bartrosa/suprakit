"""Tests for `suprakit.protocols` (Translator/Renderer/Validator + ValidationReport)."""

from __future__ import annotations

from suprakit.protocols import (
    Renderer,
    Translator,
    ValidationIssue,
    ValidationReport,
    Validator,
)


class _DummyTranslator:
    def translate(self, source: str) -> dict[str, str]:
        return {"text": source}


class _DummyRenderer:
    def render(self, ir: dict[str, str]) -> str:
        return ir.get("text", "")


class _DummyValidator:
    def validate(self, ir: dict[str, str]) -> ValidationReport:
        return ValidationReport(ok=True, issues=[])


class _NotATranslator:
    def something_else(self) -> None: ...


def test_translator_runtime_checkable_positive() -> None:
    assert isinstance(_DummyTranslator(), Translator)


def test_translator_runtime_checkable_negative() -> None:
    assert not isinstance(_NotATranslator(), Translator)


def test_renderer_runtime_checkable() -> None:
    assert isinstance(_DummyRenderer(), Renderer)


def test_validator_runtime_checkable() -> None:
    assert isinstance(_DummyValidator(), Validator)


def test_validation_report_filters_by_severity() -> None:
    report = ValidationReport(
        ok=False,
        issues=[
            ValidationIssue(severity="error", code="E001", message="bad"),
            ValidationIssue(severity="warning", code="W001", message="meh"),
            ValidationIssue(severity="info", code="I001", message="fyi"),
            ValidationIssue(severity="error", code="E002", message="bad-2"),
        ],
    )
    assert len(report.errors) == 2
    assert len(report.warnings) == 1
    assert len(report.infos) == 1
    assert all(i.severity == "error" for i in report.errors)


def test_validation_report_empty_default() -> None:
    report = ValidationReport(ok=True)
    assert report.issues == []
    assert report.errors == []
    assert report.warnings == []


def test_validation_issue_invalid_severity_rejected() -> None:
    import pytest
    from pydantic import ValidationError as PydanticValidationError

    with pytest.raises(PydanticValidationError):
        ValidationIssue(severity="critical", code="X", message="y")  # type: ignore[arg-type]
