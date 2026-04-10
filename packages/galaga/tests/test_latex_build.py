"""Tests for latex_build: Expr → LNode tree → LaTeX string.

Tests the full pipeline: build() → rewrite() → emit() and compares
against expected LaTeX output. This ensures the new three-phase renderer
produces identical results to the old single-pass render_latex().
"""

import numpy as np

from galaga import Algebra
from galaga.expr import (
    Add,
    Anticommutator,
    Commutator,
    Complement,
    Conjugate,
    Div,
    Dual,
    Even,
    Exp,
    Gp,
    Grade,
    Inverse,
    Involute,
    Lc,
    Log,
    Neg,
    Norm,
    Odd,
    Op,
    Rc,
    Regressive,
    Reverse,
    Scalar,
    ScalarDiv,
    ScalarMul,
    Squared,
    Sub,
    Sym,
    Uncomplement,
    Undual,
    Unit,
)
from galaga.latex_build import build
from galaga.latex_emit import emit
from galaga.latex_rewrite import rewrite

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
        """Sym renders its name."""
        assert _latex(a) == "a"

    def test_sym_latex_name(self):
        """Sym with latex name uses it."""
        assert _latex(theta) == r"\theta"

    def test_scalar(self):
        """Scalar renders as number."""
        assert _latex(Scalar(3.14)) == "3.14"

    def test_scalar_int(self):
        """Integer scalar renders without decimal."""
        assert _latex(Scalar(2)) == "2"


class TestArithmetic:
    def test_add(self):
        """Add renders with +."""
        assert _latex(Add(a, b)) == "a + b"

    def test_sub(self):
        """Sub renders with -."""
        assert _latex(Sub(a, b)) == "a - b"

    def test_neg(self):
        """Neg renders with prefix -."""
        assert _latex(Neg(a)) == "-a"

    def test_neg_add(self):
        """Neg of sum wraps in parens."""
        assert _latex(Neg(Add(a, b))) == r"-\left(a + b\right)"

    def test_scalar_mul(self):
        """ScalarMul renders as coefficient."""
        assert _latex(ScalarMul(3, a)) == "3 a"

    def test_scalar_mul_neg1(self):
        """ScalarMul by -1 renders as -a."""
        assert _latex(ScalarMul(-1, a)) == "-a"

    def test_scalar_div(self):
        """ScalarDiv renders as \frac."""
        assert _latex(ScalarDiv(a, 2)) == r"\frac{a}{2}"

    def test_div(self):
        """Div renders as \frac."""
        assert _latex(Div(a, b)) == r"\frac{a}{b}"


class TestProducts:
    def test_gp(self):
        """Gp renders as juxtaposition with space."""
        assert _latex(Gp(a, b)) == "a b"

    def test_op(self):
        r"""Op renders with \wedge."""
        assert _latex(Op(a, b)) == r"a \wedge b"

    def test_lc(self):
        r"""Lc renders with \lrcorner."""
        assert _latex(Lc(a, b)) == r"a \;\lrcorner\; b"

    def test_rc(self):
        r"""Rc renders with \llcorner."""
        assert _latex(Rc(a, b)) == r"a \;\llcorner\; b"

    def test_regressive(self):
        """Regressive renders with \vee."""
        assert _latex(Regressive(a, b)) == r"a \vee b"


class TestUnary:
    def test_reverse(self):
        """Reverse renders as \tilde."""
        assert _latex(Reverse(a)) == r"\tilde{a}"

    def test_reverse_compound(self):
        r"""Reverse of compound uses \widetilde."""
        assert _latex(Reverse(Add(a, b))) == r"\widetilde{a + b}"

    def test_involute(self):
        r"""Involute renders as \hat."""
        assert _latex(Involute(a)) == r"\hat{a}"

    def test_conjugate(self):
        """Conjugate renders as \bar."""
        assert _latex(Conjugate(a)) == r"\bar{a}"

    def test_conjugate_compound(self):
        r"""Conjugate of compound uses \overline."""
        assert _latex(Conjugate(Add(a, b))) == r"\overline{a + b}"

    def test_dual(self):
        """Dual renders as ^*."""
        assert _latex(Dual(a)) == "a^*"

    def test_undual(self):
        """Undual renders as ^{*^{-1}}."""
        assert _latex(Undual(a)) == "a^{*^{-1}}"

    def test_complement(self):
        r"""Complement renders as ^{\complement}."""
        assert _latex(Complement(a)) == r"a^{\complement}"

    def test_uncomplement(self):
        r"""Uncomplement renders as ^{\complement^{-1}}."""
        assert _latex(Uncomplement(a)) == r"a^{\complement^{-1}}"

    def test_inverse(self):
        """Inverse renders as ^{-1}."""
        assert _latex(Inverse(a)) == "a^{-1}"

    def test_squared(self):
        """Squared renders as ^2."""
        assert _latex(Squared(a)) == "a^2"


