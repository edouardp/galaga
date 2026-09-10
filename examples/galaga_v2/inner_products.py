"""Choose inner-product operations by intent, grade rules, and metric."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga as ga
    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, presets

    return Algebra, DisplayPolicy, ga, gm, mo, np, presets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Which inner product do I mean?

    On vectors, familiar inner-product operations agree. On multivectors,
    several useful extensions answer different questions. Choosing one means
    deciding whether you want a scalar pairing, a directed grade reduction,
    or a grade-difference product, and how scalar inputs should behave.

    This lesson uses **Galaga's explicit definitions**. Terminology and
    contraction sign conventions vary between sources. The intended use and
    formula are more informative than the dot symbol alone.

    Start with [bilinear and wedge tables](bilinear_and_wedge_tables.py) for
    background on the Gram matrix and $ab=a\cdot b+a\wedge b$.

    ## Choose by intent

    | Operation | What you want to compute |
    | --- | --- |
    | `metric_inner_product(A, B)` | The scalar pairing induced by the vector metric on exterior blades; their self-pairing gives signed squared volume. |
    | `scalar_product(A, B)` | Exactly the scalar component of the geometric product $AB$, including its multiplication signs. |
    | `left_contraction(A, B)` | The part of $AB$ that reduces the grade of the right operand by the grade of the left. |
    | `right_contraction(A, B)` | The part of $AB$ that reduces the grade of the left operand by the grade of the right. |
    | `hestenes_inner(A, B)` | The lowest-grade part of each nonscalar homogeneous product, with scalar-input interactions excluded. |
    | `doran_lasenby_inner(A, B)` | The grade-difference product with scalar inputs retained as multiplication. |

    These describe mathematical intent, not interchangeable implementations
    of one operation. Contractions and grade-difference products can return
    vectors or higher grades, despite often being called inner products.

    ## Why authors make different choices

    **Hestenes develops both grade reduction and metric measurement.** His
    vector–multivector inner product lowers grade, while his separate
    reversion-based scalar pairing measures Euclidean magnitude. An author's
    name therefore does not identify a single pairing. See equations
    (1.9)–(1.10) and (1.38)–(1.40) in
    [Hestenes, *Synopsis of Geometric Algebra*](https://davidhestenes.net/geocalc/pdf/NFMPchapt1.pdf).

    **Doran organizes products by grade selection.** His thesis defines the
    lowest-grade homogeneous product and scalar extraction separately in
    equations (1.23) and (1.28). This motivates comparing their algebraic
    roles; Galaga's precise scalar-boundary rules are listed below. See
    [Doran, *Geometric Algebra and its Application*, §1.2](https://geometry.mrao.cam.ac.uk/wp-content/uploads/2015/02/DoranThesis.pdf).

    **Dorst and Mann emphasize subspace geometry.** Their contraction encodes
    the complementary subspace within a target blade after orthogonal
    projection, making a directional grade reduction useful. This is a
    geometric rationale for contractions, not an assertion that contractions
    are normalized projections. See their
    [computational-framework tutorial, “Inner product of blades”](https://staff.fnwi.uva.nl/l.dorst/cga-1.pdf).

    **Lengyel reserves inner product for metric measurement.** He advocates
    the compound-matrix extension of the vector metric and criticizes calling
    nonscalar products inner products. That terminology is his position;
    the grade-selected operations remain well-defined. His metric pairing
    agrees with reversion-based scalar pairing, not Galaga's bare scalar
    extraction. See
    [Lengyel's discussion of inner products](https://terathon.com/blog/poor-foundations-ga.html).

    The practical lesson is to translate formulas, including their reversals
    and scalar cases, rather than infer semantics from an author's name.
    Galaga's retained `dorst_inner` alias in particular is not a declaration
    that Dorst's preferred contraction and Doran–Lasenby are identical.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The exact grade rules

    Write $A_r$ and $B_s$ for homogeneous inputs of grades $r$ and $s$.
    Brackets $\langle X\rangle_k$ select grade $k$; reversion
    $\widetilde{B_s}=(-1)^{s(s-1)/2}B_s$ reverses the vector-factor order.

    | Operation | Result on $A_r,B_s$ |
    | --- | --- |
    | Scalar product | $\langle A_r B_s\rangle_0$ |
    | Metric inner product | $\langle A_r\widetilde{B_s}\rangle_0$ |
    | Left contraction | $\langle A_r B_s\rangle_{s-r}$ if $r\leq s$, otherwise zero |
    | Right contraction | $\langle A_r B_s\rangle_{r-s}$ if $r\geq s$, otherwise zero |
    | Hestenes | $\langle A_r B_s \rangle_{\lvert r-s\rvert}$ if $r,s>0$, otherwise zero |
    | Doran–Lasenby | $\langle A_r B_s\rangle_{\lvert r-s\rvert}$, including grade zero |

    All six extend **bilinearly** to mixed grades: split both inputs by grade,
    apply the rule to each pair, and add. Do not assign one grade to a mixed
    multivector. The two scalar-valued pairings receive contributions only
    from equal-grade pairs.

    In Galaga, `A | B` and the compatibility name `dorst_inner(A, B)` mean
    `doran_lasenby_inner(A, B)`. There is no ambiguous `inner_product` or `ip`
    dispatcher. We use functional notation below so each expression names
    the operation being performed; changing notation does not change results.
    """)
    return


