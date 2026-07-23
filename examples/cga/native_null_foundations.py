import marimo

__generated_with = "0.23.11"
app = marimo.App()


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
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, p_cga, scalar_product, squared
    from galaga.cga import ConformalModel

    return (
        Algebra,
        ConformalModel,
        DisplayPolicy,
        gm,
        mo,
        np,
        p_cga,
        scalar_product,
        squared,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Native-null CGA foundations

    **Claim:** Galaga can store the conformal origin and infinity as actual
    null basis vectors. There is no hidden orthogonal frame and no
    presentation-time change of basis.

    This notebook constructs the model, verifies its metric, embeds Euclidean
    points, and exercises the homogeneous `up`/`down` mapping.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, DisplayPolicy, p_cga):
    algebra = Algebra(
        config=p_cga(spatial_dim=3, frame="null"),
        display=DisplayPolicy(content="full"),
    )
    cga = ConformalModel(algebra, expr=True)
    e1, e2, e3 = cga.euclidean_basis_vectors()
    eo, einf = cga.origin, cga.infinity
    return algebra, cga, einf, eo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Gram matrix is the model

    The ordered basis is
    $(e_1,e_2,e_3,e_o,e_\infty)$. Its only off-diagonal metric entries are
    $e_o\mathbin{\cdot}e_\infty=e_\infty\mathbin{\cdot}e_o=-1$:

    $$
    G=\begin{bmatrix}
    1&0&0&0&0\\
    0&1&0&0&0\\
    0&0&1&0&0\\
    0&0&0&0&-1\\
    0&0&0&-1&0
    \end{bmatrix}.
    $$
    """)
    return


@app.cell
def _(algebra, einf, eo, gm, scalar_product, squared):
    _eo_squared = squared(eo).named("s_o", latex=r"s_o")
    _einf_squared = squared(einf).named("s_inf", latex=r"s_\infty")
    _null_pair = scalar_product(eo, einf).named("kappa", latex=r"\kappa")
    _gram = algebra.gram

    gm.md(rt"""
    The configured Gram matrix is

    ```text
    {_gram!s}
    ```

    and the null-pair identities are

    {_eo_squared}

    {_einf_squared}

    {_null_pair}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Euclidean vectors and round points

    For $\kappa=e_o\mathbin{\cdot}e_\infty$, the embedding is

    $$
    A(x,r^2)=e_o+x-\frac{x^2+r^2}{2\kappa}e_\infty.
    $$

    The ordinary conformal point $P(x)$ is the case $r^2=0$. A general round
    point has $A(x,r^2)^2=-r^2$.
    """)
    return


@app.cell
def _(cga, gm, squared):
    position = cga.euclidean_vector((1.0, 2.0, -0.5)).named("x")
    point = cga.up(position).named("P")
    round_point = cga.round_point(position, radius_squared=4.0).named("A")
    _point_squared = squared(point)
    _round_squared = squared(round_point)

    gm.md(rt"""
    {position}

    {point}

    {_point_squared}

    {round_point}

    {_round_squared}
    """)
    return point, position


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Distances are inner products

    For ordinary points,
    $P(x)\mathbin{\cdot}P(y)=-\tfrac12\lVert x-y\rVert^2$. The scalar product
    below therefore recovers the ordinary Euclidean squared distance.
    """)
    return


@app.cell
def _(cga, gm, np, point, position, scalar_product):
    _other_position = cga.euclidean_vector((-2.0, 1.0, 0.5)).named("y")
    _other_point = cga.up(_other_position).named("Q")
    _conformal_distance = (-2 * scalar_product(point, _other_point)).named(
        "d^2", latex=r"d^2"
    )
    _coordinate_delta = cga.coordinates(point) - cga.coordinates(_other_point)
    _euclidean_distance = float(np.dot(_coordinate_delta, _coordinate_delta))
    _position_coordinates = cga.coordinates(cga.up(position))

    gm.md(rt"""
    {_other_point}

    {_conformal_distance}

    The Euclidean coordinate calculation gives `{_euclidean_distance:.6g}`.
    The `up`/`coordinates` round trip returns `{_position_coordinates!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Homogeneous scaling

    A conformal point is homogeneous: a nonzero scalar multiple represents
    the same point. `weight` reads its $e_o$ coefficient, `homogenize` (or
    `homo`) restores weight one, and `down` extracts a Euclidean vector.
    """)
    return


@app.cell
def _(cga, gm, point):
    _scaled = (3 * point).named("P_hat", latex=r"\widehat{P}")
    _weight = cga.weight(_scaled).named("w", latex="w")
    _normalized = cga.homo(_scaled).named("P_h", latex=r"P_h")
    _down = cga.down(_normalized).named("x_h", latex=r"x_h")
    _coordinates = cga.coordinates(_normalized)

    gm.md(rt"""
    {_scaled}

    {_weight}

    {_normalized}

    {_down}

    Extracted coordinates: `{_coordinates!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `ConformalModel` adds model semantics, not another algebra. Every value
    above is an ordinary Galaga `Multivector`, and every product is evaluated
    by the same Gram-matrix numeric core used by the other presets.
    """)
    return


if __name__ == "__main__":
    app.run()
