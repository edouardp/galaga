"""Null pairs, boosts and complements: a non-diagonal metric is not a defect."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from galaga_matrix import MatrixRepr, from_matrix, to_matrix

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        BladeConvention,
        Name,
        complement,
        dual,
        exp,
        inverse,
        metric_inner_product,
        outer_product,
        presets,
        uncomplement,
    )

    return (
        Algebra,
        BladeConvention,
        MatrixRepr,
        Name,
        complement,
        dual,
        exp,
        from_matrix,
        gm,
        inverse,
        metric_inner_product,
        mo,
        np,
        outer_product,
        plt,
        presets,
        to_matrix,
        uncomplement,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Witt bases: solve problems with null coordinates

    **Problem A:** two light signals approach from opposite directions.
    What frequencies does a moving receiver measure? We will use one null
    pair to make the two Doppler factors appear directly as scalings.

    **Problem B:** represent a few fermionic modes on a computer. How do we
    add a particle, reject double occupancy, count particles and compute
    their energy without manually inventing sign-filled matrices? One Witt
    pair per mode will generate those operators and their matrices.

    These are two different interpretations of the same algebraic pattern,
    not a claim that fermionic modes are spacetime directions. First learn
    the small amount of metric vocabulary needed for both.

    A null vector has zero self-pairing. A radical vector is orthogonal to
    **every** vector. A metric is degenerate when its radical is nonzero.
    Those are different conditions.

    A real Witt pair obeys
    $$p^2=q^2=0,\qquad p\cdot q=1,\qquad pq+qp=2.$$
    Its Gram determinant is $-1$, not zero. Neither vector is in the radical.
    The normalization here is $p\cdot q=1$; texts using $1/2$ get a different
    Clifford anticommutator.
    """)
    return


@app.cell
def _(mo):
    pair_count = mo.ui.dropdown([1, 2, 3], value=2, label="Number of Witt pairs")
    rapidity_control = mo.ui.slider(-1.5, 1.5, step=0.1, value=0.7, label="Rapidity", show_value=True)
    return pair_count, rapidity_control


@app.cell
def _(make_witt_algebra, metric_inner_product, np, outer_product, pair_count):
    pairs = int(pair_count.value)
    witt = make_witt_algebra(pairs)
    null_vectors = witt.basis_vectors(expr=True)
    ps, qs = null_vectors[::2], null_vectors[1::2]
    assert not witt.is_degenerate
    for _i, _p in enumerate(ps):
        for _j, _q in enumerate(qs):
            assert metric_inner_product(_p, _q) == int(_i == _j)
        assert _p * _p == 0
    for _q in qs:
        assert _q * _q == 0
    computed_gram = np.array([[float(metric_inner_product(_a, _b)) for _b in null_vectors] for _a in null_vectors])
    np.testing.assert_array_equal(computed_gram, witt.gram)
    witt_volume = outer_product(*null_vectors)
    assert witt_volume == witt.I
    positive = tuple((_p + _q) / np.sqrt(2) for _p, _q in zip(ps, qs))
    negative = tuple((_p - _q) / np.sqrt(2) for _p, _q in zip(ps, qs))
    orthogonal_vectors = tuple(_v for _uv in zip(positive, negative) for _v in _uv)
    orthogonal_gram = np.array(
        [[float(metric_inner_product(_a, _b)) for _b in orthogonal_vectors] for _a in orthogonal_vectors]
    )
    np.testing.assert_allclose(orthogonal_gram, np.diag([1, -1] * pairs), rtol=0, atol=1e-12)
    return negative, null_vectors, pairs, positive, ps, qs, witt, witt_volume


