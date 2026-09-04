import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    import galaga_anywidget.viz as viz
    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, p_cga, sqrt
    from galaga.cga import ConformalModel

    return Algebra, ConformalModel, DisplayPolicy, gm, mo, p_cga, sqrt, viz


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # A circle from three movable conformal points

    Three direct conformal points determine a direct circle by their outer
    product. The solid points below are editable; the dotted circle is a
    read-only result that is recomputed in Python whenever one of its defining
    points moves.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, DisplayPolicy, p_cga):
    circle_algebra = Algebra(
        config=p_cga(spatial_dim=2),
        display=DisplayPolicy(content="full"),
    )
    circle_cga = ConformalModel(circle_algebra, expr=True)
    return (circle_cga,)


@app.cell
def _(circle_cga, viz):
    circle_viz = viz.CGA2D(
        circle_cga,
        colors=["#0072B2", "#D55E00", "#009E73", "#7C3AED"],
        xlim=(-4.0, 4.0),
        ylim=(-3.0, 3.0),
    )
    return (circle_viz,)


@app.cell
def _(circle_cga, circle_viz):
    _px, _py = circle_viz.coordinates("P", default=(-1.75, -0.75))
    _qx, _qy = circle_viz.coordinates("Q", default=(0.25, 1.5))
    _rx, _ry = circle_viz.coordinates("R", default=(1.75, -0.5))

    P = circle_cga.up(_px, _py).named("P")
    Q = circle_cga.up(_qx, _qy).named("Q")
    R = circle_cga.up(_rx, _ry).named("R")
    return P, Q, R


@app.cell
def _(P, Q, R):
    C = (P ^ Q ^ R).named("C")
    return (C,)


@app.cell
def _(C, P, Q, R, circle_viz):
    circle_viz.display(
        [P, Q, R],
        immutable=[C],
    )
    return


@app.cell
def _(C, P, Q, R, circle_cga, circle_viz, gm, mo, sqrt):
    _circle_center = circle_cga.center(C)
    _euclidean_center = circle_cga.down(_circle_center).named("center")
    _radius_squared = circle_cga.radius_squared(_circle_center)
    _radius = sqrt(_radius_squared).named('radius')

    mo.vstack([
    gm.md(t"""
    ## Live algebra after dragging

    The AnyWidget owns the named Euclidean coordinate pairs for `P`, `Q`, and
    `R`. A drag changes those reactive UI values, so Marimo constructs fresh
    ordinary conformal points and reruns `C = P ^ Q ^ R`.

    $$
    C = P \\wedge Q \\wedge R.
    $$

    {P} <br/>
    {Q} <br/>
    {R} <br/>
    **Calculated Circle**: <br/>
    {C} <br/>
    {_euclidean_center} <br/>
    {_radius}
    """),
    circle_viz])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `circle_viz` is constructed once in a cell that does not depend on `P`,
    `Q`, `R`, or `C`; that same UI element is rendered alongside the live
    algebra. The point cell reads its current named coordinate pairs and uses
    ordinary `circle_cga.up(...)` calls. A separate reactive cell passes the
    resulting multivectors to `circle_viz.display(...)`, which updates the
    existing AnyWidget in place. `immutable=[C]` gives the derived circle a
    dotted stroke and prevents direct manipulation. The widget never
    constructs the circle algebraically: the visible Python wedge remains
    authoritative.
    """)
    return


if __name__ == "__main__":
    app.run()
