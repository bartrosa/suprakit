# Performance notes

suprakit targets three environments:

1. **CPU-only** (Linux/Windows x86_64) — CI baseline.
2. **Apple Silicon** (arm64 macOS) — primary development; PyTorch via MPS where applicable.
3. **CUDA** (Linux + NVIDIA, `sm_75+`) — batched ML inference and optional JAX paths.

The first `anionfit` release is **correctness-first**. Avoid premature GPU-specific code paths in modules that do not require torch/JAX.

## Optimization matrix (living document)

| Workload | Bottleneck | CPU strategy | Apple M3+ strategy | CUDA strategy | Decision rule |
| --- | --- | --- | --- | --- | --- |
| GFN2-xTB single point / opt on one molecule | tblite (Fortran, OpenMP) | Set `OMP_NUM_THREADS` to available cores | Accelerate-backed BLAS where applicable | Same as CPU (no GPU xTB) | Do not attempt to GPU-accelerate xTB |
| xTB over hundreds of molecules | Embarrassingly parallel | `joblib.Parallel(..., backend="loky")`; set `OMP_NUM_THREADS=1` in workers | Same | Same | Parallelize at molecule granularity |
| RDKit 3D embedding over a SMILES library | RDKit C++ + Python overhead | joblib over batches | Same | Same | Identical across backends |
| MACE / AIMNet MLIP inference | PyTorch forward pass | CPU torch | Prefer MPS with float32 guards | CUDA for large batches | Route through `detect_device().torch_device` |
| Batched dense linear algebra | NumPy / SciPy | MKL / OpenBLAS / Accelerate | Accelerate | cuBLAS / optional JAX | JAX only if profiling proves benefit |
| PySCF DFT / TD-DFT | Dense linear algebra | CPU BLAS defaults | Accelerate | Optional GPU extensions | CPU default |
| Conformer ensemble loops | Python loops | Vectorize with NumPy | NumPy | NumPy / optional JAX | Vectorize first |
| Pure-Python inner loops shown hot by profiling | Interpreter overhead | numba / Cython first | Same | Same | Rust (`native/`) only after profiling + Python fallback + benchmark |

### tblite / OpenMP hygiene

Parallelize **molecules** with joblib. Inside each worker, force **single-threaded** OpenMP (`OMP_NUM_THREADS=1`) to avoid nested oversubscription. `suprakit.core.parallel.molecule_map` implements this pattern.
