"""Two rotation planes, principal logarithms, and the isoclinic exception."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, dual, exp, grade, is_rotor, is_rotor_generator, log, metric_inner_product, presets

    return (
        Algebra,
        dual,
        exp,
        gm,
        grade,
        is_rotor,
        is_rotor_generator,
        log,
        metric_inner_product,
        mo,
        np,
        plt,
        presets,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # A 4D rotor can rotate two planes at once

    In three Euclidean dimensions a rotation fixes an axis and rotates its
    perpendicular plane. In four dimensions a generic rotation rotates two
    mutually orthogonal planes, potentially through different angles.
    We mean **Euclidean** $\mathrm{Cl}(4,0)$, not spacetime algebra.

    We will construct a rotor, recover its principal logarithm, test whether
    that bivector is simple, and extract two commuting plane generators.
    Equal-magnitude angles expose a genuine ambiguity, not an implementation
    failure. The self-dual splitting will explain why.
    """)
    return


@app.cell
def _(Algebra, presets):
    algebra = Algebra(config=presets.euclidean(4))
    e1, e2, e3, e4 = algebra.basis_vectors(expr=True)
    plane12, plane34 = e1 ^ e2, e3 ^ e4
    assert plane12 * plane12 == plane34 * plane34 == -1
    assert plane12 * plane34 == plane34 * plane12 == algebra.I
    return algebra, e1, e2, e3, e4, plane12, plane34


@app.cell
def _(mo):
    angle12 = mo.ui.slider(-100, 100, step=5, value=70, label="Angle in plane 12 (degrees)", show_value=True)
    angle34 = mo.ui.slider(-100, 100, step=5, value=30, label="Angle in plane 34 (degrees)", show_value=True)
    ambiguity_angle = mo.ui.slider(
        0, 90, step=5, value=35, label="Alternative isoclinic planes (degrees)", show_value=True
    )
    return ambiguity_angle, angle12, angle34


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Build and apply a double rotation

    Let $P=e_1\wedge e_2$, $Q=e_3\wedge e_4$, and
    $$B=-\tfrac12(\alpha P+\beta Q),\qquad R=\exp B.$$
    The sign and half-angle implement $x\mapsto Rx\widetilde R$, rotating
    $e_1$ toward $e_2$ by $\alpha$ and $e_3$ toward $e_4$ by $\beta$.
    Since $PQ=QP$, $\exp B=\exp(-\alpha P/2)\exp(-\beta Q/2)$.

    The plots are two **orthogonal coordinate projections** of one vector
    orbit, not a literal drawing of 4D space. A zero angle leaves an entire
    plane fixed; two nonzero angles generally do not.
    Grey marks the initial vector and orange the final vector; the arc
    follows $\exp(sB)x\exp(-sB)$ for $0\leq s\leq1$.
    """)
    return


@app.cell
def _(
    algebra,
    angle12,
    angle34,
    e1,
    e2,
    e3,
    e4,
    exp,
    is_rotor,
    np,
    plane12,
    plane34,
):
    alpha, beta = np.deg2rad(angle12.value), np.deg2rad(angle34.value)
    generator = -(alpha * plane12 + beta * plane34) / 2
    rotor = exp(generator)
    input_vector = (e1 + e3) / np.sqrt(2)
    output_vector = rotor * input_vector * ~rotor
    factorized = exp(-alpha * plane12 / 2) * exp(-beta * plane34 / 2)
    assert is_rotor(rotor)
    np.testing.assert_allclose(factorized.data, rotor.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose((rotor * ~rotor).data, algebra.identity.data, rtol=0, atol=1e-12)
    _expected = (np.cos(alpha) * e1 + np.sin(alpha) * e2 + np.cos(beta) * e3 + np.sin(beta) * e4) / np.sqrt(2)
    np.testing.assert_allclose(output_vector.data, _expected.data, rtol=0, atol=1e-12)
    return generator, input_vector, output_vector, rotor


@app.cell
def _(
    angle12,
    angle34,
    generator,
    gm,
    input_vector,
    mo,
    output_vector,
    plot_two_planes,
    rotor,
):
    mo.vstack(
        [
            mo.hstack([angle12, angle34], wrap=True),
            gm.md(rt"""
    **Constructed bivector (expression and value)**

    $$B={generator.latex(content="value")!s}.$$

    $$R={rotor.latex(content="value")!s}.$$

    $$Rx\widetilde R={output_vector.latex(content="value")!s}.$$
    """),
            plot_two_planes(generator, input_vector),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Recover a generator, then test simplicity

    `log(R)` is a mathematical principal logarithm, not an arbitrary choice
    of rotor generator. Here $|\alpha|+|\beta|<360^\circ$ keeps both
    half-angle combinations away from the principal branch cut.
    We check that the result is a bivector generator and exponentiates back.
    Outside such a branch, a logarithm need not recover the angles originally
    supplied. The identity alone cannot remember full turns.

    For a **bivector** over the reals, in any dimension or metric,
    $$B\text{ is decomposable (including zero)}\quad\Longleftrightarrow\quad
      B\wedge B=0.$$
    A nonzero decomposable bivector is one plane element.
    This is the Plücker test, not a test on arbitrary multivectors.
    Check coefficients of $B\wedge B$, not its metric norm: in a degenerate
    or indefinite algebra, a nonzero multivector can have zero self-pairing.

    Here $B=aP+bQ$ gives $B\wedge B=2abI$. One nonzero plane term is
    simple; two nonzero terms are not, even when their angles coincide.
    """)
    return


