# `anionfit`

`anionfit` hosts workflows for correlating computed electrostatic descriptors with experimental binding metrics, starting from:

- receptor construction helpers for resorcin[4]arene scaffolds (`anionfit.receptors`)
- substituent dictionaries / enumerators (`anionfit.substituents`)
- linear ESP→log(Ka) calibration (`anionfit.predict`)
- GFN2-xTB bowl-probe ESP evaluation (`anionfit.esp`)

## Design constraints (bootstrap)

- **CPU-only** for `anionfit` logic: no torch/JAX imports in `anionfit/`.
- Parallelism uses `suprakit.core.parallel.molecule_map` / `molecule_map_parallel` with safe OpenMP settings (`OMP_NUM_THREADS=1` inside workers).

## Method — GFN2-xTB ESP at probe point

### Discovery (audit trail)

The following summarizes what was verified for `tblite` in this repository (see also `context/tblite-api-discovery.txt`):

- **tblite version (local dev):** import may fail when the `xtb` extra is not installed; CI on Linux uses the published manylinux wheel.
- **Working import path:** `from tblite.ase import TBLite` (ASE calculator integration).
- **Constructor / single-point:** `Atoms(...); atoms.calc = TBLite(method="GFN2-xTB", charge=..., solvation=("alpb", "<solvent>"), ...)` then `atoms.get_potential_energy()` (eV) and `atoms.get_charges()` (Mulliken, in units of *e*).
- **Result keys:** ASE exposes energy, forces, Mulliken charges, dipole, etc.; positions are handled in Å externally and converted to Bohr inside `GFN2Backend` for ESP sums.
- **Solvation idiom:** `solvation=("alpb", solvent_name)` matches upstream ASE documentation for ALPB-style cavities.
- **Direct ESP-at-points:** **no** — documented `TBLite` properties do not include molecular ESP sampled on arbitrary 3D probe points.

### Point-charge approximation

Because arbitrary probe ESP is unavailable through the documented calculator API, `anionfit.esp` evaluates

\[
\phi(\mathbf{r}) = \sum_i \frac{q_i}{|\mathbf{r} - \mathbf{r}_i|}
\]

with Mulliken atomic charges \(\{q_i\}\) from GFN2-xTB (via ASE), \(\mathbf{r}_i\) and \(\mathbf{r}\) in **Bohr**, and \(\phi\) in atomic units. This matches **Scenario B** from the implementation plan: a Hunter–Pike-style screening potential. Linear ESP→binding calibrations absorb most additive offsets versus exact density-derived ESP.

### Probe geometry and `PROBE_OFFSET_BOHR`

- **Upper bowl centroid \(\mathbf{C}\):** mean coordinates of the four upper-rim aromatic carbons (`upper_rim_atom_indices`).
- **Lower reference \(\mathbf{L}\):** centroid of four lower-rim ipso aromatic carbons (`lower_rim_ipso_atom_indices`) for supported EWG fragments.
- **Axis:** \(\hat{\mathbf{n}} = (\mathbf{C} - \mathbf{L}) / \|\mathbf{C} - \mathbf{L}\|\) points from the lower rim toward the upper rim (out of the bowl for cone conformers).
- **Probe:** \(\mathbf{P} = \mathbf{C} + r_{\mathrm{probe}} \hat{\mathbf{n}}\).

The default `PROBE_OFFSET_BOHR` is `2.0 Å × 1.8897261246257702` (= 2.0 Å in Bohr). Changing `DEFAULT_PROBE_OFFSET_ANGSTROM`, the axis convention, or rim atom selection is a **breaking change** for refitted correlation models—bump the model training version and re-extract SI reference data when applicable.
