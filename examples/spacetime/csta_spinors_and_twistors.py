"""CSTA spinors and twistors: ideals, incidence, light rays and conformal action."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from galaga_matrix import MatrixRepr

    import galaga_annotation as ga
    import galaga_marimo as gm
    from galaga import Algebra, even_grades, exp, grade, presets, scalar_product
    from galaga.models import ConformalSpacetimeModel

    return (
        Algebra,
        ConformalSpacetimeModel,
        MatrixRepr,
        even_grades,
        exp,
        ga,
        gm,
        grade,
        mo,
        np,
        plt,
        presets,
        scalar_product,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CSTA spinors and twistors

    A light ray has two useful descriptions: a blade in conformal spacetime
    and a projective null twistor. This notebook constructs both, then checks
    that they describe the same events.

    We will build a spinor space using a projector, choose complex coordinates,
    recover a ray from a twistor, recover an event from two incident twistors,
    and transform all these objects consistently.

    The coordinates and pairing below belong to an **explicit spinor frame**.
    A four-component conformal spinor is not automatically a Dirac particle
    state. Our calculations concern conformal geometry; no field equation or
    particle interpretation is assumed.

    This is a companion to the
    [CSTA zoo and operators](./csta_zoo_and_operators.py) and
    [model and units tour](./csta_model_and_classifiers.py).
    """)
    return


