import marimo

__generated_with = "0.23.11"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _repository = Path(__file__).resolve().parent.parent.parent
    for _source in (
        _repository,
        _repository / "packages" / "galaga",
        _repository / "packages" / "galaga_marimo",
    ):
        _path = str(_source)
        if _path not in sys.path:
            sys.path.insert(0, _path)
    return


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga.facade import (
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


if __name__ == "__main__":
    app.run()
