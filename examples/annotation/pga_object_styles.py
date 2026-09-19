"""Interactive semantic highlights for Projective Geometric Algebra objects."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():

    import marimo as mo
    import numpy as np

    import galaga_annotation as ga
    import galaga_marimo as gm
    from galaga import Algebra, complement, exp, p_pga

    return Algebra, complement, exp, ga, gm, mo, np, p_pga


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Projective Geometric Algebra object styles

    PGA is $\mathrm{Cl}(3,0,1)$: three Euclidean basis vectors plus one
    **degenerate** vector $e_0^2=0$. Splitting a value by whether its blades
    contain $e_0$ separates its **Euclidean** part (direction, rotation,
    homogeneous coordinate) from its **projective** part (moment, position,
    translation). For a motor that is rotation versus translation; for a line,
    direction versus moment; for a plane, normal versus offset.
    """)
    return


@app.cell
def _(Algebra, complement, exp, np, p_pga):
    algebra = Algebra(config=p_pga(), expr=True)
    e1, e2, e3, e0 = algebra.basis_vectors(expr=True)
    e0_bit = int(np.flatnonzero(e0.data)[0])
    e123 = e1 ^ e2 ^ e3
    E1 = e2 ^ e3 ^ e0
    E2 = -(e1 ^ e3 ^ e0)
    E3 = e1 ^ e2 ^ e0

    def point(x, y, z=0.0):
        return (e123 + x * E1 + y * E2 + z * E3).named(f"P({x:g},{y:g},{z:g})")

    P, Q, R = point(1, 0, 0), point(0, 1, 0), point(0, 0, 1)
    objects = {
        "point": P,
        "line": (complement(P) ^ complement(Q)).named("L"),
        "plane": (complement(P) ^ complement(Q) ^ complement(R)).named("Pi"),
        "rotor": exp(-0.4 * (e1 * e2)).named("R"),
        "motor": ((1 + 0.5 * e0 * e3) * exp(-0.4 * (e1 * e2))).named("M"),
    }
    return algebra, e0, e0_bit, e1, e2, objects


@app.cell
def _(e0_bit, ga, np):
    def _masks(value):
        return tuple(int(index) for index in np.flatnonzero(value.data))

    def _terms(value, masks):
        return ga.terms(*(value.algebra.blade(mask) for mask in masks))

    def euclidean_projective_rules(value, marker):
        masks = _masks(value)
        euclidean = tuple(mask for mask in masks if not mask & e0_bit)
        projective = tuple(mask for mask in masks if mask & e0_bit)
        rules = []
        if euclidean:
            rules.append(
                ga.on(
                    _terms(value, euclidean),
                    background="#DCEEFF",
                    label="Euclidean",
                    color="#0072B2",
                    marker=marker,
                    join=True,
                )
            )
        if projective:
            rules.append(
                ga.on(
                    _terms(value, projective),
                    background="#FDE7D9",
                    label="projective (e0)",
                    color="#D55E00",
                    marker="undergroup",
                    join=True,
                )
            )
        return rules

    def grade_rules(value):
        palette = {0: "#111827", 1: "#0072B2", 2: "#D55E00", 3: "#009E73", 4: "#CC79A7"}
        return [ga.on(ga.grade(grade), color=colour, join=True) for grade, colour in palette.items()]

    return euclidean_projective_rules, grade_rules


@app.cell
def _(mo):
    object_choice = mo.ui.dropdown(
        ["point", "line", "plane", "rotor", "motor"], value="motor", label="PGA object"
    )
    return (object_choice,)


@app.cell
def _(mo):
    decomposition_choice = mo.ui.dropdown(
        ["euclidean / projective", "grade"], value="euclidean / projective", label="Decomposition"
    )
    return (decomposition_choice,)


@app.cell
def _(mo):
    over_marker = mo.ui.dropdown(
        ["overgroup", "overbrace", "overline", "overbracket"],
        value="overgroup",
        label="Over marker",
    )
    return (over_marker,)


@app.cell
def _(
    decomposition_choice,
    euclidean_projective_rules,
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
        euclidean_projective_rules(value, over_marker.value)
        if decomposition_choice.value == "euclidean / projective"
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
    ## Reading the split

    - **rotor** — scalar and Euclidean bivector only, so it is all Euclidean
      (rotation). A rotor has no projective part.
    - **motor** — the Euclidean part is rotation and the projective part is
      translation.
    - **line** — direction (Euclidean bivector) versus moment (projective
      bivector), the Plücker split.
    - **point / plane** — the homogeneous coordinate versus the offset
      components carrying $e_0$.

    The `grade` decomposition instead colours every grade and does not use an
    over marker.
    """)
    return


@app.cell
def _(euclidean_projective_rules, ga, gm, objects):
    motor = objects["motor"]
    views = {
        marker: ga.annotator(*euclidean_projective_rules(motor, marker))(motor)
        for marker in ("overgroup", "overbrace", "overline", "overbracket")
    }
    gm.md(t"""
    **overgroup:** {views["overgroup"]:block}

    **overbrace:** {views["overbrace"]:block}

    **overline:** {views["overline"]:block}

    **overbracket:** {views["overbracket"]:block}
    """)
    return (views,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    - The split is derived from the basis, not hardcoded: a blade belongs to
      the projective part exactly when it contains the degenerate $e_0$.
    - `over_marker` selects the callout style for the Euclidean label; the
      projective label keeps its under-group.
    - The same recipe covers objects (point, line, plane) and transformations
      (rotor, motor).
    """)
    return


if __name__ == "__main__":
    app.run()
