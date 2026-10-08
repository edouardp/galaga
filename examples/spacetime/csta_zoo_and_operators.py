"""CSTA geometry, projectors, nilpotents and verified conformal transformations."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, exp, outer_product, presets, right_hodge_dual, sandwich, scalar_product, squared
    from galaga.models import ConformalSpacetimeModel

    return (
        Algebra,
        ConformalSpacetimeModel,
        exp,
        gm,
        mo,
        np,
        outer_product,
        plt,
        presets,
        right_hodge_dual,
        sandwich,
        scalar_product,
        squared,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The CSTA zoo: objects and operators

    This notebook tours geometric objects in four-dimensional spacetime,
    then explores projectors and transformations in the same algebra.

    ```python
    model.classify(object, representation="direct")
    model.classify_operator(operator)
    ```

    These answer different questions. Geometric blades describe the same
    object after nonzero rescaling. An idempotent satisfies $P^2=P$ at its
    **actual scale**: replacing $P$ by $2P$ usually destroys that property.

    Coordinates are natural with $c=1$, ordered $(t,x,y,z)$. The
    [model and units tour](./csta_model_and_classifiers.py) shows physical
    conversions, including a 1g interpretation of an accelerated worldline.
    """)
    return


@app.cell
def _(Algebra, ConformalSpacetimeModel, presets):
    zoo_algebra = Algebra(config=presets.csta(), expr=True)
    zoo = ConformalSpacetimeModel(zoo_algebra, expr=True)
    time_axis, x_axis, y_axis, z_axis = zoo.spacetime_basis_vectors()
    origin, infinity = zoo.origin, zoo.infinity
    return (
        infinity,
        origin,
        time_axis,
        x_axis,
        y_axis,
        z_axis,
        zoo,
        zoo_algebra,
    )


@app.cell
def _(zoo_algebra):
    zoo_algebra.bilinear_form_table()
    return


