"""Tests for the precedence-aware tree-walking renderer.

Tests are written FIRST — the renderer must pass all of these.
"""

import pytest
from ga import Algebra
from ga.symbolic import (
    Sym, Scalar, Gp, Op, Add, Sub, Neg, ScalarMul, ScalarDiv, Div,
    Reverse, Involute, Conjugate, Dual, Undual, Inverse, Squared, Exp,
    Grade, Norm, Unit, Even, Odd,
    Lc, Rc, Hi, Dli, Sp,
    Commutator, Anticommutator, LieBracket, JordanProduct,
)


@pytest.fixture
def alg():
    return Algebra((1, 1, 1))


@pytest.fixture
def syms(alg):
    e1, e2, e3 = alg.basis_vectors()
    a = Sym(e1, "a")
    b = Sym(e2, "b")
    c = Sym(e3, "c")
    return a, b, c


# ============================================================
# Import the renderer under test
# ============================================================

from ga.render import render, render_latex


# ============================================================
# Atoms
# ============================================================

class TestAtoms:
    def test_sym(self, syms):
        a, _, _ = syms
        assert render(a) == "a"

    def test_scalar_int(self):
        assert render(Scalar(3)) == "3"

    def test_scalar_float(self):
        assert render(Scalar(2.5)) == "2.5"

    def test_scalar_neg(self):
        assert render(Scalar(-1)) == "-1"


# ============================================================
# Negation
# ============================================================

class TestNeg:
    def test_neg_atom(self, syms):
        a, _, _ = syms
        assert render(Neg(a)) == "-a"

    def test_neg_sum(self, syms):
        a, b, _ = syms
        assert render(Neg(Add(a, b))) == "-(a + b)"

    def test_neg_product(self, syms):
        a, b, _ = syms
        assert render(Neg(Gp(a, b))) == "-ab"

    def test_double_neg(self, syms):
        a, _, _ = syms
        assert render(Neg(Neg(a))) == "--a"


# ============================================================
# Scalar multiplication and division
# ============================================================

class TestScalarMulDiv:
    def test_scalar_mul(self, syms):
        a, _, _ = syms
        assert render(ScalarMul(3, a)) == "3a"

    def test_scalar_mul_neg1(self, syms):
        a, _, _ = syms
        assert render(ScalarMul(-1, a)) == "-a"

    def test_scalar_mul_sum(self, syms):
        a, b, _ = syms
        assert render(ScalarMul(2, Add(a, b))) == "2(a + b)"

    def test_scalar_div(self, syms):
        a, _, _ = syms
        assert render(ScalarDiv(a, 2)) == "a/2"

    def test_scalar_div_sum(self, syms):
        a, b, _ = syms
        assert render(ScalarDiv(Add(a, b), 2)) == "(a + b)/2"


# ============================================================
# Geometric product (juxtaposition)
# ============================================================

class TestGp:
    def test_two_atoms(self, syms):
        a, b, _ = syms
        assert render(Gp(a, b)) == "ab"

    def test_three_atoms(self, syms):
        a, b, c = syms
        assert render(Gp(Gp(a, b), c)) == "abc"

    def test_sum_left(self, syms):
        a, b, c = syms
        assert render(Gp(Add(a, b), c)) == "(a + b)c"

    def test_sum_right(self, syms):
        a, b, c = syms
        assert render(Gp(a, Add(b, c))) == "a(b + c)"

    def test_sum_both(self, syms):
        a, b, c = syms
        assert render(Gp(Add(a, b), Add(b, c))) == "(a + b)(b + c)"

    def test_wedge_in_gp(self, syms):
        """Wedge inside gp needs parens since wedge has lower precedence."""
        a, b, c = syms
        assert render(Gp(Op(a, b), c)) == "(a∧b)c"

    def test_gp_of_wedge_right(self, syms):
        a, b, c = syms
        assert render(Gp(a, Op(b, c))) == "a(b∧c)"


# ============================================================
# Outer (wedge) product
# ============================================================

