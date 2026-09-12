import marimo

__generated_with = "0.24.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_matrix import MatrixRepr, from_matrix, to_matrix

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        exp,
        grade,
        inverse,
        p_cga,
        scalar_product,
        squared,
    )
    from galaga.cga import ConformalModel

    return (
        Algebra,
        ConformalModel,
        DisplayPolicy,
        MatrixRepr,
        exp,
        from_matrix,
        gm,
        grade,
        inverse,
        mo,
        np,
        p_cga,
        scalar_product,
        squared,
        to_matrix,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CGA objects as complex matrices and quaternion matrices

    A point, a point pair, and a rotor all live in the same conformal algebra,
    but they occupy different grades. We will inspect their matrix images and
    use that difference to understand the scope of quaternion representations.

    Three-dimensional CGA has **32 real coefficients**. Its full compact
    representation is **$4\times4$ complex**. Its left-regular representation
    is **$32\times32$ real**, acting on those 32 coefficients; those real
    entries can equally be used in complex arithmetic.

    A single **$2\times2$ quaternion** matrix holds only **16 real coefficients**.
    It represents the even subalgebra, which contains bivectors and rotors.
    General native CGA-to-quaternion conversion is not implemented yet. The
    quaternion examples below explicitly build an even-algebra coordinate map
    using today's public APIs, then show why a mixed-grade value needs a pair.
    """)
    return


@app.cell
def _():
    null_pair_scale = -1.0
    return (null_pair_scale,)


@app.cell
def _(
    Algebra,
    ConformalModel,
    DisplayPolicy,
    MatrixRepr,
    null_pair_scale,
    p_cga,
):
    cga_algebra = Algebra(
        config=p_cga(3, frame="null", null_pair=null_pair_scale),
        display=DisplayPolicy(content="full"),
    )
    cga = ConformalModel(cga_algebra, expr=True)
    e1, e2, e3 = cga.euclidean_basis_vectors()
    eo, einf = cga.origin, cga.infinity
    gram_matrix = MatrixRepr(cga_algebra.gram).name(latex=r"G")
    return cga, cga_algebra, e1, e2, e3, einf, eo, gram_matrix


@app.cell
def _(cga_algebra, gm, gram_matrix):
    _inertia = cga_algebra.inertia
    gm.md(rt"""
    ## Start with the metric

    {gram_matrix:block}

    The native order is $(e_o,e_1,e_2,e_3,e_\infty)$, with inertia
    `{_inertia!s}`. The off-diagonal null-pair entry makes the metric
    nondegenerate. Try changing `null_pair_scale` to another negative value:
    the normalizations and coordinate maps below are derived from the algebra.
    """)
    return


@app.cell
def _(cga, e1, e2, einf, eo, exp, scalar_product):
    point_p = cga.up((1.0, 0.0, 0.0)).named("P")
    point_q = cga.up((0.0, 1.0, 0.0)).named("Q")
    point_r = cga.up((-1.0, 0.0, 0.0)).named("R")
    point_s = cga.up((0.0, 0.0, 1.0)).named("S")
    point_pair = (point_p ^ point_q).named("D")
    line = (point_p ^ point_q ^ einf).named("L")
    circle = (point_p ^ point_q ^ point_r).named("C")
    sphere = (point_p ^ point_q ^ point_r ^ point_s).named("Sigma", latex=r"\Sigma")
    plane = (point_p ^ point_q ^ point_r ^ einf).named("Pi", latex=r"\Pi")
    dual_sphere = cga.dual(sphere).named("s")

    spatial_bivector = (e1 ^ e2).named("B")
    rotation = exp(-0.35 * spatial_bivector).named("R_rot", latex=r"R_{\mathrm{rot}}")
    displacement = cga.euclidean_vector((0.5, -1.0, 0.25)).named("d")
    _null_pair = float(scalar_product(eo, einf))
    translation = exp(displacement * einf / (2.0 * _null_pair)).named("T")
    motor = (translation * rotation).named("M")
    mixed_value = (rotation + point_p).named("A")

    samples = {
        "Euclidean vector": (e1, "A spatial vector has grade 1 and positive square."),
        "Null origin": (eo, "The origin is a nonzero null vector."),
        "Infinity": (einf, "Infinity is the other member of the native null pair."),
        "Lifted point": (point_p, "The Euclidean point (1, 0, 0) lifts to a null grade-1 vector P."),
        "Point pair": (point_pair, "P wedge Q is a grade-2 blade: two lifted points already give an even object."),
        "Line through two points": (line, "P wedge Q wedge infinity is a grade-3 direct (OPNS) line."),
        "Circle through three points": (circle, "P wedge Q wedge R is a grade-3 direct (OPNS) circle."),
        "Sphere through four points": (sphere, "Four lifted points give a grade-4 direct (OPNS) sphere."),
        "Plane through three points": (plane, "Three lifted points and infinity give a grade-4 direct plane."),
        "Dual sphere": (dual_sphere, "Dualizing the direct sphere produces a grade-1 vector for the same surface."),
        "Spatial bivector": (spatial_bivector, "This grade-2 plane blade generates spatial rotations."),
        "Rotation rotor": (rotation, "Exponentiating the bivector produces a mixture of grades 0 and 2."),
        "Translation rotor": (translation, "The translation generator uses the computed null-pair normalization."),
        "Composed motor": (motor, "Translation times rotation is even and can also contain grade 4."),
        "Mixed rotor plus point": (
            mixed_value,
            "A rotor plus a point contains both even and odd grades; it is not a versor.",
        ),
    }
    quaternion_examples = {
        "Spatial bivector": spatial_bivector,
        "Rotation rotor": rotation,
        "Translation rotor": translation,
        "Composed motor": motor,
    }
    return mixed_value, quaternion_examples, samples


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Explore the full complex representation

    Start with the lifted point. Its matrix is nonzero but its square vanishes,
    just as $P^2=0$. Then compare a point pair, a circle, and a rotor. A small
    matrix does not imply a low-grade multivector: all grades share the same
    $4\times4$ matrix space.

    The expandable left-regular matrix shows the same object acting by left
    multiplication on the full coefficient space. It is larger, but both
    representations recover the original native coefficients.
    """)
    return


