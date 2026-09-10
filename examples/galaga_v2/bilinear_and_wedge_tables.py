"""Read Gram and exterior-product tables, then explore their relationship."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, presets, scalar_product

    return Algebra, DisplayPolicy, gm, mo, np, presets, scalar_product


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Reading bilinear-form and wedge-product tables

    A table lets us inspect how basis elements combine. We will learn to read
    two tables, use them to calculate with vectors, and see how they determine
    the geometric product. No matrix-representation background is needed.

    ## The bilinear form tells us how vectors pair

    A **bilinear form** is linear in each of its two arguments. In this
    notebook it is also symmetric. Once a basis is chosen, its entries form
    the **Gram matrix** $G_{ij}=e_i\cdot e_j$.

    Read row $i$, column $j$ as the pairing of those two basis vectors:
    diagonal entries are their squares, and off-diagonal entries are their
    mutual pairings. A zero pairing means orthogonality. Positive-definite
    forms describe ordinary Euclidean lengths and angles; other forms can
    give negative or zero squares to nonzero vectors.

    In three-dimensional Euclidean space the standard basis has unit squares
    and orthogonal pairs. The labelled table below shows precisely that.
    Grey `#bbbbbb` entries mark exact zeros.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, presets):
    euclidean = Algebra(config=presets.euclidean(3), display=DisplayPolicy(content="full"))
    euclidean.bilinear_form_table()
    return (euclidean,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Change one pairing

    Keep the same formal basis and vary $t=e_1\cdot e_3$, leaving all three
    squares equal to one. The symmetric entry $e_3\cdot e_1$ changes with it.
    This family remains positive definite for $|t|<1$, the slider's range.
    At $t=0$ our basis is orthonormal; otherwise it is oblique.

    For coordinate columns $\mathbf{a}$ and $\mathbf{b}$, bilinearity gives

    $$a\cdot b=\sum_{i,j}a_iG_{ij}b_j=\mathbf{a}^{\mathsf T}G\mathbf{b}.$$

    Try predicting the pairing of $a=2e_1+e_3$ and $b=e_1+e_2-e_3$ before
    moving the slider. The calculation below checks the coordinate formula
    against Galaga's scalar product.
    """)
    return


@app.cell
def _(mo):
    metric_slider = mo.ui.slider(start=-0.9, stop=0.9, step=0.1, value=0.5, label="Pairing t", show_value=True)
    metric_slider  # noqa: B018 - Marimo displays the cell's final expression.
    return (metric_slider,)


@app.cell
def _(Algebra, DisplayPolicy, metric_slider, np, scalar_product):
    pairing = metric_slider.value
    oblique = Algebra(
        gram=[[1, 0, pairing], [0, 1, 0], [pairing, 0, 1]],
        display=DisplayPolicy(content="full"),
    )
    e1, e2, e3 = oblique.basis_vectors(expr=True)
    vector_a = 2 * e1 + e3
    vector_b = e1 + e2 - e3
    coordinate_pairing = float(np.array([2, 0, 1]) @ oblique.gram @ np.array([1, 1, -1]))
    algebra_pairing = scalar_product(vector_a, vector_b)
    np.testing.assert_allclose(float(algebra_pairing), coordinate_pairing, atol=1e-12, rtol=0)
    return algebra_pairing, coordinate_pairing, e1, e3, oblique


@app.cell
def _(algebra_pairing, coordinate_pairing, gm, oblique):
    _table = oblique.bilinear_form_table()
    gm.md(rt"""
{_table:block}

Coordinate calculation: $a\cdot b={coordinate_pairing:g}$.

Computed algebra expression:

{algebra_pairing:block}

A Gram matrix represents a bilinear form on **vectors**. It is not a
matrix representation of multiplication by an arbitrary multivector.
""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The wedge product records oriented span

    Two vectors wedge to a bivector, representing their oriented area element.
    Its coefficients describe the oriented parallelogram; measuring its area
    also requires a metric. The wedge is bilinear and alternating:

    $$a\wedge a=0,\qquad a\wedge b=-b\wedge a.$$

    Read a wedge-table cell as **row wedged with column**. All nonzero entries
    in the vector-only table are bivectors. With a fixed exterior basis,
    their coefficients do not depend on the metric: move the slider and
    compare this table with the bilinear table above.
    """)
    return


@app.cell
def _(e1, e3, euclidean, gm, np, oblique, scalar_product):
    wedge_table = oblique.wedge_product_table(colour=True)
    wedge = e1 ^ e3
    geometric = e1 * e3
    symmetric_part = scalar_product(e1, e3)
    np.testing.assert_allclose(geometric.data, (symmetric_part + wedge).data, atol=1e-12, rtol=0)
    assert wedge_table.latex() == euclidean.wedge_product_table(color=True).latex()
    gm.md(rt"""
{wedge_table:block}

## The geometric product combines both tables

For vectors, $ab=a\cdot b+a\wedge b$. Equivalently,

$$a\cdot b=\tfrac12(ab+ba),\qquad a\wedge b=\tfrac12(ab-ba).$$

Here the computed geometric product and exterior product are:

{geometric:block}

{wedge:block}

The scalar part follows the slider. The exterior blade stays the same.
In an oblique basis, $e_1e_3$ therefore need not equal $e_1\wedge e_3$.
""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Include every basis blade

    `full=True` includes the scalar $1$, vectors, bivectors, and higher blades,
    grouped by grade. In three dimensions there are $2^3=8$ basis blades,
    so we can comfortably read the full $8\times8$ table.

    The scalar is the wedge identity: $1\wedge A=A\wedge1=A$.
    Repeating a basis-vector factor gives zero. Otherwise grades add.
    `colour=True` (or `color=True`) colours the result by grade; zeros stay
    grey. Without that option, nonzero entries use the normal text colour.

    For homogeneous elements of grades $p$ and $q$,
    $A_p\wedge B_q=(-1)^{pq}B_q\wedge A_p$. A vector and a bivector thus
    commute under the wedge. Locate $e_1\wedge e_{23}$ and
    $e_{23}\wedge e_1$ in the table and compare them below.
    """)
    return


