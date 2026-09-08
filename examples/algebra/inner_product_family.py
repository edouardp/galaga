import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_matrix import MatrixRepr

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        Notation,
        doran_lasenby_inner,
        evaluate,
        hestenes_inner,
        left_contraction,
        metric_inner_product,
        right_contraction,
        scalar_product,
    )

    return (
        Algebra,
        DisplayPolicy,
        MatrixRepr,
        Notation,
        doran_lasenby_inner,
        evaluate,
        gm,
        hestenes_inner,
        left_contraction,
        metric_inner_product,
        mo,
        np,
        right_contraction,
        scalar_product,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Which inner product do you mean?

    These six operations agree on vector pairs but differ on scalars, higher
    grades, and operand order. Agreement on two vectors cannot identify the
    convention! We will first compute from a Gram matrix, then compare the
    functions on inputs chosen to reveal their differences.

    Galaga 2 exposes named functions, not an `ip(..., mode=...)` dispatcher.
    The `|` operator always means `doran_lasenby_inner`. A local import such as
    `from galaga import hestenes_inner as ip` chooses one fixed convention;
    it does not change `|`.
    """)
    return


@app.cell
def _(mo):
    metric_selector = mo.ui.dropdown(
        options={
            "Oblique positive": ((2, 1), (1, 3)),
            "Euclidean": ((1, 0), (0, 1)),
            "Indefinite": ((2, 1), (1, -1)),
            "Degenerate": ((1, 0), (0, 0)),
        },
        value="Oblique positive",
        label="Choose the Gram matrix",
    )
    mo.hstack([metric_selector])
    return (metric_selector,)


@app.cell
def _(metric_selector, np):
    gram = np.array(metric_selector.value, dtype=float)
    return (gram,)


@app.cell
def _(Algebra, DisplayPolicy, MatrixRepr, gram):
    algebra = Algebra(gram=gram, display=DisplayPolicy(content="full"))
    e1, e2 = algebra.basis_vectors(expr=True)
    B = (e1 ^ e2).named("B")
    gram_matrix = MatrixRepr(gram).name(latex=r"G")
    return B, algebra, e1, e2, gram_matrix


@app.cell
def _(B, e1, e2, gm, gram_matrix):
    gm.md(rt"""
    ## 1. Start with the metric and a genuine bivector

    {gram_matrix}

    Our basis vectors are {e1:value} and {e2:value}, and our oriented
    bivector is {B:full}.

    Use the wedge to construct $B=e_1\wedge e_2$: in an oblique basis,
    $e_1e_2=G_{{12}}+B$ also has a scalar part.
    """)
    return


@app.cell
def _(
    B,
    algebra,
    doran_lasenby_inner,
    e1,
    e2,
    hestenes_inner,
    left_contraction,
    metric_inner_product,
    right_contraction,
    scalar_product,
):
    inner_operations = {
        "Doran–Lasenby": doran_lasenby_inner,
        "Hestenes": hestenes_inner,
        "Left contraction": left_contraction,
        "Right contraction": right_contraction,
        "Scalar product": scalar_product,
        "Metric pairing": metric_inner_product,
    }
    comparison_pairs = {
        "Scalar on the left": (algebra.scalar(2), e1),
        "Scalar on the right": (e1, algebra.scalar(2)),
        "Vector then bivector": (e1, B),
        "Bivector then vector": (B, e1),
        "Bivector with itself": (B, B),
        "Mixed grades": ((2 + e1 + B).named("a"), (3 + e2 + 2 * B).named("b")),
    }
    comparison_results = {
        _title: {_label: _function(*_pair) for _label, _function in inner_operations.items()}
        for _title, _pair in comparison_pairs.items()
    }
    return comparison_pairs, comparison_results, inner_operations


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Predict the grade before inspecting the value

    For homogeneous grades $r$ and $s$, Doran–Lasenby selects grade $|r-s|$;
    Hestenes does the same **only when both grades are nonzero**.
    Left contraction selects $s-r$, and right contraction selects $r-s$.
    A negative requested grade gives zero.

    Thus a scalar passes through on either side for Doran–Lasenby, on the
    left for left contraction, and on the right for right contraction.
    Hestenes discards scalar contributions. Both scalar-valued pairings give
    zero between a scalar and a vector.

    For $B=e_1\wedge e_2$, compute the contraction from the metric:
    $e_1\mathbin{\rfloor}B=G_{11}e_2-G_{12}e_1$.
    Reversing the order gives
    $B\mathbin{\lfloor}e_1=G_{12}e_1-G_{11}e_2$.
    Try changing the metric and check both the surviving grade and its sign.
    """)
    return