@app.cell
def _(mo, samples):
    object_selector = mo.ui.dropdown(
        options=list(samples),
        value="Lifted point",
        label="CGA object",
    )
    object_selector
    return (object_selector,)


@app.cell
def _(
    from_matrix,
    gm,
    grade,
    mo,
    np,
    object_selector,
    samples,
    squared,
    to_matrix,
):
    _value, _description = samples[object_selector.value]
    _grades = tuple(_g for _g in range(_value.algebra.n + 1) if np.any(np.abs(grade(_value, _g).data) > 1e-12))
    _complex = to_matrix(_value, mode="compact")
    _regular = to_matrix(_value, mode="left-regular")
    _square = squared(_value)
    _matrix_square = _complex @ _complex
    _compact_error = float(np.max(np.abs(from_matrix(_complex).data - _value.data)))
    _regular_error = float(np.max(np.abs(from_matrix(_regular).data - _value.data)))
    mo.vstack(
        [
            gm.md(rt"""
        {_description!s} Present grades: `{_grades!s}`.

        {_value:block}
        """),
            mo.hstack(
                [
                    gm.md(rt"""**Compact complex image**

            {_complex:block}
            """),
                    gm.md(rt"""**Square of that matrix**

            {_matrix_square:block}
            """),
                ]
            ),
            gm.md(rt"""
        The algebra computes {_square:block}

        Maximum coefficient recovery errors: compact `{_compact_error:.3e}`;
        left-regular `{_regular_error:.3e}`.
        """),
            mo.accordion(
                {
                    "Expand the 32×32 left-regular matrix": gm.md(t"""{_regular:block}"""),
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A few quaternion examples, with an explicit coordinate map

    The even conformal algebra is isomorphic to
    $\operatorname{Cl}(1,3)\cong M_2(\mathbb H)$. We can demonstrate this using
    the existing quaternion mode for an auxiliary $\operatorname{Cl}(1,3)$
    algebra. This is a notebook construction: `to_matrix` does not yet perform
    this native CGA conversion for us.

    Normalize $e_o-e_\infty$ and $e_o+e_\infty$ using their **computed** squares,
    calling the results $u$ and $v$. Then use the even generators

    $$
    h_0=uv,\qquad h_k=ue_k\quad(k=1,2,3).
    $$

    Their measured squares determine the auxiliary signature. Products of the
    $h$ generators give a coordinate map from its 16 blades into the native CGA
    even subspace. We solve for those coordinates before using quaternion mode.
    """)
    return


@app.cell
def _(
    Algebra,
    MatrixRepr,
    cga_algebra,
    e1,
    e2,
    e3,
    einf,
    eo,
    np,
    scalar_product,
    squared,
):
    _u_raw, _v_raw = eo - einf, eo + einf
    _u = _u_raw / np.sqrt(float(squared(_u_raw)))
    _v = _v_raw / np.sqrt(-float(squared(_v_raw)))
    even_generators = (_u * _v, _u * e1, _u * e2, _u * e3)
    measured_even_gram = np.array(
        [[float(scalar_product(_left, _right)) for _right in even_generators] for _left in even_generators]
    )
    _signature = tuple(int(np.sign(float(squared(_generator)))) for _generator in even_generators)
    auxiliary_algebra = Algebra(signature=_signature)
    even_gram_matrix = MatrixRepr(measured_even_gram).name(latex=r"G_h")
    _columns = []
    for _mask in range(auxiliary_algebra.dim):
        _blade = cga_algebra.identity
        for _index, _generator in enumerate(even_generators):
            if _mask & (1 << _index):
                _blade = _blade * _generator
        _columns.append(_blade.data)
    even_frame = np.column_stack(_columns)
    return auxiliary_algebra, even_frame, even_gram_matrix


@app.cell
def _(auxiliary_algebra, cga_algebra, even_frame, from_matrix, np, to_matrix):
    def quaternion_image(value):
        """Map a native even value through the notebook's auxiliary algebra."""
        _odd_masks = [mask for mask in range(cga_algebra.dim) if mask.bit_count() % 2]
        if np.any(np.abs(value.data[_odd_masks]) > 1e-12):
            raise ValueError("A single quaternion matrix here requires an even CGA value.")
        _coefficients, _, _, _ = np.linalg.lstsq(even_frame, value.data, rcond=None)
        _auxiliary = auxiliary_algebra.multivector(_coefficients)
        return to_matrix(_auxiliary, mode="quaternion")

    def native_from_quaternion(matrix):
        """Return to CGA after the existing inverse recovers auxiliary coordinates."""
        _auxiliary = from_matrix(matrix)
        return cga_algebra.multivector(even_frame @ _auxiliary.data)

    return native_from_quaternion, quaternion_image


@app.cell
def _(even_frame, even_gram_matrix, gm, np):
    _rank = int(np.linalg.matrix_rank(even_frame))
    gm.md(rt"""
    The computed generator metric is

    {even_gram_matrix:block}

    The coordinate map has rank `{_rank!s}`, covering the entire even subspace.
    We use the signs of the measured unit squares to construct the auxiliary
    normalized signature; this avoids treating roundoff such as $1-10^{{-16}}$
    as a deliberately scaled metric.

    Each quaternion matrix below retains the **auxiliary algebra** as its
    provenance. To recover the original CGA value, `native_from_quaternion`
    explicitly maps those coordinates back. The two displayed representations
    use different matrix bases, so their complex backing arrays need not match
    entry for entry.
    """)
    return


@app.cell
def _(
    MatrixRepr,
    gm,
    mo,
    native_from_quaternion,
    np,
    quaternion_examples,
    quaternion_image,
    to_matrix,
):
    _panels = {}
    for _label, _value in quaternion_examples.items():
        _complex = to_matrix(_value, mode="compact")
        _quaternion = MatrixRepr(quaternion_image(_value)).name(latex=r"Q")
        _error = float(np.max(np.abs(native_from_quaternion(_quaternion).data - _value.data)))
        _panels[_label] = mo.vstack(
            [
                gm.md(t"""{_value:block}"""),
                mo.vstack(
                    [
                        gm.md(t"""**4×4 complex**

                {_complex:block}
                """),
                        gm.md(t"""**2×2 quaternion, via even coordinates**

                {_quaternion:block}
                """),
                    ]
                ),
                gm.md(t"""Maximum native coefficient recovery error: `{_error:.3e}`."""),
            ]
        )
    mo.accordion(_panels)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why a mixed-grade value needs two quaternion matrices

    Take $A=R_{\mathrm{rot}}+P$. Its rotor part is even and its point part is
    odd. Adding them is a valid algebra operation, although the result is not
    a geometric rotor or a point.

    The five-dimensional pseudoscalar commutes with every element and has
    negative square. Normalize it to $J^2=-1$, using the computed square.
    Multiplication by $J^{-1}$ converts odd values into even ones, so

    $$
    A=E+BJ,\qquad E=A_{\mathrm{even}},\qquad
    B=A_{\mathrm{odd}}J^{-1}.
    $$

    Both $E$ and $B$ can be mapped to quaternion matrices. **Keep both matrices
    and the factor $J$**: dropping that factor changes the element and its
    multiplication law. $J$ is a central imaginary unit, distinct from the
    noncommuting quaternion units $i,j,k$.
    """)
    return


@app.cell
def _(
    cga_algebra,
    grade,
    inverse,
    native_from_quaternion,
    np,
    quaternion_image,
    squared,
):
    _pseudoscalar = cga_algebra.blade(cga_algebra.dim - 1)
    central_unit = _pseudoscalar / np.sqrt(-float(squared(_pseudoscalar)))
    _central_inverse = inverse(central_unit)

    def quaternion_pair(value):
        """Teaching encoding A = E + B J; not a native matrix-package API."""
        _even = sum(
            (grade(value, g) for g in range(0, cga_algebra.n + 1, 2)),
            cga_algebra.scalar(0),
        )
        _odd_factor = (value - _even) * _central_inverse
        return quaternion_image(_even), quaternion_image(_odd_factor)

    def native_from_pair(pair):
        _even, _odd_factor = pair
        return native_from_quaternion(_even) + native_from_quaternion(_odd_factor) * central_unit

    return central_unit, native_from_pair, quaternion_pair


@app.cell
def _(
    MatrixRepr,
    central_unit,
    gm,
    mixed_value,
    mo,
    native_from_pair,
    np,
    quaternion_pair,
    squared,
    to_matrix,
):
    _even_q, _odd_q = quaternion_pair(mixed_value)
    _even_q = MatrixRepr(_even_q).name(latex=r"Q(E)")
    _odd_q = MatrixRepr(_odd_q).name(latex=r"Q(B)")
    _complex = to_matrix(mixed_value, mode="compact")
    _unit_square = float(squared(central_unit))
    _recovered = native_from_pair((_even_q, _odd_q))
    _error = float(np.max(np.abs(_recovered.data - mixed_value.data)))
    mo.vstack(
        [
            gm.md(rt"""
        {mixed_value:block}

        The computed normalization gives $J^2={_unit_square:g}$. The full
        complex representation still needs only one matrix:

        {_complex:block}

        The quaternion encoding needs these two matrices, representing $E+BJ$:
        """),
            mo.hstack(
                [
                    gm.md(t"""{_even_q:block}"""),
                    gm.md(t"""{_odd_q:block}"""),
                ]
            ),
            gm.md(t"""Recombining them recovers all native coefficients with maximum
        error `{_error:.3e}`."""),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This pair also explains multiplication. If $A=E+BJ$ and $C=F+DJ$, then

    $$
    AC=(EF-BD)+(ED+BF)J.
    $$

    Quaternion matrix products must retain this order. Even values need only
    $Q(E)$; an odd value needs its $Q(B)$ **and** the information that it
    multiplies $J$. A general mixed value requires both.

    The notebook's explicit pair is a teaching construction, not a settled
    public quaternion API for full CGA. Native even-domain conversion,
    automatic provenance, and a general user-facing quaternion encoding remain
    work to do. For full CGA conversion today, use the compact complex form.

    Try selecting the point, the direct sphere, and the dual sphere above.
    They illustrate why the grades of an object—and the chosen direct or dual
    description—matter more than its geometric name when choosing a domain.
    """)
    return


if __name__ == "__main__":
    app.run()