@app.cell
def _(mo):
    metric_choice = mo.ui.dropdown(
        options=["Euclidean", "Oblique", "Lorentzian", "Degenerate"], value="Euclidean", label="Metric"
    )
    case_choice = mo.ui.dropdown(
        options=[
            "Vectors",
            "Vector–bivector",
            "Bivector–vector",
            "Bivectors",
            "Scalar–vector",
            "Scalars",
            "Mixed grades",
        ],
        value="Bivectors",
        label="Operands",
    )
    mo.hstack([metric_choice, case_choice])
    return case_choice, metric_choice


@app.cell
def _(Algebra, DisplayPolicy, ga, metric_choice, presets):
    _metrics = {
        "Euclidean": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        "Oblique": [[1, 0.5, 0], [0.5, 1, 0], [0, 0, 1]],
        "Lorentzian": [[1, 0, 0], [0, -1, 0], [0, 0, -1]],
        "Degenerate": [[1, 0, 0], [0, 0, 0], [0, 0, 1]],
    }
    algebra = Algebra(
        gram=_metrics[metric_choice.value],
        notation=presets.notation.functional(),
        display=DisplayPolicy(content="full"),
    )
    x, y, z = algebra.basis_vectors(expr=True)
    plane = (x ^ y).named("B")
    operations = {
        "scalar_product": ga.scalar_product,
        "metric_inner_product": ga.metric_inner_product,
        "left_contraction": ga.left_contraction,
        "right_contraction": ga.right_contraction,
        "hestenes_inner": ga.hestenes_inner,
        "doran_lasenby_inner": ga.doran_lasenby_inner,
    }
    samples = {
        "Vectors": (x, (x + y).named("v")),
        "Vector–bivector": (x, plane),
        "Bivector–vector": (plane, x),
        "Bivectors": (plane, plane),
        "Scalar–vector": (algebra.scalar(2).named("s"), x),
        "Scalars": (algebra.scalar(2).named("s"), algebra.scalar(3).named("t")),
        "Mixed grades": ((2 + x + plane).named("M"), (3 + x + plane).named("N")),
    }
    comparisons = {
        label: {name: operation(left, right) for name, operation in operations.items()}
        for label, (left, right) in samples.items()
    }
    return algebra, comparisons, samples


