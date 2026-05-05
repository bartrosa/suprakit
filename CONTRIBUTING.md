# Contributing

Thank you for helping improve **suprakit**. This document covers setup, workflow, and quality expectations.

## Setup

Install [uv](https://docs.astral.sh/uv/). From the repository root:

```bash
make install
```

This runs:

- `uv sync --extra dev --extra chem --extra xtb --extra cpu` — runtime stack for **RDKit/ASE**, **tblite (xtb)**, **PyTorch (cpu)**, plus dev tools (pytest, ruff, mypy, pre-commit, MkDocs, Jupyter, …).
- `uv run pre-commit install` — Git hooks.

If **tblite** does not install on your machine, use:

```bash
make install-lite
```

(`chem` + `cpu` + `dev` only; some xtb-focused tests may not apply.)

Apple Silicon / CUDA variants: `make install-mps` or `make install-cuda` (see `Makefile`).

## Workflow

- Branch from `main`.
- Prefer **one PR focused on one roadmap step** (see [`docs/roadmap.md`](docs/roadmap.md)), even when touching existing computational modules.
- Capture meaningful architecture decisions as ADRs under `docs/adr/` when you introduce them (expect more from PR 1 onward).

## Conventions

- **Formatting & lint**: [Ruff](https://docs.astral.sh/ruff/) — `make lint`, `make format`, or `make check`.
- **Types**: [mypy](https://mypy.readthedocs.io/) — `make typecheck`. Third-party chemistry/ML imports are configured with `ignore_missing_imports`; **`suprakit.core`** is checked with **strict** settings (see `pyproject.toml`).
- **Tests**: [pytest](https://pytest.org/) with coverage in the default `addopts`. Use markers `integration` and `slow` for heavier tests (they are excluded from the default `make test` / CI selection).

## Commands

Full gate before push (matches CI intent):

```bash
make check
```

Optional: run every hook on all files:

```bash
uv run pre-commit run --all-files
```

Documentation (MkDocs): `make docs` or `make docs-build`.
