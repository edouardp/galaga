import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell(hide_code=True)
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_marimo")
    for _p in [_root, _gamo]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from galaga.facade import Algebra, exp, inverse, left_contraction
    import galaga_marimo as gm

    return Algebra, exp, gm, inverse, left_contraction, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Projectors in Geometric Algebra

    Projection is one of the places where geometric algebra is unusually clean.
    A single formula handles "drop onto this direction" and "drop into this plane"
    using the same geometric product machinery.

    For a vector $v$ and an invertible blade $B$, the projection into the
    subspace represented by $B$ is

    $$
    \operatorname{proj}_B(v) = (v \rfloor B) B^{-1},
    $$

    and the rejection is the complementary part

    $$
    \operatorname{rej}_B(v) = (v \wedge B) B^{-1}.
    $$

    Galaga 2 keeps these decompositions explicit instead of adding redundant
    core operations: projection is `left_contraction(v, B) * inverse(B)`, and
    rejection is `v - projection`.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), )
    e1, e2, e3 = alg.basis_vectors(expr=True)
    return e1, e2, e3


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Projection onto a Line

    Start with `e₁` and rotate it by a rotor. The resulting direction `a` defines
    the line. Projection keeps only the component of `v` parallel to that line;
    rejection keeps the perpendicular remainder.
    """)
    return


@app.cell
def _(mo):
    angle = mo.ui.slider(start=0, stop=180, step=1, value=30, label="line angle")
    vx = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=1.6, label="v_x")
    vy = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=1.1, label="v_y")
    vz = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=0.8, label="v_z")
    mo.vstack([angle, vx, vy, vz])
    return angle, vx, vy, vz


@app.cell(hide_code=True)
def _(angle, e1, e2, e3, exp, gm, inverse, left_contraction, np, vx, vy, vz):
    _theta = np.radians(angle.value)
    R = exp((-_theta / 2) * (e1 * e2)).named("R", latex="R")
    a = R * e1 * ~R
    v = (vx.value * e1 + vy.value * e2 + vz.value * e3).named("v")
    p = left_contraction(v, a) * inverse(a)
    r = v - p

    gm.md(rt"""
    Rotor defining the line:
    {R} = {R:value}

    {a} = {a:value}

    {v} = {v:value}

    Projection onto the line:
    {p} = {p:value}

    Rejection from the line:
    {r} = {r:value}

    Check:
    {p + r} = {(p + r):value}
    """)
    return R, a, p, r, v


@app.cell(hide_code=True)
def _(a, p, plt, r, v):
    _a = a.vector_part[:2]
    _v = v.vector_part[:2]
    _p = p.vector_part[:2]
    _r = r.vector_part[:2]

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.plot([-2.5 * _a[0], 2.5 * _a[0]], [-2.5 * _a[1], 2.5 * _a[1]], color="gray", alpha=0.5)
    _ax.quiver(0, 0, _v[0], _v[1], angles="xy", scale_units="xy", scale=1, color="black", width=0.012, label="v")
    _ax.quiver(0, 0, _p[0], _p[1], angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012, label="proj")
    _ax.quiver(_p[0], _p[1], _r[0], _r[1], angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012, label="rej")
    _ax.set_aspect("equal")
    _ax.set_xlim(-3, 3)
    _ax.set_ylim(-3, 3)
    _ax.set_title("Line projection and rejection in the x-y plane")
    _ax.grid(True, alpha=0.2)
    _ax.legend()
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Projection into a Plane

    Now start from a reference plane and rotate it with the same rotor. Projecting
    a 3D vector into that plane removes the normal component, while rejection
    isolates the normal part.
    """)
    return


@app.cell(hide_code=True)
def _(R, e1, e3, gm, inverse, left_contraction, v):
    B = R * (e1 ^ e3) * ~R
    p_plane = left_contraction(v, B) * inverse(B)
    r_plane = v - p_plane

    gm.md(rt"""
    Plane blade:
    {B} = {B:value}

    Projection into the plane:
    {p_plane} = {p_plane:value}

    Rejection from the plane:
    {r_plane} = {r_plane:value}

    Again:
    {p_plane + r_plane} = {(p_plane + r_plane):value}
    """)
    return p_plane, r_plane


@app.cell
def _(np, p_plane, plt, r_plane, v):
    _v = v.vector_part
    _p = p_plane.vector_part
    _r = r_plane.vector_part

    _fig = plt.figure(figsize=(7, 5))
    _ax = _fig.add_subplot(111, projection="3d")
    _xx, _yy = np.meshgrid(np.linspace(-2.5, 2.5, 2), np.linspace(-2.5, 2.5, 2))
    _zz = np.zeros_like(_xx)
    _ax.plot_surface(_xx, _yy, _zz, alpha=0.12, color="steelblue")
    _ax.quiver(0, 0, 0, _v[0], _v[1], _v[2], color="black", linewidth=2.5, arrow_length_ratio=0.08)
    _ax.quiver(0, 0, 0, _p[0], _p[1], _p[2], color="steelblue", linewidth=2.5, arrow_length_ratio=0.08)
    _ax.quiver(_p[0], _p[1], _p[2], _r[0], _r[1], _r[2], color="crimson", linewidth=2.5, arrow_length_ratio=0.08)
    _ax.set_xlim(-3, 3)
    _ax.set_ylim(-3, 3)
    _ax.set_zlim(-3, 3)
    _ax.set_box_aspect((1, 1, 1))
    _ax.set_title("Projection into the e₁∧e₂ plane")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why Named Projectors Matter

    In ordinary vector calculus, the line and plane formulas are usually taught as
    different tricks. In GA they are the same operation against different blades.

    That is the real payoff:

    - a **line** is a 1-blade
    - a **plane** is a 2-blade
    - projection and rejection work uniformly on either
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
