# SPDX-License-Identifier: Apache-2.0
"""Resorcin[4]arene receptor builders for supramolecular screening workflows."""

from __future__ import annotations

from rdkit import Chem
from rdkit.Chem import AllChem

from suprakit.anionfit.substituents import fragment_mol

# Parent calix[4]resorcinarene scaffold (PubChem CID 10929046 connectivity).
_PARENT_CALIX_RESORCINARENE_SMILES = (
    "C1C2=CC(=C(C=C2O)O)CC3=CC(=C(C=C3O)O)CC4=C(C=C(C(=C4)CC5=C(C=C(C1=C5)O)O)O)O"
)

# Upper-rim aromatic CH situated between two oxygen substituents on each resorcinol ring (1,3 arrangement).
UPPER_RIM_PRIMARY_SMARTS = "[c;H1]([c]O)[c]O"

# Lower-rim attachment points across supported EWG fragments (ipso aromatic carbon).
# Each entry is ``(SMARTS, ipso_atom_index)`` where ``ipso_atom_index`` selects the ipso carbon
# within ``Mol.GetSubstructMatches(...)`` tuples.
LOWER_RIM_IPSO_DEFINITIONS: tuple[tuple[str, int], ...] = (
    ("[c][N+](=O)[O-]", 0),
    ("[c][N+]([O-])=O", 0),
    ("[c]C#N", 0),
    ("[c]C=O", 0),
    ("[c]C(F)(F)F", 0),
    ("[c]S(=O)(=O)", 0),
    ("[c]C(=O)C", 0),
    ("[c]C(=O)N", 0),
    ("[c][Br]", 0),
    ("[c][Cl]", 0),
    # Pentafluorophenyl: bowl-attached aromatic ipso is the second atom (after the bridge bond).
    ("[c]-[c]1[c](F)[c](F)[c](F)[c](F)[c]1F", 1),
)


def upper_rim_atom_indices(mol: Chem.Mol) -> tuple[int, int, int, int]:
    """Return the four upper-rim aromatic carbon indices (deterministic ordering).

    The primary SMARTS encodes the resorcinol CH between two oxygen substituents. When lower-rim
    substitution removes competing CH sites, exactly four aromatic CH sites remain for symmetric
    tetra-substituted receptors and are selected via an explicit fallback.
    """

    primary = Chem.MolFromSmarts(UPPER_RIM_PRIMARY_SMARTS)
    matches = mol.GetSubstructMatches(primary)
    if len(matches) == 4:
        return tuple(sorted(int(m[0]) for m in matches))

    ch_pattern = Chem.MolFromSmarts("[cH1]")
    aromatic_ch = sorted([int(m[0]) for m in mol.GetSubstructMatches(ch_pattern)])
    if len(aromatic_ch) == 4:
        return tuple(aromatic_ch)

    smiles = Chem.MolToSmiles(mol)
    raise ValueError(
        "Could not identify exactly four upper-rim aromatic CH atoms for this receptor topology. "
        f"matches(primary)={len(matches)} aromatic_CH={len(aromatic_ch)} SMILES={smiles}"
    )


def lower_rim_ipso_atom_indices(mol: Chem.Mol) -> tuple[int, int, int, int]:
    """Return four lower-rim ipso aromatic carbons for supported substituent patterns."""

    ipsos: set[int] = set()
    for smarts, ipso_idx in LOWER_RIM_IPSO_DEFINITIONS:
        q = Chem.MolFromSmarts(smarts)
        if q is None:
            raise RuntimeError(f"Internal SMARTS failed to parse: {smarts!r}")
        for hit in mol.GetSubstructMatches(q):
            ipsos.add(int(hit[ipso_idx]))

    ordered = tuple(sorted(ipsos))
    if len(ordered) != 4:
        smiles = Chem.MolToSmiles(mol)
        raise ValueError(
            "Could not identify exactly four lower-rim ipso atoms for this receptor topology. "
            f"found={len(ordered)} SMILES={smiles}"
        )

    return ordered


def _embed_with_seed(mol: Chem.Mol, *, random_seed: int) -> Chem.Mol:
    mh = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = random_seed
    status = AllChem.EmbedMolecule(mh, params)
    if status != 0:
        raise RuntimeError("ETKDG embedding failed for resorcin[4]arene scaffold.")
    AllChem.MMFFOptimizeMolecule(mh)
    return mh


def _lower_rim_attachment_indices(mol_with_h: Chem.Mol, *, random_seed: int = 42) -> list[int]:
    """Pick four chemically equivalent aromatic carbons on one rim using a deterministic 3D heuristic."""

    mh = _embed_with_seed(mol_with_h, random_seed=random_seed)
    conf = mh.GetConformer()
    pattern = Chem.MolFromSmarts("[cH1]")
    matches = [m[0] for m in mh.GetSubstructMatches(pattern)]
    if len(matches) != 8:
        raise RuntimeError("Unexpected aromatic CH pattern for parent scaffold.")

    zs = [(idx, conf.GetAtomPosition(idx).z) for idx in matches]
    zs.sort(key=lambda t: t[1])
    # Preserve ascending-z order: user-provided substituents index from most negative z upward.
    return [idx for idx, _ in zs[:4]]


