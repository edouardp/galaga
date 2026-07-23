import marimo

__generated_with = "0.23.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    from pathlib import Path

    _repository = Path(__file__).resolve().parent.parent.parent
    for _source in (
        _repository,
        _repository / "packages" / "galaga",
        _repository / "packages" / "galaga_marimo",
    ):
        _path = str(_source)
        if _path not in sys.path:
            sys.path.insert(0, _path)
    return


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, inverse, outer_product, p_lengyel_cga
    from galaga.cga import ConformalModel

    return Algebra, ConformalModel, DisplayPolicy, gm, inverse, mo, outer_product, p_lengyel_cga


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CGA reflections and inversions

    Reflections in planes and inversions in spheres are the same conformal
    operation: reflection in a non-null IPNS vector. No CGA-specific numeric
    primitive is required. Galaga uses the ordinary geometric product and
    inverse, while `ConformalModel` supplies the native-null embedding and
    coordinate extraction.

    For an IPNS vector $a$ and conformal point $P$,

    $$P'=-a P a^{-1}.$$

    The minus sign is the standard odd-versor action on vectors. Projective
    coordinates are unchanged by an overall nonzero scale, but this sign also
    keeps the usual positive point weight in these examples.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, DisplayPolicy, p_lengyel_cga):
    algebra = Algebra(
        config=p_lengyel_cga(),
        display=DisplayPolicy(content="full"),
    )
    cga = ConformalModel(algebra, expr=True)
    e1, e2, e3 = cga.euclidean_basis_vectors()
    return cga, e1, e2, e3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reflection in an offset plane

    With $e_o\mathbin{\bullet}e_\infty=-1$, the IPNS plane
    $\pi=e_1+d e_\infty$ represents $x=d$. Reflecting $(3,2,0)$ in the plane
    $x=1$ therefore gives $(-1,2,0)$.
    """)
    return


@app.cell
def _(cga, e1, gm, inverse):
    point = cga.round_point((3, 2, 0)).named("P")
    plane = (e1 + cga.infinity).named(r"\pi")
    reflected = (-plane * point * inverse(plane)).named(
        r"P^{\prime}",
        latex=r"P^{\prime}",
    )
    _reflected_coordinates = cga.coordinates(reflected)

    gm.md(rt"""
    {point}

    {plane}

    {reflected}

    Reflected coordinates: `{_reflected_coordinates!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inversion in a sphere

    An IPNS sphere with center $c$ and radius $r$ is

    $$s=P(c)-\tfrac12 r^2 e_\infty.$$

    `round_point(c, radius_squared=-r²)` constructs exactly this non-null
    vector: the argument is a signed round-point radius, so the negative sign
    selects a real inversion sphere. A point $x$ maps to

    $$c+\frac{r^2(x-c)}{\lVert x-c\rVert^2}.$$
    """)
    return


@app.cell
def _(cga, gm, inverse):
    sphere = cga.round_point((1, 0, 0), radius_squared=-4).named("s")
    source = cga.round_point((5, 0, 0)).named("X")
    inverted = (-sphere * source * inverse(sphere)).named(
        r"X^{\prime}",
        latex=r"X^{\prime}",
    )
    restored = (-sphere * inverted * inverse(sphere)).named(
        r"X^{\prime\prime}",
        latex=r"X^{\prime\prime}",
    )
    _inverted_coordinates = cga.coordinates(inverted)
    _restored_coordinates = cga.coordinates(restored)

    gm.md(rt"""
    {sphere}

    {source}

    {inverted}

    Inverted coordinates: `{_inverted_coordinates!s}`.

    Applying the same inversion twice restores the point:

    {restored}

    Restored coordinates: `{_restored_coordinates!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A line becomes a circle

    Conformal inversion preserves the OPNS grade but changes the geometric
    family. A line not passing through the inversion center becomes a circle
    passing through that center. In 3D both are trivectors, so this transition
    requires no change of storage type.

    A single-vector versor contributes one minus sign for each transformed
    vector. The OPNS line below has grade three, hence its induced action is
    again $-s L s^{-1}$.
    """)
    return


@app.cell
def _(cga, gm, inverse, outer_product):
    _line_a = cga.round_point((-2, 1, 0))
    _line_b = cga.round_point((2, 1, 0))
    line = outer_product(_line_a, _line_b, cga.infinity).named("L")
    unit_sphere = cga.round_point((0, 0, 0), radius_squared=-1).named("S")
    circle = (-unit_sphere * line * inverse(unit_sphere)).named("C")

    _contains_inversion_center = not any(
        abs(float(coefficient)) > 1e-12
        for coefficient in outer_product(cga.origin, circle).data
    )

    gm.md(rt"""
    {line}

    {unit_sphere}

    {circle}

    $C$ contains the inversion center: `{_contains_inversion_center!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Reflection, sphere inversion, and line-to-circle conversion are therefore
    consequences of the same versor action. Keeping them as explicit products
    makes their algebraic relationship visible and avoids adding redundant
    numeric operations to the core.
    """)
    return


if __name__ == "__main__":
    app.run()
