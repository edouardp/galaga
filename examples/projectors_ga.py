import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell(hide_code=True)
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "gamo")
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

    from ga import Algebra, exp, project, reject
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt, project, reject


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

    In this library those are the named functions `project(v, B)` and
    `reject(v, B)`.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
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
def _(angle, e1, e2, e3, exp, gm, np, project, reject, vx, vy, vz):
    _theta = np.radians(angle.value)
    R = exp((-_theta / 2) * (e1 * e2)).name(latex="R")
    a = R * e1 * ~R
    v = (vx.value * e1 + vy.value * e2 + vz.value * e3).name("v")
    p = project(v, a)
    r = reject(v, a)

    gm.md(t"""
    Rotor defining the line:
    {R} = {R.eval()}

    {a} = {a.eval()}

    {v} = {v.eval()}

    Projection onto the line:
    {p} = {p.eval()}

    Rejection from the line:
    {r} = {r.eval()}

    Check:
    {p + r} = {(p + r).eval()}
    """)
    return R, a, p, r, v


@app.cell(hide_code=True)
def _(a, p, plt, r, v):
    _a = a.eval().vector_part[:2]
    _v = v.eval().vector_part[:2]
    _p = p.eval().vector_part[:2]
    _r = r.eval().vector_part[:2]

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
def _(R, e1, e3, gm, project, reject, v):
    B = R * (e1 ^ e3) * ~R
    p_plane = project(v, B)
    r_plane = reject(v, B)

    gm.md(t"""
    Plane blade:
    {B} = {B.eval()}

    Projection into the plane:
    {p_plane} = {p_plane.eval()}

    Rejection from the plane:
    {r_plane} = {r_plane.eval()}

    Again:
    {p_plane + r_plane} = {(p_plane + r_plane).eval()}
    """)
    return p_plane, r_plane


@app.cell
def _(np, p_plane, plt, r_plane, v):
    _v = v.eval().vector_part
    _p = p_plane.eval().vector_part
    _r = r_plane.eval().vector_part

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
