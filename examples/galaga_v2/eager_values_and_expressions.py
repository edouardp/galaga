import marimo

__generated_with = "0.24.0"
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
    - `.with_expr()` uses the name as a symbol when named; otherwise it keeps
      existing provenance or attaches a literal snapshot.
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
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The denominator is part of the explanation

    Dividing by a multivector records **both operands**, even if the current
    denominator happens to be scalar. Replay can change its value without
    changing the already-computed quotient. In contrast, `a / 3` records the
    Python number `3` as a fixed scalar parameter.

    The rounded inputs below illustrate `hbar / (mass * speed)`; they are
    supplied values, not a physical-constants database or a units system.
    Doubling the mass should halve the quotient. Inspect the fraction before
    reading the numeric check.
    """)
    return


@app.cell
def _(algebra, gm):
    import numpy as _np

    from galaga import Name as _Name
    from galaga import evaluate as _evaluate

    quotient_hbar = algebra.scalar(1.055e-34).named(_Name("hbar", "ℏ", r"\hbar"))
    quotient_mass = algebra.scalar(9.109e-31).named(_Name("mass", latex=r"m_e"))
    quotient_speed = algebra.scalar(3e8).named("c")
    physical_quotient = quotient_hbar / (quotient_mass * quotient_speed)
    quotient_rebound = _evaluate(
        physical_quotient.expr,
        algebra=algebra,
        environment={"hbar": quotient_hbar, "mass": 2 * quotient_mass, "c": quotient_speed},
    )
    _fraction = physical_quotient.display("expr/latex")
    _tiny = float(_np.nextafter(0.0, 1.0))
    subnormal_quotient = _tiny / algebra.scalar(_tiny, expr=True)
    assert subnormal_quotient == 1

    gm.md(rt"""
    The denominator's product remains visible:

    $$
    {_fraction!s}.
    $$

    Original quotient: `{float(physical_quotient):.6e}`.
    Replayed with twice the mass: `{float(quotient_rebound):.6e}`.
    The original value has not changed.

    Floating-point arithmetic needs care even when the answer is simple.
    The smallest positive stored float divided by itself is
    `{float(subnormal_quotient):g}`. Direct scalar division avoids first
    forming its unrepresentably large reciprocal. A tiny **nonzero vector
    component** in a divisor must also be retained: a tolerant scalar
    predicate is not permission to discard stored grades.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Literal snapshots versus symbol bindings

    A plain multivector is a numeric operand, not a bare expression node.
    Combining it with a tracked operand records its coefficients as a literal
    snapshot. A named operand instead contributes a symbol: replay needs an
    explicit binding and can use a new value without changing the eager result.

    Here a bivector multiplies a vector, producing both vector and trivector
    grades. Compare the two histories before and after rebinding `a`.
    """)
    return


@app.cell
def _(algebra, geometric_product, gm):
    from galaga import evaluate as _evaluate

    history_source = algebra.vector((2, -1, 1))
    history_replacement = algebra.vector((1, 2, -1))
    _plane = algebra.blade(3)
    literal_history = geometric_product(_plane, history_source.with_expr())
    named_history = geometric_product(_plane, history_source.named("a"))
    literal_replay = _evaluate(literal_history.expr, algebra=algebra)
    assert literal_replay == literal_history
    named_replay = _evaluate(named_history.expr, algebra=algebra, environment={"a": history_replacement})
    _literal_expression = literal_history.display("expr/latex")
    _named_expression = named_history.display("expr/latex")
    _original_value = named_history.display("value/latex")
    _replayed_value = named_replay.display("value/latex")

    gm.md(rt"""
    Both calculations initially give the same numeric value:

    $$
    {_original_value!s}.
    $$

    Literal history (no environment needed):

    $$
    {_literal_expression!s}.
    $$

    Named history (bind `a` explicitly):

    $$
    {_named_expression!s}.
    $$

    Replaying the named history with `a = algebra.vector((1, 2, -1))` gives

    $$
    {_replayed_value!s}.
    $$

    `literal_replay` still equals the original value. `named_history` also
    keeps its original coefficients; replay returns a new value.
    """)
    return (history_replacement,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Nodes describe operations; values perform them

    `Symbol("a")` has no coefficients, so it cannot replace a multivector in
    numeric multiplication. To build an expression without calculating yet,
    use `Call` and then `evaluate(..., algebra=..., environment=...)`.

    Node `repr` is diagnostic structure, not formatted mathematics. Use
    `render(node, presentation=...)` for mathematical display. Even a standalone
    `ScalarLiteral` needs an algebra when evaluated; nodes carry no hidden
    evaluation context.

    Prefer `unit(a)` to the deprecated `normalize(a)` and `normalise(a)`
    warning adapters. Normalization divides by the metric-derived magnitude;
    it is not `inverse(a)`. A nonzero null vector cannot be normalized this way.
    """)
    return


