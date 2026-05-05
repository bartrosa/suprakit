# Architecture Decision Records (ADR)

This directory holds **Architecture Decision Records** in the spirit of [Michael Nygard's ADR format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions): short, durable notes that capture context, the decision, consequences, and alternatives.

## Naming convention

Files are numbered and kebab-cased:

`NNNN-kebab-case-title.md`

## Index

- [ADR-0001 — Tech stack: Python 3.11+, uv, pydantic v2, Hatchling](0001-tech-stack.md)
- [ADR-0002 — IR design: `SupraSpec` as a discriminated pydantic v2 root](0002-ir-design.md)
- [ADR-0003 — Mixed-oracle validation: deterministic by default, LLM-as-judge in eval](0003-mixed-oracle.md)

When proposing a new ADR, copy [`0000-template.md`](0000-template.md) as `NNNN-kebab-title.md` and add it to the list above.
