# SPDX-License-Identifier: Apache-2.0
"""Core utilities (I/O, numerics, xTB plumbing, device selection, parallelism)."""

from suprakit.core.device import (
    Backend,
    DeviceInfo,
    default_dtype,
    default_numpy_dtype,
    detect_device,
)
from suprakit.core.io import read_sdf_mol, read_smiles, to_smiles
from suprakit.core.parallel import molecule_map
from suprakit.core.xtb import (
    TBLITE_IMPORT_ERROR,
    is_tblite_available,
    xtb_optimize,
    xtb_singlepoint,
)

__all__ = [
    "TBLITE_IMPORT_ERROR",
    "Backend",
    "DeviceInfo",
    "default_dtype",
    "default_numpy_dtype",
    "detect_device",
    "is_tblite_available",
    "molecule_map",
    "read_sdf_mol",
    "read_smiles",
    "to_smiles",
    "xtb_optimize",
    "xtb_singlepoint",
]