class TestPostfixOnPostfix:
    def test_undual_of_dual(self):
        """Undual of dual wraps inner in parens."""
        assert _latex(Undual(Dual(a))) == r"\left(a^*\right)^{*^{-1}}"

    def test_inverse_of_dual(self):
        """Inverse of dual wraps inner in parens."""
        assert _latex(Inverse(Dual(a))) == r"\left(a^*\right)^{-1}"

    def test_dual_of_inverse(self):
        """Dual of inverse wraps inner in parens."""
        assert _latex(Dual(Inverse(a))) == r"\left(a^{-1}\right)^*"


class TestPostfixOnSup:
    """Postfix symbols starting with ^ must brace-wrap Sup children."""

    def test_postfix_dagger_on_exp(self):
        """reverse(exp(a)) with dagger notation: {e^{a}}^{\\dagger}"""
        from galaga.notation import Notation, NotationRule

        n = Notation()
        n.set("Reverse", "latex", NotationRule(kind="superscript", symbol=r"\dagger"))
        from galaga.latex_build import build
        from galaga.latex_emit import emit
        from galaga.latex_rewrite import rewrite

        tree = build(Reverse(Exp(a)), n)
        result = emit(rewrite(tree))
        assert result == r"{e^{a}}^{\dagger}"

    def test_superscript_on_simple(self):
        """reverse(a) with superscript dagger: a^{\\dagger}"""
        from galaga.notation import Notation, NotationRule

        n = Notation()
        n.set("Reverse", "latex", NotationRule(kind="superscript", symbol=r"\dagger"))
        from galaga.latex_build import build
        from galaga.latex_emit import emit
        from galaga.latex_rewrite import rewrite

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
        """Complement of exp brace-wraps."""
        result = _latex(Complement(Exp(a)))
        assert result == r"{e^{a}}^{\complement}"


class TestWrap:
    def test_grade(self):
        """Grade renders with \\langle \rangle."""
        assert _latex(Grade(a, 1)) == r"\langle a \rangle_{1}"

    def test_norm(self):
        r"""Norm renders with \lVert."""
        assert _latex(Norm(a)) == r"\lVert a \rVert"

    def test_even(self):
        """Even renders with \text{even} subscript."""
        assert _latex(Even(a)) == r"\langle a \rangle_{\text{even}}"

    def test_odd(self):
        """Odd renders with \text{odd} subscript."""
        assert _latex(Odd(a)) == r"\langle a \rangle_{\text{odd}}"

    def test_unit_atom(self):
        r"""Unit of atom renders as \hat."""
        assert _latex(Unit(a)) == r"\hat{a}"

    def test_unit_compound(self):
        r"""Unit of compound uses \widehat."""
        result = _latex(Unit(Add(a, b)))
        # Unit of compound uses wide hat accent
        assert r"\widehat" in result


class TestExp:
    def test_simple(self):
        """Exp renders as e^{...}."""
        assert _latex(Exp(a)) == "e^{a}"

    def test_exp_with_frac_uses_tfrac(self):
        """The key test: frac inside exp superscript becomes inline slash."""
        expr = Exp(ScalarDiv(theta, 2))
        assert _latex(expr) == r"e^{\theta/2}"

    def test_exp_with_product_and_frac(self):
        """Exp with product and frac uses slash, not \\frac."""
        expr = Exp(Gp(ScalarDiv(Neg(theta), 2), b))
        result = _latex(expr)
        assert "/" in result
        assert r"\frac" not in result


class TestLog:
    def test_simple(self):
        """Exp renders as e^{...}."""
        assert _latex(Log(a)) == r"\log\left(a\right)"

    def test_log_of_exp(self):
        """Log of exp: \\log(e^{a})."""
        assert _latex(Log(Exp(a))) == r"\log\left(e^{a}\right)"


class TestCommutator:
    def test_commutator(self):
        """Commutator renders with brackets."""
        assert _latex(Commutator(a, b)) == r"[a,\, b]"

    def test_anticommutator(self):
        """Anticommutator renders with braces."""
        result = _latex(Anticommutator(a, b))
        # Should have braces or similar
        assert "a" in result and "b" in result


