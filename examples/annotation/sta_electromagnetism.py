"""Teach spacetime algebra and electromagnetism through semantic annotations."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import numpy as np
    import marimo as mo

    import galaga_annotation as ga
    import galaga_marimo as gm
    from galaga import (
        Algebra,
        Presenter,
        exp,
        grade,
        hestenes_inner,
        presets,
        sandwich,
        scalar_product,
    )

    return (
        Algebra,
        Presenter,
        exp,
        ga,
        gm,
        grade,
        hestenes_inner,
        mo,
        np,
        presets,
        sandwich,
        scalar_product,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Spacetime algebra and electromagnetism—one geometric language

    Spacetime algebra (STA) is $\mathrm{Cl}(1,3)$: one timelike direction and
    three spacelike directions. Its six bivectors already contain the two
    transformations and the two field concepts we want to distinguish:

    - **timelike–spacelike planes** generate Lorentz boosts;
    - **spatial planes** generate ordinary rotations;
    - the same split packages the electric and magnetic fields into one
      Faraday bivector $F=\mathbf E+I\mathbf B$.

    This lesson uses color as semantic vocabulary. Blue means **boost**, orange
    means **spatial rotation**, red means **electric**, and steel blue means
    **magnetic**. The annotations attach to algebraic terms, not positions in a
    rendered string, so the callouts remain correct when notation changes.
    """)
    return


