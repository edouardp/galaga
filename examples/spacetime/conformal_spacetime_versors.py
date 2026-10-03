"""Conformal spacetime translations and dilations from a null pair."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, BladeConvention, Name, exp, metric_inner_product, sandwich

    return (
        Algebra,
        BladeConvention,
        Name,
        exp,
        gm,
        metric_inner_product,
        mo,
        np,
        sandwich,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Conformal spacetime: moving and scaling events

    The [event and radar lesson](conformal_spacetime_events.py) constructs
    $\mathrm{Cl}(2,4)$ in the basis
    $\{\gamma_0,\gamma_1,\gamma_2,\gamma_3,n_o,n_\infty\}$.
    Here the same Gram matrix lets us **act** on embedded events. A null
    bivector generates translations; the $n_o\wedge n_\infty$ bivector generates
    dilations. We will check each result against the event embedding itself.

    Our conventions are $\gamma_0^2=1$, $\gamma_i^2=-1$,
    $n_o^2=n_\infty^2=0$, and $n_o\cdot n_\infty=-1$.
    """)
    return


@app.cell
def _(Algebra, BladeConvention, Name, metric_inner_product, np):
    gram = np.zeros((6, 6))
    gram[:4, :4] = np.diag([1, -1, -1, -1])
    gram[4, 5] = gram[5, 4] = -1
    _vector_names = tuple(Name(f"g{_i}", f"γ{'₀₁₂₃'[_i]}", rf"\gamma_{_i}") for _i in range(4)) + (
        Name("n_o", "nₒ", r"n_o"),
        Name("n_inf", "n∞", r"n_\infty"),
    )
    _labels = {}
    for _mask in range(1 << 6):
        _parts = [_name for _i, _name in enumerate(_vector_names) if _mask & (1 << _i)]
        _labels[_mask] = Name(
            "".join(_name.ascii for _name in _parts) or "1",
            "∧".join(_name.unicode for _name in _parts) or "1",
            r" \wedge ".join(_name.latex for _name in _parts) or "1",
        )
    csta = Algebra(gram=gram, blades=BladeConvention(6, _labels), expr=True)
    g0, g1, g2, g3, origin, infinity = csta.basis_vectors(expr=True)

    def spacetime(t, x=0.0, y=0.0, z=0.0):
        return t * g0 + x * g1 + y * g2 + z * g3

    def event(t, x=0.0, y=0.0, z=0.0):
        _v = spacetime(t, x, y, z)
        return origin + _v + 0.5 * (_v * _v) * infinity

    def normalize_point(point):
        _weight = -float(metric_inner_product(point, infinity))
        assert abs(_weight) > 1e-12
        return point / _weight

    assert not csta.is_degenerate
    return csta, event, g0, g1, infinity, normalize_point, origin


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Translate an event

    For a spacetime displacement $a$, the translator is

    $$T(a)=\exp(-\tfrac12 a\wedge n_\infty)=1-\tfrac12a n_\infty.$$

    The exponential terminates because $(a\wedge n_\infty)^2=0$. Its
    sandwich action sends $X(x)$ to $X(x+a)$. The slider changes the
    *time* displacement while the spatial displacement remains $1/4$.
    """)
    return


@app.cell
def _(mo):
    time_shift = mo.ui.slider(-1.0, 1.0, step=0.05, value=0.5, label="Time translation")
    time_shift  # noqa: B018 - marimo displays the final expression
    return (time_shift,)


@app.cell
def _(
    csta,
    event,
    exp,
    g0,
    g1,
    gm,
    infinity,
    normalize_point,
    origin,
    sandwich,
    time_shift,
):
    displacement = time_shift.value * g0 + 0.25 * g1
    translator = exp(-0.5 * (displacement ^ infinity))
    source = event(0.75, 0.1)
    moved = normalize_point(sandwich(translator, source))
    expected_move = event(0.75 + time_shift.value, 0.35)
    assert (displacement ^ infinity) ** 2 == 0
    assert translator.almost_equal(1 - 0.5 * displacement * infinity)
    assert (translator * ~translator).almost_equal(csta.scalar(1))
    assert moved.almost_equal(expected_move, atol=1e-10)
    assert normalize_point(sandwich(translator, origin)).almost_equal(event(time_shift.value, 0.25), atol=1e-10)
    gm.md(rt"""
    The computed translator is {translator}.

    Starting from $x=(0.75,0.10)$, the sandwich gives {moved}.
    Directly embedding $x+a$ gives {expected_move}.
    Their coefficients agree to numerical tolerance.
    """)
    return (source,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dilate about the origin

    With scale $\lambda=e^\alpha>0$, set

    $$D(\alpha)=\exp\!\left(\tfrac{\alpha}{2}
    (n_o\wedge n_\infty)\right).$$

    The sandwich produces a *projective* conformal vector. Divide by
    $-D X D^{-1}\cdot n_\infty$ to restore $X\cdot n_\infty=-1$. The result
    should then equal $X(\lambda x)$. The raw sandwich need not have unit
    conformal weight, even though it remains null.
    """)
    return


