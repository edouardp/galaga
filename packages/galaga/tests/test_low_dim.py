"""Tests for low-dimensional algebras: Cl(0), Cl(1), Cl(2), and degenerate cases."""

import numpy as np
import pytest

from galaga import (
    Algebra,
    conjugate,
    dual,
    even_grades,
    exp,
    gp,
    inverse,
    involute,
    is_bivector,
    is_rotor,
    is_scalar,
    is_vector,
    log,
    norm,
    odd_grades,
    op,
    project,
    reflect,
    reject,
    reverse,
    sandwich,
    squared,
    undual,
    unit,
)


class TestCl0:
    """Cl(0) — the scalar algebra. dim=1, only grade-0."""

    @pytest.fixture
    def cl0(self):
        return Algebra(())

    def test_dimension(self, cl0):
        """Cl(0) has 2^0 = 1 dimension."""
        assert cl0.dim == 1

    def test_basis_vectors_empty(self, cl0):
        """Cl(0) has no basis vectors."""
        assert cl0.basis_vectors() == ()

    def test_pseudoscalar_is_scalar_one(self, cl0):
        """Pseudoscalar in Cl(0) is the scalar 1."""
        assert np.isclose(cl0.I.data[0], 1.0)

    def test_scalar_gp(self, cl0):
        """Geometric product of scalars is ordinary multiplication."""
        assert np.isclose((gp(cl0.scalar(3), cl0.scalar(5))).scalar_part, 15.0)

    def test_scalar_reverse(self, cl0):
        """Reverse is identity on scalars."""
        s = cl0.scalar(7)
        assert np.allclose(reverse(s).data, s.data)

    def test_scalar_involute(self, cl0):
        """Grade involution is identity on scalars."""
        s = cl0.scalar(7)
        assert np.allclose(involute(s).data, s.data)

    def test_scalar_conjugate(self, cl0):
        """Clifford conjugate is identity on scalars."""
        s = cl0.scalar(7)
        assert np.allclose(conjugate(s).data, s.data)

    def test_scalar_norm(self, cl0):
        """Norm of a scalar is its absolute value."""
        assert np.isclose(norm(cl0.scalar(5)), 5.0)

    def test_scalar_inverse(self, cl0):
        """s * s⁻¹ = 1 for nonzero scalars."""
        s = cl0.scalar(4)
        assert np.isclose((gp(s, inverse(s))).scalar_part, 1.0)

    def test_scalar_dual(self, cl0):
        """Dual is identity in Cl(0) since I = 1."""
        # In Cl(0), I=1, so dual(s) = s * I^-1 = s
        s = cl0.scalar(5)
        assert np.allclose(dual(s).data, s.data)

    def test_scalar_exp(self, cl0):
        """exp(1) = e for a scalar."""
        assert np.isclose((exp(cl0.scalar(1))).scalar_part, np.e)

    def test_even_odd_grades(self, cl0):
        """Scalars are purely even-grade."""
        s = cl0.scalar(5)
        assert np.isclose((even_grades(s)).scalar_part, 5.0)
        assert np.isclose((odd_grades(s)).scalar_part, 0.0)

    def test_is_scalar(self, cl0):
        """is_scalar recognizes a scalar element."""
        assert is_scalar(cl0.scalar(5))

    def test_is_rotor(self, cl0):
        """Unit scalar is a valid rotor."""
        assert is_rotor(cl0.scalar(1))

    def test_rotor_rejects_scalar(self, cl0):
        """rotor() rejects non-bivector input."""
        with pytest.raises(ValueError, match="bivector"):
            cl0.rotor(cl0.scalar(1), radians=0.5)


