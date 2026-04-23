# `anionfit`

`anionfit` hosts workflows for correlating computed surface electrostatics with experimental binding metrics, starting from:

- receptor construction helpers for resorcin[4]arene scaffolds (`anionfit.receptors`)
- substituent dictionaries / enumerators (`anionfit.substituents`)
- linear ESP→log(Ka) calibration (`anionfit.predict`)

Electrostatic evaluation via **tblite** (`anionfit.esp`) is staged behind explicit documentation in `context/TODO-anionfit-esp-implementation.md` until the Python API surface is fully validated.

## Design constraints (bootstrap)

- **CPU-only** for `anionfit` logic: no torch/JAX imports in `anionfit/`.
- Parallelism uses `suprakit.core.parallel.molecule_map` with safe OpenMP settings.
