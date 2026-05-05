"""Smoke tests for PR 0 bootstrap. Real tests come in PR 1+."""

import suprakit


def test_package_imports() -> None:
    assert suprakit is not None


def test_version_present() -> None:
    assert hasattr(suprakit, "__version__")
    assert isinstance(suprakit.__version__, str)
