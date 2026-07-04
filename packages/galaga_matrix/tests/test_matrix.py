"""Tests for galaga_matrix."""

import numpy as np
import pytest
from galaga_matrix import MatrixRepr, from_matrix, to_matrix
from galaga_matrix.matrix import (
    Quat,
    _classify,
    _quaternion_block_basis,
    _spinor_roundtrip_possible,
    compact_basis,
    to_quaternion_matrix,
)

from galaga import Algebra
from galaga.algebra import Multivector

# ── Left-regular representation ──


class TestLeftRegular:
    def test_scalar_is_identity(self):
        alg = Algebra(2)
        s = alg.scalar(3.0)
        mat = to_matrix(s)
        assert np.allclose(mat, 3.0 * np.eye(4))

    def test_roundtrip_vector(self):
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        v = 2 * e1 + 3 * e2 - e3
        mat = to_matrix(v)
        v2 = from_matrix(alg, mat)
        assert np.allclose(v.data, v2.data)

    def test_roundtrip_general_mv(self):
        alg = Algebra(3)
        np.random.seed(42)
        data = np.random.randn(alg.dim)
        mv = Multivector(alg, data)
        mat = to_matrix(mv)
        mv2 = from_matrix(alg, mat)
        assert np.allclose(mv.data, mv2.data)

    def test_product_is_matrix_product(self):
        """L(a*b) = L(a) @ L(b)."""
        alg = Algebra(2, 1)
        e = alg.basis_vectors()
        a = e[0] + 2 * e[1]
        b = 3 * e[0] - e[2]
        from galaga.algebra import gp

        mat_ab = to_matrix(gp(a, b))
        mat_a = to_matrix(a)
        mat_b = to_matrix(b)
        assert np.allclose(mat_ab, mat_a @ mat_b)

    def test_shape(self):
        alg = Algebra(4)
        e = alg.basis_vectors()
        mat = to_matrix(e[0])
        assert mat.shape == (16, 16)

    def test_wrong_shape_raises(self):
        alg = Algebra(2)
        with pytest.raises(ValueError, match="Expected"):
            from_matrix(alg, np.eye(3))

    def test_sta(self):
        sta = Algebra(1, 3)
        sta.basis_vectors()
        np.random.seed(7)
        data = np.random.randn(sta.dim)
        mv = Multivector(sta, data)
        mv2 = from_matrix(sta, to_matrix(mv))
        assert np.allclose(mv.data, mv2.data)


# ── Compact representation: Clifford relations ──


class TestCompactCliffordRelations:
    """Verify γᵢ² = sig(i)*I and {γᵢ, γⱼ} = 0 for all non-degenerate algebras."""

    @pytest.mark.parametrize(
        "p,q",
        [(p, q) for p in range(6) for q in range(6) if 0 < p + q <= 8],
    )
    def test_clifford_relations(self, p, q):
        alg = Algebra(p, q)
        gammas = compact_basis(alg)
        k = gammas[0].shape[0]
        I_k = np.eye(k, dtype=complex)

        for i, g in enumerate(gammas):
            assert np.allclose(g @ g, alg.signature[i] * I_k), f"γ[{i}]² != {alg.signature[i]}*I in Cl({p},{q})"

        for i in range(len(gammas)):
            for j in range(i + 1, len(gammas)):
                ac = gammas[i] @ gammas[j] + gammas[j] @ gammas[i]
                assert np.allclose(ac, 0), f"{{γ[{i}], γ[{j}]}} != 0 in Cl({p},{q})"


# ── Compact: Pauli ──


class TestPauli:
    def test_cl30_pauli_matrices(self):
        alg = Algebra(3)
        gammas = compact_basis(alg)
        assert len(gammas) == 3
        assert gammas[0].shape == (2, 2)
        # σ₁
        assert np.allclose(gammas[0], [[0, 1], [1, 0]])
        # σ₂
        assert np.allclose(gammas[1], [[0, -1j], [1j, 0]])
        # σ₃
        assert np.allclose(gammas[2], [[1, 0], [0, -1]])

    def test_cl03_squares_to_minus_identity(self):
        alg = Algebra(0, 3)
        gammas = compact_basis(alg)
        I2 = np.eye(2, dtype=complex)
        for g in gammas:
            assert np.allclose(g @ g, -I2)


# ── Compact: Dirac ──


class TestDirac:
    def test_cl13_dirac_matrices(self):
        sta = Algebra(1, 3)
        gammas = compact_basis(sta)
        assert len(gammas) == 4
        assert gammas[0].shape == (4, 4)
        I4 = np.eye(4, dtype=complex)
        # γ⁰² = +I (timelike)
        assert np.allclose(gammas[0] @ gammas[0], I4)
        # γⁱ² = -I (spacelike)
        for i in range(1, 4):
            assert np.allclose(gammas[i] @ gammas[i], -I4)

    def test_cl31_dirac_matrices(self):
        alg = Algebra(3, 1)
        gammas = compact_basis(alg)
        I4 = np.eye(4, dtype=complex)
        # First 3 square to +I, last squares to -I
        for i in range(3):
            assert np.allclose(gammas[i] @ gammas[i], I4)
        assert np.allclose(gammas[3] @ gammas[3], -I4)


# ── Compact: roundtrip ──


