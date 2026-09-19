"""Target a provenance subtree by matching it structurally."""

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
    # Targeting a subtree by provenance

    Instead of counting operands (`ga.operand(2)`), you can name the subtree you
    mean. `ga.subexpression(value)` compares the recorded provenance tree
    structurally and finds the matching occurrence, so the rule follows an
    edited expression as long as that subtree remains.
    """)
    return


@app.cell
def _(Algebra):
    algebra = Algebra(3, expr=True)
    e1, e2, e3 = algebra.basis_vectors(expr=True)
    R = (1 + e1 * e2).named("R")
    v = (e1 + 2 * e2).named("v")
    result = (R * v * ~R).named("w")
    pair = ((~R) * (~R)).named("p")
    return R, pair, result


@app.cell
def _(R, ga, gm, result):
    view = ga.annotate(
        result,
        ga.on(ga.subexpression(~R), background="#e8f5e9", label="reverse factor"),
    )
    gm.md(t"""
    **The `~R` factor, found by subtree match:** {view:block}

    The same target keeps working if the product gains or loses other factors.
    """)
    return (view,)


@app.cell
def _(R, ga, gm, pair):
    all_occurrences = ga.annotate(pair, ga.on(ga.subexpression(~R), background="#e8f5e9"))
    first_occurrence = ga.annotate(pair, ga.on(ga.subexpression(~R, occurrence=0), color="crimson"))
    gm.md(t"""
    **Every occurrence:** {all_occurrences:block}

    **Only `occurrence=0`:** {first_occurrence:block}
    """)
    return all_occurrences, first_occurrence


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    - `ga.subexpression(...)` matches the recorded provenance tree
      structurally, not numerically: `e1 + e1` and `2 e1` are different trees.
    - It requires a tracked value (`expr=True`); on an untracked value it is an
      invalid request, not an empty match.
    - Use `occurrence=n` when the same subtree appears more than once, or the
      default `"all"` to decorate every copy.
    """)
    return


if __name__ == "__main__":
    app.run()
