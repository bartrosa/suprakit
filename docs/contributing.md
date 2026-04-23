# Contributing

## Tooling

- `make` is the documented entry point (`make test`, `make lint`, `make typecheck`, `make docs`).
- Formatting and linting use **Ruff** (`make fmt`, `make lint`).
- Strict typing applies to `src/suprakit/core/` (`make typecheck`).

Install Git hooks once:

```bash
make hooks
```

The commit-msg hook requires `--hook-type commit-msg` (handled by `make hooks`).

## Commits (Conventional Commits)

This repository uses Conventional Commits via **commitizen** (see `.pre-commit-config.yaml`).

Examples:

- `feat(anionfit): add EWG substituent enumerator`
- `fix(core): handle empty conformer list in geom.centroid`
- `docs: clarify uv installation instructions`
- `refactor(anionfit): extract ESP probe-point logic`
- `test(anionfit): add property-based tests for substituent enumeration`
- `perf(core): vectorize centroid over conformer batch`
- `chore: bump ruff to 0.8.1`

Common types:

`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

## Native extensions policy

Python is the default implementation surface.

Do **not** introduce Rust/C/C++ extensions unless profiling proves a bottleneck that cannot be solved with vectorization, better algorithms, or `joblib`.

When native code *is* justified:

- Prefer **Rust + maturin + pyo3** under `native/<name>/`.
- Provide a **Python fallback** implementation that is slower but correct.
- Add a **benchmark** proving speedup vs fallback.

See `native/README.md` for directory conventions.