class TestOp:
    def test_two_atoms(self, syms):
        a, b, _ = syms
        assert render(Op(a, b)) == "a∧b"

    def test_sum_in_wedge(self, syms):
        a, b, c = syms
        assert render(Op(Add(a, b), c)) == "(a + b)∧c"

    def test_scalar_mul_in_wedge(self, syms):
        a, b, _ = syms
        assert render(Op(ScalarMul(2, a), b)) == "(2a)∧b"

    def test_scalar_mul_of_wedge(self, syms):
        a, b, _ = syms
        assert render(ScalarMul(2, Op(a, b))) == "2a∧b"

    def test_associative_left(self, syms):
        a, b, c = syms
        assert render(Op(Op(a, b), c)) == "a∧b∧c"

    def test_associative_right(self, syms):
        a, b, c = syms
        assert render(Op(a, Op(b, c))) == "a∧b∧c"

    def test_associative_both(self, syms):
        a, b, c = syms
        d = Sym(syms[0]._mv, "d")
        assert render(Op(Op(a, b), Op(c, d))) == "a∧b∧c∧d"


# ============================================================
# Addition and subtraction
# ============================================================

class TestAddSub:
    def test_add(self, syms):
        a, b, _ = syms
        assert render(Add(a, b)) == "a + b"

    def test_sub(self, syms):
        a, b, _ = syms
        assert render(Sub(a, b)) == "a - b"

    def test_add_three(self, syms):
        a, b, c = syms
        assert render(Add(Add(a, b), c)) == "a + b + c"

    def test_sub_of_sum(self, syms):
        a, b, c = syms
        # a - (b + c) — the RHS needs parens because subtraction
        assert render(Sub(a, Add(b, c))) == "a - (b + c)"


# ============================================================
# Postfix unary: reverse, involute, conjugate, dual, inverse, squared
# ============================================================

class TestPostfixUnary:
    def test_reverse_atom(self, syms):
        a, _, _ = syms
        assert render(Reverse(a)) == "a\u0303"

    def test_reverse_sum(self, syms):
        a, b, _ = syms
        assert render(Reverse(Add(a, b))) == "~(a + b)"

    def test_reverse_product(self, syms):
        a, b, _ = syms
        assert render(Reverse(Gp(a, b))) == "~(ab)"

    def test_involute_atom(self, syms):
        a, _, _ = syms
        assert render(Involute(a)) == "a\u0302"

    def test_involute_sum(self, syms):
        a, b, _ = syms
        assert render(Involute(Add(a, b))) == "inv(a + b)"

    def test_conjugate_atom(self, syms):
        a, _, _ = syms
        assert render(Conjugate(a)) == "a\u0304"

    def test_conjugate_sum(self, syms):
        a, b, _ = syms
        assert render(Conjugate(Add(a, b))) == "conj(a + b)"

    def test_dual_atom(self, syms):
        a, _, _ = syms
        assert render(Dual(a)) == "a⋆"

    def test_dual_sum(self, syms):
        a, b, _ = syms
        assert render(Dual(Add(a, b))) == "(a + b)⋆"

    def test_dual_product(self, syms):
        a, b, _ = syms
        assert render(Dual(Gp(a, b))) == "(ab)⋆"

    def test_undual_atom(self, syms):
        a, _, _ = syms
        assert render(Undual(a)) == "a⋆⁻¹"

    def test_inverse_atom(self, syms):
        a, _, _ = syms
        assert render(Inverse(a)) == "a⁻¹"

    def test_inverse_sum(self, syms):
        a, b, _ = syms
        assert render(Inverse(Add(a, b))) == "(a + b)⁻¹"

    def test_inverse_product(self, syms):
        a, b, _ = syms
        assert render(Inverse(Gp(a, b))) == "(ab)⁻¹"

    def test_squared_atom(self, syms):
        a, _, _ = syms
        assert render(Squared(a)) == "a²"

    def test_squared_sum(self, syms):
        a, b, _ = syms
        assert render(Squared(Add(a, b))) == "(a + b)²"

    def test_squared_product(self, syms):
        a, b, _ = syms
        assert render(Squared(Gp(a, b))) == "(ab)²"


# ============================================================
# Grade, Norm, Unit, Exp — bracket-style (no precedence issue)
# ============================================================

