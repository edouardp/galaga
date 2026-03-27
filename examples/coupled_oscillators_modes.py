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

    from ga import Algebra, grade, norm, unit
    import galaga_marimo as gm

    return Algebra, gm, mo, np, plt, unit


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Coupled Oscillators and Normal Modes

    Two coupled oscillators are a clean example of how geometric algebra can treat
    configuration space itself as a vector space. The normal modes are just a new
    orthonormal basis in that space.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1), repr_unicode=True)
    e1, e2 = alg.basis_vectors(lazy=True)
    return e1, e2


@app.cell
def _(e1, e2, gm, unit):
    symmetric = unit(e1 + e2).name("u₊", latex=r"u_+")
    antisymmetric = unit(e1 - e2).name("u₋", latex=r"u_-")

    gm.md(t"""
    ## Mode Basis

    {symmetric} = {symmetric.eval()}

    {antisymmetric} = {antisymmetric.eval()}

    The in-phase and out-of-phase motions are just the rotated basis vectors of
    configuration space.
    """)
    return antisymmetric, symmetric


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Decompose the Initial Displacement

    Any displacement vector `q = x₁ e₁ + x₂ e₂` can be expanded in the modal basis.
    The time evolution then becomes two uncoupled cosine motions with different
    frequencies.
    """)
    return


@app.cell
def _(mo):
    x1 = mo.ui.slider(start=-2.0, stop=2.0, step=0.05, value=1.0, label="initial x₁")
    x2 = mo.ui.slider(start=-2.0, stop=2.0, step=0.05, value=0.3, label="initial x₂")
    w_plus = mo.ui.slider(start=0.2, stop=3.0, step=0.05, value=1.0, label="ω₊")
    w_minus = mo.ui.slider(start=0.2, stop=3.0, step=0.05, value=1.8, label="ω₋")
    time = mo.ui.slider(start=0.0, stop=20.0, step=0.05, value=3.2, label="time t")
    mo.vstack([x1, x2, w_plus, w_minus, time])
    return time, w_minus, w_plus, x1, x2


@app.cell
def _(antisymmetric, e1, e2, gm, np, symmetric, time, w_minus, w_plus, x1, x2):
    q0 = (x1.value * e1 + x2.value * e2).name(latex=r"q_0")
    a_plus = ((q0 * symmetric).eval()).scalar_part
    a_minus = ((q0 * antisymmetric).eval()).scalar_part
    qp = (a_plus * np.cos(w_plus.value * time.value) * symmetric).name(latex=r"q_+(t)")
    qm = (a_minus * np.cos(w_minus.value * time.value) * antisymmetric).name(latex=r"q_-(t)")
    qt = (qp + qm).name(latex=r"q(t)")

    gm.md(t"""
    {q0} = {q0.eval()}

    Mode amplitude along {symmetric}: {a_plus:.4f}

    Mode amplitude along {antisymmetric}: {a_minus:.4f}

    {qp} = {qp.eval()}

    {qm} = {qm.eval()}

    {qt} = {qt.eval()}
    """)
    return a_minus, a_plus


@app.cell
def _(
    a_minus,
    a_plus,
    antisymmetric,
    np,
    plt,
    symmetric,
    time,
    w_minus,
    w_plus,
):
    _times = np.linspace(0, 20, 500)
    _q = np.array([
        (
            a_plus * np.cos(w_plus.value * _t) * symmetric.eval().vector_part[:2]
            + a_minus * np.cos(w_minus.value * _t) * antisymmetric.eval().vector_part[:2]
        )
        for _t in _times
    ])
    _current = (
        a_plus * np.cos(w_plus.value * time.value) * symmetric.eval().vector_part[:2]
        + a_minus * np.cos(w_minus.value * time.value) * antisymmetric.eval().vector_part[:2]
    )

    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 4))
    _ax1.plot(_times, _q[:, 0], color="crimson", label=r"$x_1(t)$")
    _ax1.plot(_times, _q[:, 1], color="steelblue", label=r"$x_2(t)$")
    _ax1.axvline(time.value, color="black", alpha=0.3)
    _ax1.set_xlabel("time")
    _ax1.set_ylabel("displacement")
    _ax1.set_title("Oscillator coordinates")
    _ax1.grid(True, alpha=0.2)
    _ax1.legend()

    _ax2.plot(_q[:, 0], _q[:, 1], color="darkorange", linewidth=2)
    _ax2.plot(_current[0], _current[1], "ko", ms=8)
    _ax2.set_xlabel(r"$x_1$")
    _ax2.set_ylabel(r"$x_2$")
    _ax2.set_title("Configuration-space trajectory")
    _ax2.set_aspect("equal")
    _ax2.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