@app.cell
def _(gm, mo, negative, pair_count, pairs, positive, witt, witt_volume):
    _plus, _minus = positive[0], negative[0]
    mo.vstack(
        [
            pair_count,
            gm.md(rt"""
    ## 1. The common tool: paired null directions

    {witt.bilinear_form_table():block}

    There are **{pairs}** positive and **{pairs}** negative directions, despite
    every displayed basis vector being null. With three pairs this is
    $\mathrm{{Cl}}(3,3)$, not Euclidean $\mathrm{{Cl}}(6,0)$: dimension alone
    does not determine a Clifford algebra.

    For each pair, recover orthogonal directions
    $u_i=(p_i+q_i)/\sqrt{{2}}$ and $v_i=(p_i-q_i)/\sqrt{{2}}$.
    Here the first two are

    $$u_1={_plus.latex(content="value")!s},\qquad v_1={_minus.latex(content="value")!s}.$$

    Their computed squares are $+1$ and $-1$. Conversely
    $p_i=(u_i+v_i)/\sqrt{{2}}$, $q_i=(u_i-v_i)/\sqrt{{2}}$.

    The chosen native order is $(p_1,q_1,p_2,q_2,\ldots)$ and defines

    $$I={witt_volume.latex(content="value")!s}.$$

    No independent sign setting is needed. Moving to a different ordered basis
    changes its volume by the determinant of the basis map.

    One pair suffices for the receiver problem below. The pair-count selector
    will also set the number of independent fermionic modes in Problem B.
    """),
        ]
    )
    return


@app.cell
def _(gm, metric_inner_product, null_vectors, ps, qs):
    reciprocal_vectors = tuple(_v for _qp in zip(qs, ps) for _v in _qp)
    for _i, _a in enumerate(null_vectors):
        for _j, _b in enumerate(reciprocal_vectors):
            assert metric_inner_product(_a, _b) == int(_i == _j)
    _sample = 2 * ps[0] + 3 * qs[0]
    _p_coordinate = metric_inner_product(_sample, qs[0])
    _q_coordinate = metric_inner_product(_sample, ps[0])
    gm.md(rt"""
    ## 2. Reciprocal vectors are already in the basis

    The reciprocal of $p_i$ is $q_i$, and conversely. For $x=ap_i+bq_i$,
    $a=x\cdot q_i$ and $b=x\cdot p_i$, **not** $x\cdot p_i$ and $x\cdot q_i$.

    For $x={_sample.latex(content="value")!s}$, the recovered coordinates are
    ${_p_coordinate.latex(content="value")!s}$ and ${_q_coordinate.latex(content="value")!s}$.

    The span of all the $p_i$ is totally isotropic: its internal pairings vanish.
    It is not the radical of the whole space, because the $q_i$ detect it.
    This is the algebraic pattern behind $V\oplus V^*$: pairing vectors with
    covectors, with a choice of normalization. Our example is linear algebra,
    not an implementation of generalized geometry.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Problem A: a receiver moving between two light signals

    Work in one space and one time dimension, with $c=1$. Define a unit
    time direction $u=(p_1+q_1)/\sqrt2$ and space direction
    $s=(p_1-q_1)/\sqrt2$. In the laboratory, two equal-frequency light signals
    have wavevectors $k_\rightarrow=u+s=\sqrt2p_1$ and
    $k_\leftarrow=u-s=\sqrt2q_1$; laboratory frequency is our unit.

    An observer with velocity $v=\tanh\eta$ has unit future time direction
    $U=\cosh\eta\,u+\sinh\eta\,s$. Its measured frequency is $k\cdot U$.
    Before calculating: moving right should redshift the right-going signal
    being chased and blueshift the left-going signal met head-on.

    Let $K=p_1\wedge q_1$. Because $p_1q_1$ also has scalar part $1$,
    **do not** replace this wedge by a geometric product.
    Computation gives $K^2=+1$, so
    $R=\exp(-\eta K/2)=\cosh(\eta/2)-K\sinh(\eta/2)$.

    With this sign, $U=\widetilde R uR$, whereas $Rk\widetilde R$ expresses
    the fixed signal in the receiver frame. Distinguish changing the observer
    from actively changing the signal. The null coordinates scale as
    $p_1\mapsto e^{-\eta}p_1$, $q_1\mapsto e^\eta q_1$.
    No hyperbolic mixing of two coordinates is needed.
    """)
    return