@app.cell
def _(algebra, case_choice, comparisons, gm, mo, samples):
    _left, _right = samples[case_choice.value]
    _results = comparisons[case_choice.value]
    mo.vstack(
        [
            algebra.bilinear_form_table(),
            gm.md(rt"""
    Left operand:

    {_left:block}

    Right operand:

    {_right:block}
    """),
            *[gm.md(rt"""{_value:block}""") for _value in _results.values()],
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Measuring blades versus extracting a scalar

    Choose **Bivectors**, initially in the Euclidean metric. The plane blade
    $B=e_1\wedge e_2$ has geometric square $-1$. `scalar_product(B, B)`
    reports that scalar component. `metric_inner_product(B, B)` pairs the
    blade with its reverse and gives $+1$, its squared Euclidean area.

    For decomposable grade-$r$ blades $A=a_1\wedge\cdots\wedge a_r$ and
    $B=b_1\wedge\cdots\wedge b_r$, the metric-induced pairing is

    $$\langle A\widetilde B\rangle_0=\det[a_i\cdot b_j].$$

    Use this pairing for metric measurements of blades. It is symmetric and
    positive definite on the exterior algebra when the vector metric is
    positive definite. With indefinite metrics it can be negative, and with
    degenerate metrics nonzero blades can pair to zero with everything.
    It is not universally a positive norm.

    Use scalar extraction when an identity specifically asks for
    $\langle AB\rangle_0$; silently inserting reversion changes that identity.
    On grade-$r$ pairs the two answers differ by $(-1)^{r(r-1)/2}$.
    Vectors agree, bivectors disagree in sign, and both scalar-valued
    pairings vanish between unequal grades.

    Switch to **Oblique**, **Lorentzian**, then **Degenerate** and check the
    computed determinant against the metric self-pairing below.
    """)
    return


@app.cell
def _(algebra, comparisons, gm, np):
    induced_square = float(np.linalg.det(algebra.gram[:2, :2]))
    _metric_square = comparisons["Bivectors"]["metric_inner_product"]
    np.testing.assert_allclose(float(_metric_square), induced_square, atol=1e-12, rtol=0)
    gm.md(rt"""
    The restricted Gram determinant is {induced_square:g}.

    {_metric_square:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Contractions reduce grade in a chosen direction

    Choose **Vector–bivector**. Left contraction inserts a vector into a plane
    blade and leaves a vector. Right contraction is zero because its grade
    inequality is not satisfied. Switch to **Bivector–vector** to see the
    roles reverse, including the sign caused by the order in the geometric
    product. In Euclidean space:

    $$e_1\mathbin{\rfloor}(e_1\wedge e_2)=e_2,\qquad
    (e_1\wedge e_2)\mathbin{\lfloor}e_1=-e_2.$$

    For vectors $a,b,c$, left contraction gives
    $a\mathbin{\rfloor}(b\wedge c)=(a\cdot b)c-(a\cdot c)b$.
    This makes contractions useful when extracting a metric-dependent
    direction from an oriented subspace. A contraction alone is not a
    normalized projection: projection formulas also need the appropriate
    inverse or scale factors and a suitable nondegenerate subspace.

    Equal-grade contractions return the scalar product, without reversion.
    Do not assume that contracting a blade with itself gives its positive
    squared size. For scalar inputs, left contraction permits scalar on the
    left, and right contraction permits scalar on the right; the permitted
    operation is ordinary scalar multiplication.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Grade-difference products: do scalars participate?

    Hestenes and Doran–Lasenby select grade $|r-s|$ without asking the caller
    to choose a contraction direction. Use them for formulas written with
    that grade-difference convention. They coincide whenever neither input
    has a scalar part, so vector-only examples cannot distinguish them.

    Hestenes excludes every pair involving grade zero. Choose it when scalar
    interactions should be absent from the inner part of your expression.
    Doran–Lasenby retains those interactions: choose it when the same product
    should extend scalar multiplication. Select **Scalar–vector**, then
    **Scalars**, to see the difference directly.

    For the literature's distinction between contractions and the Hestenes
    product, see Dorst, Fontijne, and Mann,
    [*Geometric Algebra for Computer Science*, Appendix B](https://www.oreilly.com/library/view/geometric-algebra-for/9780123749420/chapter-235.html).

    Select **Mixed grades** to see why this choice matters even when neither
    input is purely scalar. Every homogeneous pair contributes separately;
    some can cancel. A zero result does not by itself mean there were no
    contributing pairs.

    A useful identity for checking the bookkeeping is

    $$D(A,B)=L(A,B)+R(A,B)-S(A,B),$$

    where $D$ is Doran–Lasenby, $L,R$ are the contractions, and $S$ is scalar
    extraction. The subtraction removes the double counting of equal-grade
    contributions. This identity holds for mixed multivectors too.
    """)
    return


@app.cell
def _(comparisons, gm, np):
    _mixed = comparisons["Mixed grades"]
    reconstructed_inner = _mixed["left_contraction"] + _mixed["right_contraction"] - _mixed["scalar_product"]
    np.testing.assert_allclose(reconstructed_inner.data, _mixed["doran_lasenby_inner"].data, atol=1e-12, rtol=0)
    gm.md(rt"""
    For the mixed inputs $M$ and $N$, computing $L+R-S$ gives:

    {reconstructed_inner:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Related RGA operations: interior and antidot

    Galaga's `left_interior_product` and `right_interior_product` are
    Hodge-dual/antiwedge constructions used in its RGA model. They combine
    metric information with complementary geometry. They are not aliases
    for the two contractions above; even their signs can differ.

    Their exact constructions are
    `antiwedge(left_hodge_dual(A), B)` and
    `antiwedge(A, right_hodge_dual(B))`, respectively. Use them when following
    that RGA construction and its orientation conventions.

    `antidot_product` pairs using the complementary-compound antimetric and
    returns a **pseudoscalar**, rather than a scalar. It is useful in the RGA
    weight/antimetric construction. Degenerate PGA provides a revealing
    example: the null basis vector has zero metric self-pairing but nonzero
    antidot self-pairing. The outputs below are computed from the RGA metric.
    The source definitions are described in Lengyel's
    [RGA dot-product reference](https://rigidgeometricalgebra.org/wiki/index.php?title=Dot_products)
    and his discussion of
    [interior products and projection](https://terathon.com/blog/symmetries-pga.html).
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, ga, gm, mo, presets):
    rga = Algebra(config=presets.rga(), notation=presets.notation.functional(), display=DisplayPolicy(content="full"))
    _x, _y, _z, null_vector = rga.basis_vectors(expr=True)
    _plane = _x ^ _y
    related_results = {
        "left_interior": ga.left_interior_product(_x, _plane),
        "left_contraction": ga.left_contraction(_x, _plane),
        "right_interior": ga.right_interior_product(_plane, _x),
        "right_contraction": ga.right_contraction(_plane, _x),
        "metric": ga.metric_inner_product(null_vector, null_vector),
        "antidot": ga.antidot_product(null_vector, null_vector),
    }
    mo.vstack([gm.md(rt"""{_result:block}""") for _result in related_results.values()])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercises

    - Predict all six answers for two vectors, then verify them in each metric.
    - Explain why only one contraction survives for unequal pure grades.
    - Find the scalar interactions that distinguish Hestenes from
      Doran–Lasenby on the mixed example. Explain any cancellation.
    - Replace $B$ by $2B$. Predict how each self-pairing scales.
    - Explain why the metric self-pairing of a nonzero blade can vanish in
      the degenerate example, and why that does not make the blade zero.

    When translating a formula, check its grade rule, scalar treatment,
    reversal convention, and output grade before choosing an API operation.
    For more on model-specific constructions, continue with
    [RGA geometry and measurement](../rga/geometry_and_measurement.py).
    """)
    return


if __name__ == "__main__":
    app.run()