@app.cell
def _(Algebra, ConformalSpacetimeModel, presets):
    spin_algebra = Algebra(config=presets.csta(), user_config_files=False)
    spin_model = ConformalSpacetimeModel(spin_algebra)
    g0, g1, g2, g3 = spin_model.spacetime_basis_vectors()
    no, ni = spin_model.origin, spin_model.infinity
    spin_algebra
    return g0, g1, g2, ni, no, spin_algebra, spin_model


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. A projector gives us a spinor space

    The metric is $\gamma_0^2=1$, $\gamma_j^2=-1$ for spatial vectors,
    $n_o^2=n_\infty^2=0$, and $n_o\cdot n_\infty=-1$.
    ### K: the time–x boost plane

    $K=\gamma_1\gamma_0$ is an oriented bivector in the time–x plane.
    The plane has one positive and one negative metric direction, so
    $K^2=1$. It is a **boost generator**: exponentiating it gives the rotor

    $$
    R(\eta)=\exp(\tfrac12\eta K)
    =\cosh(\tfrac12\eta)+K\sinh(\tfrac12\eta).
    $$

    Here $\eta$ is rapidity. For example,
    $R\gamma_0\widetilde R=\cosh\eta\,\gamma_0+\sinh\eta\,\gamma_1$.
    Choosing $\gamma_1$ fixes a spatial axis for our spinor frame.

    ### E: the conformal scale plane

    $E=n_o\wedge n_\infty$ is the oriented plane element of the two extra
    conformal directions. Although its two basis vectors are individually
    null, their nonzero pairing makes their plane have signature $(1,1)$,
    giving $E^2=1$.

    Its exponential generates a **dilation**:

    $$
    D(\lambda)=\exp(\tfrac12\lambda E),\qquad
    Dn_o\widetilde D=e^{-\lambda}n_o,\qquad
    Dn_\infty\widetilde D=e^\lambda n_\infty.
    $$

    The spacetime part $q$ of a lifted event stays fixed before homogeneous
    normalization. Rescaling the transformed event so its $n_o$ coefficient
    is one then gives $q\mapsto e^\lambda q$. Thus this extra plane encodes
    **conformal scale**, rather than an extra physical spatial direction.
    See the [conformal dilation construction](https://clifford.readthedocs.io/en/latest/tutorials/cga/index.html#dilations);
    its plane orientation is opposite to our $n_o\wedge n_\infty$ convention.

    ### Why use this pair to build P?

    Both bivectors square to one, so each supplies two idempotent projectors,
    $(1\pm K)/2$ and $(1\pm E)/2$. Every direction in the time–x plane is
    orthogonal to every direction in the conformal scale plane, which makes
    $K$ and $E$ commute. We can therefore
    multiply the projectors to select one joint sector:

    $$
    P=\frac{1+K}{2}\frac{1+E}{2},\qquad
    P^2=P,\quad PK=PE=P.
    $$

    The letters $K$ and $E$ are labels for these two chosen bivectors.
    The spatial axis and the plus-sign sector are frame conventions.
    Their role here is to give us a convenient projector and a concrete
    spinor representation.

    The even left ideal

    $$
    S=\mathrm{Cl}^{+}(2,4)P,\qquad \psi=AP,\qquad \psi P=\psi
    $$

    is our spinor space. “Ideal” means it stays in this space when multiplied
    on the left by an even algebra element. The projector fixes a reference
    on the **right**: $\psi K=\psi$ and $\psi E=\psi$ follow from $\psi=AP$.
    Left multiplication, such as $R\psi$, transforms the spinor.

    The full algebra has 64 real dimensions; its even part has 32.
    The full left ideal $\mathrm{Cl}(2,4)P$ has 16 real dimensions, whereas
    $S$ has **8 real dimensions**, or four complex dimensions. We compute
    these ranks from products rather than assuming every projector is minimal.
    """)
    return


@app.cell
def _(g0, g1, ni, no, spin_algebra):
    boost_plane = g1 * g0
    null_plane = no ^ ni
    spin_projector = (1 + boost_plane) * (1 + null_plane) / 4
    I = spin_algebra.I
    spin_projector
    return I, boost_plane, null_plane, spin_projector


@app.cell
def _(I, gm, np, spin_algebra, spin_projector):
    even_blades = tuple(blade for k in (0, 2, 4, 6) for blade in spin_algebra.basis_blades(k))
    all_blades = tuple(blade for k in range(7) for blade in spin_algebra.basis_blades(k))
    even_ideal_rank = np.linalg.matrix_rank(np.column_stack([(b * spin_projector).data for b in even_blades]))
    full_ideal_rank = np.linalg.matrix_rank(np.column_stack([(b * spin_projector).data for b in all_blades]))
    projector_error = np.max(np.abs((spin_projector * spin_projector - spin_projector).data))
    gm.md(t"""
    | Computed property | Result |
    |---|---:|
    | Projector residual | {projector_error:.2g} |
    | Full ideal, real dimension | {full_ideal_rank} |
    | Even ideal, real dimension | {even_ideal_rank} |
    | Square of the pseudoscalar | {I * I} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Four complex coordinates, with an algebraic meaning

    Let $I$ be the six-dimensional pseudoscalar. It satisfies $I^2=-1$ and
    commutes with even elements. Left multiplication by $I$ supplies the
    complex structure on $S$: the complex number $i$ is represented by $I$.
    This $I$ is the **CSTA** pseudoscalar, not the four-dimensional STA one.

    Choose the frame

    $$
    f_0=P,\quad f_1=\gamma_0\gamma_2P,\quad
    f_2=I\gamma_0n_oP,\quad f_3=I\gamma_2n_oP.
    $$

    Then a column $Z=(z_0,z_1,z_2,z_3)^T\in\mathbb C^4$ encodes

    $$
    \psi(Z)=\sum_{j=0}^{3}\bigl(\operatorname{Re}z_j+
    I\operatorname{Im}z_j\bigr)f_j.
    $$

    We split the column into two two-component pieces, $Z=(\omega,\pi)$.
    The frame fixes their signs and axis convention; it is the bridge between
    the algebra and the matrices shown here.

    Columns below use **blue for the upper $\omega$ pair** and **amber for
    the lower $\pi$ pair**. The same row ordering is used in every column.
    """)
    return


@app.cell
def _(I, g0, g2, no, np, spin_projector):
    twistor_frame = (
        spin_projector,
        g0 * g2 * spin_projector,
        I * g0 * no * spin_projector,
        I * g2 * no * spin_projector,
    )
    frame_columns = np.column_stack([v.data for f in twistor_frame for v in (f, I * f)])
    return frame_columns, twistor_frame


@app.cell
def _(I, frame_columns, np, spin_algebra, twistor_frame):
    def twistor(z):
        """Encode a four-complex-component column in this notebook's frame."""
        z = np.asarray(z, dtype=complex)
        if z.shape != (4,) or not np.all(np.isfinite(z)):
            raise ValueError("Expected four finite complex coordinates")
        return sum(
            (float(c.real) * f + float(c.imag) * I * f for c, f in zip(z, twistor_frame, strict=True)),
            spin_algebra.scalar(0),
        )

    def twistor_coordinates(psi):
        """Recover coordinates; reject values outside the chosen even ideal."""
        if psi.algebra is not spin_algebra:
            raise ValueError("Expected a multivector in the notebook's CSTA algebra")
        scale = np.max(np.abs(psi.data))
        if scale == 0:
            return np.zeros(4, dtype=complex)
        normalized = psi.data / scale
        coefficients = np.linalg.lstsq(frame_columns, normalized, rcond=None)[0]
        if not np.allclose(frame_columns @ coefficients, normalized, atol=1e-10, rtol=1e-10):
            raise ValueError("The value is outside the chosen even spinor ideal")
        return scale * (coefficients[::2] + 1j * coefficients[1::2])

    def spin_action(operator):
        """Matrix of left multiplication on the chosen four-complex frame."""
        return np.column_stack([twistor_coordinates(operator * f) for f in twistor_frame])

    return spin_action, twistor, twistor_coordinates


@app.cell
def _(MatrixRepr, ga, np):
    column_annotator = ga.annotator(
        ga.on(ga.block(rows=slice(0, 2)), background="#e8f0ff", color="#1d4ed8"),
        ga.on(ga.block(rows=slice(2, 4)), background="#fff3df", color="#9a4d00"),
    )

    def twistor_column_view(z):
        column = MatrixRepr(np.asarray(z, dtype=complex).reshape(4, 1), kind="ket")
        return column_annotator(column)

    return (twistor_column_view,)


@app.cell
def _(
    I,
    gm,
    np,
    spin_projector,
    twistor,
    twistor_column_view,
    twistor_coordinates,
):
    sample_column = np.array([1 + 0.5j, -0.25j, 0.3, 1 - 0.2j])
    sample_spinor = twistor(sample_column)
    column_roundtrip = np.max(np.abs(twistor_coordinates(sample_spinor) - sample_column))
    ideal_residual = np.max(np.abs((sample_spinor * spin_projector - sample_spinor).data))
    phase_residual = np.max(np.abs(twistor_coordinates(I * sample_spinor) - 1j * sample_column))
    gm.md(t"""
    Example column:

    {gm.block_latex(twistor_column_view(sample_column))}

    | Check | Maximum residual |
    |---|---:|
    | Column → multivector → column | {column_roundtrip:.2g} |
    | Right multiplication by the projector leaves the spinor unchanged | {ideal_residual:.2g} |
    | Pseudoscalar multiplication agrees with multiplication by i | {phase_residual:.2g} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. The twistor pairing and its classification

    This conformal spinor space carries a Hermitian pairing of signature
    $(2,2)$. We derive its matrix from geometric products. Set

    $$
    C=I\gamma_0\left(n_o-\frac12n_\infty\right),\quad
    b(\psi,\phi)=4\left\langle\widetilde\psi\,\phi\,C\right\rangle_0,\quad
    h(\psi,\phi)=b(\psi,\phi)-i\,b(\psi,I\phi).
    $$

    In our frame its matrix is

    $$
    H=\begin{pmatrix}0&\mathbf1_2\\\mathbf1_2&0\end{pmatrix},\qquad
    h(Z,W)=Z^\dagger HW,\qquad
    h(Z,Z)=2\operatorname{Re}(\omega^\dagger\pi).
    $$

    A nonzero twistor is **null**, **positive** or **negative** according to
    the sign of $h(Z,Z)$. Zero has no projective meaning.
    Positive/negative here describes this pairing, not spacetime causality.

    The labels require the spinor frame and pairing. The notebook's
    `twistor_kind()` checks them; the model's geometric and operator
    classifiers continue to answer their own questions.
    """)
    return


@app.cell
def _(I, g0, grade, ni, no):
    pairing_connector = I * g0 * (no - ni / 2)

    def twistor_pairing(psi, phi):
        """Hermitian pairing, derived from this frame's geometric products."""
        real_part = 4 * float(grade(~psi * phi * pairing_connector, 0))
        imaginary_part = -4 * float(grade(~psi * I * phi * pairing_connector, 0))
        return complex(real_part, imaginary_part)

    return (twistor_pairing,)


@app.cell
def _(np, twistor_coordinates, twistor_frame, twistor_pairing):
    twistor_metric = np.array([[twistor_pairing(u, v) for v in twistor_frame] for u in twistor_frame])

    def twistor_kind(psi, *, tolerance=1e-10):
        z = twistor_coordinates(psi)
        scale = np.max(np.abs(z))
        if scale == 0:
            return "zero (not projective)"
        z = z / scale
        norm = float((z.conj() @ twistor_metric @ z).real)
        if abs(norm) <= tolerance:
            return "null twistor"
        return "positive twistor" if norm > 0 else "negative twistor"

    return twistor_kind, twistor_metric


@app.cell
def _(
    MatrixRepr,
    gm,
    np,
    twistor,
    twistor_kind,
    twistor_metric,
    twistor_pairing,
):
    pairing_examples = (
        ("Zero", twistor([0, 0, 0, 0])),
        ("Null, incident to the origin", twistor([0, 0, 1, 0])),
        ("Positive", twistor([1, 0, 1, 0])),
        ("Negative", twistor([1, 0, -1, 0])),
        ("Null, no finite event incidence", twistor([1, 0, 0, 0])),
    )
    pairing_rows = "\n".join(
        f"| {name} | {twistor_pairing(psi, psi).real:.3g} | {twistor_kind(psi)} |" for name, psi in pairing_examples
    )
    metric_spectrum = np.linalg.eigvalsh(twistor_metric)
    gm.md(t"""
    Computed pairing matrix:

    {gm.block_latex(MatrixRepr(twistor_metric))}

    Eigenvalues: **{metric_spectrum}**.

    | Example | Pairing with itself | Classification |
    |---|---:|---|
    {pairing_rows}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Event incidence: a product that vanishes

    For a lifted event $X(q)=n_o+q+\frac12q^2n_\infty$, incidence is

    $$
    X(q)\psi=0.
    $$

    In our coordinates, the equivalent equation is

    $$
    \omega=-iQ(q)\pi,\qquad
    Q(t,x,y,z)=
    \begin{pmatrix}
    t+x&-y+iz\\-y-iz&t-x
    \end{pmatrix},\qquad \det Q=q^2.
    $$

    The unusual spatial axis placement follows from our chosen frame.
    $Q$ is Hermitian for real spacetime coordinates.

    We obtain $Q$ from the actual left action of the translator
    $T(q)=1-\frac12q n_\infty$. It maps $n_o$ to $X(q)$ and has block form

    $$
    M(T(q))=\begin{pmatrix}\mathbf1_2&-iQ(q)\\0&\mathbf1_2\end{pmatrix}.
    $$

    Thus an origin-incident spinor $(0,\pi)$ becomes
    $(-iQ(q)\pi,\pi)$. For fixed $q$, arbitrary nonzero $\pi\in\mathbb C^2$
    gives the incident twistor family. After complex rescaling that family
    is a projective line, $\mathbb{CP}^1$.
    """)
    return


@app.cell
def _(ni, np, spin_action, spin_model, twistor):
    def spacetime_matrix(q):
        """Derive the Hermitian coordinate matrix from the translator action."""
        vector = spin_model.spacetime_vector(q)
        translator = 1 - vector * ni / 2
        return 1j * spin_action(translator)[:2, 2:]

    def incident_twistor(q, pi):
        pi = np.asarray(pi, dtype=complex)
        if pi.shape != (2,) or not np.all(np.isfinite(pi)) or not np.any(pi):
            raise ValueError("Expected a nonzero finite two-component spinor")
        return twistor(np.concatenate((-1j * spacetime_matrix(q) @ pi, pi)))

    return incident_twistor, spacetime_matrix


@app.cell
def _(
    MatrixRepr,
    ga,
    gm,
    incident_twistor,
    ni,
    np,
    spacetime_matrix,
    spin_action,
    spin_model,
    twistor_column_view,
    twistor_coordinates,
    twistor_kind,
):
    emission_coordinates = np.array([0.7, 0.2, -0.3, 0.4])
    emission_event = spin_model.event(*emission_coordinates)
    ray_spinor = incident_twistor(emission_coordinates, [1, 0.4 + 0.3j])
    emission_translator = 1 - spin_model.spacetime_vector(emission_coordinates) * ni / 2
    event_incidence_error = np.max(np.abs((emission_event * ray_spinor).data))
    interval_error = abs(
        np.linalg.det(spacetime_matrix(emission_coordinates))
        - float(spin_model.spacetime_vector(emission_coordinates) ** 2)
    )
    translator_view = ga.annotate(
        MatrixRepr(spin_action(emission_translator)),
        ga.on(ga.block(rows=slice(0, 2), columns=slice(2, 4)), background="#e8f5e9", color="#166534"),
    )
    gm.md(t"""
    An emission event has natural coordinates **{emission_coordinates}**.
    One incident twistor has column

    {gm.block_latex(twistor_column_view(twistor_coordinates(ray_spinor)))}

    Its label is **{twistor_kind(ray_spinor)}**. The geometric-product
    incidence residual is **{event_incidence_error:.2g}**; the determinant /
    spacetime-square residual is **{interval_error:.2g}**.

    Its translator acts through this matrix. The **green block** mixes
    the lower pi pair into the upper omega pair; the lower pair stays fixed.

    {gm.block_latex(translator_view)}
    """)
    return emission_coordinates, emission_event, ray_spinor


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. One projective null twistor → a light ray

    Holding $(\omega,\pi)$ fixed, solve $Q(q)\pi=i\omega$ for **real** $q$.
    With $\pi\ne0$, the real linear system has rank three. A null twistor
    makes it consistent, so its solutions form

    $$
    q(s)=q_*+s\,\ell,\qquad \ell^2=0.
    $$

    The least-squares anchor $q_*$ below is a convenient point on the ray;
    it is not a distinguished origin. We normalize $\ell^0=1$, selecting
    the future-directed parameter. The corresponding spatial velocity
    has magnitude $c$.

    Positive and negative twistors have no real finite event solving this
    incidence equation. A null twistor with $\pi=0$, $\omega\ne0$ also has no
    finite solution; its incidence belongs to the conformal boundary.
    """)
    return


@app.cell
def _(np, spacetime_matrix, twistor_coordinates):
    coordinate_matrices = tuple(spacetime_matrix(unit) for unit in np.eye(4))

    def real_incidence_system(psi):
        z = twistor_coordinates(psi)
        scale = np.max(np.abs(z))
        if scale:
            z = z / scale
        coefficients = np.column_stack([matrix @ z[2:] for matrix in coordinate_matrices])
        target = 1j * z[:2]
        return np.vstack((coefficients.real, coefficients.imag)), np.concatenate((target.real, target.imag))

    def finite_light_ray(psi):
        """Recover the finite ray; reject inconsistent or boundary incidence."""
        coefficients, target = real_incidence_system(psi)
        if np.linalg.matrix_rank(coefficients) != 3:
            raise ValueError("Expected a nonzero twistor with finite light-ray incidence")
        anchor = np.linalg.lstsq(coefficients, target, rcond=None)[0]
        if not np.allclose(coefficients @ anchor, target, atol=1e-10):
            raise ValueError("This twistor has no real finite event incidence")
        direction = np.linalg.svd(coefficients)[2][-1]
        return anchor, direction / direction[0]

    return finite_light_ray, real_incidence_system


@app.cell
def _(gm, np, real_incidence_system, twistor, twistor_kind):
    incidence_examples = (
        ("Finite null example", twistor([0, 0, 1, 0])),
        ("Positive example", twistor([1, 0, 1, 0])),
        ("Negative example", twistor([1, 0, -1, 0])),
        ("Boundary null example", twistor([1, 0, 0, 0])),
    )
    incidence_rows = []
    for incidence_name, incidence_spinor in incidence_examples:
        incidence_matrix, incidence_target = real_incidence_system(incidence_spinor)
        incidence_solution = np.linalg.lstsq(incidence_matrix, incidence_target, rcond=None)[0]
        incidence_residual = np.linalg.norm(incidence_matrix @ incidence_solution - incidence_target)
        incidence_rows.append(
            f"| {incidence_name} | {twistor_kind(incidence_spinor)} "
            f"| {np.linalg.matrix_rank(incidence_matrix)} | {incidence_residual:.2g} |"
        )
    gm.md(t"""
    Here is the finite incidence calculation for each kind.
    A nonzero residual means that no real finite event solves the equation.

    | Example | Pairing label | Real-system rank | Best incidence residual |
    |---|---|---:|---:|
    {"\n".join(incidence_rows)}
    """)
    return


@app.cell
def _(finite_light_ray, gm, np, ray_spinor, spin_model):
    ray_anchor, ray_direction = finite_light_ray(ray_spinor)
    ray_events = tuple(spin_model.event(*(ray_anchor + s * ray_direction)) for s in (-1, 0, 1))
    direct_light_ray = ray_events[0] ^ ray_events[1]
    flat_light_ray = direct_light_ray ^ spin_model.infinity
    null_direction_error = abs(float(spin_model.spacetime_vector(ray_direction) ** 2))
    ray_product_error = max(np.max(np.abs((event * ray_spinor).data)) for event in ray_events)
    ray_wedge_error = np.max(np.abs((ray_events[2] ^ direct_light_ray).data))
    light_speed = spin_model.format_speed(np.linalg.norm(ray_direction[1:]), unit="% c")
    gm.md(t"""
    | Computed quantity | Result |
    |---|---|
    | An anchor on the ray | {ray_anchor} |
    | Future-directed tangent | {ray_direction} |
    | Spatial speed | {light_speed} |
    | Tangent square residual | {null_direction_error:.2g} |
    | Event × spinor incidence residual | {ray_product_error:.2g} |
    | Third event ∧ two-event blade residual | {ray_wedge_error:.2g} |
    | Classification of the grade-2 blade | {spin_model.classify(direct_light_ray).kind} |
    | Classification after wedging infinity | {spin_model.classify(flat_light_ray).kind} |
    """)
    return ray_anchor, ray_direction


@app.cell
def _(mo):
    ray_parameter = mo.ui.slider(-2, 2, step=0.1, value=0.5, label="Position along the light ray (natural parameter)")
    return (ray_parameter,)


@app.cell
def _(
    gm,
    np,
    ray_anchor,
    ray_direction,
    ray_parameter,
    ray_spinor,
    spin_model,
):
    selected_ray_coordinates = ray_anchor + ray_parameter.value * ray_direction
    selected_ray_event = spin_model.event(*selected_ray_coordinates)
    selected_incidence_error = np.max(np.abs((selected_ray_event * ray_spinor).data))
    gm.md(t"""
    Selected event coordinates: **{selected_ray_coordinates}**.
    Its product with the fixed spinor has residual **{selected_incidence_error:.2g}**.
    """)
    return


@app.cell
def _(
    emission_coordinates,
    mo,
    np,
    plt,
    ray_anchor,
    ray_direction,
    ray_parameter,
):
    ray_parameters = np.linspace(-2, 2, 80)
    ray_points = ray_anchor[:, None] + ray_direction[:, None] * ray_parameters
    selected_ray_point = ray_anchor + ray_parameter.value * ray_direction
    ray_figure, ray_axes = plt.subplots(figsize=(7, 4))
    for coordinate, label in zip((1, 2, 3), ("x", "y", "z"), strict=True):
        ray_axes.plot(ray_points[0], ray_points[coordinate], label=label)
        ray_axes.scatter(selected_ray_point[0], selected_ray_point[coordinate], s=30)
    ray_axes.axvline(emission_coordinates[0], color="gray", linestyle=":", label="emission time")
    ray_axes.set(
        xlabel="t (natural)", ylabel="Spatial coordinate (natural)", title="One twistor, every event on a light ray"
    )
    ray_axes.legend()
    ray_axes.grid(alpha=0.2)

    mo.vstack([ray_parameter,ray_figure])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Two independent incident twistors → an event

    We can recover the event **using geometric products and grade
    extraction**, without solving a matrix incidence system. The construction
    uses the explicit spinor frame chosen in section 2.

    Fix the frame's antisymmetric connector

    $$
    B=\gamma_0\gamma_2(n_o-\tfrac12n_\infty),\qquad \widetilde B=-B.
    $$

    For two spinors, form the alternating bilinear

    $$
    A(\psi,\phi)=\psi B\widetilde\phi-\phi B\widetilde\psi.
    $$

    At the origin our frame gives
    $A(f_2,f_3)=-n_o$. Translate the two spinors with
    $T(q)=1-\frac12q n_\infty$. Their bilinear transforms as a sandwich:

    $$
    A(Tf_2,Tf_3)=T\,A(f_2,f_3)\widetilde T=-X(q).
    $$

    Thus the two origin-incident directions become two distinct light rays
    meeting at $q$, and their alternating spinor product gives that event.
    For this pair, the product is already a real vector; normalizing its
    conformal weight $w(V)=-V\cdot n_\infty$ gives $X$.

    Both have zero self-pairing, and their mutual pairing is also zero.
    The incident spinor plane is **totally isotropic** for $h$.

    ### The phase of a general pair

    Independent complex combinations of the two incident spinors multiply
    $A$ by their nonzero complex determinant. In the real algebra that phase
    can mix its grade-1 and grade-5 parts. Set

    $$
    V=\langle A\rangle_1,\qquad W=\langle A\rangle_5I,\qquad
    a=-V\cdot n_\infty,\quad b=-W\cdot n_\infty.
    $$

    Both $V$ and $W$ are real multiples of the same event vector, so

    $$
    X=\frac{aV+bW}{a^2+b^2}.
    $$

    This also works when multiplying one spinor by $I$ makes the entire
    grade-1 part vanish. Dependent pairs give $A=0$. A pair must span a
    real event's incident spinor plane; arbitrary null twistors need not
    meet. A zero denominator cannot select a finite event.
    """)
    return


