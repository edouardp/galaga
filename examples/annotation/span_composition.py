"""Compose continuous highlights with independent above/below callouts."""

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
    # Composing annotation spans

    A teaching diagram often needs several explanations over the same
    multivector: a continuous colour identifies one semantic family, while a
    brace identifies a related substructure. Those intervals are independent.
    They may be equal, nested in either direction, disjoint, or crossing.

    This lesson builds those layouts from semantic term selectors. The visible
    expression is emitted once; callouts are measured against invisible copies
    of their selected terms.
    """)
    return


@app.cell
def _(Algebra):
    algebra = Algebra(4, expr=True)
    e1, e2, e3, e4 = algebra.basis_vectors()
    value = (e1 + 2 * e2 - 3 * e3 + 4 * e4).without_expr()
    blades = {"e1": e1, "e2": e2, "e3": e3, "e4": e4}
    return blades, e1, e2, e3, e4, value


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One interval model

    Move the callout relative to the green highlight. Crossing a highlight
    boundary does not switch rendering strategies or split the fill.
    """)
    return


@app.cell
def _(mo):
    relationship_choice = mo.ui.dropdown(
        [
            "equal",
            "callout is a subset",
            "highlight is a subset",
            "disjoint",
            "crossing",
        ],
        value="crossing",
        label="Interval relationship",
    )
    marker_choice = mo.ui.dropdown(
        ["overgroup", "overbrace", "overline", "overbracket"],
        value="overbrace",
        label="Callout marker",
    )
    return marker_choice, relationship_choice


