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
        dual, norm, unit, inverse, exp, log, sandwich, squared,
        left_contraction, commutator, even_grades, odd_grades,
    )
    from galaga.symbolic import simplify
    import galaga_marimo as gm

    return (
        Algebra,
        commutator,
        dual,
        exp,
        gm,
        grade,
        norm,
        np,
        simplify,
        squared,
        unit,
    )


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    # LaTeX-Driven Naming

    Use `.name(latex=...)` to define symbols — unicode and ASCII are
    derived automatically from the LaTeX command.
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## 3D Euclidean — Rotors")
    return


@app.cell
def _(Algebra):
    cl3 = Algebra((1, 1, 1))
    e1, e2, e3 = cl3.basis_vectors(lazy=True)
    return cl3, e1, e2, e3


@app.cell
def _(cl3, np):
    _theta = cl3.scalar(np.pi / 3).name(latex=r"\theta")
    print(_theta)
    _theta
    return


@app.cell
def _(e1, e2):
    _B = (e1 ^ e2).name(latex=r"\mathbf{B}")
    print(_B)
    _B
    return


@app.cell
def _(cl3, e1, e2, exp, np):
    _B = (e1 ^ e2).name(latex=r"\mathbf{B}")
    _theta = cl3.scalar(np.pi / 3).name(latex=r"\theta")
    _R = exp(-_B * _theta / 2).name("R")
    print(_R)
    _R
    return


@app.cell
def _(cl3, e1, e2, exp, np):
    _B = (e1 ^ e2).name(latex=r"\mathbf{B}")
    _theta = cl3.scalar(np.pi / 3).name(latex=r"\theta")
    _R = exp(-_B * _theta / 2).name("R")
    _v = e1.name(latex=r"\mathbf{v}")
    _result = _R * _v * ~_R
    print(_result)
    _result
    return


@app.cell
def _(cl3, e1, e2, exp, grade, np):
    _B = (e1 ^ e2).name(latex=r"\mathbf{B}")
    _theta = cl3.scalar(np.pi / 3).name(latex=r"\theta")
    _R = exp(-_B * _theta / 2).name("R")
    _v = e1.name(latex=r"\mathbf{v}")
    _result = grade(_R * _v * ~_R, 1)
    print(_result)
    _result
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Quantum Mechanics — Pauli Algebra

    Spin-½ states are rotors in Cl(3,0). The Pauli matrices become
    basis vectors.
    """)
    return


@app.cell
def _(Algebra):
    pauli = Algebra((1, 1, 1), names="sigma")
    s1, s2, s3 = pauli.basis_vectors(lazy=True)
    return pauli, s1, s2, s3


@app.cell
def _(pauli):
    _psi = pauli.scalar(1.0).name(latex=r"\psi")
    print(_psi)
    _psi
    return


@app.cell
def _(exp, np, pauli, s2, s3):
    _psi = exp(-(s2 * s3) * pauli.scalar(np.pi / 4).name(latex=r"\theta") / 2).name(latex=r"\psi")
    print(_psi)
    _psi
    return


@app.cell
def _(exp, np, pauli, s2, s3):
    _psi = exp(-(s2 * s3).name(latex=r"\mathbf{B}") * pauli.scalar(np.pi / 4).name(latex=r"\theta") / 2).name(latex=r"\psi")
    _n = s3.name(latex=r"\hat{n}")
    _result = _psi * _n * ~_psi
    print(_result)
    _result
    return


@app.cell
def _(exp, pauli, s1, s2, s3):
    _omega = pauli.scalar(1.0).name(latex=r"\omega")
    _t = pauli.scalar(0.3).name("t")
    _B_field = (s1 * s2).name(latex=r"\mathbf{B}")
    _U = exp(-_B_field * _omega * _t / 2).name("U")
    _spin = s3.name(latex=r"\hat{s}")
    _precessed = _U * _spin * ~_U
    print(_precessed)
    _precessed
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Spacetime Algebra — Electromagnetism

    In Cl(1,3), the electromagnetic field is a bivector
    $\\mathcal{{F}} = \\mathbf{{E}} + I\\mathbf{{B}}$.
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma")
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1, g2, sta


@app.cell
def _(g0, g1):
    _E = (g1 * g0).name(latex=r"\mathbf{E}")
    print(_E)
    _E
    return


@app.cell
def _(g1, g2):
    _B = (g1 * g2).name(latex=r"\mathbf{B}")
    print(_B)
    _B
    return


@app.cell
def _(g0, g1, g2, sta):
    _E = (g1 * g0).name(latex=r"\mathbf{E}")
    _B = (g1 * g2).name(latex=r"\mathbf{B}")
    _I = sta.pseudoscalar().name("I")
    _F = (_E.eval() + _I.eval() * _B.eval()).name(latex=r"\mathcal{F}")
    print(_F)
    _F
    return


@app.cell
def _(g0, g1, g2, squared, sta):
    _E = (g1 * g0).name(latex=r"\mathbf{E}")
    _B = (g1 * g2).name(latex=r"\mathbf{B}")
    _I = sta.pseudoscalar().name("I")
    _F = (_E.eval() + _I.eval() * _B.eval()).name(latex=r"\mathcal{F}")
    _invariant = squared(_F)
    print(_invariant)
    _invariant
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Lorentz Boost

    A boost is a rotor built from a timelike bivector.
    """)
    return