@app.cell
def _(
    I,
    even_grades,
    g0,
    g2,
    grade,
    ni,
    no,
    np,
    scalar_product,
    spin_algebra,
    spin_projector,
):
    event_connector = g0 * g2 * (no - ni / 2)

    def event_from_twistors(psi, phi):
        """Recover a finite real event from this frame's incident spinor pair."""
        spinors = []
        for value in (psi, phi):
            if value.algebra is not spin_algebra or not np.all(np.isfinite(value.data)):
                raise ValueError("Expected finite spinors in the notebook's CSTA algebra")
            scale = np.max(np.abs(value.data))
            if scale == 0:
                raise ValueError("Zero has no projective twistor meaning")
            value = value / scale
            if not even_grades(value).almost_equal(value) or not (value * spin_projector).almost_equal(value):
                raise ValueError("Expected spinors in the chosen even ideal")
            spinors.append(value)
        psi, phi = spinors
        alternating = psi * event_connector * ~phi - phi * event_connector * ~psi
        scale = np.max(np.abs(alternating.data))
        if scale <= 1e-10:
            raise ValueError("The spinor pair is dependent or numerically unresolved")
        alternating = alternating / scale
        vector = grade(alternating, 1)
        phase_vector = grade(alternating, 5) * I
        a = -float(scalar_product(vector, ni))
        b = -float(scalar_product(phase_vector, ni))
        if a * a + b * b <= 1e-20:
            raise ValueError("This pair cannot select a finite event")
        event = (a * vector + b * phase_vector) / (a * a + b * b)
        zero = spin_algebra.scalar(0)
        if not all(value.almost_equal(zero) for value in (event * event, event * psi, event * phi)):
            raise ValueError("The pair does not describe a shared real event")
        return event

    return event_connector, event_from_twistors


