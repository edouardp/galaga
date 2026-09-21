"""Teach covectors, metric identification, reciprocal bases, and the PGA boundary."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_annotation as ann
    import galaga_marimo as gm
    from galaga import (
        Algebra,
        metric_inner_product,
        outer_product,
        presets,
        right_complement,
    )
    from galaga_matrix import MatrixRepr

    return (
        Algebra,
        MatrixRepr,
        ann,
        gm,
        metric_inner_product,
        mo,
        np,
        outer_product,
        presets,
        right_complement,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Covectors: do we need them in geometric algebra?

    A vector is an element of a vector space $V$. A **covector** is a linear
    measurement of vectors:

    $$
    \alpha:V\longrightarrow\mathbb R,
    \qquad
    v\longmapsto\alpha(v).
    $$

    Gradients, differentials, forces paired with displacements, plane
    equations, and the rows of a Jacobian naturally begin life as covectors.
    Yet geometric-algebra calculations often draw all of them as vectors.

    That shortcut is legitimate only after a metric has identified $V^*$ with
    $V$. This lesson asks what the identification buys us, what coordinate
    mistakes it can hide, and exactly where it fails.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Pairing comes before the metric

    Relative to a basis $e_i$ and its dual basis $\varepsilon^i$,

    $$
    v=v^i e_i,
    \qquad
    \alpha=\alpha_i\varepsilon^i,
    \qquad
    \alpha(v)=\alpha_i v^i.
    $$

    The pairing $V^*\times V\to\mathbb R$ is canonical: it needs no lengths,
    angles, or Gram matrix.

    A metric adds the **flat map**

    $$
    \flat:V\to V^*,
    \qquad
    v^\flat(w)=g(v,w).
    $$

    If the metric is non-degenerate, flat has an inverse called **sharp**:

    $$
    \sharp:V^*\to V,
    \qquad
    g(\alpha^\sharp,v)=\alpha(v).
    $$

    In coordinates, if $G$ is the Gram matrix,

    $$
    [v^\flat]=G[v],
    \qquad
    [\alpha^\sharp]=G^{-1}[\alpha].
    $$

    Galaga has multivectors and metric products rather than a separate
    `Covector` class. In a non-degenerate algebra, we can therefore represent
    $\alpha$ by the vector $\alpha^\sharp$—provided we remember that the metric
    performed the conversion.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, metric_inner_product, np):
    temperature_algebra = Algebra(2, expr=True)
    temperature_e1, temperature_e2 = temperature_algebra.basis_vectors(expr=True)
    temperature_point = np.array([1.0, 2.0])
    temperature_differential_components = np.array([4.0, 9.0])
    temperature_velocity_components = np.array([0.5, -0.25])
    temperature_covector_rate = float(
        temperature_differential_components @ temperature_velocity_components
    )
    temperature_gradient = (4 * temperature_e1 + 9 * temperature_e2).named(
        "grad_T",
        latex=r"\nabla T",
    )
    temperature_velocity = (0.5 * temperature_e1 - 0.25 * temperature_e2).named("v")
    temperature_ga_rate = metric_inner_product(
        temperature_gradient,
        temperature_velocity,
    ).named("dT_p(v)", latex=r"dT_p(v)")
    temperature_rates_agree = bool(
        np.isclose(float(temperature_ga_rate), temperature_covector_rate)
    )
    temperature_differential_matrix = MatrixRepr(
        temperature_differential_components.reshape(1, 2)
    ).name(latex=r"[dT_p]")
    temperature_velocity_matrix = MatrixRepr(
        temperature_velocity_components.reshape(2, 1)
    ).name(latex=r"[v]")
    return (
        temperature_algebra,
        temperature_covector_rate,
        temperature_differential_matrix,
        temperature_e1,
        temperature_e2,
        temperature_ga_rate,
        temperature_gradient,
        temperature_point,
        temperature_rates_agree,
        temperature_velocity,
        temperature_velocity_matrix,
    )


@app.cell
def _(ann, temperature_ga_rate, temperature_gradient):
    temperature_gradient_view = ann.annotate(
        temperature_gradient,
        label=r"metric representative of dT",
        marker="underbrace",
        color="#0072B2",
    )
    temperature_rate_view = ann.annotate(
        temperature_ga_rate,
        ann.on(
            ann.operator("metric_inner_product"),
            label="evaluate the covector",
            marker="overbrace",
            color="#6F42C1",
        ),
    )
    return temperature_gradient_view, temperature_rate_view


@app.cell
def _(
    gm,
    temperature_covector_rate,
    temperature_differential_matrix,
    temperature_gradient_view,
    temperature_point,
    temperature_rate_view,
    temperature_rates_agree,
    temperature_velocity,
    temperature_velocity_matrix,
):
    gm.md(rt"""
    ## 2. A differential measures motion through a field

    Consider the temperature field

    $$T(x,y)=x^2+xy+2y^2.$$

    At $p=({temperature_point[0]:.0f},{temperature_point[1]:.0f})$, its
    differential and a robot's instantaneous velocity have coordinate arrays

    {temperature_differential_matrix:block}

    {temperature_velocity_matrix:block}

    The differential is a covector: it consumes the velocity and reports the
    temperature change per unit time,

    $$dT_p(v)=[4\;9]\begin{{bmatrix}}0.5\\-0.25\end{{bmatrix}}
      ={temperature_covector_rate:.2f}.$$

    In Euclidean coordinates the identity metric turns the same components
    into the familiar gradient vector:

    {temperature_gradient_view:block}

    For {temperature_velocity}, Galaga evaluates the same measurement with the
    metric inner product:

    {temperature_rate_view:block}

    The canonical covector evaluation and the GA computation agree:
    **{temperature_rates_agree}**.

    This is why vector calculus often appears not to need covectors: a Euclidean
    orthonormal basis makes flat and sharp numerically invisible.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Vectors and covectors transform differently

    The distinction becomes operational under a change of coordinates. Suppose
    displayed vector components change by

    $$v'=Jv.$$

    To preserve the scalar pairing, the same covector's components must change
    contragrediently:

    $$
    \alpha'=J^{-T}\alpha,
    \qquad
    \alpha'^T v'=\alpha^T v.
    $$

    Treating the covector as another coordinate column and applying $J$ to it
    generally changes the measurement.
    """)
    return


@app.cell
def _(MatrixRepr, np):
    frame_change = np.array([[1.0, 0.75], [0.0, 1.0]])
    original_vector_components = np.array([2.0, -1.0])
    original_covector_components = np.array([3.0, 4.0])
    transformed_vector_components = frame_change @ original_vector_components
    transformed_covector_components = (
        np.linalg.inv(frame_change).T @ original_covector_components
    )
    wrongly_transformed_covector_components = frame_change @ original_covector_components
    original_pairing = float(original_covector_components @ original_vector_components)
    transformed_pairing = float(
        transformed_covector_components @ transformed_vector_components
    )
    wrong_pairing = float(
        wrongly_transformed_covector_components @ transformed_vector_components
    )
    coordinate_pairing_is_invariant = bool(
        np.isclose(original_pairing, transformed_pairing)
    )
    vector_style_covector_transform_fails = not bool(
        np.isclose(original_pairing, wrong_pairing)
    )
    frame_change_matrix = MatrixRepr(frame_change).name(latex="J")
    transformed_vector_matrix = MatrixRepr(
        transformed_vector_components.reshape(2, 1)
    ).name(latex=r"[v']")
    transformed_covector_matrix = MatrixRepr(
        transformed_covector_components.reshape(1, 2)
    ).name(latex=r"[\alpha']")
    wrong_covector_matrix = MatrixRepr(
        wrongly_transformed_covector_components.reshape(1, 2)
    ).name(latex=r"[\alpha'_{\mathrm{wrong}}]")
    return (
        coordinate_pairing_is_invariant,
        frame_change,
        frame_change_matrix,
        original_covector_components,
        original_pairing,
        original_vector_components,
        transformed_covector_components,
        transformed_covector_matrix,
        transformed_pairing,
        transformed_vector_components,
        transformed_vector_matrix,
        vector_style_covector_transform_fails,
        wrong_covector_matrix,
        wrong_pairing,
        wrongly_transformed_covector_components,
    )


@app.cell
def _(
    coordinate_pairing_is_invariant,
    frame_change_matrix,
    gm,
    original_pairing,
    transformed_covector_matrix,
    transformed_pairing,
    transformed_vector_matrix,
    vector_style_covector_transform_fails,
    wrong_covector_matrix,
    wrong_pairing,
):
    gm.md(rt"""
    Use a shear as the frame change:

    {frame_change_matrix:block}

    The correctly transformed vector and covector components are

    {transformed_vector_matrix:block}

    {transformed_covector_matrix:block}

    Their pairing remains ${transformed_pairing:.1f}$, equal to the original
    ${original_pairing:.1f}$: **{coordinate_pairing_is_invariant}**.

    If the covector is transformed like a vector instead, we get

    {wrong_covector_matrix:block}

    and the pairing changes to ${wrong_pairing:.1f}$. The naive rule fails:
    **{vector_style_covector_transform_fails}**.

    This matters in practice for gradients, constraint Jacobians, generalized
    forces, and back-propagated sensitivities: these are naturally rows or
    covectors, even if a Euclidean metric later turns them into vectors.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. An oblique basis requires reciprocal vectors

    Let $e_1$ and $e_2$ be unit vectors with
    $e_1\mathbin{\bullet}e_2=0.5$. The dual basis satisfies

    $$\varepsilon^i(e_j)=\delta^i{}_j.$$

    Galaga has no covector basis objects, but the metric representatives of
    these covectors are the **reciprocal vectors**

    $$e^i=G^{ij}e_j,$$

    which satisfy $e^i\mathbin{\bullet}e_j=\delta^i{}_j$. The superscript is a
    reminder that $e^i$ is not generally the same vector as $e_i$.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, metric_inner_product, np):
    oblique_gram = np.array([[1.0, 0.5], [0.5, 1.0]])
    oblique_algebra = Algebra(gram=oblique_gram, expr=True)
    oblique_e1, oblique_e2 = oblique_algebra.basis_vectors(expr=True)
    inverse_oblique_gram = np.linalg.inv(oblique_gram)
    reciprocal_e1 = (
        inverse_oblique_gram[0, 0] * oblique_e1
        + inverse_oblique_gram[1, 0] * oblique_e2
    ).named("e^1", latex="e^1")
    reciprocal_e2 = (
        inverse_oblique_gram[0, 1] * oblique_e1
        + inverse_oblique_gram[1, 1] * oblique_e2
    ).named("e^2", latex="e^2")
    reciprocal_pairings = np.array(
        [
            [
                float(metric_inner_product(reciprocal, basis_vector))
                for basis_vector in (oblique_e1, oblique_e2)
            ]
            for reciprocal in (reciprocal_e1, reciprocal_e2)
        ]
    )
    reciprocal_identity_holds = bool(np.allclose(reciprocal_pairings, np.eye(2)))
    reciprocal_pairing_matrix = MatrixRepr(reciprocal_pairings).name(
        latex=r"[e^i\mathbin{\bullet}e_j]"
    )
    oblique_metric_table = oblique_algebra.bilinear_form_table()

    oblique_covector_components = np.array([3.0, 4.0])
    oblique_probe_components = np.array([2.0, -1.0])
    oblique_sharp_components = inverse_oblique_gram @ oblique_covector_components
    oblique_covector_sharp = (
        oblique_sharp_components[0] * oblique_e1
        + oblique_sharp_components[1] * oblique_e2
    ).named("alpha_sharp", latex=r"\alpha^\sharp")
    oblique_probe = (2 * oblique_e1 - oblique_e2).named("v")
    oblique_covector_evaluation = float(
        oblique_covector_components @ oblique_probe_components
    )
    oblique_ga_evaluation = float(
        metric_inner_product(oblique_covector_sharp, oblique_probe)
    )
    oblique_naive_vector = (3 * oblique_e1 + 4 * oblique_e2).named(
        "alpha_naive",
        latex=r"\alpha_{\mathrm{naive}}",
    )
    oblique_naive_evaluation = float(
        metric_inner_product(oblique_naive_vector, oblique_probe)
    )
    oblique_sharp_evaluation_holds = bool(
        np.isclose(oblique_covector_evaluation, oblique_ga_evaluation)
    )
    oblique_naive_identification_fails = not bool(
        np.isclose(oblique_covector_evaluation, oblique_naive_evaluation)
    )
    return (
        inverse_oblique_gram,
        oblique_algebra,
        oblique_covector_components,
        oblique_covector_evaluation,
        oblique_covector_sharp,
        oblique_e1,
        oblique_e2,
        oblique_ga_evaluation,
        oblique_gram,
        oblique_metric_table,
        oblique_naive_evaluation,
        oblique_naive_identification_fails,
        oblique_naive_vector,
        oblique_probe,
        oblique_probe_components,
        oblique_sharp_components,
        oblique_sharp_evaluation_holds,
        reciprocal_e1,
        reciprocal_e2,
        reciprocal_identity_holds,
        reciprocal_pairing_matrix,
        reciprocal_pairings,
    )


