# ADR-0001: Tech stack — Python 3.11+, uv, pydantic v2, Hatchling

- Status: accepted
- Date: 2026-05-05

## Context

`suprakit` is greenfield: NL → DSL → QC inputs for supramolecular chemistry. From the very start we need:

- A **modern Python** (≥3.11) so we can rely on native `X | Y` unions, `typing.Protocol[…]`, structural pattern matching where useful, and good performance.
- A **fast, reproducible package & environment manager** that supports a single `uv.lock`.
- A **schema-first data layer** that emits JSON Schema directly (we want to feed it to LLMs in PR 2+ as structured-output specs).
- A **multi-provider LLM** layer later, plus optional binary toolchains (RDKit, libsbml, xtb/crest), each of which has its own packaging quirks.
- Strong static guarantees: a strict type checker, an opinionated linter/formatter, and a fast test runner — all wired into pre-commit and CI.
- Permissive licensing aligned with scientific Python (Apache-2.0 / MIT-friendly).

We do not want to invent a build system or a settings layer ourselves; we do want the core tooling to be boring.

## Decision

- **Language**: Python ≥3.11 (CI matrix: 3.11, 3.12).
- **Package & env manager**: [uv](https://docs.astral.sh/uv/). `uv.lock` is committed for reproducibility.
- **Build backend**: [Hatchling](https://hatch.pypa.io/) (`src/`-layout, `packages = ["src/suprakit"]`).
- **Data layer**: [pydantic v2](https://docs.pydantic.dev/) — used for the IR (`SupraSpec` and variants in PR 1) and for in-process settings starting in PR 2 (via `pydantic-settings`). v1 is **not** supported.
- **Quality stack**: [ruff](https://docs.astral.sh/ruff/) (lint + format), [mypy](https://mypy.readthedocs.io/) (`strict` for `suprakit.core.*`, `suprakit.ir.*`, `suprakit.protocols`, `suprakit.exceptions`), [pytest](https://pytest.org/), [pre-commit](https://pre-commit.com/), GitHub Actions.
- **License**: Apache-2.0 (matches the scientific Python ecosystem and the existing computational modules in this repo).

## Consequences

- **Pros**: Single, fast, reproducible install path (`make install`); JSON Schema "for free" from pydantic v2; modern type system unblocks expressive IR (discriminated unions). pre-commit + strict mypy raise the floor of every PR.
- **Cons / trade-offs**:
  - pydantic v2 still lags behind some scientific libraries that target v1. Where this bites (e.g. `libsbml` adapters in PR 4), we wrap rather than mix.
  - `uv` is younger than pip/poetry; we accept the version churn in exchange for speed and the integrated lockfile.
  - Strict mypy for `core` / `ir` / `protocols` requires per-module overrides for chemistry-heavy code (RDKit, scipy stubs); those overrides are scoped tightly.

## Alternatives considered

- **poetry**: rejected — slower install path, less integrated lockfile-vs-resolver story, and weaker support for our planned extras matrix (cpu/mps/cuda, jax, mlip, …).
- **conda env as primary**: rejected as primary — slows day-to-day work and locks contributors into a non-standard wheel ecosystem. We **do** rely on conda-style binaries indirectly for some QC tools in PR 5 (xtb, crest), but only at the edges.
- **pydantic v1**: rejected — sunsetted; v2's discriminated unions, `RootModel`, `TypeAdapter`, and JSON Schema are central to the IR.
- **DataClasses + manual JSON Schema**: rejected — duplicates work and drifts; the cost of pydantic is paid once and amortized.
- **Black + isort + flake8**: rejected — `ruff` collapses them into one fast tool and matches our editor integration.
