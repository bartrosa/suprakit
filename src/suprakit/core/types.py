# SPDX-License-Identifier: Apache-2.0
"""Lightweight typing helpers shared across suprakit."""

from __future__ import annotations

from typing import Any, TypeAlias

JSONArray: TypeAlias = list[Any]
JSONObject: TypeAlias = dict[str, Any]
