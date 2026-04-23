# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

try:
    import tblite  # noqa: F401

    HAS_TBLITE = True
except Exception:
    HAS_TBLITE = False


requires_tblite = pytest.mark.skipif(not HAS_TBLITE, reason="tblite optional extra not installed")
