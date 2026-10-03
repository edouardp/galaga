"""A continuously accelerating ship: hyperbolic motion, CSTA meets, and radio contact."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(
    width="medium",
    layout_file="layouts/conformal_spacetime_events.grid.json",
)


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, BladeConvention, Name, dual, exp, meet, metric_inner_product, sandwich

    return (
        Algebra,
        BladeConvention,
        Name,
        dual,
        exp,
        gm,
        meet,
        metric_inner_product,
        mo,
        np,
        plt,
        sandwich,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Can Earth keep talking to a ship accelerating at 1 g?

    Alice leaves Earth at rest and keeps her engine on, feeling a constant
    **proper acceleration**. Earth sends a radio message; Alice immediately
    echoes it. When does she receive it, when does Earth hear back, and can
    a message sent too late ever catch her?

    Conformal spacetime algebra (CSTA) turns this into geometry:
    **three sampled events define Alice's hyperbola; that curve meets a
    light cone to find reception; a second light cone meets Earth's line
    to find the echo.** We will name those objects and show each GA equation
    next to its short piece of code.

    The calculation uses natural units throughout. The chosen acceleration
    supplies a conversion to seconds, years, metres, AU, and light-years.
    This is an ideal constant-acceleration journey in flat spacetime, with
    no turnaround, braking, fuel budget, or gravitational fields.
    """)
    return


@app.cell
def _(mo):
    acceleration_g = mo.ui.slider(0.1, 2.0, step=0.1, value=1.0, label="Alice's proper acceleration (g)")
    acceleration_g  # noqa: B018
    return (acceleration_g,)


