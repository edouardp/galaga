import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga import (
        Algebra,
        DisplayPolicy,
        grade,
        norm,
        inverse,
        exp,
        sandwich,
    )
    import galaga_marimo as gm

    return Algebra, DisplayPolicy, exp, gm, grade, inverse, mo, norm, np, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # galaga_marimo — Examples

    This notebook demonstrates the `galaga_marimo` helper library for rendering
    geometric algebra objects in marimo notebooks using Python 3.14 t-strings.

    The core idea: interpolate GA objects directly into markdown, and they
    automatically render as LaTeX. No manual `.latex()` calls needed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup
    """)
    return


@app.cell
def _(Algebra, exp):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors(expr=True)

    v = 3 * e1 + 2 * e2 - e3
    B = e1 ^ e2
    R = exp(-0.7 * B / 2)

    # Named eager values retain expression provenance.
    v_s = v.named("v")
    R_s = R.named("R")
    return B, R, R_s, alg, e1, e2, e3, v, v_s


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Basic Interpolation

    Any object with a `.latex()` or `._repr_latex_()` method is automatically rendered as inline LaTeX.
    Plain Python values (strings, ints, floats) render as text.
    """)
    return


@app.cell
def _(B, R, e1, gm, v):
    gm.md(t"""
    - A vector: {v}
    - A basis vector: {e1}
    - A bivector: {B}
    - A rotor: {R}
    - A plain string: {"hello"}
    - An integer: {42}
    - A float: {3.14}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Format Specs

    Use format specs to control rendering:

    | Spec | Effect |
    |---|---|
    | `:latex` or `:inline` | Force inline LaTeX |
    | `:block` | Force display-mode LaTeX ($$...$$) |
    | `:text` or `:unicode` | Force plain text (no LaTeX) |
    | `:name`, `:expr`, `:value`, `:full` | Select Galaga semantic content |
    | `:.3f`, `:+.2f`, etc. | Standard formatting for Python numbers |
    """)
    return


@app.cell
def _(gm, norm, np, v):
    gm.md(t"""
    **Numeric format specs:**
    - Pi to 3 decimals: {np.pi:.3f}
    - Signed float: {2.5:+.1f}
    - Percentage: {0.875:.1%}
    - Scientific: {6.022e23:.3e}
    - Integer formatting: {1234567:,}

    **Numeric specs on GA scalars:**
    - Norm with provenance: {norm(v):full}
    - Norm as a Python scalar (3 dp): {float(norm(v)):.3f}
    - Norm² as a Python scalar (1 dp): {float(norm(v)) ** 2:.1f}

    **GA format specs:**
    - Auto (default): {v}
    - Explicit inline: {v:latex}
    - Block display: {v:block}
    - Unicode text: {v:text}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Format Specs on Multivectors

    Multivectors use content/target format specs, not Python's `:.3f`.
    Set `DisplayPolicy(coefficient_precision=3)` for **three significant
    digits**, independently of the selected content. This is not a request
    for three decimal places or for explicitly printing coefficients ±1.

    For fixed decimal places, query an individual coefficient and format
    the resulting Python number. Rendered text is rounded; inspect numeric
    coefficients, not glyphs, when checking equality or numerical error.
    """)
    return