@app.cell
def _(exp, generator, grade, is_rotor_generator, log, np, rotor):
    principal_log = log(rotor)
    assert is_rotor_generator(principal_log)
    recovered = grade(principal_log, 2)
    np.testing.assert_allclose(principal_log.data, recovered.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(recovered.data, generator.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(exp(principal_log).data, rotor.data, rtol=0, atol=1e-12)
    wedge_square = recovered ^ recovered
    simple = np.linalg.norm(wedge_square.data) <= 1e-10
    log_residual = np.linalg.norm(exp(principal_log).data - rotor.data)
    return log_residual, principal_log, recovered, simple, wedge_square


@app.cell
def _(gm, log_residual, principal_log, simple, wedge_square):
    gm.md(rt"""
    $$\log R={principal_log.latex(content="value")!s}.$$

    $$B\wedge B={wedge_square.latex(content="value")!s}.$$

    Decomposable at the lesson's coefficient tolerance: **{simple!s}**.
    Exponential roundtrip residual: **{log_residual:.2e}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Extract the two commuting pieces without knowing their planes

    This formula is specific to an oriented orthonormal **Euclidean 4D**
    algebra, where $I^2=1$. Define
    $$D=\operatorname{dual}(B),\quad S=-\langle B^2\rangle_0,\quad T=(B\wedge B)/I,\quad \Delta=\sqrt{S^2-T^2}.$$
    With Galaga's dual convention, $\operatorname{dual}(P)=-Q$.
    If $B=aP+bQ$, then $D=-bP-aQ$, $S=a^2+b^2$, $T=2ab$ and
    $\Delta=|a^2-b^2|$.

    Solving these two linear equations isolates the larger-magnitude piece:
    $$B_1=\frac{(S+\Delta)B+TD}{2\Delta},\qquad B_2=B-B_1.$$
    Check $B_i\wedge B_i=0$, $B_1B_2=B_2B_1$, and
    $\exp B_1\exp B_2=R$. These are weighted generators; divide a nonzero
    piece by its magnitude to obtain a unit plane.

    At equal magnitudes $\Delta=0$: this formula must not divide by zero.
    Near equality it is ill-conditioned. The notebook reports that case
    instead of displaying numerically invented planes.
    """)
    return


@app.cell
def _(decompose_4d, exp, gm, mo, np, recovered, rotor):
    pieces, invariants, decomposition_status = decompose_4d(recovered)
    _S, _T, _delta = invariants
    _panels = [
        gm.md(rt"""
    $$S={_S:.6g},\qquad T={_T:.6g},\qquad \Delta={_delta:.6g}.$$

    **{decomposition_status}**
    """)
    ]
    if pieces is not None:
        first_piece, second_piece = pieces
        for _piece in pieces:
            np.testing.assert_allclose((_piece ^ _piece).data, 0, rtol=0, atol=1e-10)
        np.testing.assert_allclose((first_piece * second_piece - second_piece * first_piece).data, 0, atol=1e-10)
        np.testing.assert_allclose((exp(first_piece) * exp(second_piece)).data, rotor.data, rtol=0, atol=1e-10)
        _panels.append(
            gm.md(rt"""
    $$B_1={first_piece.latex(content="value")!s},\qquad B_2={second_piece.latex(content="value")!s}.$$
    """)
        )
    mo.vstack(_panels)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Self-dual does not mean simple

    Fix the Euclidean Hodge-star convention $\star e_{12}=e_{34}$.
    On bivectors in this notebook, $\star B=-\operatorname{dual}(B)$.
    Set $B_\pm=(B\pm\star B)/2$; then $\star B_\pm=\pm B_\pm$.

    **Correction to the conversation:** a simple bivector does not have
    one part zero. Simplicity means $\|B_+\|^2=\|B_-\|^2$, because
    $$B\wedge B=(\|B_+\|^2-\|B_-\|^2)I.$$
    For $B=e_{12}$, $B_\pm=(e_{12}\pm e_{34})/2$: both are nonzero
    and each has squared norm $1/2$. A nonzero self-dual or
    anti-self-dual bivector is nonsimple and generates an isoclinic rotation.

    The two three-dimensional sectors commute. This is the Lie-algebra
    splitting $\mathfrak{so}(4)=\mathfrak{su}(2)\oplus\mathfrak{su}(2)$;
    at the group level $\mathrm{Spin}(4)\cong SU(2)\times SU(2)$.
    These sectors are not the two simple planes extracted above.
    """)
    return


@app.cell
def _(algebra, dual, exp, gm, metric_inner_product, np, recovered, rotor):
    hodge = -dual(recovered)
    self_dual = (recovered + hodge) / 2
    anti_self_dual = (recovered - hodge) / 2
    plus_norm = float(metric_inner_product(self_dual, self_dual))
    minus_norm = float(metric_inner_product(anti_self_dual, anti_self_dual))
    np.testing.assert_allclose((recovered ^ recovered).data, ((plus_norm - minus_norm) * algebra.I).data, atol=1e-12)
    np.testing.assert_allclose((self_dual * anti_self_dual - anti_self_dual * self_dual).data, 0, atol=1e-12)
    np.testing.assert_allclose((exp(self_dual) * exp(anti_self_dual)).data, rotor.data, atol=1e-12)
    gm.md(rt"""
    $$B_+={self_dual.latex(content="value")!s}.$$

    $$B_-={anti_self_dual.latex(content="value")!s}.$$

    $$\|B_+\|^2={plus_norm:.6g},\qquad \|B_-\|^2={minus_norm:.6g}.$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Equal angles: different planes, exactly the same motion

    Independently of the two angles above, fix
    $B_{\rm iso}=-(\pi/6)(e_{12}+e_{34})$: a $60^\circ$ rotation in both planes.
    Mix the axes by $\phi$:
    $$u=\cos\phi\,e_1+\sin\phi\,e_3,\quad
      v=\cos\phi\,e_2+\sin\phi\,e_4,$$
    $$s=-\sin\phi\,e_1+\cos\phi\,e_3,\quad
      t=-\sin\phi\,e_2+\cos\phi\,e_4.$$
    The orthogonal planes $u\wedge v$ and $s\wedge t$ change, but their sum
    remains $e_{12}+e_{34}$. There is no preferred pair for an extraction
    routine to recover. This is a geometric ambiguity; the zero generator
    is a separate case with no rotation planes at all.
    """)
    return


@app.cell
def _(ambiguity_angle, e1, e2, e3, e4, exp, gm, mo, np, plane12, plane34):
    phi = np.deg2rad(ambiguity_angle.value)
    u, v = np.cos(phi) * e1 + np.sin(phi) * e3, np.cos(phi) * e2 + np.sin(phi) * e4
    s, t = -np.sin(phi) * e1 + np.cos(phi) * e3, -np.sin(phi) * e2 + np.cos(phi) * e4
    alternative_plane1, alternative_plane2 = u ^ v, s ^ t
    iso_generator = -np.pi / 6 * (plane12 + plane34)
    iso_rotor = exp(iso_generator)
    alternative_rotor = exp(-np.pi / 6 * alternative_plane1) * exp(-np.pi / 6 * alternative_plane2)
    np.testing.assert_allclose((alternative_plane1 + alternative_plane2).data, (plane12 + plane34).data, atol=1e-12)
    np.testing.assert_allclose(alternative_rotor.data, iso_rotor.data, atol=1e-12)
    ambiguity_residual = np.linalg.norm(alternative_rotor.data - iso_rotor.data)
    mo.vstack(
        [
            ambiguity_angle,
            gm.md(rt"""
    $$P_\phi={alternative_plane1.latex(content="value")!s}.$$

    $$Q_\phi={alternative_plane2.latex(content="value")!s}.$$

    Rotor agreement despite the changing planes: **{ambiguity_residual:.2e}**.
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. The wedge-square test survives higher dimensions and other metrics

    The special dual-based extraction formula does **not** carry over:
    in six dimensions the dual of a bivector has grade four.
    The bivector simplicity test $B\wedge B=0$ does carry over.
    In Euclidean dimension $n$, an orthogonal normal form has at most
    $\lfloor n/2\rfloor$ mutually orthogonal plane terms.

    Here are a decomposable and a three-plane bivector in six dimensions,
    followed by a nonsimple bivector in a completely degenerate metric.
    The last example has zero metric self-pairing but a nonzero wedge square.
    """)
    return


@app.cell
def _(Algebra, gm, metric_inner_product, mo, presets):
    six = Algebra(config=presets.euclidean(6))
    _a, _b, _c, _d, _e, _f = six.basis_vectors()
    simple_six = (_a + _c) ^ (_b - _f)
    nonsimple_six = (_a ^ _b) + 2 * (_c ^ _d) + 3 * (_e ^ _f)
    assert simple_six ^ simple_six == 0
    assert nonsimple_six ^ nonsimple_six != 0
    degenerate = Algebra(gram=[[0] * 4 for _ in range(4)])
    _a, _b, _c, _d = degenerate.basis_vectors()
    null_nonsimple = (_a ^ _b) + (_c ^ _d)
    null_wedge_square = null_nonsimple ^ null_nonsimple
    assert metric_inner_product(null_nonsimple, null_nonsimple) == 0
    assert metric_inner_product(null_wedge_square, null_wedge_square) == 0
    assert null_wedge_square != 0
    mo.vstack(
        [
            gm.md(rt"""
    **Six-dimensional Euclidean examples**

    $$A={simple_six.latex(content="value")!s},\qquad A\wedge A=0.$$

    $$C={nonsimple_six.latex(content="value")!s}.$$

    $$C\wedge C={(nonsimple_six ^ nonsimple_six).latex(content="value")!s}.$$
    """),
            gm.md(rt"""
    **Zero metric, nonzero exterior geometry**

    $$N={null_nonsimple.latex(content="value")!s},\qquad
    N\wedge N={null_wedge_square.latex(content="value")!s}.$$
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Further reading

    [Roelfs and De Keninck, *Graded Symmetry Groups: Plane and Simple*](https://arxiv.org/abs/2107.03771)
    develops invariant decomposition and its relation to rotor exponentials.
    Our extraction formula is the restricted Euclidean 4D calculation
    derived above, not an implementation of the paper's general algorithm.

    [John Baez, *This Week's Finds*, Week 61](https://math.ucr.edu/home/baez/twf_html/week61.html)
    explains the group-level $\mathrm{Spin}(4)=SU(2)\times SU(2)$ relationship.

    Continue with [Witt bases](witt_bases_and_null_geometry.py) to separate
    null vectors from degenerate metrics, or
    [logarithms and rotors](exp_log_rotors.py) for the public logarithm contract.

    ## Appendix: numerical extraction and plotting
    """)
    return


@app.cell(hide_code=True)
def _(dual, grade, np):
    def decompose_4d(bivector):
        """Lesson-local formula for a real Euclidean 4D bivector."""
        S = -float(grade(bivector * bivector, 0))
        T = float((bivector ^ bivector) / bivector.algebra.I)
        delta = np.sqrt(max(0.0, S * S - T * T))
        if S <= 1e-24:
            return None, (S, T, delta), "Zero generator: no distinguished planes."
        if delta <= 1e-6 * S:
            return None, (S, T, delta), "Isoclinic or numerically unresolved: no stable unique plane pair."
        first = ((S + delta) * bivector + T * dual(bivector)) / (2 * delta)
        return (first, bivector - first), (S, T, delta), "Distinct plane magnitudes: extraction is resolved."

    return (decompose_4d,)


@app.cell(hide_code=True)
def _(exp, np, plt):
    def plot_two_planes(generator_value, vector_value):
        fractions = np.linspace(0, 1, 80)
        orbit = []
        for fraction in fractions:
            r = exp(fraction * generator_value)
            orbit.append((r * vector_value * ~r).data[[1, 2, 4, 8]])
        coords = np.array(orbit)
        fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
        for axis, offset, title in zip(axes, (0, 2), ("12-plane projection", "34-plane projection")):
            axis.plot(coords[:, offset], coords[:, offset + 1], color="tab:blue")
            axis.scatter(coords[[0, -1], offset], coords[[0, -1], offset + 1], color=["grey", "tab:orange"])
            axis.set(title=title, xlim=(-1, 1), ylim=(-1, 1), aspect="equal")
            axis.set_xlabel(f"e{offset + 1} coordinate")
            axis.set_ylabel(f"e{offset + 2} coordinate")
        fig.tight_layout()
        plt.close(fig)
        return fig

    return (plot_two_planes,)


if __name__ == "__main__":
    app.run()