@app.cell
def _(
    I,
    emission_coordinates,
    emission_event,
    event_connector,
    event_from_twistors,
    gm,
    grade,
    ni,
    np,
    scalar_product,
    spin_model,
    twistor_frame,
    twistor_pairing,
):
    event_translator = 1 - spin_model.spacetime_vector(emission_coordinates) * ni / 2
    first_incident = event_translator * twistor_frame[2]
    second_incident = event_translator * twistor_frame[3]
    event_bilinear = first_incident * event_connector * ~second_incident - second_incident * event_connector * ~first_incident
    event_vector = grade(event_bilinear, 1)
    recovered_event = event_vector / -float(scalar_product(event_vector, ni))
    phase_bilinear = (I * first_incident) * event_connector * ~second_incident - second_incident * event_connector * ~(I * first_incident)
    phase_recovered_event = event_from_twistors(I * first_incident, second_incident)
    rescaled_recovered_event = event_from_twistors(I * first_incident, (2 + 3 * I) * second_incident)
    mutual_pairing = twistor_pairing(first_incident, second_incident)
    gm.md(t"""
    The alternating product computed from the two translated spinors is

    {gm.block_latex(event_bilinear)}

    | Check | Result |
    |---|---|
    | Bilinear plus the original event, residual | {np.max(np.abs((event_bilinear + emission_event).data)):.2g} |
    | Recovered event coordinates | {spin_model.coordinates(recovered_event)} |
    | Recovered event minus the original event, residual | {np.max(np.abs((recovered_event - emission_event).data)):.2g} |
    | Recovered event squared, residual | {np.max(np.abs((recovered_event * recovered_event).data)):.2g} |
    | Recovered event × first spinor, residual | {np.max(np.abs((recovered_event * first_incident).data)):.2g} |
    | Recovered event × second spinor, residual | {np.max(np.abs((recovered_event * second_incident).data)):.2g} |
    | Mutual pairing of the two incident twistors | {abs(mutual_pairing):.2g} |
    | Grade-1 part after multiplying the first spinor by I, residual | {np.max(np.abs(grade(phase_bilinear, 1).data)):.2g} |
    | Event recovery from that pure grade-5 phase, residual | {np.max(np.abs((phase_recovered_event - emission_event).data)):.2g} |
    | Event recovery after independent complex rescaling, residual | {np.max(np.abs((rescaled_recovered_event - emission_event).data)):.2g} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Spinors transform on one side; events transform on two

    For a conformal rotor $R$ with $R\widetilde R=1$,

    $$
    \psi'=R\psi,\qquad X'=RX\widetilde R,\qquad
    X'\psi'=R(X\psi)=0.
    $$

    The pairing is preserved too. For its real part,

    $$
    b(R\psi,R\phi)=
    4\left\langle\widetilde\psi\,\widetilde R R\,\phi C\right\rangle_0
    =b(\psi,\phi).
    $$

    Because $I$ commutes with even $R$, the imaginary part follows.
    In matrix language this is $M(R)^\dagger H M(R)=H$.
    Connected conformal rotors give determinant-one matrices: this is the
    $SU(2,2)$ twistor representation of $\operatorname{Spin}^{+}(2,4)$.
    These are indefinite-unitary matrices, not generally unitary for the
    positive-definite Euclidean column norm.
    """)
    return


