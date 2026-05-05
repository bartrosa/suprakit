"""JSON / YAML serialization helpers for `SupraSpec` (round-trip stable)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from suprakit.exceptions import IRError
from suprakit.ir.spec import SupraSpec


def dump_yaml(spec: SupraSpec) -> str:
    """Serialize a `SupraSpec` to a YAML string."""

    return yaml.safe_dump(
        spec.to_dict(),
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )


def load_yaml(s: str) -> SupraSpec:
    """Deserialize a YAML string into a `SupraSpec`."""

    try:
        data = yaml.safe_load(s)
    except yaml.YAMLError as exc:
        raise IRError(f"Invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise IRError("Top-level YAML document must be a mapping.")
    return SupraSpec.from_dict(data)


def dump_json(spec: SupraSpec, *, indent: int | None = 2) -> str:
    """Serialize a `SupraSpec` to a JSON string."""

    return json.dumps(spec.to_dict(), indent=indent, ensure_ascii=False, sort_keys=False)


def load_json(s: str) -> SupraSpec:
    """Deserialize a JSON string into a `SupraSpec`."""

    try:
        data = json.loads(s)
    except json.JSONDecodeError as exc:
        raise IRError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise IRError("Top-level JSON value must be an object.")
    return SupraSpec.from_dict(data)


def load_yaml_file(path: str | Path) -> SupraSpec:
    """Load and parse a YAML file into a `SupraSpec`."""

    return load_yaml(Path(path).read_text(encoding="utf-8"))


def load_json_file(path: str | Path) -> SupraSpec:
    """Load and parse a JSON file into a `SupraSpec`."""

    return load_json(Path(path).read_text(encoding="utf-8"))