class TestCompactRoundtrip:
    """Roundtrip works for simple algebras (not A⊕A types)."""

    @pytest.mark.parametrize(
        "p,q",
        [(p, q) for p in range(6) for q in range(6) if 0 < p + q <= 8 and "+" not in _classify(p, q)[0]],
    )
    def test_roundtrip(self, p, q):
        alg = Algebra(p, q)
        np.random.seed(42)
        data = np.random.randn(alg.dim)
        mv = Multivector(alg, data)
        mat = to_matrix(mv, mode="compact")
        mv2 = from_matrix(alg, mat, mode="compact")
        assert np.allclose(mv.data, mv2.data, atol=1e-10), f"Roundtrip failed for Cl({p},{q})"

    def test_compact_product_is_matrix_product(self):
        """Compact representation is an algebra homomorphism."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        a = e1 + 2 * e2
        b = 3 * e1 - e3
        from galaga.algebra import gp

        mat_ab = to_matrix(gp(a, b), mode="compact")
        mat_a = to_matrix(a, mode="compact")
        mat_b = to_matrix(b, mode="compact")
        assert np.allclose(mat_ab, mat_a @ mat_b)

    def test_double_algebra_compact_inverse_raises(self):
        """Compact one-summand representations cannot be inverted uniquely."""
        alg = Algebra(0, 3)
        mv = alg.scalar(1.0)

        with pytest.raises(TypeError, match="not injective"):
            from_matrix(alg, to_matrix(mv, mode="compact"), mode="compact")

    def test_compact_inverse_rejects_matrix_outside_image(self):
        """Quaternionic compact images are proper real subalgebras of M(2k,C)."""
        sta = Algebra(1, 3)
        mat = np.zeros((4, 4), dtype=complex)
        mat[0, 1] = 1.0

        with pytest.raises(ValueError, match="not in the image"):
            from_matrix(sta, mat, mode="compact")

    def test_compact_inverse_wrong_shape_raises(self):
        alg = Algebra(3)

        with pytest.raises(ValueError, match="Expected"):
            from_matrix(alg, np.eye(3, dtype=complex), mode="compact")

    def test_compact_inverse_degenerate_raises(self):
        alg = Algebra(2, 0, 1)

        with pytest.raises(NotImplementedError, match="degenerate"):
            from_matrix(alg, np.eye(4, dtype=complex), mode="compact")

    def test_scalar_algebra_compact_roundtrip(self):
        """Cl(0,0) has a 1x1 compact representation."""
        alg = Algebra(0, 0)
        mv = alg.scalar(3.0)

        mat = to_matrix(mv, mode="compact")
        mv2 = from_matrix(alg, mat, mode="compact")

        assert mat.shape == (1, 1)
        assert np.allclose(mv.data, mv2.data)


# ── Classification ──


class TestClassify:
    def test_cl30_is_quaternion_plus(self):
        # Cl(3,0): s = (0-3) mod 8 = 5 → complex
        # Wait: Cl(3,0) ≅ M(2,ℂ) — that's complex, not quat+quat
        etype, dim = _classify(3, 0)
        assert "+" not in etype

    def test_cl03_is_double(self):
        # Cl(0,3) ≅ ℍ ⊕ ℍ: s = (3-0) mod 8 = 3 → quat+quat
        etype, dim = _classify(0, 3)
        assert etype == "quaternion+quaternion"

    def test_cl13_is_simple(self):
        etype, dim = _classify(1, 3)
        assert "+" not in etype


# ── Degenerate algebra ──


class TestDegenerate:
    def test_left_regular_works(self):
        alg = Algebra(2, 0, 1)  # PGA
        e = alg.basis_vectors()
        v = e[0] + e[1]
        mat = to_matrix(v)
        v2 = from_matrix(alg, mat)
        assert np.allclose(v.data, v2.data)

    def test_compact_raises(self):
        alg = Algebra(2, 0, 1)
        e = alg.basis_vectors()
        with pytest.raises(NotImplementedError, match="degenerate"):
            to_matrix(e[0], mode="compact")


# ── Invalid mode ──


class TestInvalidMode:
    def test_to_matrix_bad_mode(self):
        alg = Algebra(2)
        with pytest.raises(ValueError, match="Unknown mode"):
            to_matrix(alg.basis_vectors()[0], mode="bad")

    def test_from_matrix_bad_mode(self):
        alg = Algebra(2)
        with pytest.raises(ValueError, match="Unknown mode"):
            from_matrix(alg, np.eye(4), mode="bad")


# ── MatrixRepr rendering ──


class TestMatrixRepr:
    def test_latex_raw(self):
        mat = np.array([[1, 0], [0, -1]], dtype=complex)
        mr = MatrixRepr(mat)
        latex = mr.latex()
        assert r"\begin{pmatrix}" in latex
        assert r"\end{pmatrix}" in latex

    def test_latex_with_label(self):
        mat = np.eye(2, dtype=complex)
        mr = MatrixRepr(mat, label=r"\sigma_1")
        latex = mr.latex()
        assert r"\sigma_1 = " in latex

    def test_latex_inline_wrap(self):
        mat = np.eye(2, dtype=complex)
        mr = MatrixRepr(mat)
        assert mr.latex(wrap="$").startswith("$")
        assert mr.latex(wrap="$").endswith("$")

    def test_latex_display_wrap(self):
        mat = np.eye(2, dtype=complex)
        mr = MatrixRepr(mat)
        assert mr.latex(wrap="$$").startswith("$$")

    def test_repr_latex(self):
        mat = np.eye(2, dtype=complex)
        mr = MatrixRepr(mat)
        assert mr._repr_latex_().startswith("$")

    def test_complex_formatting(self):
        mat = np.array([[1 + 2j]], dtype=complex)
        mr = MatrixRepr(mat)
        latex = mr.latex()
        assert "i" in latex

    def test_real_formatting(self):
        mat = np.array([[3.0 + 0j]], dtype=complex)
        mr = MatrixRepr(mat)
        latex = mr.latex()
        assert "3" in latex
        # The cell content should be just "3", no imaginary part
        assert "3\n" in latex

    def test_neg_unit_imag_formatting(self):
        mat = np.array([[-1j]], dtype=complex)
        mr = MatrixRepr(mat)
        assert "-i" in mr.latex()
        assert "-1i" not in mr.latex()

    def test_array_protocol(self):
        mat = np.array([[1, 2], [3, 4]], dtype=complex)
        mr = MatrixRepr(mat)
        assert np.array_equal(np.array(mr), mat)

    def test_array_dtype_conversion(self):
        mat = np.array([[1, 0], [0, 1]], dtype=complex)
        mr = MatrixRepr(mat)
        result = np.array(mr, dtype=float)
        assert result.dtype == float

    def test_asarray(self):
        mat = np.array([[1 + 2j]], dtype=complex)
        mr = MatrixRepr(mat)
        assert np.array_equal(np.asarray(mr), mat)

    def test_numpy_functions(self):
        mat = np.array([[1, 2], [3, 4]], dtype=complex)
        mr = MatrixRepr(mat)
        assert np.trace(mr) == 5
        assert np.allclose(np.linalg.det(mr), -2)

    def test_mv_roundtrip_compact(self):
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        v = 2 * e1 + 3 * e2 - e3
        mr = MatrixRepr(to_matrix(v, mode="compact"), algebra=alg, mode="compact")
        assert np.allclose(mr.mv.data, v.data)

    def test_mv_roundtrip_left_regular(self):
        alg = Algebra(2)
        e1, e2 = alg.basis_vectors()
        v = e1 + 4 * e2
        mr = MatrixRepr(to_matrix(v, mode="left-regular"), algebra=alg, mode="left-regular")
        assert np.allclose(mr.mv.data, v.data)

    def test_mv_no_algebra_raises(self):
        mr = MatrixRepr(np.eye(2, dtype=complex))
        with pytest.raises(ValueError, match="No algebra"):
            _ = mr.mv


# ── Quaternion matrix form ──


class TestQuaternionMatrix:
    def test_sta_gamma0_is_real_diagonal(self):
        sta = Algebra(1, 3)
        g0 = sta.basis_vectors()[0]
        qm = to_quaternion_matrix(g0)
        assert len(qm) == 2
        assert qm[0][0].a == pytest.approx(1)
        assert qm[1][1].a == pytest.approx(-1)
        # Off-diagonal should be zero
        assert abs(qm[0][1].a) < 1e-12
        assert abs(qm[1][0].a) < 1e-12

    def test_sta_is_2x2(self):
        sta = Algebra(1, 3)
        g1 = sta.basis_vectors()[1]
        qm = to_quaternion_matrix(g1)
        assert len(qm) == 2
        assert len(qm[0]) == 2

    def test_sta_spatial_gamma_uses_quaternion_block_unit(self):
        """Cl(1,3) quaternion matrix form uses real M(2,H) blocks."""
        sta = Algebra(1, 3)
        g1 = sta.basis_vectors()[1]
        qm = to_quaternion_matrix(g1)

        assert qm[0][0] == Quat(0)
        assert qm[1][1] == Quat(0)
        assert qm[0][1] == Quat(0, 1, 0, 0)
        assert qm[1][0] == Quat(0, 1, 0, 0)

    def test_sta_quaternion_block_basis_clifford_relations(self):
        """The explicit Cl(1,3) M(2,H) basis satisfies the Clifford relations."""
        sta = Algebra(1, 3)
        gammas = _quaternion_block_basis(sta)
        I4 = np.eye(4, dtype=complex)

        assert np.allclose(gammas[0] @ gammas[0], I4)
        for g in gammas[1:]:
            assert np.allclose(g @ g, -I4)

        for i in range(len(gammas)):
            for j in range(i + 1, len(gammas)):
                assert np.allclose(gammas[i] @ gammas[j] + gammas[j] @ gammas[i], 0)

    def test_cl02_is_1x1(self):
        alg = Algebra(0, 2)
        e1 = alg.basis_vectors()[0]
        qm = to_quaternion_matrix(e1)
        assert len(qm) == 1
        assert len(qm[0]) == 1
        # e1 in Cl(0,2) should be pure imaginary quaternion
        q = qm[0][0]
        assert abs(q.a) < 1e-12
        assert abs(q.b) - 1 < 1e-12 or abs(q.c) - 1 < 1e-12 or abs(q.d) - 1 < 1e-12

    def test_non_quaternionic_raises(self):
        cl3 = Algebra(3)
        with pytest.raises(TypeError, match="not quaternionic"):
            to_quaternion_matrix(cl3.basis_vectors()[0])

    def test_quaternionic_double_algebra_raises(self):
        alg = Algebra(0, 3)
        with pytest.raises(TypeError, match="not a single quaternionic matrix algebra"):
            to_quaternion_matrix(alg.scalar(1.0))

    def test_unsupported_quaternionic_block_basis_raises(self):
        alg = Algebra(4, 0)

        with pytest.raises(TypeError, match="not implemented"):
            to_quaternion_matrix(alg.scalar(1.0))

    def test_quat_latex(self):
        q = Quat(1, 0, -1, 0)
        assert q.latex() == "1-j"

    def test_quat_repr(self):
        q = Quat(0, 0, 0, 1)
        assert repr(q) == "k"

    def test_quat_zero(self):
        q = Quat(0, 0, 0, 0)
        assert q.latex() == "0"


# ── Spinor (column vector) representation ──


class TestSpinorMatrix:
    """Tests for to_spinor_matrix and from_spinor_matrix."""

    def test_cl30_returns_2x1(self):
        """Cl(3,0) spinor is a 2-component column."""
        from galaga_matrix import to_spinor_matrix

        alg = Algebra(3)
        # scalar 1 is the simplest even MV (identity rotor)
        s = alg.scalar(1.0)
        spinor = to_spinor_matrix(s)
        assert spinor.shape == (2, 1)

    def test_column_api_is_canonical_and_matrix_api_aliases_it(self):
        from galaga_matrix import (
            from_spinor_column,
            from_spinor_matrix,
            to_spinor_column,
            to_spinor_matrix,
        )

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        psi = alg.scalar(1.5) + 0.25 * (e1 * e2) - 0.75 * (e2 * e3)

        col = to_spinor_column(psi)
        old_col = to_spinor_matrix(psi)
        assert np.allclose(col, old_col)
        assert np.allclose(from_spinor_column(alg, col).data, psi.data)
        assert np.allclose(from_spinor_matrix(alg, col).data, psi.data)

    def test_cl30_identity_rotor(self):
        """Identity rotor maps to spin-up (1, 0)^T."""
        from galaga_matrix import to_spinor_matrix

        alg = Algebra(3)
        s = alg.scalar(1.0)
        spinor = to_spinor_matrix(s)
        expected = np.array([[1], [0]], dtype=complex)
        assert np.allclose(spinor, expected)

    def test_cl30_rotor_roundtrip(self):
        """Even MV roundtrips through spinor representation."""
        from galaga_matrix import from_spinor_matrix, to_spinor_matrix

        from galaga import exp

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        # Rotor: 45° rotation in e12 plane
        R = exp(-0.25 * np.pi * (e1 * e2))
        spinor = to_spinor_matrix(R)
        R2 = from_spinor_matrix(alg, spinor)
        assert np.allclose(R.data, R2.data, atol=1e-10)

    def test_cl30_arbitrary_even_roundtrip(self):
        """Non-unit even MV roundtrips."""
        from galaga_matrix import from_spinor_matrix, to_spinor_matrix

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        # General even element (not normalized)
        psi = alg.scalar(2.0) + 0.5 * (e1 * e2) - 0.3 * (e2 * e3) + 0.7 * (e3 * e1)
        spinor = to_spinor_matrix(psi)
        psi2 = from_spinor_matrix(alg, spinor)
        assert np.allclose(psi.data, psi2.data, atol=1e-10)

    def test_cl30_z_rotation_spinor(self):
        r"""z-rotation rotor gives standard quantum spinor.

        R = exp(-φ/2 e₁₂) maps to [[cos(φ/2)], [-i sin(φ/2)]] up to phase.
        Actually for e₁₂ rotation, ψ = cos(φ/2) - sin(φ/2) e₁₂.
        The Pauli representation: σ₁σ₂ = iσ₃ = i*diag(1,-1).
        So matrix is cos(φ/2)*I - sin(φ/2)*i*diag(1,-1)
                   = diag(cos(φ/2) - i sin(φ/2), cos(φ/2) + i sin(φ/2))
                   = diag(e^{-iφ/2}, e^{iφ/2}).
        Projected onto p = diag(1,0): spinor = [[e^{-iφ/2}], [0]].
        """
        from galaga_matrix import to_spinor_matrix

        from galaga import exp

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        phi = 1.2  # arbitrary angle
        R = exp((-phi / 2) * (e1 * e2))
        spinor = to_spinor_matrix(R)
        expected = np.array([[np.exp(-1j * phi / 2)], [0]], dtype=complex)
        assert np.allclose(spinor, expected, atol=1e-12)

    def test_cl30_bloch_state(self):
        """Standard Bloch sphere state θ, φ gives known spinor."""
        from galaga_matrix import to_spinor_matrix

        from galaga import exp

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        theta = np.pi / 3
        phi = np.pi / 4
        # Standard rotor for Bloch state
        R = exp((-phi / 2) * (e1 * e2)) * exp((-theta / 2) * (e3 * e1))
        spinor = to_spinor_matrix(R)
        # Standard quantum spinor: [cos(θ/2), e^{iφ} sin(θ/2)]
        # But our convention uses p = ½(1 + σ₃), so we get:
        # The first column of R's matrix representation
        expected = np.array(
            [[np.cos(theta / 2) * np.exp(-1j * phi / 2)], [np.sin(theta / 2) * np.exp(1j * phi / 2)]],
            dtype=complex,
        )
        assert np.allclose(spinor, expected, atol=1e-12)

    def test_cl13_returns_4x1(self):
        """Cl(1,3) spinor is a 4-component Dirac spinor."""
        from galaga_matrix import to_spinor_matrix

        sta = Algebra(1, 3)
        s = sta.scalar(1.0)
        spinor = to_spinor_matrix(s)
        assert spinor.shape == (4, 1)

    def test_cl13_identity_spinor(self):
        """Identity in STA maps to (1,0,0,0)^T."""
        from galaga_matrix import to_spinor_matrix

        sta = Algebra(1, 3)
        s = sta.scalar(1.0)
        spinor = to_spinor_matrix(s)
        expected = np.zeros((4, 1), dtype=complex)
        expected[0, 0] = 1.0
        assert np.allclose(spinor, expected)

    def test_cl13_majorana_basis_convention(self):
        """The documented Majorana basis makes charge conjugation real."""
        from galaga_matrix import from_spinor_matrix, to_spinor_matrix

        sta = Algebra(1, 3)
        gammas = compact_basis(sta)
        I4 = np.eye(4, dtype=complex)
        charge_conjugation_B = 1j * gammas[2]
        majorana_from_dirac = (1 / np.sqrt(2)) * np.array(
            [
                [1j, 0, 0, -1j],
                [0, 1j, 1j, 0],
                [1, 0, 0, 1],
                [0, 1, -1, 0],
            ],
            dtype=complex,
        )
        dirac_from_majorana = majorana_from_dirac.conj().T
        majorana_gammas = [majorana_from_dirac @ gamma @ dirac_from_majorana for gamma in gammas]

        assert np.allclose(majorana_from_dirac.conj().T @ majorana_from_dirac, I4)
        assert np.allclose(
            majorana_from_dirac @ charge_conjugation_B @ majorana_from_dirac.T,
            I4,
            atol=1e-10,
        )
        assert all(np.allclose(gamma.real, 0, atol=1e-10) for gamma in majorana_gammas)

        for mu, gamma_mu in enumerate(majorana_gammas):
            for nu, gamma_nu in enumerate(majorana_gammas):
                assert np.allclose(
                    gamma_mu @ gamma_nu + gamma_nu @ gamma_mu,
                    2 * sta.signature[mu] * I4 if mu == nu else np.zeros((4, 4)),
                    atol=1e-10,
                )

        g0, g1, g2, g3 = sta.basis_vectors()
        psi = (
            sta.scalar(1.0)
            + 0.45 * (g0 * g1)
            + 0.35 * (g1 * g2)
            - 0.20 * (g0 * g3)
            + 0.25 * sta.pseudoscalar()
            + 0.12 * (g2 * g3)
        )
        dirac_column = to_spinor_matrix(psi)
        majorana_column = majorana_from_dirac @ dirac_column

        assert np.allclose(dirac_from_majorana @ majorana_column, dirac_column)
        assert np.allclose(
            from_spinor_matrix(sta, dirac_from_majorana @ majorana_column).data,
            psi.data,
            atol=1e-10,
        )
        assert np.allclose(
            majorana_from_dirac @ (charge_conjugation_B @ dirac_column.conj()),
            majorana_column.conj(),
            atol=1e-10,
        )

        real_majorana_column = np.array([[1.0], [0.25], [-0.5], [0.75]], dtype=complex)
        real_majorana_as_dirac = dirac_from_majorana @ real_majorana_column
        assert np.allclose(
            charge_conjugation_B @ real_majorana_as_dirac.conj(),
            real_majorana_as_dirac,
            atol=1e-10,
        )
        real_majorana_mv = from_spinor_matrix(sta, real_majorana_as_dirac)
        assert np.allclose(
            majorana_from_dirac @ to_spinor_matrix(real_majorana_mv),
            real_majorana_column,
            atol=1e-10,
        )

    def test_cl13_roundtrip(self):
        """Even MV in Cl(1,3) roundtrips."""
        from galaga_matrix import from_spinor_matrix, to_spinor_matrix

        from galaga import exp

        sta = Algebra(1, 3)
        g = sta.basis_vectors()
        # Boost in γ₀γ₁ plane
        B = 0.3 * (g[0] * g[1])
        R = exp(B)
        spinor = to_spinor_matrix(R)
        R2 = from_spinor_matrix(sta, spinor)
        assert np.allclose(R.data, R2.data, atol=1e-10)

    def test_odd_grade_raises(self):
        """Odd-grade MV raises ValueError."""
        from galaga_matrix import to_spinor_matrix

        alg = Algebra(3)
        e1 = alg.basis_vectors()[0]
        with pytest.raises(ValueError, match="even-grade"):
            to_spinor_matrix(e1)

    def test_mixed_grade_raises(self):
        """Mixed even+odd MV raises ValueError."""
        from galaga_matrix import to_spinor_matrix

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        mv = alg.scalar(1.0) + e1  # scalar + vector
        with pytest.raises(ValueError, match="even-grade"):
            to_spinor_matrix(mv)

    def test_zero_even_mv(self):
        """Zero even MV gives zero spinor."""
        from galaga_matrix import to_spinor_matrix

        alg = Algebra(3)
        z = alg.scalar(0.0)
        spinor = to_spinor_matrix(z)
        assert np.allclose(spinor, 0)

    def test_from_spinor_wrong_shape_raises(self):
        """Wrong-shape spinor raises ValueError."""
        from galaga_matrix import from_spinor_matrix

        alg = Algebra(3)
        with pytest.raises(ValueError, match="Expected"):
            from_spinor_matrix(alg, np.ones((3, 1), dtype=complex))

    def test_from_spinor_outside_image_raises(self):
        """Overdetermined spinor systems reject columns outside the image."""
        from galaga_matrix import from_spinor_matrix

        alg = Algebra(0, 2)
        with pytest.raises(ValueError, match="not in the image"):
            from_spinor_matrix(alg, np.array([[0], [1]], dtype=complex))

    @pytest.mark.parametrize(
        "signature",
        [
            (3, 1),
            (2, 2),
            (4, 1),
        ],
    )
    def test_spinor_roundtrip_rank_check_rejects_non_injective_maps(self, signature):
        alg = Algebra(*signature)

        assert not _spinor_roundtrip_possible(alg)

    @pytest.mark.parametrize(
        "signature",
        [
            (3, 1),
            (2, 2),
            (4, 1),
        ],
    )
    def test_to_spinor_column_rejects_non_injective_maps(self, signature):
        from galaga_matrix import to_spinor_column

        alg = Algebra(*signature)
        with pytest.raises(TypeError, match="does not support faithful spinor roundtrip"):
            to_spinor_column(alg.scalar(1.0))

    @pytest.mark.parametrize(
        "signature",
        [
            (3, 1),
            (2, 2),
            (4, 1),
        ],
    )
    def test_from_spinor_column_rejects_non_injective_maps(self, signature):
        from galaga_matrix import from_spinor_column

        alg = Algebra(*signature)
        spinor = np.zeros((compact_basis(alg)[0].shape[0], 1), dtype=complex)
        with pytest.raises(TypeError, match="does not support faithful spinor roundtrip"):
            from_spinor_column(alg, spinor)

    def test_from_spinor_flat_vector(self):
        """Flat (k,) array is accepted."""
        from galaga_matrix import from_spinor_matrix, to_spinor_matrix

        from galaga import exp

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        R = exp(-0.5 * (e1 * e2))
        spinor = to_spinor_matrix(R)
        R2 = from_spinor_matrix(alg, spinor.flatten())
        assert np.allclose(R.data, R2.data, atol=1e-10)

    def test_spinor_norm_equals_mv_norm(self):
        """‖spinor‖² = ψ scalar_part(ψ~ψ) for normalized rotor."""
        from galaga_matrix import to_spinor_matrix

        from galaga import exp

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        R = exp(-0.7 * (e2 * e3))
        spinor = to_spinor_matrix(R)
        spinor_norm_sq = float(np.real((spinor.conj().T @ spinor)[0, 0]))
        # For a rotor, R~R = 1, so spinor should be normalized
        assert np.isclose(spinor_norm_sq, 1.0, atol=1e-12)


class TestSpinorQuaternion:
    """Tests for to_spinor_quaternion and from_spinor_quaternion."""

    def test_cl13_returns_2_quats(self):
        """Cl(1,3) quaternionic spinor has 2 quaternion components."""
        from galaga_matrix import to_spinor_quaternion

        sta = Algebra(1, 3)
        s = sta.scalar(1.0)
        qspinor = to_spinor_quaternion(s)
        assert len(qspinor) == 2
        assert all(isinstance(q, Quat) for q in qspinor)

    def test_cl13_identity_quat_spinor(self):
        """Identity in STA maps to (1, 0) quaternion spinor."""
        from galaga_matrix import to_spinor_quaternion

        sta = Algebra(1, 3)
        s = sta.scalar(1.0)
        qspinor = to_spinor_quaternion(s)
        # First quaternion should be 1 (real unit)
        assert abs(qspinor[0].a - 1) < 1e-12
        assert abs(qspinor[0].b) < 1e-12
        assert abs(qspinor[0].c) < 1e-12
        assert abs(qspinor[0].d) < 1e-12
        # Second quaternion should be 0
        assert abs(qspinor[1].a) < 1e-12
        assert abs(qspinor[1].b) < 1e-12
        assert abs(qspinor[1].c) < 1e-12
        assert abs(qspinor[1].d) < 1e-12

    def test_cl13_roundtrip(self):
        """Even MV in Cl(1,3) roundtrips through quaternionic spinor."""
        from galaga_matrix import from_spinor_quaternion, to_spinor_quaternion

        from galaga import exp

        sta = Algebra(1, 3)
        g = sta.basis_vectors()
        B = 0.4 * (g[0] * g[1]) + 0.2 * (g[2] * g[3])
        R = exp(B)
        qspinor = to_spinor_quaternion(R)
        R2 = from_spinor_quaternion(sta, qspinor)
        assert np.allclose(R.data, R2.data, atol=1e-10)

    def test_cl13_arbitrary_even_roundtrip(self):
        """General even MV in Cl(1,3) roundtrips."""
        from galaga_matrix import from_spinor_quaternion, to_spinor_quaternion

        from galaga import even_grades

        sta = Algebra(1, 3)
        np.random.seed(99)
        data = np.random.randn(sta.dim)
        mv = Multivector(sta, data)
        mv_even = even_grades(mv)
        qspinor = to_spinor_quaternion(mv_even)
        mv2 = from_spinor_quaternion(sta, qspinor)
        assert np.allclose(mv_even.data, mv2.data, atol=1e-10)

    def test_cl02_returns_1_quat(self):
        """Cl(0,2) quaternionic spinor has 1 quaternion component."""
        from galaga_matrix import to_spinor_quaternion

        alg = Algebra(0, 2)
        s = alg.scalar(1.0)
        qspinor = to_spinor_quaternion(s)
        assert len(qspinor) == 1

    def test_cl02_roundtrip(self):
        """Even MV in Cl(0,2) roundtrips through quaternionic spinor."""
        from galaga_matrix import from_spinor_quaternion, to_spinor_quaternion

        alg = Algebra(0, 2)
        e1, e2 = alg.basis_vectors()
        psi = alg.scalar(0.5) + 0.3 * (e1 * e2)
        qspinor = to_spinor_quaternion(psi)
        psi2 = from_spinor_quaternion(alg, qspinor)
        assert np.allclose(psi.data, psi2.data, atol=1e-10)

    def test_non_quaternionic_raises(self):
        """Non-quaternionic algebra raises TypeError."""
        from galaga_matrix import to_spinor_quaternion

        alg = Algebra(3)
        s = alg.scalar(1.0)
        with pytest.raises(TypeError, match="not quaternionic"):
            to_spinor_quaternion(s)

    def test_from_non_quaternionic_raises(self):
        """Non-quaternionic algebra raises TypeError."""
        from galaga_matrix import from_spinor_quaternion

        alg = Algebra(3)
        with pytest.raises(TypeError, match="not quaternionic"):
            from_spinor_quaternion(alg, [Quat(1), Quat(0)])

    def test_quaternionic_double_algebra_raises(self):
        """One summand of a double algebra is not exposed as a quaternionic spinor."""
        from galaga_matrix import to_spinor_quaternion

        alg = Algebra(0, 3)
        with pytest.raises(TypeError, match="not a single quaternionic matrix algebra"):
            to_spinor_quaternion(alg.scalar(1.0))

    def test_from_quaternionic_double_algebra_raises(self):
        """One summand of a double algebra is not exposed as a quaternionic spinor."""
        from galaga_matrix import from_spinor_quaternion

        alg = Algebra(0, 3)
        with pytest.raises(TypeError, match="not a single quaternionic matrix algebra"):
            from_spinor_quaternion(alg, [Quat(1)])

    @pytest.mark.parametrize("func_name", ["to_spinor_quaternion", "from_spinor_quaternion"])
    def test_unsupported_quaternionic_block_basis_raises(self, func_name):
        import galaga_matrix

        alg = Algebra(4, 0)
        func = getattr(galaga_matrix, func_name)
        with pytest.raises(TypeError, match="not implemented"):
            if func_name.startswith("to_"):
                func(alg.scalar(1.0))
            else:
                func(alg, [Quat(1), Quat(0)])

    def test_from_quaternion_spinor_outside_image_raises(self):
        """Cl(0,2) even spinors occupy a real subspace of one quaternion."""
        from galaga_matrix import from_spinor_quaternion

        alg = Algebra(0, 2)
        with pytest.raises(ValueError, match="not in the image"):
            from_spinor_quaternion(alg, [Quat(0, 0, 1, 0)])

    def test_from_quaternion_spinor_non_quat_entry_raises(self):
        from galaga_matrix import from_spinor_quaternion

        alg = Algebra(0, 2)
        with pytest.raises(TypeError, match="Quat entries"):
            from_spinor_quaternion(alg, [1])

    def test_odd_grade_raises(self):
        """Odd-grade MV raises ValueError."""
        from galaga_matrix import to_spinor_quaternion

        sta = Algebra(1, 3)
        g0 = sta.basis_vectors()[0]
        with pytest.raises(ValueError, match="even-grade"):
            to_spinor_quaternion(g0)

    def test_from_wrong_length_raises(self):
        """Wrong-length quaternion list raises ValueError."""
        from galaga_matrix import from_spinor_quaternion

        sta = Algebra(1, 3)
        with pytest.raises(ValueError, match="Expected 2"):
            from_spinor_quaternion(sta, [Quat(1)])

    def test_8_real_dof(self):
        """Quaternionic spinor has 8 real degrees of freedom for Cl(1,3)."""
        from galaga_matrix import to_spinor_quaternion

        from galaga import exp

        sta = Algebra(1, 3)
        g = sta.basis_vectors()
        # A general boost+rotation
        B = 0.3 * (g[0] * g[1]) + 0.5 * (g[1] * g[2]) + 0.1 * (g[0] * g[3])
        R = exp(B)
        qspinor = to_spinor_quaternion(R)
        # Count non-trivially-zero real components
        reals = []
        for q in qspinor:
            reals.extend([q.a, q.b, q.c, q.d])
        assert len(reals) == 8  # 2 quaternions × 4 real each


class TestSpinorFullRoundtrip:
    """End-to-end roundtrip tests: MV → spinor (all forms) → MV."""

    @pytest.mark.parametrize("seed", range(5))
    def test_cl30_complex_spinor_roundtrip(self, seed):
        """Random even Cl(3,0) MV roundtrips via complex spinor."""
        from galaga_matrix import from_spinor_matrix, to_spinor_matrix

        from galaga import even_grades

        alg = Algebra(3)
        np.random.seed(seed)
        data = np.random.randn(alg.dim)
        mv = even_grades(Multivector(alg, data))
        spinor = to_spinor_matrix(mv)
        mv2 = from_spinor_matrix(alg, spinor)
        assert np.allclose(mv.data, mv2.data, atol=1e-10), f"Cl(3,0) complex spinor roundtrip failed (seed={seed})"

    @pytest.mark.parametrize("seed", range(5))
    def test_cl13_complex_spinor_roundtrip(self, seed):
        """Random even Cl(1,3) MV roundtrips via complex spinor."""
        from galaga_matrix import from_spinor_matrix, to_spinor_matrix

        from galaga import even_grades

        sta = Algebra(1, 3)
        np.random.seed(seed + 100)
        data = np.random.randn(sta.dim)
        mv = even_grades(Multivector(sta, data))
        spinor = to_spinor_matrix(mv)
        mv2 = from_spinor_matrix(sta, spinor)
        assert np.allclose(mv.data, mv2.data, atol=1e-10), f"Cl(1,3) complex spinor roundtrip failed (seed={seed})"

    @pytest.mark.parametrize("seed", range(5))
    def test_cl40_complex_spinor_roundtrip(self, seed):
        """Random even Cl(4,0) MV roundtrips via complex spinor."""
        from galaga_matrix import from_spinor_column, to_spinor_column

        from galaga import even_grades

        alg = Algebra(4, 0)
        np.random.seed(seed + 150)
        data = np.random.randn(alg.dim)
        mv = even_grades(Multivector(alg, data))
        spinor = to_spinor_column(mv)
        mv2 = from_spinor_column(alg, spinor)
        assert np.allclose(mv.data, mv2.data, atol=1e-10), f"Cl(4,0) complex spinor roundtrip failed (seed={seed})"

    @pytest.mark.parametrize("seed", range(5))
    def test_cl31_complex_spinor_raises(self, seed):
        """Cl(3,1) is real-type and cannot faithfully roundtrip through spinor."""
        from galaga_matrix import to_spinor_matrix

        from galaga import even_grades

        alg = Algebra(3, 1)
        np.random.seed(seed + 200)
        data = np.random.randn(alg.dim)
        mv = even_grades(Multivector(alg, data))
        with pytest.raises(TypeError, match="does not support faithful spinor roundtrip"):
            to_spinor_matrix(mv)

    @pytest.mark.parametrize("seed", range(5))
    def test_cl13_quaternion_spinor_roundtrip(self, seed):
        """Random even Cl(1,3) MV roundtrips via quaternionic spinor."""
        from galaga_matrix import from_spinor_quaternion, to_spinor_quaternion

        from galaga import even_grades

        sta = Algebra(1, 3)
        np.random.seed(seed + 300)
        data = np.random.randn(sta.dim)
        mv = even_grades(Multivector(sta, data))
        qspinor = to_spinor_quaternion(mv)
        mv2 = from_spinor_quaternion(sta, qspinor)
        assert np.allclose(mv.data, mv2.data, atol=1e-10), f"Cl(1,3) quat spinor roundtrip failed (seed={seed})"

    @pytest.mark.parametrize("seed", range(5))
    def test_cl02_quaternion_spinor_roundtrip(self, seed):
        """Random even Cl(0,2) MV roundtrips via quaternionic spinor."""
        from galaga_matrix import from_spinor_quaternion, to_spinor_quaternion

        from galaga import even_grades

        alg = Algebra(0, 2)
        np.random.seed(seed + 400)
        data = np.random.randn(alg.dim)
        mv = even_grades(Multivector(alg, data))
        qspinor = to_spinor_quaternion(mv)
        mv2 = from_spinor_quaternion(alg, qspinor)
        assert np.allclose(mv.data, mv2.data, atol=1e-10), f"Cl(0,2) quat spinor roundtrip failed (seed={seed})"

    def test_cl13_complex_and_quaternion_spinor_consistent(self):
        """Complex and quaternion spinors encode the same information."""
        from galaga_matrix import (
            from_spinor_matrix,
            from_spinor_quaternion,
            to_spinor_matrix,
            to_spinor_quaternion,
        )

        from galaga import exp

        sta = Algebra(1, 3)
        g = sta.basis_vectors()
        B = 0.5 * (g[0] * g[2]) - 0.3 * (g[1] * g[3])
        R = exp(B)

        # Both forms should recover the same MV
        spinor_c = to_spinor_matrix(R)
        spinor_q = to_spinor_quaternion(R)
        mv_from_c = from_spinor_matrix(sta, spinor_c)
        mv_from_q = from_spinor_quaternion(sta, spinor_q)
        assert np.allclose(mv_from_c.data, mv_from_q.data, atol=1e-10)
        assert np.allclose(R.data, mv_from_c.data, atol=1e-10)

    def test_cl30_spinor_preserves_rotor_structure(self):
        """A rotor roundtripped through spinor form is still a rotor."""
        from galaga_matrix import from_spinor_matrix, to_spinor_matrix

        from galaga import exp, reverse

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        R = exp(-0.8 * (e1 * e3))
        spinor = to_spinor_matrix(R)
        R2 = from_spinor_matrix(alg, spinor)
        # Check R2 is still a rotor: R2 * ~R2 = 1
        product = (R2 * reverse(R2)).data
        expected = np.zeros(alg.dim)
        expected[0] = 1.0
        assert np.allclose(product, expected, atol=1e-10)


class TestQuatMatrixRepr:
    def test_latex_rendering(self):
        from galaga_matrix import QuatMatrixRepr

        qm = [[Quat(1, 0, 0, 0), Quat(0, 0, 1, 0)], [Quat(0, 0, -1, 0), Quat(-1, 0, 0, 0)]]
        qr = QuatMatrixRepr(qm, label=r"\gamma_1")
        latex = qr.latex()
        assert r"\begin{pmatrix}" in latex
        assert r"\gamma_1" in latex

    def test_repr_latex(self):
        from galaga_matrix import QuatMatrixRepr

        qm = [[Quat(1)]]
        qr = QuatMatrixRepr(qm)
        assert qr._repr_latex_().startswith("$")


# ── MatrixRepr transparent proxy ──


class TestMatrixReprArithmetic:
    """Arithmetic operators on MatrixRepr."""

    def _make(self, data, **kwargs):
        return MatrixRepr(np.array(data, dtype=complex), **kwargs)

    def test_matmul_two_repr(self):
        """MatrixRepr @ MatrixRepr returns MatrixRepr."""
        A = self._make([[1, 2], [3, 4]])
        B = self._make([[5, 6], [7, 8]])
        C = A @ B
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, np.array([[19, 22], [43, 50]], dtype=complex))

    def test_matmul_with_ndarray(self):
        """MatrixRepr @ ndarray returns MatrixRepr."""
        A = self._make([[1, 0], [0, 1]])
        B = np.array([[3, 4], [5, 6]], dtype=complex)
        C = A @ B
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, B)

    def test_rmatmul_with_ndarray(self):
        """ndarray @ MatrixRepr returns MatrixRepr."""
        A = np.array([[1, 2], [3, 4]], dtype=complex)
        B = self._make([[1, 0], [0, 1]])
        C = A @ B
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, A)

    def test_add(self):
        A = self._make([[1, 2], [3, 4]])
        B = self._make([[10, 20], [30, 40]])
        C = A + B
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[11, 22], [33, 44]])

    def test_radd(self):
        A = self._make([[1, 0], [0, 1]])
        C = np.eye(2, dtype=complex) + A
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, 2 * np.eye(2))

    def test_sub(self):
        A = self._make([[5, 6], [7, 8]])
        B = self._make([[1, 2], [3, 4]])
        C = A - B
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[4, 4], [4, 4]])

    def test_rsub(self):
        A = self._make([[1, 0], [0, 1]])
        C = np.eye(2, dtype=complex) * 3 - A
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, 2 * np.eye(2))

    def test_mul_scalar(self):
        A = self._make([[1, 2], [3, 4]])
        C = A * 2
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[2, 4], [6, 8]])

    def test_rmul_scalar(self):
        A = self._make([[1, 2], [3, 4]])
        C = 3 * A
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[3, 6], [9, 12]])

    def test_truediv_scalar(self):
        A = self._make([[4, 6], [8, 10]])
        C = A / 2
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[2, 3], [4, 5]])

    def test_neg(self):
        A = self._make([[1, -2], [3, -4]])
        C = -A
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[-1, 2], [-3, 4]])

    def test_pos(self):
        A = self._make([[1, 2], [3, 4]])
        C = +A
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, A.mat)

    def test_pow_square(self):
        A = self._make([[0, 1], [1, 0]])  # Pauli X
        C = A**2
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, np.eye(2))

    def test_pow_zero(self):
        A = self._make([[1, 2], [3, 4]])
        C = A**0
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, np.eye(2))

    def test_pow_negative(self):
        """A**(-1) is the matrix inverse."""
        A = self._make([[1, 2], [3, 4]])
        C = A ** (-1)
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat @ A.mat, np.eye(2), atol=1e-10)


class TestMatrixReprUnary:
    """Transpose, conjugate, trace, det, inv."""

    def _make(self, data, **kwargs):
        return MatrixRepr(np.array(data, dtype=complex), **kwargs)

    def test_transpose(self):
        A = self._make([[1, 2], [3, 4]])
        assert isinstance(A.T, MatrixRepr)
        assert np.allclose(A.T.mat, [[1, 3], [2, 4]])

    def test_hermitian(self):
        A = self._make([[1, 1j], [-1j, 2]])
        H = A.H
        assert isinstance(H, MatrixRepr)
        assert np.allclose(H.mat, [[1, 1j], [-1j, 2]])  # this one is Hermitian

    def test_hermitian_non_hermitian(self):
        A = self._make([[0, 1j], [0, 0]])
        H = A.H
        assert np.allclose(H.mat, [[0, 0], [-1j, 0]])

    def test_conj(self):
        A = self._make([[1 + 1j, 2 - 1j], [3, 4 + 2j]])
        C = A.conj()
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[1 - 1j, 2 + 1j], [3, 4 - 2j]])

    def test_trace(self):
        A = self._make([[1, 2], [3, 4]])
        assert A.trace() == 5

    def test_trace_complex(self):
        A = self._make([[1 + 1j, 0], [0, 2 - 1j]])
        assert A.trace() == 3

    def test_det(self):
        A = self._make([[1, 2], [3, 4]])
        assert np.isclose(A.det(), -2)

    def test_det_singular(self):
        A = self._make([[1, 2], [2, 4]])
        assert np.isclose(A.det(), 0)

    def test_inv(self):
        A = self._make([[1, 2], [3, 4]])
        Ainv = A.inv()
        assert isinstance(Ainv, MatrixRepr)
        assert np.allclose((A @ Ainv).mat, np.eye(2), atol=1e-10)

    def test_inv_roundtrip(self):
        A = self._make([[1, 1j], [0, 1]])
        assert np.allclose((A.inv() @ A).mat, np.eye(2), atol=1e-10)


class TestMatrixReprShape:
    """Shape, dtype, len, getitem."""

    def _make(self, data, **kwargs):
        return MatrixRepr(np.array(data, dtype=complex), **kwargs)

    def test_shape(self):
        A = self._make([[1, 2, 3], [4, 5, 6]])
        assert A.shape == (2, 3)

    def test_dtype(self):
        A = self._make([[1, 2], [3, 4]])
        assert A.dtype == complex

    def test_len(self):
        A = self._make([[1, 2], [3, 4], [5, 6]])
        assert len(A) == 3

    def test_getitem_element(self):
        A = self._make([[1, 2], [3, 4]])
        assert A[0, 0] == 1
        assert A[1, 1] == 4

    def test_getitem_row(self):
        A = self._make([[1, 2], [3, 4]])
        row = A[0, :]
        # 1D result is returned raw (not wrapped)
        assert isinstance(row, np.ndarray)
        assert np.allclose(row, [1, 2])

    def test_getitem_submatrix(self):
        A = self._make([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        sub = A[0:2, 0:2]
        assert isinstance(sub, MatrixRepr)
        assert np.allclose(sub.mat, [[1, 2], [4, 5]])


class TestMatrixReprNumpyInterop:
    """__array_ufunc__ and numpy function interop."""

    def _make(self, data, **kwargs):
        return MatrixRepr(np.array(data, dtype=complex), **kwargs)

    def test_np_add(self):
        A = self._make([[1, 2], [3, 4]])
        B = self._make([[10, 20], [30, 40]])
        C = np.add(A, B)
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[11, 22], [33, 44]])

    def test_np_multiply(self):
        A = self._make([[1, 2], [3, 4]])
        C = np.multiply(A, 2)
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[2, 4], [6, 8]])

    def test_np_conj(self):
        A = self._make([[1 + 1j, 2], [3, 4 - 1j]])
        C = np.conj(A)
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[1 - 1j, 2], [3, 4 + 1j]])

    def test_np_matmul(self):
        A = self._make([[1, 0], [0, 1]])
        B = self._make([[5, 6], [7, 8]])
        C = np.matmul(A, B)
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[5, 6], [7, 8]])

    def test_np_trace(self):
        """np.trace returns scalar (not wrapped)."""
        A = self._make([[1, 2], [3, 4]])
        assert np.trace(A) == 5

    def test_np_linalg_det(self):
        """np.linalg.det works through __array__."""
        A = self._make([[1, 2], [3, 4]])
        assert np.isclose(np.linalg.det(A), -2)

    def test_np_allclose_with_repr(self):
        """np.allclose works between MatrixRepr and array."""
        A = self._make([[1, 2], [3, 4]])
        assert np.allclose(A, [[1, 2], [3, 4]])


class TestMatrixReprFactory:
    """Factory methods: identity, zeros, kron."""

    def test_identity(self):
        I = MatrixRepr.identity(3)
        assert isinstance(I, MatrixRepr)
        assert I.shape == (3, 3)
        assert np.allclose(I.mat, np.eye(3))

    def test_identity_with_algebra(self):
        alg = Algebra(3)
        I = MatrixRepr.identity(2, algebra=alg, mode="compact")
        assert I.algebra is alg
        assert I.mode == "compact"

    def test_zeros(self):
        Z = MatrixRepr.zeros((2, 3))
        assert isinstance(Z, MatrixRepr)
        assert Z.shape == (2, 3)
        assert np.allclose(Z.mat, 0)

    def test_kron(self):
        A = MatrixRepr(np.eye(2, dtype=complex))
        B = MatrixRepr(np.array([[1, 2], [3, 4]], dtype=complex))
        K = A.kron(B)
        assert isinstance(K, MatrixRepr)
        assert K.shape == (4, 4)
        expected = np.kron(np.eye(2), [[1, 2], [3, 4]])
        assert np.allclose(K.mat, expected)


class TestMatrixReprMetadata:
    """Metadata propagation through operations."""

    def test_algebra_propagates_through_matmul(self):
        alg = Algebra(3)
        A = MatrixRepr(np.eye(2, dtype=complex), algebra=alg, mode="compact")
        B = MatrixRepr(np.eye(2, dtype=complex))
        C = A @ B
        assert C.algebra is alg
        assert C.mode == "compact"

    def test_mode_propagates_through_add(self):
        A = MatrixRepr(np.eye(2, dtype=complex), mode="compact")
        B = MatrixRepr(np.eye(2, dtype=complex))
        C = A + B
        assert C.mode == "compact"

    def test_label_not_propagated(self):
        """Labels are specific to a named matrix and shouldn't propagate."""
        A = MatrixRepr(np.eye(2, dtype=complex), label=r"\sigma_1")
        B = MatrixRepr(np.eye(2, dtype=complex))
        C = A @ B
        assert C.label is None

    def test_algebra_propagates_through_inv(self):
        alg = Algebra(3)
        A = MatrixRepr(np.array([[1, 2], [3, 4]], dtype=complex), algebra=alg, mode="compact")
        Ainv = A.inv()
        assert Ainv.algebra is alg

    def test_algebra_propagates_through_transpose(self):
        alg = Algebra(3)
        A = MatrixRepr(np.array([[1, 2], [3, 4]], dtype=complex), algebra=alg, mode="left-regular")
        assert A.T.algebra is alg
        assert A.T.mode == "left-regular"


