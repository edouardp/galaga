import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "galaga_marimo")
    for _p in [_root, _gamo]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _():
    import marimo as mo
    from ga import Algebra, inverse, norm, squared, unit
    import galaga_marimo as gm

    return Algebra, gm, inverse, mo, norm, squared, unit


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
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2


@app.cell
def _(e1, e2, gm, inverse, norm, squared, unit):
    v = 3 * e1 + 4 * e2
    B = e1 ^ e2
    gm.md(t"""
    {v} = {v.eval()}

    {squared(v)} = {squared(v).eval()}

    {norm(v)} = {norm(v).eval():.1f}

    {unit(v)} = {unit(v).eval()}

    {inverse(v)} = {inverse(v).eval()}

    {B} = {B.eval()}

    {squared(B)} = {squared(B).eval()}

    {norm(B)} = {norm(B).eval():.1f}

    {unit(B)} = {unit(B).eval()}

    {inverse(B)} = {inverse(B).eval()}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
