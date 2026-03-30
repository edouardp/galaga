import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_marimo")
    for p in [_root, _gamo]:
        if p not in sys.path:
            sys.path.insert(0, p)
    return


@app.cell
def _():
    import marimo as mo

    return


@app.cell
def _():
    import numpy as np
    from galaga import (
        Algebra, gp, op, grade, reverse, involute, conjugate,
        dual, undual, norm, unit, inverse, exp, log,
        sandwich, squared,
        left_contraction, right_contraction,
        hestenes_inner, doran_lasenby_inner, scalar_product,
        commutator, anticommutator, lie_bracket, jordan_product,
        even_grades, odd_grades,
    )
    from galaga.symbolic import simplify
    import galaga_marimo as gm

    return (
        Algebra,
        anticommutator,
        commutator,
        conjugate,
        dual,
        even_grades,
        exp,
        gm,
        grade,
        hestenes_inner,
        inverse,
        involute,
        jordan_product,
        left_contraction,
        lie_bracket,
        norm,
        np,
        reverse,
        right_contraction,
        scalar_product,
        simplify,
        squared,
        unit,
    )


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return alg, e1, e2, e3


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"# Symbolic Rendering Gallery")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Named Objects")
    return


@app.cell
def _(e1):
    _v = e1.name("v")
    _v
    return


@app.cell
def _(e1, e2):
    _B = (e1 ^ e2).name("B")
    _B
    return


@app.cell
def _(alg, np):
    _theta = alg.scalar(np.pi / 4).name("θ", latex=r"\theta")
    _theta
    return


@app.cell
def _(alg):
    _m = alg.scalar(9.109e-31).name("mₑ", latex=r"m_e")
    _m
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Products")
    return


@app.cell
def _(e1, e2):
    _v = e1 * e2
    _v
    return


@app.cell
def _(e1, e2):
    _v = e1 ^ e2
    _v
    return


@app.cell
def _(e1, e2, e3):
    _v = e1 ^ e2 ^ e3
    _v
    return


@app.cell
def _(e1, e2):
    _v = e1 * e2 * e1
    _v
    return


@app.cell
def _(e1, e2):
    _a = e1.name("a")
    _b = e2.name("b")
    _v = _a * _b
    _v
    return


@app.cell
def _(e1, e2):
    _a = e1.name("a")
    _b = e2.name("b")
    _v = _a ^ _b
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Scalar Multiplication & Division")
    return


@app.cell
def _(e1):
    _v = 3 * e1
    _v
    return


@app.cell
def _(e1, e2):
    _v = 2 * (e1 + e2)
    _v
    return


@app.cell
def _(e1):
    _v = e1.name("v")
    _r = _v / 2
    _r
    return


@app.cell
def _(e1, e2):
    _v = (e1 + e2).name("v")
    _r = _v / 3
    _r
    return


@app.cell
def _(alg, e1, e2, np):
    _B = (e1 ^ e2).name("B")
    _theta = alg.scalar(np.pi / 3).name("θ", latex=r"\theta")
    _v = -_B * _theta / 2
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Addition & Subtraction")
    return


@app.cell
def _(e1, e2):
    _v = e1 + e2
    _v
    return


@app.cell
def _(e1, e2):
    _v = e1 - e2
    _v
    return


@app.cell
def _(e1, e2, e3):
    _v = e1 + 2 * e2 + 3 * e3
    _v
    return


@app.cell
def _(e1, e2, e3):
    _v = (e1 ^ e2) + 2 * (e2 ^ e3)
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Unary Operations")
    return


@app.cell
def _(e1, e2, reverse):
    _R = (e1 * e2).name("R")
    _v = reverse(_R)
    _v
    return


@app.cell
def _(e1, involute):
    _v = e1.name("v")
    _r = involute(_v)
    _r
    return


@app.cell
def _(conjugate, e1, e2):
    _R = (e1 * e2).name("R")
    _v = conjugate(_R)
    _v
    return


@app.cell
def _(dual, e1):
    _v = e1.name("v")
    _r = dual(_v)
    _r
    return


@app.cell
def _(e1, inverse):
    _v = e1.name("v")
    _r = inverse(_v)
    _r
    return


@app.cell
def _(e1, e2, squared):
    _R = (e1 * e2).name("R")
    _v = squared(_R)
    _v
    return


