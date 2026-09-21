"""Interactively choose the CGA cocarrier marker style."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():

    import marimo as mo

    import galaga_annotation as ga
    import galaga_marimo as gm
    from galaga import Algebra, outer_product, presets
    from galaga.cga import ConformalModel

    return Algebra, ConformalModel, ga, gm, mo, outer_product, presets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Cocarrier marker styles

    `ga.highlight_cga(model, over_marker=...)` chooses how the cocarrier
    callouts bracket their terms. The default `overbrace` and the alternative
    `overbracket` give the most reliable teaching layouts. `overline` and
    `overgroup` remain available for lessons that explicitly want them.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, outer_product, presets):
    cga = ConformalModel(Algebra(config=presets.lengyel_cga(), expr=True), expr=True)
    a = cga.up((0.75, 1.0, 2.0))
    b = cga.up((-0.25, 0.1, 0.2))
    c = cga.up((0.0, 1.0, 0.0))
    d = cga.up((0.0, 0.0, 1.0))
    objects = {
        "round point": a.without_expr(),
        "flat point": outer_product(a, cga.infinity).without_expr(),
        "dipole": outer_product(a, b).without_expr(),
        "line": outer_product(a, b, cga.infinity).without_expr(),
        "circle": outer_product(a, b, c).without_expr(),
        "plane": outer_product(a, b, c, cga.infinity).without_expr(),
        "sphere": outer_product(a, b, c, d).without_expr(),
    }
    return cga, objects


@app.cell
def _(mo):
    object_choice = mo.ui.dropdown(
        ["round point", "flat point", "dipole", "line", "circle", "plane", "sphere"],
        value="dipole",
        label="CGA object",
    )
    return (object_choice,)


@app.cell
def _(mo):
    decomposition_choice = mo.ui.dropdown(
        ["incidence", "components"], value="incidence", label="Decomposition"
    )
    return (decomposition_choice,)


@app.cell
def _(mo):
    over_marker = mo.ui.dropdown(
        ["overbrace", "overbracket", "overline", "overgroup"],
        value="overbrace",
        label="Cocarrier marker",
    )
    return (over_marker,)


@app.cell
def _(
    cga,
    decomposition_choice,
    ga,
    gm,
    mo,
    object_choice,
    objects,
    over_marker,
):
    highlight = ga.highlight_cga(cga, decomposition=decomposition_choice.value, over_marker=over_marker.value)
    view = highlight(objects[object_choice.value])
    mo.vstack(
        [
            mo.hstack([object_choice, decomposition_choice, over_marker]),
            gm.md(t"""
    **{object_choice.value} · {decomposition_choice.value} · `{over_marker.value}`**

    {view:block}
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Component versus incidence

    `decomposition` selects the explanatory vocabulary, not the algebra.

    **Component decomposition** (`"components"`) uses Lengyel's four families —
    round weight, round bulk, flat bulk, flat weight — and names each with the
    role it plays for the classified object. A circle reads as *plane part*,
    *center part*, *flat part*, *flat weight*; a sphere as *origin part*,
    *center part*, *flat part*, *flat weight*; a line as *direction* and
    *position*.

    **Incidence decomposition** (`"incidence"`, the default) describes the same
    object by its carrier/cocarrier geometry. Where a specialized layout exists
    (dipoles and circles) it fills the carrier and flat spans, then brackets the
    *cocarrier* subset — the directional part of the carrier, or the
    positional/moment part of the flat. A circle therefore reads as *carrier
    plane*, *cocarrier direction*, *flat line*, *cocarrier moment*; a dipole as
    *carrier line*, *cocarrier normal*, *flat point*, *cocarrier position*.
    Objects without a specialized incidence layout (line, plane, sphere, round
    point) fall back to the component-role names.
    """)
    return


@app.cell
def _(cga, ga, gm, objects):
    component_view = ga.highlight_cga(cga, decomposition="components", over_marker="overbrace")(objects["circle"])
    incidence_view = ga.highlight_cga(cga, decomposition="incidence", over_marker="overbrace")(objects["circle"])
    gm.md(t"""
    **Circle, component families:** {component_view:block}

    **Circle, incidence geometry:** <br/><br/>{incidence_view:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## All four styles side by side

    On the incidence view the marker style changes only the cocarrier callouts;
    the carrier and flat spans keep their fills and labels.
    """)
    return


@app.cell
def _(cga, ga, gm, objects):
    comparison = {
        marker: ga.highlight_cga(cga, over_marker=marker)(objects["dipole"])
        for marker in ("overbrace", "overbracket", "overline", "overgroup")
    }
    gm.md(t"""
    **overbrace:** {comparison["overbrace"]:block}

    **overbracket:** {comparison["overbracket"]:block}

    **overline:** {comparison["overline"]:block}

    **overgroup:** {comparison["overgroup"]:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    - `over_marker` defaults to `overbrace`; `overbracket`, `overline`, and
      `overgroup` remain explicit alternatives. Anything else raises
      `ValueError`.
    - It only affects the incidence decomposition. Component-role views label
      families below and have no over markers.
    - `ga.highlight_object` is an alias of `ga.highlight_cga`.
    """)
    return


if __name__ == "__main__":
    app.run()
