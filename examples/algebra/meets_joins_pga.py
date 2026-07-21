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
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from galaga.facade import Algebra, DisplayPolicy, complement
    import galaga_marimo as gm

    return Algebra, DisplayPolicy, complement, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Meets and Joins in PGA

    In projective geometry, the outer product builds joins and complement tricks
    help move between primal and dual representations. This notebook gives a few
    small line/point examples.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy):
    pga = Algebra((1, 1, 1, 0), display=DisplayPolicy(content="full"))
    e1, e2, e3, e0 = pga.basis_vectors(expr=True)
    e123,_,_,_ = pga.basis_blades(3, expr=True)
    #e123 = (e1 ^ e2 ^ e3)
    E1 = (e2 ^ e3 ^ e0).named("E_1")
    E2 = (-e1 ^ e3 ^ e0).named("E_2")
    E3 = (e1 ^ e2 ^ e0).named("E_3")
    return E1, E2, E3, e0, e1, e123, e3, pga


@app.cell
def _(E1, E2, E3, e123, np):
    def point(x, y, z=0.0):
        return e123 + x * E1 + y * E2 + z * E3

    def coords(P):
        _P = P
        _w = _P.data[7]
        return np.array([_P.data[14] / _w, -_P.data[13] / _w, _P.data[11] / _w])

    return coords, point


@app.cell
def _(complement, gm, point):
    A = point(-1, 0).named("A")
    B = point(1, 1).named("B")
    C = point(-0.5, 1.5).named("C")
    line_ab = complement(A) ^ complement(B)
    line_bc = complement(B) ^ complement(C)
    gm.md(rt"""
    {A}

    {B}

    {C}

    Join of A and B: $\quad$
    {line_ab}

    Join of B and C: $\quad$
    {line_bc}
    """)
    return A, B, C


@app.cell
def _(A, B, C, coords, np, plt):
    _pts = np.array([coords(A), coords(B), coords(C)])
    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.plot(_pts[[0, 1], 0], _pts[[0, 1], 1], color="steelblue", linewidth=2.5)
    _ax.plot(_pts[[1, 2], 0], _pts[[1, 2], 1], color="crimson", linewidth=2.5)
    _ax.scatter(_pts[:, 0], _pts[:, 1], color="black")
    _ax.set_aspect("equal")
    _ax.set_xlim(-2, 2)
    _ax.set_ylim(-1, 2.5)
    _ax.grid(True, alpha=0.2)
    _ax.set_title("Joins of projective points")
    _fig.tight_layout()
    _fig
    return


@app.cell
def _(e0, e1, e3):
    (-e1 ^ e3 ^ e0)
    return


@app.cell
def _(e0, e1, e3):
    (-e1 ^ e3 ^ e0)
    return


@app.cell
def _(pga):
    pga.basis_blades(3,expr=True)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
