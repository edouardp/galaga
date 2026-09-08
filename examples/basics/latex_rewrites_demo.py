import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, exp, log
    from galaga.expression import Symbol, evaluate, simplify
    from galaga.rendering import tree
    from galaga.rendering.latex import emit

    return Algebra, Symbol, emit, evaluate, exp, gm, log, mo, np, simplify, tree


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # LaTeX layout and expression simplification

    This replaces the old render-tree rewrite demonstration. Galaga 2 builds
    an **immutable semantic layout tree**, then emits LaTeX. Script fractions
    can be compacted during emission, but explicit grouping and signs are
    respected. Rendering is not algebraic simplification.

    We will compare actual multivector expressions with explicit layout
    nodes, so the boundary between those two responsibilities is visible.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors(expr=True)
    return alg, e1, e2, e3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Fractions in superscripts

    A fraction outside a script uses `\frac`. The same fraction inside an
    exponent uses a compact slash. The emitter selects the layout without
    changing the input tree.

    For a Euclidean rotor, the exponent uses a **unit bivector** $B$, with
    $B^2=-1$, and $R=\exp(-\theta B/2)$. Exponentiating a Euclidean vector
    instead would not demonstrate a rotation rotor.
    """)
    return


@app.cell
def _(alg, e1, e2, exp, gm, np):
    _theta = alg.scalar(np.pi / 4, expr=True).named("theta", latex=r"\theta")
    layout_plane = (e1 ^ e2).named("B")
    assert layout_plane * layout_plane == -1
    layout_rotor = exp(-_theta * layout_plane / 2)
    np.testing.assert_allclose((layout_rotor * ~layout_rotor).data, alg.identity.data, atol=1e-12)
    gm.md(t"""Computed rotor: {layout_rotor:full}

    Its generating plane squares to {layout_plane * layout_plane:value}.
    """)
    return layout_plane, layout_rotor


@app.cell
def _(emit, gm, tree):
    _a = tree.Identifier("a")
    _half = tree.Fraction(_a, tree.Literal(2))
    layout_nodes = {
        "Ordinary fraction": _half,
        "Script fraction": tree.Power(tree.Identifier("e"), _half),
        "Explicit nested groups": tree.Group(tree.Group(_a)),
        "Explicit negative numerator": tree.Fraction(tree.Prefix("-", _a), tree.Literal(2)),
        "Explicit denominator one": tree.Fraction(_a, tree.Literal(1)),
    }
    _before = tuple(hash(_node) for _node in layout_nodes.values())
    layout_latex = {_label: emit(_node) for _label, _node in layout_nodes.items()}
    assert tuple(hash(_node) for _node in layout_nodes.values()) == _before
    gm.md(rt"""The same fraction at normal size and in an exponent:

    $${layout_latex["Ordinary fraction"]!s},\qquad {layout_latex["Script fraction"]!s}.$$
    """)
    return layout_latex, layout_nodes


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Explicit grouping is preserved

    `Group(Group(a))` requests two groups. V2 does not silently remove one.
    Ordinary expressions use precedence-aware layout, so callers usually
    need not construct groups themselves.

    ## 3. A negative numerator remains a negative numerator

    `Fraction(Prefix("-", a), 2)` and `Prefix("-", Fraction(a, 2))` are
    different layout requests. They describe equal arithmetic but place the
    sign differently. Emission does not rewrite one into the other.
    """)
    return


@app.cell
def _(gm, layout_latex):
    gm.md(t"""
    Nested groups: $${layout_latex["Explicit nested groups"]!s}.$$

    Negative numerator: $${layout_latex["Explicit negative numerator"]!s}.$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Division by one: value, expression, and layout

    Dividing a multivector by one immediately computes the same value.
    Its provenance still records the division. Calling `simplify` on that
    expression explicitly removes the identity operation. By contrast, a
    hand-built `Fraction(a, 1)` still prints the requested denominator.
    """)
    return


@app.cell
def _(Symbol, alg, e1, evaluate, gm, layout_latex, simplify):
    division_input = e1.named("v")
    divided_by_one = division_input / 1
    simplified_division = simplify(divided_by_one.expr)
    assert divided_by_one == division_input
    assert simplified_division == Symbol(division_input.name)
    assert evaluate(simplified_division, algebra=alg, environment={"v": division_input}) == division_input
    gm.md(t"""Recorded expression: {divided_by_one:expr}

    Already-computed value: {divided_by_one:value}

    Simplification leaves the named input symbol. Replaying that symbol uses
    an explicit environment mapping its name to the concrete input value.

    Explicit layout (not an expression to simplify):

    $${layout_latex["Explicit denominator one"]!s}.$$
    """)
    return divided_by_one, division_input, simplified_division


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Put the layers together

    Named inputs keep the expression readable; `:expr`, `:value`, and `:full`
    select provenance, coefficients, and the combined teaching display.
    None changes the result of the rotation or its logarithm.
    """)
    return


@app.cell
def _(alg, e1, e2, e3, exp, gm, layout_plane, log, np):
    _theta = alg.scalar(np.pi / 3, expr=True).named("theta", latex=r"\theta")
    _v = (3 * e1 + 4 * e2 + e3).named("v")
    _R = exp(-_theta * layout_plane / 2)
    _rotated = _R * _v * ~_R
    gm.md(t"""Rotor: {_R:full}

    Vector: {_v:full}

    Rotation: {_rotated:full}

    Log of rotor: {log(_R):full}
    """)
    return


if __name__ == "__main__":
    app.run()
