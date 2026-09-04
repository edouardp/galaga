import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    import galaga_anywidget.viz as viz
    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, outer_product, p_cga
    from galaga.cga import ConformalModel

    return (
        Algebra,
        ConformalModel,
        DisplayPolicy,
        gm,
        mo,
        outer_product,
        p_cga,
        viz,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Interactive 2D conformal geometry

    This persistent AnyWidget draws direct 2D CGA points, lines, and circles.
    Drag the purple point: the widget synchronizes its Cartesian coordinates
    to Python, where `ConformalModel.up()` constructs the current conformal
    multivector.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, DisplayPolicy, p_cga):
    plane_algebra = Algebra(
        config=p_cga(spatial_dim=2),
        display=DisplayPolicy(content="full"),
    )
    plane_cga = ConformalModel(plane_algebra, expr=True)
    return (plane_cga,)


@app.cell(hide_code=True)
def _(mo, outer_product, plane_cga):
    _point_seed = plane_cga.up(-1.25, 1.0).named("P")
    _line_point_a = plane_cga.up(-2.5, -1.0)
    _line_point_b = plane_cga.up(2.5, 1.5)
    _line_seed = outer_product(
        _line_point_a,
        _line_point_b,
        plane_cga.infinity,
    ).named("L")
    _circle_point_a = plane_cga.up(1.0, 0.0)
    _circle_point_b = plane_cga.up(0.0, 1.0)
    _circle_point_c = plane_cga.up(-1.0, 0.0)
    _circle_seed = outer_product(
        _circle_point_a,
        _circle_point_b,
        _circle_point_c,
    ).named("C")
    initial_cga_values = (_point_seed, _line_seed, _circle_seed)
    get_cga_values, set_cga_values = mo.state(initial_cga_values)
    return get_cga_values, initial_cga_values, set_cga_values


@app.cell(hide_code=True)
def _(initial_cga_values, plane_cga, set_cga_values, viz):
    cga_view = viz.display(
        initial_cga_values,
        model=plane_cga,
        on_values=set_cga_values,
        colors=["#7C3AED", "#EA580C", "#059669"],
        xlim=(-4.0, 4.0),
        ylim=(-3.0, 3.0),
    )
    cga_view
    return (cga_view,)


@app.cell
def _(get_cga_values, gm, plane_cga):
    P, L, C = get_cga_values()
    x = plane_cga.down(P).named("x")

    gm.md(t"""
    ## Synchronized algebra values

    The AnyWidget updates the state containing its current multivectors. This
    cell is reactive, so Marimo reruns these ordinary Python bindings after an
    interaction without reading them back from the rendering object.

    Current direct point:

    {P:block}

    Its Euclidean image under $\\operatorname{{down}}$:

    {x:block}

    The read-only line and circle remain ordinary current values too:

    {L:block}

    {C:block}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This follows the usual AnyWidget pattern: browser interaction updates
    synchronized traitlets, `on_values` replaces the Marimo state tuple, and a
    dependent cell reruns and binds the current algebra values. Galaga
    multivectors remain immutable, but `P` is replaced by the latest `up(x, y)`
    result automatically. `on_change=` remains available when code also needs
    an individual old/new notification.
    """)
    return


if __name__ == "__main__":
    app.run()
