import marimo

__generated_with = "0.23.11"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_marimo")
    for _path in [_root, _gamo]:
        if _path not in sys.path:
            sys.path.insert(0, _path)
    return


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga.facade import (
        Algebra,
        antidot_product,
        antimetric_apply,
        antireverse,
        antiwedge,
        bulk_part,
        dual,
        geometric_antiproduct,
        gp,
        left_complement,
        left_hodge_dual,
        left_interior_product,
        left_weight_dual,
        metric_apply,
        metric_inner_product,
        op,
        p_rga,
        reverse,
        right_complement,
        right_hodge_dual,
        right_interior_product,
        right_weight_dual,
        transwedge,
        transwedge_antiproduct,
        weight_part,
    )

    return (
        Algebra,
        antidot_product,
        antimetric_apply,
        antireverse,
        antiwedge,
        bulk_part,
        dual,
        geometric_antiproduct,
        gm,
        gp,
        left_complement,
        left_hodge_dual,
        left_interior_product,
        left_weight_dual,
        metric_apply,
        metric_inner_product,
        mo,
        op,
        p_rga,
        reverse,
        right_complement,
        right_hodge_dual,
        right_interior_product,
        right_weight_dual,
        transwedge,
        transwedge_antiproduct,
        weight_part,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Rigid Geometric Algebra (RGA)

    Rigid Geometric Algebra is Eric Lengyel's exterior-algebra formulation of
    projective geometry. Four-dimensional RGA models Euclidean 3-space with
    three positive basis vectors and one null basis vector. Incidence operations
    are metric-independent, while separate metric and antimetric operations
    describe bulk and weight.

    This notebook introduces Galaga's RGA convention layer and computes its
    defining identities with expression-tracked multivectors. It uses the **primal
    convention**: points are vectors, lines are bivectors, and planes are
    trivectors.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Constructing the algebra

    RGA orders its vector basis as $e_1,e_2,e_3,e_4$, with $e_4^2=0$.
    The explicit signature matters: Galaga's `(p, q, r)` convenience form puts
    null vectors first, while the RGA convention puts the null vector last.

    - `p_rga()` supplies the signature, Lengyel's factored blade labels (such
      as $e_{31}$ and $e_{423}$), and the matching operation notation.
    - `expr=True` records immutable expression provenance while numeric
      coefficients remain eagerly available.
    - Marimo interpolation chooses `:expr`, `:value`, or `:full` at the point
      where a lesson needs a particular view.
    """)
    return


@app.cell
def _(Algebra, p_rga):
    rga = Algebra(config=p_rga())
    return (rga,)


@app.cell
def _(rga):
    locals().update(rga.locals(expr=True))
    return


@app.cell
def _(e1, e2, e3, e4, gm, rga):
    gm.md(rt"""
    The metric is derived from the signature **{rga.signature}**.

    {e1} <br/>
    {e2} <br/>
    {e3} <br/>
    {e4}

    Their computed squares distinguish a Euclidean direction from the null
    projective direction:

    {e1**2} <br/>
    {e4**2}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Operations at a glance

    The RGA layer is explicit rather than overloading Galaga's established
    operators.

    | Concept | Galaga function | Output |
    |---|---|---|
    | Join / wedge | `op(a, b)` | grade sum |
    | Meet / antiwedge | `antiwedge(a, b)` | regressive grade |
    | Right / left complement | `right_complement(a)`, `left_complement(a)` | complementary grade |
    | Metric / antimetric map | `metric_apply(a)`, `antimetric_apply(a)` | same grade |
    | Bulk / weight part | `bulk_part(a)`, `weight_part(a)` | same grade |
    | Dot / antidot pairing | `metric_inner_product(a, b)`, `antidot_product(a, b)` | scalar / antiscalar |
    | Right / left bulk dual | `right_hodge_dual(a)`, `left_hodge_dual(a)` | complementary grade |
    | Right / left weight dual | `right_weight_dual(a)`, `left_weight_dual(a)` | complementary grade |
    | Geometric product / antiproduct | `gp(a, b)`, `geometric_antiproduct(a, b)` | generally mixed grade |
    | Reverse / antireverse | `reverse(a)`, `antireverse(a)` | same grade |
    | Right / left interior product | `right_interior_product(a, b)`, `left_interior_product(a, b)` | grade difference |
    | Order-$k$ transwedge | `transwedge(a, b, k)` | grade $r+s-2k$ |
    | Order-$k$ transwedge antiproduct | `transwedge_antiproduct(a, b, k)` | grade $r+s-4+2k$ |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Join and meet

    The exterior product joins primal objects: two points determine a line.
    The antiwedge is its De Morgan dual and computes a meet: two planes
    determine their intersection line. Neither operation needs a metric.
    """)
    return


@app.cell
def _(antiwedge, e1, e2, e3, e4, e423, e431, gm):
    point_p = (e1 + 2 * e2 + e4).named("P", latex="P")
    point_q = (-e1 + e3 + e4).named("Q", latex="Q")

    plane_x = e423.named(r"\pi_x", latex=r"\pi_x")
    plane_y = e431.named(r"\pi_y", latex=r"\pi_y")

    gm.md(rt"""
    Two homogeneous points join to a line:

    {point_p}

    {point_q}

    {point_p ^ point_q}

    The coordinate planes meet in their common line:

    {plane_x}

    {plane_y}

    {antiwedge(plane_x, plane_y)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Complements

    Complements depend on basis orientation, not metric inversion. For a basis
    blade $A$, the right complement fills the missing factors on the right,
    while the left complement fills them on the left:

    $$
    A \wedge \overline{A}=\text{𝟙}, \qquad
    \underline{A}\wedge A=\text{𝟙}.
    $$

    Here $\text{𝟙}$ is the RGA antiscalar (the pseudoscalar), not scalar $1$.
    """)
    return


@app.cell
def _(e1, gm, left_complement, right_complement):
    gm.md(rt"""
    Computing the signs gives the two complementary trivectors:

    {right_complement(e1)}

    {left_complement(e1)}

    Both defining wedge identities produce the oriented antiscalar:

    {e1 ^ right_complement(e1)}

    {left_complement(e1) ^ e1}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Metric, antimetric, bulk, and weight

    The extended metric multiplies a blade by the metric entries for basis
    vectors it contains. The antimetric uses the entries for basis vectors
    absent from the blade. With signature $(1,1,1,0)$:

    - `metric_apply` removes terms containing null $e_4$;
    - `antimetric_apply` removes terms that do not contain $e_4$.

    These maps are also exposed as `bulk_part` and `weight_part`. Their sum
    reconstructs the original multivector in this RGA model.
    """)
    return


@app.cell
def _(
    antimetric_apply,
    bulk_part,
    e23,
    e31,
    e41,
    e42,
    gm,
    metric_apply,
    weight_part,
):
    _line = (2 * e23 - e31 + 3 * e41 - e42).named("L", latex="L")

    gm.md(rt"""
    Start with a line containing Euclidean and weighted terms:

    { _line }

    The metric and antimetric maps compute complementary projections:

    { metric_apply(_line) }

    { antimetric_apply(_line) }

    The named bulk and weight parts agree with those maps:

    { bulk_part(_line) }

    { weight_part(_line) }

    Their sum reconstructs the input:

    { bulk_part(_line) + weight_part(_line) }
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dot and antidot products

    RGA's dot product pairs equal-grade components through the extended metric
    and returns a scalar. The antidot product uses the antimetric and returns an
    antiscalar:

    $$
    A\mathbin{\bullet}B=(A^TGB)\,1, \qquad
    A\mathbin{\circ}B=(A^T\mathbb{G}B)\,\text{𝟙}.
    $$

    This dot product is not merely the scalar part of the geometric product.
    For example, the RGA dot square of a Euclidean bivector is positive.
    """)
    return


@app.cell
def _(antidot_product, e23, e41, gm, metric_inner_product):
    _B = e23.named("B", latex="B")
    _W = e41.named("W", latex="W")

    gm.md(rt"""
    The metric and antimetric select complementary information:

    {_B}

    {metric_inner_product(_B, _B)}

    {_W}

    {metric_inner_product(_W, _W)}

    {antidot_product(_W, _W)}

    The last result has grade four: it is a multiple of the antiscalar.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Bulk and weight duals

    RGA distinguishes complements from metric duals. Its right and left bulk
    (Hodge) duals apply the metric before taking a complement:

    $$
    A^{\text{★}}=\overline{\mathbf{G}A}, \qquad
    A_{\text{★}}=\underline{\mathbf{G}A}.
    $$

    Weight duals use the antimetric:

    $$
    A^{\text{☆}}=\overline{\mathbb{G}A}, \qquad
    A_{\text{☆}}=\underline{\mathbb{G}A}.
    $$
    """)
    return


@app.cell
def _(
    e1,
    e41,
    gm,
    left_hodge_dual,
    left_weight_dual,
    right_hodge_dual,
    right_weight_dual,
):
    weight_blade = e41.named("W", latex="W")

    gm.md(rt"""
    For a Euclidean vector, the bulk dual is nonzero:

    {right_hodge_dual(e1)}

    {left_hodge_dual(e1)}

    The computed right-dual wedge pairing is:

    {e1 ^ right_hodge_dual(e1)}

    A weighted bivector instead has nonzero weight duals:

    {weight_blade}

    {right_weight_dual(weight_blade)}

    {left_weight_dual(weight_blade)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Geometric product and antiproduct

    For vectors, the geometric product combines the exterior product and RGA
    dot product:

    $$
    uv=u\wedge v+u\mathbin{\bullet}v.
    $$

    Dually, for antivectors (grade-three elements here), the geometric
    antiproduct combines the antiwedge and antidot product. Reverse changes
    signs by grade; antireverse applies the corresponding rule by antigrade.
    """)
    return


@app.cell
def _(
    antidot_product,
    antireverse,
    antiwedge,
    e1,
    e2,
    e3,
    e4,
    geometric_antiproduct,
    gm,
    gp,
    metric_inner_product,
    op,
    reverse,
    right_complement,
):
    vector_u = (e1 + 2 * e2 + e4).named("u", latex="u")
    vector_v = (e1 - e2 + e3).named("v", latex="v")
    vector_gp = gp(vector_u, vector_v)
    vector_gp_parts = op(vector_u, vector_v) + metric_inner_product(vector_u, vector_v)
    antivector_u = right_complement(vector_u)
    antivector_v = right_complement(vector_v)
    antivector_gap = geometric_antiproduct(antivector_u, antivector_v)
    antivector_gap_parts = antiwedge(antivector_u, antivector_v) + antidot_product(antivector_u, antivector_v)
    reversed_join = reverse(op(vector_u, vector_v))
    complemented_reversed_join = right_complement(reversed_join)
    antireversed_meet = antireverse(antiwedge(antivector_u, antivector_v))

    gm.md(rt"""
    The vector product decomposition computes the same multivector both ways:

    {vector_gp}

    {vector_gp_parts}

    Complementing the vectors gives antivectors:

    {antivector_u}

    {antivector_v}

    The antiproduct decomposition also agrees:

    {antivector_gap}

    {antivector_gap_parts}

    The reverse and antireverse act on complementary grade-two results, so
    their outputs are not directly equal. Right-complementing the reversed
    join gives:

    {complemented_reversed_join}

    This agrees with antireversing the meet:

    {antireversed_meet}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Interior products

    RGA interior products are defined from bulk duals and the antiwedge:

    $$
    a\mathbin{\rfloor}B=a_{\text{★}}\vee B, \qquad
    B\mathbin{\lfloor}a=B\vee a^{\text{★}}.
    $$

    Operand order matters. For vector $a$ and bivector $B$:

    $$
    a\mathbin{\text{⟑}}B=a\wedge B+B\mathbin{\lfloor}a, \qquad
    B\mathbin{\text{⟑}}a=B\wedge a+a\mathbin{\rfloor}B.
    $$
    """)
    return


@app.cell
def _(e1, e2, e3, gm, left_interior_product, op, right_interior_product):
    _a = (e1 + e2).named("a", latex="a")
    _B = op(e1 + 2 * e3, e2 - e3).named("B", latex="B")

    gm.md(rt"""
    Choose:

    {_a}

    {_B}

    The vector-bivector decomposition computes:

    {_a * _B}

    {(_a ^ _B) + right_interior_product(_B, _a)}

    Reversing the operand order computes:

    {_B * _a}

    {(_B ^ _a) + left_interior_product(_a, _B)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Transwedge products

    The order-$k$ transwedge contracts $k$ basis directions between homogeneous
    operands. Order zero is the exterior product. For bivectors, orders 0, 1,
    and 2 reconstruct the geometric product with the Terathon signs:

    $$
    AB=
    A\mathbin{\underset{0}{\text{⩓}}}B +
    A\mathbin{\underset{1}{\text{⩓}}}B -
    A\mathbin{\underset{2}{\text{⩓}}}B.
    $$

    The transwedge antiproduct is the De Morgan dual family and reconstructs the
    geometric antiproduct with the same signed sum:

    $$
    A\mathbin{\text{⟇}}B=
    A\mathbin{\underset{0}{\text{⩔}}}B +
    A\mathbin{\underset{1}{\text{⩔}}}B -
    A\mathbin{\underset{2}{\text{⩔}}}B.
    $$
    """)
    return


@app.cell
def _(
    e12,
    e23,
    e31,
    e41,
    e42,
    geometric_antiproduct,
    gm,
    transwedge,
    transwedge_antiproduct,
):
    _a = (e23 + 2 * e31 + e41).named("A", latex="A")
    _b = (e12 - e31 + 3 * e42).named("B", latex="B")

    gm.md(rt"""
    Use two bivectors containing Euclidean and weighted terms:

    {_a}

    {_b}

    Their transwedge orders are:

    {transwedge(_a, _b, 0)}

    {transwedge(_a, _b, 1)}

    {transwedge(_a, _b, 2)}

    The signed sum matches the independently computed geometric product:

    {transwedge(_a, _b, 0) + transwedge(_a, _b, 1) - transwedge(_a, _b, 2)}

    {_a * _b}

    The three transwedge-antiproduct orders are:

    {transwedge_antiproduct(_a, _b, 0)}

    {transwedge_antiproduct(_a, _b, 1)}

    {transwedge_antiproduct(_a, _b, 2)}

    Their signed sum matches the geometric antiproduct:

    {transwedge_antiproduct(_a, _b, 0) + transwedge_antiproduct(_a, _b, 1) - transwedge_antiproduct(_a, _b, 2)}

    {geometric_antiproduct(_a, _b)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Degenerate duality: an important distinction

    Galaga's existing `dual()` multiplies by the inverse pseudoscalar. It is a
    different operation from an RGA bulk dual and is undefined when the metric
    is degenerate. The RGA Hodge construction applies the metric and then takes
    a complement, so it remains defined and projects away null bulk components.
    """)
    return


@app.cell
def _(dual, e1, right_hodge_dual):
    try:
        _inverse_pseudoscalar_result = dual(e1)
        inverse_dual_message = f"unexpected result: {_inverse_pseudoscalar_result}"
    except ValueError as _dual_error:
        inverse_dual_message = str(_dual_error)

    rga_bulk_dual = right_hodge_dual(e1)
    return inverse_dual_message, rga_bulk_dual


@app.cell
def _(e1, gm, inverse_dual_message, rga_bulk_dual):
    gm.md(rt"""
    For the same vector {e1}:

    - `dual(e1)` reports: **{inverse_dual_message}**
    - `right_hodge_dual(e1)` remains well-defined:

    {rga_bulk_dual}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Summary

    RGA separates three ideas that can coincide in a nondegenerate Euclidean
    algebra:

    1. complements encode orientation and incidence without a metric;
    2. the metric and antimetric isolate bulk and weight;
    3. bulk and weight duals combine those maps with complements.

    The wedge/antiwedge, product/antiproduct, interior, and transwedge families
    then come in De Morgan pairs. Keeping those roles explicit lets the same
    definitions work cleanly with RGA's null basis vector.
    """)
    return


if __name__ == "__main__":
    app.run()