class TestBracketOps:
    def test_grade(self, syms):
        a, _, _ = syms
        assert render(Grade(a, 1)) == "⟨a⟩₁"

    def test_grade_of_sum(self, syms):
        a, b, _ = syms
        assert render(Grade(Add(a, b), 2)) == "⟨a + b⟩₂"

    def test_norm(self, syms):
        a, _, _ = syms
        assert render(Norm(a)) == "‖a‖"

    def test_unit_atom(self, syms):
        a, _, _ = syms
        assert render(Unit(a)) == "a\u0302"

    def test_unit_sum(self, syms):
        a, b, _ = syms
        assert render(Unit(Add(a, b))) == "(a + b)/‖a + b‖"

    def test_exp(self, syms):
        a, _, _ = syms
        assert render(Exp(a)) == "exp(a)"

    def test_exp_sum(self, syms):
        a, b, _ = syms
        assert render(Exp(Add(a, b))) == "exp(a + b)"


# ============================================================
# Inner products and contractions
# ============================================================

class TestInnerProducts:
    def test_left_contraction(self, syms):
        a, b, _ = syms
        assert render(Lc(a, b)) == "a⌋b"

    def test_right_contraction(self, syms):
        a, b, _ = syms
        assert render(Rc(a, b)) == "a⌊b"

    def test_hestenes(self, syms):
        a, b, _ = syms
        assert render(Hi(a, b)) == "a·b"

    def test_doran_lasenby(self, syms):
        a, b, _ = syms
        assert render(Dli(a, b)) == "a·b"

    def test_scalar_product(self, syms):
        a, b, _ = syms
        assert render(Sp(a, b)) == "a∗b"

    def test_contraction_of_sum(self, syms):
        a, b, c = syms
        assert render(Lc(Add(a, b), c)) == "(a + b)⌋c"


# ============================================================
# Commutator family
# ============================================================

class TestCommutators:
    def test_commutator(self, syms):
        a, b, _ = syms
        assert render(Commutator(a, b)) == "[a, b]"

    def test_anticommutator(self, syms):
        a, b, _ = syms
        assert render(Anticommutator(a, b)) == "{a, b}"

    def test_lie_bracket(self, syms):
        a, b, _ = syms
        assert render(LieBracket(a, b)) == "½[a, b]"

    def test_jordan_product(self, syms):
        a, b, _ = syms
        assert render(JordanProduct(a, b)) == "½{a, b}"


# ============================================================
# Division
# ============================================================

class TestDiv:
    def test_div_atoms(self, syms):
        a, b, _ = syms
        assert render(Div(a, b)) == "a/b"

    def test_div_sum_numerator(self, syms):
        a, b, c = syms
        assert render(Div(Add(a, b), c)) == "(a + b)/c"

    def test_div_sum_denominator(self, syms):
        a, b, c = syms
        assert render(Div(a, Add(b, c))) == "a/(b + c)"

    def test_div_product_denominator(self, syms):
        a, b, c = syms
        assert render(Div(a, Gp(b, c))) == "a/(bc)"


# ============================================================
# Complex compositions
# ============================================================

class TestCompositions:
    def test_sandwich(self, syms):
        """R * v * ~R with R=a, v=b"""
        a, b, _ = syms
        expr = Gp(Gp(a, b), Reverse(a))
        expected = "ab" + "a" + "\u0303"
        assert render(expr) == expected

    def test_sandwich_named(self, alg):
        e1, e2, _ = alg.basis_vectors()
        R = Sym(e1 * e2, "R")
        v = Sym(e1, "v")
        expr = Gp(Gp(R, v), Reverse(R))
        assert render(expr) == "RvR\u0303"

    def test_reverse_of_sum_in_product(self, syms):
        a, b, c = syms
        expr = Gp(Reverse(Add(a, b)), c)
        assert render(expr) == "~(a + b)c"

    def test_product_times_reverse_sum(self, syms):
        a, b, c = syms
        expr = Gp(c, Reverse(Add(a, b)))
        assert render(expr) == "c~(a + b)"

    def test_sum_sandwich(self, syms):
        a, b, c = syms
        expr = Gp(Gp(Add(a, b), c), Reverse(Add(a, b)))
        assert render(expr) == "(a + b)c~(a + b)"

    def test_scalar_mul_in_exp(self, syms):
        a, b, _ = syms
        expr = Exp(ScalarDiv(Neg(Gp(a, b)), 2))
        assert render(expr) == "exp(-ab/2)"

    def test_grade_of_sandwich(self, syms):
        a, b, _ = syms
        R, v = a, b
        expr = Grade(Gp(Gp(R, v), Reverse(R)), 1)
        assert render(expr) == "⟨aba\u0303⟩₁"

    def test_nested_reverse(self, syms):
        a, _, _ = syms
        expr = Reverse(Reverse(a))
        s = render(expr)
        assert "a" in s

    def test_wedge_plus_scalar_wedge(self, syms):
        a, b, c = syms
        expr = Add(Op(a, b), ScalarMul(2, Op(b, c)))
        assert render(expr) == "a∧b + 2b∧c"

    def test_neg_scalar_mul_in_product(self, syms):
        a, b, _ = syms
        expr = Gp(ScalarMul(-1, a), b)
        assert render(expr) == "(-a)b" or render(expr) == "-ab"


