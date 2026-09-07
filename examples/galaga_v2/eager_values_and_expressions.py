import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        doran_lasenby_inner,
        geometric_product,
        grade,
        norm,
        outer_product,
        p_euclidean,
        reverse,
        unit,
    )

    return (
        Algebra,
        DisplayPolicy,
        doran_lasenby_inner,
        geometric_product,
        gm,
        grade,
        mo,
        norm,
        outer_product,
        p_euclidean,
        reverse,
        unit,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Eager values with optional expression provenance

    **Claim:** a Galaga 2 multivector is always an eager numeric value.
    Expression tracking is optional immutable metadata used for explanation
    and rendering; it never delays or replaces the numeric calculation.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, p_euclidean):
    algebra = Algebra(
        config=p_euclidean(3),
        display=DisplayPolicy(content="full"),
    )
    e1, e2, e3 = algebra.basis_vectors(expr=True)
    u = (2 * e1 + e2).named("u", latex=r"\mathbf{u}")
    v = (e1 - 3 * e3).named("v", latex=r"\mathbf{v}")
    return algebra, e1, e2, e3, u, v


@app.cell
def _(gm, u, v):
    gm.md(rt"""
    The factories calculate coefficients immediately. `expr=True` also gives
    the basis vectors literal expression leaves, so later operations can
    retain their derivation:

    {u}

    {v}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Long operation names are the primary API

    Explicit names make mathematically different operations visible in code.
    Operators remain useful notation aliases:

    | Primary function | Operator alias |
    |---|---|
    | `geometric_product(a, b)` | `a * b` |
    | `outer_product(a, b)` | `a ^ b` |
    | `doran_lasenby_inner(a, b)` | `a \| b` |
    | `reverse(a)` | `~a` |

    Galaga 2 intentionally has no ambiguous `inner_product` function. Choose
    the Doran–Lasenby, Hestenes, metric, scalar, contraction, or interior
    product explicitly.
    """)
    return


@app.cell
def _(doran_lasenby_inner, geometric_product, outer_product, reverse, u, v):
    uv = geometric_product(u, v).named("P")
    oriented_area = outer_product(u, v).named("B")
    vector_inner = doran_lasenby_inner(u, v).named("s")
    reversed_product = reverse(uv)
    return oriented_area, reversed_product, uv, vector_inner


@app.cell
def _(gm, oriented_area, reversed_product, uv, vector_inner):
    gm.md(rt"""
    {uv}

    {oriented_area}

    {vector_inner}

    {reversed_product}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Products may be variadic

    `geometric_product` and `outer_product` accept two or more operands. The
    numeric operation and its provenance are folded left, so a call remains a
    sequence of ordinary binary algebra operations rather than introducing a
    second n-ary product definition.
    """)
    return


@app.cell
def _(e1, e2, e3, geometric_product, gm, outer_product):
    _pseudoscalar_from_wedge = outer_product(e1, e2, e3)
    _pseudoscalar_from_product = geometric_product(e1, e2, e3)

    gm.md(rt"""
    `outer_product(e1, e2, e3)`:

    {_pseudoscalar_from_wedge}

    `geometric_product(e1, e2, e3)`:

    {_pseudoscalar_from_product}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Naming and provenance are independent

    - `.named(...)` returns a new wrapper with a semantic `Name`.
    - `.unnamed()` removes only that name.
    - `.with_expr()` attaches an inferred literal expression when provenance
      was not requested at construction.
    - `.without_expr()` removes only provenance.

    A named value becomes a symbolic leaf when it participates in a tracked
    operation. Its coefficients remain available throughout.
    """)
    return


@app.cell
def _(algebra, geometric_product, gm):
    plain_vector = algebra.vector((1.0, 2.0, -1.0))
    explanatory_vector = plain_vector.named("a").with_expr()
    explanatory_square = geometric_product(explanatory_vector, explanatory_vector)
    _plain_has_expression = plain_vector.expr is not None
    _tracked_has_expression = explanatory_square.expr is not None
    _coefficients = explanatory_square.data

    gm.md(rt"""
    The plain value has provenance: `{_plain_has_expression!s}`.

    The tracked result has provenance: `{_tracked_has_expression!s}`.

    {explanatory_square}

    Its eager coefficient array is still:

    ```text
    {_coefficients!s}
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Blade factories avoid notebook-local mutation

    `blade(...)` accepts a configured name, native mask, signed `BladeRef`, or
    a signed unit blade value. `blades(...)` is the ordered batch form. This is
    useful in Marimo, where mutating `locals()` would defeat dependency
    tracking.
    """)
    return


