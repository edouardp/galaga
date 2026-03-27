"""Tests for latex_build: Expr → LNode tree → LaTeX string.

Tests the full pipeline: build() → rewrite() → emit() and compares
against expected LaTeX output. This ensures the new three-phase renderer
produces identical results to the old single-pass render_latex().
"""

import numpy as np
from ga import Algebra
from ga.latex_build import build
from ga.latex_emit import emit
from ga.latex_rewrite import rewrite
from ga.symbolic import (
    Sym, Scalar, Add, Sub, Neg, Gp, Op, ScalarMul, ScalarDiv, Div,
    Reverse, Involute, Conjugate, Dual, Undual, Complement, Uncomplement,
    Inverse, Squared, Exp, Log, Grade, Norm, Unit, Even, Odd,
    Lc, Rc, Hi, Dli, Sp, Regressive,
    Commutator, Anticommutator,
)

# Minimal algebra for constructing Sym nodes
_alg = Algebra((1, 1, 1))
_e1, _e2, _e3 = _alg.basis_vectors()


def _sym(name, mv=None, latex=None):
    """Helper to create a Sym with proper MV backing."""
    return Sym(mv or _e1, name, name_latex=latex or name)


def _latex(expr):
    """Full pipeline: build → rewrite → emit."""
    return emit(rewrite(build(expr)))


# Helpers
a = _sym("a")
b = _sym("b")
theta = _sym("θ", latex=r"\theta")


class TestAtoms:
    def test_sym(self):
        assert _latex(a) == "a"

    def test_sym_latex_name(self):
        assert _latex(theta) == r"\theta"

    def test_scalar(self):
        assert _latex(Scalar(3.14)) == "3.14"

    def test_scalar_int(self):
        assert _latex(Scalar(2)) == "2"


class TestArithmetic:
    def test_add(self):
        assert _latex(Add(a, b)) == "a + b"

    def test_sub(self):
        assert _latex(Sub(a, b)) == "a - b"

    def test_neg(self):
        assert _latex(Neg(a)) == "-a"

    def test_neg_add(self):
        assert _latex(Neg(Add(a, b))) == r"-\left(a + b\right)"

    def test_scalar_mul(self):
        assert _latex(ScalarMul(3, a)) == "3 a"

    def test_scalar_mul_neg1(self):
        assert _latex(ScalarMul(-1, a)) == "-a"

    def test_scalar_div(self):
        assert _latex(ScalarDiv(a, 2)) == r"\frac{a}{2}"

    def test_div(self):
        assert _latex(Div(a, b)) == r"\frac{a}{b}"


class TestProducts:
    def test_gp(self):
        assert _latex(Gp(a, b)) == "a b"

    def test_op(self):
        assert _latex(Op(a, b)) == r"a \wedge b"

    def test_lc(self):
        assert _latex(Lc(a, b)) == r"a \;\lrcorner\; b"

    def test_rc(self):
        assert _latex(Rc(a, b)) == r"a \;\llcorner\; b"

    def test_regressive(self):
        assert _latex(Regressive(a, b)) == r"a \vee b"


class TestUnary:
    def test_reverse(self):
        assert _latex(Reverse(a)) == r"\tilde{a}"

    def test_reverse_compound(self):
        assert _latex(Reverse(Add(a, b))) == r"\widetilde{a + b}"

    def test_involute(self):
        assert _latex(Involute(a)) == r"\hat{a}"

    def test_conjugate(self):
        assert _latex(Conjugate(a)) == r"\bar{a}"

    def test_conjugate_compound(self):
        assert _latex(Conjugate(Add(a, b))) == r"\overline{a + b}"

    def test_dual(self):
        assert _latex(Dual(a)) == "a^*"

    def test_undual(self):
        assert _latex(Undual(a)) == "a^{*^{-1}}"

    def test_complement(self):
        assert _latex(Complement(a)) == r"a^{\complement}"

    def test_uncomplement(self):
        assert _latex(Uncomplement(a)) == r"a^{\complement^{-1}}"

    def test_inverse(self):
        assert _latex(Inverse(a)) == "a^{-1}"

    def test_squared(self):
        assert _latex(Squared(a)) == "a^2"


class TestPostfixOnPostfix:
    def test_undual_of_dual(self):
        assert _latex(Undual(Dual(a))) == r"\left(a^*\right)^{*^{-1}}"

    def test_inverse_of_dual(self):
        assert _latex(Inverse(Dual(a))) == r"\left(a^*\right)^{-1}"

    def test_dual_of_inverse(self):
        assert _latex(Dual(Inverse(a))) == r"\left(a^{-1}\right)^*"


