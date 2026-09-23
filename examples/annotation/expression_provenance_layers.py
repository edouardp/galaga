"""Reveal named expression provenance one layer at a time."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import galaga_annotation as ga
    import galaga_marimo as gm
    from galaga import Algebra, Presenter, presets

    return Algebra, Presenter, ga, gm, mo, presets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Reading an expression one provenance layer at a time

    A compact expression is easier to read when useful intermediate objects
    have names. The tradeoff is that a symbol such as $B$ or $x$ hides the
    expression that created it.

    This lesson uses annotations as a **one-level reveal**. The main equation
    keeps its named symbols, while a short rule points from each symbol to its
    defining expression. We can then apply the same idea to one of those
    definitions and step back another layer.
    """)
    return


@app.cell
def _(Algebra, Presenter, presets):
    algebra = Algebra(config=presets.euclidean(3), expr=True)
    e1, e2, e3 = algebra.basis_vectors(expr=True)

    u = (e1 + e2).named("u")
    v = (e2 - e3).named("v")
    B = (u ^ v).named("B")
    x = (e1 + 2 * e3).named("x")
    a = (B * x).named("a")

    full_presenter = Presenter(content="full")
    return B, a, e1, e2, e3, full_presenter, u, v, x


@app.cell
def _(B, a, e1, e2, e3):
    expected_B = (e1 ^ e2) - (e1 ^ e3) - (e2 ^ e3)
    expected_a = -2 * e1 - 3 * e2 + e3 + (e1 ^ e2 ^ e3)
    provenance_verified = B.almost_equal(expected_B) and a.almost_equal(expected_a)
    assert provenance_verified
    return (provenance_verified,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## First reveal: the variables in $a=Bx$

    The middle of a full Galaga display is the retained expression; the
    right-hand side is its evaluated multivector. Here the two variables in
    $Bx$ remain compact, but each is labelled by its own retained expression.
    """)
    return


@app.cell
def _(B, a, full_presenter, ga, gm, provenance_verified, x):
    B_definition = B.latex(content="expr")
    x_definition = x.latex(content="expr")
    top_view = full_presenter(
        ga.annotate(
            a,
            ga.on(
                ga.variable("B"),
                label_latex=B_definition,
                marker="rule",
                color="#0072B2",
                label_color="#0072B2",
            ),
            ga.on(
                ga.variable("x"),
                label_latex=x_definition,
                marker="rule",
                color="#D55E00",
                label_color="#D55E00",
            ),
        )
    )
    gm.md(t"""
    {top_view:block}

    Numeric identity checked independently: **{provenance_verified}**.
    """)
    return B_definition, top_view, x_definition


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The annotations do not expand or rewrite $Bx$. They decorate the recorded
    occurrences of the symbols $B$ and $x$. Their labels are generated from
    `B.latex(content="expr")` and `x.latex(content="expr")`, rather than from
    duplicated handwritten LaTeX.

    ## Second reveal: step into $B=u\wedge v$

    Now use $B$ as the displayed value. Its own expression contains two named
    variables, so the same pattern reveals the definitions of $u$ and $v$.
    """)
    return


@app.cell
def _(B, full_presenter, ga, gm, u, v):
    u_definition = u.latex(content="expr")
    v_definition = v.latex(content="expr")
    plane_view = full_presenter(
        ga.annotate(
            B,
            ga.on(
                ga.variable("u"),
                label_latex=u_definition,
                marker="rule",
                color="#009E73",
                label_color="#009E73",
            ),
            ga.on(
                ga.variable("v"),
                label_latex=v_definition,
                marker="rule",
                color="#7C3AED",
                label_color="#7C3AED",
            ),
        )
    )
    gm.md(t"""
    {plane_view:block}
    """)
    return plane_view, u_definition, v_definition


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The leaf definitions

    At the next level the expressions contain only basis vectors and scalar
    coefficients, so there is no useful named intermediate left to reveal.
    The provenance ladder terminates naturally instead of forcing the main
    equation to inline every earlier calculation.
    """)
    return


@app.cell
def _(full_presenter, gm, u, v, x):
    u_leaf = full_presenter(u)
    v_leaf = full_presenter(v)
    x_leaf = full_presenter(x)
    gm.md(t"""
    {u_leaf:block}

    {v_leaf:block}

    {x_leaf:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why this is preferable to automatic expansion

    - The main equation stays at the abstraction level where it is being used.
    - Every label comes from the symbol's actual retained expression.
    - `ga.variable(...)` follows semantic symbol occurrences, not character
      positions in emitted LaTeX.
    - The evaluated value remains visible, so each abstraction layer can be
      checked against the same numerical result.
    - A notebook author chooses how many layers to reveal; annotations do not
      silently turn a readable expression into a large expanded tree.
    """)
    return


if __name__ == "__main__":
    app.run()
