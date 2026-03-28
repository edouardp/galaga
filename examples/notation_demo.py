import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "galaga_marimo")
    for p in [_root, _gamo]:
        if p not in sys.path:
            sys.path.insert(0, p)
    return


@app.cell
def _():
    import marimo as mo

    return


@app.cell
def _():
    from galaga import Algebra, reverse, involute, conjugate, dual, inverse, squared, exp, grade
    from galaga.notation import Notation, NotationRule
    from galaga.symbolic import simplify
    import galaga_marimo as gm
    import numpy as np

    return (
        Algebra,
        Notation,
        NotationRule,
        conjugate,
        dual,
        exp,
        gm,
        grade,
        inverse,
        involute,
        reverse,
        squared,
    )


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    # Notation System

    Every algebra has a `Notation` object that controls how operations render.
    You can override individual rules or use presets for different textbook
    conventions.
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Default Notation")
    return


@app.cell
def _(
    Algebra,
    conjugate,
    dual,
    exp,
    gm,
    grade,
    inverse,
    involute,
    reverse,
    squared,
):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    _v = e1.name("v")
    _R = (e1 * e2).name("R")
    _B = (e1 ^ e2).name("B")

    with gm.doc() as _d:
        _d.text("| Operation | Unicode | LaTeX |")
        _d.line("|-----------|---------|-------|")
        _ops = [
            ("reverse(v)", reverse(_v)),
            ("involute(v)", involute(_v)),
            ("conjugate(v)", conjugate(_v)),
            ("dual(v)", dual(_v)),
            ("inverse(v)", inverse(_v)),
            ("squared(v)", squared(_v)),
            ("v ^ B", _v ^ _B),
            ("R * v * ~R", _R * _v * ~_R),
            ("grade(R*v*~R, 1)", grade(_R * _v * ~_R, 1)),
            ("exp(B)", exp(_B)),
        ]
        for _label, expr in _ops:
            _d.line(f"| `{_label}` | {expr} | ${expr.latex()}$ |")

    _d.render()
    return alg, e1, e2


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Hestenes Preset

    Hestenes & Sobczyk use dagger (†) for the reverse instead of tilde.
    """)
    return


@app.cell
def _(Algebra, Notation, gm, reverse):
    _alg = Algebra((1, 1, 1), notation=Notation.hestenes())
    _e1, _e2, _ = _alg.basis_vectors(lazy=True)
    _v = _e1.name("v")
    _R = (_e1 * _e2).name("R")

    gm.md(t"""
    With `Notation.hestenes()`:

    - reverse(v) = {reverse(_v)}
    - R * v * ~R = {_R * _v * ~_R}

    Compare default: ṽ vs Hestenes: v†
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Custom Override: Dagger Reverse

    Override just the reverse notation on an existing algebra:
    """)
    return


@app.cell
def _(NotationRule, alg, e1, e2, gm, reverse):
    # Override reverse to use dagger
    alg.notation.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
    alg.notation.set("Reverse", "latex", NotationRule(kind="postfix", symbol="^\\dagger"))

    _v = e1.name("v")
    _R = (e1 * e2).name("R")

    gm.md(t"""
    ```python
    alg.notation.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
    ```

    - reverse(v) = {reverse(_v)}
    - R * v * ~R = {_R * _v * ~_R}
    - LaTeX: ${(_R * _v * ~_R).latex()}$
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Function-Style Notation

    Render operations as function calls instead of symbols:
    """)
    return


@app.cell
def _(Algebra, NotationRule, gm, reverse):
    _alg = Algebra((1, 1, 1))

    # Function-style for several operations
    _alg.notation.set("Reverse", "unicode", NotationRule(kind="function", symbol="rev"))
    _alg.notation.set("Reverse", "latex", NotationRule(kind="function", symbol="rev"))
    _alg.notation.set("Op", "unicode", NotationRule(kind="function", symbol="wedge"))
    _alg.notation.set("Op", "latex", NotationRule(kind="function", symbol="wedge"))

    _e1, _e2, _ = _alg.basis_vectors(lazy=True)
    _v = _e1.name("v")
    _R = (_e1 * _e2).name("R")

    gm.md(t"""
    ```python
    alg.notation.set("Reverse", "unicode", NotationRule(kind="function", symbol="rev"))
    alg.notation.set("Op", "unicode", NotationRule(kind="function", symbol="wedge"))
    ```

    - reverse(v) = {reverse(_v)}
    - e₁ ^ e₂ = {_e1 ^ _e2}
    - R * v * ~R = {_R * _v * ~_R}
    - LaTeX: ${reverse(_v).latex()}$, ${(_e1 ^ _e2).latex()}$
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Prefix Dual

    Some authors write the dual as a prefix star `*v` instead of postfix `v⋆`:
    """)
    return


@app.cell
def _(Algebra, NotationRule, dual, gm):
    _alg = Algebra((1, 1, 1))
    _alg.notation.set("Dual", "unicode", NotationRule(kind="prefix", symbol="*"))
    _alg.notation.set("Dual", "latex", NotationRule(kind="prefix", symbol="*"))

    _e1, _, _ = _alg.basis_vectors(lazy=True)
    _v = _e1.name("v")

    gm.md(t"""
    ```python
    alg.notation.set("Dual", "unicode", NotationRule(kind="prefix", symbol="*"))
    ```

    - dual(v) = {dual(_v)}
    - Default would be: v⋆
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Side-by-Side: Default vs Hestenes")
    return


@app.cell
def _(Algebra, Notation, dual, gm, inverse, reverse):
    _default = Algebra((1, 1, 1))
    _hestenes = Algebra((1, 1, 1), notation=Notation.hestenes())

    _ops = [
        ("reverse", lambda a: reverse(a.basis_vectors(lazy=True)[0].name("v"))),
        ("dual", lambda a: dual(a.basis_vectors(lazy=True)[0].name("v"))),
        ("inverse", lambda a: inverse(a.basis_vectors(lazy=True)[0].name("v"))),
    ]

    with gm.doc() as d:
        d.text("| Operation | Default | Hestenes |")
        d.line("|-----------|---------|----------|")
        for label, fn in _ops:
            d_expr = fn(_default)
            h_expr = fn(_hestenes)
            d.line(f"| {label} | {d_expr} | {h_expr} |")
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## All Rule Kinds

    | Kind | Description | Example |
    |------|-------------|---------|
    | `prefix` | Symbol before operand | `-x`, `*v` |
    | `postfix` | Symbol after operand | `x†`, `x⁻¹` |
    | `accent` | Combining char (atoms) / prefix fallback (compounds) | `ṽ`, `~(a+b)` |
    | `infix` | Symbol between operands | `a∧b`, `a·b` |
    | `function` | Function call style | `rev(v)`, `wedge(a, b)` |
    | `wrap` | Delimiters around content | `⟨x⟩₁`, `exp(x)` |
    | `juxtaposition` | No symbol, smart spacing | `ab`, `pi ve` |
    """)
    return


if __name__ == "__main__":
    app.run()