@app.cell
def _(DisplayPolicy, alg, e1, e2, e3, gm):
    w = 1.006 * e1 + 3.462 * e2 - e3
    coefficient_presentation = alg.presentation.with_display(DisplayPolicy(content="value", coefficient_precision=3))
    rounded_latex = w.latex(presentation=coefficient_presentation)

    gm.md(t"""
    - Default value display: {w:value}
    - Three significant digits: ${rounded_latex!s}$
    - The $e_1$ coefficient, three decimal places: {w.coefficient(1):.3f}
    - The $e_3$ coefficient, three decimal places: {w.coefficient(4):.3f}

    These are different rendering requests over the same stored coefficients.
    """)
    return coefficient_presentation, rounded_latex, w


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Conversion Flags

    Standard Python conversion flags (`!s`, `!r`, `!a`) force text mode,
    bypassing LaTeX rendering. Useful for debugging.
    """)
    return


@app.cell
def _(gm, v):
    gm.md(t"""
    - Default (LaTeX): {v}
    - `!s` (str): {v!s}
    - `!r` (repr): {v!r}
    - `!a` (ascii): {v!a}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Expressions over eager values

    `expr=True` records immutable provenance; `.named(...)` supplies a
    semantic name. No symbolic wrapper or delayed evaluation is required.
    Use `:expr` and `:value` to teach the computation and its result separately.
    """)
    return


@app.cell
def _(R_s, gm, grade, v_s):
    sandwich_expr = grade(R_s * v_s * ~R_s, 1)

    gm.md(t"""
    Sandwich expression: {sandwich_expr:expr}

    Computed value: {sandwich_expr:value}

    Combined: {sandwich_expr:full}
    """)
    return (sandwich_expr,)


@app.cell
def _(R_s, alg, gm, np, v_s):
    _double_reverse = ~~v_s
    _rotor_norm = R_s * ~R_s
    np.testing.assert_allclose(_double_reverse.data, v_s.data, atol=1e-12)
    np.testing.assert_allclose(_rotor_norm.data, alg.identity.data, atol=1e-12)
    gm.md(t"""
    **Numeric checks with provenance (not universal symbolic proofs):**

    - Double reverse: {_double_reverse:full}
    - Rotor normalization: {_rotor_norm:full}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Explicit Wrappers

    Use `gm.latex()`, `gm.block_latex()`, and `gm.text()` to override
    auto-detection when needed.
    """)
    return


@app.cell
def _(gm, v):
    gm.md(t"""
    - Force LaTeX on anything: {gm.latex(42)}
    - Force block: {gm.block_latex(v)}
    - Force text on a multivector: {gm.text(v)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## `gm.inline()` and `gm.block()`

    These wrap the entire template in `$...$` or `$$...$$` respectively.
    Everything inside is treated as LaTeX — useful for equations.
    """)
    return


@app.cell
def _(R, gm, v):
    _rotated = R * v * ~R
    gm.inline(t"""R v \\tilde{{R}} = {_rotated:value}""")
    return


@app.cell
def _(R, gm, v):
    rotated = R * v * ~R
    gm.block(t"""R v \\tilde{{R}} = {rotated:value}""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Lists with `mo.vstack`

    For programmatic content, use a list comprehension with `gm.md()` inside `mo.vstack()`.
    Each `gm.md()` returns a marimo Html object.
    """)
    return


@app.cell
def _(e1, e2, exp, gm, mo, np):
    _angles = [0, 30, 45, 60, 90]
    _B = e1 ^ e2

    mo.vstack([gm.md(t"""**θ = {_deg}°:** rotor = {exp(-np.radians(_deg) * _B / 2):value}""") for _deg in _angles])
    return


@app.cell
def _(e1, e2, gm, inverse, mo):
    _a = e1.named("a")
    _b = e2.named("b")

    _exprs = [
        ("Wedge", _a ^ _b),
        ("Inverse", inverse(_a)),
    ]

    mo.vstack([gm.md(t"""**{_name}:** {_e:full}""") for _name, _e in _exprs])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Doc Builder

    For complex documents with mixed loops, conditionals, and prose,
    use `gm.doc()`. It collects rendered t-strings and joins them
    into one markdown block.
    """)
    return


@app.cell
def _(alg, e1, e2, e3, gm):
    _basis = [("e₁", e1), ("e₂", e2), ("e₃", e3)]

    with gm.doc() as _doc:
        _doc.text("### Basis Vector Properties")
        for _index, (_name, _ei) in enumerate(_basis):
            _sq = _ei * _ei
            assert _sq == alg.gram[_index, _index]
            _doc.md(t"""- **{_name}**: {_ei}, square = {_sq:value}""")
        _doc.text("Each square above was checked against the Gram matrix diagonal.")

    _doc.render()
    return


@app.cell
def _(coefficient_presentation, e1, e2, exp, gm, np):
    with gm.doc() as _doc:
        _doc.text("### Rotor Table")
        _doc.text("| Angle | Rotor |")
        _doc.line("|---|---|")
        for _deg in range(0, 361, 45):
            _R = exp(-np.radians(_deg) * (e1 ^ e2) / 2)
            _latex = _R.latex(presentation=coefficient_presentation)
            _doc.md(t"""| {_deg}° | ${_latex!s}$ |""")

    _doc.render()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Mixing with Marimo UI

    `gm.md()` returns a marimo Html object, so it works seamlessly
    with `mo.vstack`, `mo.hstack`, sliders, etc.
    """)
    return


@app.cell
def _(mo):
    theta_slider = mo.ui.slider(start=0, stop=360, step=1, value=45, label="θ (degrees)")
    theta_slider
    return (theta_slider,)


@app.cell
def _(e1, e2, exp, gm, mo, np, sandwich, theta_slider):
    _R = exp(-np.radians(theta_slider.value) * (e1 ^ e2) / 2)
    _v = e1
    _result = sandwich(_R, _v)

    mo.vstack(
        [
            gm.md(t"""**θ = {theta_slider.value}°**"""),
            gm.md(t"""Rotor: {_R}"""),
            gm.md(t"""$e_1$ rotated: {_result}"""),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## HTML Escaping

    Text interpolations are HTML-escaped. They are not a general-purpose
    sanitiser for arbitrary Markdown or LaTeX. Explicit LaTeX wrappers are
    appropriate for trusted mathematical content.
    """)
    return


@app.cell
def _(gm):
    user_input = "<script>alert('xss')</script>"
    gm.md(t"""User said: {user_input}""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Edge Cases
    """)
    return


@app.cell
def _(alg, gm):
    zero = alg.scalar(0.0)
    one = alg.scalar(1.0)
    big = alg.scalar(1e10)

    gm.md(t"""
    - Zero multivector: {zero}
    - Scalar one: {one}
    - Large scalar: {big}
    - None as text: {None}
    - Bool: {True}
    - Empty string: {""}
    """)
    return


if __name__ == "__main__":
    app.run()
