# Native acceleration (`native/`)

Python is the default implementation surface for **suprakit**. This directory reserves space for optional Rust/C/C++ extensions following the policy below.

## Profiling-first rule

Do **not** add a native submodule until profiling shows a Python bottleneck that cannot be fixed by:

- NumPy vectorization / batching
- better algorithms / data structures
- `joblib` parallelism (`suprakit.core.parallel.molecule_map`)

Document the evidence (profiles, timings) in the PR that introduces native code.

## Rust is the preferred native stack

When native code is justified, prefer **Rust** delivered as a Python extension via **maturin + pyo3**.

Typical layout:

```
native/<name>/
├── Cargo.toml
├── src/lib.rs
└── README.md
```

Integration options:

- publish as an independent Python package under `native/<name>/` and depend on it from `pyproject.toml`, **or**
- wire an extension module into this repo using maturin’s PEP 517 hooks (keep build reproducible under `uv`).

Add a Makefile target:

```make
native-<name>: ## build native/<name>
	cd native/<name> && uv run maturin develop  # example
```

## Mandatory Python fallback + benchmark

Every native submodule **must**:

1. Provide a Python implementation that is slow but correct.
2. Select native code with a lazy import pattern:

```python
try:
    from ._native import fast_fn  # Rust extension
except ImportError:
    from ._pyfallback import fast_fn
```

3. Ship a benchmark that demonstrates speedup versus the Python fallback (`pytest-benchmark` under `benchmarks/` once real workloads exist).

## C/C++ only when linking existing libraries

Use **pybind11** or **cffi** only when you must call into an existing C/C++ chemistry library without a Rust binding.