@app.cell
def _(comparison_pairs, comparison_results, gm, mo):
    _panels = []
    for _title, (_left, _right) in comparison_pairs.items():
        _results = comparison_results[_title]
        _dli = _results["Doran–Lasenby"]
        _hi = _results["Hestenes"]
        _lc = _results["Left contraction"]
        _rc = _results["Right contraction"]
        _sp = _results["Scalar product"]
        _metric = _results["Metric pairing"]
        _panels.append(
            gm.md(t"""
        ### {_title!s}

        Left operand: {_left:value}. Right operand: {_right:value}.

        | Function | Computed value |
        |---|---|
        | `doran_lasenby_inner` | {_dli:value} |
        | `hestenes_inner` | {_hi:value} |
        | `left_contraction` | {_lc:value} |
        | `right_contraction` | {_rc:value} |
        | `scalar_product` | {_sp:value} |
        | `metric_inner_product` | {_metric:value} |
        """)
        )
    mo.vstack(_panels)
    return


@app.cell
def _(B, comparison_results, e1, e2, gram, metric_inner_product, np, scalar_product):
    determinant = float(np.linalg.det(gram))
    bivector_scalar = scalar_product(B, B)
    bivector_metric = metric_inner_product(B, B)
    np.testing.assert_allclose(float(bivector_scalar), -determinant, rtol=0, atol=1e-12)
    np.testing.assert_allclose(float(bivector_metric), determinant, rtol=0, atol=1e-12)
    _expected_left = gram[0, 0] * e2 - gram[0, 1] * e1
    assert comparison_results["Vector then bivector"]["Left contraction"] == _expected_left
    assert comparison_results["Bivector then vector"]["Right contraction"] == -_expected_left
    return bivector_metric, bivector_scalar, determinant


@app.cell
def _(bivector_metric, bivector_scalar, determinant, gm):
    gm.md(rt"""
    ## 3. Scalar part is not the exterior metric pairing

    For this Gram matrix, $\det G={determinant}$.
    The induced pairing of the oriented area with itself is
    {bivector_metric:value}, whereas the scalar part of $BB$ is
    {bivector_scalar:value}.

    Reversion negates a bivector. Consequently,
    $\langle BB\rangle_0=-\det G$, but
    $\langle B\widetilde B\rangle_0=\det G$.
    These signs come from the metric, not the label $B$.

    In the degenerate example both pairings vanish even though $B$ is a
    nonzero bivector. In an indefinite metric the pairing is not positive
    definite. Do not infer that a value is zero from its self-pairing.

    For mixed grades, apply each definition to every pair of homogeneous
    components and add the results. You cannot use one grade-difference
    rule for the whole mixed multivector. The final comparison above
    demonstrates how scalar contributions and bivector signs interact.
    """)
    return


@app.cell
def _(algebra, comparison_pairs, comparison_results, evaluate, np):
    mixed_dli = comparison_results["Mixed grades"]["Doran–Lasenby"]
    mixed_hi = comparison_results["Mixed grades"]["Hestenes"]
    _a, _b = comparison_pairs["Mixed grades"]
    assert mixed_dli.expr.operation_id == "doran_lasenby_inner"
    assert mixed_hi.expr.operation_id == "hestenes_inner"
    for _value in (mixed_dli, mixed_hi):
        _replayed = evaluate(_value.expr, algebra=algebra, environment={"a": _a, "b": _b})
        np.testing.assert_allclose(_replayed.data, _value.data, rtol=0, atol=1e-12)
    return mixed_dli, mixed_hi


@app.cell
def _(Notation, gm, mixed_dli, mixed_hi):
    _functional_dli = mixed_dli.display("expr/latex", notation=Notation.functional())
    _functional_hi = mixed_hi.display("expr/latex", notation=Notation.functional())
    gm.md(rt"""
    ## 4. A shared symbol does not imply a shared operation

    The default LaTeX notation uses a dot for both of these products.
    Their stored operation IDs remain distinct. Functional notation makes
    the difference explicit:

    $${_functional_dli!s}$$

    $${_functional_hi!s}$$

    The cells above also replay both expressions with explicit symbol
    bindings and check their coefficients. Rendering a different symbol
    never changes the operation or its eager numeric result.
    """)
    return


if __name__ == "__main__":
    app.run()
