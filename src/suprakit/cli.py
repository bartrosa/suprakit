# SPDX-License-Identifier: Apache-2.0
"""Typer CLI entry points for ``suprakit``."""

from __future__ import annotations

import csv
import io
import re
from importlib import resources

import numpy as np
import typer
from rdkit import Chem

from suprakit.anionfit.predict import ESPLogKaModel
from suprakit.anionfit.receptors import build_resorcin4arene
from suprakit.anionfit.substituents import EWG_SMILES

app = typer.Typer(help="suprakit command-line interface.", add_completion=False)
anionfit_app = typer.Typer(help="Anion-binding calibration workflows.")
app.add_typer(anionfit_app, name="anionfit")


def _looks_like_smiles(text: str) -> bool:
    lowered = text.strip()
    return (
        any(sym in lowered for sym in "=#[()]") or lowered.endswith("Br") or lowered.endswith("Cl")
    )


def _parse_subst_pattern(text: str) -> list[str]:
    chunks = [chunk.strip() for chunk in text.split("+") if chunk.strip()]
    codes: list[str] = []
    for chunk in chunks:
        match = re.fullmatch(r"(\d+)x([A-Za-z0-9]+)", chunk)
        if not match:
            raise typer.BadParameter(
                f"Cannot parse substitution fragment {chunk!r}. Expected forms like 4xNO2."
            )
        count = int(match.group(1))
        code = match.group(2)
        codes.extend([code] * count)
    if len(codes) != 4:
        raise typer.BadParameter(
            f"Expected exactly four substituents after parsing; got {len(codes)}."
        )
    return codes


def _esp_from_placeholder_table(code: str) -> float | None:
    csv_path = resources.files("suprakit.anionfit.data").joinpath("priyadarshini_2025.csv")
    raw = csv_path.read_text(encoding="utf-8")
    filtered = "\n".join(
        line for line in raw.splitlines() if line.strip() and not line.strip().startswith("#")
    )
    reader = csv.DictReader(io.StringIO(filtered))
    for row in reader:
        if row["substituent"].strip() == code:
            return float(row["esp_au"])
    return None


@anionfit_app.command("predict")
def anionfit_predict(
    query: str = typer.Argument(
        ..., help="Substituent pattern (e.g. 4xNO2) or a receptor SMILES string."
    ),
    esp_au: float | None = typer.Option(
        None,
        "--esp-au",
        help="Optional ESP value (atomic units). When omitted the CLI attempts tblite-backed ESP (currently deferred).",
    ),
    use_placeholder_table: bool = typer.Option(
        False,
        "--use-placeholder-table/--no-placeholder-table",
        help="Use bundled placeholder ESP values for supported symmetric 4x EWG codes (testing only).",
    ),
) -> None:
    """Predict log(Ka) from ESP using the bundled linear calibration model."""

    model = ESPLogKaModel.from_priyadarshini_2025()

    esp_value: float | None = esp_au

    if _looks_like_smiles(query):
        mol = Chem.MolFromSmiles(query)
        if mol is None:
            raise typer.BadParameter("Could not interpret query as valid SMILES.")
        if esp_value is None:
            typer.echo(
                "SMILES input requires `--esp-au` until `anionfit` ESP evaluation is implemented "
                "(see context/TODO-anionfit-esp-implementation.md).",
                err=True,
            )
            raise typer.Exit(code=2)
    else:
        codes = _parse_subst_pattern(query)
        for code in codes:
            if code not in EWG_SMILES:
                raise typer.BadParameter(f"Unknown substituent code {code!r}.")

        build_codes = codes
        _ = build_resorcin4arene(build_codes)

        if esp_value is None:
            if use_placeholder_table and len(set(codes)) == 1:
                esp_value = _esp_from_placeholder_table(codes[0])
                if esp_value is not None:
                    typer.echo(
                        "Using bundled **placeholder** ESP from `priyadarshini_2025.csv` "
                        "(not experimental data).",
                        err=True,
                    )
            if esp_value is None:
                typer.echo(
                    "ESP is not available yet (tblite ESP extraction deferred). "
                    "Provide `--esp-au`, or `--use-placeholder-table` with symmetric codes such as `4xNO2`, "
                    "or consult context/TODO-anionfit-esp-implementation.md.",
                    err=True,
                )
                raise typer.Exit(code=2)

    assert esp_value is not None  # for type checker
    prediction = float(model.predict(np.array([esp_value]))[0])
    typer.echo(f"ESP (a.u.) input: {esp_value:.6f}")
    typer.echo(f"log10 Ka (placeholder calibration): {prediction:.4f}")


__all__ = ["app"]