class TestCl1:
    """Cl(1) — scalar + one vector. dim=2."""

    @pytest.fixture
    def cl1(self):
        return Algebra((1,))

    def test_dimension(self, cl1):
        """Cl(1) has 2^1 = 2 dimensions."""
        assert cl1.dim == 2

    def test_basis_vector_squares_to_one(self, cl1):
        """e1² = +1 in Cl(1)."""
        (e1,) = cl1.basis_vectors()
        assert np.isclose((gp(e1, e1)).scalar_part, 1.0)

    def test_vector_norm(self, cl1):
        """Norm of αe1 is |α|."""
        (e1,) = cl1.basis_vectors()
        assert np.isclose(norm(e1), 1.0)
        assert np.isclose(norm(3 * e1), 3.0)

    def test_vector_inverse(self, cl1):
        """e1 * e1⁻¹ = 1."""
        (e1,) = cl1.basis_vectors()
        assert np.allclose(gp(e1, inverse(e1)).data, cl1.scalar(1).data)

    def test_vector_unit(self, cl1):
        """unit() normalizes a vector to norm 1."""
        (e1,) = cl1.basis_vectors()
        assert np.isclose(norm(unit(3 * e1)), 1.0)

    def test_dual_vector_to_scalar(self, cl1):
        """Dual of a vector in Cl(1) is a scalar."""
        (e1,) = cl1.basis_vectors()
        d = dual(e1)
        assert is_scalar(d)

    def test_dual_undual_roundtrip(self, cl1):
        """undual(dual(x)) = x."""
        (e1,) = cl1.basis_vectors()
        assert np.allclose(undual(dual(e1)).data, e1.data)

    def test_project_onto_self(self, cl1):
        """Projection of a vector onto itself is itself."""
        (e1,) = cl1.basis_vectors()
        assert np.allclose(project(e1, e1).data, e1.data)

    def test_reject_from_self(self, cl1):
        """Rejection of a vector from itself is zero."""
        (e1,) = cl1.basis_vectors()
        assert np.allclose(reject(e1, e1).data, cl1.scalar(0).data, atol=1e-12)

    def test_reflect_in_self(self, cl1):
        """Reflecting e1 in e1 negates it."""
        (e1,) = cl1.basis_vectors()
        assert np.allclose(reflect(e1, e1).data, (-e1).data)

    def test_rotor_rejects_vector(self, cl1):
        """rotor() rejects a vector as the bivector argument."""
        (e1,) = cl1.basis_vectors()
        with pytest.raises(ValueError):
            cl1.rotor(e1, radians=0.5)

    def test_rotor_rejects_scalar(self, cl1):
        """rotor() rejects a scalar as the bivector argument."""
        with pytest.raises(ValueError, match="bivector"):
            cl1.rotor(cl1.scalar(1), radians=0.5)

    def test_log_identity(self, cl1):
        """log(1) = 0."""
        assert np.allclose(log(cl1.scalar(1)).data, cl1.scalar(0).data, atol=1e-12)

    def test_exp_zero(self, cl1):
        """exp(0) = 1."""
        assert np.allclose(exp(cl1.scalar(0)).data, cl1.scalar(1).data)

    def test_predicates(self, cl1):
        """is_vector and is_scalar correctly classify elements."""
        (e1,) = cl1.basis_vectors()
        assert is_vector(e1)
        assert not is_scalar(e1)
        assert is_scalar(cl1.scalar(5))


class TestCl2:
    """Cl(2) — full 2D Euclidean algebra. dim=4."""

    @pytest.fixture
    def cl2(self):
        return Algebra((1, 1))

    def test_dimension(self, cl2):
        """Cl(2) has 2^2 = 4 dimensions."""
        assert cl2.dim == 4

    def test_wedge_product(self, cl2):
        """Wedge of two basis vectors produces a bivector."""
        e1, e2 = cl2.basis_vectors()
        B = op(e1, e2)
        assert is_bivector(B)

    def test_bivector_squares_to_minus_one(self, cl2):
        """Unit bivector e12² = -1 in Euclidean Cl(2)."""
        e1, e2 = cl2.basis_vectors()
        B = op(e1, e2)
        assert np.isclose((squared(B)).scalar_part, -1.0)

    def test_dual(self, cl2):
        """Dual of a vector in 2D is a vector."""
        e1, e2 = cl2.basis_vectors()
        d = dual(e1)
        # dual(e1) in 2D should be ±e2
        assert is_vector(d)

    def test_exp_bivector(self, cl2):
        """exp of a bivector produces a rotor."""
        e1, e2 = cl2.basis_vectors()
        B = op(e1, e2)
        R = exp(np.pi / 4 * B)
        assert is_rotor(R)

    def test_rotor_rotation(self, cl2):
        """π/2 rotor in e12 plane rotates e1 to e2."""
        e1, e2 = cl2.basis_vectors()
        R = cl2.rotor(op(e1, e2), radians=np.pi / 2)
        rotated = sandwich(R, e1)
        assert np.allclose(rotated.data, e2.data, atol=1e-12)

    def test_log_exp_roundtrip(self, cl2):
        """log(exp(B)) = B for a bivector B."""
        e1, e2 = cl2.basis_vectors()
        B = 0.3 * op(e1, e2)
        assert np.allclose(log(exp(B)).data, B.data, atol=1e-12)

    def test_pseudoscalar(self, cl2):
        """Pseudoscalar I equals e1∧e2."""
        e1, e2 = cl2.basis_vectors()
        assert np.allclose(cl2.I.data, op(e1, e2).data)