# ============================================================
# LaTeX rendering
# ============================================================

class TestLatex:
    def test_sym(self, syms):
        a, _, _ = syms
        assert render_latex(a) == "a"

    def test_gp(self, syms):
        a, b, _ = syms
        assert render_latex(Gp(a, b)) == "a b"

    def test_wedge(self, syms):
        a, b, _ = syms
        assert render_latex(Op(a, b)) == r"a \wedge b"

    def test_add(self, syms):
        a, b, _ = syms
        assert render_latex(Add(a, b)) == "a + b"

    def test_reverse(self, syms):
        a, _, _ = syms
        assert render_latex(Reverse(a)) == r"\tilde{a}"

    def test_reverse_sum(self, syms):
        a, b, _ = syms
        assert render_latex(Reverse(Add(a, b))) == r"\widetilde{a + b}"

    def test_grade(self, syms):
        a, _, _ = syms
        assert render_latex(Grade(a, 1)) == r"\langle a \rangle_{1}"

    def test_scalar_div(self, syms):
        a, _, _ = syms
        assert render_latex(ScalarDiv(a, 2)) == r"\frac{a}{2}"

    def test_div(self, syms):
        a, b, _ = syms
        assert render_latex(Div(a, b)) == r"\frac{a}{b}"

    def test_exp(self, syms):
        a, _, _ = syms
        assert render_latex(Exp(a)) == r"e^{a}"

    def test_squared(self, syms):
        a, _, _ = syms
        assert render_latex(Squared(a)) == "a^2"

    def test_squared_sum(self, syms):
        a, b, _ = syms
        assert render_latex(Squared(Add(a, b))) == r"\left(a + b\right)^2"

    def test_inverse_product(self, syms):
        a, b, _ = syms
        assert render_latex(Inverse(Gp(a, b))) == r"\left(a b\right)^{-1}"

    def test_sandwich_latex(self, alg):
        e1, e2, _ = alg.basis_vectors()
        R = Sym(e1 * e2, "R")
        v = Sym(e1, "v")
        expr = Gp(Gp(R, v), Reverse(R))
        assert render_latex(expr) == r"R v \tilde{R}"


# ============================================================
# Mixed infix/postfix precedence cases
# ============================================================

