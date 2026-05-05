"""Round-trip tests for YAML/JSON serialization of `SupraSpec`."""

from __future__ import annotations

from pathlib import Path

import pytest

from suprakit.exceptions import IRError
from suprakit.ir import (
    ComplexSpec,
    MoleculeSpec,
    QCJobSpec,
    ReactionSystemSpec,
    dump_json,
    dump_yaml,
    load_json,
    load_json_file,
    load_yaml,
    load_yaml_file,
)

FIXTURES = Path(__file__).parent.parent / "data" / "ir"

VARIANT_TYPES = {
    "ethanol.yaml": MoleculeSpec,
    "crown_ether_complex.yaml": ComplexSpec,
    "michaelis_menten.yaml": ReactionSystemSpec,
    "xtb_optimization.yaml": QCJobSpec,
}


@pytest.mark.parametrize("fixture", sorted(VARIANT_TYPES))
def test_yaml_fixture_loads(fixture: str) -> None:
    spec = load_yaml_file(FIXTURES / fixture)
    assert isinstance(spec.root, VARIANT_TYPES[fixture])


@pytest.mark.parametrize("fixture", sorted(VARIANT_TYPES))
def test_yaml_roundtrip(fixture: str) -> None:
    spec = load_yaml_file(FIXTURES / fixture)
    again = load_yaml(dump_yaml(spec))
    assert spec == again


@pytest.mark.parametrize("fixture", sorted(VARIANT_TYPES))
def test_json_roundtrip(fixture: str) -> None:
    spec = load_yaml_file(FIXTURES / fixture)
    again = load_json(dump_json(spec))
    assert spec == again


@pytest.mark.parametrize("fixture", sorted(VARIANT_TYPES))
def test_json_file_roundtrip(tmp_path: Path, fixture: str) -> None:
    spec = load_yaml_file(FIXTURES / fixture)
    json_path = tmp_path / fixture.replace(".yaml", ".json")
    json_path.write_text(dump_json(spec), encoding="utf-8")
    again = load_json_file(json_path)
    assert spec == again


def test_dump_yaml_string_output() -> None:
    spec = load_yaml_file(FIXTURES / "ethanol.yaml")
    text = dump_yaml(spec)
    assert "kind: molecule" in text
    assert "smiles: CCO" in text


def test_dump_json_default_indent() -> None:
    spec = load_yaml_file(FIXTURES / "ethanol.yaml")
    text = dump_json(spec)
    assert text.startswith("{\n")


def test_dump_json_compact() -> None:
    spec = load_yaml_file(FIXTURES / "ethanol.yaml")
    text = dump_json(spec, indent=None)
    assert "\n" not in text


def test_load_invalid_yaml_raises() -> None:
    with pytest.raises(IRError):
        load_yaml(":\n  invalid: [unclosed")


def test_load_yaml_non_mapping_raises() -> None:
    with pytest.raises(IRError):
        load_yaml("- just\n- a list\n")


def test_load_invalid_json_raises() -> None:
    with pytest.raises(IRError):
        load_json("{not json")


def test_load_json_non_mapping_raises() -> None:
    with pytest.raises(IRError):
        load_json("[1, 2, 3]")
