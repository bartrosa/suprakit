# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from suprakit.anionfit.substituents import enumerate_patterns


def test_symmetric_enumerator_cardinality() -> None:
    codes = ["NO2", "CN", "CHO"]
    patterns = enumerate_patterns(codes, symmetric_only=True)
    assert len(patterns) == len(codes)


def test_cartesian_enumerator_count() -> None:
    codes = ["NO2", "CN"]
    patterns = enumerate_patterns(codes, symmetric_only=False)
    assert len(patterns) == len(codes) ** 4