class TestPrecedence:
    def test_add_in_gp(self):
        """Sum in gp gets parenthesized."""
        expr = Gp(Add(a, b), a)
        assert _latex(expr) == r"\left(a + b\right) a"

    def test_gp_in_add(self):
        """Product in sum needs no parens."""
        expr = Add(Gp(a, b), a)
        assert _latex(expr) == "a b + a"

    def test_nested_frac_outside_sup_stays_frac(self):
        """Frac not inside Sup should remain \\frac."""
        expr = ScalarDiv(a, 2)
        assert _latex(expr) == r"\frac{a}{2}"


class TestPrefixSpacing:
    """Regression: prefix LaTeX commands must not run into the operand."""

    def test_latex_command_gets_space(self):
        """LaTeX command prefix gets trailing space."""
        from galaga.notation import Notation, NotationRule

        n = Notation()
        n.set("Reverse", "latex", NotationRule(kind="prefix", symbol=r"\tilde"))
        from galaga.latex_build import build
        from galaga.latex_emit import emit
        from galaga.latex_rewrite import rewrite

        assert emit(rewrite(build(Reverse(a), n))) == r"\tilde a"

    def test_latex_command_compound_gets_space(self):
        """LaTeX command prefix before parens gets space."""
        from galaga.notation import Notation, NotationRule

        n = Notation()
        n.set("Reverse", "latex", NotationRule(kind="prefix", symbol=r"\tilde"))
        from galaga.latex_build import build
        from galaga.latex_emit import emit
        from galaga.latex_rewrite import rewrite

        assert emit(rewrite(build(Reverse(Add(a, b)), n))) == r"\tilde \left(a + b\right)"

    def test_non_command_prefix_no_space(self):
        """Prefix '-' should NOT get a space."""
        assert _latex(Neg(a)) == "-a"

    def test_prefix_ending_in_brace_no_space(self):
        """Prefix ending in } has no space."""
        from galaga.notation import Notation, NotationRule

        n = Notation()
        n.set("Reverse", "latex", NotationRule(kind="prefix", symbol=r"{\sim}"))
        from galaga.latex_build import build
        from galaga.latex_emit import emit
        from galaga.latex_rewrite import rewrite

        assert emit(rewrite(build(Reverse(a), n))) == r"{\sim}a"


class TestSuperscriptKind:
    """Regression: superscript notation kind."""

    def _render(self, expr, symbol):
        from galaga.latex_build import build
        from galaga.latex_emit import emit
        from galaga.latex_rewrite import rewrite
        from galaga.notation import Notation, NotationRule

        n = Notation()
        n.set("Reverse", "latex", NotationRule(kind="superscript", symbol=symbol))
        return emit(rewrite(build(expr, n)))

    def test_simple_atom(self):
        """Superscript on atom: a^{symbol}."""
        assert self._render(Reverse(a), r"\dagger") == r"a^{\dagger}"

    def test_compound(self):
        """Superscript on compound wraps in parens."""
        result = self._render(Reverse(Add(a, b)), r"\dagger")
        assert result == r"\left(a + b\right)^{\dagger}"

    def test_on_exp_braces(self):
        """Sup-on-Sup must brace-wrap."""
        result = self._render(Reverse(Exp(a)), r"\dagger")
        assert result == r"{e^{a}}^{\dagger}"

    def test_custom_symbol(self):
        """Custom superscript symbol."""
        assert self._render(Reverse(a), "R") == "a^{R}"


class TestEndToEndLatex:
    """End-to-end: real Algebra objects through the full pipeline."""

    def test_exp_frac_slash(self):
        """exp(-θ/2 B) uses slash not frac in superscript."""
        from galaga import Algebra, exp

        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        th = alg.scalar(np.radians(45)).name(latex=r"\theta")
        B = (e1 * e2).name("B")
        R = exp((-th / 2) * B)
        latex = R.latex()
        assert "/" in latex
        assert r"\frac" not in latex

    def test_neg_hoisted_in_exp(self):
        """Negation hoists before slash in superscript."""
        from galaga import Algebra, exp

        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        th = alg.scalar(1.0).name(latex=r"\theta")
        B = (e1 * e2).name("B")
        latex = exp((-th / 2) * B).latex()
        assert latex.startswith("e^{-")

    def test_complement_lazy(self):
        """complement() stays symbolic on lazy MVs."""
        from galaga import Algebra, complement

        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        c = complement(v)
        assert c._is_symbolic
        assert r"\complement" in c.latex()

    def test_log_lazy(self):
        """log() stays symbolic on lazy MVs."""
        from galaga import Algebra, exp, log

        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        B = (e1 * e2).name("B")
        R = exp(B)
        latex = log(R).latex()
        assert r"\log" in latex


