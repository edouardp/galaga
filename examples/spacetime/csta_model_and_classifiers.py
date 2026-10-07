"""An API tour of Galaga's conformal spacetime model and classifiers."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    from math import sqrt

    import marimo as mo

    import galaga_marimo as gm
    from galaga import Algebra, exp, outer_product, presets, right_hodge_dual, sandwich, scalar_product
    from galaga.models import ConformalSpacetimeModel, SpacetimeUnits

    return (
        Algebra,
        ConformalSpacetimeModel,
        SpacetimeUnits,
        exp,
        gm,
        mo,
        outer_product,
        presets,
        right_hodge_dual,
        sandwich,
        scalar_product,
        sqrt,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Conformal spacetime: an API tour

    `ConformalSpacetimeModel` adds geometric meaning to a six-dimensional
    algebra. Its physical base is four-dimensional spacetime with signature
    $(+---)$, followed by the conformal null pair $n_o,n_\infty$.

    This notebook concentrates on the API:

    - construct and recover spacetime events;
    - calculate signed intervals;
    - construct event pairs, causal flat lines, and signed rounds; and
    - classify those objects from their algebraic structure.

    The algebra uses natural units with $c=1$. The model can accept seconds
    and metres, or other time/distance units, and convert results to useful
    physical scales. By default one natural time unit is one second and one
    natural length unit is one light-second.
    """)
    return


@app.cell
def _(Algebra, ConformalSpacetimeModel, presets):
    csta_algebra = Algebra(config=presets.csta(), expr=True)
    csta_model = ConformalSpacetimeModel(csta_algebra, expr=True)
    return csta_algebra, csta_model


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The configured algebra

    The ordered vector basis is

    $$
    \{\gamma_0,\gamma_1,\gamma_2,\gamma_3,n_o,n_\infty\}.
    $$

    The first four vectors have the STA metric $(+---)$. The final two are
    null and satisfy $n_o\cdot n_\infty=-1$.
    """)
    return


@app.cell
def _(csta_algebra):
    csta_algebra
    return


@app.cell
def _(csta_algebra):
    csta_algebra.basis_vectors()
    return


@app.cell
def _(csta_algebra):
    csta_algebra.bilinear_form_table()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Events and the conformal lift

    For a spacetime vector

    $$
    x=t\gamma_0+x^1\gamma_1+x^2\gamma_2+x^3\gamma_3,
    $$

    the model constructs

    $$
    X(x)=n_o+x+\frac{1}{2}x^2n_\infty.
    $$

    Every embedded event is null: $X(x)^2=0$. `event()` and `point()` are the
    semantic constructors; `up()` exposes the conventional conformal name.
    """)
    return


@app.cell
def _(csta_model):
    alice_departure = csta_model.event(0, 0, 0, 0).named("A_0", latex=r"A_0")
    alice_later = csta_model.event(2, 1, 0, 0).named("A_1", latex=r"A_1")
    alice_coordinates = csta_model.coordinates(alice_later)
    alice_is_null = (alice_later * alice_later).almost_equal(csta_model.algebra.scalar(0))
    return alice_coordinates, alice_departure, alice_is_null, alice_later


@app.cell
def _(alice_coordinates, alice_departure, alice_is_null, alice_later, gm):
    gm.md(t"""
    {alice_departure}

    {alice_later}

    Recovered coordinates: `{alice_coordinates!s}`

    Computed check $A_1^2=0$: `{alice_is_null!s}`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Seconds, metres, and other units

    `units="si"` sets the coordinate order to **seconds, metres, metres,
    metres**. A tuple such as `units=("min", "km")` selects mixed units.
    `event(..., units=...)` overrides the model default for one construction;
    `coordinates(..., units=...)` selects the output units independently.

    The metric still has $c=1$. For a physical time scale $T_0$, conversion is

    $$
    t_{\mathrm{SI}}=T_0t,\qquad
    \mathbf{x}_{\mathrm{SI}}=cT_0\mathbf{x},\qquad
    v_{\mathrm{SI}}=c\beta.
    $$

    The default is $T_0=1$ second. `time_scale_seconds=...` changes it, or pass
    a reusable `SpacetimeUnits` as `unit_scale`. Choose a scale that keeps
    coordinates near unity: for metre-sized geometry, $T_0=1/c$ seconds
    makes one natural length unit one metre. Numeric tolerances still apply
    to **natural** values, so scale matters for small intervals.

    Multivectors already belong to the normalized algebra and are never
    converted again. `down()` and `separation_squared()` also retain natural
    units; `coordinates()` supplies the physical boundary conversion.
    """)
    return


