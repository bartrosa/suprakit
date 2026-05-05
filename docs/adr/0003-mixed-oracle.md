# ADR-0003: Mixed-oracle validation — deterministic by default, LLM-as-judge in eval

- Status: accepted
- Date: 2026-05-05

## Context

Translating natural language into IR and rendering IR into SMILES/SBML/QC inputs is a chain where each step can drift from intent. We need a way to ask: **"is this still the right molecule / system / job?"**

Two tempting extremes:

1. **Pure deterministic checks**: parse outputs, canonicalize, reject what doesn't round-trip. Catches structural and syntactic regressions, but is **blind to semantics** ("does this SMILES actually describe ethanol?", "does B3LYP/def2-SVP make sense for this host?").
2. **LLM-as-judge end-to-end**: ask a strong model to score whether the output matches the prompt's intent. Catches semantics, but is **expensive, non-deterministic, and flaky** in CI; it also undermines reproducibility.

We want the strengths of both while paying for each only when it earns its keep.

## Decision

We adopt a **two-layer oracle** with the following responsibilities and defaults:

### Layer 1 — Deterministic (always on)

Runs in pre-commit / CI on every PR. Cheap, repeatable, no network. Includes:

- **Pydantic structural validation** of every IR value (PR 1).
- **Output parsability**: round-trip canonicalization where applicable (e.g. SMILES via RDKit in PR 3, SBML well-formedness in PR 4).
- **Schema conformance**: `SupraSpec.json_schema()` → JSON Schema validation of round-tripped fixtures.
- **Smoke execution where it's cheap**:
  - Reaction systems: a tiny tellurium / SBML simulation step to confirm the network is well-posed (PR 4).
  - QC jobs: a dry-run / argument-parse step against `xtb`/`crest` / engine drivers in PR 5 (no real SCF in CI).
- **Domain-level `Validator`** implementations (PR 3+) emitting `ValidationReport` items: severity = error/warning/info.

This layer **gates merges**.

### Layer 2 — LLM-as-judge (opt-in, eval-only by default)

Runs in the **eval harness** (PR 7) and on demand locally. Includes:

- NL ↔ IR semantic equivalence checks ("did the translator capture host/guest correctly?").
- Sanity checks on QC-job choices (engine + method + basis vs. the system).
- Plausibility scoring for free-form fields (`expected_geometry`, `non_covalent_hints`).

Surfaced via a feature flag (`SUPRAKIT_LLM_JUDGE=1` or equivalent); never required for `make check` to pass.

## Consequences

- **CI stays cheap, deterministic, and offline-friendly**, so contributors don't pay an LLM bill for normal work.
- **Eval is rich** — the LLM judge sees runs the deterministic layer can't reason about, and metrics from PR 7 give us a longitudinal signal across providers and models.
- The **`Validator` protocol is the same surface** for both layers: deterministic checks emit `error`/`warning`/`info`; the LLM judge emits the same shape with `severity=info` (or `warning` when configured), so downstream consumers don't branch.
- We accept that some semantic regressions will only show up in eval, not in CI — that's the price of keeping merges fast.

## Alternatives considered

- **Pure deterministic**: rejected — we already know it misses "wrong-but-parseable" semantic drift, especially for ambiguous NL inputs.
- **Pure LLM-as-judge in CI**: rejected — cost, latency, flakiness, and a hard dependency on third-party APIs from inside `make check`.
- **Always-on hybrid (deterministic + LLM in CI)**: rejected — runtime/cost amplifies on every PR for a benefit that's mostly eval-shaped. We can revisit if PR 7 metrics demand it.
- **Snapshot/golden-file testing only**: useful and partly used, but insufficient on its own — snapshots ossify outputs and reward over-fitting to the current renderer.