class TestMatrixReprPauliAlgebra:
    """Integration: Pauli matrices as MatrixRepr obey the Clifford relations."""

    def _pauli(self):
        s1 = MatrixRepr(np.array([[0, 1], [1, 0]], dtype=complex), label=r"\sigma_1")
        s2 = MatrixRepr(np.array([[0, -1j], [1j, 0]], dtype=complex), label=r"\sigma_2")
        s3 = MatrixRepr(np.array([[1, 0], [0, -1]], dtype=complex), label=r"\sigma_3")
        I2 = MatrixRepr.identity(2)
        return s1, s2, s3, I2

    def test_pauli_squares_to_identity(self):
        s1, s2, s3, I2 = self._pauli()
        assert np.allclose((s1 @ s1).mat, I2.mat)
        assert np.allclose((s2 @ s2).mat, I2.mat)
        assert np.allclose((s3 @ s3).mat, I2.mat)

    def test_pauli_anticommutation(self):
        s1, s2, s3, I2 = self._pauli()
        assert np.allclose((s1 @ s2 + s2 @ s1).mat, 0)
        assert np.allclose((s2 @ s3 + s3 @ s2).mat, 0)
        assert np.allclose((s3 @ s1 + s1 @ s3).mat, 0)

    def test_pauli_products(self):
        s1, s2, s3, I2 = self._pauli()
        # σ₁σ₂ = iσ₃
        assert np.allclose((s1 @ s2).mat, 1j * s3.mat)
        # σ₂σ₃ = iσ₁
        assert np.allclose((s2 @ s3).mat, 1j * s1.mat)
        # σ₃σ₁ = iσ₂
        assert np.allclose((s3 @ s1).mat, 1j * s2.mat)

    def test_pauli_hermitian(self):
        s1, s2, s3, _ = self._pauli()
        assert np.allclose(s1.H.mat, s1.mat)
        assert np.allclose(s2.H.mat, s2.mat)
        assert np.allclose(s3.H.mat, s3.mat)

    def test_pauli_traceless(self):
        s1, s2, s3, _ = self._pauli()
        assert s1.trace() == 0
        assert s2.trace() == 0
        assert s3.trace() == 0

    def test_pauli_det(self):
        s1, s2, s3, _ = self._pauli()
        assert np.isclose(s1.det(), -1)
        assert np.isclose(s2.det(), -1)
        assert np.isclose(s3.det(), -1)

    def test_rotor_from_pauli(self):
        """exp(-iθ/2 σ₃) via MatrixRepr arithmetic."""
        _, _, s3, I2 = self._pauli()
        theta = np.pi / 3
        # R = cos(θ/2)I - i sin(θ/2)σ₃
        R = I2 * np.cos(theta / 2) + s3 * (-1j * np.sin(theta / 2))
        assert isinstance(R, MatrixRepr)
        # R should be unitary: R @ R.H = I
        assert np.allclose((R @ R.H).mat, np.eye(2), atol=1e-10)