@app.cell
def _(algebra, gm, history_replacement):
    from galaga import Call as _Call
    from galaga import ScalarLiteral as _ScalarLiteral
    from galaga import Symbol as _Symbol
    from galaga import evaluate as _evaluate
    from galaga import render as _render

    scalar_node = _ScalarLiteral(3)
    reflected_node = _Call("subtract", (scalar_node, _Symbol("a")))
    reflected_replay = _evaluate(reflected_node, algebra=algebra, environment={"a": history_replacement})
    scalar_node_value = _evaluate(scalar_node, algebra=algebra)
    assert scalar_node_value == 3
    _diagnostic = repr(reflected_node)
    _math = _render(reflected_node, presentation=algebra.presentation, target="latex")

    gm.md(rt"""
    The source order in `3 - a` is explicit:

    ```text
    {_diagnostic!s}
    ```

    Its mathematical rendering is ${_math!s}$. Replaying with the same new
    binding gives:

    {reflected_replay}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Three different meanings of equality

    Multivectors compare numeric values, ignoring their names and provenance.
    Expression nodes instead compare operation IDs, ordered operands and
    normalized parameters. A symbol's identity includes all its name spellings,
    not just the ASCII identifier.

    Rendered strings answer a third question. If two different symbols are
    both given the LaTeX spelling `x`, their expressions can look identical
    without being the same history. Do not use rendered mathematics as a
    cache key for an expression or its evaluated value.

    Literal coefficients are finite floating-point numbers, compared exactly,
    not approximately. Construction converts inputs to floats; it does not
    create exact rational or arbitrary-precision storage. Adjacent floats can
    be numerically close without being equal literal nodes. Equal nodes have
    compatible hashes; unequal nodes need not have different hashes.
    """)
    return


@app.cell
def _(algebra, gm):
    import numpy as _np

    import galaga as _ga

    _vector = algebra.vector((1, 2, -1))
    identity_left = 5 * _vector.named("left", latex="x")
    identity_right = 5 * _vector.named("right", latex="x")
    identity_values_equal = identity_left == identity_right
    identity_histories_equal = identity_left.expr == identity_right.expr
    _left_math = identity_left.display("expr/latex")
    identity_renderings_equal = _left_math == identity_right.display("expr/latex")
    identity_rebound = _ga.evaluate(
        identity_right.expr,
        algebra=algebra,
        environment={"right": algebra.vector((2, 0, 1))},
    )
    _rebound_math = identity_rebound.display("value/latex")
    adjacent_literals = (_ga.ScalarLiteral(1), _ga.ScalarLiteral(_np.nextafter(1.0, 2.0)))
    adjacent_literals_equal = adjacent_literals[0] == adjacent_literals[1]
    signed_zero_literals = (_ga.ScalarLiteral(0.0), _ga.ScalarLiteral(-0.0))
    signed_zero_lookup = {signed_zero_literals[0]: "same key"}[signed_zero_literals[1]]

    gm.md(rt"""
    The two histories both display as ${_left_math!s}$.

    | Comparison | Equal? |
    |---|---|
    | Eager multivector values | {identity_values_equal!s} |
    | Expression histories | {identity_histories_equal!s} |
    | LaTeX strings | {identity_renderings_equal!s} |

    Rebinding only the symbol `right` gives the new value ${_rebound_math!s}$.
    The original two eager values are unchanged.

    The adjacent floating-point literals are:

    ```text
    {repr(adjacent_literals[0])!s}
    {repr(adjacent_literals[1])!s}
    ```

    Their node equality is `{adjacent_literals_equal!s}`. In contrast,
    `+0.0` and `-0.0` compare equal and give the same dictionary lookup:
    `{signed_zero_lookup!s}`. These rules concern stored numbers, not display
    rounding or a chosen tolerance.
    """)
    return


if __name__ == "__main__":
    app.run()