@app.cell
def _(ConformalSpacetimeModel, csta_algebra):
    si_csta_model = ConformalSpacetimeModel(csta_algebra, units="si", expr=True)
    si_light_speed = si_csta_model.speed_in(1)
    si_light_event = si_csta_model.event(1, si_light_speed, 0, 0)
    si_light_coordinates = si_csta_model.coordinates(si_light_event)
    mixed_unit_event = si_csta_model.event(1, 2, 0, 0, units=("min", "km"))
    mixed_unit_coordinates = si_csta_model.coordinates(mixed_unit_event, units=("min", "km"))
    unit_format_examples = "\n".join(
        f"| {description} | {formatted} |"
        for description, formatted in (
            ("A microsecond", si_csta_model.format_time(si_csta_model.unit_scale.time_from(1, "us"))),
            ("A millisecond", si_csta_model.format_time(si_csta_model.unit_scale.time_from(1, "ms"))),
            ("90 seconds", si_csta_model.format_time(90)),
            ("A nanometre", si_csta_model.format_distance(si_csta_model.unit_scale.distance_from(1, "nm"))),
            ("Two kilometres", si_csta_model.format_distance(si_csta_model.unit_scale.distance_from(2, "km"))),
            ("97 percent of light speed", si_csta_model.format_speed(0.97)),
            ("Same speed in metres/second", si_csta_model.format_speed(0.97, "m/s", precision=6)),
        )
    )
    return (
        mixed_unit_coordinates,
        mixed_unit_event,
        si_light_coordinates,
        si_light_event,
        unit_format_examples,
    )


@app.cell
def _(
    gm,
    mixed_unit_coordinates,
    mixed_unit_event,
    si_light_coordinates,
    si_light_event,
    unit_format_examples,
):
    gm.md(t"""
    A light signal after one second: {si_light_event:expr}

    Recovered SI coordinates: `{si_light_coordinates!s}`

    Mixed-unit input: {mixed_unit_event:expr}

    Recovered minutes/km coordinates: `{mixed_unit_coordinates!s}`

    `time_in`, `distance_in`, `speed_in`, and `acceleration_in` return
    **numbers** in the requested unit. `format_*` returns **strings**, choosing
    a unit by magnitude unless you specify one. `precision` is the number of
    significant digits.

    | Quantity | Automatic or selected display |
    |:--|:--|
    {unit_format_examples}

    The reusable backend also has `time_from`, `distance_from`, `speed_from`,
    and `acceleration_from` to turn physical numbers into natural values.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Operator or expanded expressions

    The default operator form retains the API call, such as
    $\operatorname{event}(2,1,0,0)$. To expose the embedding equation, create a
    model view with `with_expression_form("expanded")`. Both views share the
    same algebra. `expression_form` reports a view's default, and the
    keyword of the same name overrides it for one call.

    `expr=True` controls whether provenance is retained; the expression form
    selects how that provenance is described. It does not change the value
    or its classification.
    """)
    return


@app.cell
def _(csta_model):
    expanded_csta_model = csta_model.with_expression_form("expanded")
    expanded_event = expanded_csta_model.event(2, 1, 0, 0).named("A_exp", latex=r"A_{\mathrm{expanded}}")
    compact_override = expanded_csta_model.event(2, 1, 0, 0, expression_form="operator").named(
        "A_op", latex=r"A_{\mathrm{operator}}"
    )
    return compact_override, expanded_csta_model, expanded_event


