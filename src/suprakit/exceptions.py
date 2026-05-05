"""Domain exception hierarchy for suprakit."""

from __future__ import annotations


class SuprakitError(Exception):
    """Base exception for all suprakit errors."""


class IRError(SuprakitError):
    """IR-related errors (validation, serialization)."""


class TranslationError(SuprakitError):
    """Translator failed to produce valid IR."""


class RenderError(SuprakitError):
    """Renderer failed to produce output."""


class ValidationError(SuprakitError):
    """Semantic validation failed."""