def _remove_single_hydrogen(rw: Chem.RWMol, carbon_idx: int) -> None:
    hatoms = [
        n.GetIdx()
        for n in rw.GetAtomWithIdx(carbon_idx).GetNeighbors()
        if n.GetSymbol() == "H" and n.GetTotalDegree() == 1
    ]
    if not hatoms:
        raise RuntimeError(f"No removable hydrogen found on atom {carbon_idx}.")
    rw.RemoveAtom(hatoms[0])


def _attach_dummy_fragment(mol: Chem.Mol, carbon_idx: int, frag: Chem.Mol) -> Chem.Mol:
    """Attach ``frag`` (must contain one dummy atom ``*``) at ``carbon_idx``."""

    rw = Chem.RWMol(mol)
    _remove_single_hydrogen(rw, carbon_idx)
    base = rw.GetMol()

    dummy_local = None
    for atom in frag.GetAtoms():
        if atom.GetAtomicNum() == 0:
            dummy_local = atom.GetIdx()
            break
    if dummy_local is None:
        raise ValueError("Fragment must contain a dummy attachment atom `[*]`.")

    combined = Chem.CombineMols(base, frag)
    rw_comb = Chem.RWMol(combined)

    offset = base.GetNumAtoms()
    dummy_global = offset + dummy_local

    dummy_atom = rw_comb.GetAtomWithIdx(dummy_global)
    if dummy_atom.GetAtomicNum() != 0:
        raise RuntimeError("Failed to locate combined dummy atom.")

    nbrs = [n.GetIdx() for n in dummy_atom.GetNeighbors()]
    if len(nbrs) != 1:
        raise RuntimeError(
            "Dummy atom must have exactly one heavy-atom neighbor (the substituent)."
        )
    heavy_nbr = nbrs[0]

    rw_comb.RemoveAtom(dummy_global)

    # Index adjustment after deletion
    heavy_after = heavy_nbr if heavy_nbr < dummy_global else heavy_nbr - 1
    carbon_after = carbon_idx if carbon_idx < dummy_global else carbon_idx - 1

    rw_comb.AddBond(carbon_after, heavy_after, Chem.BondType.SINGLE)

    out = rw_comb.GetMol()
    Chem.SanitizeMol(out)
    return out


def _methylate_upper_rim(mol: Chem.Mol) -> Chem.Mol:
    """Convert phenolic OH groups to methoxy groups (upper-rim methylation surrogate)."""

    rxn = AllChem.ReactionFromSmarts("[c:1][OH]>>[c:1][O][CH3]")
    products = mol
    for _ in range(16):
        if not products.GetSubstructMatches(Chem.MolFromSmarts("[c][OH]")):
            break
        outcomes = rxn.RunReactants((products,))
        if not outcomes:
            break
        products = outcomes[0][0]
        Chem.SanitizeMol(products)
    return products


def build_resorcin4arene(
    lower_rim_substituents: list[str],
    *,
    upper_rim: str = "methyl",
) -> Chem.Mol:
    """Build a cone-oriented resorcin[4]arene receptor with four lower-rim substituents.

    Args:
        lower_rim_substituents: Four substituent codes understood by ``substituents.EWG_SMILES``.
        upper_rim: ``"methyl"`` applies a methoxy surrogate to phenolic OH groups; ``"hydroxyl"`` keeps OH.

    Notes:
        The lower rim is selected using a deterministic geometric heuristic (minimum ``z`` aromatic CH sites
        after ETKDG embedding, seed ``42``). This is adequate for cheminformatics bootstrap work but should be
        revisited when comparing to experimentally characterized conformers.
    """

    if len(lower_rim_substituents) != 4:
        raise ValueError("Exactly four lower-rim substituents are required.")

    mol = Chem.MolFromSmiles(_PARENT_CALIX_RESORCINARENE_SMILES)
    if mol is None:
        raise RuntimeError("Internal scaffold SMILES failed to parse.")

    scaffold = Chem.AddHs(mol)
    attach_idx = _lower_rim_attachment_indices(scaffold)

    current = scaffold
    # Attach from highest toward lowest carbon index so intermediate RDKit renumbering stays stable.
    pairs = sorted(
        zip(attach_idx, lower_rim_substituents, strict=True),
        key=lambda item: item[0],
        reverse=True,
    )
    for carbon_idx, code in pairs:
        frag = fragment_mol(code)
        current = _attach_dummy_fragment(current, carbon_idx, frag)

    current = Chem.RemoveHs(current)

    if upper_rim.strip().lower() == "methyl":
        current = _methylate_upper_rim(current)
    elif upper_rim.strip().lower() not in {"hydroxyl", "hydroxy", "oh"}:
        raise ValueError("upper_rim must be one of: methyl | hydroxyl")

    return current


__all__ = [
    "LOWER_RIM_IPSO_DEFINITIONS",
    "UPPER_RIM_PRIMARY_SMARTS",
    "build_resorcin4arene",
    "lower_rim_ipso_atom_indices",
    "upper_rim_atom_indices",
]
