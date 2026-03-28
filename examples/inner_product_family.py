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
    from galaga import (
        Algebra,
        doran_lasenby_inner,
        hestenes_inner,
        left_contraction,
        right_contraction,
        scalar_product,
    )
    import galaga_marimo as gm

    return (
        Algebra,
        doran_lasenby_inner,
        gm,
        hestenes_inner,
        left_contraction,
        mo,
        right_contraction,
        scalar_product,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Inner Product Family

    Geometric algebra has several inner-like products because different geometric
    tasks want different grade-selection rules. This notebook compares the named
    operations on the same operands.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell
def _(e1, e2, e3, gm):
    gm.md(t"""
    Basis vectors:

    {e1} = {e1.eval()}

    {e2} = {e2.eval()}

    {e3} = {e3.eval()}
    """)
    return


@app.cell
def _(
    doran_lasenby_inner,
    e1,
    e2,
    e3,
    gm,
    hestenes_inner,
    left_contraction,
    right_contraction,
    scalar_product,
):
    a = e1 + 2 * e2
    b = e2 + e3
    A = e1 * e2
    B = e2 * e3

    with gm.doc() as d:
        d.md(t"""
        Input vector pair:
        {a} = {a.eval()}

        {b} = {b.eval()}

        Input bivector pair:
        {A} = {A.eval()}

        {B} = {B.eval()}
        """)
        d.text("| Operation | On vectors | On bivectors |")
        d.line("|---|---|---|")
        _ops = [
            ("Doran-Lasenby", doran_lasenby_inner),
            ("Hestenes", hestenes_inner),
            ("Left contraction", left_contraction),
            ("Right contraction", right_contraction),
            ("Scalar product", scalar_product),
        ]
        for _label, _fn in _ops:
            d.line(
                f"| {_label} | ${_fn(a, b).latex()}$ | ${_fn(A, B).latex()}$ |"
            )
    d.render()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
