"""Browse the rich displays for algebras, basis blades, and product tables."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, presets

    return Algebra, gm, mo, presets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # A gallery of algebra displays

    Galaga's values and tables have rich LaTeX displays. This notebook puts
    those displays side by side: an algebra's metric, its basis vectors and
    bivectors, the exterior product table, and bilinear form tables.

    The small examples below keep every table readable. A full bilinear table
    includes all exterior blades, so its size grows quickly with dimension.
    """)
    return


@app.cell
def _(Algebra, presets):
    cga = Algebra(config=presets.cga(spatial_dim=2))
    sta = Algebra(config=presets.sta())
    return cga, sta


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Algebra displays

    The CGA preset gives a four-vector conformal algebra for the plane.
    The STA preset gives one time direction and three spatial directions.
    Each object below displays the simplest exact description of its stored
    metric: a signature when possible, or an inline Gram matrix otherwise.
    """)
    return


@app.cell
def _(cga, gm):
    gm.md(t"""The conformal plane uses **{cga.n} basis vectors**.""")
    return


@app.cell
def _(sta):
    sta
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Basis vectors and grade-two blades

    `basis_vectors()` and `basis_blades(2)` return unpackable sequences in
    the algebra's display order. Their rich tables follow that same order,
    with each blade's zero-based sequence index beside it.
    """)
    return


@app.cell
def _(cga):
    cga.basis_vectors()
    return


@app.cell
def _(cga):
    cga.basis_blades(2)
    return


@app.cell
def _(sta):
    sta.basis_blades(2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Wedge product table

    A cell in `wedge_product_table()` reads as row wedged with column. For
    vectors, the table records the oriented exterior blades. The same table
    is useful across metrics because the exterior product is metric
    independent.
    """)
    return


@app.cell
def _(cga):
    cga.wedge_product_table(colour=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Bilinear form tables

    The vector table is the Gram matrix: entry $(i,j)$ is $e_i\cdot e_j$.
    The full table extends the metric-induced pairing to every exterior
    basis blade, including the scalar. Here a three-dimensional oblique
    metric makes the off-diagonal pairings apparent while keeping the full
    $8\times8$ table compact.
    """)
    return


@app.cell
def _(Algebra):
    oblique = Algebra(gram=[[1,    0.25, 0],
                            [0.25, 1,    0],
                            [0,    0,   -1]])
    return (oblique,)


@app.cell
def _(oblique):
    oblique.bilinear_form_table()
    return


@app.cell
def _(oblique):
    oblique.bilinear_form_table(full=True)
    return


if __name__ == "__main__":
    app.run()
