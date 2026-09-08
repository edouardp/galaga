import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_matrix import MatrixRepr

    import galaga_marimo as gm
    from galaga import Algebra, exp, grade, inverse, is_even, is_rotor, log, sandwich

    return Algebra, MatrixRepr, exp, gm, grade, inverse, is_even, is_rotor, log, mo, np, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Exponentials, Logarithms, and Rotors

    Start with the generator, then compute its square. A simple bivector can
    generate a rotation, a boost, or a null transformation depending on the
    metric. An even multivector need not be a rotor.

    We will separate three questions: what does `exp` compute, when does
    reversion give an inverse, and when can `log` recover the generator?
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
def _(angle, e1, e2, exp, gm, is_rotor, log, np, sandwich):
    rotation_angle = np.deg2rad(angle.value)
    rotation_plane = e1 ^ e2
    assert rotation_plane * rotation_plane == -1
    rotation_rotor = exp(-rotation_angle * rotation_plane / 2)
    rotated_vector = sandwich(rotation_rotor, e1)
    recovered_generator = log(rotation_rotor)
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

    On this supported principal branch,
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

    Generic `exp` supports this compound generator. Generic `log` is more
    limited: its current real Study-number branch does not cover this
    nonsimple example, even though the exponential is a valid rotor.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, exp, gm, grade, is_rotor, np):
    compound_algebra = Algebra(4)
    _a, _b, _c, _d = compound_algebra.basis_vectors(expr=True)
    _first, _second = _a ^ _b, _c ^ _d
    compound_generator = _first + _second
    assert _first * _second == _second * _first
    compound_rotor = exp(-0.25 * compound_generator)
    compound_factored = exp(-0.25 * _first) * exp(-0.25 * _second)
    compound_grade_four = grade(compound_rotor, 4)
    _scalar_norm = float(grade(compound_generator * ~compound_generator, 0))
    incomplete_rotor = np.cos(0.25) - np.sin(0.25) * compound_generator / np.sqrt(_scalar_norm)
    incomplete_reverse_product = incomplete_rotor * ~incomplete_rotor
    assert is_rotor(compound_rotor) and not is_rotor(incomplete_rotor)
    np.testing.assert_allclose(compound_rotor.data, compound_factored.data, rtol=0, atol=1e-12)
    _gram = MatrixRepr(compound_algebra.gram).name(latex="G")
    gm.md(rt"""
    $${_gram}.$$
    $$B^2={compound_generator * compound_generator}.$$
    The full exponential and its grade-four part are
    $$R={compound_rotor},\qquad \langle R\rangle_4={compound_grade_four}.$$
    The incomplete trigonometric recipe gives
    $$S={incomplete_rotor},\qquad S\widetilde S={incomplete_reverse_product}.$$
    The nonzero grade-four residual means this $S$ is not unit under reversion.
    """)
    return (
        compound_factored,
        compound_generator,
        compound_grade_four,
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

    The public `is_rotor` predicate tests evenness and the **whole**
    reverse product against one with an absolute tolerance. It is not a
    general high-dimensional proof that every vector is mapped to a vector.
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


if __name__ == "__main__":
    app.run()