@app.cell
def _(ann, oblique_covector_sharp, oblique_naive_vector):
    oblique_sharp_view = ann.annotate(
        oblique_covector_sharp,
        label="raised with the inverse metric",
        marker="underbrace",
        color="#2F7D4F",
    )
    oblique_naive_view = ann.annotate(
        oblique_naive_vector,
        label="same coefficients, wrong vector",
        marker="underbrace",
        color="#D55E00",
    )
    return oblique_naive_view, oblique_sharp_view


@app.cell
def _(
    gm,
    oblique_covector_evaluation,
    oblique_ga_evaluation,
    oblique_metric_table,
    oblique_naive_evaluation,
    oblique_naive_identification_fails,
    oblique_naive_view,
    oblique_probe,
    oblique_sharp_evaluation_holds,
    oblique_sharp_view,
    reciprocal_e1,
    reciprocal_e2,
    reciprocal_identity_holds,
    reciprocal_pairing_matrix,
):
    gm.md(rt"""
    The oblique Gram matrix is

    {oblique_metric_table:block}

    Its reciprocal vectors are

    {reciprocal_e1:block}

    {reciprocal_e2:block}

    Galaga computes all four pairings:

    {reciprocal_pairing_matrix:block}

    so the reciprocal-basis identity holds: **{reciprocal_identity_holds}**.

    Now take the covector $\alpha=3\varepsilon^1+4\varepsilon^2$ and the
    vector {oblique_probe}. Canonical evaluation gives
    $\alpha(v)={oblique_covector_evaluation:.1f}$.

    Raising the covector with $G^{{-1}}$ gives

    {oblique_sharp_view:block}

    and $\alpha^\sharp\mathbin{{\bullet}}v={oblique_ga_evaluation:.1f}$:
    **{oblique_sharp_evaluation_holds}**.

    Merely reusing the covector's two coefficients as vector coefficients gives

    {oblique_naive_view:block}

    whose pairing with $v$ is ${oblique_naive_evaluation:.1f}$ instead. The
    naive identification fails: **{oblique_naive_identification_fails}**.

    So GA can represent this covector perfectly, but only after the inverse
    metric—or equivalently the reciprocal basis—has done real work.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Degenerate PGA is the hard boundary

    In two-dimensional PGA the ordered basis is $(e_1,e_2,e_0)$ and $e_0$ is
    in the radical of the metric:

    $$g(e_0,v)=0\qquad\text{for every }v.$$

    Therefore the flat map has a kernel and no inverse. Consider the perfectly
    valid covector $\varepsilon^0$ that extracts the $e_0$ coordinate:

    $$\varepsilon^0(xe_1+ye_2+we_0)=w.$$

    No vector $a$ can satisfy

    $$g(a,v)=\varepsilon^0(v)\qquad\text{for every }v,$$

    because evaluating at $v=e_0$ would require $0=1$.
    """)
    return