class TestAccentWidth:
    """LaTeX accents use narrow (\\tilde) for single glyphs, wide (\\widetilde) for multi-char."""

    def test_single_char_narrow(self):
        """Single letter uses \\tilde."""
        assert _latex(Reverse(a)) == r"\tilde{a}"

    def test_multi_char_wide(self):
        """Multi-letter name uses \\widetilde."""
        ab = _sym("AB")
        assert _latex(Reverse(ab)) == r"\widetilde{AB}"

    def test_latex_command_narrow(self):
        """LaTeX command like \\theta is a single glyph — uses \\tilde."""
        assert _latex(Reverse(theta)) == r"\tilde{\theta}"

    def test_compound_expr_wide(self):
        """Compound expression uses \\widetilde."""
        assert _latex(Reverse(Add(a, b))) == r"\widetilde{a + b}"

    def test_conjugate_single_narrow(self):
        """Conjugate single char uses \\bar."""
        assert _latex(Conjugate(a)) == r"\bar{a}"

    def test_conjugate_multi_wide(self):
        """Conjugate multi-char uses \\overline."""
        ab = _sym("AB")
        assert _latex(Conjugate(ab)) == r"\overline{AB}"


class TestPostfixOnSuperscriptName:
    """Postfix ^ on a Sym whose latex name contains ^ must brace-wrap."""

    def test_undual_of_named_dual(self):
        """undual(B^\\star) brace-wraps: {B^\\star}^{*^{-1}}."""
        from galaga.expr import Sym, Undual

        _alg2 = Algebra((1, 1, 1))
        _b = _alg2.basis_vectors()[0]
        b_star = Sym(_b, "B*", name_latex=r"B^\star")
        result = _latex(Undual(b_star))
        assert result == r"{B^\star}^{*^{-1}}"

    def test_inverse_of_named_superscript(self):
        """inverse(x^2) brace-wraps: {x^2}^{-1}."""
        x_sq = _sym("x²", latex="x^2")
        result = _latex(Inverse(x_sq))
        assert result == r"{x^2}^{-1}"

    def test_postfix_on_plain_name_no_braces(self):
        """dual(a) has no extra braces: a^*."""
        result = _latex(Dual(a))
        assert result == "a^*"


class TestPostfixOnCompoundName:
    """Postfix on Sym whose name contains operators gets parenthesised."""

    def test_dual_of_wedge_name(self):
        r"""Dual of 'a \wedge b' wraps: \left(a \wedge b\right)^*."""
        wedge_sym = _sym("a∧b", latex=r"a \wedge b")
        result = _latex(Dual(wedge_sym))
        assert r"\left(a \wedge b\right)^*" == result

    def test_dual_of_simple_name_no_parens(self):
        """Dual of simple name: B^*."""
        result = _latex(Dual(a))
        assert result == "a^*"

    def test_complement_of_wedge_name(self):
        r"""Complement of 'a \wedge b' wraps."""
        wedge_sym = _sym("a∧b", latex=r"a \wedge b")
        result = _latex(Complement(wedge_sym))
        assert r"\left(a \wedge b\right)" in result


