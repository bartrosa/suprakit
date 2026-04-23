# Installation

suprakit uses **`uv`** as the single workflow tool for environments, locking, and command execution.

The Makefile targets wrap `uv run …` invocations so contributors do not need to memorize long CLI flags.

## CPU (Linux x86_64 recommended for tblite wheels)

```bash
make install
```

This installs:

- optional extras **`chem`** (RDKit + ASE) and **`xtb`** (`tblite` Python bindings)
- optional extra **`cpu`** (PyTorch CPU wheels)
- dependency group **`dev`** (tests, docs, lint)

### Apple Silicon (arm64 macOS)

PyPI ships **manylinux x86_64** wheels for `tblite`. On arm64 macOS, `tblite` may build from source and can require a Fortran toolchain plus OpenMP (`brew install gcc libomp cmake pkgconf`) before `make install` succeeds.

If `tblite` installation fails locally, use:

```bash
make install-lite
```

This installs **`chem` + `cpu` + `dev`** without `tblite`. Core RDKit workflows and tests continue to work; xTB-backed features remain unavailable until `tblite` can be installed.

## Apple Silicon — PyTorch MPS

```bash
make install-mps
```

PyTorch wheels from PyPI enable MPS on arm64 macOS without extra indexes.

## CUDA (Linux + NVIDIA GPU)

```bash
make install-cuda
```

This prints and uses the PyTorch CUDA wheel index (`cu121`). For JAX CUDA wheels, prefer the upstream guidance:

```bash
uv add "jax[cuda12]" --index-url https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
```

### External chemistry binaries (CREST / `xtb` CLI)

The `anionfit` bootstrap path relies on **`tblite`** Python wheels on supported platforms and does **not** require the standalone `xtb` executable.

If you need **CREST** or the **`xtb` CLI** for other workflows, install them separately (system package manager, conda-forge, or source builds).

## Runtime backend selection

Many modules route accelerator selection through `suprakit.core.device.detect_device`.

```bash
SUPRAKIT_DEVICE=cpu make test
SUPRAKIT_DEVICE=mps make notebook
```

See [Performance](performance.md) for guidance on threading, OpenMP, and optional ML accelerators.
