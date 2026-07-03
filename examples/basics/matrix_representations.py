import marimo

__generated_with = "0.23.4"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_marimo")
    _gmat = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_matrix")
    for _p in [_root, _gamo, _gmat]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga import Algebra, gp, reverse, exp, sandwich
    from galaga import b_sta

    import galaga_marimo as gm
    from galaga_matrix import to_matrix, from_matrix, MatrixRepr, QuatMatrixRepr, to_quaternion_matrix
    from galaga_matrix.matrix import compact_basis

    return (
        Algebra,
        MatrixRepr,
        b_sta,
        compact_basis,
        exp,
        from_matrix,
        gm,
        gp,
        mo,
        np,
        sandwich,
        to_matrix,
        to_quaternion_matrix,
    )


@app.cell
def _(MatrixRepr, to_matrix, to_quaternion_matrix):
    # Monkey patch, oook oook
    from galaga.algebra import Multivector
    #from galaga_matrix import to_matrix, MatrixRepr

    Multivector.matrix = property(lambda self: MatrixRepr(to_matrix(self), algebra=self.algebra, mode="left-regular"))
    Multivector.pauli = property(lambda self: MatrixRepr(to_matrix(self, mode="compact"), algebra=self.algebra, mode="compact"))
    Multivector.dirac = property(lambda self: MatrixRepr(to_matrix(self, mode="compact"), algebra=self.algebra, mode="compact"))
    Multivector.quat = property(lambda self: MatrixRepr(to_quaternion_matrix(self)))
    return


@app.cell
def _(gm):
    gm.md(t"""
    # Matrix Representations of Clifford Algebras

    Every multivector has a matrix representation. This notebook demonstrates
    two modes:

    - **Left-regular**: the $2^n \\times 2^n$ real matrix from the left multiplication map
    - **Compact**: the minimal-dimension complex matrix (Pauli, Dirac, or general)
    """)
    return


@app.cell
def _(gm):
    gm.md(t"""
    ## Pauli Matrices — $\\mathrm{{Cl}}(3,0)$

    The three basis vectors of $\\mathrm{{Cl}}(3,0)$ map to the $2 \\times 2$ Pauli matrices.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, compact_basis, gm):
    _cl3 = Algebra(3)
    _e1, _e2, _e3 = _cl3.basis_vectors(symbolic=True)

    _gammas = compact_basis(_cl3)
    _s1 = MatrixRepr(_gammas[0], label=r"\sigma_1")
    _s2 = MatrixRepr(_gammas[1], label=r"\sigma_2")
    _s3 = MatrixRepr(_gammas[2], label=r"\sigma_3")

    gm.md(t"""
    {_s1:block}

    {_s2:block}

    {_s3:block}

    Verify: $\\sigma_1^2 = \\sigma_2^2 = \\sigma_3^2 = I$ and $\\sigma_i \\sigma_j = -\\sigma_j \\sigma_i$ for $i \\neq j$.
    """)
    return


@app.cell
def _(gm):
    gm.md(t"""
    ### Vector → Matrix → Vector roundtrip
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, from_matrix, gm, np, to_matrix):
    _cl3 = Algebra(3)
    _e1, _e2, _e3 = _cl3.basis_vectors(symbolic=True)
    _v = (3 * _e1 + 2 * _e2 - _e3).name(latex=r"\mathbf{v}")

    _mat = to_matrix(_v, mode="compact")
    _v_back = from_matrix(_cl3, _mat, mode="compact")
    _v_back.name(latex=r"\mathbf{v}'")

    gm.md(t"""
    Start with {_v}:

    {_v.display()}

    Its compact matrix representation:

    {MatrixRepr(_mat, label=r"M(\mathbf{v})"):block}

    Recover the multivector from the matrix:

    {_v_back.display()}

    Roundtrip exact: {np.allclose(_v.data, _v_back.data)}
    """)
    return


