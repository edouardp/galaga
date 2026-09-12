import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, outer_product, p_cga, scalar_product, squared
    from galaga.cga import ConformalModel

    return (
        Algebra,
        ConformalModel,
        DisplayPolicy,
        gm,
        mo,
        np,
        outer_product,
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

    Continue with [basis order and orientation](basis_order_and_orientation.py)
    for interactive choices, coordinate conversion and worked dual-sign examples.
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
    $(e_o,e_1,e_2,e_3,e_\infty)$. Its only off-diagonal metric entries are
    $e_o\mathbin{\cdot}e_\infty=e_\infty\mathbin{\cdot}e_o=-1$:

    The labelled table below is rendered directly from the algebra.
    """)
    return


@app.cell
def _(algebra, einf, eo, gm, scalar_product, squared):
    _eo_squared = squared(eo).named("s_o", latex=r"s_o")
    _einf_squared = squared(einf).named("s_inf", latex=r"s_\infty")
    _null_pair = scalar_product(eo, einf).named("kappa", latex=r"\kappa")
    _gram = algebra.bilinear_form_table()

    gm.md(rt"""
The configured Gram matrix is

{_gram:block}

and the null-pair identities are

{_eo_squared}

{_einf_squared}

{_null_pair}
""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Native order fixes orientation; display order does not

    Let $I_E=e_1\wedge e_2\wedge e_3$ and define the model's oriented volume by
    $I_C=e_o\wedge I_E\wedge e_\infty$. In the default origin-first basis,
    $I_C=\mathrm{algebra.I}$. These are wedges: using geometric products for
    the nonorthogonal null pair would introduce an unwanted lower-grade term.

    The explicit compatibility choice is
    `p_cga(3, basis_order="euclidean-first")`.
    Moving $e_o$ past three Euclidean axes reverses orientation. In spatial
    dimension $n$, that permutation has sign $(-1)^n$.
    `DisplayOrder` only rearranges printed terms; it cannot make this sign vanish.
    """)
    return


@app.cell
def _(Algebra, ConformalModel, algebra, cga, gm, mo, outer_product, p_cga):
    euclidean_volume = outer_product(*cga.euclidean_basis_vectors())
    null_plane = cga.origin ^ cga.infinity
    conformal_volume = cga.origin ^ euclidean_volume ^ cga.infinity
    assert conformal_volume == algebra.I
    compatibility_algebra = Algebra(config=p_cga(3, basis_order="euclidean-first"))
    _compatibility_model = ConformalModel(compatibility_algebra)
    _ie_old = outer_product(*_compatibility_model.euclidean_basis_vectors())
    _ic_old = _compatibility_model.origin ^ _ie_old ^ _compatibility_model.infinity
    compatibility_orientation = float(_ic_old / compatibility_algebra.I)
    assert compatibility_orientation == -1
    mo.vstack([
        gm.md(t"""
**Default origin-first frame**

$$I_E={euclidean_volume.latex(content="value")!s},\\quad E={null_plane.latex(content="value")!s},\\quad I_C={conformal_volume.latex(content="value")!s}.$$

The computed ratio $I_C/I_{{\\mathrm{{native}}}}$ is $1$.
"""),
        gm.md(t"""
**Compatibility Euclidean-first frame**

{compatibility_algebra.bilinear_form_table():block}

$$I_C={_ic_old.latex(content="value")!s}.$$

The computed ratio $I_C/I_{{\\mathrm{{native}}}}$ is {compatibility_orientation:g}.
Arrays from this frame need an exterior basis conversion before they
can be interpreted in the default frame. Renaming or copying them is
not a conversion.
"""),
    ])
    return compatibility_algebra, compatibility_orientation, conformal_volume, euclidean_volume, null_plane


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Comparison with the familiar orthogonal construction

    Many libraries start with $(e_1,e_2,e_3,e_+,e_-)$, where
    $e_+^2=1$ and $e_-^2=-1$, and derive
    $e_o=(e_- - e_+)/2$, $e_\infty=e_-+e_+$.
    Then $e_o\wedge e_\infty=-e_+\wedge e_-$.
    In 3D the null-pair sign and the three-axis permutation cancel:
    our $I_C$ agrees with that orthogonal native pseudoscalar.
    In 2D it has the opposite sign. The following values are computed in the
    orthogonal algebra, not copied from the native-null coefficient arrays.

    `ConformalModel` currently requires a native-null preset; using derived
    null vectors here does not extend its accepted models.
    """)
    return


@app.cell
def _(Algebra, gm, outer_product, p_cga, scalar_product):
    orthogonal_algebra = Algebra(config=p_cga(3, frame="orthogonal"))
    *_spatial, _plus, _minus = orthogonal_algebra.basis_vectors()
    _origin = (_minus - _plus) / 2
    _infinity = _minus + _plus
    _volume = _origin ^ outer_product(*_spatial) ^ _infinity
    assert _origin * _origin == _infinity * _infinity == 0
    assert scalar_product(_origin, _infinity) == -1
    orthogonal_orientation = float(_volume / orthogonal_algebra.I)
    assert orthogonal_orientation == 1
    gm.md(t"""
$$e_o={_origin.latex(content="value")!s},\\qquad e_\\infty={_infinity.latex(content="value")!s}.$$

$$I_C={_volume.latex(content="value")!s}.$$

The computed ratio to the orthogonal native pseudoscalar is {orthogonal_orientation:g}.
""")
    return orthogonal_algebra, orthogonal_orientation


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