@app.cell
def _(e1, unit):
    _v = e1.name("v")
    _r = unit(_v)
    _r
    return


@app.cell
def _(e1, norm):
    _v = e1.name("v")
    _r = norm(_v)
    _r
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Unary on Compound Expressions")
    return


@app.cell
def _(e1, e2, reverse):
    _v = reverse(e1 + e2)
    _v
    return


@app.cell
def _(e1, e2, inverse):
    _v = inverse(e1 * e2)
    _v
    return


@app.cell
def _(dual, e1, e2):
    _v = dual(e1 + e2)
    _v
    return


@app.cell
def _(e1, e2, squared):
    _v = squared(e1 + e2)
    _v
    return


@app.cell
def _(e1, e2):
    _v = -(e1 + e2)
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Grade Projection")
    return


@app.cell
def _(e1, e2, grade):
    _R = (e1 * e2).name("R")
    _v = e1.name("v")
    _r = grade(_R * _v * ~_R, 1)
    _r
    return


@app.cell
def _(e1, e2, e3, even_grades):
    _mv = e1 + (e1 ^ e2) + (e1 ^ e2 ^ e3)
    _v = even_grades(_mv)
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Inner Products & Contractions")
    return


@app.cell
def _(e1, e2, left_contraction):
    _a = e1.name("a")
    _B = (e1 ^ e2).name("B")
    _v = left_contraction(_a, _B)
    _v
    return


@app.cell
def _(e1, e2, right_contraction):
    _B = (e1 ^ e2).name("B")
    _a = e1.name("a")
    _v = right_contraction(_B, _a)
    _v
    return


@app.cell
def _(e1, e2, hestenes_inner):
    _a = e1.name("a")
    _b = e2.name("b")
    _v = hestenes_inner(_a, _b)
    _v
    return


@app.cell
def _(e1, e2, scalar_product):
    _a = e1.name("a")
    _b = e2.name("b")
    _v = scalar_product(_a, _b)
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Commutator Family")
    return


@app.cell
def _(commutator, e1, e2):
    _A = (e1 ^ e2).name("A")
    _B = (e2 ^ e1).name("B")
    _v = commutator(_A, _B)
    _v
    return


@app.cell
def _(anticommutator, e1, e2):
    _A = (e1 ^ e2).name("A")
    _B = (e2 ^ e1).name("B")
    _v = anticommutator(_A, _B)
    _v
    return


@app.cell
def _(e1, e2, lie_bracket):
    _A = (e1 ^ e2).name("A")
    _B = (e2 ^ e1).name("B")
    _v = lie_bracket(_A, _B)
    _v
    return


@app.cell
def _(e1, e2, jordan_product):
    _a = e1.name("a")
    _b = e2.name("b")
    _v = jordan_product(_a, _b)
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Exponential")
    return


@app.cell
def _(e1, e2, exp):
    _B = (e1 ^ e2).name("B")
    _v = exp(_B)
    _v
    return


@app.cell
def _(alg, e1, e2, exp, np):
    _B = (e1 ^ e2).name("B")
    _theta = alg.scalar(np.pi / 4).name("θ", latex=r"\theta")
    _v = exp(-_B * _theta / 2)
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Division")
    return


@app.cell
def _(alg):
    _a = alg.scalar(10).name("a")
    _b = alg.scalar(2).name("b")
    _v = _a / _b
    _v
    return


@app.cell
def _(alg):
    _hbar = alg.scalar(1.055e-34).name("ℏ", latex=r"\hbar")
    _m = alg.scalar(9.109e-31).name("m", latex=r"m_e")
    _c = alg.scalar(3e8).name("c")
    _v = _hbar / (_m * _c)
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Rotor Sandwich")
    return


@app.cell
def _(alg, e1, e2, exp, np):
    _B = (e1 ^ e2).name("B")
    _theta = alg.scalar(np.pi / 4).name("θ", latex=r"\theta")
    _R = exp(-_B * _theta / 2).name("R")
    _v = e1.name("v")
    _result = _R * _v * ~_R
    _result
    return


@app.cell
def _(alg, e1, e2, exp, grade, np):
    _B = (e1 ^ e2).name("B")
    _theta = alg.scalar(np.pi / 4).name("θ", latex=r"\theta")
    _R = exp(-_B * _theta / 2).name("R")
    _v = e1.name("v")
    _result = grade(_R * _v * ~_R, 1)
    _result
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Simplification")
    return