@app.cell
def _(Algebra, Presenter, presets):
    BOOST_BLUE = "#0072B2"
    BOOST_FILL = "#DCEEFF"
    ROTATION_ORANGE = "#D55E00"
    ROTATION_FILL = "#FDE7D9"
    ELECTRIC_RED = "#C43C39"
    ELECTRIC_FILL = "#FBE3E1"
    MAGNETIC_BLUE = "#2F6FB0"
    MAGNETIC_FILL = "#DDEAF7"

    sta = Algebra(config=presets.sta("mostly-minus"), expr=True)
    g0, g1, g2, g3 = sta.basis_vectors(expr=True)
    I_sta = sta.I.named("I", latex="I")
    sigma1, sigma2, sigma3 = g1 * g0, g2 * g0, g3 * g0
    spatial12, spatial23, spatial31 = I_sta * sigma3, I_sta * sigma1, I_sta * sigma2
    boost_planes = (sigma1, sigma2, sigma3)
    rotation_planes = (spatial23, spatial31, spatial12)
    sta_presenter = Presenter(blades=presets.blades.sta(sigmas=True), content="value")
    return (
        BOOST_BLUE,
        BOOST_FILL,
        ELECTRIC_FILL,
        ELECTRIC_RED,
        I_sta,
        MAGNETIC_BLUE,
        MAGNETIC_FILL,
        ROTATION_FILL,
        ROTATION_ORANGE,
        boost_planes,
        g0,
        g1,
        g2,
        rotation_planes,
        sigma1,
        sigma2,
        spatial12,
        sta_presenter,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The bivector split predicts the geometry

    In the mostly-minus signature,
    $\gamma_0^2=+1$ and $\gamma_k^2=-1$. Define the observer-relative
    bivectors $\sigma_k=\gamma_k\gamma_0$.

    A simple bivector's square tells us what its exponential does:

    - $K^2=+1$ gives hyperbolic functions—**a boost**;
    - $J^2=-1$ gives circular functions—**a rotation**.

    The next equation is not colored blade-by-blade. Two stable color groups
    let the reader recognize the conceptual split before reading every term.
    """)
    return


@app.cell
def _(
    BOOST_BLUE,
    BOOST_FILL,
    ROTATION_FILL,
    ROTATION_ORANGE,
    boost_planes,
    ga,
    gm,
    rotation_planes,
    sta_presenter,
):
    _zero = boost_planes[0].algebra.scalar(0.0)
    generator_catalog = sum(boost_planes + rotation_planes, start=_zero)
    generator_annotator = ga.annotator(
        ga.on(
            ga.terms(*boost_planes),
            label="boost planes\nsquare +1",
            background=BOOST_FILL,
            label_color=BOOST_BLUE,
            marker="rule",
            color=BOOST_BLUE,
            join=True,
        ),
        ga.on(
            ga.terms(*rotation_planes),
            label="rotation planes\nsquare -1",
            background=ROTATION_FILL,
            label_color=ROTATION_ORANGE,
            marker="rule",
            color=ROTATION_ORANGE,
            join=True,
        ),
    )
    generator_view = sta_presenter(generator_annotator(generator_catalog))
    generator_square_values = tuple(float(plane * plane) for plane in boost_planes + rotation_planes)
    generators_verified = generator_square_values == (1.0, 1.0, 1.0, -1.0, -1.0, -1.0)
    gm.md(rt"""
    {generator_view:block}

    Computed squares, in displayed family order:
    `{generator_square_values}`. Verified split: **{generators_verified}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. One exponential, two kinds of motion

    Both transformations use a rotor $R=e^{B/2}$ and the same sandwich
    $a'=Ra\widetilde R$. What changes is the geometry of the generator $B$.
    Move the controls and compare how a boost mixes time with one spatial axis,
    while a rotation remains entirely spatial.
    """)
    return


@app.cell
def _(mo):
    rapidity_control = mo.ui.slider(0.0, 1.5, step=0.05, value=0.6, label="boost rapidity φ")
    angle_control = mo.ui.slider(0.0, 180.0, step=1.0, value=40.0, label="rotation angle θ (degrees)")
    return angle_control, rapidity_control


@app.cell
def _(
    BOOST_BLUE,
    BOOST_FILL,
    ROTATION_FILL,
    ROTATION_ORANGE,
    angle_control,
    exp,
    g0,
    g1,
    g2,
    ga,
    gm,
    mo,
    np,
    rapidity_control,
    sandwich,
    sigma1,
    spatial12,
    sta_presenter,
):
    boost_generator = sigma1
    rotation_generator = spatial12
    rapidity_value = rapidity_control.value
    angle_value = np.radians(angle_control.value)
    boost_rotor = exp(rapidity_value * boost_generator / 2)
    rotation_rotor = exp(-angle_value * rotation_generator / 2)
    boosted_time = sandwich(boost_rotor, g0)
    rotated_axis = sandwich(rotation_rotor, g1)
    _unit_scalar = g0.algebra.scalar(1.0)
    rotors_verified = (boost_rotor * ~boost_rotor).almost_equal(_unit_scalar) and (
        rotation_rotor * ~rotation_rotor
    ).almost_equal(_unit_scalar)

    selected_generator_annotator = ga.annotator(
        ga.on(
            ga.term(boost_generator),
            label="boost generator",
            background=BOOST_FILL,
            label_color=BOOST_BLUE,
            marker="rule",
            color=BOOST_BLUE,
        ),
        ga.on(
            ga.term(rotation_generator),
            label="rotation generator",
            background=ROTATION_FILL,
            label_color=ROTATION_ORANGE,
            marker="rule",
            color=ROTATION_ORANGE,
        ),
    )
    selected_generators_view = sta_presenter(selected_generator_annotator(boost_generator + rotation_generator))
    boosted_time_view = sta_presenter(
        ga.annotator(
            ga.on(
                ga.terms(g0, g1),
                label="time–space mixing",
                background=BOOST_FILL,
                label_color=BOOST_BLUE,
                #marker="rule",
                side="below",
                clearance="3px",
                color=BOOST_BLUE,
                join=True,
            )
        )(boosted_time)
    )
    rotated_axis_view = sta_presenter(
        ga.annotator(
            ga.on(
                ga.terms(g1, g2),
                label="spatial rotation",
                background=ROTATION_FILL,
                label_color=ROTATION_ORANGE,
                #marker="rule",
                side="below",
                clearance="3px",
                color=ROTATION_ORANGE,
                join=True,
            )
        )(rotated_axis)
    )

    mo.vstack(
        [
            mo.hstack([rapidity_control, angle_control], justify="space-around"),
            gm.md(rt"""
    **The generators:** {selected_generators_view:block}

    **Boosted time axis:** {boosted_time_view:block}

    **Rotated spatial axis:** {rotated_axis_view:block}

    Both rotors satisfy $R\widetilde R=1$: **{rotors_verified}**.
        """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Electromagnetism is another bivector split

    Relative to the observer $\gamma_0$, the electric field occupies the boost
    planes $\sigma_k$. The magnetic field occupies the rotation planes
    $I\sigma_k$. They are not unrelated three-vectors bolted together; they are
    complementary parts of one spacetime bivector:

    $$F=\mathbf E+I\mathbf B.$$

    Keep the red/blue distinction in mind—the same colors will follow each
    field contribution into the Lorentz force.
    """)
    return


