"""Explore ordinary plane calculations in a one-pair Witt basis."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from galaga_matrix import MatrixRepr

    import galaga_marimo as gm
    from galaga import Algebra, exp, metric_inner_product

    return Algebra, MatrixRepr, exp, gm, metric_inner_product, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The plane in null coordinates

    Start with two basis vectors $p$ and $q$ whose Gram matrix is

    $$G_s=\begin{pmatrix}0&s\\s&0\end{pmatrix},\qquad s=+1\text{ or }-1.$$

    Both basis vectors have zero square, but they pair with each other.
    We will use this basis for coordinates, products, and transformations,
    then compare the same coefficient pair with a Euclidean plane.
    Changing $s$ simply reverses one null basis direction. The $s=-1$
    choice resembles the origin/infinity pairing used in conformal GA;
    neither choice changes the signature $\mathrm{Cl}(1,1)$.
    This is one Witt pair: the small starting point for the
    [broader Witt lesson](witt_bases_and_null_geometry.py).
    """)
    return


@app.cell
def _(mo):
    sign_control = mo.ui.dropdown({"−1 (CGA-style)": -1, "+1": 1}, value="−1 (CGA-style)", label="Null pairing")
    sign_control  # noqa: B018 - marimo displays the cell's final expression
    return (sign_control,)


@app.cell
def _(Algebra, metric_inner_product, np, sign_control):
    pairing_sign = sign_control.value
    witt = Algebra(gram=np.array([[0.0, pairing_sign], [pairing_sign, 0.0]]), expr=True)
    euclidean = Algebra(2, expr=True)
    p, q = witt.basis_vectors(expr=True)
    e1, e2 = euclidean.basis_vectors(expr=True)
    assert p * p == q * q == 0
    assert p * q + q * p == 2 * pairing_sign
    assert metric_inner_product(p, q) == pairing_sign
    assert not witt.is_degenerate
    return e1, e2, euclidean, p, pairing_sign, q, witt


@app.cell
def _(gm, witt):
    gm.md(rt"""
    {witt.bilinear_form_table():block}

    The determinant is **{float(witt.metric_determinant):g}**, so the form is
    nondegenerate. A null basis vector is not a radical vector: $p$ pairs
    with $q$ even though $p^2=0$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Ordinary coordinates, a different metric

    For $x=ap+bq$ and $y=cp+dq$, their inner product is $s(ad+bc)$,
    their exterior product is $(ad-bc)(p\wedge q)$, and $x^2=2sab$.
    The reciprocal basis is $(q/s,p/s)$: pairing $x$ with $q/s$ recovers $a$,
    while pairing with $p/s$ recovers $b$.

    In Euclidean $\mathrm{Cl}(2,0)$, the same coefficients have square
    $a^2+b^2$. The wedge still records the same oriented coordinate area.
    The Witt plane cannot measure Euclidean distance merely by relabelling
    its vectors.
    """)
    return


@app.cell
def _(mo):
    a_control = mo.ui.slider(-2.0, 2.0, step=0.1, value=1.2, label="p coefficient")
    b_control = mo.ui.slider(-2.0, 2.0, step=0.1, value=0.8, label="q coefficient")
    mo.hstack([a_control, b_control], wrap=True)
    return a_control, b_control


@app.cell
def _(a_control, b_control, e1, e2, euclidean, metric_inner_product, p, pairing_sign, q):
    x = (a_control.value * p + b_control.value * q).named("x")
    x_euclidean = (a_control.value * e1 + b_control.value * e2).named("x_E")
    y = (0.8 * p - 0.6 * q).named("y")
    y_euclidean = (0.8 * e1 - 0.6 * e2).named("y_E")
    witt_square = float(x * x)
    euclidean_square = float(x_euclidean * x_euclidean)
    area_witt = x ^ y
    area_euclidean = x_euclidean ^ y_euclidean
    assert abs(float(metric_inner_product(x, q / pairing_sign)) - a_control.value) < 1e-12
    assert abs(float(metric_inner_product(x, p / pairing_sign)) - b_control.value) < 1e-12
    assert abs(witt_square - 2 * pairing_sign * a_control.value * b_control.value) < 1e-12
    assert abs(euclidean_square - (a_control.value**2 + b_control.value**2)) < 1e-12
    assert abs(area_witt.coefficient(3) - area_euclidean.coefficient(3)) < 1e-12
    assert x_euclidean.algebra is euclidean
    return area_euclidean, area_witt, euclidean_square, witt_square, x, x_euclidean


