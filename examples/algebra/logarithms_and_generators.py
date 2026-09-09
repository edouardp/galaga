import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


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
        is_rotor,
        is_rotor_generator,
        is_scalar,
        log,
        rotor_generator,
        sandwich,
        scalar_part,
    )

    return (
        Algebra,
        MatrixRepr,
        exp,
        gm,
        grade,
        is_rotor,
        is_rotor_generator,
        is_scalar,
        log,
        mo,
        np,
        rotor_generator,
        sandwich,
        scalar_part,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Logarithms and rotor generators

    A logarithm solves $\exp L=A$. A **rotor generator** must also keep
    $\exp(tL)$ inside the rotor group as the parameter $t$ varies.
    These are different questions, even when $A$ itself is a rotor.

    | Operation | Question it answers |
    | --- | --- |
    | `log(A)` | What is the real principal **algebra** logarithm? |
    | `rotor_generator(R)` | Is this rotor's principal logarithm a geometric generator? Return it if so. |
    | `is_rotor_generator(B)` | Does this candidate satisfy the infinitesimal rotor conditions? |

    This notebook starts with nonrotor logarithms, then explores compound
    inputs, nilpotents, branches, and two different paths to the same rotor.
    It complements `exp_log_rotors.py`, which introduces exponential recipes
    and the rotor predicate. All examples use the public Galaga 2 API.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Logarithms do not require rotors

    Start with the ordinary scalar identity $\log 2=\ln 2$. Supply a scalar
    **multivector**, so Galaga knows which algebra the result belongs to.
    `log(2)` alone does not specify that algebra.

    Odd grades are allowed too. In a positive one-dimensional metric,
    $v^2=1$ and $\exp(tv)=\cosh t+v\sinh t$. Multiplying by a positive
    scalar changes the logarithm's scalar part; it must not be normalized away.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, exp, gm, is_rotor, log, np):
    vector_algebra = Algebra(gram=[[1]])
    _v = vector_algebra.blade(1, expr=True)
    assert _v * _v == vector_algebra.gram[0, 0]
    scalar_input = vector_algebra.scalar(2, expr=True)
    scalar_logarithm = log(scalar_input)
    vector_input = 2 * exp(0.3 * _v)
    vector_logarithm = log(vector_input)
    vector_expected = np.log(2) + 0.3 * _v
    np.testing.assert_allclose(vector_logarithm.data, vector_expected.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(exp(vector_logarithm).data, vector_input.data, rtol=0, atol=1e-12)
    assert not is_rotor(vector_input)
    _gram = MatrixRepr(vector_algebra.gram).name(latex="G")
    gm.md(rt"""
    {_gram:block}

    $$\log 2={scalar_logarithm.latex(content="value")!s}.$$
    $$A=2\exp(0.3v)={vector_input.latex(content="value")!s},\qquad
    \log A={vector_logarithm.latex(content="value")!s}.$$

    Is $A$ a rotor? **{is_rotor(vector_input)}**. Its logarithm is nevertheless
    valid: exponentiating the answer recovers the original, unnormalized $A$.
    """)
    return scalar_input, scalar_logarithm, vector_algebra, vector_expected, vector_input, vector_logarithm


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Compound inputs need the whole algebra

    A closed form for $a+N$ with scalar $N^2$ is useful, but not general.
    Here two disjoint planes commute. One has negative square and one positive
    square, so their exponentials combine a rotation-like action and a boost.
    We compute their squares from the **non-diagonal Gram matrix**.

    The product contains a grade-four term. `log` must retain that information
    while recovering the compound generator. These coefficients are generator
    scales, not angles of normalized planes. `rotor_generator` adds the
    geometric validation without changing the answer on this branch.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, exp, gm, is_rotor, is_rotor_generator, is_scalar, log, np, rotor_generator, scalar_part):
    compound_algebra = Algebra(gram=[[2, 0.5, 0, 0], [0.5, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]])
    compound_gram = MatrixRepr(compound_algebra.gram).name(latex="G")
    compound_planes = (compound_algebra.blade(3, expr=True), compound_algebra.blade(12, expr=True))
    _p, _q = compound_planes
    _g = compound_algebra.gram
    assert _p * _p == _g[0, 1] ** 2 - _g[0, 0] * _g[1, 1]
    assert _q * _q == _g[2, 3] ** 2 - _g[2, 2] * _g[3, 3]
    assert _p * _q == _q * _p
    compound_generator = 0.2 * _p + 0.3 * _q
    compound_rotor = exp(0.2 * _p) * exp(0.3 * _q)
    compound_logarithm = log(compound_rotor)
    compound_recovered = rotor_generator(compound_rotor)
    _n = compound_rotor - scalar_part(compound_rotor)
    assert not is_scalar(_n * _n)
    assert is_rotor(compound_rotor) and is_rotor_generator(compound_recovered)
    np.testing.assert_allclose(compound_logarithm.data, compound_generator.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(compound_recovered.data, compound_generator.data, rtol=0, atol=1e-12)
    gm.md(rt"""
    {compound_gram:block}

    $$P={_p.latex(content="value")!s},\qquad Q={_q.latex(content="value")!s}.$$
    $$P^2={(_p * _p).latex(content="value")!s},\qquad Q^2={(_q * _q).latex(content="value")!s}.$$
    $$B=0.2P+0.3Q={compound_generator.latex(content="value")!s}.$$
    $$R=\exp(0.2P)\exp(0.3Q)={compound_rotor.latex(content="value")!s}.$$
    $$\log R={compound_logarithm.latex(content="value")!s}.$$

    `rotor_generator(R)` returns {compound_recovered:value}.
    The general logarithm uses the native left action: it does not throw away
    the grade-four coefficient or replace the Gram matrix by its diagonal.
    """)
    return (
        compound_algebra,
        compound_generator,
        compound_gram,
        compound_logarithm,
        compound_planes,
        compound_recovered,
        compound_rotor,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. A mixed-grade nilpotent logarithm

    A degenerate metric does not mean every element is singular. In an
    all-null algebra, choose $N=e_1+e_{23}$. Compute its powers first:
    $N^2$ is nonzero but $N^3=0$. Thus $1+N$ is invertible and its logarithm is

    $$\log(1+N)=N-\frac{N^2}{2}.$$

    Stopping at $N$ would be wrong. The logarithm contains grades one, two,
    and three; it is not a geometric rotor generator. This is also a case
    where an eigenvector-diagonalization shortcut is inappropriate. The
    general logarithm implementation does not require diagonalizability.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, exp, gm, is_rotor_generator, log, np):
    nilpotent_algebra = Algebra(signature=(0, 0, 0))
    nilpotent = nilpotent_algebra.blade(1, expr=True) + nilpotent_algebra.blade(6, expr=True)
    nilpotent_square = nilpotent * nilpotent
    assert nilpotent_square != 0 and nilpotent_square * nilpotent == 0
    nilpotent_input = 1 + nilpotent
    nilpotent_logarithm = log(nilpotent_input)
    nilpotent_expected = nilpotent - nilpotent_square / 2
    np.testing.assert_allclose(nilpotent_logarithm.data, nilpotent_expected.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(exp(nilpotent_logarithm).data, nilpotent_input.data, rtol=0, atol=1e-12)
    assert not is_rotor_generator(nilpotent_logarithm)
    _gram = MatrixRepr(nilpotent_algebra.gram).name(latex="G")
    gm.md(rt"""
    {_gram:block}

    $$N={nilpotent.latex(content="value")!s},\qquad N^2={nilpotent_square.latex(content="value")!s},\qquad
    N^3={(nilpotent_square * nilpotent).latex(content="value")!s}.$$
    $$\log(1+N)={nilpotent_logarithm.latex(content="value")!s}.$$

    Notice the grade-three correction. The test is the defining identity:
    exponentiating this **whole** answer recovers $1+N$.
    """)
    return nilpotent, nilpotent_algebra, nilpotent_expected, nilpotent_input, nilpotent_logarithm, nilpotent_square


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. A principal branch is a choice

    Exponentiation is many-to-one. For a plane with $J^2=-1$, adding $2\pi J$
    to an exponent does not change its exponential. `log(exp(B))` therefore
    need not return the original $B$: the principal branch wraps its phase.

    The real principal logarithm excludes singular inputs and the
    nonpositive-real spectral axis. Rejection on that cut does **not** prove
    that no other real logarithm exists. For example, $\exp(\pi J)=-1$,
    but `log(-1)` will not choose a plane for you.
    """)
    return


@app.cell
def _(Algebra, exp, gm, log, mo, np):
    branch_algebra = Algebra(2)
    branch_plane = branch_algebra.blade(3, expr=True)
    assert branch_plane * branch_plane == -np.linalg.det(branch_algebra.gram)
    unwrapped_generator = 1.25 * np.pi * branch_plane
    branch_input = exp(unwrapped_generator)
    wrapped_logarithm = log(branch_input)
    np.testing.assert_allclose(wrapped_logarithm.data, (-0.75 * np.pi * branch_plane).data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(exp(wrapped_logarithm).data, branch_input.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(exp(np.pi * branch_plane).data, (-branch_algebra.identity).data, rtol=0, atol=1e-12)
    _vector = branch_algebra.blade(1)
    assert (1 + _vector) * (1 - _vector) == 0 and 1 - _vector != 0
    branch_failures = []
    _outputs = [
        gm.md(rt"""
        $$B={unwrapped_generator.latex(content="value")!s},\qquad
        \log(\exp B)={wrapped_logarithm.latex(content="value")!s}.$$
        Their difference is $-2\pi J$; both exponents produce the same element.
        """)
    ]
    for _label, _value in (
        ("Zero is singular", branch_algebra.scalar(0)),
        ("1 + e1 is a nonzero zero divisor", 1 + _vector),
        ("Minus one is on the principal branch cut", -branch_algebra.identity),
    ):
        try:
            log(_value)
        except ValueError as _error:
            _message = str(_error)
        else:
            raise AssertionError("this input must not have an accepted principal logarithm")
        branch_failures.append((_label, _value, _message))
        _outputs.append(gm.md(t"""**{_label!s}**: `{_message!s}`."""))
    mo.vstack(_outputs)
    return branch_algebra, branch_failures, branch_input, branch_plane, unwrapped_generator, wrapped_logarithm


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Same endpoint, different paths

    In six-dimensional Euclidean space, the pseudoscalar $I$ satisfies
    $I^2=-1$ and $\widetilde I=-I$. It is a rotor, yet its principal
    logarithm $L=\pi I/2$ is **not** a rotor generator.

    At the half-step, $\exp(L/2)=(1+I)/\sqrt2$ is unit and even but sends
    a vector into grade five. That fails the vector-preservation condition.
    The endpoint alone is not enough to certify a geometric path.

    A different logarithm is the bivector
    $B=\pi(e_{12}+e_{34}+e_{56})/2$. It reaches the same $I$ while generating
    rotors throughout the path. We construct this alternative explicitly:
    `rotor_generator` does not search alternative branches automatically.
    """)
    return


@app.cell
def _(Algebra, exp, gm, is_rotor, is_rotor_generator, log, np, rotor_generator):
    path_algebra = Algebra(6)
    path_volume = path_algebra.pseudoscalar(expr=True)
    _reverse_sign = (-1) ** (path_algebra.n * (path_algebra.n - 1) // 2)
    assert path_volume * path_volume == _reverse_sign * np.linalg.det(path_algebra.gram)
    assert ~path_volume == _reverse_sign * path_volume
    _pairs = ((0, 1), (2, 3), (4, 5))
    _planes = [path_algebra.blade((1 << _i) | (1 << _j), expr=True) for _i, _j in _pairs]
    for _plane, (_i, _j) in zip(_planes, _pairs, strict=True):
        assert _plane * _plane == path_algebra.gram[_i, _j] ** 2 - path_algebra.gram[_i, _i] * path_algebra.gram[_j, _j]
    assert _planes[0] * _planes[1] * _planes[2] == path_volume
    path_logarithm = log(path_volume)
    path_generator = np.pi / 2 * sum(_planes)
    assert is_rotor(path_volume)
    assert not is_rotor_generator(path_logarithm) and is_rotor_generator(path_generator)
    np.testing.assert_allclose(exp(path_generator).data, path_volume.data, rtol=0, atol=1e-12)
    try:
        rotor_generator(path_volume)
    except ValueError as _error:
        path_generator_error = str(_error)
    else:
        raise AssertionError("the principal logarithm is not a rotor generator")
    gm.md(rt"""
    $$L=\log I={path_logarithm.latex(content="value")!s},\qquad B={path_generator.latex(content="value")!s}.$$

    `is_rotor_generator(L)`: **{is_rotor_generator(path_logarithm)}**.
    `is_rotor_generator(B)`: **{is_rotor_generator(path_generator)}**.

    `rotor_generator(I)` reports: `{path_generator_error!s}`.
    This is an honest branch limitation, not proof that no generator exists.
    """)
    return path_algebra, path_generator, path_generator_error, path_logarithm, path_volume


@app.cell
def _(mo):
    path_parameter = mo.ui.slider(start=0, stop=1, step=0.05, value=0.5, label="path parameter t")
    mo.vstack([path_parameter])
    return (path_parameter,)


@app.cell
def _(exp, gm, grade, is_rotor, mo, np, path_algebra, path_generator, path_logarithm, path_parameter, sandwich):
    path_time = path_parameter.value
    algebra_path_element = exp(path_time * path_logarithm)
    geometric_path_element = exp(path_time * path_generator)
    _vector = path_algebra.blade(1, expr=True)
    algebra_path_image = sandwich(algebra_path_element, _vector)
    geometric_path_image = sandwich(geometric_path_element, _vector)
    path_leakage = float(np.max(np.abs(grade(algebra_path_image, 5).data)))
    assert is_rotor(geometric_path_element)
    np.testing.assert_allclose(geometric_path_image.data, grade(geometric_path_image, 1).data, rtol=0, atol=1e-12)
    mo.vstack(
        [
            gm.md(rt"""
            ### Algebra-logarithm path at $t={path_time}$

            $$\exp(tL)={algebra_path_element.latex(content="value")!s}.$$
            $$\exp(tL)e_1\widetilde{{\exp(tL)}}={algebra_path_image.latex(content="value")!s}.$$

            Is it a rotor? **{is_rotor(algebra_path_element)}**.
            Largest grade-five coefficient magnitude: **{path_leakage:.3g}**.
            """),
            gm.md(rt"""
            ### Geometric-generator path at $t={path_time}$

            $$\exp(tB)e_1\widetilde{{\exp(tB)}}={geometric_path_image.latex(content="value")!s}.$$

            Is it a rotor? **{is_rotor(geometric_path_element)}**.
            Move the slider to either endpoint, then back into the interior.
            The algebra-logarithm path fails between two valid rotor endpoints;
            the geometric path preserves vectors throughout.
            """),
        ]
    )
    return (
        algebra_path_element,
        algebra_path_image,
        geometric_path_element,
        geometric_path_image,
        path_leakage,
        path_time,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Tolerance is not a branch selector

    `log(A, atol=...)` checks coefficient convergence and the exponential
    residual, bounded by `atol * max(1, max(abs(A.data)))`. This is a
    **backward-error** check: it is not a guarantee of logarithm accuracy
    near a branch cut. Raising `atol` does not request a different branch.

    The generator predicate checks evenness, reverse skewness, and
    vector-valued commutators with every native basis vector. Its tolerance
    is absolute in stored coefficients; it does not certify arbitrary large
    times or poorly conditioned changes of basis.

    The general logarithm uses a dense native left action of dimension $2^n$
    and bounded quadrature. Large algebras are expensive, and difficult
    conditioning or slow convergence can raise even when a logarithm exists.

    **Use `log` for the algebra question; use `rotor_generator` for a checked
    geometric exponent; use `is_rotor_generator` to validate an independent
    candidate.** None of them silently changes branches or normalizes inputs.
    """)
    return


if __name__ == "__main__":
    app.run()