@app.cell
def _(boost_plane, exp, g1, g2, ni, no, null_plane):
    spin_transformations = (
        ("Boost", exp(0.3 * boost_plane)),
        ("Spatial rotation", exp(0.2 * g1 * g2)),
        ("Translation", exp(-0.1 * g2 * ni / 2)),
        ("Dilation", exp(0.1 * null_plane / 2)),
        ("Special conformal", exp(-0.1 * g2 * no / 2)),
    )
    return (spin_transformations,)


@app.cell
def _(
    emission_event,
    gm,
    np,
    ray_spinor,
    spin_action,
    spin_model,
    spin_transformations,
    twistor_metric,
    twistor_pairing,
):
    transformation_rows = []
    for transformation_name, rotor in spin_transformations:
        transformed_event = rotor * emission_event * ~rotor
        transformed_spinor = rotor * ray_spinor
        action = spin_action(rotor)
        incidence_error = np.max(np.abs((transformed_event * transformed_spinor).data))
        pairing_error = abs(
            twistor_pairing(transformed_spinor, transformed_spinor) - twistor_pairing(ray_spinor, ray_spinor)
        )
        metric_error = np.max(np.abs(action.conj().T @ twistor_metric @ action - twistor_metric))
        determinant_error = abs(np.linalg.det(action) - 1)
        transformation_rows.append(
            f"| {transformation_name} | {spin_model.classify_operator(rotor).transformation} "
            f"| {incidence_error:.2g} | {pairing_error:.2g} | {metric_error:.2g} | {determinant_error:.2g} |"
        )
    gm.md(t"""
    | Construction | Operator classifier | Incidence residual | Pairing residual | Matrix metric residual | det − 1 residual |
    |---|---|---:|---:|---:|---:|
    {"\n".join(transformation_rows)}
    """)
    return


