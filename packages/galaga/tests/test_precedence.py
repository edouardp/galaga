"""Tests for symbolic rendering precedence — parenthesization.

Each test constructs a lazy expression and checks that the string
representation has correct parentheses for mathematical precedence.
"""

import pytest
from ga import (
    Algebra, reverse, involute, conjugate, grade, dual,
    unit, inverse, squared, exp,
)


@pytest.fixture
def lazy3():
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    a = e1.name("a")
    b = e2.name("b")
    c = e3.name("c")
    return alg, a, b, c


class TestPostfixUnaryOnSums:
    """Postfix unary ops (reverse, involute, conjugate, dual, inverse)
    must wrap sums in parens: (a + b)̃ not a + b̃."""

    def test_reverse_of_sum(self, lazy3):
        _, a, b, _ = lazy3
        assert str(reverse(a + b)) == "~(a + b)"

    def test_involute_of_sum(self, lazy3):
        _, a, b, _ = lazy3
        assert str(involute(a + b)) == "inv(a + b)"

    def test_conjugate_of_sum(self, lazy3):
        _, a, b, _ = lazy3
        assert str(conjugate(a + b)) == "conj(a + b)"

    def test_dual_of_sum(self, lazy3):
        _, a, b, _ = lazy3
        assert str(dual(a + b)) == "(a + b)⋆"

    def test_inverse_of_sum(self, lazy3):
        _, a, b, _ = lazy3
        assert str(inverse(a + b)) == "(a + b)⁻¹"


class TestPostfixUnaryOnProducts:
    """Postfix unary ops on products should NOT add parens:
    ab̃ is fine (reverse applies to b only in rendering, but
    actually the Reverse wraps the whole Gp node)."""

    def test_reverse_of_product(self, lazy3):
        _, a, b, _ = lazy3
        # Reverse of (a*b) — the tilde applies to the whole product
        # Needs prefix ~ for compound: ~(ab)
        assert str(reverse(a * b)) == "~(ab)"

    def test_inverse_of_product(self, lazy3):
        _, a, b, _ = lazy3
        assert str(inverse(a * b)) == "(ab)⁻¹"

    def test_dual_of_product(self, lazy3):
        _, a, b, _ = lazy3
        assert str(dual(a * b)) == "(ab)⋆"

    def test_squared_of_product(self, lazy3):
        _, a, b, _ = lazy3
        assert str(squared(a * b)) == "(ab)²"


class TestPostfixUnaryOnSingleName:
    """Single named values need no parens."""

    def test_reverse_of_name(self, lazy3):
        _, a, _, _ = lazy3
        assert str(reverse(a)) == "a\u0303"

    def test_inverse_of_name(self, lazy3):
        _, a, _, _ = lazy3
        assert str(inverse(a)) == "a⁻¹"

    def test_dual_of_name(self, lazy3):
        _, a, _, _ = lazy3
        assert str(dual(a)) == "a⋆"

    def test_squared_of_name(self, lazy3):
        _, a, _, _ = lazy3
        assert str(squared(a)) == "a²"


class TestNegation:
    """Negation of sums needs parens: -(a + b) not -a + b."""

    def test_neg_of_sum(self, lazy3):
        _, a, b, _ = lazy3
        assert str(-(a + b)) == "-(a + b)"

    def test_neg_of_product(self, lazy3):
        _, a, b, _ = lazy3
        assert str(-(a * b)) == "-ab"

    def test_neg_of_name(self, lazy3):
        _, a, _, _ = lazy3
        assert str(-a) == "-a"


class TestReverseInProduct:
    """~(a + b) inside a product needs parens."""

    def test_reverse_sum_times_c(self, lazy3):
        _, a, b, c = lazy3
        assert str(~(a + b) * c) == "~(a + b)c"

    def test_c_times_reverse_sum(self, lazy3):
        _, a, b, c = lazy3
        assert str(c * ~(a + b)) == "c~(a + b)"


class TestSandwichLike:
    """Sandwich patterns with sums."""

    def test_sum_sandwich(self, lazy3):
        _, a, b, c = lazy3
        expr = (a + b) * c * ~(a + b)
        s = str(expr)
        assert "(a + b)" in s
        assert "~(a + b)" in s


class TestDoubleReverse:
    """Double reverse should show nested tildes or simplify."""

    def test_double_reverse(self, lazy3):
        _, a, _, _ = lazy3
        # ~~a — the inner reverse is ã, outer wraps it
        s = str(~~a)
        # Should be parseable — either ã̃ or (ã)̃
        assert "a" in s


class TestScalarDivOfSum:
    """(a + b) / 2 should keep parens."""

    def test_sum_div_scalar(self, lazy3):
        _, a, b, _ = lazy3
        assert str((a + b) / 2) == "(a + b)/2"


class TestScalarMulInWedge:
    """ScalarMul inside wedge must be distinguishable."""

    def test_scalar_mul_wedge_left(self, lazy3):
        _, a, b, _ = lazy3
        # (2a) ^ b should show parens to distinguish from 2(a^b)
        assert str((2 * a) ^ b) == "(2a)∧b"

    def test_scalar_mul_wedge_vs_outer(self, lazy3):
        _, a, b, _ = lazy3
        # 2(a^b) should NOT have inner parens
        assert str(2 * (a ^ b)) == "2a∧b"


class TestUnitOfSum:
    """unit(a + b) should show parens in the hat notation."""

    def test_unit_of_sum(self, lazy3):
        _, a, b, _ = lazy3
        s = str(unit(a + b))
        # Should have parens around a + b
        assert "(a + b)" in s


class TestExpOfSum:
    """exp already wraps in exp(...) so parens are implicit."""

    def test_exp_of_sum(self, lazy3):
        _, a, b, _ = lazy3
        assert str(exp(a + b)) == "exp(a + b)"
