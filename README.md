# suprakit

**suprakit** is two things in one repository: a **long-term roadmap** from natural language to chemical/biological DSLs and quantum-chemistry inputs, and a **working toolkit today** for computational supramolecular chemistry—including **anionfit**, **xtb/tblite helpers**, geometry utilities, and a **CLI**.

## Status

Alpha · WIP (roadmap pre-alpha for NL→DSL; computational modules are farther along)

## Idea

Business-facing scenarios and executable checks stay aligned when teams share *examples* in a structured language—this is the familiar BDD story with Gherkin. **suprakit** applies the same separation of concerns to chemistry: stakeholders describe hosts, guests, and assemblies in natural language; the toolkit maps that intent onto DSLs such as SMILES or SBML and eventually onto QC input decks. Mixed-oracle workflows (rules, models, and calculators) sit behind stable interfaces so the science can evolve without rewriting the whole pipeline.

## What works today

The repo already ships Python modules used in notebooks and tests:

- **`suprakit.anionfit`** — ESP / binding-style workflows and bundled datasets (see `notebooks/`).
- **`suprakit.core`** — geometry, I/O, parallelism, **tblite/xtb**-oriented helpers where optional deps are installed.
- **`suprakit.cli`** — Typer-based CLI (`suprakit` entry point after install).

Full docs for the computational stack live in **`docs/`** (MkDocs). Install **chem + xtb + cpu** extras for the same environment as `make install`.

## Roadmap (NL → DSL → QC)

- **PR 0** — Bootstrap repo (packaging, CI, quality stack, docs stubs) — **combined with existing computational code**.
- **PR 1** — **SupraSpec** IR + protocols + ADRs.
- **PR 2** — Multi-provider LLM abstraction.
- **PR 3** — NL → SMILES.
- **PR 4** — NL → SBML.
- **PR 5** — QC pipeline (xtb + crest).
- **PR 6** — CLI (extend/reconcile with current CLI).
- **PR 7** — Evaluation harness.

See [`docs/roadmap.md`](docs/roadmap.md).

## Quick start

```bash
git clone https://github.com/<your-org>/suprakit.git
cd suprakit
make install
make check
```

Use `make install-lite` if **tblite** fails to install on your platform (skips xtb extra; some tests may be skipped or fail—prefer full install on Linux x86_64 CI).

Replace the clone URL with your fork or upstream repository.

## Development

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for setup variants (`install`, `install-lite`, `install-mps`, …), conventions, and `make check`.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE). (Roadmap/ADR docs follow the same repo license.)