@app.cell
def _(mo):
    spin_rapidity = mo.ui.slider(-1.5, 1.5, step=0.1, value=0.6, label="Boost rapidity")
    return (spin_rapidity,)


@app.cell
def _(
    MatrixRepr,
    boost_plane,
    emission_event,
    exp,
    gm,
    mo,
    ray_spinor,
    spin_action,
    spin_model,
    spin_rapidity,
    twistor_column_view,
    twistor_coordinates,
):
    chosen_boost = exp(spin_rapidity.value * boost_plane / 2)
    boosted_spinor = chosen_boost * ray_spinor
    boosted_event = chosen_boost * emission_event * ~chosen_boost

    mo.vstack([spin_rapidity,
    gm.md(t"""
    The boost acts on the spinor column through

    {gm.block_latex(MatrixRepr(spin_action(chosen_boost)))}

    giving

    {gm.block_latex(twistor_column_view(twistor_coordinates(boosted_spinor)))}

    The transformed emission event has coordinates **{spin_model.coordinates(boosted_event)}**.
    """)])
    return (chosen_boost,)


@app.cell
def _(chosen_boost, emission_event, ga, gm, ray_spinor):
    lesson_rotor = chosen_boost.with_expr().named("R")
    lesson_spinor = ray_spinor.with_expr().named("psi", latex=r"\psi")
    lesson_event = emission_event.with_expr().named("X")
    spinor_action_view = ga.annotate(
        lesson_rotor * lesson_spinor,
        ga.on(ga.variable("R"), background="#e8f0ff", label="rotor", marker="rule"),
        ga.on(ga.variable("psi"), label="spinor", marker="rule"),
    )
    event_action_view = ga.annotate(
        lesson_rotor * lesson_event * ~lesson_rotor,
        ga.on(ga.variable("R"), background="#e8f0ff", label="rotor", marker="rule"),
        ga.on(ga.variable("X"), label="event", marker="rule"),
        ga.on(ga.subexpression(~lesson_rotor), background="#e8f0ff", label="reverse\nrotor", marker="rule"),
    )
    gm.md(t"""
    **Single-sided spinor action**

    {gm.block_latex(spinor_action_view.latex(content="expr"))}

    **Event sandwich**

    {gm.block_latex(event_action_view.latex(content="expr"))}

    The shaded rotor factors show the difference in the actions.
    These annotations decorate the expressions; their numerical values
    are the boosted spinor and event computed above.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. The double cover, and what “the same twistor” means

    A spatial rotation through $\theta$ uses
    $R(\theta)=\exp(\frac12\theta\,\gamma_1\gamma_2)$.
    At $2\pi$, $R=-1$: the spinor changes sign, while the event is unchanged.
    At $4\pi$ the spinor itself returns.

    However, $\psi$ and $-\psi$ are the same **projective twistor**, so the
    light ray is already unchanged at $2\pi$. Keep the distinction between
    a spinor representative, its projective class, and a geometric blade.
    """)
    return