@app.cell
def _(compact_override, csta_model, expanded_csta_model, expanded_event, gm):
    gm.md(t"""
    Expanded model default: `{expanded_csta_model.expression_form}`

    {expanded_event}

    Operator override on the same model view:

    {compact_override}

    The original model default is still `{csta_model.expression_form}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Signed intervals and causal classes

    Normalized conformal events encode the ordinary Minkowski interval:

    $$
    (a-b)^2=-2X(a)\cdot X(b).
    $$

    With signature $(+---)$, a positive value is timelike, zero is null, and
    a negative value is spacelike.

    An interval is a scalar measurement, so classify its sign with
    `causal_kind(separation_squared(A, B))`. Use `classify(blade)` for the
    geometric object constructed from those events.
    """)
    return


@app.cell
def _(csta_model):
    interval_origin = csta_model.event(0, 0, 0, 0)
    interval_events = (
        ("one second at rest", csta_model.event(1, 0, 0, 0)),
        ("one light-second", csta_model.event(1, 1, 0, 0)),
        ("simultaneous separation", csta_model.event(0, 1, 0, 0)),
    )
    interval_rows = tuple(
        (
            label,
            csta_model.separation_squared(interval_origin, event),
            csta_model.causal_kind(csta_model.separation_squared(interval_origin, event)),
        )
        for label, event in interval_events
    )
    return interval_events, interval_origin, interval_rows


@app.cell
def _(gm, interval_rows):
    _table_rows = "\n".join(
        f"| {label} | {squared_interval:g} | {causal} |" for label, squared_interval, causal in interval_rows
    )
    gm.md(t"""
    | Separation | Interval² | Causal class |
    |:--|--:|:--|
    {_table_rows}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Classification is model-aware

    `classify()` checks algebra ownership, grade, blade simplicity, incidence
    with $n_\infty$, and metric invariants. It returns structured data that a
    notebook, visualizer, or annotation layer can consume.

    A conformal null vector has two valid readings: directly as an event, or
    dually as the light cone centred on that event. State the representation
    when that distinction matters.
    """)
    return


@app.cell
def _(alice_departure, csta_model):
    event_auto = csta_model.classify(alice_departure)
    event_direct = csta_model.classify(alice_departure, representation="direct")
    event_dual = csta_model.classify(alice_departure, representation="dual")
    return event_auto, event_direct, event_dual


@app.cell
def _(event_auto, event_direct, event_dual, gm):
    gm.md(t"""
    | Request | Classified kind | Representation |
    |:--|:--|:--|
    | automatic | `{event_auto.kind}` | `{event_auto.representation}` |
    | direct | `{event_direct.kind}` | `{event_direct.representation}` |
    | dual | `{event_dual.kind}` | `{event_dual.representation}` |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Event pairs and causal flat lines

    Two events define the OPNS event pair

    $$
    P=X(a)\wedge X(b).
    $$

    Adding infinity produces the complete flat line through them:

    $$
    L=X(a)\wedge X(b)\wedge n_\infty.
    $$

    For a flat line, the classifier extracts its carrier direction from the
    blade and classifies that direction as timelike, null, or spacelike.
    """)
    return


@app.cell
def _(csta_model, interval_events, interval_origin):
    selected_event = interval_events[1][1]
    light_event_pair = (interval_origin ^ selected_event).named("P")
    light_worldline = (light_event_pair ^ csta_model.infinity).named("L")
    pair_classification = csta_model.classify(light_event_pair)
    line_classification = csta_model.classify(light_worldline)
    return (
        light_event_pair,
        light_worldline,
        line_classification,
        pair_classification,
    )


@app.cell
def _(
    gm,
    light_event_pair,
    light_worldline,
    line_classification,
    pair_classification,
):
    gm.md(t"""
    {light_event_pair}

    Event-pair classifier: `{pair_classification.kind}`

    {light_worldline}

    Flat-line classifier: `{line_classification.kind}` with causal carrier
    `{line_classification.causal}`.

    The explicit wedges above are equivalent to `event_pair(A, B)` and
    `flat_line(A, B)`; both constructions use the same classifier.
    """)
    return


