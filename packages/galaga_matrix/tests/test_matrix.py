"""Tests for galaga_matrix."""

import numpy as np
import pytest
from galaga_matrix import MatrixRepr, from_matrix, to_matrix
from galaga_matrix.matrix import (
    Quat,
    _classify,
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

    def test_quat_latex(self):
        q = Quat(1, 0, -1, 0)
        assert q.latex() == "1-j"

    def test_quat_repr(self):
        q = Quat(0, 0, 0, 1)
        assert repr(q) == "k"

    def test_quat_zero(self):
        q = Quat(0, 0, 0, 0)
        assert q.latex() == "0"


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
