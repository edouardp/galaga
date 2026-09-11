import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from galaga_matrix import MatrixRepr, from_spinor_column, to_matrix, to_spinor_column

    import galaga_marimo as gm
    from galaga import Algebra, even_grades, exp, odd_grades, presets, reverse

    return (
        Algebra,
        MatrixRepr,
        even_grades,
        exp,
        from_spinor_column,
        gm,
        mo,
        np,
        odd_grades,
        plt,
        presets,
        reverse,
        to_matrix,
        to_spinor_column,
    )


@app.cell
def _(gm, mo):
    def matrix_panel(title, matrix, caption=None):
        """Keep headings above math, and explanatory text below it."""
        items = [gm.md(t"""**{title}**"""), gm.md(t"""{matrix:block}""")]
        if caption is not None:
            items.append(caption)
        return mo.vstack(items, align="start", gap=0.75)

    return (matrix_panel,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # One spinor, three representations

    **Ideals, columns, and geometric actions**

    If we change how a spinor is represented, does its transformation change,
    or just its coordinates? We will follow the same calculation through a
    Clifford algebra, matrices, and columns, then use the Weyl basis to see chirality.

    Prerequisites: geometric products, reversion, and ordinary matrix multiplication.
    Read `spinor_columns.py` for the conversion API. Here the emphasis is on
    **what an action means**, not on classifying every kind of spinor.

    Conventions: first $\mathrm{Cl}(3,0)$ with $e_i^2=+1$, then
    $\mathrm{Cl}(1,3)$ with $\gamma_0^2=+1$ and $\gamma_i^2=-1$.
    A column is a state; a square matrix is an operator on states.
    """)
    return


@app.cell
def _(Algebra, MatrixRepr, np, presets, to_matrix):
    pauli = Algebra(config=presets.euclidean(3))
    e1, e2, e3 = pauli.basis_vectors(expr=True)
    f = (1 + e3) / 2
    f_matrix = to_matrix(f, mode="compact")
    assert f * f == f
    assert e3 * e3 == pauli.gram[2, 2] == 1
    np.testing.assert_allclose(f_matrix.mat, np.diag([1, 0]), atol=1e-12)

    def ideal_column(value):
        """Extract this lesson's Cl(3,0) ideal column, not an arbitrary MV column."""
        np.testing.assert_allclose((value * f).data, value.data, rtol=0, atol=1e-12)
        matrix = to_matrix(value, mode="compact").mat
        np.testing.assert_allclose(matrix[:, 1], 0, rtol=0, atol=1e-12)
        return MatrixRepr(matrix[:, :1], algebra=pauli, mode="compact", basis="pauli", kind="ket")

    return e1, e2, e3, f, f_matrix, ideal_column, pauli


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. A column hiding inside the algebra

    Choose the idempotent $f=(1+e_3)/2$. The **left ideal**
    $\mathrm{Cl}(3,0)f$ consists of all $Af$ and is closed under left multiplication:
    $B(Af)=(BA)f$ for **every** multivector $B$, not just rotors.

    Its two-component complex description is

    $$\psi=af+be_1f
    \quad\longleftrightarrow\quad
    \begin{pmatrix}a&0\\b&0\end{pmatrix}
    \quad\longleftrightarrow\quad
    \begin{pmatrix}a\\b\end{pmatrix}.$$

    In the real algebra, complex amplitudes use the central pseudoscalar
    $I=e_{123}$, whose square is $-1$. It maps to $i$ in the Pauli matrices.
    We do **not** insert Python complex coefficients into Galaga multivectors.

    Change the real and imaginary parts below. Neither normalization nor a
    nonzero state is required for this linear-algebra experiment.
    """)
    return


@app.cell
def _(mo):
    a_real = mo.ui.slider(-2, 2, step=0.25, value=1, label="Re(a)")
    a_imag = mo.ui.slider(-2, 2, step=0.25, value=0.5, label="Im(a)")
    b_real = mo.ui.slider(-2, 2, step=0.25, value=0.5, label="Re(b)")
    b_imag = mo.ui.slider(-2, 2, step=0.25, value=-0.75, label="Im(b)")
    return a_imag, a_real, b_imag, b_real


@app.cell
def _(
    a_imag,
    a_real,
    b_imag,
    b_real,
    e1,
    f,
    f_matrix,
    gm,
    ideal_column,
    matrix_panel,
    mo,
    np,
    pauli,
    to_matrix,
):
    amplitude_a = a_real.value + a_imag.value * pauli.I
    amplitude_b = b_real.value + b_imag.value * pauli.I
    ideal_spinor = (amplitude_a * f + amplitude_b * e1 * f).named(r"\psi")
    spinor_matrix = to_matrix(ideal_spinor, mode="compact")
    spinor_ket = ideal_column(ideal_spinor)

    np.testing.assert_allclose(to_matrix(pauli.I, mode="compact").mat, 1j * np.eye(2), atol=1e-12)

    mo.vstack(
        [
            mo.hstack([mo.vstack([a_real, a_imag]), mo.vstack([b_real, b_imag])]),
            matrix_panel(
                "The chosen projector",
                f_matrix,
                mo.md("Its image has complex dimension one; the **left ideal** has complex dimension two."),
            ),
            gm.md(rt"""
    **Algebra element**

    {ideal_spinor:full}

    $$\psi={ideal_spinor.latex(content="value")!s}.$$
    """),
            mo.hstack(
                [
                    matrix_panel("Ideal matrix", spinor_matrix),
                    matrix_panel("Column", spinor_ket),
                ],
                wrap=True,
                gap=2,
            ),
        ]
    )
    return ideal_spinor, spinor_ket


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. The apparent shear is actually a swap

    Predict the result before selecting an operator:

    $$e_1(af+be_1f)=bf+ae_1f,$$
    because $e_1^2=1$. This is invertible: applying $e_1$ twice returns the state.
    Meanwhile $e_3$ changes the sign of the second component.

    The statement $f^2=f$ does **not** make left multiplication by $f$ an identity:

    $$\psi f=\psi,\qquad f\psi=af.$$

    $f$ is an identity on the **right** of this ideal and a projector on the
    **left**. Fixing one state ($e_3f=f$) does not mean fixing every state.
    """)
    return


