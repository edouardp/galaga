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
    from galaga import Algebra, DisplayPolicy, complement, dual, inverse, left_contraction, uncomplement, undual
    import galaga_marimo as gm

    return (
        Algebra,
        DisplayPolicy,
        complement,
        dual,
        gm,
        inverse,
        left_contraction,
        mo,
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
def _(Algebra, DisplayPolicy):
    alg = Algebra((1, 1, 1), display=DisplayPolicy(content="full"))
    e1, e2, e3 = alg.basis_vectors(expr=True)
    return e1, e2, e3


@app.cell
def _(
    complement,
    dual,
    e1,
    e2,
    e3,
    gm,
    inverse,
    left_contraction,
    uncomplement,
    undual,
):
    B = (e1 ^ e2).named("B")
    v = (e1 + e2 + e3).named("v")
    projection = left_contraction(v, B) * inverse(B)
    rejection = v - projection
    reflection = -e3 * v * inverse(e3)
    gm.md(rt"""
    {B}

    Dual of {B:name}: $\quad$  {dual(B)}

    Undual of Dual of {B:name}: $\quad$ {undual(dual(B))}

    Complement of {B:name}: $\quad$  {complement(B)}

    Uncomplement of Complement of {B:name}: $\quad$ {uncomplement(complement(B))}

    Project {v:name} onto {B:name}: $\quad$ {projection}

    Reject {v:name} onto {B:name}: $\quad$ {rejection}

    Reflect {v:name} in {e3}: $\quad$ {reflection}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
