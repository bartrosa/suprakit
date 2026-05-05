# Roadmap

High-level plan for evolving **suprakit**. Each milestone maps to a focused PR; definitions below describe what “done” means at a glance.

## PR 0 — Bootstrap

Repository skeleton: packaging with Hatchling, `uv` lockfile, Ruff + Mypy + Pytest + pre-commit, GitHub Actions on Python 3.11 and 3.12, documentation stubs (ADR template, roadmap), and smoke tests — **while keeping** the existing computational supramolecular stack (anionfit, core, CLI, notebooks, MkDocs) so the NL→DSL roadmap and today’s toolkit evolve in the **same** repo.

## PR 1 — SupraSpec IR + protocols + ADRs

Introduce the internal representation (**SupraSpec**), stable protocols (e.g. boundaries for translators/renderers/validators without concrete chemistry), and the first real ADRs documenting those choices.

## PR 2 — Multi-provider LLM

Abstraction for language-model backends (configuration, retries, tracing hooks) so later PRs can swap providers without touching DSL code.

## PR 3 — NL → SMILES

Natural language → structural chemistry DSL path focused on SMILES (and related textual chemistry outputs), with tests around parsing and round-trip expectations where feasible.

## PR 4 — NL → SBML

Natural language → systems biology markup path (SBML-oriented), including validation hooks aligned with the IR from PR 1.

## PR 5 — QC pipeline (xtb + crest)

Orchestration toward quantum-chemistry inputs using **xtb** and **crest** (and related tooling) as execution backends, behind clear interfaces.

## PR 6 — CLI

User-facing command-line entrypoints for the toolkit (install story, subcommands, `--help`, sensible defaults).

## PR 7 — Evaluation harness

Repeatable benchmarks and evaluation scripts for NL→DSL and pipeline quality (metrics, fixtures, regression guards).
