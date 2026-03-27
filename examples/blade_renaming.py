import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "gamo")
    for p in [_root, _gamo]:
        if p not in sys.path:
            sys.path.insert(0, p)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from ga import Algebra, reverse, dual, grade, exp, norm, squared
    import galaga_marimo as gm
    import numpy as np

    return Algebra, dual, exp, gm, grade, norm, np, reverse, squared


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    # Basis Blade Renaming

    Every algebra has a `BasisBlade` object for each blade in the algebra.
    You can rename them, and the change takes effect immediately in all
    rendering — including existing multivectors.
    """)
    return


# ============================================================
# Default names
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Default Names")
    return


@app.cell
def _(Algebra, gm):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors()

    gm.md(t"""
    Default Cl(3,0) basis blades:

    | Blade | Unicode | LaTeX |
    |-------|---------|-------|
    | e₁ | {e1} | ${e1.latex()}$ |
    | e₂ | {e2} | ${e2.latex()}$ |
    | e₃ | {e3} | ${e3.latex()}$ |
    | e₁₂ | {e1 ^ e2} | ${(e1 ^ e2).latex()}$ |
    | e₁₃ | {e1 ^ e3} | ${(e1 ^ e3).latex()}$ |
    | e₂₃ | {e2 ^ e3} | ${(e2 ^ e3).latex()}$ |
    | e₁₂₃ | {e1 ^ e2 ^ e3} | ${(e1 ^ e2 ^ e3).latex()}$ |
    """)
    return alg, e1, e2, e3


# ============================================================
# Rename the pseudoscalar
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Rename the Pseudoscalar to I")
    return


@app.cell
def _(alg, e1, e2, e3, gm):
    alg.get_basis_blade(alg.pseudoscalar()).rename(
        unicode="𝑰", ascii="I", latex="I"
    )

    gm.md(t"""
    After renaming:

    - Pseudoscalar: {alg.pseudoscalar()} (was e₁₂₃)
    - LaTeX: ${alg.pseudoscalar().latex()}$
    - Existing `e1 ^ e2 ^ e3` also updates: {e1 ^ e2 ^ e3}
    """)
    return


# ============================================================
# Rename bivectors for angular momentum
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Angular Momentum Bivectors")
    return


@app.cell
def _(Algebra, gm, squared):
    am = Algebra((1, 1, 1))

    # Name the bivectors as angular momentum components
    am.get_basis_blade(0b110).rename(unicode="L₁", ascii="L1", latex="L_1")  # e₂₃
    am.get_basis_blade(0b101).rename(unicode="L₂", ascii="L2", latex="L_2")  # e₁₃
    am.get_basis_blade(0b011).rename(unicode="L₃", ascii="L3", latex="L_3")  # e₁₂

    e1, e2, e3 = am.basis_vectors(lazy=True)
    _L1 = (e2 ^ e3).name("L₁", latex="L_1")
    _L2 = (e1 ^ e3).name("L₂", latex="L_2")
    _L3 = (e1 ^ e2).name("L₃", latex="L_3")

    gm.md(t"""
    Bivectors renamed to angular momentum:

    | Blade | Name | LaTeX |
    |-------|------|-------|
    | e₂∧e₃ | {_L1} | ${_L1.latex()}$ |
    | e₁∧e₃ | {_L2} | ${_L2.latex()}$ |
    | e₁∧e₂ | {_L3} | ${_L3.latex()}$ |

    Casimir: {squared(_L1)} + {squared(_L2)} + {squared(_L3)} = {(squared(_L1).eval() + squared(_L2).eval() + squared(_L3).eval())}
    """)
    return


# ============================================================
# Spacetime Algebra with custom blade names
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Spacetime Algebra — Custom Bivector Names")
    return


@app.cell
def _(Algebra, gm):
    sta = Algebra((1, -1, -1, -1), names="gamma")

    # Name the pseudoscalar
    sta.get_basis_blade(sta.pseudoscalar()).rename(
        unicode="𝑰", ascii="I", latex="I"
    )

    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)

    # Name the spatial bivectors as sigma
    sta.get_basis_blade(0b0011).rename(unicode="σ₁", ascii="s1", latex=r"\sigma_1")  # γ₀γ₁
    sta.get_basis_blade(0b0101).rename(unicode="σ₂", ascii="s2", latex=r"\sigma_2")  # γ₀γ₂
    sta.get_basis_blade(0b1001).rename(unicode="σ₃", ascii="s3", latex=r"\sigma_3")  # γ₀γ₃

    gm.md(t"""
    Spatial bivectors renamed to relative vectors (σ):

    | Product | Name | LaTeX |
    |---------|------|-------|
    | γ₀γ₁ | {g0 * g1} | ${(g0 * g1).eval().latex()}$ |
    | γ₀γ₂ | {g0 * g2} | ${(g0 * g2).eval().latex()}$ |
    | γ₀γ₃ | {g0 * g3} | ${(g0 * g3).eval().latex()}$ |

    Pseudoscalar: {sta.pseudoscalar()}

    These are the Pauli algebra embedded in STA!
    """)
    return


# ============================================================
# PGA with geometric names
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Projective GA — Geometric Names")
    return


@app.cell
def _(Algebra, gm):
    pga = Algebra((1, 1, 1, 0))

    # Name the null basis vector
    pga.get_basis_blade(0b1000).rename(unicode="e₀", ascii="e0", latex="e_0")

    # Name the pseudoscalar
    pga.get_basis_blade(pga.pseudoscalar()).rename(
        unicode="𝑰", ascii="I", latex="I"
    )

    pe1, pe2, pe3, pe0 = pga.basis_vectors()

    gm.md(t"""
    PGA Cl(3,0,1) with renamed null vector:

    | Blade | Name |
    |-------|------|
    | basis 4 | {pe0} (null direction) |
    | e₁∧e₀ | {pe1 ^ pe0} |
    | pseudoscalar | {pga.pseudoscalar()} |
    """)
    return


# ============================================================
# Dynamic renaming
# ============================================================


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Dynamic Renaming

    Renaming is live — it affects existing multivectors immediately.
    No need to re-fetch basis vectors.
    """)
    return


@app.cell
def _(Algebra, gm):
    _alg = Algebra((1, 1))
    _e1, _e2 = _alg.basis_vectors()

    _before = str(_e1 ^ _e2)
    _alg.get_basis_blade(0b11).rename(unicode="ω", latex=r"\omega")
    _after = str(_e1 ^ _e2)

    gm.md(t"""
    Cl(2,0) bivector:

    - Before rename: {_before}
    - After rename to ω: {_after}
    - Same MV object, different rendering!
    """)
    return


if __name__ == "__main__":
    app.run()