@app.cell
def _(csta_model, interval_events, interval_origin):
    causal_line_rows = tuple(
        (
            label,
            csta_model.separation_squared(interval_origin, event),
            csta_model.causal_kind(csta_model.separation_squared(interval_origin, event)),
            csta_model.classify(interval_origin ^ event).causal,
            csta_model.classify(csta_model.flat_line(interval_origin, event)).causal,
        )
        for label, event in interval_events
    )
    return (causal_line_rows,)


@app.cell
def _(causal_line_rows, gm):
    _line_rows = "\n".join(
        f"| {label} | {interval:g} | {interval_class} | {pair_class} | {line_class} |"
        for label, interval, interval_class, pair_class, line_class in causal_line_rows
    )
    gm.md(t"""
    | Events | Interval² | Interval class | Event pair | Flat line |
    |:--|--:|:--|:--|:--|
    {_line_rows}

    The pair's square alone cannot distinguish timelike from spacelike
    separation. The object classifier uses infinity to recover the line's
    carrier direction, then measures it with the spacetime metric.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Signed rounds

    An IPNS signed round centred at $c$ is

    $$
    S(c,\rho^2)=X(c)-\frac{1}{2}\rho^2n_\infty,
    $$

    and its square is $S^2=\rho^2$. The sign distinguishes a proper-time
    hyperboloid, a light cone, and a proper-distance hyperboloid.
    """)
    return


@app.cell
def _(csta_model):
    signed_rounds = tuple(
        (
            radius_squared,
            csta_model.signed_round((0, 0, 0, 0), radius_squared),
        )
        for radius_squared in (1.0, 0.0, -1.0)
    )
    round_rows = tuple(
        (
            radius_squared,
            float(value * value),
            csta_model.classify(value, representation="dual"),
        )
        for radius_squared, value in signed_rounds
    )
    return (round_rows,)


@app.cell
def _(gm, round_rows):
    _round_rows = "\n".join(
        f"| {requested:g} | {computed:g} | {classification.kind} | {classification.causal} |"
        for requested, computed, classification in round_rows
    )
    gm.md(rt"""
    | Requested $\rho^2$ | Computed $S^2$ | Object | Causal class |
    |--:|--:|:--|:--|
    {_round_rows}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Construct a light cone by wedging events

    Suppose a flash is emitted at $c=(10,3,-2,1)$. Choose five events reached
    by light from that emission, so $(q_i-c)^2=0$. Four samples are one second
    later; the fifth is two seconds later. The different times let the
    samples span five independent conformal directions.

    In four-dimensional spacetime, five independent embedded events define
    a round hypersurface:

    $$
    C=X(q_1)\wedge X(q_2)\wedge X(q_3)\wedge X(q_4)\wedge X(q_5).
    $$

    Its dual vector $S=\operatorname{right\_hodge\_dual}(C)$ describes the
    same surface through $X(q)\cdot S=0$. Here $S^2=0$, and the surface is a
    light cone. The same `classify()` method handles both forms: use
    `representation="direct"` for $C$, and `"dual"` for $S$.

    The cone includes both future and past branches. Selecting only events
    after the flash requires an additional time condition.
    """)
    return