class TestMatrixReprQuaternionReject:
    """Quaternion MatrixRepr correctly rejects numeric operations."""

    def test_quat_add_raises(self):
        qm = [[Quat(1, 0, 0, 0)]]
        A = MatrixRepr(qm)
        with pytest.raises(TypeError, match="quaternion"):
            A + A

    def test_quat_matmul_raises(self):
        qm = [[Quat(1, 0, 0, 0)]]
        A = MatrixRepr(qm)
        with pytest.raises(TypeError, match="quaternion"):
            A @ A

    def test_quat_shape_raises(self):
        qm = [[Quat(1, 0, 0, 0)]]
        A = MatrixRepr(qm)
        with pytest.raises(TypeError, match="quaternion"):
            _ = A.shape

    def test_quat_inv_raises(self):
        qm = [[Quat(1, 0, 0, 0)]]
        A = MatrixRepr(qm)
        with pytest.raises(TypeError, match="quaternion"):
            A.inv()


class TestMatrixReprNaming:
    """Label propagation: MV name → ρ(name), MatrixRepr label → ρ⁻¹(label)."""

    def test_to_matrix_named_mv_gets_rho_label(self):
        """Named MV produces MatrixRepr with ρ(name) label."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        R = (e1 * e2).name(latex=r"\hat{B}")
        M = to_matrix(R, mode="compact")
        assert M.label == r"\rho(\hat{B})"

    def test_to_matrix_unnamed_mv_no_label(self):
        """Unnamed MV produces MatrixRepr with no label."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        v = 2 * e1 + 3 * e2
        M = to_matrix(v, mode="compact")
        assert M.label is None

    def test_from_matrix_labeled_gives_rho_inv_name(self):
        """Labeled MatrixRepr produces MV named ρ⁻¹(label)."""
        alg = Algebra(3)
        M = MatrixRepr(
            np.array([[0, 1], [1, 0]], dtype=complex),
            label=r"\sigma_1",
            algebra=alg,
            mode="compact",
        )
        mv = from_matrix(alg, M)
        assert mv._name_latex == r"\rho^{-1}(\sigma_1)"

    def test_from_matrix_unlabeled_no_name(self):
        """Unlabeled MatrixRepr produces unnamed MV."""
        alg = Algebra(3)
        M = MatrixRepr(
            np.array([[0, 1], [1, 0]], dtype=complex),
            algebra=alg,
            mode="compact",
        )
        mv = from_matrix(alg, M)
        assert getattr(mv, "_name_latex", None) is None

    def test_from_matrix_raw_ndarray_no_name(self):
        """Raw ndarray produces unnamed MV (backward compat)."""
        alg = Algebra(3)
        mat = np.array([[0, 1], [1, 0]], dtype=complex)
        mv = from_matrix(alg, mat, mode="compact")
        assert getattr(mv, "_name_latex", None) is None

    def test_roundtrip_named_mv(self):
        """Named MV → to_matrix → from_matrix preserves data, gets composed name."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        R = (0.5 * (e1 * e2)).name(latex="B")
        M = to_matrix(R, mode="compact")
        assert M.label == r"\rho(B)"
        mv2 = from_matrix(alg, M)
        assert np.allclose(R.data, mv2.data)
        assert mv2._name_latex == r"\rho^{-1}(\rho(B))"

    def test_to_matrix_ascii_name_fallback(self):
        """MV with only ASCII name (no latex) still gets labeled."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        R = (e1 * e2).name("B12")
        M = to_matrix(R, mode="compact")
        assert M.label == r"\rho(B12)"


