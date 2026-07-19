import marimo

__generated_with = "0.21.1"
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
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from galaga.facade import Algebra, exp, norm, sandwich, unit
    import galaga_marimo as gm

    return Algebra, exp, gm, mo, norm, np, plt, sandwich, unit


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Rotations from Bivectors

    Rotations are exponentials of planes, applied by conjugation. This notebook
    shows the full chain from spanning vectors to a bivector generator, then to
    a rotor, then to the sandwich action on a vector.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1), )
    e1, e2 = alg.basis_vectors(expr=True)
    return alg, e1, e2


@app.cell
def _(mo):
    opening_deg = mo.ui.slider(start=10, stop=170, step=1, value=50, label="opening angle between a and b")
    rotation_deg = mo.ui.slider(start=0, stop=180, step=1, value=60, label="target rotation angle")
    vector_deg = mo.ui.slider(start=0, stop=180, step=1, value=20, label="input vector angle")
    generator_mode = mo.ui.dropdown(
        options=["unit bivector", "raw wedge"],
        value="unit bivector",
        label="generator",
    )
    mo.vstack([opening_deg, rotation_deg, vector_deg, generator_mode])
    return generator_mode, opening_deg, rotation_deg, vector_deg


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Domain Grounding

    A planar rotation should preserve vector length while changing only the
    direction by the chosen angle. The spanning pair $a, b$ defines the plane,
    but the rotation angle should come from the user control, not from the
    accidental area of $a \wedge b$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## GA Formulation

    We separate the roles carefully:

    - vectors $a, b$ span the plane
    - the bivector $B = a \wedge b$ is the plane object
    - the unit bivector $\widehat{B}$ is the rotation generator
    - the rotor $R = e^{-\theta \widehat{B} / 2}$ is the operator
    - the sandwich $v' = R v \tilde{R}$ is the action
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Minimal Math

    Two unit vectors with opening angle $\phi$ satisfy

    $$a \wedge b = \sin(\phi) e_{12}.$$

    That means the raw wedge carries both plane information and area scale. If
    we exponentiate the raw wedge directly, the effective rotation angle becomes
    $\theta \sin(\phi)$ instead of $\theta$.
    """)
    return


@app.cell
def _(
    alg,
    e1,
    e2,
    exp,
    generator_mode,
    np,
    opening_deg,
    rotation_deg,
    sandwich,
    unit,
    vector_deg,
):
    _phi = np.radians(opening_deg.value)
    _theta = alg.scalar(np.radians(rotation_deg.value)).named(r"\theta", latex=r"\theta")
    _alpha = np.radians(vector_deg.value)

    a = (1.0 * e1).named("a")
    b = (np.cos(_phi) * e1 + np.sin(_phi) * e2).named("b")
    B_raw = (a ^ b).named(r"a \wedge b", latex=r"a \wedge b")
    B_unit = unit(B_raw).named(r"\widehat{B}", latex=r"\widehat{B}")
    generator = B_unit if generator_mode.value == "unit bivector" else B_raw
    R = exp((-_theta / 2) * generator).named("R")
    v = (np.cos(_alpha) * e1 + np.sin(_alpha) * e2).named("v")
    v_rot = sandwich(R, v).named(r"v'", latex=r"v'")
    return B_raw, B_unit, R, a, b, generator, v, v_rot


@app.cell(hide_code=True)
def _(B_raw, B_unit, R, a, b, generator, gm, norm, rotation_deg, v, v_rot):
    gm.md(rt"""
    ## Code Layer

    {a} = {a:value}

    {b} = {b:value}

    {B_raw} = {B_raw:value}

    {B_unit} = {B_unit:value}

    Generator used in the exponential:

    {generator} = {generator:value}

    {R} = {R:value}

    {v} = {v:value}

    {v_rot} = {v_rot:value}

    Length check:

    {norm(v):.3f} $\\rightarrow$ {norm(v_rot):.3f}

    Requested angle: ${rotation_deg.value:.0f}^\\circ$
    """)
    return


@app.cell(hide_code=True)
def _(
    B_raw,
    generator_mode,
    gm,
    norm,
    np,
    opening_deg,
    rotation_deg,
    v,
    v_rot,
):
    _input = v.vector_part[:2]
    _output = v_rot.vector_part[:2]
    _input_angle = np.degrees(np.arctan2(_input[1], _input[0]))
    _output_angle = np.degrees(np.arctan2(_output[1], _output[0]))
    _actual_rotation = (_output_angle - _input_angle) % 360
    _raw_scale = norm(B_raw)
    _predicted_rotation = (
        rotation_deg.value if generator_mode.value == "unit bivector" else rotation_deg.value * _raw_scale
    )

    gm.md(rt"""
    ## Validation

    The wedge magnitude is {_raw_scale:.3f}, which matches \\sin({opening_deg.value:.0f}$^\\circ$).

    Predicted rotation from the chosen generator: {_predicted_rotation:.2f}$^\\circ$

    Measured rotation from the sandwich action: ${_actual_rotation:.2f}^\\circ$

    This is the key invariant story:

    - norm is preserved by the rotor sandwich
    - the unit bivector makes the angle parameter mean exactly what it says
    - the raw wedge is a useful plane object, but a poor generator when its magnitude is not one
    """)
    return


@app.cell
def _(a, b, plt, v, v_rot):
    _a = a.vector_part[:2]
    _b = b.vector_part[:2]
    _v = v.vector_part[:2]
    _v_rot = v_rot.vector_part[:2]

    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.quiver(0, 0, _a[0], _a[1], angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.010)
    _ax.quiver(0, 0, _b[0], _b[1], angles="xy", scale_units="xy", scale=1, color="darkorange", width=0.010)
    _ax.quiver(0, 0, _v[0], _v[1], angles="xy", scale_units="xy", scale=1, color="black", width=0.012)
    _ax.quiver(
        0,
        0,
        _v_rot[0],
        _v_rot[1],
        angles="xy",
        scale_units="xy",
        scale=1,
        color="crimson",
        width=0.012,
    )
    _ax.text(_a[0] + 0.05, _a[1] + 0.05, "a", color="steelblue")
    _ax.text(_b[0] + 0.05, _b[1] + 0.05, "b", color="darkorange")
    _ax.text(_v[0] + 0.05, _v[1] + 0.05, "v", color="black")
    _ax.text(_v_rot[0] + 0.05, _v_rot[1] + 0.05, "v'", color="crimson")
    _ax.set_aspect("equal")
    _ax.set_xlim(-1.4, 1.4)
    _ax.set_ylim(-1.4, 1.4)
    _ax.grid(True, alpha=0.2)
    _ax.set_title("Plane vectors, bivector generator, and rotated vector")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Domain Check

    The picture matches the intended behaviour: the rotor changes direction
    while preserving length. The only time the angle looks wrong is when we use
    the raw wedge as if it were already a unit generator.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