@app.cell
def _(algebra, e1, e2, e3, gm):
    e12, e31 = algebra.blades(e1 ^ e2, e3 ^ e1, expr=True)
    _line = (2 * e12 - e31).named("L")

    gm.md(rt"""
    {e12}

    {e31}

    {_line}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Scalar results and checked conversion

    Anonymous numeric operations return ordinary Python scalars where that is
    their natural result. If an operation such as `norm` receives a named or
    tracked value, it returns a scalar multivector so the explanatory
    expression survives.

    `float(value)` succeeds only when the entire multivector is scalar. It
    never silently takes the grade-0 part of a mixed-grade value.
    """)
    return


@app.cell
def _(gm, norm, u, unit):
    u_length = norm(u)
    u_direction = unit(u)
    _length_as_float = float(u_length)

    gm.md(rt"""
    {u_length}

    {u_direction}

    Explicit numeric formatting converts the scalar multivector first:
    `{_length_as_float:.3f}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Grade selection remains explicit with `grade(value, k)` or `value[k]`.
    `scalar_part(value)` exists as an optional helper, but
    `float(grade(value, 0))` states both operations directly.
    """)
    return


@app.cell
def _(gm, grade, uv):
    _uv_scalar = grade(uv, 0)
    _uv_bivector = uv[2]

    gm.md(rt"""
    Scalar grade:

    {_uv_scalar}

    Bivector grade:

    {_uv_bivector}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Small numbers, fractions, and names

    A display tolerance is not numeric equality. By default, coefficients with
    magnitude smaller than $10^{-12}$ are hidden in the **value** display. For a
    calculation involving tiny values, explicitly select
    `DisplayPolicy(zero_tolerance=0)`. This changes presentation, not storage.

    Scalar division still uses floating-point arithmetic: a displayed fraction
    is not an exact rational type. Literal arithmetic may simplify to a decimal.
    A named numerator instead remains symbolic; replay then needs its value
    supplied in an explicit environment.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, gm):
    from fractions import Fraction
    from galaga.expression import evaluate

    _scalar_algebra = Algebra(1)
    small_scalar = _scalar_algebra.scalar(1.2e-34, expr=True).named("epsilon", latex=r"\epsilon")
    small_default_latex = small_scalar.latex(content="value")
    _visible = _scalar_algebra.presentation.with_display(DisplayPolicy(zero_tolerance=0))
    small_visible_latex = small_scalar.display("value/latex", presentation=_visible)
    assert float(small_scalar) == 1.2e-34
    assert small_scalar != 0

    third_literal = _scalar_algebra.scalar(1, expr=True) / 3
    _numerator = _scalar_algebra.scalar(1, expr=True).named("a")
    third_named = _numerator / 3
    third_replayed = evaluate(third_named.expr, algebra=_scalar_algebra, environment={"a": _numerator})
    assert third_replayed == third_named
    assert Fraction(float(third_literal)) != Fraction(1, 3)
    _literal_latex = third_literal.latex(content="full")
    _named_latex = third_named.latex(content="full")

    gm.md(rt"""
    The stored small coefficient is `{float(small_scalar):.2e}`, and it is
    **not equal to zero**. Its default value display is ${small_default_latex!s}$;
    with the display tolerance disabled it is ${small_visible_latex!s}$.
    Do not interpret a tolerance-filtered display as an exact equality.

    Literal division:

    $$
    {_literal_latex!s}
    $$

    Named-numerator division, replayed with an explicit value for `a`:

    $$
    {_named_latex!s}
    $$

    `.named(...)` does not enable expression tracking or create a physical
    constant. Here `expr=True` was requested explicitly. Supply values and
    units from the domain of your application. Scientific LaTeX currently
    uses `\times`; `coefficient_precision` sets significant digits, not
    fixed-decimal padding.
    """)
    return (
        small_default_latex,
        small_scalar,
        small_visible_latex,
        third_literal,
        third_named,
        third_replayed,
    )


if __name__ == "__main__":
    app.run()
