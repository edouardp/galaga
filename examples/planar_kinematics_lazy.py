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
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from ga import Algebra, exp
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Planar Kinematics with Rotors

    A rigid body's orientation in the plane is a rotor. Once the state is written
    in GA form, sweeping the angle parameter generates the full motion history with
    very little bookkeeping.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1), repr_unicode=True)
    e1, e2 = alg.basis_vectors(lazy=True)
    return e1, e2


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Rotor State

    In the plane, the bivector `e₁e₂` squares to `-1`, so its exponential
    generates ordinary circular motion.
    """)
    return


@app.cell
def _(mo):
    angle = mo.ui.slider(start=0, stop=360, step=1, value=40, label="body angle")
    omega = mo.ui.slider(start=0.1, stop=3.0, step=0.05, value=1.2, label="angular speed")
    mo.vstack([angle, omega])
    return angle, omega


@app.cell
def _(angle, e1, e2, exp, gm, np):
    _theta = np.radians(angle.value)
    B = (e1 * e2).name("B", latex=r"e_1 e_2")
    R = exp((-_theta / 2) * B).name("R")
    arm = (1.6 * e1 + 0.6 * e2).name("r")
    rotated_arm = (R * arm * ~R).name(latex=r"r'")

    gm.md(t"""
    {B} = {B.eval()}

    {R} = {R.eval()}

    {arm} = {arm.eval()}

    {rotated_arm} = {rotated_arm.eval()}
    """)
    return arm, rotated_arm


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Motion History

    Treat the body-fixed point `r` as attached to the rotor and sample across
    time. This produces the trajectory as a family of evaluated sandwich products.
    """)
    return


@app.cell
def _(arm, e1, e2, exp, np, omega, plt, rotated_arm):
    _w = omega.value
    _times = np.linspace(0, 2 * np.pi / _w, 240)
    _pts = []
    for _t in _times:
        _R = exp((-_w * _t / 2) * (e1.eval() * e2.eval()))
        _v = (_R * arm.eval() * ~_R)
        _pts.append(_v.vector_part[:2])
    _pts = np.array(_pts)
    _current = rotated_arm.eval().vector_part[:2]

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.plot(_pts[:, 0], _pts[:, 1], color="steelblue", linewidth=2, label="tip trajectory")
    _ax.plot([0, _current[0]], [0, _current[1]], color="crimson", linewidth=2.5, label="current arm")
    _ax.scatter([_current[0]], [_current[1]], color="crimson", s=50)
    _ax.set_aspect("equal")
    _ax.grid(True, alpha=0.2)
    _ax.set_xlim(-2.2, 2.2)
    _ax.set_ylim(-2.2, 2.2)
    _ax.set_title(f"Rigid rotation with angular speed ω = {_w:.2f}")
    _ax.legend()
    _fig.tight_layout()
    _fig


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Angular Velocity as the Rotor Generator

    The bivector generator is the algebraic angular velocity. The notebook keeps
    that generator visible instead of hiding it behind matrices or complex numbers.
    """)
    return


@app.cell
def _(e1, e2, gm, omega):
    generator = (omega.value * (e1 * e2)).name(latex=r"\Omega")
    gm.md(t"""
    {generator} = {generator.eval()}

    This is the planar angular-velocity bivector driving the motion.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