@app.cell
def _(area_euclidean, area_witt, euclidean_square, gm, witt_square, x, x_euclidean):
    gm.md(rt"""
    The same coordinate pair gives {x} and {x_euclidean}.

    Witt square: **{witt_square:.3g}**. Euclidean square:
    **{euclidean_square:.3g}**.

    Wedge areas: {area_witt} and {area_euclidean}. Their native bivector
    coefficients agree, while their metric squares generally differ.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recover the familiar diagonal basis

    Set $u=(p+sq)/\sqrt2$ and $v=(p-sq)/\sqrt2$. The algebra computes
    $u^2=1$, $v^2=-1$, and $u\cdot v=0$. Thus the off-diagonal Gram matrix
    is a different basis for $\mathrm{Cl}(1,1)$, not a degenerate algebra.
    If $x=ap+bq$, its diagonal coordinates are
    $x_u=(a+sb)/\sqrt2$ and $x_v=(a-sb)/\sqrt2$.
    """)
    return


@app.cell
def _(gm, metric_inner_product, np, p, pairing_sign, q, x):
    u = (p + pairing_sign * q) / np.sqrt(2)
    v = (p - pairing_sign * q) / np.sqrt(2)
    diagonal_u = metric_inner_product(x, u)
    diagonal_v = -metric_inner_product(x, v)
    assert np.isclose(float(u * u), 1)
    assert np.isclose(float(v * v), -1)
    assert np.isclose(float(metric_inner_product(u, v)), 0)
    assert x.almost_equal(diagonal_u * u + diagonal_v * v)
    gm.md(rt"""
    The recovered coordinates are **{float(diagonal_u):.3g}** and
    **{float(diagonal_v):.3g}**. Their signed square
    $x_u^2-x_v^2$ is **{float(diagonal_u) ** 2 - float(diagonal_v) ** 2:.3g}**.
    """)
    return u, v


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Complex versus split-complex numbers

    The even part of Euclidean $\mathrm{Cl}(2,0)$ consists of $a+bI_E$ with
    $I_E^2=-1$, like complex numbers. In this Witt plane the even part also
    has the form $a+bI$, but $I^2=+1$: these are **split-complex numbers**.
    Its exponential uses hyperbolic functions, and it has nonzero zero
    divisors. The full Clifford algebra also includes the vectors $p,q$;
    the number-system comparison concerns its even part.

    See [Oregon State's split-complex notes](https://books.physics.oregonstate.edu/GELG/csplit.html)
    for the number-system viewpoint.
    """)
    return


@app.cell
def _(euclidean, exp, gm, np, p, pairing_sign, q, witt):
    witt_I = witt.I
    euclidean_I = euclidean.I
    split_unit = witt_I / pairing_sign
    positive_projector = (1 + split_unit) / 2
    negative_projector = (1 - split_unit) / 2
    assert witt_I * witt_I == 1
    assert euclidean_I * euclidean_I == -1
    assert positive_projector == (p * q) / (2 * pairing_sign)
    assert negative_projector == (q * p) / (2 * pairing_sign)
    assert positive_projector * positive_projector == positive_projector
    assert negative_projector * negative_projector == negative_projector
    assert positive_projector * negative_projector == 0
    assert (positive_projector + negative_projector) == 1
    _phase = exp(0.7 * euclidean_I)
    _hyperbolic = exp(0.7 * split_unit)
    assert _phase.almost_equal(np.cos(0.7) + np.sin(0.7) * euclidean_I)
    assert _hyperbolic.almost_equal(np.cosh(0.7) + np.sinh(0.7) * split_unit)
    gm.md(rt"""
    Euclidean $I_E^2$ is **{float(euclidean_I * euclidean_I):g}**;
    Witt $I^2$ is **{float(witt_I * witt_I):g}**.

    Complex-like phase: {_phase}. Split-complex exponential:
    {_hyperbolic}.

    The two nonzero projectors {positive_projector} and
    {negative_projector} square to themselves but multiply to zero.
    """)
    return negative_projector, positive_projector


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What the null basis buys us

    The projectors are directly the signed half-products $pq/(2s)$ and
    $qp/(2s)$. The basis vectors themselves are nilpotent ($p^2=q^2=0$),
    although their mutual product is not. From these elements we can build
    the four matrix units of $2\times2$ real matrices. This gives a concrete
    model of the **full** $\mathrm{Cl}(1,1)$, beyond its split-complex even part.
    """)
    return


