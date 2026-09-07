"""Public low-dimensional compositions and explicit provenance contracts.

The retired rotor constructor's validation is not imposed on generic exp.
Historical method identities and observations are retained in ADR-108's archive.
"""

import numpy as np
import pytest

import galaga as ga
from galaga.expression import BladeLiteral, ScalarLiteral, Symbol, evaluate


class TestCl0Helpers:
    def test_rotor_rejects_scalar(self):
        algebra = ga.Algebra(())
        with pytest.raises(ValueError, match="grade must be"):
            algebra.basis_blades(2)
        assert not ga.is_bivector(algebra.scalar(1))
        with pytest.raises(AttributeError, match="rotor"):
            algebra.rotor(algebra.scalar(1), radians=0.5)
        # Generic scalar exponentiation remains valid; it is not a plane-angle API.
        result = ga.exp(algebra.scalar(0.5))
        assert float(result) == pytest.approx(np.exp(0.5))
        assert not ga.is_rotor(result)
        assert algebra.pseudoscalar(expr=True).expr == ScalarLiteral(1)


class TestCl1Helpers:
    @pytest.fixture
    def cl1(self):
        return ga.Algebra((1,))

    def test_project_onto_self(self, cl1):
        (e1,) = cl1.basis_vectors()
        projection = ga.left_contraction(e1, e1) * ga.inverse(e1)
        np.testing.assert_array_equal(projection.data, e1.data)

    def test_reject_from_self(self, cl1):
        (e1,) = cl1.basis_vectors()
        projection = ga.left_contraction(e1, e1) * ga.inverse(e1)
        np.testing.assert_array_equal((e1 - projection).data, cl1.scalar(0).data)

    def test_reflect_in_self(self, cl1):
        (e1,) = cl1.basis_vectors()
        np.testing.assert_array_equal((-e1 * e1 * ga.inverse(e1)).data, (-e1).data)

    def test_rotor_rejects_vector(self, cl1):
        (e1,) = cl1.basis_vectors()
        assert not ga.is_bivector(e1)
        with pytest.raises(AttributeError, match="rotor"):
            cl1.rotor(e1, radians=0.5)
        result = ga.exp(0.25 * e1)
        expected = np.cosh(0.25) + np.sinh(0.25) * e1
        np.testing.assert_allclose(result.data, expected.data, rtol=0, atol=1e-12)
        assert not ga.is_rotor(result)

    def test_rotor_rejects_scalar(self, cl1):
        scalar = cl1.scalar(1)
        assert not ga.is_bivector(scalar)
        with pytest.raises(AttributeError, match="rotor"):
            cl1.rotor(scalar, radians=0.5)
        with pytest.raises(ValueError, match="grade must be"):
            cl1.basis_blades(2)
        assert cl1.pseudoscalar(expr=True).expr == BladeLiteral(1)


class TestCl2Helpers:
    def test_rotor_constructor_applies_expected_rotation(self):
        algebra = ga.Algebra((1, 1))
        e1, e2 = algebra.basis_vectors(expr=True)
        plane = e1 ^ e2
        assert plane * plane == -1
        rotor = ga.exp(-np.pi / 4 * plane)
        result = ga.sandwich(rotor, e1)
        np.testing.assert_allclose(result.data, e2.data, rtol=0, atol=1e-12)
        np.testing.assert_allclose((rotor * ga.reverse(rotor)).data, algebra.scalar(1).data, rtol=0, atol=1e-12)
        np.testing.assert_allclose(evaluate(result.expr, algebra=algebra).data, result.data, rtol=0, atol=1e-12)


class TestPseudoscalarLazy:
    def test_default_eager(self):
        algebra = ga.Algebra((1, 1, 1))
        assert algebra.pseudoscalar().expr is None

    def test_lazy_flag(self):
        algebra = ga.Algebra((1, 1, 1))
        value = algebra.pseudoscalar(expr=True)
        assert value.expr == BladeLiteral(algebra.dim - 1)
        with pytest.raises(TypeError, match="lazy"):
            algebra.pseudoscalar(lazy=True)

    def test_lazy_in_expression(self):
        algebra = ga.Algebra((1, 1, 1))
        e1, _, _ = algebra.basis_vectors(expr=True)
        pseudoscalar = algebra.pseudoscalar(expr=True).named("I")
        value = e1 * pseudoscalar
        assert value.expr.operation_id == "geometric_product"
        assert value.expr.operands == (BladeLiteral(1), Symbol("I"))
        assert value.display("expr/latex") == "e_{1} I"
        assert evaluate(value.expr, algebra=algebra, environment={"I": pseudoscalar}) == algebra.blade(6)
        with pytest.raises(KeyError, match="no value supplied"):
            evaluate(value.expr, algebra=algebra)

    def test_lazy_data_matches_eager(self):
        algebra = ga.Algebra((1, 1, 1))
        tracked, eager = algebra.pseudoscalar(expr=True), algebra.pseudoscalar()
        np.testing.assert_array_equal(tracked.data, eager.data)
        assert hash(tracked) == hash(eager)
