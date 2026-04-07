import marimo

__generated_with = "0.22.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import numpy as np

    from galaga import (
        Algebra,
        Notation,
        b_complex,
        b_quaternion,
        conjugate,
        exp,
        inverse,
        log,
        norm,
        reverse,
        unit,
    )
    from galaga.notation import NotationRule

    return (
        Algebra,
        Notation,
        NotationRule,
        b_complex,
        b_quaternion,
        conjugate,
        exp,
        inverse,
        log,
        norm,
        np,
        reverse,
        unit,
    )


@app.cell
def _(mo):
    class Display:
        def __init__(self):
            self._lines = []

        def __call__(self, *p):
            parts = []
            for _p in p:
                if hasattr(_p, "latex"):
                    parts.append(f"${_p.latex()}$")
                else:
                    parts.append(str(_p))
            self._lines.append(" ".join(parts))

        def _repr_html_(self):
            return mo.md("<br/>".join(self._lines)).text

    return (Display,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Complex Numbers and Quaternions in Geometric Algebra

    galaga provides `b_complex()` and `b_quaternion()` convention factories
    that let you work with complex numbers and quaternions directly as
    Clifford algebra elements.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Complex Numbers — Cl(2,0) even subalgebra

    The bivector $e_1 \wedge e_2$ squares to $-1$, giving us the imaginary
    unit $i = e_{12}$. The even subalgebra (scalars + bivectors) is
    isomorphic to the complex numbers.
    """)
    return


@app.cell
def _(Algebra, Display, Notation, NotationRule, b_complex):
    alg_c = Algebra(
        2,
        blades=b_complex(),
        notation=Notation.default().set(
            "Reverse", "latex", NotationRule(kind="superscript", symbol="*")
        ),
    )
    _e1, _e2 = alg_c.basis_vectors()
    _i = alg_c.pseudoscalar()

    _d = Display()
    _d("i = e₁e₂,  i² =", _i * _i)
    _d
    return (alg_c,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Complex arithmetic
    """)
    return


@app.cell
def _(Display, alg_c):
    _i = alg_c.pseudoscalar()
    _z1 = (3 + 4 * _i).name("z₁")
    _z2 = (1 - 2 * _i).name("z₂")
    _d = Display()
    _d(f"${_z1.display().latex()}$")
    _d(f"${_z2.display().latex()}$")
    _d("z₁ + z₂ =", _z1 + _z2)
    _d("z₁ · z₂ =", _z1 * _z2)
    _d("z₁² =", _z1 * _z1)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Complex conjugation via reverse

    In Cl(2,0), the reverse negates the grade-2 part (the bivector $i$),
    acting as complex conjugation. We set the notation so reverse renders
    as $z^{*}$.
    """)
    return


@app.cell
def _(Display, alg_c, norm, reverse):
    _i = alg_c.pseudoscalar()
    _z = (3 + 4 * _i).name("z")
    _zc = reverse(_z)
    _d = Display()
    _d(f"${_z.display().latex()}$")
    _d(f"${_zc.display().latex()}$")
    _d(f"${(_z * _zc).display().latex()}$")
    _d(f"${norm(_z).display().latex()}$")
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Euler's formula

    $e^{i\theta} = \cos\theta + i\sin\theta$ works directly via `exp()`.
    """)
    return


@app.cell
def _(Display, alg_c, exp, np):
    _i = alg_c.pseudoscalar()
    _theta = np.pi / 4
    _rot = exp(_i * alg_c.scalar(_theta))
    _d = Display()
    _d(f"exp(i·π/4) =", _rot)
    _d(f"cos(π/4) = {np.cos(_theta):.6f}, sin(π/4) = {np.sin(_theta):.6f}")
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Complex division

    Division uses the Clifford inverse: $z_1 / z_2 = z_1 z_2^{-1}$.
    """)
    return


@app.cell
def _(Display, alg_c):
    _i = alg_c.pseudoscalar()
    _z1 = (3 + 4 * _i).name("z₁")
    _z2 = (1 - 2 * _i).name("z₂")
    _d = Display()
    _d(f"${_z1.display().latex()}$")
    _d(f"${_z2.display().latex()}$")
    _d("z₁ / z₂ =", _z1 / _z2)
    _d("z₂ · (z₁/z₂) =", _z2 * (_z1 / _z2))
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Quaternions — Cl(3,0) bivectors

    The three bivectors of Cl(3,0) square to $-1$ and satisfy Hamilton's
    identities. `b_quaternion()` names them $i$, $j$, $k$ and sets the
    display order so terms render conventionally.
    """)
    return


