"""Highlight the displayed sign of a term, not its coefficient or blade."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():

    import marimo as mo

    import galaga_annotation as ga
    import galaga_marimo as gm
    from galaga import Algebra

    return Algebra, ga, gm, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Highlighting signs

    `ga.sign(blade)` selects the **displayed sign** of a term, without its
    coefficient or its blade. A sign is a separate slot from the term body, so
    a highlight lands on the `+` or `-` itself. Any rule style works: colour,
    fill, a label, or a marker.
    """)
    return


@app.cell
def _(Algebra):
    algebra = Algebra(3, expr=True)
    e1, e2, e3 = algebra.basis_vectors(expr=True)
    value = (0.5 + 2 * e1 - 3 * (e1 ^ e2) + 0.4 * (e1 ^ e2 ^ e3)).named("A")
    return algebra, e1, e2, e3, value


@app.cell
def _(mo):
    sign_colour = mo.ui.dropdown(
        ["#fff3cd", "#ffd6d6", "#d6ffd6"],
        value="#fff3cd",
        label="sign highlight",
    )
    return (sign_colour,)


@app.cell
def _(e1, e2, ga, gm, mo, sign_colour, value):
    signs_view = ga.annotator(
        ga.on(ga.sign(e1), background=sign_colour.value),
        ga.on(ga.sign(e1 ^ e2), background=sign_colour.value),
    )(value)
    mo.vstack(
        [
            sign_colour,
            gm.md(t"""
    **Two signs, boxed:** {signs_view:block}

    The `+` before $2e_1$ and the `-` before $3e_{12}$ are highlighted on
    their own; coefficients and blades are untouched.
    """),
        ]
    )
    return (signs_view,)


@app.cell
def _(e1, e2, e3, ga, gm, value):
    all_signs = ga.annotate(value, ga.on(ga.signs(e1, e1 ^ e2, e1 ^ e2 ^ e3), color="crimson"))
    gm.md(t"**`ga.signs(...)` colours several signs at once:** {all_signs:block}")
    return


@app.cell
def _(e1, e2, ga, gm, value):
    span_view = ga.annotator(
        ga.on(ga.terms(e1, e1 ^ e2), background="#eeeeee", join=True),
        ga.on(ga.sign(e1 ^ e2), color="crimson"),
    )(value)
    gm.md(t"""
    **A sign inside a joined span:** {span_view:block}

    The fill covers both terms and keeps its own separators; only the sign
    between them is recoloured.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    - `ga.sign(blade)` is the sign counterpart of `ga.coefficient(blade)`:
      the three selectors address the sign, the magnitude, and the whole term.
    - A sign is only selectable when it is visible. A positive leading
      coefficient has no sign, so the rule simply matches nothing.
    - Sign decorations reuse the ordinary styles and markers, so they compose
      with grade fills and joined term spans.
    """)
    return


if __name__ == "__main__":
    app.run()