@app.cell
def _(mo):
    electric_x_control = mo.ui.slider(-2.0, 2.0, step=0.05, value=1.2, label="Eₓ")
    electric_y_control = mo.ui.slider(-2.0, 2.0, step=0.05, value=0.35, label="Eᵧ")
    electric_z_control = mo.ui.slider(-2.0, 2.0, step=0.05, value=-0.2, label="E_z")
    magnetic_x_control = mo.ui.slider(-2.0, 2.0, step=0.05, value=0.15, label="Bₓ")
    magnetic_y_control = mo.ui.slider(-2.0, 2.0, step=0.05, value=-0.4, label="Bᵧ")
    magnetic_z_control = mo.ui.slider(-2.0, 2.0, step=0.05, value=0.8, label="B_z")
    return (
        electric_x_control,
        electric_y_control,
        electric_z_control,
        magnetic_x_control,
        magnetic_y_control,
        magnetic_z_control,
    )


@app.cell
def _(
    ELECTRIC_FILL,
    ELECTRIC_RED,
    MAGNETIC_BLUE,
    MAGNETIC_FILL,
    boost_planes,
    electric_x_control,
    electric_y_control,
    electric_z_control,
    ga,
    gm,
    magnetic_x_control,
    magnetic_y_control,
    magnetic_z_control,
    mo,
    np,
    rotation_planes,
    sta_presenter,
):
    electric_coefficients = np.array([electric_x_control.value, electric_y_control.value, electric_z_control.value])
    magnetic_coefficients = np.array([magnetic_x_control.value, magnetic_y_control.value, magnetic_z_control.value])
    electric_field = sum(
        (coefficient * plane for coefficient, plane in zip(electric_coefficients, boost_planes)),
        start=boost_planes[0].algebra.scalar(0.0),
    )
    magnetic_field = sum(
        (coefficient * plane for coefficient, plane in zip(magnetic_coefficients, rotation_planes)),
        start=rotation_planes[0].algebra.scalar(0.0),
    )
    faraday_field = electric_field + magnetic_field
    field_annotator = ga.annotator(
        ga.on(
            ga.terms(*boost_planes),
            label="electric part E",
            background=ELECTRIC_FILL,
            label_color=ELECTRIC_RED,
            #marker="overbrace",
            side="below",
            clearance="3px",
            color=ELECTRIC_RED,
            join=True,
        ),
        ga.on(
            ga.terms(*rotation_planes),
            label="magnetic part I B",
            background=MAGNETIC_FILL,
            label_color=MAGNETIC_BLUE,
            #marker="overbrace",
            side="below",
            clearance="3px",
            color=MAGNETIC_BLUE,
            join=True,
        ),
    )
    faraday_view = sta_presenter(field_annotator(faraday_field))
    mo.vstack(
        [
            mo.hstack([electric_x_control, electric_y_control, electric_z_control]),
            mo.hstack([magnetic_x_control, magnetic_y_control, magnetic_z_control]),
            gm.md(rt"""
    **One field, two observer-relative parts:**

    {faraday_view:block}

    Red terms lie in boost planes; blue terms lie in spatial-rotation planes.
    A different observer changes this split, but not the spacetime bivector.
    """),
        ]
    )
    return (
        electric_coefficients,
        faraday_field,
        field_annotator,
        magnetic_coefficients,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The square of $F$ remembers both invariants

    Because $F$ is one bivector, one geometric square contains two independent
    Lorentz invariants. In this convention,

    $$F^2=(\lVert\mathbf E\rVert^2-\lVert\mathbf B\rVert^2)
      +2I(\mathbf E\cdot\mathbf B).$$

    The scalar and pseudoscalar annotations identify the two grades directly;
    no coordinate parser is involved.
    """)
    return


@app.cell
def _(
    ELECTRIC_FILL,
    ELECTRIC_RED,
    I_sta,
    MAGNETIC_BLUE,
    MAGNETIC_FILL,
    electric_coefficients,
    faraday_field,
    ga,
    gm,
    grade,
    magnetic_coefficients,
    np,
    sta_presenter,
):
    field_square = faraday_field * faraday_field
    scalar_invariant = grade(field_square, 0)
    pseudoscalar_invariant = grade(field_square, 4)
    expected_scalar_invariant = float(
        np.dot(electric_coefficients, electric_coefficients) - np.dot(magnetic_coefficients, magnetic_coefficients)
    )
    expected_pseudoscalar_invariant = 2.0 * float(np.dot(electric_coefficients, magnetic_coefficients)) * I_sta
    field_invariants_verified = scalar_invariant.almost_equal(
        scalar_invariant.algebra.scalar(expected_scalar_invariant)
    ) and pseudoscalar_invariant.almost_equal(expected_pseudoscalar_invariant)
    invariant_annotator = ga.annotator(
        ga.on(
            ga.grade(0),
            label_latex=r"\lVert E\rVert^2-\lVert B\rVert^2",
            background=ELECTRIC_FILL,
            label_color=ELECTRIC_RED,
            marker="overbrace",
            color=ELECTRIC_RED,
        ),
        ga.on(
            ga.grade(4),
            label_latex=r"2I(E\cdot B)",
            background=MAGNETIC_FILL,
            label_color=MAGNETIC_BLUE,
            marker="underbrace",
            color=MAGNETIC_BLUE,
        ),
    )
    invariant_view = sta_presenter(invariant_annotator(field_square))
    gm.md(rt"""
    {invariant_view:block}

    Direct coefficient check: **{field_invariants_verified}**.
    """)
    return (field_square,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Electric versus magnetic force

    For four-velocity $u$, the force per unit charge is the vector
    $K=F\cdot u$. Linearity exposes the teaching split

    $$K=(F_E\cdot u)+(F_B\cdot u)=K_E+K_B.$$

    Choose motion along $\gamma_1$, an electric field along $\sigma_1$, and a
    magnetic field in the $I\sigma_3$ plane. The red force has a time component
    (power transfer); the blue force is transverse and has no time component.
    """)
    return