class TestCl01:
    """Cl(0,1) — anti-Euclidean. e1² = -1."""

    @pytest.fixture
    def cl01(self):
        return Algebra((-1,))

    def test_vector_squares_to_minus_one(self, cl01):
        """e1² = -1 in anti-Euclidean signature."""
        (e1,) = cl01.basis_vectors()
        assert np.isclose((gp(e1, e1)).scalar_part, -1.0)

    def test_norm(self, cl01):
        """Norm uses |e1²| so norm(e1) = 1 despite negative signature."""
        (e1,) = cl01.basis_vectors()
        assert np.isclose(norm(e1), 1.0)

    def test_exp_vector(self, cl01):
        """exp(θe1) = cos(θ) + sin(θ)e1 when e1² = -1."""
        # e1² = -1, so exp(θ e1) = cos(θ) + sin(θ) e1
        (e1,) = cl01.basis_vectors()
        result = exp(0.5 * e1)
        assert np.isclose(result.data[0], np.cos(0.5))
        assert np.isclose(result.data[1], np.sin(0.5))


class TestCl001:
    """Cl(0,0,1) — degenerate. e1² = 0."""

    @pytest.fixture
    def cl001(self):
        return Algebra((0,))

    def test_vector_squares_to_zero(self, cl001):
        """e1² = 0 in degenerate signature."""
        (e1,) = cl001.basis_vectors()
        assert np.isclose((gp(e1, e1)).scalar_part, 0.0)

    def test_exp_null(self, cl001):
        """exp(e1) = 1 + e1 when e1² = 0 (series truncates)."""
        # e1² = 0, so exp(e1) = 1 + e1
        (e1,) = cl001.basis_vectors()
        result = exp(e1)
        assert np.isclose(result.data[0], 1.0)
        assert np.isclose(result.data[1], 1.0)

    def test_inverse_fails(self, cl001):
        """Null vector has no inverse."""
        (e1,) = cl001.basis_vectors()
        with pytest.raises(ValueError, match="not invertible"):
            inverse(e1)

    def test_norm_is_zero(self, cl001):
        """Null vector has norm zero."""
        (e1,) = cl001.basis_vectors()
        assert np.isclose(norm(e1), 0.0)


class TestPseudoscalarLazy:
    """pseudoscalar(lazy=) flag."""

    def test_default_eager(self):
        """pseudoscalar() defaults to eager."""
        alg = Algebra((1, 1, 1))
        assert not alg.pseudoscalar()._is_lazy

    def test_lazy_flag(self):
        """pseudoscalar(lazy=True) returns lazy MV."""
        alg = Algebra((1, 1, 1))
        I = alg.pseudoscalar(lazy=True)
        assert I._is_lazy

    def test_lazy_in_expression(self):
        """Lazy pseudoscalar participates in expression trees."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        I = alg.pseudoscalar(lazy=True).name(latex="I")
        expr = e1 * I
        assert expr._is_lazy
        assert "I" in str(expr)

    def test_lazy_data_matches_eager(self):
        """Lazy and eager pseudoscalar have same numeric data."""
        alg = Algebra((1, 1, 1))
        assert np.allclose(
            alg.pseudoscalar(lazy=True).data,
            alg.pseudoscalar().data,
        )
