import marimo

__generated_with = "0.23.14"
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

    from galaga import Algebra, DisplayPolicy, grade, p_sta
    import galaga_marimo as gm

    return Algebra, DisplayPolicy, gm, grade, mo, np, p_sta, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Electromagnetic Waves in STA

    A plane electromagnetic wave is a particularly clean STA object: the electric
    and magnetic fields sit inside one bivector, and for a vacuum plane wave the
    invariant square collapses to zero.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, p_sta):
    sta = Algebra(config=p_sta(),display=DisplayPolicy(content="full"))
    g0, g1, g2, g3 = sta.basis_vectors(expr=True)
    I = sta.I
    return g0, g1, g2, g3


@app.cell
def _(mo):
    amplitude = mo.ui.slider(start=0.2, stop=2.0, step=0.05, value=1.0, label="field amplitude")
    phase = mo.ui.slider(start=0.0, stop=2 * 3.14159, step=0.05, value=0.0, label="phase")
    mo.vstack([amplitude, phase])
    return amplitude, phase


@app.cell(hide_code=True)
def _(amplitude, g0, g1, g2, g3, gm, grade, np, phase):
    field_amplitude = amplitude.value * np.cos(phase.value)
    E = (field_amplitude * (g1 * g0)).named("E")
    B = (field_amplitude * (g2 * g3)).named("B")
    F = E + B
    F2 = F * F

    gm.md(rt"""
    ## Plane-Wave Field

    {E}

    {B}

    {F}

    {F2}

    Scalar invariant {grade(F2, 0)}

    Pseudoscalar invariant {grade(F2, 4)}

    For this wave both invariants vanish, which is the STA signature of a null field.
    """)
    return (field_amplitude,)


@app.cell
def _(field_amplitude, np, phase, plt):
    _xs = np.linspace(0, 2 * np.pi, 300)
    _field = field_amplitude * np.cos(_xs - phase.value)

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(_xs, _field, color="crimson", linewidth=2.5, label="E_x")
    _ax.plot(_xs, _field, color="steelblue", linewidth=2, linestyle="--", label="B_y")
    _ax.set_xlabel("phase coordinate")
    _ax.set_ylabel("field amplitude")
    _ax.set_title("Vacuum plane wave: E and B in phase")
    _ax.grid(True, alpha=0.2)
    _ax.legend()
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
