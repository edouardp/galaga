import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_matrix import MatrixRepr

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        exp,
        grade,
        inverse,
        is_even,
        is_rotor,
        is_rotor_generator,
        log,
        rotor_generator,
        sandwich,
    )

    return (
        Algebra,
        MatrixRepr,
        exp,
        gm,
        grade,
        inverse,
        is_even,
        is_rotor,
        is_rotor_generator,
        log,
        mo,
        np,
        rotor_generator,
        sandwich,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Exponentials, Logarithms, and Rotors

    Start with the generator, then compute its square. A simple bivector can
    generate a rotation, a boost, or a null transformation depending on the
    metric. An even multivector need not be a rotor.

    We will separate three questions: what does `exp` compute, when does
    reversion give an inverse, and when does an algebra logarithm also
    generate a path of rotors? `log` is the real principal algebra logarithm;
    `rotor_generator` is the intentionally geometric operation.
    Galaga 2 uses explicit exponentials; the old `Algebra.rotor` constructor
    and its plane-angle aliases are retired.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra(3)
    e1, e2, _e3 = alg.basis_vectors(expr=True)
    return alg, e1, e2


@app.cell
def _(mo):
    angle = mo.ui.slider(start=0, stop=180, step=1, value=55, label="rotation angle")
    mo.vstack([angle])
    return (angle,)


@app.cell
def _(angle, e1, e2, exp, gm, is_rotor, np, rotor_generator, sandwich):
    rotation_angle = np.deg2rad(angle.value)
    rotation_plane = e1 ^ e2
    assert rotation_plane * rotation_plane == -1
    rotation_rotor = exp(-rotation_angle * rotation_plane / 2)
    rotated_vector = sandwich(rotation_rotor, e1)
    recovered_generator = rotor_generator(rotation_rotor)
    assert is_rotor(rotation_rotor)
    np.testing.assert_allclose(
        rotated_vector.data,
        (np.cos(rotation_angle) * e1 + np.sin(rotation_angle) * e2).data,
        rtol=0,
        atol=1e-12,
    )
    gm.md(rt"""
    ## 1. An oriented Euclidean plane

    Convert degrees explicitly: $\theta={rotation_angle}$ radians.
    Here $B=e_1\wedge e_2$ and $B^2={rotation_plane * rotation_plane}$, so
    $R=\exp(-\theta B/2)$ rotates $e_1$ toward $e_2$.

    $$R={rotation_rotor},\qquad R e_1\widetilde R={rotated_vector}.$$

    Here `rotor_generator(R)` checks that the principal logarithm is a
    geometric generator. On this supported branch,
    $$\log R={recovered_generator}.$$

    The half-angle and minus sign belong to this oriented sandwich convention.
    `exp` does not silently normalize its input: replacing $B$ by $3B$
    triples the rotation angle.
    """)
    return recovered_generator, rotated_vector, rotation_angle, rotation_plane, rotation_rotor


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Let the Gram matrix choose the branch

    For `B = e1 ^ e2`, compute
    $$B^2=G_{12}^2-G_{11}G_{22}.$$
    With negative square, divide by $\sqrt{-B^2}$ to obtain a unit
    elliptic plane; the parameter is an angle. With positive square,
    divide by $\sqrt{B^2}$ and interpret the parameter as rapidity.
    Zero square has no such normalization: keep the original generator and
    its scale, and use the terminating exponential $\exp(tB)=1+tB$.

    The four examples below use parameter $0.6$. Each checks
    $R\widetilde R=1$. The oblique basis need not be orthonormal,
    so its coordinate formula is not simply the Euclidean sine/cosine pair.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, exp, gm, is_rotor, log, mo, np, sandwich):
    metric_examples = []
    _outputs = []
    for _label, _gram in (
        ("Euclidean rotation", ((1, 0), (0, 1))),
        ("Oblique elliptic plane", ((2, 0.5), (0.5, 1))),
        ("Boost: angle becomes rapidity", ((2, 0.5), (0.5, -1))),
        ("Null plane: keep the generator scale", ((1, 1), (1, 1))),
    ):
        _algebra = Algebra(gram=_gram)
        _a, _b = _algebra.basis_vectors(expr=True)
        _plane = _a ^ _b
        _square = float(_plane * _plane)
        _generator = _plane / np.sqrt(abs(_square)) if _square else _plane
        _rotor = exp(-0.3 * _generator)
        _result = sandwich(_rotor, _a)
        _reverse_product = _rotor * ~_rotor
        _logarithm = log(_rotor)
        assert is_rotor(_rotor)
        np.testing.assert_allclose(_reverse_product.data, _algebra.identity.data, rtol=0, atol=1e-12)
        np.testing.assert_allclose(_logarithm.data, (-0.3 * _generator).data, rtol=0, atol=1e-12)
        _matrix = MatrixRepr(_algebra.gram).name(latex="G")
        metric_examples.append(
            {
                "label": _label,
                "gram": _matrix,
                "plane": _plane,
                "square": _square,
                "generator": _generator,
                "rotor": _rotor,
                "result": _result,
                "logarithm": _logarithm,
            }
        )
        _outputs.append(
            gm.md(rt"""
        ### {_label!s}

        $${_matrix},\qquad B^2={_square},\qquad N={_generator}.$$
        $$R=\exp(-0.3N)={_rotor},\qquad R\widetilde R={_reverse_product}.$$
        $$R e_1\widetilde R={_result},\qquad \log R={_logarithm}.$$
        """)
        )
    mo.vstack(_outputs)
    return (metric_examples,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Two planes need the grade-four term

    In Euclidean four-space the disjoint planes $B_1=e_1\wedge e_2$ and
    $B_2=e_3\wedge e_4$ commute. Therefore
    $$\exp(t(B_1+B_2))=\exp(tB_1)\exp(tB_2).$$
    Multiplying the two exponentials creates a grade-four term. A single
    cosine-plus-bivector formula discards it and generally fails
    $R\widetilde R=1$. The old helper could miss this by checking only the
    scalar part of the reverse product.

    Below, $S$ reproduces the old helper, including its scalar-norm
    normalization. That also changes the generator scale. The decisive
    failure is its nonunit reverse product, not its difference from $R$.

    `exp` supports this compound generator, and the mathematical `log`
    now recovers it on this principal branch. The general logarithm uses
    the native left action without discarding the higher-grade terms.
    `rotor_generator` additionally verifies the geometric generator contract.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, exp, gm, grade, is_rotor, log, np, rotor_generator):
    compound_algebra = Algebra(4)
    _a, _b, _c, _d = compound_algebra.basis_vectors(expr=True)
    _first, _second = _a ^ _b, _c ^ _d
    compound_generator = _first + _second
    assert _first * _second == _second * _first
    compound_rotor = exp(-0.25 * compound_generator)
    compound_factored = exp(-0.25 * _first) * exp(-0.25 * _second)
    compound_logarithm = log(compound_rotor)
    compound_recovered = rotor_generator(compound_rotor)
    compound_grade_four = grade(compound_rotor, 4)
    _scalar_norm = float(grade(compound_generator * ~compound_generator, 0))
    incomplete_rotor = np.cos(0.25) - np.sin(0.25) * compound_generator / np.sqrt(_scalar_norm)
    incomplete_reverse_product = incomplete_rotor * ~incomplete_rotor
    assert is_rotor(compound_rotor) and not is_rotor(incomplete_rotor)
    np.testing.assert_allclose(compound_rotor.data, compound_factored.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(compound_recovered.data, (-0.25 * compound_generator).data, rtol=0, atol=1e-12)
    _gram = MatrixRepr(compound_algebra.gram).name(latex="G")
    gm.md(rt"""
    $${_gram}.$$
    $$B^2={compound_generator * compound_generator}.$$
    The full exponential and its grade-four part are
    $$R={compound_rotor},\qquad \langle R\rangle_4={compound_grade_four}.$$
    The full algebra logarithm recovers both plane contributions:
    $$\log R={compound_logarithm}.$$
    The incomplete trigonometric recipe gives
    $$S={incomplete_rotor},\qquad S\widetilde S={incomplete_reverse_product}.$$
    The nonzero grade-four residual means this $S$ is not unit under reversion.
    """)
    return (
        compound_factored,
        compound_generator,
        compound_grade_four,
        compound_logarithm,
        compound_recovered,
        compound_rotor,
        incomplete_reverse_product,
        incomplete_rotor,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. An even phase is not automatically a rotor

    In spacetime with signature $(+---)$, the pseudoscalar satisfies
    $I^2=-1$ but $\widetilde I=I$. Thus $P=\exp(-I/4)$ has grades
    zero and four, while $P\widetilde P=P^2\ne1$.

    Its reverse sandwich happens to fix vectors because $I$ anticommutes
    with them. This is not evidence that $P$ is a rotor: other grades change.
    Inverse conjugation is different and mixes vector and trivector grades.
    `sandwich` (also `sw`) always uses reverse, without substituting an inverse.

    The public `is_rotor` predicate checks three conditions: evenness,
    the **whole** reverse product against one, and preservation of vectors
    under the reverse sandwich. Each check uses an absolute coefficient
    tolerance in the stored basis. The next example shows why the third
    condition is needed as well as the first two.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, exp, gm, inverse, is_even, is_rotor, np, sandwich):
    phase_algebra = Algebra((1, -1, -1, -1))
    phase_volume = phase_algebra.pseudoscalar(expr=True)
    _vector = phase_algebra.blade(1, expr=True)
    assert phase_volume * phase_volume == -1 and ~phase_volume == phase_volume
    sta_phase = exp(-0.25 * phase_volume)
    phase_reverse_product = sta_phase * ~sta_phase
    phase_sandwich = sandwich(sta_phase, _vector)
    phase_conjugated = sta_phase * _vector * inverse(sta_phase)
    assert is_even(sta_phase) and not is_rotor(sta_phase)
    np.testing.assert_allclose(phase_sandwich.data, _vector.data, rtol=0, atol=1e-12)
    _gram = MatrixRepr(phase_algebra.gram).name(latex="G")
    gm.md(rt"""
    $${_gram},\qquad I^2={phase_volume * phase_volume},\qquad \widetilde I={~phase_volume}.$$
    $$P={sta_phase},\qquad P\widetilde P={phase_reverse_product}.$$
    $$P e_1\widetilde P={phase_sandwich},\qquad P e_1 P^{-1}={phase_conjugated}.$$
    Even: **{is_even(sta_phase)}**. Passes `is_rotor`: **{is_rotor(sta_phase)}**.
    """)
    return phase_conjugated, phase_reverse_product, phase_sandwich, phase_volume, sta_phase


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Unit and even still need not mean rotor

    In six-dimensional Euclidean algebra, let $I=e_{123456}$.
    This time $I^2=-1$ **and** $\widetilde I=-I$. Therefore
    $U=(1+I)/\sqrt{2}$ is even and satisfies $U\widetilde U=1$.
    Nevertheless, $Ue_1\widetilde U=Ie_1$ has grade five, not grade one.
    `is_rotor(U)` correctly returns `False`, while `log(U)` is valid:
    $U=\exp(\pi I/4)$, so $\pi I/4$ is its real principal logarithm,
    just not a geometric rotation generator. `rotor_generator(U)` rejects
    the nonrotor input. The sandwich calculation itself remains well defined.

    Checking every native basis vector suffices by linearity. Do not instead
    ban higher even grades: genuine compound rotors can contain grades four
    and six. It is their **action on vectors** that matters.

    The default tolerance is `atol=1e-12`, with no relative tolerance.
    It bounds individual residual coefficients in the stored basis, not a
    basis-independent geometric error. Large boosts or poorly conditioned
    Gram matrices may need a larger, explicitly chosen tolerance. Here the
    grade-five error has magnitude one; it is not floating-point noise.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, gm, grade, is_even, is_rotor, log, np, sandwich):
    _algebra = Algebra(6)
    _volume = _algebra.pseudoscalar(expr=True)
    _vector = _algebra.blade(1, expr=True)
    _reverse_sign = (-1) ** (_algebra.n * (_algebra.n - 1) // 2)
    _square = _reverse_sign * np.linalg.det(_algebra.gram)
    assert _volume * _volume == _square and ~_volume == _reverse_sign * _volume
    unit_even_candidate = (1 + _volume) / np.sqrt(2)
    unit_even_logarithm = log(unit_even_candidate)
    unit_even_reverse_product = unit_even_candidate * ~unit_even_candidate
    unit_even_image = sandwich(unit_even_candidate, _vector)
    np.testing.assert_allclose(unit_even_reverse_product.data, _algebra.identity.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(unit_even_image.data, (_volume * _vector).data, rtol=0, atol=1e-12)
    assert np.linalg.norm(grade(unit_even_image, 5).data) > 0.9
    assert is_even(unit_even_candidate) and not is_rotor(unit_even_candidate)
    _gram = MatrixRepr(_algebra.gram).name(latex="G")
    gm.md(rt"""
    $${_gram},\qquad I^2={_volume * _volume},\qquad \widetilde I={~_volume}.$$
    $$U={unit_even_candidate},\qquad U\widetilde U={unit_even_reverse_product}.$$
    $$\log U={unit_even_logarithm}.$$
    $$Ue_1\widetilde U={unit_even_image}.$$
    Even: **{is_even(unit_even_candidate)}**. Passes `is_rotor`: **{is_rotor(unit_even_candidate)}**.
    The grade-five image makes this a unit even nonrotor.
    """)
    return unit_even_candidate, unit_even_image, unit_even_logarithm, unit_even_reverse_product


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. An algebra logarithm is not necessarily a rotor generator

    `log(A)` does not require evenness or unit norm: positive scalar $2$
    has logarithm $\ln 2$, and vector exponentials have vector logarithms
    on a suitable branch. Singular inputs have no finite logarithm. This
    real API selects the principal branch and rejects its spectral cut;
    it neither invents complex coefficients nor chooses an alternative plane.

    Even for a genuine rotor, the principal **algebra** logarithm need not
    generate a path of rotors. In six Euclidean dimensions $I$ is a rotor,
    and $\log I=\pi I/2$. But exponentiating half of that gives the
    nonrotor $U$ above. `is_rotor_generator(log(I))` detects the problem;
    `rotor_generator(I)` raises rather than silently discarding grade six.

    An alternative logarithm is the bivector
    $B=\pi(e_{12}+e_{34}+e_{56})/2$. Its exponential is also $I$, and
    its scaled exponentials are rotors. Finding such alternative branches
    automatically is not yet implemented by `rotor_generator`.

    The standalone predicate checks evenness, reverse skewness, and
    vector-valued commutators with every native basis vector. Checking
    only `is_rotor(exp(B))` would validate one endpoint, not the whole path.
    """)
    return


@app.cell
def _(Algebra, exp, gm, is_rotor, is_rotor_generator, log, np, rotor_generator):
    _algebra = Algebra(6)
    _volume = _algebra.pseudoscalar(expr=True)
    _planes = [_algebra.blade(_mask, expr=True) for _mask in (3, 12, 48)]
    assert all(_plane * _plane == -1 for _plane in _planes)
    assert _planes[0] * _planes[1] * _planes[2] == _volume
    assert is_rotor(_volume)
    volume_logarithm = log(_volume)
    algebra_half_step = exp(volume_logarithm / 2)
    alternative_generator = np.pi / 2 * sum(_planes)
    geometric_half_step = exp(alternative_generator / 2)
    np.testing.assert_allclose(exp(alternative_generator).data, _volume.data, rtol=0, atol=1e-12)
    assert not is_rotor_generator(volume_logarithm) and is_rotor_generator(alternative_generator)
    assert not is_rotor(algebra_half_step) and is_rotor(geometric_half_step)
    try:
        rotor_generator(_volume)
    except ValueError as _error:
        generator_branch_error = str(_error)
    else:
        raise AssertionError("the principal logarithm is not a geometric generator")
    _scalar_logarithm = log(_algebra.scalar(2))
    gm.md(rt"""
    $$\log 2={_scalar_logarithm},\qquad \log I={volume_logarithm}.$$
    The algebra half-step is
    $$\exp\left(\tfrac12\log I\right)={algebra_half_step}.$$
    The alternative generator and geometric half-step are
    $$B={alternative_generator},\qquad \exp(B/2)={geometric_half_step}.$$
    Is the algebra half-step a rotor? **{is_rotor(algebra_half_step)}**.
    Is the geometric half-step a rotor? **{is_rotor(geometric_half_step)}**.

    `rotor_generator(I)` reports: {generator_branch_error!s}.
    """)
    return algebra_half_step, alternative_generator, generator_branch_error, geometric_half_step, volume_logarithm


if __name__ == "__main__":
    app.run()