class TestPostfixOnSup:
    """Postfix symbols starting with ^ must brace-wrap Sup children."""

    def test_postfix_dagger_on_exp(self):
        """reverse(exp(a)) with dagger notation: {e^{a}}^{\\dagger}"""
        from ga.notation import Notation, NotationRule
        n = Notation()
        n.set("Reverse", "latex", NotationRule(kind="superscript", symbol=r"\dagger"))
        from ga.latex_build import build
        from ga.latex_emit import emit
        from ga.latex_rewrite import rewrite
        tree = build(Reverse(Exp(a)), n)
        result = emit(rewrite(tree))
        assert result == r"{e^{a}}^{\dagger}"

    def test_superscript_on_simple(self):
        """reverse(a) with superscript dagger: a^{\\dagger}"""
        from ga.notation import Notation, NotationRule
        n = Notation()
        n.set("Reverse", "latex", NotationRule(kind="superscript", symbol=r"\dagger"))
        from ga.latex_build import build
        from ga.latex_emit import emit
        from ga.latex_rewrite import rewrite
        tree = build(Reverse(a), n)
        result = emit(rewrite(tree))
        assert result == r"a^{\dagger}"

    def test_postfix_star_on_exp(self):
        """dual(exp(a)): {e^{a}}^*"""
        result = _latex(Dual(Exp(a)))
        assert result == r"{e^{a}}^*"

    def test_postfix_inverse_on_exp(self):
        """inverse(exp(a)): {e^{a}}^{-1}"""
        result = _latex(Inverse(Exp(a)))
        assert result == r"{e^{a}}^{-1}"

    def test_postfix_squared_on_exp(self):
        """squared(exp(a)): {e^{a}}^2"""
        result = _latex(Squared(Exp(a)))
        assert result == r"{e^{a}}^2"

    def test_postfix_on_non_sup_no_braces(self):
        """Postfix on a non-Sup node should NOT add extra braces."""
        result = _latex(Dual(a))
        assert result == "a^*"
        assert "{a}" not in result

    def test_complement_on_exp(self):
        result = _latex(Complement(Exp(a)))
        assert result == r"{e^{a}}^{\complement}"


class TestWrap:
    def test_grade(self):
        assert _latex(Grade(a, 1)) == r"\langle a \rangle_{1}"

    def test_norm(self):
        assert _latex(Norm(a)) == r"\lVert a \rVert"

    def test_even(self):
        assert _latex(Even(a)) == r"\langle a \rangle_{\text{even}}"

    def test_odd(self):
        assert _latex(Odd(a)) == r"\langle a \rangle_{\text{odd}}"

    def test_unit_atom(self):
        assert _latex(Unit(a)) == r"\hat{a}"

    def test_unit_compound(self):
        result = _latex(Unit(Add(a, b)))
        # Unit of compound uses wide hat accent
        assert r"\widehat" in result


class TestExp:
    def test_simple(self):
        assert _latex(Exp(a)) == "e^{a}"

    def test_exp_with_frac_uses_tfrac(self):
        """The key test: frac inside exp superscript becomes inline slash."""
        expr = Exp(ScalarDiv(theta, 2))
        assert _latex(expr) == r"e^{\theta/2}"

    def test_exp_with_product_and_frac(self):
        expr = Exp(Gp(ScalarDiv(Neg(theta), 2), b))
        result = _latex(expr)
        assert "/" in result
        assert r"\frac" not in result


class TestLog:
    def test_simple(self):
        assert _latex(Log(a)) == r"\log\left(a\right)"

    def test_log_of_exp(self):
        assert _latex(Log(Exp(a))) == r"\log\left(e^{a}\right)"


class TestCommutator:
    def test_commutator(self):
        assert _latex(Commutator(a, b)) == r"[a,\, b]"

    def test_anticommutator(self):
        result = _latex(Anticommutator(a, b))
        # Should have braces or similar
        assert "a" in result and "b" in result


class TestPrecedence:
    def test_add_in_gp(self):
        expr = Gp(Add(a, b), a)
        assert _latex(expr) == r"\left(a + b\right) a"

    def test_gp_in_add(self):
        expr = Add(Gp(a, b), a)
        assert _latex(expr) == "a b + a"

    def test_nested_frac_outside_sup_stays_frac(self):
        """Frac not inside Sup should remain \\frac."""
        expr = ScalarDiv(a, 2)
        assert _latex(expr) == r"\frac{a}{2}"