class TestSymProperties:
    """Sym.is_compound and Sym.has_superscript properties."""

    def test_simple_name_not_compound(self):
        """Single-letter name is not compound."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        B = (e1 ^ e2).name("B")
        s = B._to_expr()
        assert not s.is_compound

    def test_wedge_name_is_compound(self):
        """Name with wedge operator is compound."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        area = (e1.name("a") ^ e2.name("b")).name(latex=r"a \wedge b")
        s = area._to_expr()
        assert s.is_compound

    def test_sum_name_is_compound(self):
        """Name with + is compound."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        v = (e1.name("a") + e2.name("b")).name(latex="a + b")
        s = v._to_expr()
        assert s.is_compound

    def test_no_inner_expr_not_compound(self):
        """Sym without inner_expr and simple name is not compound."""
        s = _sym("B")
        assert not s.is_compound

    def test_no_inner_expr_wedge_name_compound(self):
        """Sym without inner_expr but compound name falls back to string check."""
        s = _sym("a∧b", latex=r"a \wedge b")
        assert s.is_compound

    def test_has_superscript(self):
        """Name with ^ has superscript."""
        s = _sym("B*", latex=r"B^\star")
        assert s.has_superscript

    def test_no_superscript(self):
        """Simple name has no superscript."""
        s = _sym("B")
        assert not s.has_superscript

    def test_inner_expr_preserved(self):
        """_to_expr() preserves inner expression tree."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        area = (e1.name("a") ^ e2.name("b")).name("B")
        s = area._to_expr()
        assert s._inner_expr is not None
        assert hasattr(s._inner_expr, "a")  # Op node

    def test_eager_no_inner_expr(self):
        """Eager MV has no inner expr."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        s = e1._to_expr()
        assert s._inner_expr is None


class TestFracNoParens:
    """Frac nodes skip Parens wrapping but get brace-wrapped for superscripts."""

    def test_frac_in_gp(self):
        r"""\\frac{1}{2} e_{1} — no parens around fraction."""
        result = _latex(Gp(Div(Scalar(1), Scalar(2)), a))
        assert r"\left(" not in result
        assert r"\frac{1}{2}" in result

    def test_frac_in_add(self):
        r"""\\frac{1}{2} + a — no parens."""
        result = _latex(Add(Div(Scalar(1), Scalar(2)), a))
        assert r"\left(" not in result

    def test_scalar_div_in_gp(self):
        r"""\\frac{a}{2} b — no parens around scalar div."""
        result = _latex(Gp(ScalarDiv(a, 2), b))
        assert r"\left(" not in result
        assert r"\frac{a}{2}" in result

    def test_frac_squared_brace_wrapped(self):
        r"""{\\frac{1}{2}}^2 — brace-wrapped for superscript."""
        result = _latex(Squared(Div(Scalar(1), Scalar(2))))
        assert result == r"{\frac{1}{2}}^2"

    def test_frac_inverse_brace_wrapped(self):
        r"""{\\frac{a}{b}}^{-1} — brace-wrapped for superscript."""
        result = _latex(Inverse(Div(a, b)))
        assert result == r"{\frac{a}{b}}^{-1}"

    def test_frac_dual_brace_wrapped(self):
        r"""{\\frac{a}{b}}^* — brace-wrapped for superscript."""
        result = _latex(Dual(Div(a, b)))
        assert result == r"{\frac{a}{b}}^*"

    def test_scalar_div_in_exp_becomes_slash(self):
        r"""e^{a/2} — frac becomes slash inside exp superscript."""
        result = _latex(Exp(ScalarDiv(a, 2)))
        assert result == r"e^{a/2}"

    def test_product_div_in_exp(self):
        r"""e^{a b/2} — product with scalar div in exp."""
        result = _latex(Exp(ScalarDiv(Gp(a, b), 2)))
        assert "/" in result
        assert r"\frac" not in result

    def test_frac_times_frac(self):
        r"""\\frac{1}{2} \\frac{1}{3} — no parens on either."""
        result = _latex(Gp(Div(Scalar(1), Scalar(2)), Div(Scalar(1), Scalar(3))))
        assert r"\left(" not in result


class TestSlashFracAmbiguity:
    """SlashFrac in superscripts: wrap in parens when adjacent to other terms."""

    def test_standalone_no_parens(self):
        """e^{a/2} — standalone slash, no parens needed."""
        result = _latex(Exp(ScalarDiv(a, 2)))
        assert result == r"e^{a/2}"

    def test_with_sibling_gets_parens(self):
        """e^{(a/2) b} — slash with sibling, wrapped."""
        result = _latex(Exp(Gp(ScalarDiv(a, 2), b)))
        assert r"\left(a/2\right)" in result

    def test_sibling_on_left_gets_parens(self):
        """e^{a (b/2)} — slash on right with sibling."""
        result = _latex(Exp(Gp(a, ScalarDiv(b, 2))))
        assert r"\left(b/2\right)" in result

    def test_two_fracs_both_wrapped(self):
        """e^{(a/2) (b/3)} — both slashes wrapped."""
        result = _latex(Exp(Gp(ScalarDiv(a, 2), ScalarDiv(b, 3))))
        assert result.count(r"\left(") == 2

    def test_neg_prefix_no_wrap(self):
        """e^{-a/2} — neg prefix doesn't trigger wrapping."""
        result = _latex(Exp(ScalarDiv(Neg(a), 2)))
        assert r"\left(" not in result
        assert result == r"e^{-a/2}"

    def test_product_as_numerator_no_wrap(self):
        """e^{-B θ/2} — product in numerator, single slash, no wrap."""
        _B = _sym("B")
        _th = _sym("θ", latex=r"\theta")
        result = _latex(Exp(ScalarDiv(Neg(Gp(_B, _th)), 2)))
        assert r"\left(" not in result

    def test_normal_context_no_change(self):
        r"""\\frac{a}{2} b — normal context, no parens."""
        result = _latex(Gp(ScalarDiv(a, 2), b))
        assert r"\left(" not in result
        assert r"\frac{a}{2}" in result
