# TODO: Implement `anionfit.esp` (GFN2-xTB + ESP at bowl probe)

## (a) What was supposed to be done

Implement `compute_esp_at_bowl_center` and `compute_esp_batch` in `src/suprakit/anionfit/esp.py` using:

1. RDKit 3D embedding (`ETKDG`).
2. `tblite` GFN2-xTB with an ALPB-style implicit solvation optimization (solvent configurable, default THF-like behavior as used in the notebook narrative).
3. Define the macrocyclic “bowl” centroid from the four upper-rim aromatic carbon atoms (`suprakit.core.geom` helpers / explicit atom selection from the receptor topology).
4. Choose an **in-bowl probe point** along the approximate bowl axis (document the geometric assumption explicitly in the module docstring).
5. Evaluate the molecular electrostatic potential (ESP) at that probe point in **atomic units** via `tblite`.
6. Provide batch execution through `suprakit.core.parallel.molecule_map`, with `OMP_NUM_THREADS=1` inside workers (see `suprakit.core.parallel`).

## (b) What was actually done so far

- `src/suprakit/anionfit/esp.py` contains a deliberate stub raising `NotImplementedError` pointing to this file.
- Bowl/centroid helpers exist in `src/suprakit/core/geom.py`.
- `src/suprakit/anionfit/receptors.py` + `substituents.py` + `predict.py` are implemented for the ESP→log(Ka) linear workflow using **placeholder training data**.
- Tests `tests/test_anionfit_esp.py` assert the stub behavior until this TODO is removed.

## (c) What remains

1. Confirm the supported `tblite` Python API for:
   - exporting an ESP **on a grid** or **at arbitrary points** after a ground-state calculation
   - solvent models available through Python bindings (ALPB naming differs across releases)
2. Implement optimization + ESP evaluation with **only verified API calls** (no guessed method names).
3. Remove the `NotImplementedError` paths, update/extend tests to validate numerical behavior on a tiny fixed system (marked `skipif` when `tblite` is absent).
4. Delete this file + remove the entry from `context/README.md`.

## (d) Decisions / assumptions

- “Bowl centroid” here means the centroid of four selected upper-rim aromatic carbon atoms from the receptor graph. The probe point offset along the bowl axis must be documented and kept stable across versions once chosen.
- The first bootstrap release prioritizes **correctness + installability**: `tblite` is shipped under the **`xtb` optional extra** because macOS arm64 wheels are not published on PyPI for all versions; Linux CI installs the manylinux wheel.

## (e) Upstream pointers

- tblite Python package and examples: https://github.com/tblite/tblite
- xTB/ALPB conceptual documentation: Grimme lab materials and the `tblite` paper/README.
- Related in-repo docs: `docs/modules/anionfit.md`, `docs/performance.md` (xtb row: do not attempt GPU acceleration).
