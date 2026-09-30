"""Compare a pure exterior algebra with Euclidean GA, then draw oriented area."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, complement, dual, exp, inverse, log, meet, norm, presets, sqrt

    return (
        Algebra,
        complement,
        dual,
        exp,
        gm,
        inverse,
        log,
        meet,
        mo,
        norm,
        np,
        plt,
        presets,
        sqrt,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Exterior algebra and geometric algebra

    The wedge product records oriented content: vectors span lengths,
    bivectors span areas, and trivectors span volumes. Galaga can make the
    entire Gram matrix zero with `presets.exterior(3)`. Then the geometric
    product is exactly the wedge product. We will compare that algebra with
    three-dimensional Euclidean GA, whose basis vectors have square one.
    """)
    return


@app.cell
def _(Algebra, presets):
    exterior = Algebra(config=presets.exterior(3), expr=True)
    euclidean = Algebra(3, expr=True)
    return euclidean, exterior


@app.cell
def _(exterior):
    exterior  # noqa: B018 - marimo displays the cell's final expression
    return


@app.cell
def _(euclidean):
    euclidean  # noqa: B018 - marimo displays the cell's final expression
    return


@app.cell
def _(euclidean, exterior):
    e1, e2, e3 = exterior.basis_vectors(expr=True)
    r1, r2, r3 = euclidean.basis_vectors(expr=True)
    return e1, e2, e3, r1, r2, r3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Products: what the metric changes

    The exterior product is independent of the Gram matrix. In the all-null
    algebra, $e_i^2=0$ and every geometric product is an exterior product.
    The Euclidean metric adds scalar contractions, so $e_i^2=1$ there.
    """)
    return


@app.cell
def _(e1, e2, gm, r1, r2):
    _null_square = e1**2
    _regular_square = r1**2
    _null_pair = e1 * e2
    _regular_pair = r1 * r2
    assert _null_pair == e1 ^ e2
    assert _regular_pair == r1 ^ r2
    gm.md(rt"""
    All-null basis square:
    {_null_square:block}

    Euclidean basis square:
    {_regular_square:block}

    Distinct orthogonal basis vectors multiply to their wedge in both
    examples:

    All-null basis product:
    {_null_pair:block}

    Euclidean basis product:
    {_regular_pair:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Finite powers in the exterior algebra

    Write $x=a+N$, where $a>0$ is scalar and $N$ has positive grades. In
    $n$ dimensions, $N^{n+1}=0$. Thus every real power on this principal
    branch is a finite binomial polynomial:

    $$
    x^\alpha=a^\alpha\sum_{k=0}^{n}\binom{\alpha}{k}(N/a)^k.
    $$

    This supports `x ** 0.5`, `x ** 1.5`, and negative fractional powers.
    Integer powers still work for every algebra. A noninteger `**` on the
    Euclidean algebra has no general real branch selected by Galaga.
    """)
    return


@app.cell
def _(e1, e2, e3, exterior, gm):
    nilpotent = (e1 + (e2 ^ e3)).named("N")
    x = (2 + nilpotent).named("x")
    _square = nilpotent * nilpotent
    _cube = _square * nilpotent
    assert _square == 2 * exterior.I
    assert _cube == 0
    gm.md(rt"""
    Our mixed-grade example:

    {nilpotent:block}

    Its square is {_square} and its cube is {_cube}.

    Its square is a nonzero trivector, so the finite series needs
    more than its first two terms.
    """)
    return nilpotent, x


@app.cell
def _(exp, exterior, gm, inverse, log, nilpotent, sqrt, x):
    root = sqrt(x)
    fractional = x**1.5
    inverse_value = inverse(x)
    negative_fraction = x ** (-1 / 3)
    _root_agrees = root.almost_equal(x**0.5)
    _power_agrees = (fractional * fractional).almost_equal(x**3)
    _inverse_agrees = inverse_value.almost_equal(x**-1)
    _fraction_agrees = (negative_fraction * (x ** (1 / 3))).almost_equal(exterior.identity)
    _log_agrees = exp(log(x)).almost_equal(x)
    gm.md(rt"""
    **Given:**

    {nilpotent:block}

    {x:block}

    **Square root:** {root:block}

    **Power 1.5:** {fractional:block}

    **Inverse:** {inverse_value:block}

    **Power −1/3:** {negative_fraction:block}

    The two square-root paths agree: **{_root_agrees}**. <br/> Squaring the
    $1.5$ power gives $x^3$: **{_power_agrees}**. <br/> The negative integer
    power agrees with `inverse`: **{_inverse_agrees}**. <br/> Reciprocal
    fractional powers multiply to one: **{_fraction_agrees}**.<br/>
    The logarithm and exponential round-trip: **{_log_agrees}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Complement, meet, and metric dual

    Complement uses the oriented basis and remains defined with zero Gram
    matrix. Meet is built from complements, so coordinate planes can still
    meet in a line. A metric dual needs an invertible pseudoscalar; the
    all-null pseudoscalar is not invertible. Metric norm also collapses on
    positive-grade values.
    """)
    return


@app.cell
def _(complement, dual, e1, e2, e3, gm, meet, norm, r1, r2, r3):
    _null_meet = meet(e1 ^ e2, e2 ^ e3)
    _regular_meet = meet(r1 ^ r2, r2 ^ r3)
    _null_complement = complement(e1)
    _regular_dual = dual(r1)
    _null_norm = norm(e1)
    _regular_norm = norm(r1)
    try:
        dual(e1)
    except ValueError as _exc:
        _dual_boundary = str(_exc)
    gm.md(rt"""
    The two plane meets are {_null_meet} and {_regular_meet}.
    Complement of the all-null first vector is {_null_complement};
    the Euclidean metric dual of its first vector is {_regular_dual}.

    Their metric norms are **{_null_norm}** and **{_regular_norm}**.
    Calling `dual` in the all-null algebra raises: **{_dual_boundary}**.
    """)
    return


@app.cell
def _(e1, e2, e3, gm, r1, r2, r3, sqrt):
    _null_value = 2 + e1 + (e2 ^ e3)
    _regular_value = 2 + r1 + (r2 ^ r3)
    assert (sqrt(_null_value) * sqrt(_null_value)).almost_equal(_null_value)
    try:
        _regular_value**1.5
    except TypeError:
        _power_boundary = "TypeError"
    try:
        sqrt(_regular_value)
    except ValueError:
        _sqrt_boundary = "ValueError"
    gm.md(t"""
    For the same coefficient pattern, all-null `sqrt` succeeds.
    Euclidean `** 1.5` raises **{_power_boundary}**. The current
    Euclidean `sqrt` supports Study numbers; this mixed-grade value raises
    **{_sqrt_boundary}** because its nonscalar square is nonscalar.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The boundary of the principal real branch

    A positive scalar part makes the finite real power unambiguous. Zero has
    the usual positive powers and identity at exponent zero. A nonzero value
    with zero scalar part can be nilpotent but has no uniformly chosen
    fractional root. A negative scalar part is outside this branch.
    """)
    return


@app.cell
def _(e1, exterior, gm):
    _zero = exterior.scalar(0)
    _zero_root = _zero**0.5
    _zero_to_zero = _zero**0.0
    _boundaries = {}
    for _label, _value, _exponent in (
        ("negative exponent of zero", _zero, -0.5),
        ("zero scalar part", e1, 0.5),
        ("negative scalar part", -1 + e1, 0.5),
    ):
        try:
            _value**_exponent
        except ValueError as _exc:
            _boundaries[_label] = str(_exc)
    gm.md(rt"""
    Zero to the power one half is {_zero_root}; zero to the power zero is
    {_zero_to_zero}.

    - Negative exponent of zero: **{_boundaries['negative exponent of zero']}**
    - Zero scalar part: **{_boundaries['zero scalar part']}**
    - Negative scalar part: **{_boundaries['negative scalar part']}**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Interactive oriented area

    This drawing uses the Euclidean algebra so that metric `norm` measures
    area and `dual` returns the perpendicular vector. The wedge itself
    records orientation in either algebra. When the vectors align, their
    bivector collapses to zero.
    """)
    return


@app.cell
def _(mo):
    angle = mo.ui.slider(start=-180, stop=180, step=1, value=45, label="angle of v")
    length = mo.ui.slider(start=0.2, stop=2.0, step=0.05, value=1.2, label="length of v")
    mo.vstack([angle, length])
    return angle, length


@app.cell
def _(angle, dual, gm, length, norm, np, r1, r2):
    _u = r1.named("u")
    _v = (length.value * (np.cos(np.radians(angle.value)) * r1 + np.sin(np.radians(angle.value)) * r2)).named("v")
    _wedge = _u ^ _v
    _area = norm(_wedge)
    _pseudo_cross = dual(_wedge)
    gm.md(rt"""
    {_u:block}

    {_v:block}

    Oriented area blade: {_wedge}.

    Area magnitude: **{_area}**. Dual vector: {_pseudo_cross}.
    """)
    return


@app.cell
def _(angle, length, np, plt):
    _theta = np.radians(angle.value)
    _u = np.array([1.0, 0.0])
    _v = length.value * np.array([np.cos(_theta), np.sin(_theta)])
    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.quiver(0, 0, _u[0], _u[1], angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012)
    _ax.quiver(0, 0, _v[0], _v[1], angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.012)
    _ax.fill([0, _u[0], _u[0] + _v[0], _v[0]], [0, _u[1], _u[1] + _v[1], _v[1]], color="goldenrod", alpha=0.25)
    _ax.set_aspect("equal")
    _ax.set_xlim(-2.2, 2.2)
    _ax.set_ylim(-2.2, 2.2)
    _ax.set_title("Parallelogram generated by u and v")
    _ax.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig  # noqa: B018 - marimo displays the cell's final expression
    return


if __name__ == "__main__":
    app.run()
