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
    from galaga.facade import Algebra, DisplayPolicy, half_anticommutator, half_commutator, jordan_product, lie_bracket
    import galaga_marimo as gm

    return Algebra, DisplayPolicy, gm, half_anticommutator, half_commutator, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Commutator, Lie Bracket, and Jordan Product

    The geometric product splits naturally into symmetric and antisymmetric parts.
    These named operations expose that structure directly.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy):
    alg = Algebra((1, 1, 1), display=DisplayPolicy(content="full"))
    e1, e2, e3 = alg.basis_vectors(expr=True)
    return e1, e2, e3


@app.cell
def _(e1, e2, e3, gm, half_anticommutator, half_commutator):
    A = (e1 ^ e2).named("A")
    B = e2 ^ e3
    gm.md(rt"""
    {A}

    {B}

    {half_commutator(A, B)}

    {half_anticommutator(A, B)}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