@app.cell(hide_code=True)
def _(acceleration_g, np):
    c_si = 299_792_458.0
    standard_gravity = 9.80665
    year_seconds = 365.25 * 86400
    au_metres = 149_597_870_700.0
    light_year_metres = c_si * year_seconds
    acceleration_si = acceleration_g.value * standard_gravity
    time_scale = c_si / acceleration_si
    length_scale = c_si * time_scale
    time_units = {
        "s": 1.0,
        "min": 60.0,
        "h": 3600.0,
        "days": 86400.0,
        "weeks": 7 * 86400.0,
        "months": year_seconds / 12,
        "years": year_seconds,
    }
    distance_units = {"m": 1.0, "km": 1000.0, "AU": au_metres, "ly": light_year_metres}

    def time_in(natural_time, unit="s"):
        """Return a numeric time in the requested unit, using the selected acceleration."""
        return natural_time * time_scale / time_units[unit]

    def distance_in(natural_distance, unit="m"):
        """Return a numeric distance in the requested unit."""
        return natural_distance * length_scale / distance_units[unit]

    def readable_quantity(base_value, units, unit, significant_digits):
        if unit == "auto":
            for candidate, size in reversed(tuple(units.items())):
                if abs(base_value) >= size:
                    unit = candidate
                    break
            else:
                unit = next(iter(units))
        value = base_value / units[unit]
        magnitude = ""
        for size, label in ((1e12, "trillion "), (1e9, "billion "), (1e6, "million ")):
            if abs(value) >= size:
                value /= size
                magnitude = label
                break
        places = 0 if value == 0 else max(0, significant_digits - 1 - int(np.floor(np.log10(abs(value)))))
        return f"{value:,.{places}f} {magnitude}{unit}"

    def format_time(natural_time, unit="auto", significant_digits=3):
        """Return a readable string; months mean one twelfth of a Julian year."""
        return readable_quantity(natural_time * time_scale, time_units, unit, significant_digits)

    def format_distance(natural_distance, unit="auto", significant_digits=3):
        """Return a readable string in m, km, AU, or ly."""
        return readable_quantity(natural_distance * length_scale, distance_units, unit, significant_digits)

    return (
        au_metres,
        distance_in,
        format_distance,
        format_time,
        length_scale,
        light_year_metres,
        time_in,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What does one natural unit mean?

    Set $T_0=c/a$ and $L_0=c^2/a$. Then

    $$\boxed{t_{\rm seconds}=T_0t,\qquad
    \tau_{\rm seconds}=T_0\tau,\qquad x_{\rm metres}=L_0x.}$$

    Here $\tau$ is **Alice's clock**, $t$ is **Earth-frame time**, and $x$
    is Earth-frame distance. Natural proper time $\tau=a\tau_{\rm seconds}/c$
    is also the rapidity acquired from rest. Changing the acceleration
    changes these physical scales; the dimensionless geometry stays the same.

    The helpers return numbers with `time_in(t, "days")` and
    `distance_in(x, "AU")`, or strings with `format_time(t)`
    and `format_distance(x)`. Pass a unit to either formatter to
    choose it explicitly. A year is 365.25 days; a displayed month is one
    twelfth of that year, rather than a calendar month.
    """)
    return


@app.cell
def _(acceleration_g, distance_in, format_distance, format_time, gm, time_in):
    gm.md(t"""
    At **{acceleration_g.value:.1f} g**, one natural time unit is
    **{format_time(1, "days")}** = **{time_in(1, "years"):.4f} years**.
    One natural distance unit is **{format_distance(1)}**.

    | Example call                  | Result                         |
    |:------------------------------|:-------------------------------|
    | `time_in(0.5, "days")`        | {time_in(0.5, "days"):.3f}     |
    | `format_time(0.5)`            | {format_time(0.5)}             |
    | `distance_in(0.25, "AU")`     | {distance_in(0.25, "AU"):,.3f} |
    | `format_distance(0.25, "ly")` | {format_distance(0.25, "ly")}  |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Embed a spacetime event

    Use the ordered basis
    $\{\gamma_0,\gamma_1,\gamma_2,\gamma_3,n_o,n_\infty\}$ with
    $\gamma_0^2=1$, $\gamma_i^2=-1$, $n_o^2=n_\infty^2=0$, and
    $n_o\cdot n_\infty=-1$. This gives $\mathrm{Cl}(2,4)$.

    For the physical spacetime vector $q=t\gamma_0+x\gamma_1$,

    $$\boxed{X(q)=n_o+q+\tfrac12q^2n_\infty.}$$

    An embedded event satisfies $X^2=0$ and $X\cdot n_\infty=-1$.
    Most usefully,

    $$\boxed{-2X(q_1)\cdot X(q_2)=(q_1-q_2)^2.}$$

    Positive squared separation is timelike, negative is spacelike, and
    zero is lightlike. The zero case is our test for a radio signal.
    """)
    return


@app.cell(hide_code=True)
def _(Algebra, BladeConvention, Name, np):
    gram = np.zeros((6, 6))
    gram[:4, :4] = np.diag([1, -1, -1, -1])
    gram[4, 5] = gram[5, 4] = -1
    _vector_names = tuple(Name(f"g{_i}", f"γ{'₀₁₂₃'[_i]}", rf"\gamma_{_i}") for _i in range(4)) + (
        Name("n_o", "nₒ", r"n_o"),
        Name("n_inf", "n∞", r"n_\infty"),
    )
    _labels = {}
    for _mask in range(1 << 6):
        _parts = [_name for _i, _name in enumerate(_vector_names) if _mask & (1 << _i)]
        _labels[_mask] = Name(
            "".join(_name.ascii for _name in _parts) or "1",
            "∧".join(_name.unicode for _name in _parts) or "1",
            r" \wedge ".join(_name.latex for _name in _parts) or "1",
        )
    csta = Algebra(gram=gram, blades=BladeConvention(6, _labels), expr=True)
    g0, g1, g2, g3, origin, infinity = csta.basis_vectors(expr=True)
    return csta, g0, g1, g2, g3, infinity, origin


@app.cell
def _(g0, g1, g2, g3, infinity, origin):
    def spacetime(t, x=0.0, y=0.0, z=0.0):
        return t * g0 + x * g1 + y * g2 + z * g3

    def embed(q):
        return origin + q + 0.5 * (q * q) * infinity

    def event(t, x=0.0, y=0.0, z=0.0):
        return embed(spacetime(t, x, y, z))

    return embed, event


@app.cell(hide_code=True)
def _(csta, gm, mo):
    mo.accordion({"Inspect the metric and basis": gm.md(t"""{csta.bilinear_form_table():block}""")})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. A boost rotor draws Alice's hyperbola

    Define $B=\gamma_1\gamma_0$, so $B^2=+1$. The boost rotor and Alice's
    unit four-velocity are

    $$\boxed{R(\tau)=\exp(\tfrac12\tau B),\qquad
    u(\tau)=R(\tau)\gamma_0\widetilde R(\tau).}$$

    The position, with $q(0)=0$, can also be written as a rotor sandwich:

    $$\boxed{q(\tau)=R(\tau)\gamma_1\widetilde R(\tau)-\gamma_1.}$$

    This is a hyperbolic rotation about the shifted center $-\gamma_1$.
    Differentiating it gives $dq/d\tau=u$, so it describes an accelerating
    worldline, rather than a single change of inertial frame.
    """)
    return