@app.cell
def _(
    Algebra,
    MatrixRepr,
    metric_inner_product,
    np,
    outer_product,
    presets,
    right_complement,
):
    pga_algebra = Algebra(config=presets.pga(2), expr=True)
    pga_e1, pga_e2, pga_e0 = pga_algebra.basis_vectors(expr=True)
    pga_metric_table = pga_algebra.bilinear_form_table()
    pga_e0_pairings = tuple(
        float(metric_inner_product(pga_e0, basis_vector))
        for basis_vector in (pga_e1, pga_e2, pga_e0)
    )
    pga_e0_is_in_metric_kernel = pga_e0_pairings == (0.0, 0.0, 0.0)
    pga_e0_covector_components = np.array([0.0, 0.0, 1.0])
    pga_sharp_candidate, *_ = np.linalg.lstsq(
        pga_algebra.gram,
        pga_e0_covector_components,
        rcond=None,
    )
    pga_sharp_residual = float(
        np.linalg.norm(pga_algebra.gram @ pga_sharp_candidate - pga_e0_covector_components)
    )
    pga_e0_covector_has_no_sharp = not bool(np.isclose(pga_sharp_residual, 0.0))
    pga_covector_matrix = MatrixRepr(pga_e0_covector_components.reshape(1, 3)).name(
        latex=r"[\varepsilon^0]"
    )
    pga_e0_complement = right_complement(pga_e0).named(
        "comp_e0",
        latex=r"\operatorname{comp}(e_0)",
    )
    pga_complement_identity = outer_product(
        pga_e0,
        pga_e0_complement,
    ).almost_equal(pga_algebra.pseudoscalar())
    return (
        pga_algebra,
        pga_complement_identity,
        pga_covector_matrix,
        pga_e0,
        pga_e0_complement,
        pga_e0_covector_components,
        pga_e0_covector_has_no_sharp,
        pga_e0_is_in_metric_kernel,
        pga_e0_pairings,
        pga_e1,
        pga_e2,
        pga_metric_table,
        pga_sharp_candidate,
        pga_sharp_residual,
    )