class TestMatrixReprCopyConstruction:
    """MatrixRepr(MatrixRepr) copies data and inherits metadata."""

    def test_wrap_copies_data(self):
        A = MatrixRepr(np.array([[1, 2], [3, 4]], dtype=complex))
        B = MatrixRepr(A)
        assert np.allclose(B.mat, A.mat)
        # Verify it's a copy, not a reference
        B.mat[0, 0] = 999
        assert A.mat[0, 0] == 1

    def test_wrap_inherits_metadata(self):
        alg = Algebra(3)
        A = MatrixRepr(np.eye(2, dtype=complex), label=r"\sigma_1", algebra=alg, mode="compact")
        B = MatrixRepr(A)
        assert B.label == r"\sigma_1"
        assert B.algebra is alg
        assert B.mode == "compact"

    def test_wrap_override_label(self):
        A = MatrixRepr(np.eye(2, dtype=complex), label="old")
        B = MatrixRepr(A, label="new")
        assert B.label == "new"

    def test_wrap_override_algebra(self):
        alg1 = Algebra(3)
        alg2 = Algebra(2)
        A = MatrixRepr(np.eye(2, dtype=complex), algebra=alg1)
        B = MatrixRepr(A, algebra=alg2)
        assert B.algebra is alg2

    def test_wrap_operations_still_work(self):
        A = MatrixRepr(np.array([[1, 2], [3, 4]], dtype=complex))
        B = MatrixRepr(A)
        C = B @ B
        assert isinstance(C, MatrixRepr)
        assert np.allclose(C.mat, [[7, 10], [15, 22]])