@app.cell
def _(embed, exp, g0, g1, sandwich):
    boost_plane = g1 * g0

    def alice_rotor(tau):
        return exp(0.5 * tau * boost_plane)

    def alice_velocity(tau):
        return sandwich(alice_rotor(tau), g0)

    def alice_position(tau):
        return sandwich(alice_rotor(tau), g1) - g1

    def alice_event(tau):
        return embed(alice_position(tau))

    return alice_event, alice_position


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Why do sinh and cosh appear?

    Since $B^2=+1$, the even and odd powers in the exponential give
    $R=\cosh(\tau/2)+B\sinh(\tau/2)$. Expanding the sandwiches yields

    $$u=\cosh\tau\,\gamma_0+\sinh\tau\,\gamma_1,\qquad
    q=\sinh\tau\,\gamma_0+(\cosh\tau-1)\gamma_1.$$

    Hence $t(\tau)=\sinh\tau$ and $x(\tau)=\cosh\tau-1$. These are
    coordinates of the rotor-generated motion. They obey

    $$\boxed{(x+1)^2-t^2=1},\qquad u^2=1,\qquad v/c=\tanh\tau.$$

    The trajectory is a **hyperbola in a flat Minkowski plane**. Its shape
    does not mean spacetime itself is curved. Alice follows the right
    branch after departure, $\tau\ge0$; the full algebraic curve also
    includes its earlier continuation and the other branch.
    """)
    return


@app.cell
def _(mo):
    proper_time_control = mo.ui.slider(0.0, 3.0, step=0.01, value=0.7, label="Alice's natural proper time τ")
    proper_time_control  # noqa: B018
    return (proper_time_control,)


@app.cell
def _(alice_position, g0, g1, metric_inner_product, proper_time_control):
    current_position = alice_position(proper_time_control.value)
    current_t = float(metric_inner_product(current_position, g0))
    current_x = -float(metric_inner_product(current_position, g1))
    return current_t, current_x


@app.cell(hide_code=True)
def _(
    current_t,
    current_x,
    format_distance,
    format_time,
    gm,
    np,
    proper_time_control,
):
    gm.md(t"""
    | Clock or distance | Natural value | Physical value |
    |:--|--:|:--|
    | Alice's elapsed proper time | {proper_time_control.value:.3f} | {format_time(proper_time_control.value)} |
    | Earth-frame elapsed time | {current_t:.3f} | {format_time(current_t)} |
    | Distance from Earth | {current_x:.3f} | {format_distance(current_x)} |

    Alice's speed in Earth's frame is **{np.tanh(proper_time_control.value):.3%} of c**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Three sampled events define the conformal curve

    In 3D Euclidean CGA, wedging three non-collinear **embedded points**
    defines their circle. The same construction works here with conformally
    embedded spacetime events. In a Euclidean carrier plane the round has
    a circular equation; in Alice's timelike carrier plane this round has
    the hyperbolic equation $(x+1)^2-t^2=1$.

    Sample Alice at **proper** times $0,\frac12,1$:
    $A_0=X(q(0))$, $A_{1/2}=X(q(1/2))$, $A_1=X(q(1))$.
    The Earth times of those events are $0,\sinh(1/2),\sinh(1)$.

    $$\boxed{C=A_0\wedge A_{1/2}\wedge A_1.}$$

    $C$ is a grade-three **OPNS round**: its events satisfy $X(q)\wedge C=0$.
    Here the round is hyperbolic because its carrier plane has signature
    $(1,1)$. The three events determine the full conformal conic; the
    physical branch and forward time are extra selections. This wedge is
    of the **six-dimensional embedded events**, not the raw STA vectors.

    Our samples lie on the unit hyperbola generated above, whose natural
    proper acceleration is one. A time component alone does not make any
    three events samples of this worldline: the plane's metric and the
    resulting round matter. Restoring units gives hyperbola radius $c^2/a$.
    """)
    return


@app.cell
def _(alice_event):
    A0 = alice_event(0).named("A0", latex=r"A_0")
    Ahalf = alice_event(0.5).named("Ahalf", latex=r"A_{1/2}")
    A1 = alice_event(1).named("A1", latex=r"A_1")
    alice_curve = (A0 ^ Ahalf ^ A1).named("C")
    return (alice_curve,)


@app.cell(hide_code=True)
def _(
    alice_curve,
    alice_event,
    format_distance,
    format_time,
    gm,
    np,
    proper_time_control,
):
    sample_table = "\n".join(
        f"| {tau:g} | {np.sinh(tau):.4f} | {np.cosh(tau) - 1:.4f} | "
        f"{format_time(tau)} | {format_time(np.sinh(tau))} | {format_distance(np.cosh(tau) - 1)} |"
        for tau in (0, 0.5, 1)
    )
    curve_residual = max(
        abs(coefficient) for coefficient in (alice_event(proper_time_control.value) ^ alice_curve).data
    )
    gm.md(rt"""
    | Sample $\tau$ | $t$ | $x$ | Alice's clock | Earth's clock | Distance |
    |--:|--:|--:|:--|:--|:--|
    {sample_table}

    At the selected $\tau$, the largest coefficient of $X(q)\wedge C$ is
    **{curve_residual:.2g}** (zero to floating-point precision).
    """)
    return


@app.cell(hide_code=True)
def _(current_t, current_x, distance_in, np, plt, time_in):
    _tau = np.linspace(-1.5, max(2.1, np.arcsinh(current_t) + 0.1), 220)
    worldline_figure, _ax = plt.subplots(figsize=(7, 5.5))
    _ax.plot(np.cosh(_tau) - 1, np.sinh(_tau), color="darkorange", label="C: right hyperbola branch")
    _ax.plot(-np.cosh(_tau) - 1, np.sinh(_tau), color="0.65", linestyle=":", label="C: other branch")
    for _value, _label in ((0, "A₀"), (0.5, "A½"), (1, "A₁")):
        _x, _t = np.cosh(_value) - 1, np.sinh(_value)
        _ax.scatter([_x], [_t], color="black", zorder=5)
        _ax.annotate(f"{_label}  (τ={_value:g})", (_x, _t), xytext=(10, -3), textcoords="offset points")
    _ax.scatter([current_x], [current_t], color="purple", zorder=6, label="selected Alice event")
    _ax.scatter([-1], [0], marker="+", color="0.3")
    _ax.annotate("center (−1, 0)", (-1, 0), xytext=(-5, -18), textcoords="offset points", ha="center")
    _ax.set(
        xlabel="x (natural distance)",
        ylabel="t (natural time)",
        title="Three conformal events define the hyperbolic round",
    )
    _ax.set_xlim(-4.5, max(3.5, 1.15 * current_x))
    _ax.set_ylim(-2, max(4, 1.1 * current_t))
    _ax.secondary_xaxis(
        "top", functions=(lambda x: distance_in(x, "ly"), lambda x: x / distance_in(1, "ly"))
    ).set_xlabel("distance (light-years)")
    _ax.secondary_yaxis(
        "right", functions=(lambda t: time_in(t, "years"), lambda t: t / time_in(1, "years"))
    ).set_ylabel("Earth time (years)")
    _ax.grid(alpha=0.2)
    _ax.legend(loc="upper left", fontsize=8)
    worldline_figure.tight_layout()
    worldline_figure  # noqa: B018
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Which CSTA objects are we intersecting?

    **OPNS** means a point is incident when $X\wedge A=0$; **IPNS** means
    it is incident when $X\cdot S=0$. Galaga's meet below takes two OPNS
    blades, so we use `dual` to convert an IPNS hypersurface.
    Multiplying an object blade by a nonzero scalar does not change its locus.

    | Symbol | Object in this example | Representation |
    |:--|:--|:--|
    | $\Pi$ | The full $t$–$x$ plane, with $y=z=0$ | grade 4, OPNS flat |
    | $H$ | All events a signed squared interval $-1$ from $(0,-1,0,0)$ | grade 1, IPNS round hypersurface |
    | $C$ | Alice's hyperbolic round in that plane | grade 3, OPNS round |
    | $K_E=X(E)$ | Past and future light cone of Earth's emission event | grade 1, IPNS zero-radius round |
    | $L_\oplus$ | Earth's inertial worldline at $x=y=z=0$ | grade 3, OPNS flat line |

    The signed round formula is
    $S(c,\rho^2)=X(c)-\frac12\rho^2n_\infty$.
    For $c=(0,-1,0,0)$ and $\rho^2=-1$, it gives
    $H=X(c)+\frac12n_\infty$. In full spacetime $H$ is a
    **three-dimensional hypersurface**. Intersecting it with $\Pi$ gives
    the same one-dimensional curve that we constructed from three samples:

    $$\boxed{C\ \propto\ \operatorname{meet}(\Pi,\operatorname{dual}(H)).}$$
    """)
    return