@app.cell
def _(ann, pga_e0, pga_e0_complement):
    pga_kernel_view = ann.annotate(
        pga_e0,
        label="nonzero vector killed by flat",
        marker="underbrace",
        color="#D55E00",
    )
    pga_complement_view = ann.annotate(
        pga_e0_complement,
        label="metric-independent exterior complement",
        marker="underbrace",
        color="#2F7D4F",
    )
    return pga_complement_view, pga_kernel_view


@app.cell
def _(
    gm,
    pga_complement_identity,
    pga_complement_view,
    pga_covector_matrix,
    pga_e0_covector_has_no_sharp,
    pga_e0_is_in_metric_kernel,
    pga_kernel_view,
    pga_metric_table,
    pga_sharp_residual,
):
    gm.md(rt"""
    Galaga's PGA metric table makes the radical visible:

    {pga_metric_table:block}

    {pga_kernel_view:block}

    All three pairings of $e_0$ with the basis vanish:
    **{pga_e0_is_in_metric_kernel}**.

    The covector that extracts the homogeneous coordinate is

    {pga_covector_matrix:block}

    Solving $G[a]=[\varepsilon^0]$ by least squares leaves residual
    ${pga_sharp_residual:.1f}$, so it has no metric sharp vector:
    **{pga_e0_covector_has_no_sharp}**.

    PGA is not thereby deprived of duality. It uses metric-independent exterior
    complement maps:

    {pga_complement_view:block}

    and Galaga verifies

    $$e_0\wedge\operatorname{{comp}}(e_0)=I:
      \quad \text{{{pga_complement_identity!s}}}.$$

    Complement does **not** pretend that $\varepsilon^0$ has acquired a sharp
    vector. It is a different construction, based on the ordered exterior
    basis rather than an inverse metric. Plane-based and point-based PGA can
    choose a primal or dual exterior algebra as their model; that modeling
    choice should not be confused with raising an index.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. What about differential forms?

    A $k$-form is an alternating covariant object in $\Lambda^kV^*$. With a
    non-degenerate metric, sharp extends grade by grade and lets a GA library
    represent forms as multivectors. That is enough for many algebraic
    identities involving wedge products, contractions, and Hodge duals.

    It is not the whole calculus of forms. Pullbacks, fields over a manifold,
    the exterior derivative $d$, Lie derivatives, and integration retain the
    domain/codomain distinction even when a metric is available. Galaga does
    not currently model those as first-class objects.

    The metric-free insertion operation also starts with a covector:

    $$
    \iota_\alpha:\Lambda^kV\longrightarrow\Lambda^{k-1}V.
    $$

    Galaga's contraction operations accept multivectors because the metric has
    already supplied the relevant sharp/flat identification. The companion
    inner/interior-products lesson follows those convention choices in detail.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Do we need a covector type in Galaga?

    | Use case | Are GA vectors enough? |
    |---|---|
    | Fixed non-degenerate metric, coordinate-free calculation | Usually yes: represent $\alpha$ by $\alpha^\sharp$ |
    | Orthonormal Euclidean coordinates | Yes, but the easy identification can hide the concept |
    | Oblique coordinates | Yes only with $G^{-1}$ or a reciprocal basis |
    | Coordinate changes, Jacobians, gradients, generalized forces | Keep the vector/covector distinction explicit even if storage is shared |
    | Degenerate PGA metric | No metric identification of all covectors exists; use the chosen primal/dual model and complements deliberately |
    | Differential-form calculus | A future explicit covector/form layer would carry useful semantics beyond current multivectors |

    For Galaga's present geometric-algebra operations, a mandatory `Covector`
    runtime type would add ceremony to the common non-degenerate case. The
    current multivector representation is sufficient when the musical
    conversion is understood.

    But covectors are not mathematically redundant. A future API for general
    linear maps, pullbacks, automatic differentiation, or differential forms
    should model $V^*$ explicitly rather than silently treating every row as a
    vector. PGA already demonstrates why the distinction cannot be erased by
    the metric.
    """)
    return


if __name__ == "__main__":
    app.run()
