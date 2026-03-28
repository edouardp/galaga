import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "galaga_marimo")
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

    from galaga import Algebra, grade
    import galaga_marimo as gm

    return Algebra, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Null Geometry in STA

    Null vectors sit on the light cone: they are nonzero vectors whose square is
    zero. They are central to relativity and electromagnetism because light rays
    and vacuum wave directions are null.
    """)
    return


@app.cell
def _(Algebra):
    sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
    g0, g1, g2, g3 = sta.basis_vectors(lazy=True)
    return g0, g1


@app.cell(hide_code=True)
def _(g0, g1, gm):
    k_plus = g0 + g1
    k_minus = g0 - g1
    gm.md(t"""
    ## Basic Null Vectors

    {k_plus} = {k_plus.eval()}

    {k_minus} = {k_minus.eval()}

    {(k_plus * k_plus)} = {(k_plus * k_plus).eval()}

    {(k_minus * k_minus)} = {(k_minus * k_minus).eval()}
    """)
    return


@app.cell
def _(mo):
    rapidity = mo.ui.slider(start=0.0, stop=3.0, step=0.02, value=0.8, label="observer rapidity")
    rapidity
    return (rapidity,)


@app.cell(hide_code=True)
def _(gm, np, rapidity):
    _phi = rapidity.value
    _future = np.array([np.cosh(_phi), np.sinh(_phi)])
    gm.md(t"""
    ## Light Cone and Observers

    A boosted timelike observer has components

    $$
    (\\cosh \\varphi, \\sinh \\varphi) = ({_future[0]:.6f}, {_future[1]:.6f})
    $$

    Null directions remain on the cone under boosts, which is why light speed is
    invariant.
    """)
    return


@app.cell
def _(np, plt, rapidity):
    _phi = rapidity.value
    _fig, _ax = plt.subplots(figsize=(6.5, 6.5))
    _x = np.linspace(-2.2, 2.2, 300)
    _ax.plot(_x, _x, "k--", alpha=0.35)
    _ax.plot(_x, -_x, "k--", alpha=0.35)
    _ax.quiver(0, 0, 0, 1.0, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012)
    _ax.quiver(0, 0, np.sinh(_phi), np.cosh(_phi), angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012)
    _ax.set_aspect("equal")
    _ax.set_xlim(-2.2, 2.2)
    _ax.set_ylim(-2.2, 2.2)
    _ax.set_xlabel("$x$")
    _ax.set_ylabel("$t$")
    _ax.set_title("Null directions and timelike observers")
    _ax.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