@app.cell
def _():
    def geometry_table(model, objects, *, representation="auto"):
        rows = []
        for description, value in objects:
            result = model.classify(value, representation=representation)
            properties = dict(result.properties)
            rows.append(
                f"| {description} | {result.grade if result.grade is not None else '—'} "
                f"| {result.kind} | {result.causal or '—'} "
                f"| {properties.get('carrier_inertia', '—')} | {properties.get('tangent_inertia', '—')} |"
            )
        return "\n".join(rows)

    def operator_table(model, operators, *, max_power=8):
        return "\n".join(
            f"| {description} | {', '.join(result.traits) or '—'} "
            f"| {result.transformation or '—'} | {result.nilpotency_index or '—'} |"
            for description, value in operators
            for result in (model.classify_operator(value, max_power=max_power),)
        )

    return geometry_table, operator_table


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Events, pairs and flats

    The lift is $X(q)=n_o+q+\frac12q^2 n_{\infty}$, and $X(q)^2=0$.
    With $A=X(0)$ and $B=X(q)$:

    $$
    P=A\wedge B,\qquad L=A\wedge B\wedge n_\infty.
    $$

    Non-null pairs describe two events. For null-separated events, the
    grade-2 blade already describes a **lightlike line**: further events on
    that line also satisfy $X(q)\wedge P=0$. Wedging infinity gives its flat
    grade-3 representation.

    Three events plus infinity define a flat 2-plane; four plus infinity a
    flat hyperplane. A timelike plane contains timelike, spacelike and null
    directions. The label describes its **carrier signature**, not every
    direction in it.
    """)
    return


@app.cell
def _(geometry_table, infinity, outer_product, zoo):
    departure = zoo.event(0, 0, 0, 0).named("A")
    temporal_event = zoo.event(1, 0, 0, 0).named("T")
    spatial_event = zoo.event(0, 1, 0, 0).named("S")
    light_event = zoo.event(1, 1, 0, 0).named("N")
    transverse_event = zoo.event(0, 0, 1, 0)
    third_spatial_event = zoo.event(0, 0, 0, 1)
    basic_objects = (
        ("Event", departure),
        ("Flat point", departure ^ infinity),
        ("Timelike pair", departure ^ temporal_event),
        ("Spacelike pair", departure ^ spatial_event),
        ("Null pair / lightlike line", departure ^ light_event),
        ("Timelike flat line", zoo.flat_line(departure, temporal_event)),
        ("Spacelike flat line", zoo.flat_line(departure, spatial_event)),
        ("Null flat line", zoo.flat_line(departure, light_event)),
        ("Timelike 2-plane", outer_product(departure, temporal_event, spatial_event, infinity)),
        ("Spacelike 2-plane", outer_product(departure, spatial_event, transverse_event, infinity)),
        ("Null 2-plane", outer_product(departure, light_event, transverse_event, infinity)),
        ("Timelike hyperplane", outer_product(departure, temporal_event, spatial_event, transverse_event, infinity)),
        (
            "Spacelike hyperplane",
            outer_product(departure, spatial_event, transverse_event, third_spatial_event, infinity),
        ),
        ("Null hyperplane", outer_product(departure, light_event, transverse_event, third_spatial_event, infinity)),
        ("Point at infinity", infinity),
    )
    basic_table = geometry_table(zoo, basic_objects, representation="direct")
    light_pair = departure ^ light_event
    light_pair_incidence = (zoo.event(2, 2, 0, 0) ^ light_pair).almost_equal(zoo.algebra.scalar(0))
    return basic_table, light_pair, light_pair_incidence


@app.cell
def _(basic_table, gm, light_pair, light_pair_incidence):
    gm.md(t"""
    {light_pair:expr}

    An additional event at `(2,2,0,0)` lies on this grade-2 object:
    `{light_pair_incidence!s}`.

    | Construction | Grade | Classification | Causal interpretation | Carrier inertia | Tangent inertia |
    |:--|--:|:--|:--|:--|:--|
    {basic_table}

    Inertias count **(positive, negative, zero)** metric directions. A dash
    means no single causal label is assigned, not that something is null.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Round curves: circle, hyperbola and parabola

    Three suitable events define a round curve:

    $$
    C=X(q_1)\wedge X(q_2)\wedge X(q_3).
    $$

    The carrier metric determines the type. A spacelike carrier gives a
    circle; a Lorentzian carrier gives a hyperbola or null line pair. A null
    carrier can give a parabola. In this example its events satisfy
    $t=x=y^2/2$, $z=0$. Despite its null **carrier**, its tangents are spacelike.

    The accelerated example uses a rotor, with $K=\gamma_1\gamma_0$:

    $$
    R(\tau)=e^{\tau K/2},\qquad
    q(\tau)=-\gamma_1+R(\tau)\gamma_1\widetilde{R(\tau)}.
    $$

    Its hyperbola has timelike tangents. The blade specifies the complete
    curve, while a worldline also needs a branch and proper-time parametrization.
    """)
    return


@app.cell
def _(
    exp,
    geometry_table,
    infinity,
    origin,
    outer_product,
    sandwich,
    time_axis,
    x_axis,
    y_axis,
    zoo,
):
    boost_generator = x_axis * time_axis
    dilation_generator = origin ^ infinity
    circle = outer_product(*(zoo.event(q) for q in ((0, 1, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0))))
    acceleration_events = tuple(
        zoo.event(-x_axis + sandwich(exp(tau * boost_generator / 2), x_axis)) for tau in (0, 0.5, 1)
    )
    acceleration_hyperbola = outer_product(*acceleration_events)
    spacelike_hyperbola = outer_product(
        *(zoo.event(q) for q in ((1, 0, 0, 0), (1.25, 0.75, 0, 0), (5 / 3, 4 / 3, 0, 0)))
    )
    parabola = outer_product(*(zoo.event(q) for q in ((0, 0, 0, 0), (0.5, 0.5, 1, 0), (0.5, 0.5, -1, 0))))
    null_line_pair = outer_product(*(zoo.event(q) for q in ((0, 0, 0, 0), (1, 1, 0, 0), (1, -1, 0, 0))))
    curve_objects = (
        ("Spatial circle", circle),
        ("Accelerated worldline's hyperbola", acceleration_hyperbola),
        ("Hyperbola with spacelike tangents", spacelike_hyperbola),
        ("Parabola", parabola),
        ("Intersecting null line pair", null_line_pair),
        ("Point circle", origin ^ x_axis ^ y_axis),
        ("Imaginary circle", (origin + 0.5 * infinity) ^ x_axis ^ y_axis),
        ("Parallel null lines", (origin - 0.5 * infinity) ^ (time_axis + x_axis) ^ y_axis),
        ("Double null line", origin ^ (time_axis + x_axis) ^ y_axis),
        ("Imaginary parallel null lines", (origin + 0.5 * infinity) ^ (time_axis + x_axis) ^ y_axis),
    )
    curve_table = geometry_table(zoo, curve_objects)
    parabola_incidence = (zoo.event(2, 2, 2, 0) ^ parabola).almost_equal(zoo.algebra.scalar(0))
    return (
        boost_generator,
        curve_table,
        dilation_generator,
        parabola,
        parabola_incidence,
    )


@app.cell
def _(curve_table, gm, parabola, parabola_incidence):
    gm.md(t"""
    {parabola:expr}

    Another parabola event `(2,2,2,0)` passes the wedge-incidence check:
    `{parabola_incidence!s}`.

    | Construction | Grade | Classification | Causal interpretation | Carrier inertia | Tangent inertia |
    |:--|--:|:--|:--|:--|:--|
    {curve_table}

    Imaginary rounds have no real event locus. Point circles are degenerate;
    parallel and double null lines have no unique centre. The classifier
    reports a centre only when the restricted quadratic has a unique one.
    """)
    return


@app.cell
def _(boost_generator, exp, np, plt, sandwich, x_axis, zoo):
    curve_parameters = np.linspace(-2, 2, 100)
    rotor_curve_coordinates = np.array(
        [
            zoo.coordinates(zoo.event(-x_axis + sandwich(exp(tau * boost_generator / 2), x_axis)))
            for tau in curve_parameters
        ]
    )
    curve_figure, curve_axes = plt.subplots(1, 3, figsize=(10, 3), layout="constrained")
    curve_axes[0].plot(np.cos(curve_parameters * np.pi), np.sin(curve_parameters * np.pi))
    curve_axes[0].set(xlabel="x", ylabel="y", title="Circle; t=0", aspect="equal")
    curve_axes[1].plot(rotor_curve_coordinates[:, 1], rotor_curve_coordinates[:, 0])
    curve_axes[1].set(xlabel="x", ylabel="t", title="Timelike hyperbola branch")
    curve_axes[2].plot(curve_parameters, curve_parameters**2 / 2)
    curve_axes[2].set(xlabel="y", ylabel="t=x", title="Parabola in a null carrier")
    curve_figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Round surfaces and full hypersurfaces

    Four independent events define a grade-4 round surface. For a convenient
    direct construction at the origin, use

    $$
    W=n_o+\frac12\rho^2n_\infty,\qquad
    B=W\wedge d_1\wedge d_2\wedge d_3.
    $$

    Here $W^2=-\rho^2$. Events in its span satisfy $q^2=\rho^2$.
    Three spatial directions give a sphere; a Lorentzian 3-carrier gives
    a one-sheet hyperboloid, two-sheet hyperboloid or cone. A one-sheet
    hyperboloid has a mixed tangent metric; a cone has degenerate tangent
    planes. Neither gets a single causal tangent label.

    Full grade-5 hypersurfaces have an IPNS dual vector
    $S=X(c)-\frac12\rho^2n_\infty$, with **the opposite infinity sign** to $W$.
    The vector's incidence equation is $X(q)\cdot S=0$, again giving
    $(q-c)^2=\rho^2$.
    """)
    return


