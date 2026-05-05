# ADR-0002: IR design — `SupraSpec` as a discriminated pydantic v2 root

- Status: accepted
- Date: 2026-05-05

## Context

The whole project hinges on a stable bridge between **natural language**, **chemical/biological DSLs** (SMILES, SBML), and **QC inputs**. We need an internal representation (IR) that:

1. Captures supramolecular concepts that **don't fit existing DSLs**: host/guest roles, complex stoichiometry, non-covalent hints, mixed-phase systems, QC engine + task + method tuples.
2. Provides a **single contract** between `Translator` (NL → IR), `Renderer` (IR → output), and `Validator` (IR → report). Future PRs add concrete implementations behind these contracts.
3. Yields a **machine-readable schema** so LLMs can be asked to emit IR directly (pydantic v2 `model_json_schema` / `TypeAdapter.json_schema()`).
4. Is **easy to extend** without reshaping callers — new fields default-additive, new variants land as new `kind` literals.

Reusing SMILES, SBML, or a free-form dict as the IR was tempting but rejected (see Alternatives).

## Decision

- The IR root is **`SupraSpec`**, a `pydantic.RootModel` over a **discriminated union** keyed on `kind`:
  - `MoleculeSpec` (`kind: "molecule"`) — a single chemical species with one or more identifiers.
  - `ComplexSpec` (`kind: "complex"`) — a multi-component supramolecular assembly with roles and non-covalent hints.
  - `ReactionSystemSpec` (`kind: "reaction_system"`) — a network of species and reactions with symbolic rate laws (SBML-shaped).
  - `QCJobSpec` (`kind: "qc_job"`) — a QC job with engine, task, method, and an embedded discriminated `target: MoleculeSpec | ComplexSpec`.
- All variants inherit from a common **`StrictModel`** with `extra="forbid"`, `str_strip_whitespace=True`, `validate_assignment=True`.
- Cross-cutting primitives (`Phase`, `ComponentRole`, `TaskKind`, `QCEngine`, `NonNegativeFloat`, `PositiveInt`) live in `suprakit.ir.base`.
- The full JSON Schema is exported via `get_json_schema()` (`TypeAdapter(SupraSpecVariant).json_schema()`); it includes `discriminator: { propertyName: "kind", mapping: {...} }` and a `oneOf` over the four variants — an LLM-friendly contract.
- **Serialization** is deterministic round-trip in **JSON and YAML** (PyYAML, `safe_load` / `safe_dump`). YAML round-trips are tested fixture-by-fixture.
- **Validation** has two layers:
  - **Pydantic-level (structural + simple semantic)** — required identifiers, unique IDs, reference integrity, charge consistency for explicitly set `total_charge`, `phase=solid` ⇒ `pbc` required. Soft signals (e.g. `cp2k` + non-solid, `xtb`/`crest` + `basis_set`) are emitted as Python warnings, not errors.
  - **Domain-level (`Validator` protocol)** — semantic checks beyond pydantic, returning a `ValidationReport` of `ValidationIssue` items by severity. PR 1 ships only the protocol; concrete validators arrive with each renderer PR.

## Consequences

- **Pros**: each renderer/translator gets a typed contract; rendering ignores irrelevant fields; LLM structured output uses one canonical schema; extending the IR is additive (new field default-set, or a new `kind` literal); JSON ⇄ YAML round-trip lets us share fixtures with humans and machines alike.
- **Cons / trade-offs**:
  - The IR is a **fifth concept** alongside NL/SMILES/SBML/QC input — contributors must learn it. Mitigated by the fixtures in `tests/data/ir/` and explicit ADR.
  - Discriminated unions tie the IR to pydantic v2 (cf. ADR-0001); a future migration would mean rewriting variants.
  - Soft warnings live in `pydantic` model validators; consumers must opt into Python's `warnings` filter to surface them. This keeps construction non-fatal but hides signal — the upcoming `Validator` layer will surface them as `ValidationIssue`s.

## Alternatives considered

- **Schema-less `dict` IR**: rejected — no validation, no JSON Schema, no IDE help, no clear contract.
- **DataClasses + hand-written JSON Schema**: rejected — duplicated work, drift between code and schema, no built-in discriminated union semantics.
- **SMILES / SBML as IR**: rejected — those are *output* targets. Suprachemistry adds host/guest roles, stoichiometric complexes, non-covalent hints, and QC-job framing that don't fit either format. Mapping back from SMILES/SBML to those concepts is lossy.
- **A custom textual mini-DSL**: rejected — reinventing a parser, IDE story, and schema export. pydantic + JSON Schema gets us all three for free.
- **Single flat model with optional everything**: rejected — pushes variant logic into runtime checks instead of the type system; LLM structured-output specs become uselessly permissive.
