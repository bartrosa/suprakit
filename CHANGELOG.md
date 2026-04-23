# Changelog

## [Unreleased]

### Added

- `anionfit.esp`: GFN2-xTB ESP at bowl probe via tblite, with point-charge approximation. Closes TODO-anionfit-esp-implementation.
- `core.xtb.GFN2Backend`: swappable ESP backend abstraction.

## 0.1.0 — 2026-04-23

### Added

- Initial Python package scaffold (`suprakit`) with `uv` + `Makefile` workflow.
- Core utilities for device detection, parallelism, geometry, and minimal `tblite` hooks.
- `anionfit` module for resorcin[4]arene assembly, substituent enumeration, and ESP→log(Ka) linear modeling.
- Documentation skeleton (MkDocs Material) and CI workflows for tests + docs publishing hooks.

### Notes

- Optional extras split **`chem`** (RDKit + ASE) vs **`xtb`** (`tblite`) to keep installs tractable across platforms.