@app.cell
def _(mo):
    speed_control = mo.ui.slider(0.0, 0.95, step=0.01, value=0.6, label="particle speed v/c along γ₁")
    return (speed_control,)


@app.cell
def _(
    ELECTRIC_FILL,
    ELECTRIC_RED,
    MAGNETIC_BLUE,
    MAGNETIC_FILL,
    electric_x_control,
    g0,
    g1,
    g2,
    ga,
    gm,
    hestenes_inner,
    magnetic_z_control,
    mo,
    np,
    scalar_product,
    sigma1,
    spatial12,
    speed_control,
    sta_presenter,
):
    speed_value = speed_control.value
    lorentz_gamma = 1.0 / np.sqrt(1.0 - speed_value**2)
    four_velocity = lorentz_gamma * (g0 + speed_value * g1)
    force_electric_field = electric_x_control.value * sigma1
    force_magnetic_field = magnetic_z_control.value * spatial12
    force_field = force_electric_field + force_magnetic_field
    electric_force = hestenes_inner(force_electric_field, four_velocity)
    magnetic_force = hestenes_inner(force_magnetic_field, four_velocity)
    lorentz_force = hestenes_inner(force_field, four_velocity)
    force_linearity_verified = lorentz_force.almost_equal(electric_force + magnetic_force)
    force_orthogonality = float(scalar_product(four_velocity, lorentz_force))
    magnetic_power = float(scalar_product(g0, magnetic_force))
    force_geometry_verified = bool(np.isclose(force_orthogonality, 0.0) and np.isclose(magnetic_power, 0.0))
    force_annotator = ga.annotator(
        ga.on(
            ga.terms(g0, g1),
            label="electric force:\nwork + acceleration",
            background=ELECTRIC_FILL,
            label_color=ELECTRIC_RED,
            marker="rule",
            color=ELECTRIC_RED,
            join=True,
        ),
        ga.on(
            ga.term(g2, include_sign=False),
            label="magnetic force:\ntransverse",
            background=MAGNETIC_FILL,
            label_color=MAGNETIC_BLUE,
            marker="rule",
            color=MAGNETIC_BLUE,
        ),
    )
    force_view = sta_presenter(force_annotator(lorentz_force))
    electric_force_view = sta_presenter(
        ga.annotate(electric_force, label_latex="K_E", background=ELECTRIC_FILL, label_color=ELECTRIC_RED)
    )
    magnetic_force_view = sta_presenter(
        ga.annotate(magnetic_force, label_latex="K_B", background=MAGNETIC_FILL, label_color=MAGNETIC_BLUE)
    )
    mo.vstack(
        [
            speed_control,
            gm.md(rt"""
    **Electric contribution:** {electric_force_view:block}

    **Magnetic contribution:** {magnetic_force_view:block}

    **Combined four-force:** {force_view:block}

    Linearity verified: **{force_linearity_verified}**.
    Orthogonality $u\cdot K=0$ and zero magnetic power verified:
    **{force_geometry_verified}**.
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. A boost changes the split, not the field

    Electric and magnetic fields are observer-relative parts of $F$. Boosting
    the field generally redistributes coefficients between the red and blue
    families. The scalar and pseudoscalar parts of $F^2$ remain unchanged.
    """)
    return


@app.cell
def _(mo):
    field_boost_control = mo.ui.slider(-1.2, 1.2, step=0.05, value=0.45, label="field boost rapidity along γ₂")
    return (field_boost_control,)


@app.cell
def _(
    exp,
    faraday_field,
    field_annotator,
    field_boost_control,
    field_square,
    gm,
    grade,
    mo,
    sandwich,
    sigma2,
    sta_presenter,
):
    field_rapidity = field_boost_control.value
    field_boost_rotor = exp(field_rapidity * sigma2 / 2)
    boosted_field = sandwich(field_boost_rotor, faraday_field)
    boosted_field_view = sta_presenter(field_annotator(boosted_field))
    boosted_field_square = boosted_field * boosted_field
    boosted_invariants_verified = grade(boosted_field_square, 0).almost_equal(grade(field_square, 0)) and grade(
        boosted_field_square, 4
    ).almost_equal(grade(field_square, 4))
    mo.vstack(
        [
            field_boost_control,
            gm.md(rt"""
    **Original observer split:** {sta_presenter(field_annotator(faraday_field)):block}

    **Boosted observer split:** {boosted_field_view:block}

    Same scalar and pseudoscalar invariants: **{boosted_invariants_verified}**.
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    1. **Bivector square controls transformation type.** Boost planes square
       to $+1$; spatial-rotation planes square to $-1$.
    2. **Electric and magnetic fields are one bivector.** Their separation is
       observer-relative, which is why boosts mix them.
    3. **The geometric product preserves structure.** Scalar and
       pseudoscalar pieces of $F^2$ expose both field invariants.
    4. **The Lorentz force split is linear but geometric.** The electric part
       transfers energy; the magnetic part bends the spatial velocity.

    The colors are deliberately reused rather than reassigned in every cell:
    recognition should become faster as the lesson progresses.
    """)
    return


if __name__ == "__main__":
    app.run()