@app.cell
def _(euclidean, gm):
    full_wedge = euclidean.wedge_product_table(full=True, colour=True)
    _x, _y, _z = euclidean.basis_vectors(expr=True)
    vector_bivector = _x ^ (_y ^ _z)
    bivector_vector = (_y ^ _z) ^ _x
    assert vector_bivector == bivector_vector
    gm.md(rt"""
{full_wedge:block}

{vector_bivector:block}

{bivector_vector:block}
""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Null vectors and degenerate forms

    A nonzero **null vector** has square zero. A **degenerate form** has a
    nonzero vector orthogonal to every vector: its Gram matrix has deficient
    rank. These are different conditions.

    PGA has a null basis vector whose entire Gram row is zero. CGA has two
    null basis vectors with a nonzero mutual pairing. Inspect their tables
    and computed ranks below: CGA's null pair does not make its form
    degenerate.
    """)
    return


@app.cell
def _(Algebra, gm, np, presets, scalar_product):
    pga = Algebra(config=presets.pga())
    cga = Algebra(config=presets.cga())
    pga_rank = int(np.linalg.matrix_rank(pga.gram))
    cga_rank = int(np.linalg.matrix_rank(cga.gram))
    _o, _infinity = cga.basis_vectors()[-2:]
    null_origin_square = scalar_product(_o, _o)
    null_infinity_square = scalar_product(_infinity, _infinity)
    null_pair_product = scalar_product(_o, _infinity)
    _pga_table, _cga_table = pga.bilinear_form_table(), cga.bilinear_form_table()
    gm.md(rt"""
**PGA:** rank {pga_rank:g} of {pga.n:g}.

{_pga_table:block}

**CGA:** rank {cga_rank:g} of {cga.n:g}.

{_cga_table:block}

CGA Summary
$$
e_o^2 = {null_origin_square!s},\quad e_\infty^2={null_infinity_square!s},\quad e_o\cdot e_\infty={null_pair_product!s}.
$$
""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Explore other conventions

    Choose a preset to compare its bilinear and wedge tables. STA uses a
    Lorentzian metric; its signed sigma and pseudovector aliases illustrate
    how names can encode signs. RGA and PGA share a metric but use different
    conventions and model roles. Such changes can affect displayed labels
    and signs without changing the underlying exterior product.

    `presets.complex()` uses the even subalgebra of Euclidean $\mathrm{Cl}(2,0)$:
    its Gram table describes the two real vector generators. The complex
    imaginary unit is their bivector, whose geometric square is $-1$.

    Full tables contain $4^n$ entries: five-dimensional CGA produces a
    $32\times32$ table. Enable the full-table option when you want that detail.
    """)
    return


@app.cell
def _(mo):
    geometry_selector = mo.ui.dropdown(
        options=["Euclidean", "STA", "PGA", "CGA", "RGA", "Complex"],
        value="STA",
        label="Geometry",
    )
    full_toggle = mo.ui.checkbox(value=False, label="Show all basis blades (can be wide)")
    mo.hstack([geometry_selector, full_toggle])
    return full_toggle, geometry_selector


@app.cell
def _(Algebra, full_toggle, geometry_selector, gm, presets):
    _choices = {
        "Euclidean": presets.euclidean(),
        "STA": presets.sta(sigmas=True, pseudovectors=True),
        "PGA": presets.pga(),
        "CGA": presets.cga(),
        "RGA": presets.rga(),
        "Complex": presets.complex(),
    }
    selected_algebra = Algebra(config=_choices[geometry_selector.value])
    _bilinear = selected_algebra.bilinear_form_table()
    selected_wedge = selected_algebra.wedge_product_table(full=full_toggle.value, colour=True)
    gm.md(rt"""
{_bilinear:block}

{selected_wedge:block}
""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Try it yourself

    - Set the pairing to zero, then to a negative value. Predict which table
      entries change and which terms appear in $e_1e_3$.
    - Find a zero wedge between two nonzero blades that share a vector factor.
    - Explain why a vector's wedge with itself always vanishes even when its
      geometric square is nonzero.
    - In the complex preset, compare the bivector's wedge square with its
      geometric square. Which product reproduces multiplication by $i$?

    Continue with [compact matrices in an oblique basis](../matrix/general_gram_compact_foundations.py)
    or [CGA from its Gram matrix](../matrix/cga_via_gram_matrix.py).
    For independent vocabulary choices, see [preset namespaces](preset_namespaces.py).
    """)
    return


if __name__ == "__main__":
    app.run()
