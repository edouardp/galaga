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
    from galaga import Algebra, anticommutator, commutator, jordan_product, lie_bracket
    import galaga_marimo as gm

    return (
        Algebra,
        anticommutator,
        commutator,
        gm,
        jordan_product,
        lie_bracket,
        mo,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Commutator, Lie Bracket, and Jordan Product

    The geometric product splits naturally into symmetric and antisymmetric parts.
    These named operations expose that structure directly.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell
def _(anticommutator, commutator, e1, e2, e3, gm, jordan_product, lie_bracket):
    A = e1 ^ e2
    B = e2 ^ e3
    gm.md(t"""
    {A} = {A.eval()}

    {B} = {B.eval()}

    {commutator(A, B)} = {commutator(A, B).eval()}

    {anticommutator(A, B)} = {anticommutator(A, B).eval()}

    {lie_bracket(A, B)} = {lie_bracket(A, B).eval()}

    {jordan_product(A, B)} = {jordan_product(A, B).eval()}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