@app.cell
def _(Algebra, Display, b_quaternion):
    alg_q = Algebra(3, blades=b_quaternion())
    _e1, _e2, _e3 = alg_q.basis_vectors()
    i, j, k = alg_q.basis_blades(k=2)
    _d = Display()
    _d("i =", i, "  j =", j, "  k =", k)
    _d("i² =", i * i, "  j² =", j * j, "  k² =", k * k)
    _d("ijk =", i * j * k)
    _d
    return alg_q, i, j, k


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Hamilton's multiplication table
    """)
    return


@app.cell
def _(Display, i, j, k):
    _d = Display()
    _d("ij =", i * j, "  jk =", j * k, "  ki =", k * i)
    _d("ji =", j * i, "  kj =", k * j, "  ik =", i * k)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Quaternion arithmetic

    Terms display in the conventional $1 + ai + bj + ck$ order.
    """)
    return


@app.cell
def _(Display, alg_q, i, j, k):
    _q1 = alg_q.scalar(1) + 2 * i + 3 * j + 4 * k
    _q2 = alg_q.scalar(2) - i + j - 3 * k
    _d = Display()
    _d("q₁ =", _q1)
    _d("q₂ =", _q2)
    _d("q₁ + q₂ =", _q1 + _q2)
    _d("q₁ · q₂ =", _q1 * _q2)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Quaternion conjugate, norm, inverse

    The quaternion conjugate is the Clifford conjugate (reverse ∘ involute),
    which negates the bivector part.
    """)
    return


@app.cell
def _(Display, alg_q, conjugate, i, inverse, j, k, norm):
    _q = alg_q.scalar(1) + 2 * i + 3 * j + 4 * k
    _qbar = conjugate(_q)
    _d = Display()
    _d("q =", _q)
    _d("q̄ = conjugate(q) =", _qbar)
    _d("q · q̄ =", _q * _qbar)
    _d("|q| =", norm(_q))
    _d("q⁻¹ =", inverse(_q))
    _d("q · q⁻¹ =", _q * inverse(_q))
    _d
    return


@app.cell
def _(Display, alg_q, conjugate, exp, i, j, np):
    # Rotate j by 90° around the i axis
    _theta = np.pi / 2
    _q = exp(i * alg_q.scalar(_theta / 2))
    _v = j
    _rotated = _q * _v * conjugate(_q)
    _d = Display()
    _d(f"Rotation quaternion (90° around i): q =", _q)
    _d("v =", _v)
    _d("qvq̄ =", _rotated)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Log, exp, and SLERP

    `log(q)` extracts the bivector (rotation axis × half-angle) from a unit
    quaternion. Scaling it and re-exponentiating gives spherical linear
    interpolation (SLERP).
    """)
    return


@app.cell
def _(Display, alg_q, exp, i, log, np):
    _theta = np.pi / 3
    _q = exp(i * alg_q.scalar(_theta / 2))
    _b = log(_q)
    _d = Display()
    _d("q = exp(iπ/6) =", _q)
    _d("log(q) =", _b)
    _d("exp(log(q)) =", exp(_b))
    _d()
    _d("SLERP — interpolate from identity to q:")
    for _t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        _qt = exp(alg_q.scalar(_t) * _b)
        _d(f"  t={_t}:", _qt)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Unit quaternion

    `unit(q)` normalises any quaternion to unit length.
    """)
    return


@app.cell
def _(Display, alg_q, i, j, k, norm, unit):
    _q = alg_q.scalar(1) + 2 * i + 3 * j + 4 * k
    _qu = unit(_q)
    _d = Display()
    _d("q =", _q)
    _d("|q| =", norm(_q))
    _d("unit(q) =", _qu)
    _d("|unit(q)| =", norm(_qu))
    _d
    return


if __name__ == "__main__":
    app.run()
