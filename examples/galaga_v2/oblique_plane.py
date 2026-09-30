"""Explore a two-vector oblique Gram metric and its geometry."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga import Algebra, metric_inner_product, presets
    from galaga_anywidget import oblique2d

    return Algebra, gm, metric_inner_product, mo, oblique2d, presets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # An oblique Euclidean plane

    The basis vectors have unit length but need not be perpendicular. Choose
    their angle in degrees; the preset derives the Gram matrix from it. The
    geometric product then has both a scalar and a bivector part.
    """)
    return


@app.cell
def _(mo):
    angle_degrees = mo.ui.slider(
        start=15,
        stop=165,
        step=5,
        value=60,
        label="Angle between basis vectors (degrees)",
    )
    return (angle_degrees,)


@app.cell
def _(Algebra, angle_degrees, presets):
    oblique = Algebra(config=presets.oblique_plane(degrees=angle_degrees.value), expr=True)
    e1, e2 = oblique.basis_vectors()
    return e1, e2, oblique


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The stored metric

    In the ordered basis $(e_1,e_2)$, the matrix has ones on the diagonal
    and $\cos(\theta)$ off the diagonal. The algebra and its bilinear form
    table below display that metric directly.
    """)
    return


@app.cell
def _(oblique):
    oblique
    return


@app.cell
def _(oblique):
    oblique.bilinear_form_table()
    return


@app.cell
def _(e1, e2, metric_inner_product):
    inner = float(metric_inner_product(e1, e2))
    wedge = e1 ^ e2
    product = e1 * e2
    return inner, product, wedge


@app.cell
def _(gm, inner, product, wedge):
    gm.md(rt"""
    The metric gives $e_1\cdot e_2={inner:g}$. Galaga computes

    $$e_1e_2={product}={inner:g}+{wedge}.$$

    The bivector term is the oriented area swept out by the two basis
    directions. The scalar term records their nonzero inner product.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A geometric view

    The widget embeds this positive-definite Gram metric in a Euclidean
    drawing plane. Basis directions and vector arrows have the lengths and
    angles determined by the metric. A grade-two multivector is shown as an
    oriented parallelogram with its signed area. Scalars and mixed-grade
    multivectors are not drawn as ordinary arrows or regions.
    """)
    return


@app.cell
def _(e1, e2):
    sample_vector = (e1 + 0.5 * e2).named("u")
    sample_bivector = (1.5 * (e1 ^ e2)).named("A")
    return sample_bivector, sample_vector


@app.cell
def _(angle_degrees, mo, oblique, oblique2d, sample_bivector, sample_vector):
    plane_widget = mo.ui.anywidget(
        oblique2d(oblique, [sample_vector, sample_bivector], labels=["u", "A"])
    )

    mo.vstack([angle_degrees, plane_widget])
    return


@app.cell
def _(gm, sample_bivector, sample_vector):
    gm.md(rt"""
    Green arrow: ${sample_vector}$.<br/>
    Purple region: ${sample_bivector}$.<br/>
    The widget derives both from the algebra values and its Gram matrix.
    """)
    return


if __name__ == "__main__":
    app.run()
