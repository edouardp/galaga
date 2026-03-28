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
    from galaga import Algebra, complement, dual, project, reflect, reject, undual, uncomplement
    import galaga_marimo as gm

    return (
        Algebra,
        complement,
        dual,
        gm,
        mo,
        project,
        reflect,
        reject,
        uncomplement,
        undual,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Duality and Subspaces

    Duality operations change how a subspace is represented. Projectors and
    reflections then act on those represented subspaces.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell
def _(
    complement,
    dual,
    e1,
    e2,
    e3,
    gm,
    project,
    reflect,
    reject,
    uncomplement,
    undual,
):
    B = (e1 ^ e2).name("B")
    v = (e1 + e2 + e3).name("v")
    gm.md(t"""
    {B} = {B.eval()}

    Dual of {B}: $\\quad$  {dual(B)} = {dual(B).eval()}

    Undual of Dual of {B}: $\\quad$ {undual(dual(B))} = {undual(dual(B)).eval()}

    Complement of {B}: $\\quad$  {complement(B)} = {complement(B).eval()}

    Uncomplement of Complement of {B}: $\\quad$ {uncomplement(complement(B))} = {uncomplement(complement(B)).eval()}

    Project {v} onto {B}: $\\quad$ {project(v, B)} = {project(v, B).eval()}

    Reject {v} onto {B}: $\\quad$ {reject(v, B)} = {reject(v, B).eval()}

    Reflect {v} in {e3}: $\\quad$ {reflect(v, e3)} = {reflect(v, e3).eval()}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