@app.cell
def _(exp, np, ps, qs, rapidity_control):
    rapidity = rapidity_control.value
    boost_plane = ps[0] ^ qs[0]
    boost = exp(-rapidity * boost_plane / 2)
    boosted_p = boost * ps[0] * ~boost
    boosted_q = boost * qs[0] * ~boost
    boosted_sample = boost * (ps[0] + qs[0]) * ~boost
    assert boost_plane * boost_plane == 1
    np.testing.assert_allclose(boosted_p.data, (np.exp(-rapidity) * ps[0]).data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(boosted_q.data, (np.exp(rapidity) * qs[0]).data, rtol=0, atol=1e-12)
    np.testing.assert_allclose((boosted_sample * boosted_sample).data, ps[0].algebra.scalar(2).data, atol=1e-12)
    return boost, boost_plane, boosted_sample


@app.cell
def _(boost, metric_inner_product, negative, np, positive, rapidity_control):
    lab_time, lab_space = positive[0], negative[0]
    receiver_velocity = np.tanh(rapidity_control.value)
    receiver_time = ~boost * lab_time * boost
    right_signal, left_signal = lab_time + lab_space, lab_time - lab_space
    right_frequency = float(metric_inner_product(right_signal, receiver_time))
    left_frequency = float(metric_inner_product(left_signal, receiver_time))
    np.testing.assert_allclose((receiver_time * receiver_time).data, lab_time.algebra.identity.data, atol=1e-12)
    np.testing.assert_allclose(right_frequency, np.sqrt((1 - receiver_velocity) / (1 + receiver_velocity)), atol=1e-12)
    np.testing.assert_allclose(left_frequency, np.sqrt((1 + receiver_velocity) / (1 - receiver_velocity)), atol=1e-12)
    return left_frequency, receiver_velocity, right_frequency


@app.cell
def _(
    boost,
    boost_plane,
    boosted_sample,
    gm,
    left_frequency,
    mo,
    plot_null_boost,
    ps,
    qs,
    rapidity_control,
    receiver_velocity,
    right_frequency,
):
    mo.vstack(
        [
            rapidity_control,
            gm.md(rt"""
    **Construct the plane by wedging the named null vectors**

    {boost_plane:expr}

    $$R={boost.latex(content="value")!s}.$$

    $$R(p_1+q_1)\widetilde R={boosted_sample.latex(content="value")!s}.$$

    **Receiver speed:** $v/c={receiver_velocity:.4f}$.
    **Measured frequencies / laboratory frequency:**
    right-going **{right_frequency:.4f}**, left-going **{left_frequency:.4f}**.

    At $\eta=0$ both are one. Reverse the sign of the slider to exchange
    redshift and blueshift. The factors multiply to one: these two equal
    laboratory signals are scaled reciprocally, not attenuated together.

    The plot underneath shows that reciprocal scaling. Its axes are null
    coordinates and its invariant is $2xy=2$; it is not a Euclidean picture
    of the light rays.
    """),
            plot_null_boost(boosted_sample, ps[0], qs[0]),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Problem B: build an occupation-state simulator

    A fermionic mode is either empty or occupied. With $m$ modes there are
    $2^m$ occupation states. We need an operator that adds a particle but
    returns zero if that mode is already occupied, an operator that removes
    it, and a number operator with eigenvalues $0$ and $1$.

    Null pairs give precisely these rules. Set
    $a_i=p_i/\sqrt2$, $c_i=q_i/\sqrt2$; then
    $$a_i c_j+c_j a_i=\delta_{ij},\qquad
      a_i a_j+a_j a_i=c_i c_j+c_j c_i=0.$$
    In the occupation basis constructed below, $c_i$ is the matrix adjoint
    of $a_i$. It is **not** its Clifford reverse. We choose the usual positive
    inner product on occupation columns; the indefinite Clifford metric
    is not the quantum probability norm.

    Start by constructing the empty-state projector in one mode:

    In one pair, $p^2=q^2=0$, but $f=pq/2$ satisfies $f^2=f$.
    Moreover, $pf=0$, $qf=q$, and $p(qf)=2f$. After normalization these
    are the unnormalized creation/annihilation relations. Here $f$ is the
    empty state as an ideal element, not a scalar identity. A number operator
    is instead $ca=qp/2$.

    Below are a small full metric table and the compact matrix of $f$.
    The basis matrices square to zero; their anticommutator is $2$ times
    the matrix identity. The projector survives a matrix-to-GA roundtrip.
    """)
    return


@app.cell
def _(from_matrix, gm, make_witt_algebra, mo, np, to_matrix):
    one_pair = make_witt_algebra(1)
    p, q = one_pair.basis_vectors()
    projector = p * q / 2
    assert projector * projector == projector
    assert p * projector == 0 and q * projector == q
    assert p * (q * projector) == 2 * projector
    p_matrix = to_matrix(p, mode="compact")
    q_matrix = to_matrix(q, mode="compact")
    projector_matrix = to_matrix(projector, mode="compact")
    np.testing.assert_allclose(p_matrix.mat @ p_matrix.mat, 0, atol=1e-12)
    np.testing.assert_allclose(q_matrix.mat @ q_matrix.mat, 0, atol=1e-12)
    np.testing.assert_allclose(
        p_matrix.mat @ q_matrix.mat + q_matrix.mat @ p_matrix.mat, 2 * np.eye(p_matrix.shape[0]), atol=1e-12
    )
    np.testing.assert_allclose(from_matrix(projector_matrix).data, projector.data, atol=1e-12)
    mo.vstack(
        [
            gm.md(rt"""
    $$f={projector.latex(content="value")!s}.$$

    {one_pair.bilinear_form_table(full=True):block}

    {projector_matrix:block}
    """)
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### From a projector to useful state transitions

    For $m$ modes, form $F=\prod_i a_i c_i$ and use the basis
    $$|n_1\cdots n_m\rangle=c_1^{n_1}\cdots c_m^{n_m}F.$$
    These are multivectors in a left ideal: operators act on the **left**,
    not by a rotor sandwich. Each mode's number operator is $N_i=c_i a_i$.
    Choose independent mode energies $\epsilon_i=i$ in arbitrary units;
    $H=\sum_i\epsilon_i N_i$ assigns an energy to each occupation state.

    Try creating a particle in an occupied mode: the result is the zero
    vector, not the vacuum state. For two or more modes, compare creating
    in mode 2 from occupations 00 and 10. The second action has a minus
    sign because creation operators anticommute. Our written state order
    fixes that sign convention.

    The matrix below is computed from each operator's action on the ideal
    basis. It is in **occupation coordinates**, not necessarily the compact
    matrix basis used above. Basis order is listed explicitly; the leftmost
    bit is mode 1 and changes fastest. With three pairs this yields eight
    states in $\mathrm{Cl}(3,3)$.

    This is a finite real operator model, not a spin-statistics derivation
    or a simulation of complex quantum time evolution.
    """)
    return


@app.cell
def _(np, occupation_action_matrix, pairs, ps, qs, witt):
    annihilators = tuple(_p / np.sqrt(2) for _p in ps)
    creators = tuple(_q / np.sqrt(2) for _q in qs)
    vacuum = witt.identity
    for _a, _c in zip(annihilators, creators):
        vacuum = vacuum * (_a * _c)
    np.testing.assert_allclose((vacuum * vacuum).data, vacuum.data, atol=1e-12)
    occupation_states = []
    for _mask in range(1 << pairs):
        _state = vacuum
        for _i in reversed(range(pairs)):
            if _mask & (1 << _i):
                _state = creators[_i] * _state
        occupation_states.append(_state)
    occupation_states = tuple(occupation_states)
    occupation_labels = tuple("".join(str((_mask >> _i) & 1) for _i in range(pairs)) for _mask in range(1 << pairs))
    number_operators = tuple(_c * _a for _c, _a in zip(creators, annihilators))
    mode_energies = tuple(range(1, pairs + 1))
    hamiltonian = sum((_e * _n for _e, _n in zip(mode_energies, number_operators)), witt.scalar(0))
    energy_matrix = occupation_action_matrix(hamiltonian, occupation_states)
    for _a, _c in zip(annihilators, creators):
        _A = occupation_action_matrix(_a, occupation_states)
        _C = occupation_action_matrix(_c, occupation_states)
        np.testing.assert_allclose(_A.T, _C, rtol=0, atol=1e-12)
    return (
        annihilators,
        creators,
        energy_matrix,
        number_operators,
        occupation_labels,
        occupation_states,
    )


@app.cell
def _(mo, occupation_labels, pairs):
    occupation_control = mo.ui.dropdown(
        list(occupation_labels), value=occupation_labels[1 if pairs > 1 else 0], label="Input occupation"
    )
    mode_control = mo.ui.dropdown(list(range(1, pairs + 1)), value=2 if pairs > 1 else 1, label="Mode")
    action_control = mo.ui.dropdown(["Create", "Annihilate", "Count"], value="Create", label="Action")
    return action_control, mode_control, occupation_control


@app.cell
def _(
    action_control,
    annihilators,
    creators,
    energy_matrix,
    mode_control,
    np,
    number_operators,
    occupation_action_matrix,
    occupation_control,
    occupation_labels,
    occupation_states,
):
    input_index = occupation_labels.index(occupation_control.value)
    selected_mode = int(mode_control.value) - 1
    selected_action = {"Create": creators, "Annihilate": annihilators, "Count": number_operators}[action_control.value][
        selected_mode
    ]
    action_matrix = occupation_action_matrix(selected_action, occupation_states)
    action_column = action_matrix[:, input_index : input_index + 1]
    action_state = selected_action * occupation_states[input_index]
    np.testing.assert_allclose(
        np.column_stack([_state.data for _state in occupation_states]) @ action_column[:, 0],
        action_state.data,
        rtol=0,
        atol=1e-12,
    )
    input_energy = float(energy_matrix[input_index, input_index])
    _nonzero = np.flatnonzero(np.abs(action_column[:, 0]) > 1e-10)
    if len(_nonzero):
        _target = int(_nonzero[0])
        transition_description = (
            ("+" if action_column[_target, 0] > 0 else "-") + "|" + occupation_labels[_target] + ">"
        )
    else:
        transition_description = "zero vector: no surviving state (not the vacuum)"
    return action_column, action_matrix, input_energy, transition_description


@app.cell
def _(
    MatrixRepr,
    action_column,
    action_control,
    action_matrix,
    gm,
    input_energy,
    mo,
    mode_control,
    occupation_control,
    occupation_labels,
    pair_count,
    transition_description,
):
    _basis_order = ", ".join("|" + _bits + ">" for _bits in occupation_labels)
    mo.vstack(
        [
            mo.hstack([pair_count, occupation_control, mode_control, action_control], wrap=True),
            gm.md(t"""
    **Computed transition:** {transition_description}.
    The input state has energy **{input_energy:g}** in the chosen units.

    **Row/column basis order:** {_basis_order}.

    **Action matrix in occupation coordinates**

    {MatrixRepr(action_matrix):block}

    **Resulting occupation column**

    {MatrixRepr(action_column):block}
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. When this machinery applies—and when it does not

    CGA adds one null pair to a Euclidean subspace, with
    $e_o\cdot e_\infty=-1$ in the default preset. Setting $p=e_o$ and
    $q=-e_\infty$ gives our normalized Witt pair, **including the minus sign**.
    Its metric is nondegenerate, so its native pseudoscalar is invertible.

    PGA instead has a radical direction: its null vector pairs to zero
    with every basis vector. Its pseudoscalar is not invertible.
    Galaga's `dual` therefore rejects PGA. The metric-independent
    `complement`/`uncomplement` remain available and underpin its regressive
    product. They depend on the chosen ordered exterior basis.

    For each **native basis blade with coefficient $+1$** $A$,
    $A\wedge\operatorname{complement}(A)=I$. This formula is not asserted
    for arbitrary scaled blades. Do not silently replace every operation
    called "dual" with a complement: conventions and signs matter.
    """)
    return


@app.cell
def _(
    Algebra,
    complement,
    dual,
    gm,
    inverse,
    metric_inner_product,
    mo,
    np,
    outer_product,
    presets,
    uncomplement,
):
    cga = Algebra(config=presets.cga(2))
    pga = Algebra(config=presets.pga(2))
    _eo, _einf = cga.blade("origin"), cga.blade("infinity")
    assert metric_inner_product(_eo, -_einf) == 1
    assert not cga.is_degenerate and pga.is_degenerate
    cga_square, pga_square = cga.I * cga.I, pga.I * pga.I
    np.testing.assert_allclose((cga.I * inverse(cga.I)).data, cga.identity.data, atol=1e-12)
    assert pga_square == 0
    dual_error = ""
    try:
        dual(pga.basis_vectors()[0])
    except ValueError as _error:
        dual_error = str(_error)
    assert "invertible pseudoscalar" in dual_error
    for _alg in (cga, pga):
        assert outer_product(*_alg.basis_vectors()) == _alg.I
        for _mask in _alg.display_order:
            _blade = _alg.blade(_mask)
            assert _blade ^ complement(_blade) == _alg.I
            assert uncomplement(complement(_blade)) == _blade
    _radical = pga.basis_vectors()[-1]
    assert all(metric_inner_product(_radical, _v) == 0 for _v in pga.basis_vectors())
    mo.vstack(
        [
            gm.md(rt"""
    **CGA: null vectors, nondegenerate metric**

    {cga.bilinear_form_table():block}

    $$I_{{CGA}}^2={cga_square.latex(content="value")!s}.$$
    """),
            gm.md(rt"""
    **PGA: a radical direction, degenerate metric**

    {pga.bilinear_form_table():block}

    $$I_{{PGA}}^2={pga_square.latex(content="value")!s}.$$

    Attempting `dual` reports: **{dual_error}**.
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways and further reading

    Count positive, negative and radical directions—not zero diagonal
    entries. Reciprocal pairing, boosts, nilpotents and complements all
    follow from the same Gram matrix and ordered exterior basis.
    A general real nondegenerate signature $(p,q)$ admits $\min(p,q)$
    hyperbolic pairs plus an unpaired definite subspace; only split signature
    can be made entirely from such pairs.

    For the bilinear hyperbolic-plane construction and Witt decomposition,
    see [Elman, Karpenko and Merkurjev, *The Algebraic and Geometric Theory
    of Quadratic Forms*, Chapter I](https://www.math.ucla.edu/~rse/book/Kniga.pdf).
    Read their bilinear convention separately from their quadratic-form
    polarization convention to avoid factors of two.

    The receiver calculation is a one-dimensional specialization of
    [Einstein's Doppler calculation, Section 7](https://fourmilab.ch/etexts/einstein/specrel/www/).
    For why fermionic state models use anticommuting creation and annihilation
    operators, see [David Tong's QFT notes, Section 5](https://www.damtp.cam.ac.uk/user/tong/qft/qfthtml/S5.html).
    Here we construct a small finite-mode representation of those relations;
    we do not infer quantum probabilities from the Clifford metric.

    Continue with [the CGA orientation lesson](../cga/basis_order_and_orientation.py)
    and [4D rotations](four_dimensional_rotor_planes.py).

    ## Appendix: construction and plotting

    The following helper labels native wedges; it does not implement
    Clifford products or add a preset. Plotting extracts null coordinates
    using reciprocal pairings.
    """)
    return


@app.cell(hide_code=True)
def _(Algebra, BladeConvention, Name, np):
    def make_witt_algebra(count):
        gram = np.kron(np.eye(count), np.array([[0, 1], [1, 0]]))
        vector_names = [
            Name(f"{letter}{i}", latex=f"{letter}_{{{i}}}") for i in range(1, count + 1) for letter in ("p", "q")
        ]
        labels = []
        for mask in range(1 << (2 * count)):
            factors = [name for i, name in enumerate(vector_names) if mask & (1 << i)]
            labels.append(
                Name(
                    "^".join(name.ascii for name in factors) or "1",
                    latex=r"\wedge ".join(name.latex for name in factors) or "1",
                )
            )
        return Algebra(gram=gram, blades=BladeConvention(2 * count, labels))

    return (make_witt_algebra,)


@app.cell(hide_code=True)
def _(np):
    def occupation_action_matrix(operator, states):
        """Express left multiplication in the explicitly constructed ideal basis."""
        basis = np.column_stack([state.data for state in states])
        images = np.column_stack([(operator * state).data for state in states])
        matrix, _, rank, _ = np.linalg.lstsq(basis, images, rcond=None)
        assert rank == len(states)
        np.testing.assert_allclose(basis @ matrix, images, rtol=0, atol=1e-12)
        return matrix

    return (occupation_action_matrix,)


@app.cell(hide_code=True)
def _(metric_inner_product, np, plt):
    def plot_null_boost(value, p_axis, q_axis):
        x = float(metric_inner_product(value, q_axis))
        y = float(metric_inner_product(value, p_axis))
        fig, ax = plt.subplots(figsize=(5, 4))
        grid = np.linspace(0.18, 5, 250)
        ax.plot(grid, 1 / grid, label=r"$2xy=2$")
        ax.scatter([1, x], [1, y], color=["grey", "tab:orange"])
        ax.annotate("start", (1, 1))
        ax.annotate("boosted", (x, y))
        ax.set(xlabel="p coordinate", ylabel="q coordinate", xlim=(0, 5), ylim=(0, 5))
        ax.legend()
        fig.tight_layout()
        plt.close(fig)
        return fig

    return (plot_null_boost,)


if __name__ == "__main__":
    app.run()
