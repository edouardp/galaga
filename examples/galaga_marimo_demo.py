import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "gamo")
    for p in [_root, _gamo]:
        if p not in sys.path:
            sys.path.insert(0, p)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from ga import (
        Algebra, gp, op, grade, reverse, norm, unit, inverse,
        scalar, exp, log, sandwich,
    )
    from ga import symbolic as sym
    Sym = sym.sym
    import galaga_marimo as gm

    return Algebra, Sym, gm, mo, np, sandwich, sym


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    # galaga_marimo — Examples

    This notebook demonstrates the `galaga_marimo` helper library for rendering
    geometric algebra objects in marimo notebooks using Python 3.14 t-strings.

    The core idea: interpolate GA objects directly into markdown, and they
    automatically render as LaTeX. No manual `.latex()` calls needed.
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Setup
    """)
    return


@app.cell
def _(Algebra, Sym):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors()
    I = alg.I

    v = 3 * e1 + 2 * e2 - e3
    B = e1 ^ e2
    R = alg.rotor(B, radians=0.7)

    # Symbolic wrappers
    v_s = Sym(v, "v")
    R_s = Sym(R, "R")
    return B, R, R_s, alg, e1, e2, e3, v, v_s


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Basic Interpolation

    Any object with a `.latex()` method is automatically rendered as inline LaTeX.
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
def _(gm):
    gm.md(t"""
    ## Format Specs

    Use format specs to control rendering:

    | Spec | Effect |
    |---|---|
    | `:latex` or `:inline` | Force inline LaTeX |
    | `:block` | Force display-mode LaTeX ($$...$$) |
    | `:text` or `:unicode` | Force plain text (no LaTeX) |
    | `:.3f`, `:+.2f`, etc. | Standard Python numeric formatting |
    """)
    return


@app.cell
def _(gm, np, v):
    gm.md(t"""
    **Numeric format specs:**
    - Pi to 3 decimals: {np.pi:.3f}
    - Signed float: {2.5:+.1f}
    - Percentage: {0.875:.1%}
    - Scientific: {6.022e23:.3e}
    - Integer formatting: {1234567:,}

    **Numeric specs on GA scalars:**
    - Norm of v (raw): {float(np.sqrt(v.data @ v.data))}
    - Norm of v (3 dp): {float(np.sqrt(v.data @ v.data)):.3f}
    - Norm² of v (1 dp): {float(v.data @ v.data):.1f}

    **GA format specs:**
    - Auto (default): {v}
    - Explicit inline: {v:latex}
    - Block display: {v:block}
    - Unicode text: {v:text}
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Format Specs on Multivectors

    When you apply a numeric format spec like `:.3f` to a multivector,
    **every coefficient** is formatted — including ±1. The default display
    drops the `1` (writing `e₁` instead of `1e₁`), but an explicit format
    spec shows all coefficients literally. This is intentional: if you're
    asking for 3 decimal places, you want to inspect the actual values.
    """)
    return


@app.cell
def _(e1, e2, e3, gm):
    w = 1.006 * e1 + 3.462 * e2 - e3

    gm.md(t"""
    - Default (drop-1 sugar): {w}
    - With `:.3f` (all coefficients shown): {w:.3f}
    - With `:.1f`: {w:.1f}

    Notice `-e₃` vs `-1.000e₃` — the format spec forces explicit coefficients
    so you can verify whether a value is exactly 1.0 or just close to it.
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
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
def _(gm):
    gm.md(t"""
    ## Symbolic Expressions

    Symbolic expression trees also have `.latex()`, so they render automatically.
    """)
    return


@app.cell
def _(R_s, gm, sym, v_s):
    sandwich_expr = sym.grade(R_s * v_s * ~R_s, 1)

    gm.md(t"""
    Sandwich product: {sandwich_expr} = {sandwich_expr.eval()}
    """)
    return


@app.cell
def _(R_s, gm, sym, v_s):
    gm.md(t"""
    **Simplification examples:**
    - Double reverse: {sym.simplify(~~v_s)}
    - Rotor normalization: {sym.simplify(R_s * ~R_s)}
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
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
def _(gm):
    gm.md(t"""
    ## `gm.inline()` and `gm.block()`

    These wrap the entire template in `$...$` or `$$...$$` respectively.
    Everything inside is treated as LaTeX — useful for equations.
    """)
    return


@app.cell
def _(R, gm, v):
    _rotated = R * v * ~R
    gm.inline(t"R v \\tilde{{R}} = {_rotated}")
    return


@app.cell
def _(R, gm, v):
    rotated = R * v * ~R
    gm.block(t"R v \\tilde{{R}} = {rotated}")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Lists with `mo.vstack`

    For programmatic content, use a list comprehension with `gm.md()` inside `mo.vstack()`.
    Each `gm.md()` returns a marimo Html object.
    """)
    return


@app.cell
def _(alg, e1, e2, gm, mo, np):
    angles = [0, 30, 45, 60, 90]
    _B = e1 ^ e2

    mo.vstack([
        gm.md(t"**θ = {deg}°:** rotor = {alg.rotor(_B, np.radians(deg))}")
        for deg in angles
    ])
    return


@app.cell
def _(Sym, e1, e2, gm, mo, sym):
    a = Sym(e1, "a")
    b = Sym(e2, "b")

    exprs = [
        ("Wedge", sym.op(a, b)),
        ("Inverse", sym.inverse(a)),
    ]

    mo.vstack([
        gm.md(t"**{name}:** {e} = {e.eval()}")
        for name, e in exprs
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Doc Builder

    For complex documents with mixed loops, conditionals, and prose,
    use `gm.doc()`. It collects rendered t-strings and joins them
    into one markdown block.
    """)
    return


@app.cell
def _(e1, e2, e3, gm):
    basis = [("e₁", e1), ("e₂", e2), ("e₃", e3)]

    with gm.doc() as _doc:
        _doc.md(t"### Basis Vector Properties")
        for name, ei in basis:
            sq = ei * ei
            _doc.md(t"- **{name}**: {ei}, square = {sq}")
        _doc.md(t"All basis vectors square to $+1$ ✓")

    _doc.render()
    return


@app.cell
def _(alg, e1, e2, gm, np):
    with gm.doc() as _doc:
        _doc.md(t"### Rotor Table")
        _doc.text("| Angle | Rotor |")
        _doc.line("|---|---|")
        for deg in range(0, 361, 45):
            _R = alg.rotor(e1 ^ e2, radians=np.radians(deg))
            _doc.line(f"| {deg}° | ${_R:.3f}$ |")

    _doc.render()
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
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
def _(alg, e1, e2, gm, mo, np, sandwich, theta_slider):
    _R = alg.rotor(e1 ^ e2, radians=np.radians(theta_slider.value))
    _v = e1
    _result = sandwich(_R, _v)

    mo.vstack([
        gm.md(t"**θ = {theta_slider.value}°**"),
        gm.md(t"Rotor: {_R}"),
        gm.md(t"$e_1$ rotated: {_result}"),
    ])
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## HTML Escaping

    Text values are automatically escaped to prevent XSS.
    GA objects (rendered as LaTeX) are trusted.
    """)
    return


@app.cell
def _(gm):
    user_input = "<script>alert('xss')</script>"
    gm.md(t"User said: {user_input}")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
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


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
