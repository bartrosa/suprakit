"""Tests for `suprakit.ir.qcjob.QCJobSpec`."""

from __future__ import annotations

import warnings

import pytest
from pydantic import ValidationError as PydanticValidationError

from suprakit.ir import (
    ComplexComponent,
    ComplexSpec,
    ComponentRole,
    MoleculeSpec,
    PBCParameters,
    Phase,
    QCEngine,
    QCJobSpec,
    TaskKind,
)


def _ethanol_target() -> MoleculeSpec:
    return MoleculeSpec(name="ethanol", smiles="CCO")


def _crown_complex() -> ComplexSpec:
    return ComplexSpec(
        components=[
            ComplexComponent(
                molecule=MoleculeSpec(smiles="C1COCCOCCOCCOCCOCCO1"),
                role=ComponentRole.HOST,
            ),
            ComplexComponent(
                molecule=MoleculeSpec(smiles="[K+]", charge=1),
                role=ComponentRole.GUEST,
            ),
        ],
        total_charge=1,
    )


def test_qcjob_minimal_valid_molecule_target() -> None:
    job = QCJobSpec(
        target=_ethanol_target(),
        engine=QCEngine.XTB,
        task=TaskKind.SINGLE_POINT,
        method="GFN2-xTB",
    )
    assert job.kind == "qc_job"
    assert isinstance(job.target, MoleculeSpec)
    assert job.target.kind == "molecule"


def test_qcjob_minimal_valid_complex_target() -> None:
    job = QCJobSpec(
        target=_crown_complex(),
        engine=QCEngine.XTB,
        task=TaskKind.OPTIMIZATION,
        method="GFN2-xTB",
    )
    assert isinstance(job.target, ComplexSpec)
    assert job.target.kind == "complex"


def test_qcjob_solid_phase_without_pbc_raises() -> None:
    with pytest.raises(PydanticValidationError) as exc:
        QCJobSpec(
            target=_ethanol_target(),
            engine=QCEngine.CP2K,
            task=TaskKind.OPTIMIZATION,
            method="PBE",
            phase=Phase.SOLID,
        )
    assert "requires `pbc`" in str(exc.value)


def test_qcjob_solid_phase_with_pbc_ok() -> None:
    job = QCJobSpec(
        target=_ethanol_target(),
        engine=QCEngine.CP2K,
        task=TaskKind.OPTIMIZATION,
        method="PBE",
        phase=Phase.SOLID,
        pbc=PBCParameters(cell_a=10.0, cell_b=10.0, cell_c=10.0),
    )
    assert job.pbc is not None


def test_qcjob_xtb_with_basis_set_warns() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        QCJobSpec(
            target=_ethanol_target(),
            engine=QCEngine.XTB,
            task=TaskKind.SINGLE_POINT,
            method="GFN2-xTB",
            basis_set="def2-SVP",
        )
    assert any("basis sets" in str(w.message) for w in caught)


def test_qcjob_crest_with_basis_set_warns() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        QCJobSpec(
            target=_ethanol_target(),
            engine=QCEngine.CREST,
            task=TaskKind.CONFORMER_SEARCH,
            method="GFN2-xTB",
            basis_set="def2-TZVP",
        )
    assert any("basis sets" in str(w.message) for w in caught)


def test_qcjob_cp2k_non_solid_warns() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        QCJobSpec(
            target=_ethanol_target(),
            engine=QCEngine.CP2K,
            task=TaskKind.OPTIMIZATION,
            method="PBE",
            phase=Phase.GAS,
        )
    assert any("cp2k" in str(w.message).lower() for w in caught)


def test_qcjob_psi4_with_basis_does_not_warn() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        QCJobSpec(
            target=_ethanol_target(),
            engine=QCEngine.PSI4,
            task=TaskKind.SINGLE_POINT,
            method="B3LYP",
            basis_set="def2-SVP",
        )
    assert all("basis sets" not in str(w.message) for w in caught)


def test_qcjob_kind_literal_rejects_other() -> None:
    with pytest.raises(PydanticValidationError):
        QCJobSpec(  # type: ignore[arg-type]
            kind="bad",
            target=_ethanol_target(),
            engine=QCEngine.XTB,
            task=TaskKind.SINGLE_POINT,
            method="GFN2-xTB",
        )


def test_qcjob_extra_field_forbidden() -> None:
    with pytest.raises(PydanticValidationError):
        QCJobSpec(  # type: ignore[call-arg]
            target=_ethanol_target(),
            engine=QCEngine.XTB,
            task=TaskKind.SINGLE_POINT,
            method="GFN2-xTB",
            unknown_kw="x",
        )


def test_pbc_periodic_dimensions_bounded() -> None:
    with pytest.raises(PydanticValidationError):
        PBCParameters(cell_a=10.0, cell_b=10.0, cell_c=10.0, periodic_dimensions=4)
    with pytest.raises(PydanticValidationError):
        PBCParameters(cell_a=10.0, cell_b=10.0, cell_c=10.0, periodic_dimensions=0)


def test_qcjob_extra_keywords_accepts_scalars() -> None:
    job = QCJobSpec(
        target=_ethanol_target(),
        engine=QCEngine.XTB,
        task=TaskKind.SINGLE_POINT,
        method="GFN2-xTB",
        extra_keywords={"acc": 1.0, "max_iter": 250, "verbose": True, "label": "run-1"},
    )
    assert job.extra_keywords["max_iter"] == 250
