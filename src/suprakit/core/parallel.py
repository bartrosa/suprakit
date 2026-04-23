# SPDX-License-Identifier: Apache-2.0
"""Embarrassingly parallel helpers for molecule-scale workloads."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import TypeVar

from joblib import Parallel, delayed  # type: ignore[import-untyped]

T = TypeVar("T")
R = TypeVar("R")


def _run_with_single_thread_openmp(fn: Callable[[T], R], item: T) -> R:
    """Run ``fn(item)`` with ``OMP_NUM_THREADS`` temporarily forced to ``1``.

    Nested OpenMP/thread pools (e.g. tblite/OpenMP inside xTB) inside joblib workers
    should stay single-threaded to avoid oversubscription.
    """

    old = os.environ.get("OMP_NUM_THREADS")
    os.environ["OMP_NUM_THREADS"] = "1"
    try:
        return fn(item)
    finally:
        if old is None:
            os.environ.pop("OMP_NUM_THREADS", None)
        else:
            os.environ["OMP_NUM_THREADS"] = old


def molecule_map(
    fn: Callable[[T], R],
    items: Iterable[T],
    *,
    n_jobs: int = -1,
    batch_size: int | None = None,
    backend: str = "loky",
    prefer: str | None = None,
) -> Iterator[R]:
    """Parallel ``map`` over molecules/items using joblib.

    Parameters mirror common ``joblib.Parallel`` usage; ``prefer`` maps to ``prefer="threads"``
    style hints when needed for debugging.
    """

    _ = prefer  # reserved for future threading tweaks
    seq = list(items)
    if not seq:
        return iter(())

    worker = delayed(_run_with_single_thread_openmp)(fn)

    parallel = Parallel(n_jobs=n_jobs, backend=backend, batch_size=batch_size)
    results: Sequence[R] = parallel(worker(item) for item in seq)
    return iter(results)


def molecule_map_parallel(
    fn: Callable[[T], R],
    items: Iterable[T],
    *,
    n_jobs: int = -1,
    batch_size: int | None = None,
    backend: str = "loky",
) -> list[R]:
    """Strict materializing variant returning a list."""

    return list(molecule_map(fn, items, n_jobs=n_jobs, batch_size=batch_size, backend=backend))