@app.cell
def _(dual, event, infinity, meet):
    spacetime_plane = event(0, 0) ^ event(1, 0) ^ event(0, 1) ^ infinity
    alice_round = event(0, -1) + 0.5 * infinity
    curve_from_surfaces = meet(spacetime_plane, dual(alice_round))
    return (curve_from_surfaces,)


@app.cell(hide_code=True)
def _(alice_curve, curve_from_surfaces, gm, np):
    curve_scale = float(np.dot(curve_from_surfaces.data, alice_curve.data) / np.dot(alice_curve.data, alice_curve.data))
    surface_curve_residual = float(np.max(np.abs(curve_from_surfaces.data - curve_scale * alice_curve.data)))
    gm.md(t"""
    The surface meet has grade **{curve_from_surfaces.homogeneous_grade()}**.
    It equals **{curve_scale:.5g} × C** up to a largest coefficient error of
    **{surface_curve_residual:.2g}**. Thus the plane–round meet and the
    three-event wedge describe the same geometry.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Meet Alice's curve with the emission light cone

    Earth emits at $E=(t_e,0)$. A reception event must be on both Alice's
    curve and this event's light cone:

    $$X(R)\wedge C=0,\qquad X(R)\cdot K_E=0,\qquad K_E=X(E).$$

    Their algebraic intersection is

    $$\boxed{P=C\cap K_E
      =\operatorname{meet}(C,\operatorname{dual}(K_E)).}$$

    $P$ is a grade-two point-pair blade. It describes the candidate
    intersection events, not yet a selected reception time. The full
    cone contains past as well as future light, and $C$ contains both
    hyperbola branches. We must choose Alice's post-departure branch and
    a future right-moving signal.
    """)
    return


