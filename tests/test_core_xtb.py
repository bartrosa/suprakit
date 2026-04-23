# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest
from ase import Atoms

from suprakit.core.xtb import is_tblite_available, xtb_singlepoint

try:
    import tblite  # noqa: F401

    HAS_TBLITE = True
except Exception:
    HAS_TBLITE = False

requires_tblite = pytest.mark.skipif(not HAS_TBLITE, reason="tblite optional extra not installed")


@requires_tblite
def test_xtb_singlepoint_on_diatomic() -> None:
    atoms = Atoms("H2", positions=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]])
    result = xtb_singlepoint(atoms)
    assert "energy" in result


def test_xtb_import_error_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    from suprakit.core import xtb

    monkeypatch.setattr(xtb, "is_tblite_available", lambda: False)
    atoms = Atoms("H")
    with pytest.raises(ImportError):
        xtb_singlepoint(atoms)


def test_is_tblite_matches_environment() -> None:
    assert is_tblite_available() == HAS_TBLITE
