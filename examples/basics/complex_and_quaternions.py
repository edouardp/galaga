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
        b_complex,
        b_quaternion,
        conjugate,
        exp,
        inverse,
        log,
        norm,
        np,
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
                if hasattr(_p, "display"):
                    parts.append(f"${_p.display()}$")
                elif hasattr(_p, "latex"):
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
    Clifford algebra elements. Both use bivectors as imaginary units.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Complex Numbers — Cl(2,0) even subalgebra

    The bivector $e_1 \wedge e_2$ squares to $-1$, giving us the imaginary
    unit $i = e_{12}$. The even subalgebra (scalars + bivectors) is
    isomorphic to the complex numbers.

    We set the notation so that `reverse()` (complex conjugation) renders
    as $z^{*}$.
    """)
    return


@app.cell
def _(Algebra, Display, b_complex):
    alg_c = Algebra(2, blades=b_complex())

    _i = alg_c.pseudoscalar(lazy=True)

    _d = Display()
    _d( _i )
    _d( _i**2 )
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

    _z1 = (3 + 4 * _i).name("z_1")
    _z2 = (1 - 2 * _i).name("z_2")

    _d = Display()
    _d( _z1 )
    _d( _z2 )
    _d( _z1 + _z2 )
    _d( _z1 * _z2 )
    _d( _z1**2 )
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Complex conjugation via reverse

    In Cl(2,0), the reverse negates the grade-2 part (the bivector $i$),
    acting as complex conjugation: $\widetilde{a + bi} = a - bi$.
    """)
    return


@app.cell
def _(Display, alg_c, conjugate, norm):
    _i = alg_c.pseudoscalar()

    _z = (3 + 4 * _i).name("z")
    _z_bar = conjugate(_z)

    _d = Display()
    _d( _z )
    _d( _z_bar )
    _d( _z * _z_bar )
    _d( norm(_z) )
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

    _theta = 0.25 * alg_c.pi
    _r = exp(_theta * _i)

    _d = Display()
    _d( _r )
    _d(f"cos(π/4) = {np.cos(_theta.scalar_part):.6f},  sin(π/4) = {np.sin(_theta.scalar_part):.6f}")
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Complex division

    Division uses the Clifford inverse: $z_1 / z_2 = z_1 z_2^{-1}$.
    """)
    return


@app.cell
def _(Display, alg_c):
    _i = alg_c.pseudoscalar()

    _z1 = (3 + 4 * _i).name("z_1")
    _z2 = (1 - 2 * _i).name("z_2")

    _d = Display()
    _d( _z1 )
    _d( _z2 )
    _d( _z1 / _z2 )
    _d( _z2 * (_z1 / _z2) )
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
def _(Algebra, b_quaternion):
    alg_q = Algebra(3, blades=b_quaternion())
    i, j, k = alg_q.basis_blades(k=2, lazy=True)
    return alg_q, i, j, k


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Hamilton's Quaternion Identities
    """)
    return


@app.cell
def _(Display, i, j, k):
    _d = Display()
    _d( i**2 )
    _d( j**2 )
    _d( k**2 )
    _d( i*j*k )
    _d()
    _d( i*j )
    _d( j*k )
    _d( k*i )
    _d()
    _d( j*i )
    _d( k*j )
    _d( i*k )
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
def _(Display, i, j, k):
    _q1 = (1 + 2 * i + 3 * j + 4 * k).name("q_1")
    _q2 = (2 - i + j - 3 * k).name("q_2")

    _d = Display()
    _d( _q1 )
    _d( _q2 )
    _d( _q1 + _q2 )
    _d( _q1 * _q2 )
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Quaternion conjugate, norm, inverse

    The quaternion conjugate is the Clifford conjugate (reverse $\circ$
    involute), which negates the bivector part: $\bar{q} = a - bi - cj - dk$.
    """)
    return


@app.cell
def _(Display, conjugate, i, inverse, j, k, norm):
    _q = (1 + 2*i + 3*j + 4*k).name("q")
    _qbar = conjugate(_q)
    _qinv = inverse(_q)

    _d = Display()
    _d( _q )
    _d( _qbar )
    _d( _q * _qbar )
    _d( norm(_q) )
    _d( _qinv )
    _d( _q * _qinv )
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### 3D rotation via quaternion sandwich

    A unit quaternion $q = \cos(\theta/2) + \sin(\theta/2)(ai + bj + ck)$
    rotates a pure quaternion $v = xi + yj + zk$ by angle $\theta$ around
    axis $(a, b, c)$ via the sandwich product $q v \bar{q}$.
    """)
    return


@app.cell
def _(Display, alg_q, conjugate, exp, i, j, np):
    _theta = 0.25 * alg_q.pi
    _axis = i
    _q = exp(_theta * _axis).name("q")
    _v = j.eval().name('v')
    _rotated = (_q * _v * conjugate(_q)).name("v'")

    _d = Display()
    _d( _v )
    _d( _q, fr"$\qquad$ ({np.degrees(_theta.scalar_part)*2}° rotation around {_axis})")
    _d( _rotated )
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
def _(Display, alg_q, exp, i, log):
    _theta = alg_q.pi / 3
    _q = exp(i * _theta / 2)
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
    """)
    return


@app.cell
def _(Display, i, j, k, norm, unit):
    _q = (1 + 2 * i + 3 * j + 4 * k).name("q")
    _qu = unit(_q)

    _d = Display()
    _d( _q )
    _d( norm(_q) )
    _d( _qu )
    _d( norm(_qu) )
    _d
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