@app.cell
def _(mo):
    emission_control = mo.ui.slider(0.05, 1.2, step=0.025, value=0.5, label="Earth's emission time tₑ (natural units)")
    emission_control  # noqa: B018
    return (emission_control,)


@app.cell
def _(alice_curve, dual, emission_control, event, meet):
    emission_time = emission_control.value
    emission = event(emission_time)
    light_cone = emission
    algebraic_intersection = meet(alice_curve, dual(light_cone))
    return algebraic_intersection, emission_time, light_cone


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Select the physical event from that intersection

    For the future right-moving ray, $x=t-t_e$. On Alice's worldline,
    $t-x=1-e^{-\tau}$, so

    $$\boxed{\tau_R=-\log(1-t_e),\quad 0\le t_e<1.}$$

    We use this coordinate equation to select the physical event and
    check it against the **computed meet blade**, $X(R)\wedge P=0$.
    At $t_e=1$ reception recedes to infinite proper time. Messages sent
    at or after this horizon never catch Alice while she accelerates forever.
    There is no last successful message: every $t_e<1$ works, with an
    ever-longer wait as $t_e$ approaches one.
    """)
    return


@app.cell(hide_code=True)
def _(alice_event, np):
    def radar_times(t_e):
        """Natural times and distance for a future signal and immediate echo."""
        if t_e < 0:
            raise ValueError("This journey starts at t_e=0.")
        if t_e >= 1:
            return None
        tau = float(-np.log1p(-t_e))
        return {
            "ship": tau,
            "receive": float(np.sinh(tau)),
            "distance": float(2 * np.sinh(tau / 2) ** 2),
            "echo": float(np.expm1(tau)),
        }

    def reception_event(t_e):
        timings = radar_times(t_e)
        return None if timings is None else alice_event(timings["ship"])

    return radar_times, reception_event


@app.cell(hide_code=True)
def _(
    algebraic_intersection,
    emission_time,
    light_cone,
    metric_inner_product,
    radar_times,
    reception_event,
):
    reception_data = radar_times(emission_time)
    reception = reception_event(emission_time)
    reception_residual = None if reception is None else max(abs(v) for v in (reception ^ algebraic_intersection).data)
    light_residual = None if reception is None else abs(float(metric_inner_product(reception, light_cone)))
    return light_residual, reception, reception_data, reception_residual


@app.cell(hide_code=True)
def _(
    emission_time,
    format_distance,
    format_time,
    gm,
    light_residual,
    reception_data,
    reception_residual,
):
    if reception_data is None:
        reception_report = (
            f"Emission at **{format_time(emission_time)}** is at or beyond the "
            f"**{format_time(1, 'days')}** horizon. There is no finite future reception."
        )
    else:
        reception_report = (
            "| Event or reading | Natural value | Physical value |\n|:--|--:|:--|\n"
            f"| Earth sends | {emission_time:.4f} | {format_time(emission_time)} |\n"
            f"| Alice receives: her clock | {reception_data['ship']:.4f} | {format_time(reception_data['ship'])} |\n"
            f"| Alice receives: Earth-frame time | {reception_data['receive']:.4f} | {format_time(reception_data['receive'])} |\n"
            f"| Distance at reception | {reception_data['distance']:.4f} | {format_distance(reception_data['distance'])} |\n\n"
            f"Meet incidence residual: **{reception_residual:.2g}**; "
            f"light-cone incidence residual: **{light_residual:.2g}**."
        )
    gm.md(t"""{reception_report}""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Meet the reply's light cone with Earth's worldline

    Alice echoes immediately from $R$. Earth is the flat line
    $L_\oplus=X(0)\wedge X(\gamma_0)\wedge n_\infty$. The new intersection is

    $$\boxed{Q=\operatorname{meet}(L_\oplus,\operatorname{dual}(X(R))).}$$

    Its two events are the original emission $E$ and the future echo arrival
    $F$. Choose the future one. The left-moving return ray gives

    $$\boxed{t_F=t_R+x_R=e^{\tau_R}-1=\frac{t_e}{1-t_e}.}$$

    For example, $t_e=0.5$ gives $R=(0.75,0.25)$ and $F=(1,0)$.
    The outbound and return legs each take $0.25$ Earth time units.
    Earth can still hear from Alice after the outbound-message horizon:
    that horizon limits which **new messages can catch her**.
    """)
    return


@app.cell
def _(dual, event, infinity, meet, reception, reception_data):
    earth_line = event(0) ^ event(1) ^ infinity
    echo_pair = None if reception is None else meet(earth_line, dual(reception))
    echo_event = None if reception_data is None else event(reception_data["echo"])
    return echo_event, echo_pair


@app.cell(hide_code=True)
def _(echo_event, echo_pair, emission_time, format_time, gm, reception_data):
    echo_residual = None if echo_pair is None else max(abs(v) for v in (echo_event ^ echo_pair).data)
    echo_report = (
        "Without reception there is no echoed reply."
        if reception_data is None
        else f"Earth hears the reply at **{format_time(reception_data['echo'])}** after departure "
        f"(natural time **{reception_data['echo']:.4f}**). The round trip took "
        f"**{format_time(reception_data['echo'] - emission_time)}**. "
        f"The selected event lies on the reply meet: residual **{echo_residual:.2g}**."
    )
    gm.md(t"""{echo_report}""")
    return


@app.cell(hide_code=True)
def _(distance_in, emission_time, np, plt, reception_data, time_in):
    _limit = 3.0 if reception_data is None else max(2.0, 1.12 * reception_data["echo"])
    _t = np.linspace(0, _limit, 280)
    _x = _t**2 / (np.sqrt(1 + _t**2) + 1)
    radar_figure, _ax = plt.subplots(figsize=(7, 6))
    _ax.plot(_x, _t, color="darkorange", linewidth=2, label="C: Alice's worldline")
    _ax.plot([0, 0], [0, _limit], color="0.3", label="L⊕: Earth")
    _ray_t = np.linspace(emission_time, _limit, 180)
    _ax.plot(_ray_t - emission_time, _ray_t, color="royalblue", label="future outgoing ray from E")
    _ax.plot([0, max(0, _limit - 1)], [1, _limit], color="0.6", linestyle="--", label="horizon ray: t − x = 1")
    _ax.scatter([0], [emission_time], color="royalblue", zorder=5)
    _ax.annotate("E: send", (0, emission_time), xytext=(8, -12), textcoords="offset points")
    if reception_data is not None:
        _r_t, _r_x, _f_t = reception_data["receive"], reception_data["distance"], reception_data["echo"]
        _ax.plot([_r_x, 0], [_r_t, _f_t], color="seagreen", linewidth=2, label="future reply from R")
        _ax.scatter([_r_x, 0], [_r_t, _f_t], color="seagreen", zorder=5)
        _ax.annotate("R: receive + reply", (_r_x, _r_t), xytext=(8, 0), textcoords="offset points")
        _ax.annotate("F: echo arrives", (0, _f_t), xytext=(8, 4), textcoords="offset points")
    _ax.set(xlim=(-0.12 * _limit, _limit), ylim=(0, _limit), xlabel="x (natural distance)", ylabel="t (natural time)")
    _ax.set_title("One message, two CSTA intersections")
    _ax.set_aspect("equal", adjustable="box")
    _ax.secondary_xaxis(
        "top", functions=(lambda x: distance_in(x, "ly"), lambda x: x / distance_in(1, "ly"))
    ).set_xlabel("distance (light-years)")
    _ax.secondary_yaxis(
        "right", functions=(lambda t: time_in(t, "years"), lambda t: t / time_in(1, "years"))
    ).set_ylabel("Earth time (years)")
    _ax.grid(alpha=0.2)
    _ax.legend(loc="lower right", fontsize=8)
    radar_figure.tight_layout()
    radar_figure  # noqa: B018
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Give the distances some scale

    The comparisons below use Jupiter's orbital **radius** (5.2 AU),
    the approximate distance to Alpha Centauri A/B (4.3 light-years),
    and the approximate distance to Andromeda (2.5 million light-years).
    They are rulers for comparison, not modeled rendezvous destinations.

    For a natural distance $d$, the same hyperbola gives
    $\tau=2\,\operatorname{asinh}\sqrt{d/2}$ and $t=\sqrt{d(d+2)}$.
    These forms also behave well for short trips. The last column shows
    how far **before the horizon** Earth must send a message to reach Alice
    at that milestone: $1-t_e=e^{-\tau}$.
    """)
    return