class TestFromMatrixSingleArg:
    """from_matrix(MatrixRepr) without explicit algebra."""

    def test_roundtrip_compact(self):
        """from_matrix(to_matrix(B, mode='compact')) works without passing alg."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        B = 0.5 * (e1 * e2) + 0.3 * (e2 * e3)
        mv = from_matrix(to_matrix(B, mode="compact"))
        assert np.allclose(B.data, mv.data)

    def test_roundtrip_left_regular(self):
        """from_matrix(to_matrix(v)) works for left-regular mode."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        v = 2 * e1 - e3
        mv = from_matrix(to_matrix(v))
        assert np.allclose(v.data, mv.data)

    def test_raw_ndarray_without_alg_raises(self):
        """from_matrix(ndarray) without algebra raises TypeError."""
        import pytest

        mat = np.eye(4, dtype=complex)
        with pytest.raises(TypeError, match="MatrixRepr with an algebra"):
            from_matrix(mat)

    def test_matrixrepr_without_algebra_raises(self):
        """from_matrix(MatrixRepr(no algebra)) raises ValueError."""
        import pytest

        M = MatrixRepr(np.eye(2, dtype=complex), mode="compact")
        with pytest.raises(ValueError, match="no algebra reference"):
            from_matrix(M)

    def test_two_arg_form_still_works(self):
        """from_matrix(alg, mat) still works as before."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        v = e1 + e2
        mat = to_matrix(v, mode="compact")
        mv = from_matrix(alg, mat)
        assert np.allclose(v.data, mv.data)