@app.cell
def _(mo):
    operator_choice = mo.ui.dropdown(["1", "e1", "e3", "f"], value="e1", label="Left-acting operator")
    return (operator_choice,)


@app.cell
def _(
    e1,
    e3,
    f,
    gm,
    ideal_column,
    ideal_spinor,
    matrix_panel,
    mo,
    np,
    operator_choice,
    pauli,
    spinor_ket,
    to_matrix,
):
    selected_operator = {"1": pauli.identity, "e1": e1, "e3": e3, "f": f}[operator_choice.value]
    selected_matrix = to_matrix(selected_operator, mode="compact")
    acted_ideal = selected_operator * ideal_spinor
    acted_ket = selected_matrix @ spinor_ket
    action_residual = np.linalg.norm(acted_ket.mat - ideal_column(acted_ideal).mat)
    np.testing.assert_allclose(acted_ket.mat, ideal_column(acted_ideal).mat, rtol=0, atol=1e-12)
    mo.vstack(
        [
            mo.vstack([operator_choice]),
            gm.md(rt"""
    **Algebra result**

    $$A\psi={acted_ideal.latex(content="value")!s}.$$
    """),
            mo.hstack(
                [
                    matrix_panel("Operator", selected_matrix),
                    matrix_panel("Matrix result", acted_ket, gm.md(t"""Agreement residual: {action_residual:.2e}.""")),
                ],
                wrap=True,
                gap=2,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. One rotation, two actions

    Use a fixed normalized state $(f+e_1f)/\sqrt{2}$, whose Bloch vector is $e_1$.
    For $R=\exp(-\theta e_{12}/2)$ the vector transforms as
    $v'=Rv\widetilde R$, while the spinor transforms as $\psi'=R\psi$.

    The left plot is a **physical-space vector**. The middle plot shows
    **complex amplitudes**, not physical arrows rotating at a different speed.
    The Bloch vector reconstructed from the transformed column agrees with the
    sandwich action. Try $\theta=2\pi$ and $4\pi$.

    A $2\pi$ rotation changes the spinor's sign, not its isolated-state
    observables. The right plot imagines recombining it with an **unrotated
    coherent reference arm**, where that relative sign can matter. Its displayed
    quantity is $\|\chi+\chi_0\|^2/4$ for unit columns, not a measurement of an
    isolated global phase.
    """)
    return


@app.cell
def _(mo):
    turns = mo.ui.slider(0, 2, step=0.0625, value=0.25, label="Rotation θ / (2π)")
    return (turns,)


@app.cell
def _(
    e1,
    e2,
    e3,
    exp,
    f,
    gm,
    ideal_column,
    matrix_panel,
    mo,
    np,
    plt,
    reverse,
    to_matrix,
    turns,
):
    theta = 2 * np.pi * turns.value
    rotation = exp(-theta * (e1 ^ e2) / 2)
    rotation_seed = (f + e1 * f) / np.sqrt(2)
    rotation_reference = ideal_column(rotation_seed)
    rotation_state = rotation * rotation_seed
    rotation_column = ideal_column(rotation_state)
    rotated_vector = rotation * e1 * reverse(rotation)
    bloch_vector = np.array(
        [
            np.vdot(rotation_column.mat[:, 0], to_matrix(_v, mode="compact").mat @ rotation_column.mat[:, 0]).real
            for _v in (e1, e2, e3)
        ]
    )
    np.testing.assert_allclose(bloch_vector, rotated_vector.vector_part, rtol=0, atol=1e-12)
    interference = float(np.linalg.norm(rotation_column.mat + rotation_reference.mat) ** 2 / 4)
    _fig, _axes = plt.subplots(1, 3, figsize=(11, 3.3), layout="constrained")
    for _ax in _axes[:2]:
        _ax.axhline(0, color="0.8", lw=0.7)
        _ax.axvline(0, color="0.8", lw=0.7)
        _ax.set(xlim=(-1.15, 1.15), ylim=(-1.15, 1.15), aspect="equal")
    _axes[0].arrow(0, 0, *rotated_vector.vector_part[:2], width=0.018, length_includes_head=True, color="tab:blue")
    _axes[0].scatter(*bloch_vector[:2], facecolors="none", edgecolors="tab:orange", s=130, label="From column")
    _axes[0].set(title="Physical vector / Bloch vector", xlabel="e1", ylabel="e2")
    _axes[0].legend(fontsize=8, loc="lower left")
    for _index, _z in enumerate(rotation_column.mat[:, 0]):
        _axes[1].arrow(0, 0, _z.real, _z.imag, width=0.012, length_includes_head=True, color=f"C{_index}")
        _axes[1].annotate(
            f"χ{_index + 1}",
            (_z.real, _z.imag),
            xytext=(4, 6 if _index == 0 else -12),
            textcoords="offset points",
            fontsize=10,
        )
    _axes[1].set(title="Complex components", xlabel="Real", ylabel="Imaginary")
    _axes[2].bar([0], [interference], color="tab:purple")
    _axes[2].set(ylim=(0, 1.05), xticks=[0], xticklabels=["Reference-arm overlap"], title="Coherent recombination")
    rotation_figure = _fig
    plt.close(_fig)
    mo.vstack(
        [
            mo.vstack([turns]),
            rotation_figure,
            gm.md(rt"""
    $$R={rotation.latex(content="value")!s}.$$

    Coherent recombination quantity: {interference:.4f}.
    """),
            matrix_panel("Transformed column", rotation_column),
        ]
    )
    return rotation_reference, rotation_seed


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. A mirror plane is not an axis half-turn

    For a unit Euclidean normal $n$, a vector's **plane reflection** is
    $v'=-nvn$. Without the minus sign, $nvn$ is an **axis half-turn** in 3D:
    it keeps the component along $n$ and reverses both perpendicular components.
    The matrices below are derived by acting on all three basis vectors with $n=e_3$.

    On the spinor, left multiplication by $n$ is a Pin action. But the Bloch
    vector constructed from its column transforms by $NVN^\dagger$, without
    the plane-reflection minus sign: it behaves as an **axial** vector under
    this mirror, not as a polar position vector. This is not a failure of Clifford
    algebra to represent reflections; the two objects transform differently.
    """)
    return


@app.cell
def _(
    MatrixRepr,
    e1,
    e2,
    e3,
    gm,
    ideal_column,
    matrix_panel,
    mo,
    np,
    rotation_reference,
    rotation_seed,
    to_matrix,
):
    reflected_frame = tuple(-e3 * _v * e3 for _v in (e1, e2, e3))
    halfturned_frame = tuple(e3 * _v * e3 for _v in (e1, e2, e3))
    plane_reflection = MatrixRepr(np.column_stack([_v.vector_part for _v in reflected_frame]))
    axis_halfturn = MatrixRepr(np.column_stack([_v.vector_part for _v in halfturned_frame]))
    mirror_column = ideal_column(e3 * rotation_seed)
    np.testing.assert_allclose(mirror_column.mat, (to_matrix(e3, mode="compact") @ rotation_reference).mat, atol=1e-12)
    mo.vstack(
        [
            mo.hstack(
                [
                    matrix_panel(
                        "Polar-vector plane reflection",
                        plane_reflection,
                        gm.md(t"""Determinant: {np.linalg.det(plane_reflection.mat):.0f}."""),
                    ),
                    matrix_panel(
                        "Axis half-turn / axial-vector action",
                        axis_halfturn,
                        gm.md(t"""Determinant: {np.linalg.det(axis_halfturn.mat):.0f}."""),
                    ),
                ],
                wrap=True,
                gap=2,
            ),
            matrix_panel("One-sided spinor action", mirror_column),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Chirality becomes visible in the Weyl basis

    Now use **real even multivectors** $\Psi$ in $\mathrm{Cl}(1,3)$ and their
    four-component complex columns $\chi=\operatorname{column}(\Psi)$.
    Begin in GA, rather than introducing a matrix-only operation.

    Let $I=\gamma_0\gamma_1\gamma_2\gamma_3$. For our spinor convention there is
    a real bivector $J$ for which

    $$\operatorname{column}(\Psi J)=i\operatorname{column}(\Psi).$$

    We **derive** $J$ by converting $i\operatorname{column}(1)$ back to an even
    multivector, then verify this identity on all eight even basis blades.
    This identifies the column's complex structure; it does not insert complex
    coefficients into the real algebra. In this convention $J=-\gamma_1\gamma_2$.

    Since $I^2=J^2=-1$, the real-GA chirality operation is an involution:

    $$\mathcal C(\Psi)=I\Psi J,\qquad
    \mathcal C^2(\Psi)=I^2\Psi J^2=\Psi.$$

    Its complementary projections are

    $$\mathcal P_L(\Psi)=\frac{\Psi-I\Psi J}{2},\qquad
    \mathcal P_R(\Psi)=\frac{\Psi+I\Psi J}{2}.$$

    Apply $\mathcal C$ to the spinors corresponding to the four standard
    complex columns to **build its matrix** $\Gamma_5$ column by column.
    We then check $\Gamma_5=i\rho(I)$ and obtain
    $P_L=(1-\Gamma_5)/2$, $P_R=(1+\Gamma_5)/2$.

    **Operations versus elements:** $\mathcal P_L$ and $\mathcal P_R$ are
    two-sided operations on real MVs, not left multiplication by single real
    MVs. Their matrices need not belong to the image of `to_matrix`.
    In fact, `from_matrix(P_L)` rejects this projector even in the Dirac basis:
    real matrix entries do not imply real Clifford coefficients.
    The **projected spinor**, however, roundtrips using `from_spinor_column`.

    Start with a left-chiral column. An even rotor preserves chirality; an odd
    vector flips it; a sum of the two can produce both components. That sum is
    a valid Clifford operator, but is not thereby a rotation or reflection.

    Our even example includes a boost as well as a rotation, so ordinary column
    squared norms are **not conserved probabilities**. The reported left/right
    weights simply show which components are present. Chirality is not helicity.

    Switching between Dirac and Weyl changes coordinates, not the operator.
    In Weyl coordinates, blue diagonal blocks preserve chirality and orange
    off-diagonal blocks exchange it. In Dirac coordinates, that block shortcut
    is unavailable; the projectors still work.
    """)
    return


@app.cell
def _(
    Algebra,
    MatrixRepr,
    exp,
    from_spinor_column,
    np,
    presets,
    to_matrix,
    to_spinor_column,
):
    sta = Algebra(config=presets.sta())
    gamma = sta.basis_vectors(expr=True)
    spinor_complex_structure = from_spinor_column(1j * to_spinor_column(sta.identity))

    def real_chirality(psi):
        """Chirality on this lesson's real even STA spinor representatives."""
        return sta.I * psi * spinor_complex_structure

    def project_left(psi):
        return (psi - real_chirality(psi)) / 2

    def project_right(psi):
        return (psi + real_chirality(psi)) / 2

    np.testing.assert_allclose((sta.I * sta.I).data, (-sta.identity).data, atol=1e-12)
    np.testing.assert_allclose(
        (spinor_complex_structure * spinor_complex_structure).data, (-sta.identity).data, atol=1e-12
    )
    for _mask in range(sta.dim):
        if _mask.bit_count() % 2:
            continue
        _psi = sta.blade(_mask)
        np.testing.assert_allclose(
            to_spinor_column(_psi * spinor_complex_structure).mat,
            1j * to_spinor_column(_psi).mat,
            atol=1e-12,
        )
    _columns = []
    for _index in range(4):
        _unit_column = MatrixRepr(
            np.eye(4, dtype=complex)[:, _index : _index + 1],
            algebra=sta,
            mode="compact",
            basis="dirac",
            kind="ket",
        )
        _unit_spinor = from_spinor_column(_unit_column)
        _columns.append(to_spinor_column(real_chirality(_unit_spinor)).mat[:, 0])
    chirality = MatrixRepr(np.column_stack(_columns), algebra=sta, mode="compact", basis="dirac")
    dirac_identity = to_matrix(sta.identity, mode="compact")
    np.testing.assert_allclose(chirality.mat, (1j * to_matrix(sta.I, mode="compact")).mat, atol=1e-12)
    left_projector = (dirac_identity - chirality) / 2
    right_projector = (dirac_identity + chirality) / 2
    sta_seed = exp(-0.3 * gamma[1] * gamma[2]) + 0.25 * gamma[0] * gamma[1] + 0.1 * sta.I
    dirac_seed = to_spinor_column(sta_seed)
    left_seed_ga = project_left(sta_seed)
    left_seed = to_spinor_column(left_seed_ga)
    np.testing.assert_allclose(left_seed.mat, (left_projector @ dirac_seed).mat, atol=1e-12)
    even_operator = exp(0.35 * gamma[0] * gamma[1]) * exp(-0.6 * gamma[1] * gamma[2])
    odd_operator = gamma[0]
    np.testing.assert_allclose((chirality @ chirality).mat, dirac_identity.mat, atol=1e-12)
    for _g in gamma:
        _m = to_matrix(_g, mode="compact")
        np.testing.assert_allclose((chirality @ _m + _m @ chirality).mat, 0, atol=1e-12)
    return (
        chirality,
        even_operator,
        gamma,
        left_projector,
        left_seed,
        left_seed_ga,
        odd_operator,
        project_left,
        project_right,
        right_projector,
        spinor_complex_structure,
        sta,
        sta_seed,
    )


@app.cell
def _(gm, left_seed_ga, spinor_complex_structure, sta_seed):
    gm.md(rt"""
    The computed complex structure is

    $$J={spinor_complex_structure.latex(content="value")!s}.$$

    Choose this real even seed (not necessarily a rotor):

    $$\Psi_0={sta_seed.latex(content="value")!s}.$$

    Project it **in GA** to obtain the left-chiral input used below:

    $$\Psi_{{0,L}}={left_seed_ga.latex(content="value")!s}.$$
    """)
    return


@app.cell
def _(mo):
    chiral_action = mo.ui.dropdown(["even rotor", "odd vector", "mixed"], value="mixed", label="Clifford action")
    chiral_basis = mo.ui.dropdown(["weyl", "dirac"], value="weyl", label="Display basis")
    odd_strength = mo.ui.slider(-1, 1, step=0.1, value=0.6, label="Odd contribution in mixed operator")
    return chiral_action, chiral_basis, odd_strength


@app.cell
def _(
    chiral_action,
    chiral_basis,
    chirality,
    even_operator,
    gm,
    left_projector,
    left_seed,
    matrix_panel,
    mo,
    np,
    odd_operator,
    odd_strength,
    plt,
    right_projector,
    to_matrix,
):
    chiral_operator = {
        "even rotor": even_operator,
        "odd vector": odd_operator,
        "mixed": even_operator + odd_strength.value * odd_operator,
    }[chiral_action.value]
    dirac_operator = to_matrix(chiral_operator, mode="compact")
    dirac_result = dirac_operator @ left_seed
    chiral_result = dirac_result.to_basis(chiral_basis.value)
    displayed_operator = dirac_operator.to_basis(chiral_basis.value)
    displayed_chirality = chirality.to_basis(chiral_basis.value)
    displayed_left = left_projector.to_basis(chiral_basis.value)
    displayed_right = right_projector.to_basis(chiral_basis.value)
    left_weight = float(np.linalg.norm((left_projector @ dirac_result).mat) ** 2)
    right_weight = float(np.linalg.norm((right_projector @ dirac_result).mat) ** 2)
    preserving_part = (
        left_projector @ dirac_operator @ left_projector + right_projector @ dirac_operator @ right_projector
    )
    exchanging_part = (
        left_projector @ dirac_operator @ right_projector + right_projector @ dirac_operator @ left_projector
    )
    np.testing.assert_allclose((preserving_part + exchanging_part).mat, dirac_operator.mat, atol=1e-12)
    _fig, _ax = plt.subplots(figsize=(4.5, 4), layout="constrained")
    _image = _ax.imshow(np.abs(displayed_operator.mat), cmap="Greys", vmin=0)
    _fig.colorbar(_image, ax=_ax, label="Absolute matrix entry")
    if chiral_basis.value == "weyl":
        from matplotlib.patches import Rectangle as _Rectangle

        for _row in (0, 2):
            for _col in (0, 2):
                _ax.add_patch(
                    _Rectangle(
                        (_col - 0.5, _row - 0.5),
                        2,
                        2,
                        fill=False,
                        lw=3,
                        edgecolor="tab:blue" if _row == _col else "tab:orange",
                    )
                )
        _ax.set(xticks=[0.5, 2.5], xticklabels=["L in", "R in"], yticks=[0.5, 2.5], yticklabels=["L out", "R out"])
    else:
        _ax.set(xticks=range(4), yticks=range(4), xlabel="Input component", ylabel="Output component")
    _ax.set_title(f"{chiral_action.value}, {chiral_basis.value} basis")
    chiral_figure = _fig
    plt.close(_fig)
    mo.vstack(
        [
            matrix_panel("Chirality", displayed_chirality),
            mo.hstack(
                [
                    matrix_panel("Left projector", displayed_left),
                    matrix_panel("Right projector", displayed_right),
                ],
                wrap=True,
                gap=2,
            ),
            chiral_action,
            chiral_basis,
            odd_strength,
            matrix_panel("Operator", displayed_operator),
            matrix_panel(
                "Result from a left-chiral input",
                chiral_result,
                gm.md(t"""Left weight: {left_weight:.6f}. Right weight: {right_weight:.6f}."""),
            ),
            chiral_figure,
        ],
        gap=2,
    )
    return chiral_operator, dirac_operator, dirac_result


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 5.1. Close the loop: GA → column → projection → GA

    Keep the selected operator $A$ and display basis above. For this STA
    reference column, $\rho(\gamma_0)u=u$. Therefore the full Clifford action
    on an **even representative** is

    $$\Psi'=A_{\rm even}\Psi_{0,L}+A_{\rm odd}\Psi_{0,L}\gamma_0.$$

    The right factor keeps the odd operator's result in the even representation;
    it is specific to this reference convention. We check its column against
    $\rho(A)\operatorname{column}(\Psi_{0,L})$.

    Now take two independent routes: compute $\mathcal P_{L/R}(\Psi')$ directly
    with real geometric products, or project the column using $P_{L/R}$ and
    convert it back. Changing to Weyl coordinates before conversion back must
    give the same real multivector. Try the even, odd, and mixed actions.
    """)
    return


@app.cell
def _(
    chiral_basis,
    chiral_operator,
    dirac_result,
    even_grades,
    from_spinor_column,
    gamma,
    gm,
    left_projector,
    left_seed_ga,
    matrix_panel,
    mo,
    np,
    odd_grades,
    project_left,
    project_right,
    right_projector,
    to_spinor_column,
):
    acted_sta_spinor = (
        even_grades(chiral_operator) * left_seed_ga + odd_grades(chiral_operator) * left_seed_ga * gamma[0]
    )
    np.testing.assert_allclose(to_spinor_column(acted_sta_spinor).mat, dirac_result.mat, atol=1e-12)
    left_ga = project_left(acted_sta_spinor)
    right_ga = project_right(acted_sta_spinor)
    projected_left_column = (left_projector @ dirac_result).to_basis(chiral_basis.value)
    projected_right_column = (right_projector @ dirac_result).to_basis(chiral_basis.value)
    recovered_left_ga = from_spinor_column(projected_left_column)
    recovered_right_ga = from_spinor_column(projected_right_column)
    left_roundtrip_residual = float(np.linalg.norm(recovered_left_ga.data - left_ga.data))
    right_roundtrip_residual = float(np.linalg.norm(recovered_right_ga.data - right_ga.data))
    for _ga, _column, _recovered in (
        (left_ga, projected_left_column, recovered_left_ga),
        (right_ga, projected_right_column, recovered_right_ga),
    ):
        np.testing.assert_allclose(to_spinor_column(_ga).to_basis(chiral_basis.value).mat, _column.mat, atol=1e-12)
        np.testing.assert_allclose(_recovered.data, _ga.data, atol=1e-12)
    np.testing.assert_allclose((left_ga + right_ga).data, acted_sta_spinor.data, atol=1e-12)
    mo.vstack(
        [
            mo.hstack(
                [
                    matrix_panel("Projected left column", projected_left_column),
                    matrix_panel("Projected right column", projected_right_column),
                ],
                wrap=True,
                gap=2,
            ),
            gm.md(rt"""
    **Direct real-GA projections**

    $$\Psi'_L={left_ga.latex(content="value")!s}.$$

    $$\Psi'_R={right_ga.latex(content="value")!s}.$$

    **Recovered from the projected columns**

    $$\Psi'_{{L,\mathrm{{back}}}}={recovered_left_ga.latex(content="value")!s}.$$

    $$\Psi'_{{R,\mathrm{{back}}}}={recovered_right_ga.latex(content="value")!s}.$$

    Coefficient residuals: left {left_roundtrip_residual:.2e}, right {right_roundtrip_residual:.2e}.
    Both routes produce the same real spinors, with $\Psi'_L+\Psi'_R=\Psi'$.
    """),
        ],
        gap=2,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. A change of coordinates must commute with the action

    Derive $T$ by converting each Dirac basis column through the public
    `.to_basis("weyl")` API. Since this change is unitary, $T^{-1}=T^\dagger$.

    $$M_W=T M_D T^{-1},\qquad \chi_W=T\chi_D,$$
    $$M_W\chi_W=T(M_D\chi_D).$$

    This works for the **whole Clifford action**, including the mixed operator,
    not only the Spin group. Switching the matrices but leaving the state in
    its old coordinates would be a different calculation.

    This statement concerns **equivalent** representations. Different simple
    components of a split Clifford algebra can give inequivalent representations;
    that is not repaired by a basis change. A single Weyl subspace is invariant
    under even operators, not the full odd Clifford action.
    """)
    return


@app.cell
def _(
    MatrixRepr,
    dirac_operator,
    dirac_result,
    gm,
    left_seed,
    matrix_panel,
    mo,
    np,
    sta,
):
    dirac_to_weyl = np.column_stack(
        [
            MatrixRepr(np.eye(4, dtype=complex)[:, _i : _i + 1], algebra=sta, mode="compact", basis="dirac", kind="ket")
            .to_basis("weyl")
            .mat[:, 0]
            for _i in range(4)
        ]
    )
    basis_change_matrix = MatrixRepr(dirac_to_weyl)
    weyl_operator = dirac_operator.to_basis("weyl")
    weyl_input = left_seed.to_basis("weyl")
    weyl_action = weyl_operator @ weyl_input
    converted_action = dirac_result.to_basis("weyl")
    basis_action_residual = float(np.linalg.norm(weyl_action.mat - converted_action.mat))
    np.testing.assert_allclose(dirac_to_weyl.conj().T @ dirac_to_weyl, np.eye(4), atol=1e-12)
    np.testing.assert_allclose(
        weyl_operator.mat, dirac_to_weyl @ dirac_operator.mat @ dirac_to_weyl.conj().T, atol=1e-12
    )
    np.testing.assert_allclose(weyl_action.mat, converted_action.mat, atol=1e-12)
    mo.vstack(
        [
            matrix_panel("Computed basis change", basis_change_matrix),
            mo.hstack(
                [
                    matrix_panel("Change basis, then act", weyl_action),
                    matrix_panel(
                        "Act, then change basis", converted_action, gm.md(t"""Residual: {basis_action_residual:.2e}.""")
                    ),
                ],
                wrap=True,
                gap=2,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Optional: even representatives and another ideal

    Back in $\mathrm{Cl}(3,0)$, write the ideal spinor as $\psi=\Psi f$ with
    **even** $\Psi=2\langle\psi\rangle_{\rm even}$. This is the convention used
    by the Pauli spinor-column conversion. An odd vector $v$ sends the ideal
    state to $v\psi$, but $v\Psi$ is odd and is not an even representative.
    Since $e_3f=f$, the corresponding even representative is $v\Psi e_3$.
    Thus a general $A=A_{\rm even}+A_{\rm odd}$ acts on this representative by

    $$\Psi\longmapsto A_{\rm even}\Psi+A_{\rm odd}\Psi e_3.$$

    The right-hand $e_3$ records the chosen identification. It does not change
    the underlying column action. Do not send the mixed-grade ideal element
    itself to `to_spinor_column`, which explicitly requires an even representative.

    What if we choose $g=(1-e_3)/2$ instead? The map $\psi\mapsto\psi e_1$
    moves this first-column ideal to the second-column ideal. It commutes with
    every left action: $(A\psi)e_1=A(\psi e_1)$. The embedding changes, not
    the operator represented on the two-component column.
    """)
    return


@app.cell
def _(
    e1,
    e2,
    e3,
    even_grades,
    f,
    gm,
    ideal_column,
    ideal_spinor,
    matrix_panel,
    mo,
    np,
    odd_grades,
    pauli,
    to_matrix,
    to_spinor_column,
):
    even_representative = 2 * even_grades(ideal_spinor)
    general_operator = 1 + 0.3 * e1 + 0.2 * (e1 ^ e2) + 0.4 * pauli.I
    pulled_action = (
        even_grades(general_operator) * even_representative + odd_grades(general_operator) * even_representative * e3
    )
    direct_column_action = to_matrix(general_operator, mode="compact") @ ideal_column(ideal_spinor)
    pulled_column_action = to_spinor_column(pulled_action)
    other_projector = (1 - e3) / 2
    other_ideal = ideal_spinor * e1
    other_ideal_matrix = to_matrix(other_ideal, mode="compact")
    np.testing.assert_allclose((even_representative * f).data, ideal_spinor.data, atol=1e-12)
    np.testing.assert_allclose((pulled_action * f).data, (general_operator * ideal_spinor).data, atol=1e-12)
    np.testing.assert_allclose(pulled_column_action.mat, direct_column_action.mat, atol=1e-12)
    np.testing.assert_allclose((other_ideal * other_projector).data, other_ideal.data, atol=1e-12)
    mo.vstack(
        [
            gm.md(rt"""
    $$\Psi={even_representative.latex(content="value")!s}.$$
    $$A={general_operator.latex(content="value")!s}.$$
    $$\Psi'={pulled_action.latex(content="value")!s}.$$
    """),
            mo.hstack(
                [
                    matrix_panel("Full matrix action", direct_column_action),
                    matrix_panel("Converted even representative", pulled_column_action),
                ],
                wrap=True,
                gap=2,
            ),
            matrix_panel("The original state in the other ideal", other_ideal_matrix),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What to take away

    - **Ideal, column, and even representative** are related realizations, not
      identical objects with identical multiplication rules.
    - The same group element has different actions on vectors and spinors.
    - A full Clifford action is linear and well defined but need not be a
      geometric symmetry or preserve chirality.
    - A consistent change of representation preserves the calculation.
    - Chiral projection is a real two-sided GA operation. Projected spinors
      roundtrip through columns even though projector matrices themselves are
      not matrices of single real Clifford elements.

    Further reading:

    - [Clifford Algebras and Spinors, slides 18–19](https://scipp.ucsc.edu/~haber/ph251/Clifford_Algebras_and_Spinors.pdf):
      the Pauli ideal/column and even-representative constructions.
    - [Lundholm and Svensson, sections 8–9](https://www.math.lmu.de/~lundholm/clifford.pdf):
      equivalent representations and spinor modules.
    - [Todorov, sections 2–4](https://arxiv.org/abs/1106.3197): Pin/Spin and Dirac/Weyl spinors.

    These examples do not classify degenerate Clifford algebras or identify
    chirality with helicity. Matrix chirality projectors here are lesson-local
    constructions, not new Galaga API methods.
    """)
    return


if __name__ == "__main__":
    app.run()