@app.cell(hide_code=True)
def _(
    au_metres,
    current_x,
    format_distance,
    format_time,
    gm,
    length_scale,
    light_year_metres,
    np,
):
    landmarks = (
        ("Jupiter's orbital radius", 5.2 * au_metres, 1.2),
        ("distance to Alpha Centauri A/B", 4.3 * light_year_metres, 2.0),
        ("distance to Andromeda", 2.5e6 * light_year_metres, 0.5),
    )
    milestone_rows = []
    for _label, _metres, _multiple in landmarks:
        _d = _multiple * _metres / length_scale
        _tau = float(2 * np.arcsinh(np.sqrt(_d / 2)))
        _earth_t = float(np.sqrt(_d * (_d + 2)))
        milestone_rows.append(
            f"| {_multiple:g} × {_label} | {format_distance(_d)} | {format_time(_tau)} | "
            f"{format_time(_earth_t)} | {format_time(np.exp(-_tau))} |"
        )
    milestone_table = "\n".join(milestone_rows)
    if current_x == 0:
        current_comparison = "Alice is at the departure point."
    else:
        _reference = min(landmarks, key=lambda item: abs(np.log(current_x * length_scale / item[1])))
        current_comparison = (
            f"The selected Alice event is at **{current_x * length_scale / _reference[1]:.3g} × "
            f"{_reference[0]}** from Earth."
        )
    gm.md(t"""
    {current_comparison}

    | Distance milestone | Distance | Alice's elapsed time | Earth's elapsed time | Send this long before the horizon |
    |:--|:--|:--|:--|:--|
    {milestone_table}

    These are uninterrupted outbound acceleration times: Alice passes the
    milestones at speed. The galaxy-scale row extrapolates the flat-spacetime
    model, without galactic motion, gravity, or cosmological expansion.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Follow the geometry

    $$\underbrace{A_0\wedge A_{1/2}\wedge A_1}_{\text{hyperbolic round }C}
    \quad\longrightarrow\quad
    \underbrace{C\cap K_E}_{\text{candidate receptions }P}
    \quad\longrightarrow\quad
    \underbrace{L_\oplus\cap K_R}_{\text{candidate echo arrivals }Q}.$$

    The wedge and meets identify the loci. The chosen future direction,
    branch, and clock distinguish a physical radio conversation from the
    other algebraic intersections.

    **Sources and conventions.** The hyperbolic worldline follows
    [Oregon State's uniform-acceleration derivation](https://sites.science.oregonstate.edu/physics/coursewikis/GSR/book/content/uniform.html).
    Unit conversions use [JPL's astronomical constants](https://ssd.jpl.nasa.gov/astro_par.html)
    and [NIST's standard gravity](https://nvlpubs.nist.gov/nistpubs/Legacy/TN/nbstechnicalnote491.pdf).
    Approximate distance rulers are from NASA:
    [Jupiter](https://science.nasa.gov/jupiter/jupiter-facts/),
    [Alpha Centauri A/B](https://science.nasa.gov/missions/hubble/hubbles-best-image-of-alpha-centauri-a-and-b/),
    and [Andromeda](https://science.nasa.gov/asset/hubble/measuring-the-drift-of-the-andromeda-galaxy-2/).
    The supplied CSTA notes motivated the construction. The
    [classifier worksheet](conformal_spacetime_classifier.py) expands on its object types.
    """)
    return


if __name__ == "__main__":
    app.run()