@app.cell
def _(blades, ga, gm, marker_choice, mo, relationship_choice, value):
    _intervals = {
        "equal": (("e1", "e2", "e3"), ("e1", "e2", "e3")),
        "callout is a subset": (("e1", "e2", "e3", "e4"), ("e2", "e3")),
        "highlight is a subset": (("e2", "e3"), ("e1", "e2", "e3", "e4")),
        "disjoint": (("e1", "e2"), ("e3", "e4")),
        "crossing": (("e1", "e2", "e3"), ("e3", "e4")),
    }
    _highlight_names, _callout_names = _intervals[relationship_choice.value]
    interactive_view = ga.annotator(
        ga.on(
            ga.terms(*(blades[_name] for _name in _highlight_names)),
            background="#b8e6bf",
            join=True,
        ),
        ga.on(
            ga.terms(*(blades[_name] for _name in _callout_names)),
            label="independent callout",
            marker=marker_choice.value,
            color="#0099cc",
            join=True,
        ),
    )(value)
    mo.vstack(
        [
            mo.hstack([relationship_choice, marker_choice], wrap=True),
            gm.md(t"""
            {interactive_view:block}
            """),
        ],
        gap=2,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The five cases below use the same two rules. Only the selected blade sets
    change. In particular, *crossing* means that neither interval contains the
    other; this is the case a tree of nested LaTeX wrappers cannot express.
    """)
    return


@app.cell
def _(blades, ga, gm, value):
    _relationships = {
        "Equal": (("e1", "e2", "e3"), ("e1", "e2", "e3")),
        "Callout subset": (("e1", "e2", "e3", "e4"), ("e2", "e3")),
        "Highlight subset": (("e2", "e3"), ("e1", "e2", "e3", "e4")),
        "Disjoint": (("e1", "e2"), ("e3", "e4")),
        "Crossing": (("e1", "e2", "e3"), ("e3", "e4")),
    }
    comparison_views = {
        _name: ga.annotator(
            ga.on(
                ga.terms(*(blades[_blade] for _blade in _highlight)),
                background="#fff3cd",
                join=True,
            ),
            ga.on(
                ga.terms(*(blades[_blade] for _blade in _callout)),
                label=_name.lower(),
                marker="overbrace",
                color="#7c3aed",
                join=True,
            ),
        )(value)
        for _name, (_highlight, _callout) in _relationships.items()
    }
    gm.md(t"""
    **Equal:** {comparison_views["Equal"]:block}

    **Callout subset:** {comparison_views["Callout subset"]:block}

    **Highlight subset:** {comparison_views["Highlight subset"]:block}

    **Disjoint:** {comparison_views["Disjoint"]:block}

    **Crossing:** {comparison_views["Crossing"]:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Wide labels stay attached

    KaTeX normally lets a wide annotation label widen the complete over/under
    construct. That would centre a short brace inside the label width and move
    it away from the highlighted terms. External labels contribute no
    horizontal layout width, so they overflow symmetrically while the brace
    remains tied to its selected expression.
    """)
    return


@app.cell
def _(e1, e2, e3, ga, gm):
    wide_label_view = ga.annotator(
        ga.on(ga.terms(e1, e2), background="#fff3cd", join=True),
        ga.on(
            ga.terms(e1, e2),
            label="a much wider explanatory annotation",
            marker="overbrace",
            color="#7c3aed",
            join=True,
        ),
    )((e1 + e2 + e3).without_expr())
    gm.md(t"""
    {wide_label_view:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Three useful layers

    Above and below are independent channels. This permits the main teaching
    layout: one base highlight, one explanation above, and another below. The
    three intervals do not need to share boundaries.
    """)
    return


@app.cell
def _(e1, e2, e3, e4, ga, gm, value):
    three_layer_view = ga.annotator(
        ga.on(ga.terms(e1, e2, e3), background="#b8e6bf", join=True),
        ga.on(
            ga.terms(e2, e3, e4),
            label="structure above",
            marker="overbracket",
            color="#0099cc",
            clearance="2px",
            join=True,
        ),
        ga.on(
            ga.terms(e1, e2),
            label="structure below",
            marker="underbrace",
            color="#7c3aed",
            clearance="5px",
            join=True,
        ),
    )(value)
    gm.md(t"""
    {three_layer_view:block}

    The raised overbracket is visually outside the green fill. Its invisible
    reservation still contributes to the equation's outer KaTeX bounds, so it
    does not intrude into the notebook content above it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Signs belong to the rendered interval

    A minus sign on the first selected term is included in a leading span. A
    sign at a later boundary remains the separator owned by the surrounding
    sum. The marker and highlight therefore agree about where the selected run
    begins without duplicating signs.
    """)
    return


@app.cell
def _(e1, e2, e3, ga, gm):
    negative_value = (-e1 + 2 * e2 - 3 * e3).without_expr()
    negative_view = ga.annotator(
        ga.on(ga.terms(e1, e2), background="#dbeafe", join=True),
        ga.on(
            ga.terms(e1, e2),
            label="the leading minus is part of this run",
            marker="underbrace",
            join=True,
        ),
    )(negative_value)
    gm.md(t"""
    {negative_view:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Deliberate limits

    A single overlapping callout is supported in each vertical channel. Two
    callouts that overlap **on the same side** currently raise
    `SpanLayoutError`; a future layout engine would need explicit lanes and a
    spacing policy. Crossing content fills also need an overlap policy, because
    two backgrounds cannot both own the same separators continuously.

    ```python
    # Raises SpanLayoutError: two overlapping callouts compete above.
    ga.annotator(
        ga.on(ga.terms(e1, e2, e3), label="first", marker="overbrace", join=True),
        ga.on(ga.terms(e2, e3, e4), label="second", marker="overbracket", join=True),
    )(value).latex()
    ```

    ## Takeaways

    - Content styles and external callouts are separate layers.
    - Equal, nested, disjoint, and crossing intervals use one rendering model.
    - Highlight + above + below is supported, including different boundaries.
    - KaTeX reserves the callout's outer height/depth without making the base
      highlight taller.
    - Same-side overlapping callouts fail explicitly until lane stacking has a
      defined design.
    """)
    return


if __name__ == "__main__":
    app.run()
