"""Tests for the `SupraSpec` root and JSON Schema export."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError as PydanticValidationError

from suprakit.ir import (
    ComplexSpec,
    MoleculeSpec,
    QCJobSpec,
    ReactionSystemSpec,
    SupraSpec,
    get_json_schema,
)


def test_discriminated_union_picks_molecule() -> None:
    spec = SupraSpec.from_dict({"kind": "molecule", "smiles": "CCO"})
    assert isinstance(spec.root, MoleculeSpec)


def test_discriminated_union_picks_complex() -> None:
    spec = SupraSpec.from_dict(
        {
            "kind": "complex",
            "components": [
                {"molecule": {"kind": "molecule", "smiles": "CCO"}},
                {"molecule": {"kind": "molecule", "smiles": "O"}},
            ],
        }
    )
    assert isinstance(spec.root, ComplexSpec)


def test_discriminated_union_picks_reaction_system() -> None:
    spec = SupraSpec.from_dict(
        {
            "kind": "reaction_system",
            "species": [{"id": "A"}, {"id": "B"}],
            "reactions": [],
        }
    )
    assert isinstance(spec.root, ReactionSystemSpec)


def test_discriminated_union_picks_qc_job() -> None:
    spec = SupraSpec.from_dict(
        {
            "kind": "qc_job",
            "target": {"kind": "molecule", "smiles": "CCO"},
            "engine": "xtb",
            "task": "single_point",
            "method": "GFN2-xTB",
        }
    )
    assert isinstance(spec.root, QCJobSpec)


def test_unknown_kind_raises() -> None:
    with pytest.raises(PydanticValidationError):
        SupraSpec.from_dict({"kind": "unknown", "smiles": "CCO"})


def test_missing_kind_raises() -> None:
    with pytest.raises(PydanticValidationError):
        SupraSpec.from_dict({"smiles": "CCO"})


def test_to_dict_round_trip() -> None:
    payload = {"kind": "molecule", "smiles": "CCO", "name": "ethanol"}
    spec = SupraSpec.from_dict(payload)
    again = SupraSpec.from_dict(spec.to_dict())
    assert spec == again


def test_to_dict_excludes_none() -> None:
    spec = SupraSpec.from_dict({"kind": "molecule", "smiles": "CCO"})
    dumped = spec.to_dict()
    assert "inchi" not in dumped
    assert dumped["kind"] == "molecule"


def test_json_schema_exports_dict() -> None:
    schema = get_json_schema()
    assert isinstance(schema, dict)
    assert "oneOf" in schema or "anyOf" in schema or "$defs" in schema


def test_json_schema_has_all_variants() -> None:
    schema = get_json_schema()
    raw = json.dumps(schema)
    for kind in ("molecule", "complex", "reaction_system", "qc_job"):
        assert kind in raw, f"variant {kind!r} missing in JSON Schema"


def test_json_schema_uses_kind_discriminator() -> None:
    schema = get_json_schema()
    discriminator = schema.get("discriminator", {})
    assert discriminator.get("propertyName") == "kind"
    mapping = discriminator.get("mapping", {})
    assert set(mapping.keys()) == {"molecule", "complex", "reaction_system", "qc_job"}


def test_qcjob_target_discrimination_via_supraspec() -> None:
    spec = SupraSpec.from_dict(
        {
            "kind": "qc_job",
            "target": {
                "kind": "complex",
                "components": [
                    {"molecule": {"kind": "molecule", "smiles": "CCO"}},
                    {"molecule": {"kind": "molecule", "smiles": "O"}},
                ],
            },
            "engine": "xtb",
            "task": "optimization",
            "method": "GFN2-xTB",
        }
    )
    assert isinstance(spec.root, QCJobSpec)
    assert isinstance(spec.root.target, ComplexSpec)