@app.cell
def _(exp, g0, g1, sta):
    _phi = sta.scalar(0.5).name(latex=r"\varphi")
    _B = (g0 * g1).name(latex=r"\hat{B}")
    _Lambda = exp(_B * _phi / 2).name(latex=r"\Lambda")
    print(_Lambda)
    _Lambda
    return


@app.cell
def _(exp, g0, g1, sta):
    _phi = sta.scalar(0.5).name(latex=r"\varphi")
    _B = (g0 * g1).name(latex=r"\hat{B}")
    _Lambda = exp(_B * _phi / 2).name(latex=r"\Lambda")
    _p = g0.name("p")
    _boosted = _Lambda * _p * ~_Lambda
    print(_boosted)
    _boosted
    return


@app.cell
def _(exp, g0, g1, sta):
    _phi = sta.scalar(0.5).name(latex=r"\varphi")
    _B = (g0 * g1).name(latex=r"\hat{B}")
    _Lambda = exp(_B * _phi / 2).name(latex=r"\Lambda")
    _m = sta.scalar(1.0).name("m")
    _p = (_m * g0).name("p")
    _result = _Lambda * _p * ~_Lambda
    print(_result)
    _result
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Projective GA — Points and Lines

    In Cl(3,0,1), geometric primitives are blades.
    """)
    return


@app.cell
def _(Algebra):
    pga = Algebra((1, 1, 1, 0))
    pe1, pe2, pe3, pe0 = pga.basis_vectors(lazy=True)
    return pe0, pe1, pe2, pe3


@app.cell
def _(pe0, pe1, pe2):
    _P = (pe1 + pe0).name("P")
    _Q = (pe2 + pe0).name("Q")
    _line = (_P.eval() ^ _Q.eval()).name(latex=r"\ell")
    print(_line)
    _line
    return


@app.cell
def _(pe0, pe1, pe2, pe3):
    _P = (pe1 + pe0).name("P")
    _Q = (pe2 + pe0).name("Q")
    _R = (pe3 + pe0).name("R")
    _plane = (_P.eval() ^ _Q.eval() ^ _R.eval()).name(latex=r"\pi")
    print(_plane)
    _plane
    return


@app.cell
def _(dual, pe0, pe1, pe2, pe3):
    _P = (pe1 + pe0).name("P")
    _Q = (pe2 + pe0).name("Q")
    _R = (pe3 + pe0).name("R")
    _plane = (_P.eval() ^ _Q.eval() ^ _R.eval()).name(latex=r"\pi")
    _normal = dual(_plane)
    print(_normal)
    _normal
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Physical Constants — Named Scalars

    Named scalars with LaTeX-driven naming for clean formulas.
    """)
    return


@app.cell
def _(cl3):
    _hbar = cl3.scalar(1.055e-34).name(latex=r"\hbar")
    print(_hbar)
    _hbar
    return


@app.cell
def _(cl3):
    _m = cl3.scalar(9.109e-31).name(latex=r"m_e")
    print(_m)
    _m
    return


@app.cell
def _(cl3):
    _hbar = cl3.scalar(1.055e-34).name(latex=r"\hbar")
    _m = cl3.scalar(9.109e-31).name(latex=r"m_e")
    _c = cl3.scalar(3e8).name("c")
    _lambda = _hbar / (_m * _c)
    print(_lambda)
    _lambda
    return


@app.cell
def _(cl3):
    _hbar = cl3.scalar(1.055e-34).name(latex=r"\hbar")
    _p = cl3.scalar(1e-24).name("p")
    _lambda_dB = (_hbar / _p).name(latex=r"\lambda_{dB}")
    print(_lambda_dB)
    _lambda_dB
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Bivector Algebra — Angular Momentum

    Bivectors form a Lie algebra under the commutator.
    """)
    return


@app.cell
def _(commutator, e1, e2, e3):
    _L1 = (e2 ^ e3).name(latex=r"L_1")
    _L2 = (e3 ^ e1).name(latex=r"L_2")
    _result = commutator(_L1, _L2)
    print(_result)
    _result
    return


@app.cell
def _(e1, e2, e3, squared):
    _L1 = (e2 ^ e3).name(latex=r"L_1")
    _L2 = (e3 ^ e1).name(latex=r"L_2")
    _L3 = (e1 ^ e2).name(latex=r"L_3")
    _L_sq = squared(_L1).eval() + squared(_L2).eval() + squared(_L3).eval()
    print(_L_sq)
    _L_sq
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Simplification")
    return


@app.cell
def _(e1, simplify):
    _v = e1.name(latex=r"\mathbf{v}")
    _result = simplify(~~_v)
    print(_result)
    _result
    return


@app.cell
def _(e1, e2, simplify):
    _R = (e1 * e2).name("R")
    _result = simplify(_R * ~_R)
    print(_result)
    _result
    return


@app.cell
def _(e1, norm, simplify, unit):
    _v = e1.name(latex=r"\mathbf{v}")
    _result = simplify(norm(unit(_v)))
    print(_result)
    _result
    return


if __name__ == "__main__":
    app.run()
