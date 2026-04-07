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
        b_complex,
        b_quaternion,
        conjugate,
        exp,
        gp,
        inverse,
        involute,
        log,
        norm,
        reverse,
        unit,
    )

    return (
        Algebra,
        b_complex,
        b_quaternion,
        conjugate,
        exp,
        gp,
        inverse,
        involute,
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
    mo.md("""
    ## Complex Numbers — Cl(0,1)

    A single basis vector with $e_1^2 = -1$ gives us the imaginary unit $i$.
    """)
    return


@app.cell
def _(Algebra, Display, b_complex):
    _alg = Algebra(0, 1, blades=b_complex())
    _i = _alg.basis_vectors()[0]
    _d = Display()
    _d("i² =", _i * _i)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Complex arithmetic
    """)
    return


@app.cell
def _(Algebra, Display, b_complex):
    _alg = Algebra(0, 1, blades=b_complex())
    (_i,) = _alg.basis_vectors()
    _z1 = _alg.scalar(3) + 4 * _i
    _z2 = _alg.scalar(1) - 2 * _i
    _d = Display()
    _d("z₁ =", _z1)
    _d("z₂ =", _z2)
    _d("z₁ + z₂ =", _z1 + _z2)
    _d("z₁ · z₂ =", _z1 * _z2)
    _d("z₁² =", _z1 * _z1)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Complex conjugation via grade involution

    In Cl(0,1), grade involution negates the grade-1 part (the imaginary
    component), acting as complex conjugation.
    """)
    return


@app.cell
def _(Algebra, Display, b_complex, involute, norm):
    _alg = Algebra(0, 1, blades=b_complex())
    (_i,) = _alg.basis_vectors()
    _z = _alg.scalar(3) + 4 * _i
    _zbar = involute(_z)
    _d = Display()
    _d("z =", _z)
    _d("z̄ = involute(z) =", _zbar)
    _d("z · z̄ =", _z * _zbar)
    _d("|z| =", norm(_z))
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Euler's formula

    $e^{i\\theta} = \\cos\\theta + i\\sin\\theta$ works directly via `exp()`.
    """)
    return


@app.cell
def _(Algebra, Display, b_complex, exp, np):
    _alg = Algebra(0, 1, blades=b_complex())
    (_i,) = _alg.basis_vectors()
    _theta = np.pi / 4
    _rot = exp(_i * _alg.scalar(_theta))
    _d = Display()
    _d(f"exp(i·π/4) =", _rot)
    _d(f"cos(π/4) = {np.cos(_theta):.6f}, sin(π/4) = {np.sin(_theta):.6f}")
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


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### 3D rotation via quaternion sandwich

    A unit quaternion $q = \\cos(\\theta/2) + \\sin(\\theta/2)(ai + bj + ck)$
    rotates a pure quaternion $v = xi + yj + zk$ by angle $\\theta$ around
    axis $(a, b, c)$ via the sandwich product $qv\\bar{q}$.
    """)
    return


@app.cell
def _(Display, alg_q, conjugate, exp, i, j, k, np):
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


if __name__ == "__main__":
    app.run()
