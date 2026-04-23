# suprakit

Computational toolkit for supramolecular chemistry — cages, capsules, and macrocyclic hosts.

[![CI](https://img.shields.io/github/actions/workflow/status/suprakit/suprakit/ci.yml?branch=main&label=CI&logo=github)](https://github.com/suprakit/suprakit/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11--3.13-blue.svg)](pyproject.toml)

## What is this?

suprakit is an Apache-2.0 Python toolkit for reproducible computational workflows around non-covalent assemblies: molecular cages/capsules, macrocyclic hosts, and calibrated binding descriptors.

This repository starts from semi-empirical workflows (GFN2-xTB via tblite where available, RDKit cheminformatics, NumPy/SciPy numerics). The intent is to reproduce published computational protocols and iterate on hypotheses with open tools.

## Install

### CPU

```bash
make install
```

### Apple Silicon

```bash
make install-mps
```

### CUDA

```bash
make install-cuda
```

Then:

```bash
make hooks
```

Notes:

- **`chem`** installs RDKit + ASE; **`xtb`** installs tblite bindings. Linux x86_64 CI benefits from tblite wheels; arm64 macOS users may prefer `make install-lite` when tblite fails to build locally (see `docs/installation.md`).

## Quick example

```bash
make cli ARGS='anionfit predict 4xNO2 --use-placeholder-table'
```

Equivalent Python snippet:

```python
import numpy as np
from suprakit.anionfit.predict import ESPLogKaModel

model = ESPLogKaModel.from_priyadarshini_2025()
print(float(model.predict(np.array([0.20]))))
```

The bundled calibration CSV ships **explicit placeholders**, not experimental measurements.

## Modules

| Module | Status | Hardware |
| --- | --- | --- |
| `anionfit` | stable-ish (CPU workflows) | CPU (+ optional tblite/OpenMP) |
| `ecdfast` | planned | CPU |
| `cagelab` | planned | CPU / optional MPS / CUDA |
| `mechanomol` | planned | CUDA recommended |

## Development

Common tasks:

```bash
make test
make lint
make typecheck
make docs
```

Accelerator routing lives in `suprakit.core.device.detect_device`; see [`docs/performance.md`](docs/performance.md).

Runtime overrides:

```bash
SUPRAKIT_DEVICE=cpu make test
SUPRAKIT_DEVICE=mps make notebook
```

Commits follow Conventional Commits (see `docs/contributing.md`). Native acceleration policy lives in `native/README.md`.

## Citing

```bibtex
@software{suprakit2026,
  title        = {suprakit},
  howpublished = {GitHub repository},
  year         = {2026},
}
```

If you rely on downstream tools (xtb ecosystem, RDKit, ASE), cite those works directly.

## Acknowledgments

This project builds on ecosystem tools including (non-exhaustive):

- extended tight-binding models and implementations in the **xtb** ecosystem (doi:[10.1021/acs.jctc.8b00959](https://doi.org/10.1021/acs.jctc.8b00959))
- **tblite** Python bindings wrapping GFN-xTB Hamiltonians (see upstream repository documentation)
- **CREST** workflows for conformer / reaction exploration (doi:[10.1063/5.0197596](https://doi.org/10.1063/5.0197596))
- **RDKit** cheminformatics (doi:[10.1021/ci050400p](https://doi.org/10.1021/ci050400p))
- **ASE** structures and calculators (doi:[10.1088/1361-648X/ad1497](https://doi.org/10.1088/1361-648X/ad1497))

## License

Apache-2.0 — see [`LICENSE`](LICENSE).
