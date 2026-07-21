import marimo

__generated_with = "0.23.11"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_marimo")
    for _p in [_root, _gamo]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import numpy as np

    import galaga_marimo as gm
    from galaga.facade import (
        Algebra,
        DisplayPolicy,
        conjugate,
        exp,
        inverse,
        log,
        norm,
        p_complex,
        p_quaternion,
        unit,
    )

    return (
        Algebra,
        DisplayPolicy,
        conjugate,
        exp,
        gm,
        inverse,
        log,
        norm,
        np,
        p_complex,
        p_quaternion,
        unit,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Complex Numbers and Quaternions in Geometric Algebra

    Galaga provides the complete `p_complex()` and `p_quaternion()` presets,
    which combine the numeric algebra, blade convention, display order, and
    notation needed to work with complex numbers and quaternions directly as
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
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, gm, p_complex):
    alg_c = Algebra(config=p_complex(), display=DisplayPolicy(content="full"))

    _i = alg_c.blade("imaginary", expr=True)

    gm.md(rt"""
    {_i}

    {_i**2}
    """)
    return (alg_c,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Complex arithmetic
    """)
    return


@app.cell
def _(alg_c, gm):
    _i = alg_c.blade("imaginary", expr=True)

    _z1 = (3 + 4 * _i).named("z_1")
    _z2 = (1 - 2 * _i).named("z_2")

    gm.md(rt"""
    {_z1}

    {_z2}

    {_z1 + _z2}

    {_z1 * _z2}

    {_z1**2}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Complex conjugation via reverse

    In Cl(2,0), the reverse negates the grade-2 part (the bivector $i$),
    acting as complex conjugation: $\overline{a + bi} = a - bi$.
    """)
    return


@app.cell
def _(alg_c, conjugate, gm, norm):
    _i = alg_c.blade("imaginary", expr=True)

    _z = (3 + 4 * _i).named("z")

    gm.md(rt"""
    {_z}

    {conjugate(_z)}

    {_z * conjugate(_z)}

    {norm(_z)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Euler's formula

    $e^{i\theta} = \cos\theta + i\sin\theta$ works directly via `exp()`.
    """)
    return


@app.cell
def _(alg_c, exp, gm, np):
    _i = alg_c.blade("imaginary", expr=True)

    _pi = alg_c.scalar(np.pi).named("pi", latex=r"\pi")
    _theta = 0.25 * _pi
    _r = exp(_theta * _i)

    gm.md(rt"""
    {_r}

    $\cos(0.25\pi) = {np.cos(float(_theta)):.6f}$

    $\sin(0.25\pi) = {np.sin(float(_theta)):.6f}$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Complex division

    Division uses the Clifford inverse: $z_1 / z_2 = z_1 z_2^{-1}$.
    """)
    return


@app.cell
def _(alg_c, gm):
    _i = alg_c.blade("imaginary", expr=True)

    _z1 = (3 + 4 * _i).named("z_1")
    _z2 = (1 - 2 * _i).named("z_2")

    gm.md(rt"""
    {_z1}

    {_z2}

    {_z1 / _z2}

    {_z2 * (_z1 / _z2)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Quaternions — Cl(3,0) bivectors

    The three bivectors of Cl(3,0) square to $-1$ and satisfy Hamilton's
    identities. `p_quaternion()` names them $i$, $j$, $k$ and sets the
    display order so terms render conventionally.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, p_quaternion):
    alg_q = Algebra(config=p_quaternion(), display=DisplayPolicy(content="full"))
    i, j, k = alg_q.blades(
        "quaternion_i",
        "quaternion_j",
        "quaternion_k",
        expr=True,
    )
    return alg_q, i, j, k


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Hamilton's Quaternion Identities
    """)
    return


@app.cell
def _(gm, i, j, k):
    gm.md(rt"""
    {i**2}

    {j**2}

    {k**2}

    {i * j * k}

    ---

    {i * j}

    {j * k}

    {k * i}

    ---

    {j * i}

    {k * j}

    {i * k}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Quaternion arithmetic

    Terms display in the conventional $1 + ai + bj + ck$ order.
    """)
    return


@app.cell
def _(gm, i, j, k):
    _q1 = (1 + 2 * i + 3 * j + 4 * k).named("q_1")
    _q2 = (2 - i + j - 3 * k).named("q_2")

    gm.md(rt"""
    {_q1}

    {_q2}

    {_q1 + _q2}

    {_q1 * _q2}
    """)
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
def _(conjugate, gm, i, inverse, j, k, norm):
    _q = (1 + 2 * i + 3 * j + 4 * k).named("q")

    gm.md(rt"""
    {_q}

    {conjugate(_q)}

    {_q * conjugate(_q)}

    {norm(_q)}

    {inverse(_q)}

    {_q * inverse(_q)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3D rotation via quaternion sandwich

    A unit quaternion $q = \cos(\theta/2) + \sin(\theta/2)(ai + bj + ck)$
    rotates a pure quaternion $v = xi + yj + zk$ by angle $\theta$ around
    axis $(a, b, c)$ via the sandwich product $q v \bar{q}$.
    """)
    return


@app.cell
def _(alg_q, conjugate, exp, gm, i, j, np):
    _pi = alg_q.scalar(np.pi).named("pi", latex=r"\pi")
    _theta = 0.25 * _pi
    _axis = i
    _q = exp(_theta * _axis).named("q")
    _v = j.named("v")
    _rotated = (_q * _v * conjugate(_q)).named("v'")
    _degrees = np.degrees(float(_theta)) * 2

    gm.md(rt"""
    {_v}

    {_q}

    This is a ${_degrees:g}^\circ$ rotation around {_axis}.

    {_rotated}
    """)
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
def _(alg_q, exp, gm, i, log, np):
    _pi = alg_q.scalar(np.pi).named("pi", latex=r"\pi")
    _theta = _pi / 3

    _q = exp(i * _theta / 2)
    _b = log(_q).named("q_log", latex=r"q_{\log}")
    _q0 = exp(0.0 * _b)
    _q25 = exp(0.25 * _b)
    _q50 = exp(0.5 * _b)
    _q75 = exp(0.75 * _b)
    _q100 = exp(1.0 * _b)

    gm.md(rt"""
    {_q}

    {_b}

    {exp(_b)}

    **SLERP — interpolate from identity to $q$: **

    | $t$ | $\exp(t\,q_{{\log}})$ |
    |---:|:---|
    | 0 | {_q0} |
    | 0.25 | {_q25} |
    | 0.50 | {_q50} |
    | 0.75 | {_q75} |
    | 1 | {_q100} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Unit quaternion
    """)
    return


@app.cell
def _(gm, i, j, k, norm, unit):
    _q = (1 + 2 * i + 3 * j + 4 * k).named("q")

    gm.md(rt"""
    {_q}

    {norm(_q)}

    {unit(_q)}

    {norm(unit(_q))}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