@app.cell
def _(gm):
    gm.md(t"""
    ## Dirac Matrices — $\\mathrm{{Cl}}(1,3)$

    The Spacetime Algebra has a $4 \\times 4$ complex matrix representation:
    the Dirac gamma matrices.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, compact_basis, gm, np):
    _sta = Algebra(1, 3)
    _gammas = compact_basis(_sta)

    _labels = [r"\gamma^0", r"\gamma^1", r"\gamma^2", r"\gamma^3"]
    _mats = [MatrixRepr(g, label=l) for g, l in zip(_gammas, _labels)]

    _I4 = np.eye(4)
    _sq = [g @ g for g in _gammas]
    _signs = ["+I" if np.allclose(s, _I4) else "-I" for s in _sq]

    gm.md(t"""
    {_mats[0]:block}

    {_mats[1]:block}

    {_mats[2]:block}

    {_mats[3]:block}

    Squares: $(\\gamma^0)^2 = {_signs[0]}$, $(\\gamma^1)^2 = {_signs[1]}$,
    $(\\gamma^2)^2 = {_signs[2]}$, $(\\gamma^3)^2 = {_signs[3]}$
    — matching the $(+,-,-,-)$ signature.
    """)
    return


@app.cell
def _(gm):
    gm.md(t"""
    ### Product homomorphism

    The matrix representation is an algebra homomorphism:
    $M(ab) = M(a) \\, M(b)$.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, gm, gp, np, to_matrix):
    _sta = Algebra(1, 3, display_repr=True)
    _g0, _g1, _g2, _g3 = _sta.basis_vectors(symbolic=True)

    _a = (2 * _g0 + _g1).name(latex="a")
    _b = (_g2 - 3 * _g3).name(latex="b")
    _ab = gp(_a, _b)

    _Ma = to_matrix(_a, mode="compact")
    _Mb = to_matrix(_b, mode="compact")
    _Mab = to_matrix(_ab, mode="compact")
    _product = _Ma @ _Mb

    gm.md(t"""
    {_a}

    {_b}

    {_ab}

    {MatrixRepr(_Mab, label="M(ab)"):block}

    {MatrixRepr(_product, label="M(a) M(b)"):block}

    $M(ab) = M(a)\\,M(b)$: {np.allclose(_Mab, _product)}
    """)
    return


@app.cell
def _(gm):
    gm.md(t"""
    ## Left-Regular Representation

    The left-regular representation works for **any** algebra, including
    degenerate ones like PGA. It maps each multivector to a $2^n \\times 2^n$
    real matrix.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, from_matrix, gm, np, to_matrix):
    _cl2 = Algebra(2)
    _e1, _e2 = _cl2.basis_vectors(symbolic=True)
    _v = (2 * _e1 + 3 * _e2).name(latex=r"\mathbf{v}")

    _mat = to_matrix(_v, mode="left-regular")
    _v_back = from_matrix(_cl2, _mat, mode="left-regular")
    _v_back.name(latex=r"\mathbf{v}'")

    gm.md(t"""
    In $\\mathrm{{Cl}}(2,0)$, the left-regular representation gives $4 \\times 4$ real matrices.

    {_v.display()}

    {MatrixRepr(_mat.astype(complex), label=r"L(\mathbf{v})"):block}

    Roundtrip: {_v_back.display()} — exact: {np.allclose(_v.data, _v_back.data)}
    """)
    return


@app.cell
def _(gm):
    gm.md(t"""
    ### PGA — degenerate algebra

    The left-regular representation handles degenerate algebras where the
    compact representation is not available.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, from_matrix, gm, np, to_matrix):
    _pga = Algebra(2, 0, 1)
    _e = _pga.basis_vectors(symbolic=True)
    _v = (2 * _e[0] + _e[1] + 3 * _e[2]).name(latex=r"\mathbf{p}")

    _mat = to_matrix(_v, mode="left-regular")
    _v_back = from_matrix(_pga, _mat, mode="left-regular")

    gm.md(t"""
    $\\mathrm{{Cl}}(2,0,1)$ — Projective Geometric Algebra with one null dimension.

    {_v.display()}

    {MatrixRepr(_mat.astype(complex), label=r"L(\mathbf{p})"):block}

    Roundtrip exact: {np.allclose(_v.data, _v_back.data)}
    """)
    return