@app.cell
def _(mo):
    log_scale = mo.ui.slider(-1.0, 1.0, step=0.05, value=0.5, label="Logarithm of scale")
    log_scale  # noqa: B018 - marimo displays the final expression
    return (log_scale,)


@app.cell
def _(
    csta,
    event,
    exp,
    gm,
    infinity,
    log_scale,
    metric_inner_product,
    normalize_point,
    np,
    origin,
    sandwich,
    source,
):
    scale = float(np.exp(log_scale.value))
    dilator = exp(0.5 * log_scale.value * (origin ^ infinity))
    raw_scaled = sandwich(dilator, source)
    scaled = normalize_point(raw_scaled)
    expected_scale = event(0.75 * scale, 0.1 * scale)
    raw_weight = -float(metric_inner_product(raw_scaled, infinity))
    assert (dilator * ~dilator).almost_equal(csta.scalar(1), atol=1e-10)
    assert (raw_scaled * raw_scaled).almost_equal(csta.scalar(0), atol=1e-10)
    assert scaled.almost_equal(expected_scale, atol=1e-10)
    gm.md(rt"""
    $\lambda=e^{{{log_scale.value:.2f}}}={scale:.4f}$.
    The raw conformal weight is **{raw_weight:.4f}**.

    After normalization, the transformed event is {scaled}.
    Direct embedding of $\lambda x$ is {expected_scale}.
    """)
    return (scale,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What happens to intervals?

    Translation preserves the Minkowski squared interval. Dilation scales
    it by $\lambda^2$. In the normalized conformal embedding, both facts
    can be checked using $-2X(a)\cdot X(b)=(a-b)^2$.
    """)
    return


@app.cell
def _(event, gm, metric_inner_product, scale, time_shift):
    _a = event(0.75, 0.1)
    _b = event(0.2, -0.4)
    _before = -2 * float(metric_inner_product(_a, _b))
    _after_translation = -2 * float(
        metric_inner_product(event(0.75 + time_shift.value, 0.35), event(0.2 + time_shift.value, -0.15))
    )
    _after_dilation = -2 * float(
        metric_inner_product(event(0.75 * scale, 0.1 * scale), event(0.2 * scale, -0.4 * scale))
    )
    assert abs(_before - _after_translation) < 1e-10
    assert abs(_after_dilation - scale**2 * _before) < 1e-10
    gm.md(rt"""
    | Pairing-derived squared interval | Value |
    |:--|--:|
    | Before | {_before:.5f} |
    | After translation | {_after_translation:.5f} |
    | After dilation | {_after_dilation:.5f} |

    The dilation ratio is $\lambda^2={scale**2:.5f}$.
    In particular, both transformations preserve the **causal sign**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The $n_o,n_\infty$ plane supplies transformations that ordinary STA does
    not represent as linear isometries of its four spacetime coordinates.
    The algebraic checks above rely only on the displayed Gram matrix.
    This lesson follows the supplied CSTA notes and makes no assumptions
    about a twistor or spinor API.
    """)
    return


if __name__ == "__main__":
    app.run()