class TestMixedInfixPostfix:
    """Test precedence interactions between infix binary ops and postfix unary ops."""

    def test_reverse_in_gp_left(self, syms):
        """~a * b — reverse binds tighter than gp"""
        a, b, _ = syms
        expr = Gp(Reverse(a), b)
        assert render(expr) == "a\u0303b"

    def test_reverse_in_gp_right(self, syms):
        """a * ~b"""
        a, b, _ = syms
        expr = Gp(a, Reverse(b))
        assert render(expr) == "ab\u0303"

    def test_reverse_of_gp(self, syms):
        """~(a * b) — needs parens"""
        a, b, _ = syms
        expr = Reverse(Gp(a, b))
        assert render(expr) == "~(ab)"

    def test_inverse_in_gp(self, syms):
        """a⁻¹ * b"""
        a, b, _ = syms
        expr = Gp(Inverse(a), b)
        assert render(expr) == "a⁻¹b"

    def test_inverse_of_gp(self, syms):
        """(ab)⁻¹"""
        a, b, _ = syms
        expr = Inverse(Gp(a, b))
        assert render(expr) == "(ab)⁻¹"

    def test_squared_in_gp(self, syms):
        """a² * b"""
        a, b, _ = syms
        expr = Gp(Squared(a), b)
        assert render(expr) == "a²b"

    def test_squared_of_gp(self, syms):
        """(ab)²"""
        a, b, _ = syms
        expr = Squared(Gp(a, b))
        assert render(expr) == "(ab)²"

    def test_dual_in_wedge(self, syms):
        """a⋆ ∧ b"""
        a, b, _ = syms
        expr = Op(Dual(a), b)
        assert render(expr) == "a⋆∧b"

    def test_dual_of_wedge(self, syms):
        """(a∧b)⋆"""
        a, b, _ = syms
        expr = Dual(Op(a, b))
        assert render(expr) == "(a∧b)⋆"

    def test_reverse_in_add(self, syms):
        """~a + b — no parens needed"""
        a, b, _ = syms
        expr = Add(Reverse(a), b)
        assert render(expr) == "a\u0303 + b"

    def test_reverse_of_add(self, syms):
        """~(a + b) — needs prefix fallback"""
        a, b, _ = syms
        expr = Reverse(Add(a, b))
        assert render(expr) == "~(a + b)"

    def test_neg_of_reverse(self, syms):
        """-~a"""
        a, _, _ = syms
        expr = Neg(Reverse(a))
        assert render(expr) == "-a\u0303"

    def test_reverse_of_neg(self, syms):
        """~(-a)"""
        a, _, _ = syms
        expr = Reverse(Neg(a))
        assert render(expr) == "~(-a)"

    def test_scalar_mul_of_reverse(self, syms):
        """3~a"""
        a, _, _ = syms
        expr = ScalarMul(3, Reverse(a))
        assert render(expr) == "3a\u0303"

    def test_reverse_of_scalar_mul(self, syms):
        """~(3a)"""
        a, _, _ = syms
        expr = Reverse(ScalarMul(3, a))
        assert render(expr) == "~(3a)"

    def test_inverse_of_sum_in_gp(self, syms):
        """(a + b)⁻¹ * c"""
        a, b, c = syms
        expr = Gp(Inverse(Add(a, b)), c)
        assert render(expr) == "(a + b)⁻¹c"

    def test_gp_of_inverse_sum(self, syms):
        """c * (a + b)⁻¹"""
        a, b, c = syms
        expr = Gp(c, Inverse(Add(a, b)))
        assert render(expr) == "c(a + b)⁻¹"

    def test_sandwich_with_reverse(self, alg):
        """R v ~R — the classic sandwich"""
        e1, e2, _ = alg.basis_vectors()
        R = Sym(e1 * e2, "R")
        v = Sym(e1, "v")
        expr = Gp(Gp(R, v), Reverse(R))
        assert render(expr) == "RvR\u0303"

    def test_grade_of_sandwich(self, alg):
        """⟨RvR̃⟩₁"""
        e1, e2, _ = alg.basis_vectors()
        R = Sym(e1 * e2, "R")
        v = Sym(e1, "v")
        expr = Grade(Gp(Gp(R, v), Reverse(R)), 1)
        assert render(expr) == "⟨RvR\u0303⟩₁"

    def test_exp_of_neg_product_div(self, syms):
        """exp(-ab/2)"""
        a, b, _ = syms
        expr = Exp(ScalarDiv(Neg(Gp(a, b)), 2))
        assert render(expr) == "exp(-ab/2)"

    def test_squared_of_sum_in_gp(self, syms):
        """(a + b)² * c"""
        a, b, c = syms
        expr = Gp(Squared(Add(a, b)), c)
        assert render(expr) == "(a + b)²c"


class TestMixedInfixPostfixLatex:
    """LaTeX versions of mixed precedence cases."""

    def test_reverse_of_gp_latex(self, syms):
        a, b, _ = syms
        expr = Reverse(Gp(a, b))
        assert render_latex(expr) == r"\widetilde{a b}"

    def test_inverse_of_gp_latex(self, syms):
        a, b, _ = syms
        expr = Inverse(Gp(a, b))
        assert render_latex(expr) == r"\left(a b\right)^{-1}"

    def test_sandwich_latex(self, alg):
        e1, e2, _ = alg.basis_vectors()
        R = Sym(e1 * e2, "R")
        v = Sym(e1, "v")
        expr = Gp(Gp(R, v), Reverse(R))
        assert render_latex(expr) == r"R v \tilde{R}"

    def test_dual_of_sum_latex(self, syms):
        a, b, _ = syms
        expr = Dual(Add(a, b))
        assert render_latex(expr) == r"\left(a + b\right)^*"

    def test_conjugate_of_sum_latex(self, syms):
        a, b, _ = syms
        expr = Conjugate(Add(a, b))
        assert render_latex(expr) == r"\overline{a + b}"