@app.cell
def _(csta_model, right_hodge_dual, scalar_product):
    cone_apex = csta_model.event(10, 3, -2, 1).named("F")
    cone_sample_1 = csta_model.event(11, 4, -2, 1).named("P1", latex=r"P_1")
    cone_sample_2 = csta_model.event(11, 2, -2, 1).named("P2", latex=r"P_2")
    cone_sample_3 = csta_model.event(11, 3, -1, 1).named("P3", latex=r"P_3")
    cone_sample_4 = csta_model.event(11, 3, -2, 2).named("P4", latex=r"P_4")
    cone_sample_5 = csta_model.event(12, 5, -2, 1).named("P5", latex=r"P_5")

    cone_from_events = (cone_sample_1 ^ cone_sample_2 ^ cone_sample_3 ^ cone_sample_4 ^ cone_sample_5).named("C")
    cone_dual = right_hodge_dual(cone_from_events).named("S")
    cone_direct_class = csta_model.classify(cone_from_events, representation="direct")
    cone_dual_class = csta_model.classify(cone_dual, representation="dual")
    cone_recovered_apex = csta_model.coordinates(cone_dual)
    cone_samples = (cone_sample_1, cone_sample_2, cone_sample_3, cone_sample_4, cone_sample_5)
    cone_sample_checks = tuple(
        (
            csta_model.separation_squared(cone_apex, sample),
            (sample ^ cone_from_events).almost_equal(csta_model.algebra.scalar(0)),
            float(scalar_product(sample, cone_dual)),
        )
        for sample in cone_samples
    )
    return (
        cone_direct_class,
        cone_dual,
        cone_dual_class,
        cone_from_events,
        cone_recovered_apex,
        cone_sample_checks,
    )


@app.cell
def _(
    cone_direct_class,
    cone_dual,
    cone_dual_class,
    cone_from_events,
    cone_recovered_apex,
    cone_sample_checks,
    gm,
):
    cone_check_rows = "\n".join(
        f"| P{index} | {interval:g} | {incident} | {pairing:g} |"
        for index, (interval, incident, pairing) in enumerate(cone_sample_checks, start=1)
    )
    gm.md(t"""
    Direct construction:

    {cone_from_events:expr}

    Dual construction:

    {cone_dual:expr}

    | Form | Grade | Classification | Causal invariant |
    |:--|--:|:--|:--|
    | direct wedge | {cone_direct_class.grade} | `{cone_direct_class.kind}` | `{cone_direct_class.causal}` |
    | dual vector | {cone_dual_class.grade} | `{cone_dual_class.kind}` | `{cone_dual_class.causal}` |

    Recovered apex: `{cone_recovered_apex!s}`

    | Sample | Interval² from flash | Wedge incidence is zero | Dual pairing |
    |:--|--:|:--|--:|
    {cone_check_rows}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. More objects from events

    The same construction patterns provide other rounds and flats:

    - two events: an event pair;
    - three or four events: lower-dimensional rounds;
    - events wedged with infinity: a flat point, line, 2-plane, or hyperplane;
    - five events with positive or negative squared interval from a common
      centre: a proper-time or proper-distance hyperboloid.

    The lower-dimensional round labels describe structure. In an indefinite
    metric, grade three alone does not imply an ordinary Euclidean circle.
    The classifier examines the carrier metric and restricted quadratic form
    to distinguish circles, hyperbolas, and null line pairs. A degenerate
    carrier retains the structural label `round 2-object`.
    """)
    return