@app.cell
def _(gm):
    gm.md(t"""
    ## Rotors in Matrix Form

    A rotor $R = e^{{-B\\theta/2}}$ in $\\mathrm{{Cl}}(3,0)$ maps to a $2 \\times 2$
    unitary matrix — the SU(2) representation of the rotation.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, exp, from_matrix, gm, np, sandwich, to_matrix):
    _cl3 = Algebra(3)
    _e1, _e2, _e3 = _cl3.basis_vectors(symbolic=True)

    _B = (_e1 ^ _e2).name(latex="B")
    _R = exp(-0.5 * np.pi / 3 * _B.eval()).name(latex="R")
    _v = (3 * _e1 + _e2).name(latex=r"\mathbf{v}")

    _MR = to_matrix(_R, mode="compact")
    _Mv = to_matrix(_v, mode="compact")

    # Sandwich in matrix form: M(RvR†) = MR @ Mv @ MR†
    _MR_dag = _MR.conj().T
    _rotated_mat = _MR @ _Mv @ _MR_dag
    _rotated = from_matrix(_cl3, _rotated_mat, mode="compact")
    _rotated.name(latex=r"\mathbf{v}'")

    # Compare with GA sandwich
    _rotated_ga = sandwich(_R.eval(), _v.eval())

    gm.md(t"""
    Rotation by $60°$ in the {_B} plane:

    {_R.display()}

    {MatrixRepr(_MR, label="M(R)"):block}

    $M(R)$ is unitary: $M(R)^\\dagger M(R) = \\mathbb{{I}}$: {np.allclose(_MR_dag @ _MR, np.eye(2))}

    $M(R)$ is special, aka determinant = 1: $det(M(R)) = 1$: {np.allclose(np.linalg.det(_MR), 1)}

    Rotate {_v} via matrix sandwich $M(R) \\, M(\\mathbf{{v}}) \\, M(R)^\\dagger$:

    {_rotated.display()}

    Matches GA sandwich product: {np.allclose(_rotated.data, _rotated_ga.data)}
    """)
    return


@app.cell
def _(gm):
    gm.md(t"""
    ## Comparison: Compact vs Left-Regular

    The compact representation is much smaller but carries the same algebraic
    information.
    """)
    return


@app.cell
def _(Algebra, gm, to_matrix):
    _sta = Algebra(1, 3)
    _g = _sta.basis_vectors()
    _mv = 2 * _g[0] + _g[1] - 0.5 * _g[3]

    _lr = to_matrix(_mv, mode="left-regular")
    _cp = to_matrix(_mv, mode="compact")

    gm.md(t"""
    For a vector in $\\mathrm{{Cl}}(1,3)$:

    | | Left-regular | Compact |
    |---|---|---|
    | **Size** | ${_lr.shape[0]} \\times {_lr.shape[1]}$ real | ${_cp.shape[0]} \\times {_cp.shape[1]}$ complex |
    | **Entries** | {_lr.size} | {_cp.size} |
    | **dtype** | `{_lr.dtype}` | `{_cp.dtype}` |
    """)
    return


@app.cell
def _(Algebra, b_sta):
    sta = Algebra(1, 3, blades=b_sta(sigmas=True, pseudovectors=True, pss="I"), display_repr=True)
    y0,y1,y2,y3 = sta.basis_vectors(symbolic=True)
    I = sta.pseudoscalar(symbolic=True)
    return I, sta, y0, y1, y2, y3


@app.cell
def _(to_matrix, y0):
    to_matrix(y0, mode="compact")
    return


@app.cell
def _(mo):
    scalar_slider = mo.ui.slider(-5,5, value=0, label="scalar")

    y0_slider = mo.ui.slider(-5,5, value=0, label="y0")
    y1_slider = mo.ui.slider(-5,5, value=0, label="y1")
    y2_slider = mo.ui.slider(-5,5, value=0, label="y2")
    y3_slider = mo.ui.slider(-5,5, value=0, label="y3")

    y01_slider = mo.ui.slider(-5,5, value=0, label="y01")
    y02_slider = mo.ui.slider(-5,5, value=0, label="y02")
    y03_slider = mo.ui.slider(-5,5, value=0, label="y03")
    y12_slider = mo.ui.slider(-5,5, value=0, label="y12")
    y13_slider = mo.ui.slider(-5,5, value=0, label="y13")
    y23_slider = mo.ui.slider(-5,5, value=0, label="y23")

    y012_slider = mo.ui.slider(-5,5, value=0, label="y012")
    y013_slider = mo.ui.slider(-5,5, value=0, label="y013")
    y023_slider = mo.ui.slider(-5,5, value=0, label="y023")
    y123_slider = mo.ui.slider(-5,5, value=0, label="y123")

    pss_slider = mo.ui.slider(-5,5, value=0, label="y0123")
    return (
        pss_slider,
        scalar_slider,
        y012_slider,
        y013_slider,
        y01_slider,
        y023_slider,
        y02_slider,
        y03_slider,
        y0_slider,
        y123_slider,
        y12_slider,
        y13_slider,
        y1_slider,
        y23_slider,
        y2_slider,
        y3_slider,
    )


@app.cell
def _(
    gm,
    mo,
    pss_slider,
    scalar_slider,
    y0,
    y012_slider,
    y013_slider,
    y01_slider,
    y023_slider,
    y02_slider,
    y03_slider,
    y0_slider,
    y1,
    y123_slider,
    y12_slider,
    y13_slider,
    y1_slider,
    y2,
    y23_slider,
    y2_slider,
    y3,
    y3_slider,
):
    mv = (scalar_slider.value +
          y0_slider.value * y0 +
          y1_slider.value * y1 +
          y2_slider.value * y2 +
          y3_slider.value * y3 +
          y01_slider.value * (y0^y1) +
          y02_slider.value * (y0^y2) +
          y03_slider.value * (y0^y3) +
          y12_slider.value * (y1^y2) +
          y13_slider.value * (y1^y3) +
          y23_slider.value * (y2^y3) +
          y012_slider.value * (y0^y1^y2) +
          y013_slider.value * (y0^y1^y3) +
          y023_slider.value * (y0^y2^y3) +
          y123_slider.value * (y1^y2^y3) +
          pss_slider.value * (y0^y1^y2^y3)).eval().name("mv")

    mo.vstack([
        scalar_slider, y0_slider, y1_slider, y2_slider, y3_slider, y01_slider, y02_slider, y03_slider, y12_slider, y13_slider, y23_slider, y012_slider, y013_slider, y023_slider, y123_slider, pss_slider,
    gm.md(t"""
    {mv} $\\quad=\\quad$ {mv.dirac} $\\quad=\\quad$ {mv.quat}
    """)
    ])
    return


@app.cell
def _(I, y1, y2):
    m = (1 + 2*(y1^y2) + 3*I).dirac
    return (m,)


@app.cell
def _(m):
    m
    return


@app.cell
def _(m, np):
    np.trace(m)
    return


@app.cell
def _(m):
    m.mv
    return


@app.cell
def _(I, y1, y2):
    (1 + 2*(y1^y2) + 3*I)
    return


@app.cell
def _():
    return


@app.cell
def _(I, y1, y3):
    (1 + 2*(y1^y3) + 3*I).quat
    return


@app.cell
def _(np):
    gm1 = np.array([[0,1,0],[1,0,0],[0,0,0]])
    return (gm1,)


@app.cell
def _(from_matrix, gm1, sta):
    from_matrix(sta,gm1)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
