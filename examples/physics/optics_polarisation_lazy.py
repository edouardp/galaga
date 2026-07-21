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
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from galaga.facade import Algebra, exp, grade, norm, unit
    import galaga_marimo as gm

    return Algebra, exp, gm, grade, mo, norm, np, plt, unit


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Polarisation Optics with Expression-Provenance 2D GA

    A linear polariser is a projector. A wave plate is a rotor. Both fit naturally
    into the same algebra on the transverse plane.

    This notebook complements the existing polarisation demo by leaning harder on
    recorded expressions and by treating retarders as explicit rotors.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1), )
    e1, e2 = alg.basis_vectors(expr=True)
    return e1, e2


@app.cell
def _(e1, e2, exp, gm, np):
    H = e1.named("H")
    V = e2.named("V")
    D = (exp((-np.pi / 8) * (e1 * e2)) * e1 * exp((np.pi / 8) * (e1 * e2))).named("D")

    gm.md(rt"""
    ## Basis States

    {H} = {H:value}

    {V} = {V:value}

    {D} = {D:value}
    """)
    return H, V


@app.cell
def _(grade):
    def polarise(field, axis):
        return grade(field * axis, 0) * axis

    return (polarise,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Linear Polariser Chain

    The projector is

    $$
    P_a(E) = (E \cdot a)a.
    $$

    Because the axis is itself a blade, the recorded expression makes the
    geometry visible alongside its eager value.
    """)
    return


@app.cell
def _(mo):
    middle = mo.ui.slider(start=0, stop=90, step=1, value=35, label="middle polariser angle")
    middle
    return (middle,)


@app.cell
def _(H, V, e1, e2, gm, middle, norm, np, polarise, unit):
    _theta = np.radians(middle.value)
    M = unit(np.cos(_theta) * e1 + np.sin(_theta) * e2).named("M")
    E0 = H.named(r"E_0", latex=r"E_0")
    E1 = polarise(E0, M).named(r"E_1", latex=r"E_1")
    E2 = polarise(E1, V).named(r"E_2", latex=r"E_2")
    intensity = (norm(E2) ** 2)
    _intensity_value = float(intensity)

    gm.md(rt"""
    {M} = {M:value}

    {E1} = {E1:value}

    {E2} = {E2:value}

    Output intensity = {_intensity_value:.4f}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Half-Wave Plate as a Rotor

    A retarder rotates the field inside the transverse plane. In the GA picture it
    is a rotor sandwich exactly like a spatial rotation.
    """)
    return


@app.cell
def _(mo):
    plate = mo.ui.slider(start=0, stop=90, step=1, value=22, label="wave plate axis")
    plate
    return (plate,)


@app.cell
def _(H, e1, e2, exp, gm, np, plate):
    _alpha = np.radians(plate.value)
    axis = (np.cos(_alpha) * e1 + np.sin(_alpha) * e2).named("a")
    rotor = exp(-_alpha * (e1 * e2)).named("R")
    output = (rotor * H * ~rotor).named(r"E_{\mathrm{out}}", latex=r"E_{\mathrm{out}}")

    gm.md(rt"""
    {axis} = {axis:value}

    {rotor} = {rotor:value}

    {output} = {output:value}
    """)
    return


@app.cell
def _(H, V, e1, e2, exp, norm, np, plt, polarise, unit):
    _angles = np.linspace(0, 90, 181)
    _three_pol = []
    _plate_then_vertical = []
    for _deg in _angles:
        _rad = np.radians(_deg)
        _mid = unit(np.cos(_rad) * e1 + np.sin(_rad) * e2)
        _E2 = polarise(polarise(H, _mid), V)
        _three_pol.append((norm(_E2) ** 2))

        _R = exp(-_rad * (e1 * e2))
        _after_plate = _R * H * ~_R
        _plate_then_vertical.append((norm(polarise(_after_plate, V)) ** 2))

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(_angles, _three_pol, label="three polariser chain", color="steelblue")
    _ax.plot(_angles, _plate_then_vertical, label="wave plate then vertical polariser", color="crimson")
    _ax.set_xlabel("control angle (degrees)")
    _ax.set_ylabel("transmitted intensity")
    _ax.set_title("Projectors and rotors in the same 2D algebra")
    _ax.grid(True, alpha=0.2)
    _ax.legend()
    _fig.tight_layout()
    _fig

if __name__ == "__main__":
    app.run()