@app.cell
def _(e1, simplify):
    _v = e1.name("v")
    _r = simplify(~~_v)
    _r
    return


@app.cell
def _(e1, simplify):
    _v = e1.name("v")
    _r = simplify(_v - _v)
    _r
    return


@app.cell
def _(e1, simplify):
    _v = e1.name("v")
    _r = simplify(_v + _v)
    _r
    return


@app.cell
def _(e1, simplify):
    _v = e1.name("v")
    _r = simplify(_v ^ _v)
    _r
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Spacetime Algebra")
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma")
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1, g2, g3, sta


@app.cell
def _(g0, g1, g2, g3):
    _E = (g1 * g0).name("E", latex=r"\mathbf{E}")
    _B = (g1 * g2).name("B", latex=r"\mathbf{B}")
    _I = (g0 * g1 * g2 * g3).name("I")
    _F = (_E.eval() + _I.eval() * _B.eval()).name("F", latex=r"\mathcal{F}")
    _F
    return


@app.cell
def _(exp, g0, g1, sta):
    _phi = sta.scalar(0.5).name("φ", latex=r"\varphi")
    _boost = (g0 * g1).name("B", latex=r"\hat{B}")
    _L = exp(_boost * _phi / 2).name("Λ", latex=r"\Lambda")
    _p = g0.name("p")
    _result = _L * _p * ~_L
    _result
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Wide Tilde & Overline (compound expressions)")
    return


@app.cell
def _(e1, e2, reverse):
    _v = reverse(e1 + e2)
    _v
    return


@app.cell
def _(e1, e2, reverse):
    _R = (e1 * e2).name("R")
    _v = e1.name("v")
    _result = _R * _v * reverse(_R)
    _result
    return


@app.cell
def _(conjugate, e1, e2):
    _v = conjugate(e1 + e2)
    _v
    return


@app.cell
def _(conjugate, e1, e2):
    _v = conjugate(e1 * e2)
    _v
    return


@app.cell
def _(e1, e2, reverse):
    _v = reverse(e1 * e2 * e1)
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Associative Wedge Flattening")
    return


@app.cell
def _(e1, e2, e3):
    _v = (e1 ^ e2) ^ e3
    _v
    return


@app.cell
def _(e1, e2, e3):
    _v = e1 ^ (e2 ^ e3)
    _v
    return


@app.cell
def _(e1, e2, e3):
    _a = e1.name("a")
    _b = e2.name("b")
    _c = e3.name("c")
    _v = (_a ^ _b) ^ _c
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Precedence: Products with Sums")
    return


@app.cell
def _(e1, e2, e3):
    _a = e1.name("a")
    _b = e2.name("b")
    _c = e3.name("c")
    _v = (_a + _b) * _c
    _v
    return


@app.cell
def _(e1, e2, e3):
    _a = e1.name("a")
    _b = e2.name("b")
    _c = e3.name("c")
    _v = _a * (_b + _c)
    _v
    return


@app.cell
def _(e1, e2, e3):
    _a = e1.name("a")
    _b = e2.name("b")
    _c = e3.name("c")
    _v = (_a + _b) ^ _c
    _v
    return


@app.cell
def _(e1, e2):
    _a = e1.name("a")
    _b = e2.name("b")
    _v = (2 * _a) ^ _b
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Negation Precedence")
    return


@app.cell
def _(e1, e2):
    _v = -(e1 + e2)
    _v
    return


@app.cell
def _(e1, e2):
    _v = -(e1 * e2)
    _v
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Postfix Unary on Products")
    return


@app.cell
def _(e1, e2, inverse):
    _v = inverse(e1 * e2)
    _v
    return


@app.cell
def _(dual, e1, e2):
    _v = dual(e1 * e2)
    _v
    return


@app.cell
def _(e1, e2, squared):
    _v = squared(e1 * e2)
    _v
    return


@app.cell
def _(e1, e2, squared):
    _a = e1.name("a")
    _b = e2.name("b")
    _v = squared(_a + _b)
    _v
    return


@app.cell
def _(e1, e2, e3, reverse):
    _v = reverse(e1 + e2) ^ reverse(e2 + e3)
    _v
    return


@app.cell
def _(e1, reverse):
    reverse(e1)
    return


@app.cell
def _(e1, e2, grade, reverse):
    grade((e1 * e2) * reverse(e1), 1)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