@app.cell
def _(
    geometry_table,
    infinity,
    origin,
    outer_product,
    right_hodge_dual,
    time_axis,
    x_axis,
    y_axis,
    z_axis,
    zoo,
):
    sphere_from_events = outer_product(
        *(zoo.event(q) for q in ((0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (0, -1, 0, 0)))
    )
    surface_objects = (
        ("Sphere from four events", sphere_from_events),
        ("Point sphere", outer_product(origin, x_axis, y_axis, z_axis)),
        ("Imaginary sphere", outer_product(origin + 0.5 * infinity, x_axis, y_axis, z_axis)),
        ("Two-sheet hyperboloid", outer_product(origin + 0.5 * infinity, time_axis, x_axis, y_axis)),
        ("One-sheet hyperboloid", outer_product(origin - 0.5 * infinity, time_axis, x_axis, y_axis)),
        ("Cone section", outer_product(origin, time_axis, x_axis, y_axis)),
        (
            "Paraboloid",
            outer_product(
                *(zoo.event(q) for q in ((0, 0, 0, 0), (0.5, 0.5, 1, 0), (0.5, 0.5, -1, 0), (0.5, 0.5, 0, 1)))
            ),
        ),
        ("Null cylinder", outer_product(origin - 0.5 * infinity, time_axis + x_axis, y_axis, z_axis)),
        ("Collapsed null cylinder", outer_product(origin, time_axis + x_axis, y_axis, z_axis)),
        ("Imaginary null cylinder", outer_product(origin + 0.5 * infinity, time_axis + x_axis, y_axis, z_axis)),
    )
    hypersurface_objects = tuple(
        (description, right_hodge_dual(zoo.signed_round((0, 0, 0, 0), radius)))
        for description, radius in (
            ("Proper-time hyperboloid", 1),
            ("Light cone", 0),
            ("Proper-distance hyperboloid", -1),
        )
    )
    surface_table = geometry_table(zoo, (*surface_objects, *hypersurface_objects))
    sphere_dual = right_hodge_dual(sphere_from_events)
    sphere_dual_class = zoo.classify(sphere_dual, representation="dual")
    event_class = zoo.classify(zoo.event(0, 0, 0, 0), representation="direct")
    cone_class = zoo.classify(zoo.event(0, 0, 0, 0), representation="dual")
    return cone_class, event_class, sphere_dual_class, surface_table


@app.cell
def _(cone_class, event_class, gm, sphere_dual_class, surface_table):
    gm.md(t"""
    | Construction | Grade | Classification | Causal interpretation | Carrier inertia | Tangent inertia |
    |:--|--:|:--|:--|:--|:--|
    {surface_table}

    The sphere's dual has grade `{sphere_dual_class.grade}` and is still named
    `{sphere_dual_class.kind}` when classified with `representation="dual"`.

    The **same vector** at the origin is `{event_class.kind}` in direct form
    and `{cone_class.kind}` in dual form. A zero-radius full signed round is
    a light cone, not a single event. Future/past branches need a time condition.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Projectors and involutions

    Both $K=\gamma_1\gamma_0$ and $E=n_o\wedge n_\infty$ square to one:

    $$
    B_\pm=\frac12(1\pm K),\qquad C_\pm=\frac12(1\pm E).
    $$

    These are complementary idempotents. Multiplication by $P$ projects an
    algebra module because $P(PM)=PM$; it does not necessarily produce an
    event. For example $C_+X(q)$ generally has grades 1 and 3.

    Since $K$ and $E$ commute, their four simultaneous projectors are

    $$
    Q_{s,t}=\frac14(1+sK)(1+tE),\qquad s,t\in\{-1,+1\}.
    $$

    Traits overlap: the identity is idempotent, an involution and a versor.
    The zero element is both idempotent and nilpotent.
    """)
    return


@app.cell
def _(boost_generator, dilation_generator, operator_table, zoo):
    boost_projector = (1 + boost_generator) / 2
    conformal_projector = (1 + dilation_generator) / 2
    joint_projectors = tuple(
        (1 + s * boost_generator) * (1 + t * dilation_generator) / 4 for s in (-1, 1) for t in (-1, 1)
    )
    projector_operators = (
        ("Boost projector", boost_projector),
        ("Complementary boost projector", 1 - boost_projector),
        ("Conformal projector", conformal_projector),
        ("Complementary conformal projector", 1 - conformal_projector),
        ("Twice the conformal projector", 2 * conformal_projector),
        ("Boost involution K", boost_generator),
        ("Conformal involution E", dilation_generator),
        ("Identity", zoo.algebra.scalar(1)),
        ("Zero", zoo.algebra.scalar(0)),
        *((f"Joint projector {index}", value) for index, value in enumerate(joint_projectors, 1)),
    )
    projector_table = operator_table(zoo, projector_operators)
    joint_products_match = all(
        (left * right).almost_equal(left if i == j else zoo.algebra.scalar(0))
        for i, left in enumerate(joint_projectors)
        for j, right in enumerate(joint_projectors)
    )
    joint_sum_matches = sum(joint_projectors).almost_equal(zoo.algebra.scalar(1))
    projected_event = conformal_projector * zoo.event(2, 1, 0, 0)
    projected_event_class = zoo.classify(projected_event)
    return (
        joint_products_match,
        joint_sum_matches,
        projected_event,
        projected_event_class,
        projector_table,
    )


@app.cell
def _(
    gm,
    joint_products_match,
    joint_sum_matches,
    projected_event,
    projected_event_class,
    projector_table,
):
    gm.md(t"""
    | Operator | Traits | Transformation | Nilpotency index |
    |:--|:--|:--|--:|
    {projector_table}

    All sixteen joint products satisfy the projector relations:
    `{joint_products_match!s}`. Their sum is one: `{joint_sum_matches!s}`.

    Left multiplication on an event gives {projected_event:value}, which the
    **geometry** classifier describes as `{projected_event_class.kind}`.
    Idempotents are not future/past selectors or regions of spacetime.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Nilpotents and a bounded search

    Null vectors and some bivectors are nilpotent. Take orthogonal supports:

    $$
    A=(\gamma_0+\gamma_1)\gamma_2,\qquad B=n_o\gamma_3.
    $$

    They have $A^2=B^2=0$ and commute. Thus $N=A+B$ has $N^2=2AB\ne0$
    but $N^3=0$. The classifier computes the powers, rather than inferring
    this from the names.

    `max_power` defaults to 8. A missing index means **no vanishing power
    was found within that bound**. Intermediate rescaling prevents a small
    ordinary scalar from being called nilpotent merely because its powers decay.
    """)
    return


@app.cell
def _(operator_table, origin, time_axis, x_axis, y_axis, z_axis, zoo):
    nilpotent_sum = (time_axis + x_axis) * y_axis + origin * z_axis
    nilpotent_table = operator_table(
        zoo,
        (
            ("Null origin vector", origin),
            ("Index-3 example N", nilpotent_sum),
            ("Small nonnilpotent scalar", zoo.algebra.scalar(0.001)),
        ),
    )
    short_nilpotency_index = zoo.classify_operator(nilpotent_sum, max_power=2).nilpotency_index
    return nilpotent_table, short_nilpotency_index


@app.cell
def _(gm, nilpotent_table, short_nilpotency_index):
    gm.md(t"""
    | Operator | Traits | Transformation | Nilpotency index |
    |:--|:--|:--|--:|
    {nilpotent_table}

    With `max_power=2`, the index-3 example returns `{short_nilpotency_index!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Verified transformations and spectral projectors

    An even normalized versor acts by $X\mapsto V X\widetilde V$.
    Classification also accepts scaled versors and odd versors; it verifies
    the normalized **twisted adjoint** $v\mapsto\alpha(V)vV^{-1}$ on all six
    basis vectors. The action must remain vector-valued and preserve the Gram
    matrix. A unit reverse norm alone is insufficient in six dimensions.

    The boost and dilation projectors resolve their exponentials:

    $$
    e^{\eta K/2}=e^{\eta/2}B_++e^{-\eta/2}B_-,\qquad
    e^{\lambda E/2}=e^{\lambda/2}C_++e^{-\lambda/2}C_-.
    $$

    Boosts change rapidity; dilations scale all spacetime coordinates.
    Transformation names refer to this model's frame and distinguished
    origin/infinity. Compositions can have several reported components.
    """)
    return


@app.cell
def _(
    boost_generator,
    dilation_generator,
    exp,
    infinity,
    np,
    operator_table,
    origin,
    x_axis,
    y_axis,
    zoo,
):
    zoo_boost = exp(0.4 * boost_generator)
    zoo_rotation = exp(0.4 * x_axis * y_axis)
    zoo_translation = exp(infinity * x_axis / 2)
    zoo_dilation = exp(0.3 * dilation_generator / 2)
    zoo_special = exp(origin * x_axis / 2)
    zoo_inversion = origin + 0.5 * infinity
    zoo_combined = zoo_translation * zoo_dilation * zoo_boost
    transformation_table = operator_table(
        zoo,
        (
            ("Boost", zoo_boost),
            ("Spatial rotation", zoo_rotation),
            ("Translation", zoo_translation),
            ("Dilation", zoo_dilation),
            ("Special conformal map", zoo_special),
            ("Inversion", zoo_inversion),
            ("Spatial reflection", x_axis),
            ("Translation × dilation × boost", zoo_combined),
            ("Scaled boost", 2 * zoo_boost),
        ),
    )
    combined_components = dict(zoo.classify_operator(zoo_combined).properties)["components"]
    boost_spectral_check = zoo_boost.almost_equal(
        np.exp(0.4) * (1 + boost_generator) / 2 + np.exp(-0.4) * (1 - boost_generator) / 2
    )
    dilation_spectral_check = zoo_dilation.almost_equal(
        np.exp(0.15) * (1 + dilation_generator) / 2 + np.exp(-0.15) * (1 - dilation_generator) / 2
    )
    false_versor = exp(0.3 * zoo.algebra.blade((1 << zoo.algebra.n) - 1))
    false_versor_norm = (false_versor * ~false_versor).almost_equal(zoo.algebra.scalar(1))
    false_versor_traits = zoo.classify_operator(false_versor).traits
    return (
        boost_spectral_check,
        combined_components,
        dilation_spectral_check,
        false_versor_norm,
        false_versor_traits,
        transformation_table,
    )


@app.cell
def _(
    boost_spectral_check,
    combined_components,
    dilation_spectral_check,
    false_versor_norm,
    false_versor_traits,
    gm,
    transformation_table,
):
    gm.md(t"""
    | Operator | Traits | Transformation | Nilpotency index |
    |:--|:--|:--|--:|
    {transformation_table}

    Combined components: `{combined_components!s}`.

    Computed spectral identities: boost `{boost_spectral_check!s}`,
    dilation `{dilation_spectral_check!s}`.

    `exp(0.3 * I6)` has unit reverse norm: `{false_versor_norm!s}`, but its
    operator traits are `{false_versor_traits!s}`. Its basis action includes
    grade-5 parts, so it is not recognized as a versor.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Geometric projection is a different operation

    Suppose $q=2\gamma_0+\gamma_1$. Project it onto the time axis using

    $$
    q_\parallel=\frac{q\cdot\gamma_0}{\gamma_0^2}\gamma_0.
    $$

    Its event is $X(q_\parallel)$. Removing the spatial component from
    $X(q)$ while retaining its old quadratic infinity coefficient instead
    gives a non-null vector. Projection and conformal lifting need not commute.
    Null lines also require extra structure to define an orthogonal projection.
    """)
    return


@app.cell
def _(gm, infinity, origin, scalar_product, squared, time_axis, zoo):
    projection_input = zoo.spacetime_vector((2, 1, 0, 0))
    projected_position = scalar_product(projection_input, time_axis) * time_axis / scalar_product(time_axis, time_axis)
    projected_lift = zoo.event(projected_position)
    coefficient_projection = origin + projected_position + squared(projection_input) * infinity / 2
    lifted_square = float(squared(projected_lift))
    coefficient_square = float(squared(coefficient_projection))
    gm.md(t"""
    Correct lifted event: {projected_lift:value}, square `{lifted_square:g}`.

    Coefficient projection: {coefficient_projection:value}, square `{coefficient_square:g}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Reading the results

    - `classify()` returns an immutable `CSTAClassification`: kind, grade,
      representation, simplicity, finiteness, causal interpretation and properties.
    - `classify_operator()` returns an immutable `CSTAOperatorClassification`:
      overlapping traits, transformation, bounded nilpotency index and properties.
    - `finite=True` describes the affine representation; it does not guarantee
      a real locus. Imaginary objects are explicitly named where recognized.
    - Full signed rounds use a radial causal invariant. Curves use tangent
      causality. Flats use their carrier signature. Surface tangent signatures
      appear as `tangent_inertia` because they can be mixed or degenerate.
    - A geometric zero, scalar, pseudoscalar, nonsimple blade or mixed-grade
      value gets a structural result rather than an invented geometric name.
    - Recognition is numerical: `atol` and operator `rtol` set tolerances.
      A general or unrecognized result is not a proof of nonexistence.

    For background, see the CSTA constructions in
    [§6 of Double Conformal Space-Time Algebra](https://vixra.org/pdf/1602.0114v5.pdf)
    and the [Clifford conformal transformation tutorial](https://clifford.readthedocs.io/en/latest/tutorials/cga/index.html).
    """)
    return


if __name__ == "__main__":
    app.run()
