"""Annotate the name, expression, and value parts of a teaching display."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():

    import marimo as mo

    import galaga_annotation as ga
    import galaga_marimo as gm
    from galaga import Algebra, geometric_product

    return Algebra, ga, geometric_product, gm, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Targeting the name, expression, and value

    A tracked value can display three parts separated by equals signs:

    $$A = (e_1+e_2)e_1 = 1 - e_{12}$$

    `ga.content("name")`, `ga.content("expr")`, and `ga.content("value")`
    select those parts individually, so a lesson can explain a definition and
    its evaluated result separately.
    """)
    return


@app.cell
def _(Algebra, geometric_product):
    algebra = Algebra(2, expr=True)
    e1, e2 = algebra.basis_vectors(expr=True)
    value = geometric_product(e1 + e2, e1).named("A")
    return (value,)


@app.cell
def _(ga, gm, value):
    view = ga.annotate(
        value,
        ga.on(ga.content("name"), background="#e8f5e9", label="result"),
        ga.on(ga.content("expr"), background="#fff3cd", label="how it was computed"),
        ga.on(ga.content("value"), color="royalblue", label="evaluated", side="below"),
    )
    gm.md(t"""
    **One display, three annotated parts:** {view:block}
    """)
    return


@app.cell
def _(ga, value):
    name_recipe = ga.annotator(ga.on(ga.content("name"), label="result name"))
    full = name_recipe(value).katex(content="full")
    value_only = name_recipe(value).katex(content="value")
    summary = {
        "full: missing": [rule.target.kind for rule in full.missing],
        "value: missing": [rule.target.kind for rule in value_only.missing],
    }
    summary
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The target follows the active content setting: with `content="value"` there
    is no name part, so a `ga.content("name")` rule matches nothing and follows
    the ordinary `missing` policy.

    ## Takeaways

    - `ga.content("name")`, `ga.content("expr")`, and `ga.content("value")`
      address the content parts built from
      `content="name" | "expr" | "value" | "full"`.
    - These are whole-part targets, distinct from expression paths and from
      value-component selectors such as `ga.term(...)`.
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
