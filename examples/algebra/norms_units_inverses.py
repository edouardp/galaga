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
    from galaga.facade import Algebra, DisplayPolicy, inverse, norm, squared, unit
    import galaga_marimo as gm

    return Algebra, DisplayPolicy, gm, inverse, mo, norm, squared, unit


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Norms, Units, and Inverses

    These operations answer related but different questions:

    - `squared(x)` keeps the algebraic product
    - `norm(x)` returns a magnitude
    - `unit(x)` normalizes
    - `inverse(x)` solves for the multiplicative inverse when it exists
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy):
    alg = Algebra((1, 1, 1), display=DisplayPolicy(content="full"))
    e1, e2, e3 = alg.basis_vectors(expr=True)
    return e1, e2


@app.cell
def _(e1, e2, gm, inverse, norm, squared, unit):
    v = (3 * e1 + 4 * e2).named("v")
    B = (e1 ^ e2).named("B")

    gm.md(rt"""
    {v}

    {squared(v)}

    {norm(v)}

    {unit(v)}

    {inverse(v)}

    {B}

    {squared(B)}

    {norm(B)}

    {unit(B)}

    {inverse(B)}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
