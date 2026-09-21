"""Interactive semantic highlights for Rigid Geometric Algebra objects."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():

    import marimo as mo
    import numpy as np

    import galaga_annotation as ga
    import galaga_marimo as gm
    from galaga import Algebra, bulk_part, exp, op, p_rga, weight_part
    from galaga.rga import RigidModel

    return Algebra, RigidModel, bulk_part, exp, ga, gm, mo, np, op, p_rga, weight_part


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Rigid Geometric Algebra object styles

    Lengyel's point-based RGA splits every object into a **bulk** (attitude,
    direction, or rotation) part and a **weight** (moment, position, or
    translation) part. `bulk_part` and `weight_part` expose those parts from
    the validated `RigidModel`, and the annotation system labels them with the
    same marker vocabulary used elsewhere.
    """)
    return


@app.cell
def _(Algebra, RigidModel, bulk_part, exp, ga, np, op, p_rga, weight_part):
    rga = RigidModel(Algebra(config=p_rga(), expr=True), expr=True)
    e1, e2, _e3 = rga.euclidean_basis_vectors(expr=True)
    e4 = rga.projective
    objects = {
        "point": rga.point((3.0, 4.0, 0.0)).named("P"),
        "line": op(rga.point((3.0, 4.0, 0.0)), rga.point((1.0, 0.0, 0.0))).named("L"),
        "plane": op(
            rga.point((1.0, 0.0, 0.0)),
            rga.point((0.0, 1.0, 0.0)),
            rga.point((0.0, 0.0, 1.0)),
        ).named("Pi"),
        "motor": ((1 + 0.5 * e1 * e4) * exp(-0.4 * (e1 * e2))).named("M"),
        "flector": (e1 + rga.algebra.blade("e431")).named("F"),
    }
    return e1, e2, e4, objects, rga


@app.cell
def _(bulk_part, ga, np, weight_part):
    def _masks(part):
        return tuple(int(index) for index in np.flatnonzero(part.data))

    def _terms(value, part):
        return ga.terms(*(value.algebra.blade(mask) for mask in _masks(part)))

    def bulk_weight_rules(value, marker):
        rules = []
        bulk, weight = bulk_part(value), weight_part(value)
        if _masks(bulk):
            rules.append(
                ga.on(
                    _terms(value, bulk),
                    background="#DCEEFF",
                    label="bulk (attitude)",
                    color="#0072B2",
                    marker=marker,
                    join=True,
                )
            )
        if _masks(weight):
            rules.append(
                ga.on(
                    _terms(value, weight),
                    background="#FDE7D9",
                    label="weight (moment)",
                    color="#D55E00",
                    marker="underbrace",
                    join=True,
                )
            )
        return rules

    def grade_rules(value):
        palette = {0: "#111827", 1: "#0072B2", 2: "#D55E00", 3: "#009E73", 4: "#CC79A7"}
        return [ga.on(ga.grade(grade), color=colour, join=True) for grade, colour in palette.items()]

    return bulk_weight_rules, grade_rules


@app.cell
def _(mo):
    object_choice = mo.ui.dropdown(
        ["point", "line", "plane", "motor", "flector"], value="motor", label="RGA object"
    )
    return (object_choice,)


@app.cell
def _(mo):
    decomposition_choice = mo.ui.dropdown(
        ["bulk / weight", "grade"], value="bulk / weight", label="Decomposition"
    )
    return (decomposition_choice,)


@app.cell
def _(mo):
    over_marker = mo.ui.dropdown(
        ["overbrace", "overbracket", "overline", "overgroup"],
        value="overbrace",
        label="Over marker",
    )
    return (over_marker,)


@app.cell
def _(
    bulk_weight_rules,
    decomposition_choice,
    ga,
    gm,
    grade_rules,
    mo,
    object_choice,
    objects,
    over_marker,
):
    value = objects[object_choice.value]
    rules = (
        bulk_weight_rules(value, over_marker.value)
        if decomposition_choice.value == "bulk / weight"
        else grade_rules(value)
    )
    view = ga.annotator(*rules)(value)
    mo.vstack(
        [
            mo.hstack([object_choice, decomposition_choice, over_marker]),
            gm.md(t"""
    **{object_choice.value} · {decomposition_choice.value} · `{over_marker.value}`**

    {view:block}
    """),
        ]
    )
    return (view,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Bulk versus weight

    `bulk / weight` is Lengyel's metric split. For a **motor** the bulk part is
    the rotation (scalar + Euclidean bivector) and the weight part is the
    translation (projective bivectors); for a **flector** it is the point and
    the plane. A **point** splits into its Euclidean coordinates and its
    projective weight, a **line** into direction and moment, and a **plane**
    here is pure weight. The `grade` decomposition instead colours every
    grade, and does not use an over marker.
    """)
    return


@app.cell
def _(bulk_weight_rules, ga, gm, objects):
    motor = objects["motor"]
    views = {
        marker: ga.annotator(*bulk_weight_rules(motor, marker))(motor)
        for marker in ("overbrace", "overbracket", "overline", "overgroup")
    }
    gm.md(t"""
    **overbrace:** {views["overbrace"]:block}

    **overbracket:** {views["overbracket"]:block}

    **overline:** {views["overline"]:block}

    **overgroup:** {views["overgroup"]:block}
    """)
    return (views,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    - The object is split from the validated `RigidModel`, not by hardcoded
      blade names: `bulk_part` and `weight_part` decide the terms.
    - `over_marker` defaults to an overbrace for the bulk label; the weight
      label uses an underbrace. Group accents remain explicit alternatives.
    - Motors and flectors satisfy their RGA constraints and are annotated the
      same way as the pure geometric objects.
    """)
    return


if __name__ == "__main__":
    app.run()