@app.cell
def _(emission_event, exp, g1, g2, gm, np, ray_spinor):
    rotation_2pi = exp(np.pi * g1 * g2)
    rotation_4pi = exp(2 * np.pi * g1 * g2)
    gm.md(t"""
    | Check | Maximum residual |
    |---|---:|
    | 2π rotation gives the negative spinor | {np.max(np.abs((rotation_2pi * ray_spinor + ray_spinor).data)):.2g} |
    | 2π sandwich leaves the event unchanged | {np.max(np.abs((rotation_2pi * emission_event * ~rotation_2pi - emission_event).data)):.2g} |
    | 4π rotation returns the spinor | {np.max(np.abs((rotation_4pi * ray_spinor - ray_spinor).data)):.2g} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Using this in your own experiments

    The helpers in this notebook are deliberately frame-specific:

    | Helper | Meaning |
    |---|---|
    | `twistor(z)` | Encode four complex coordinates as an even-ideal multivector |
    | `twistor_coordinates(psi)` | Decode a member of that ideal |
    | `twistor_pairing(psi, phi)` | Compute the geometric Hermitian pairing |
    | `twistor_kind(psi)` | Zero, null, positive or negative in this pairing |
    | `incident_twistor(q, pi)` | Construct a twistor incident to a real finite event |
    | `finite_light_ray(psi)` | Recover an anchor and future-directed null tangent |
    | `event_from_twistors(psi, phi)` | Recover a shared finite real event using an alternating geometric product |
    | `spin_action(R)` | Matrix of left multiplication in this frame |

    An arbitrary even CSTA multivector has 32 real coefficients, whereas a
    twistor has 8. Encoding a whole even multivector into one twistor column
    therefore cannot be a faithful roundtrip. The column conversions here
    are bijective **on the chosen ideal**.

    The displayed `MatrixRepr` objects wrap arrays in our explicit frame.
    They are unbound: their `.mv` is not a conversion back to this spinor
    representation. Use the notebook helpers for those conversions.

    Numerical rank and near-null decisions use float64 tolerances. Near
    singular incidence may need better conditioning or higher precision.
    All events here are finite and real; complex spacetime incidence and
    the full conformal boundary need additional constructions.

    ### References

    - [Tim Adamo, *Lectures on twistor theory*, sections 1.4–2.1](https://arxiv.org/html/1712.02196v2):
      projective incidence, Lorentzian reality and the signature $(2,2)$ pairing.
    - [R. da Rocha and J. Vaz, *Revisiting Clifford algebras and spinors III*](https://arxiv.org/abs/math-ph/0412076):
      Clifford-algebra constructions of conformal spinors and twistors.

    The representation boundary is recorded in
    [ADR-176](../../docs/adrs/176-csta-object-and-operator-classification.md).
    """)
    return


if __name__ == "__main__":
    app.run()