@app.cell
def _(csta_model, outer_product, sqrt):
    gallery_a = csta_model.event(0, 0, 0, 0).named("A")
    gallery_b = csta_model.event(1, 0, 0, 0).named("B")
    gallery_c = csta_model.event(0, 1, 0, 0).named("C")
    gallery_d = csta_model.event(0, 0, 1, 0).named("D")
    gallery_circle_third = csta_model.event(0, -1, 0, 0).named("E")
    gallery_infinity = csta_model.infinity

    timelike_samples = tuple(
        csta_model.event(coordinates)
        for coordinates in (
            (1, 0, 0, 0),
            (sqrt(2), 1, 0, 0),
            (sqrt(2), -1, 0, 0),
            (sqrt(2), 0, 1, 0),
            (sqrt(2), 0, 0, 1),
        )
    )
    spacelike_samples = tuple(
        csta_model.event(coordinates)
        for coordinates in (
            (0, 1, 0, 0),
            (0, -1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
            (1, sqrt(2), 0, 0),
        )
    )
    objects_from_events = (
        ("A", gallery_a),
        ("A ∧ B", gallery_a ^ gallery_b),
        ("A ∧ B ∧ C", gallery_a ^ gallery_b ^ gallery_c),
        ("A ∧ B ∧ C ∧ D", gallery_a ^ gallery_b ^ gallery_c ^ gallery_d),
        ("three simultaneous spatial samples", gallery_c ^ gallery_d ^ gallery_circle_third),
        ("A ∧ infinity", gallery_a ^ gallery_infinity),
        ("A ∧ B ∧ infinity", gallery_a ^ gallery_b ^ gallery_infinity),
        ("A ∧ B ∧ C ∧ infinity", gallery_a ^ gallery_b ^ gallery_c ^ gallery_infinity),
        ("A ∧ B ∧ C ∧ D ∧ infinity", gallery_a ^ gallery_b ^ gallery_c ^ gallery_d ^ gallery_infinity),
        ("five proper-time samples", outer_product(*timelike_samples)),
        ("five proper-distance samples", outer_product(*spacelike_samples)),
        ("infinity", gallery_infinity),
    )
    object_gallery_rows = tuple(
        (construction, csta_model.classify(value, representation="direct"))
        for construction, value in objects_from_events
    )
    return (object_gallery_rows,)


@app.cell
def _(gm, object_gallery_rows):
    object_gallery_table = "\n".join(
        f"| {construction} | {classification.grade} | {classification.kind} | {classification.causal or '—'} |"
        for construction, classification in object_gallery_rows
    )
    gm.md(t"""
    | Construction | Grade | Object classifier | Causal class where available |
    |:--|--:|:--|:--|
    {object_gallery_table}

    A dash means the classifier has not assigned a causal class to that
    object. It does not mean the object is null. For curves, the causal class
    describes tangents; for signed-round hypersurfaces, it describes the
    squared interval from the centre.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Three events from constant acceleration

    With $c=1$ and unit proper acceleration along $x$, the trajectory is

    $$
    t(\tau)=\sinh\tau,\qquad x(\tau)=\cosh\tau-1.
    $$

    We construct it with a boost rotor. Put $K=\gamma_1\gamma_0$, so $K^2=1$,
    and let

    $$
    R(\tau)=\exp\left(\frac{\tau K}{2}\right),\qquad
    q(\tau)=-\gamma_1+R(\tau)\gamma_1\widetilde{R(\tau)}.
    $$

    The rotor moves the displacement from the fixed centre $-\gamma_1$.
    Its exponential generates the hyperbolic functions above. With unit
    proper acceleration, rapidity equals proper time in these natural units.

    For a real-world interpretation we choose **1g proper acceleration** with
    `SpacetimeUnits.for_acceleration(1, unit="g")`. This sets
    $T_0=c/g$ and $L_0=c^2/g$: the same dimensionless rotor then describes a
    spacecraft maintaining one standard gravity of proper acceleration.
    The geometry is unchanged; the scale converts its coordinates to time
    and distance.

    Hence $(x+1)^2-t^2=1$: it lies on a hyperbola centred at $(0,-1)$ in the
    $(t,x)$ plane. Embed three samples and wedge them:

    $$
    H=X(0)\wedge X(0.5)\wedge X(1).
    $$

    Here $X(\tau)$ means the embedded event on the trajectory at proper time
    $\tau$, rather than embedding that scalar alone. The classifier reports
    `hyperbola` with timelike tangents. It derives this from the blade;
    it is not given the acceleration or the sampling formula.

    The blade describes the full hyperbola. Alice's worldline is the chosen
    branch, traversed in increasing proper time. Branch choice, direction of
    travel, and the proper-time parametrization are additional information.
    """)
    return


@app.cell
def _(
    ConformalSpacetimeModel,
    SpacetimeUnits,
    csta_model,
    exp,
    sandwich,
    scalar_product,
):
    acceleration_unit_scale = SpacetimeUnits.for_acceleration(1, unit="g")
    accelerating_csta_model = ConformalSpacetimeModel(csta_model.algebra, expr=True, unit_scale=acceleration_unit_scale)
    acceleration_time_axis, acceleration_space_axis, _, _ = accelerating_csta_model.spacetime_basis_vectors()
    acceleration_generator = acceleration_space_axis * acceleration_time_axis
    acceleration_rotors = tuple(exp(tau * acceleration_generator / 2) for tau in (0, 0.5, 1))
    acceleration_positions = tuple(
        -acceleration_space_axis + sandwich(rotor, acceleration_space_axis) for rotor in acceleration_rotors
    )
    acceleration_samples = tuple(
        accelerating_csta_model.event(position).named(f"A{index}", latex=rf"A_{{{index}}}")
        for index, position in enumerate(acceleration_positions)
    )
    acceleration_curve = (acceleration_samples[0] ^ acceleration_samples[1] ^ acceleration_samples[2]).named("H")
    acceleration_class = accelerating_csta_model.classify(acceleration_curve)
    acceleration_properties = dict(acceleration_class.properties)
    acceleration_carrier = acceleration_properties["carrier_inertia"]
    acceleration_center = accelerating_csta_model.spacetime_vector(acceleration_properties["center"], expr=False)
    acceleration_radius_squared = acceleration_properties["signed_radius_squared"]
    acceleration_four_velocities = tuple(sandwich(rotor, acceleration_time_axis) for rotor in acceleration_rotors)
    acceleration_betas = tuple(
        (
            float(scalar_product(velocity, acceleration_space_axis))
            / float(scalar_product(acceleration_space_axis, acceleration_space_axis))
        )
        / (
            float(scalar_product(velocity, acceleration_time_axis))
            / float(scalar_product(acceleration_time_axis, acceleration_time_axis))
        )
        for velocity in acceleration_four_velocities
    )
    acceleration_physical_rows = "\n".join(
        f"| {accelerating_csta_model.format_time(tau)} "
        f"| {accelerating_csta_model.format_time(float(coordinates[0]))} "
        f"| {accelerating_csta_model.format_distance(float(coordinates[1]))} "
        f"| {accelerating_csta_model.format_speed(beta)} |"
        for tau, coordinates, beta in (
            (
                tau,
                accelerating_csta_model.coordinates(sample),
                beta,
            )
            for tau, beta, sample in zip((0, 0.5, 1), acceleration_betas, acceleration_samples, strict=True)
        )
    )
    acceleration_g = accelerating_csta_model.format_acceleration(1)
    return (
        acceleration_carrier,
        acceleration_center,
        acceleration_class,
        acceleration_curve,
        acceleration_g,
        acceleration_physical_rows,
        acceleration_radius_squared,
    )


@app.cell
def _(
    acceleration_carrier,
    acceleration_center,
    acceleration_class,
    acceleration_curve,
    acceleration_g,
    acceleration_physical_rows,
    acceleration_radius_squared,
    gm,
):
    gm.md(rt"""
    {acceleration_curve:expr}

    | Classifier field | Computed result |
    |:--|:--|
    | kind | `{acceleration_class.kind}` |
    | causal tangents | `{acceleration_class.causal}` |
    | carrier inertia (positive, negative, zero) | `{acceleration_carrier!s}` |
    | centre vector | {acceleration_center:value} |
    | signed radius² | `{acceleration_radius_squared:.6g}` |

    At constant proper acceleration **{acceleration_g}**:

    | Alice's proper time | Coordinate time in the departure frame | Distance from departure | Instantaneous coordinate speed |
    |:--|:--|:--|:--|
    {acceleration_physical_rows}

    The rotor also gives the four-velocity
    $u=R\gamma_0\widetilde R$. Its spatial/time component ratio is $v/c$.
    We extract those components using the actual metric:

    $$
    \beta=\frac{{(u\cdot\gamma_1)/\gamma_1^2}}{{(u\cdot\gamma_0)/\gamma_0^2}}.
    $$

    This is the instantaneous speed in the departure frame; it differs from
    `speed_between(first, second)`, which returns an average coordinate speed.
    Months in these strings mean one twelfth of a Julian year, not calendar
    months. The classifier's centre and radius² remain in natural units.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. A light signal across one astronomical unit

    Convert one AU to the model's natural length unit. The light travel time
    has the same natural value because $c=1$. We use the defined AU and
    speed of light, rather than rounding the time to $499$ seconds. The
    emission and reception have zero interval and define a null light ray.
    """)
    return


@app.cell
def _(csta_model):
    solar_natural_distance = csta_model.unit_scale.distance_from(1, "AU")
    sun_emission = csta_model.event(0, 0, 0, 0).named("S")
    earth_reception = csta_model.event(solar_natural_distance, solar_natural_distance, 0, 0).named("E")
    solar_interval = csta_model.separation_squared(sun_emission, earth_reception)
    solar_ray = csta_model.flat_line(sun_emission, earth_reception).named("L_{SE}", latex=r"L_{SE}")
    solar_classification = csta_model.classify(solar_ray)
    solar_distance_km = csta_model.distance_in(solar_natural_distance, "km")
    solar_distance_display = csta_model.format_distance(solar_natural_distance)
    solar_time_seconds = csta_model.time_in(solar_natural_distance)
    solar_time_display = csta_model.format_time(solar_natural_distance)
    solar_speed_display = csta_model.format_speed(csta_model.speed_between(sun_emission, earth_reception, unit="c"))
    return (
        solar_classification,
        solar_distance_display,
        solar_distance_km,
        solar_interval,
        solar_ray,
        solar_speed_display,
        solar_time_display,
        solar_time_seconds,
    )


@app.cell
def _(
    gm,
    solar_classification,
    solar_distance_display,
    solar_distance_km,
    solar_interval,
    solar_ray,
    solar_speed_display,
    solar_time_display,
    solar_time_seconds,
):
    gm.md(t"""
    {solar_ray}

    - Distance: **{solar_distance_display}** = `{solar_distance_km:,.3f}` km
    - Travel time: **{solar_time_display}** = `{solar_time_seconds:.6f}` seconds
    - Coordinate speed: **{solar_speed_display}**
    - Computed interval²: `{solar_interval:g}`
    - Classified carrier: `{solar_classification.causal}`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## API summary

    ```python
    algebra = Algebra(config=presets.csta(), expr=True)
    csta = ConformalSpacetimeModel(algebra, expr=True)

    event = csta.event(t, x, y, z)
    coordinates = csta.coordinates(event)
    interval2 = csta.separation_squared(first, second)

    pair = csta.event_pair(first, second)
    line = csta.flat_line(first, second)
    signed_round = csta.signed_round(center, radius_squared)

    direct = csta.classify(event, representation="direct")
    dual = csta.classify(signed_round, representation="dual")

    # Select the model default, or override a single construction.
    expanded_csta = csta.with_expression_form("expanded")
    expanded_event = expanded_csta.event(t, x, y, z)
    compact_event = expanded_csta.event(t, x, y, z, expression_form="operator")

    # Physical input/output, while the algebra retains its c=1 metric.
    si = ConformalSpacetimeModel(algebra, units="si")
    event = si.event(60, 2000, 0, 0)  # seconds and metres
    mixed = si.event(1, 2, 0, 0, units=("min", "km"))
    si.coordinates(mixed, units="si")
    si.format_speed(0.97)             # "97% c"
    si.speed_in(0.97, "m/s")          # numeric result

    scale = SpacetimeUnits.for_acceleration(1, unit="g")
    ship = ConformalSpacetimeModel(algebra, unit_scale=scale)
    ship.format_acceleration(1)       # "1 g"
    ```

    The algebra computes the products. The model supplies spacetime roles,
    coordinate semantics, causal interpretation, and object classification.

    Conversion constants follow the [SI definitions](https://www.bipm.org/en/measurement-units/si-defining-constants),
    [JPL astronomical parameters](https://ssd.jpl.nasa.gov/astro_par.html),
    and [NIST's standard gravity](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9).
    """)
    return


if __name__ == "__main__":
    app.run()