@app.cell
def _(MatrixRepr, gm, negative_projector, np, p, pairing_sign, positive_projector, q, witt):
    raising = p / (np.sqrt(2) * pairing_sign)
    lowering = q / np.sqrt(2)
    ideal_basis = (positive_projector, lowering)
    _basis_columns = np.column_stack([_value.data for _value in ideal_basis])

    def _left_matrix(operator):
        _action = np.column_stack([(operator * _value).data for _value in ideal_basis])
        _coordinates, _residuals, _rank, _singular = np.linalg.lstsq(_basis_columns, _action, rcond=None)
        assert _rank == 2
        np.testing.assert_allclose(_basis_columns @ _coordinates, _action, rtol=0, atol=1e-12)
        return _coordinates

    raising_matrix = _left_matrix(raising)
    lowering_matrix = _left_matrix(lowering)
    first_projector_matrix = _left_matrix(positive_projector)
    second_projector_matrix = _left_matrix(negative_projector)
    np.testing.assert_allclose(raising_matrix @ raising_matrix, 0, atol=1e-12)
    np.testing.assert_allclose(lowering_matrix @ lowering_matrix, 0, atol=1e-12)
    np.testing.assert_allclose(
        raising_matrix @ lowering_matrix + lowering_matrix @ raising_matrix,
        np.eye(2),
        rtol=0,
        atol=1e-12,
    )
    np.testing.assert_allclose(first_projector_matrix + second_projector_matrix, np.eye(2), atol=1e-12)
    assert (
        np.linalg.matrix_rank(
            np.column_stack(
                [
                    _matrix.reshape(-1)
                    for _matrix in (raising_matrix, lowering_matrix, first_projector_matrix, second_projector_matrix)
                ]
            )
        )
        == 4
    )
    assert (raising * lowering).almost_equal(positive_projector)
    assert (lowering * raising).almost_equal(negative_projector)
    assert raising * raising == lowering * lowering == 0
    assert witt.dim == 4
    gm.md(rt"""
    Acting by left multiplication on the two-dimensional ideal spanned by
    $P=pq/(2s)$ and $q/\sqrt2$ gives matrices derived from Galaga's products:

    $p/(s\sqrt2)$ acts as {MatrixRepr(raising_matrix)};
    $q/\sqrt2$ acts as {MatrixRepr(lowering_matrix)}.

    Their products give the complementary projectors
    {MatrixRepr(first_projector_matrix)} and
    {MatrixRepr(second_projector_matrix)}. The matrices square to zero in
    the off-diagonal cases and span all $2\times2$ real matrices together
    with the two diagonal projectors.
    """)
    return


@app.cell
def _(euclidean, np, plt, witt, x):
    _grid = np.linspace(-2.2, 2.2, 301)
    _a, _b = np.meshgrid(_grid, _grid)
    _witt_level = witt.gram[0, 0] * _a**2 + 2 * witt.gram[0, 1] * _a * _b + witt.gram[1, 1] * _b**2
    _euclidean_level = euclidean.gram[0, 0] * _a**2 + 2 * euclidean.gram[0, 1] * _a * _b + euclidean.gram[1, 1] * _b**2
    _figure, _axes = plt.subplots(1, 2, figsize=(10, 4.5), sharex=True, sharey=True)
    for _axis, _levels, _title in (
        (_axes[0], _witt_level, "Witt square: hyperbolae"),
        (_axes[1], _euclidean_level, "Euclidean square: circles"),
    ):
        _axis.contour(_a, _b, _levels, levels=[-2, -1, 1, 2, 4], colors="0.65", linewidths=0.8)
        _axis.axhline(0, color="0.75", linewidth=0.8)
        _axis.axvline(0, color="0.75", linewidth=0.8)
        _axis.arrow(0, 0, x.vector_part[0], x.vector_part[1], color="royalblue", width=0.018, length_includes_head=True)
        _axis.set_title(_title)
        _axis.set_xlabel("p / first coefficient")
        _axis.set_aspect("equal")
        _axis.grid(alpha=0.15)
    _axes[0].set_ylabel("q / second coefficient")
    _figure.tight_layout()
    _figure  # noqa: B018 - marimo displays the cell's final expression
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The blue arrow is the selected coordinate pair. The contour equations
    come from each algebra's Gram matrix. In the Witt plot the axes themselves
    are null lines; the Euclidean plane has only the origin at zero square.

    The [full Witt lesson](witt_bases_and_null_geometry.py) continues from
    one pair to boosts, Doppler shifts, and several pairs.
    """)
    return


if __name__ == "__main__":
    app.run()
