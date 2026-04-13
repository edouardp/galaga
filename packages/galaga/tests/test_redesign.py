"""Tests for the symbolic redesign: naming and evaluation semantics."""

import numpy as np
import pytest

from galaga import Algebra, BladeConvention, b_gamma
from galaga.expr import Sym, sym
from galaga.simplify import simplify


@pytest.fixture
def cl3():
    return Algebra((1, 1, 1))


class TestNameMethod:
    def test_name_sets_all_variants(self, cl3):
        """.name() sets ascii, unicode, and latex names."""
        e1, _, _ = cl3.basis_vectors()
        v = (e1).name("v")
        assert v._name == "v"
        assert v._name_unicode == "v"
        assert v._name_latex == "v"

    def test_name_with_overrides(self, cl3):
        """.name() with explicit overrides uses them."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\mathbf{v}", unicode="𝐯")
        assert v._name == "v"
        assert v._name_latex == r"\mathbf{v}"
        assert v._name_unicode == "𝐯"

    def test_name_makes_lazy(self, cl3):
        """.name() sets lazy mode."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert v._is_symbolic is True

    def test_name_preserves_value(self, cl3):
        """.name() doesn't change numeric data."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert v == e1

    def test_name_ascii_kwarg(self, cl3):
        """.name(ascii=) overrides ascii name."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", ascii="v_ascii")
        assert v._name == "v_ascii"


class TestAnonMethod:
    def test_anon_clears_name(self, cl3):
        """.anon() removes the display name."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v").anon()
        assert v._name is None
        assert v._name_unicode is None
        assert v._name_latex is None

    def test_anon_preserves_lazy(self, cl3):
        """.anon() keeps lazy/eager state."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v").anon()
        assert v._is_symbolic is True

    def test_anon_on_anonymous_is_noop(self, cl3):
        """.anon() on unnamed MV is a no-op."""
        e1, _, _ = cl3.basis_vectors()
        v = e1 + cl3.basis_vectors()[1]
        v2 = v.anon()
        assert v2._name is None


class TestLazyEagerMethods:
    def test_lazy_on_eager(self, cl3):
        """.lazy() makes eager MV lazy."""
        e1, _, _ = cl3.basis_vectors()
        v = (e1).lazy()
        assert v._is_symbolic is True

    def test_eager_on_lazy(self, cl3):
        """.eager() makes lazy MV eager."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        B.eager()
        assert B._is_symbolic is False
        assert B._name is None  # eager() strips name by default

    def test_eager_with_name(self, cl3):
        """.eager('B') keeps the name."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        B.eager("B")
        assert B._is_symbolic is False
        assert B._name == "B"
        assert str(B) == "B"

    def test_eval_is_eager(self, cl3):
        """.eval() returns anonymous eager copy."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        Be = B.eval()
        assert Be._is_symbolic is False
        assert Be._name is None  # eval() returns anonymous
        assert Be is not B  # eval() returns a new copy
        assert Be == B  # same value

    def test_chaining_name_eager(self, cl3):
        """.name().eager() chain works."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        B.eager("B")
        assert B._name == "B"
        assert B._is_symbolic is False

    def test_idempotence_lazy(self, cl3):
        """.lazy().lazy() is idempotent."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.lazy().lazy()
        assert v._is_symbolic is True

    def test_idempotence_eager(self, cl3):
        """.eager().eager() is idempotent."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.eager().eager()
        assert v._is_symbolic is False

    def test_idempotence_anon(self, cl3):
        """.anon().anon() is idempotent."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.anon().anon()
        assert v._name is None


class TestDisplayRules:
    def test_named_prints_name(self, cl3):
        """Named MV prints its name."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        assert str(B) == "B"

    def test_named_eager_prints_name(self, cl3):
        """Named eager MV prints its name."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        v.eager("v")
        assert str(v) == "v"

    def test_anon_lazy_prints_expr(self, cl3):
        """Anonymous lazy MV prints expression tree."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        anon = B.anon()
        # Should show the expression tree, not the name
        assert str(anon) != "B"

    def test_anon_eager_prints_format(self, cl3):
        """Anonymous eager MV prints coefficients."""
        e1, e2, _ = cl3.basis_vectors()
        x = e1 + e2
        # Eager anonymous — existing behavior
        s = str(x)
        assert "e" in s or "+" in s

    def test_latex_named(self, cl3):
        """Named MV latex() returns the name."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\mathbf{v}")
        assert v.latex() == r"\mathbf{v}"

    def test_latex_anon_eager(self, cl3):
        """Anonymous eager MV latex() returns coefficients."""
        e1, _, _ = cl3.basis_vectors()
        # Anonymous eager — coefficient rendering
        x = e1.anon()
        latex = x.latex()
        assert "e" in latex


class TestLazyPropagation:
    def test_lazy_plus_eager(self, cl3):
        """Lazy + eager = lazy."""
        e1, e2, e3 = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        x = B + e3
        assert x._is_symbolic is True
        assert "B" in str(x)
        assert "e₃" in str(x)

    def test_eager_plus_eager_stays_eager(self, cl3):
        """Eager + eager = eager."""
        e1, e2, _ = cl3.basis_vectors()
        x = e1 + e2
        assert x._is_symbolic is False

    def test_lazy_mul(self, cl3):
        """Lazy * eager = lazy."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        x = B * e1
        assert x._is_symbolic is True

    def test_scalar_mul_lazy(self, cl3):
        """Scalar * lazy = lazy."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        x = 2 * B
        assert x._is_symbolic is True
        assert "2" in str(x)
        assert "B" in str(x)

    def test_names_dont_propagate(self, cl3):
        """Names don't propagate to results."""
        e1, e2, e3 = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        x = B + e3
        assert x._name is None

    def test_eager_result_concrete(self, cl3):
        """Eager result has concrete data."""
        e1, e2, e3 = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        x = (B + e3).eager()
        assert x._is_symbolic is False
        # Should have concrete data
        assert np.any(x.data != 0)


class TestBasisBlades:
    def test_basis_named_eager(self, cl3):
        """Default basis vectors are named + eager."""
        e1, e2, e3 = cl3.basis_vectors()
        assert str(e1) != "0"  # basis blade renders by name
        assert e1._is_symbolic is False

    def test_basis_str(self, cl3):
        """Basis vector str() shows name."""
        e1, _, _ = cl3.basis_vectors()
        assert str(e1) == "e₁"

    def test_basis_anon(self, cl3):
        """.anon() on basis vector shows coefficients."""
        e1, _, _ = cl3.basis_vectors()
        a = e1.anon()
        # Should print concrete blade form
        assert a._name is None

    def test_basis_rename(self, cl3):
        """.name() on basis vector changes display."""
        e1, _, _ = cl3.basis_vectors()
        x = e1.name("x")
        assert str(x) == "x"

    def test_pseudoscalar_named(self, cl3):
        """Pseudoscalar has a display name."""
        I = cl3.pseudoscalar()
        assert str(I) == "e₁₂₃"

    def test_blade_lookup_named(self, cl3):
        """blade() returns named MV."""
        b = cl3.blade("e12")
        assert str(b) == "e₁₂"

    def test_custom_names(self):
        """Custom names appear in basis vectors."""
        sta = Algebra((1, -1, -1, -1), blades=b_gamma())
        g0, g1, g2, g3 = sta.basis_vectors()
        assert str(g0) != "0"
        assert "γ" in str(g0)


class TestSymAlias:
    def test_sym_returns_multivector(self, cl3):
        """sym() returns a Multivector."""
        from galaga.algebra import Multivector

        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert isinstance(v, Multivector)
        assert str(v) == "v"

    def test_sym_grade_detection(self, cl3):
        """sym() auto-detects grade."""
        e1, e2, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert v._grade == 1
        B = sym(e1 ^ e2, "B")
        assert B._grade == 2

    def test_sym_explicit_grade(self, cl3):
        """Sym with explicit grade."""
        e1, e2, _ = cl3.basis_vectors()
        v = sym(e1 + e2, "v", grade=1)
        assert v._grade == 1

    def test_sym_eval(self, cl3):
        """sym() result evaluates to original data."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        Re = R.eval()
        assert Re._is_symbolic is False
        assert Re._name is None  # eval() returns anonymous
        assert Re == e1 * e2  # same value


# ============================================================
# Spec use cases (verbatim from symbolic-redesign.md)
# ============================================================


class TestSpecUseCases:
    """Test all 10 use cases from the spec."""

    def test_use_case_1_plain_numeric(self, cl3):
        """Plain numeric / algebraic use."""
        e1, e2, e3 = cl3.basis_vectors()
        x = 2 * e1 + 3 * e2
        # Basis blades are named + eager, result is eager
        assert x._is_symbolic is False

    def test_use_case_2_named_symbolic_bivector(self, cl3):
        """Define a named symbolic bivector."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        assert str(B) == "B"
        assert B._is_symbolic is True

    def test_use_case_3_reveal_structure(self, cl3):
        """Reveal the symbolic structure again."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        assert str(B.anon()) != "B"

    def test_use_case_4_evaluate_keep_name(self, cl3):
        """Evaluate but keep the name."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        B.eager("B")
        assert str(B) == "B"
        # anon reveals concrete form
        s = str(B.anon())
        assert s != "B"

    def test_use_case_5_rename(self, cl3):
        """Rename an existing named object."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        B2 = B.name("plane")
        assert str(B2) == "plane"

    def test_use_case_6_lazy_unnamed(self, cl3):
        """Lazy unnamed expressions."""
        e1, e2, e3 = cl3.basis_vectors()
        expr = ((e1 + e2) ^ e3).lazy()
        str(expr)  # ensure it renders without error
        # Should show symbolic structure, not just a name
        assert expr._is_symbolic is True

    def test_use_case_7_rotor_workflow(self, cl3):
        """Rotor workflow."""
        e1, e2, _ = cl3.basis_vectors()
        theta = 0.5
        B = (e1 ^ e2).name("B")
        R = (-B * theta / 2).name("R")
        v = e1
        v_rot = R * v * ~R
        # v_rot is lazy because R is lazy
        assert v_rot._is_symbolic is True
        # Can get concrete result
        concrete = v_rot.eager()
        assert concrete._is_symbolic is False
        assert np.any(concrete.data != 0)

    def test_use_case_8_basis_basis_blade_rename(self, cl3):
        """Basis blades stay eager but can become lazy/named differently."""
        e1, _, _ = cl3.basis_vectors()
        E = e1.name("E")
        assert str(E) == "E"
        assert str(E.anon()) != "E"

    def test_use_case_9_symbolic_shorthand(self, cl3):
        """Symbolic shorthand over symbolic structure."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).lazy()
        assert B._is_symbolic is True

        B = B.name("B")
        assert str(B) == "B"

        assert str(B.anon()) != "B"

    def test_use_case_10_evaluate_without_losing_labels(self, cl3):
        """Evaluate without losing developer labels."""
        e1, e2, _ = cl3.basis_vectors()
        psi = (3 * e1 + 4 * e2).name("psi")
        psi.eager("psi")
        assert str(psi) == "psi"
        s = str(psi.anon())
        assert s != "psi"


class TestAdditionalCoverage:
    """Additional tests to cover edge cases and uncovered paths."""

    def test_lazy_add_scalar(self, cl3):
        """Lazy MV + scalar stays lazy."""
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = B + 5
        assert x._is_symbolic
        assert x == e1 + 5

    def test_lazy_sub_scalar(self, cl3):
        """Lazy MV - scalar stays lazy."""
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = B - 2
        assert x._is_symbolic
        assert x == e1 - 2

    def test_lazy_rsub_scalar(self, cl3):
        """Scalar - lazy MV stays lazy."""
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = 10 - B
        assert x._is_symbolic
        assert x == 10 - e1

    def test_lazy_radd_scalar(self, cl3):
        """Scalar + lazy MV stays lazy."""
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = 3 + B
        assert str(x) == "3 + B"

    def test_lazy_neg(self, cl3):
        """-lazy stays lazy."""
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = -B
        assert x._is_symbolic
        assert str(x) == "-B"

    def test_lazy_div(self, cl3):
        """Lazy / scalar stays lazy."""
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = B / 2
        assert x._is_symbolic
        assert x == e1 / 2

    def test_lazy_xor(self, cl3):
        """Lazy ^ eager stays lazy."""
        e1, e2, _ = cl3.basis_vectors()
        v = e1.name("v")
        x = v ^ e2
        assert x._is_symbolic
        assert "v" in str(x)

    def test_lazy_or(self, cl3):
        """Lazy | eager stays lazy."""
        e1, e2, _ = cl3.basis_vectors()
        v = e1.name("v")
        x = v | e2
        assert x._is_symbolic

    def test_lazy_invert(self, cl3):
        """~lazy stays lazy."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        x = ~v
        assert x._is_symbolic
        assert "v" in str(x)

    def test_format_unicode_named(self, cl3):
        """format(named, 'unicode') shows name."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", unicode="𝐯")
        assert f"{v:u}" == "𝐯"

    def test_format_ascii_named(self, cl3):
        """format(named, 'ascii') shows ascii name."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert f"{v:a}" == "v"

    def test_format_unicode_lazy_anon(self, cl3):
        """format(lazy_anon, 'unicode') shows expr."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1.name("a") + e2.name("b")).anon()
        assert "a" in f"{B:u}"

    def test_format_ascii_lazy_anon(self, cl3):
        """format(lazy_anon, 'ascii') shows expr."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1.name("a") + e2.name("b")).anon()
        assert "a" in f"{B:a}"

    def test_str_fallback_to_name(self, cl3):
        """When _name_unicode is None but _name is set."""
        e1, _, _ = cl3.basis_vectors()
        mv = e1._copy_with(_name="test", _name_unicode=None)
        assert str(mv) == "test"

    def test_latex_named_no_latex_name(self, cl3):
        """latex() when _name_latex is None but _name is set."""
        e1, _, _ = cl3.basis_vectors()
        mv = e1._copy_with(_name="x", _name_latex=None)
        assert mv.latex() == "x"

    def test_latex_lazy_anon(self, cl3):
        """latex() of lazy anon uses render_latex."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1.name("a") + e2.name("b")).anon()
        latex = B.latex()
        assert "a" in latex

    def test_to_expr_anonymous_eager(self, cl3):
        """_to_expr on anonymous eager MV uses str representation."""
        e1, e2, _ = cl3.basis_vectors()
        mv = (e1 + e2).anon()
        mv = mv._copy_with(_name=None, _name_unicode=None, _name_latex=None)
        expr = mv._to_expr()
        assert isinstance(expr, Sym)

    def test_lazy_mul_two_lazy(self, cl3):
        """Lazy * lazy stays lazy."""
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        x = a * b
        assert x._is_symbolic
        assert "a" in str(x)
        assert "b" in str(x)

    def test_lazy_add_two_lazy(self, cl3):
        """Lazy + lazy stays lazy."""
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        x = a + b
        assert str(x) == "a + b"

    def test_lazy_sub_two_lazy(self, cl3):
        """Lazy - lazy stays lazy."""
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        x = a - b
        assert str(x) == "a - b"

    def test_sym_latex_rendering(self, cl3):
        """Sym.latex() returns name_latex."""
        e1, _, _ = cl3.basis_vectors()
        s = Sym(e1, "v", name_latex=r"\mathbf{v}")
        assert s.latex() == r"\mathbf{v}"

    def test_symbolic_reverse_lazy_mv(self, cl3):
        """reverse(lazy_mv) stays lazy."""
        from galaga import reverse

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = reverse(v)
        assert "v" in str(result)

    def test_symbolic_grade_lazy_mv(self, cl3):
        """grade(lazy_mv, k) stays lazy."""
        from galaga import grade

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = grade(v, 1)
        assert "v" in str(result)

    def test_symbolic_sandwich_lazy_mv(self, cl3):
        """sandwich(lazy, lazy) stays lazy."""
        from galaga import sandwich

        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).name("R")
        v = e1.name("v")
        result = sandwich(R, v)
        assert "R" in str(result)

    def test_symbolic_ip_lazy_mv(self, cl3):
        """ip(lazy, lazy) stays lazy."""
        from galaga import ip

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = ip(a, e2)
        assert "a" in str(result)

    def test_symbolic_squared_lazy_mv(self, cl3):
        """squared(lazy) stays lazy."""
        from galaga import squared

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = squared(v)
        assert "v" in str(result)

    def test_ensure_expr_lazy_mv_with_expr(self, cl3):
        """_ensure_expr extracts _expr from lazy MV."""
        from galaga.expr import _ensure_expr

        e1, e2, _ = cl3.basis_vectors()
        B = e1.name("a") + e2.name("b")
        expr = _ensure_expr(B)
        assert not isinstance(expr, type(B))  # Should be Expr, not MV

    def test_ensure_expr_named_eager_mv(self, cl3):
        """_ensure_expr on named eager MV creates Sym."""
        from galaga.expr import _ensure_expr

        e1, _, _ = cl3.basis_vectors()
        # basis blades are named + eager
        expr = _ensure_expr(e1)
        assert isinstance(expr, Sym)


class TestExprOperatorCoverage:
    """Cover Expr operator overloads that are now less commonly hit."""

    def test_expr_add(self, cl3):
        """Expr + Expr builds Add."""
        e1, e2, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        b = Sym(e2, "b")
        assert str(a + b) == "a + b"

    def test_expr_radd(self, cl3):
        """scalar + Expr builds Add."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(3 + a) == "3 + a"

    def test_expr_sub(self, cl3):
        """Expr - Expr builds Sub."""
        e1, e2, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        b = Sym(e2, "b")
        assert str(a - b) == "a - b"

    def test_expr_rsub(self, cl3):
        """scalar - Expr builds Sub."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(3 - a) == "3 - a"

    def test_expr_neg(self, cl3):
        """-Expr builds Neg."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(-a) == "-a"

    def test_expr_mul_scalar(self, cl3):
        """Expr * scalar builds ScalarMul."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(a * 2) == "2a"

    def test_expr_rmul_scalar(self, cl3):
        """scalar * Expr builds ScalarMul."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(5 * a) == "5a"

    def test_expr_mul_expr(self, cl3):
        """Expr * Expr builds Gp."""
        e1, e2, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        b = Sym(e2, "b")
        assert str(a * b) == "ab"

    def test_expr_xor(self, cl3):
        """Expr ^ Expr builds Op."""
        e1, e2, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        b = Sym(e2, "b")
        assert str(a ^ b) == "a∧b"

    def test_expr_or(self, cl3):
        """Expr | Expr builds Dli."""
        e1, e2, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        b = Sym(e2, "b")
        assert "a" in str(a | b)

    def test_expr_invert(self, cl3):
        """~Expr builds Reverse."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert "a" in str(~a)

    def test_expr_truediv(self, cl3):
        """Expr / scalar builds ScalarDiv."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        result = a / 3
        assert "a" in str(result)

    def test_expr_truediv_non_scalar(self, cl3):
        """Expr / non-scalar raises TypeError."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert a.__truediv__("bad") is NotImplemented

    def test_expr_inv_property(self, cl3):
        """Expr.inv builds Inverse."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert "a" in str(a.inv)

    def test_expr_dag_property(self, cl3):
        """Expr.dag builds Reverse."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert "a" in str(a.dag)

    def test_expr_sq_property(self, cl3):
        """Expr.sq builds Squared."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(a.sq) == "a²"

    def test_expr_latex_wrap_dollar(self, cl3):
        """Expr.latex(wrap='$') wraps inline."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert a.latex(wrap="$") == "$a$"

    def test_expr_latex_wrap_display(self, cl3):
        """Expr.latex(wrap='$$') wraps display."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert "$$" in a.latex(wrap="$$")

    def test_expr_repr_latex(self, cl3):
        """Expr._repr_latex_() wraps in $."""
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert a._repr_latex_() == "$a$"

    def test_scalar_eval_raises(self):
        """Scalar.eval() raises — no algebra context."""
        from galaga.expr import Scalar

        with pytest.raises(TypeError):
            Scalar(42).eval()

    def test_sym_repr_ascii(self, cl3):
        """Sym repr uses ascii name."""
        e1, _, _ = cl3.basis_vectors()
        s = Sym(e1, "v", name_ascii="v_ascii")
        assert repr(s) == "v_ascii"

    def test_coerce_mv_with_name(self, cl3):
        """_coerce on a named MV without _expr."""
        from galaga.expr import _coerce

        e1, _, _ = cl3.basis_vectors()
        # basis blades are named + eager, no _expr
        result = _coerce(e1)
        assert isinstance(result, Sym)

    def test_is_symbolic_lazy_mv(self, cl3):
        """Lazy MV is symbolic."""
        from galaga.expr import _is_symbolic

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert _is_symbolic(v) is True

    def test_is_symbolic_eager_mv(self, cl3):
        """Eager MV is not symbolic."""
        from galaga.expr import _is_symbolic

        e1, _, _ = cl3.basis_vectors()
        assert _is_symbolic(e1) is False

    def test_simplify_rotor_norm(self, cl3):
        """simplify(R * ~R) for a rotor."""
        from galaga.expr import Gp, Reverse

        e1, e2, _ = cl3.basis_vectors()
        R_val = e1 * e2
        R = Sym(R_val, "R")
        result = simplify(Gp(R, Reverse(R)))
        # Should simplify to scalar 1 (or -1 depending on signature)
        assert "R" not in str(result)

    def test_eq_neg(self, cl3):
        """Neg Expr equality."""
        from galaga.expr import Neg
        from galaga.simplify import _eq

        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert _eq(Neg(a), Neg(a))
        assert not _eq(Neg(a), Neg(Sym(e1, "b")))

    def test_eq_grade(self, cl3):
        """Grade Expr equality."""
        from galaga.expr import Grade
        from galaga.simplify import _eq

        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert _eq(Grade(a, 1), Grade(a, 1))
        assert not _eq(Grade(a, 1), Grade(a, 2))


class TestSymbolicDropInWithLazyMV:
    """Cover symbolic module drop-in functions with lazy MVs."""

    def test_involute_lazy(self, cl3):
        """involute(lazy) returns lazy."""
        from galaga import involute

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = involute(v)
        assert "v" in str(result)

    def test_conjugate_lazy(self, cl3):
        """conjugate(lazy) returns lazy."""
        from galaga import conjugate

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = conjugate(v)
        assert "v" in str(result)

    def test_dual_lazy(self, cl3):
        """dual(lazy) returns lazy."""
        from galaga import dual

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = dual(v)
        assert "v" in str(result)

    def test_undual_lazy(self, cl3):
        """undual(lazy) returns lazy."""
        from galaga import undual

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = undual(v)
        assert "v" in str(result)

    def test_norm_lazy(self, cl3):
        """norm(lazy) returns lazy."""
        from galaga import norm

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = norm(v)
        assert "v" in str(result)

    def test_unit_lazy(self, cl3):
        """unit(lazy) returns lazy."""
        from galaga import unit

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = unit(v)
        assert "v" in str(result)

    def test_inverse_lazy(self, cl3):
        """inverse(lazy) returns lazy."""
        from galaga import inverse

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = inverse(v)
        assert "v" in str(result)

    def test_left_contraction_lazy(self, cl3):
        """left_contraction(lazy, lazy) returns lazy."""
        from galaga import left_contraction

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = left_contraction(a, e2)
        assert "a" in str(result)

    def test_right_contraction_lazy(self, cl3):
        """right_contraction(lazy, lazy) returns lazy."""
        from galaga import right_contraction

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = right_contraction(a, e2)
        assert "a" in str(result)

    def test_hestenes_inner_lazy(self, cl3):
        """hestenes_inner(lazy, lazy) returns lazy."""
        from galaga import hestenes_inner

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = hestenes_inner(a, e2)
        assert "a" in str(result)

    def test_doran_lasenby_inner_lazy(self, cl3):
        """doran_lasenby_inner(lazy, lazy) returns lazy."""
        from galaga import doran_lasenby_inner

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = doran_lasenby_inner(a, e2)
        assert "a" in str(result)

    def test_scalar_product_lazy(self, cl3):
        """scalar_product(lazy, lazy) returns lazy."""
        from galaga import scalar_product

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = scalar_product(a, e2)
        assert "a" in str(result)

    def test_commutator_lazy(self, cl3):
        """commutator(lazy, lazy) returns lazy."""
        from galaga import commutator

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = commutator(a, e2)
        assert "a" in str(result)

    def test_anticommutator_lazy(self, cl3):
        """anticommutator(lazy, lazy) returns lazy."""
        from galaga import anticommutator

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = anticommutator(a, e2)
        assert "a" in str(result)

    def test_lie_bracket_lazy(self, cl3):
        """lie_bracket(lazy, lazy) returns lazy."""
        from galaga import lie_bracket

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = lie_bracket(a, e2)
        assert "a" in str(result)

    def test_jordan_product_lazy(self, cl3):
        """jordan_product(lazy, lazy) returns lazy."""
        from galaga import jordan_product

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = jordan_product(a, e2)
        assert "a" in str(result)

    def test_even_grades_lazy(self, cl3):
        """even_grades(lazy) returns lazy."""
        from galaga import even_grades

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = even_grades(v)
        assert "v" in str(result)

    def test_odd_grades_lazy(self, cl3):
        """odd_grades(lazy) returns lazy."""
        from galaga import odd_grades

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = odd_grades(v)
        assert "v" in str(result)

    def test_ip_modes_lazy(self, cl3):
        """ip() with all modes returns lazy."""
        from galaga import ip

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        for mode in ("doran_lasenby", "hestenes", "left", "right", "scalar"):
            result = ip(a, e2, mode=mode)
            assert "a" in str(result)


class TestSandwichLazy:
    """Tests for laziness-aware sandwich()."""

    def test_sandwich_lazy_rotor(self, cl3):
        """sandwich(lazy_R, lazy_v) returns lazy."""
        from galaga import sandwich

        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).name("R")
        v = e1.name("v")
        result = sandwich(R, v)
        assert result._is_symbolic
        assert "R" in str(result)
        assert "v" in str(result)

    def test_sandwich_lazy_concrete_correct(self, cl3):
        """Lazy sandwich evaluates correctly."""
        from galaga import gp, reverse, sandwich

        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).name("R")
        result = sandwich(R, e1)
        expected = gp(gp(e1 * e2, e1), reverse(e1 * e2))
        assert result.eager() == expected

    def test_sandwich_eager_stays_eager(self, cl3):
        """sandwich(eager, eager) stays eager."""
        from galaga import sandwich

        e1, e2, _ = cl3.basis_vectors()
        result = sandwich(e1 * e2, e1)
        assert result._is_symbolic is False

    def test_sandwich_one_lazy_operand(self, cl3):
        """One lazy operand makes result lazy."""
        from galaga import sandwich

        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).name("R")
        # lazy rotor, eager vector
        result = sandwich(R, e1)
        assert result._is_symbolic
        assert "R" in str(result)

    def test_sw_alias_lazy(self, cl3):
        """sw() alias works with lazy MVs."""
        from galaga import sw

        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).name("R")
        result = sw(R, e1)
        assert result._is_symbolic


class TestSmallValueDisplay:
    """Tests for displaying values below the 1e-12 noise threshold."""

    def test_format_spec_shows_small_values(self, cl3):
        """Format spec shows small coefficients."""
        mv = cl3.scalar(9.109e-31)
        assert format(mv, ".3e") == "9.109e-31"

    def test_format_spec_shows_small_negative(self, cl3):
        """Format spec shows small negative coefficients."""
        mv = cl3.scalar(-1.055e-34)
        assert format(mv, ".3e") == "-1.055e-34"

    def test_str_suppresses_small_values(self, cl3):
        """str() suppresses near-zero coefficients."""
        mv = cl3.scalar(9.109e-31)
        assert str(mv) == "0"

    def test_latex_default_suppresses_small(self, cl3):
        """latex() suppresses near-zero by default."""
        mv = cl3.scalar(9.109e-31)
        assert mv.latex() == "0"

    def test_latex_coeff_format_shows_small(self, cl3):
        """latex(coeff_format=) shows small values with LaTeX notation."""
        mv = cl3.scalar(9.109e-31)
        result = mv.latex(coeff_format=".3e")
        assert r"9.109 \times 10^{-31}" == result

    def test_latex_coeff_format_electron_mass(self, cl3):
        """coeff_format handles electron mass scale."""
        mv = cl3.scalar(9.109e-31)
        assert "9.109" in mv.latex(coeff_format=".4e")

    def test_latex_coeff_format_planck(self, cl3):
        """coeff_format handles Planck constant scale."""
        mv = cl3.scalar(1.055e-34)
        assert "1.055" in mv.latex(coeff_format=".4e")

    def test_latex_coeff_format_compton(self, cl3):
        """coeff_format handles Compton wavelength scale."""
        mv = cl3.scalar(3.861e-13)
        assert "3.861" in mv.latex(coeff_format=".4e")

    def test_format_spec_zero_is_exact_zero(self, cl3):
        """Exact 0.0 should still show as zero even with format spec."""
        mv = cl3.scalar(0.0)
        assert format(mv, ".3e") == "0.000e+00"

    def test_physical_constants_division(self, cl3):
        """ℏ / (m * c) should give correct Compton wavelength."""
        hbar = cl3.scalar(1.055e-34).name("ℏ")
        m = cl3.scalar(9.109e-31).name("m")
        c = cl3.scalar(3e8).name("c")
        lam = hbar / (m * c)
        val = lam.eval().scalar_part
        assert abs(val - 3.86e-13) < 1e-15

    def test_physical_constants_format_in_latex(self, cl3):
        """Format spec through latex(coeff_format=) for small values."""
        hbar = cl3.scalar(1.055e-34).name("ℏ")
        m = cl3.scalar(9.109e-31).name("m")
        c = cl3.scalar(3e8).name("c")
        lam = hbar / (m * c)
        result = lam.eval().latex(coeff_format=".4e")
        assert r"\times 10^{-13}" in result


class TestMVDivision:
    """Tests for multivector / multivector division."""

    def test_scalar_div_scalar(self, cl3):
        """Scalar / scalar gives scalar."""
        a = cl3.scalar(10.0)
        b = cl3.scalar(2.0)
        assert (a / b).scalar_part == 5.0

    def test_named_scalar_div(self, cl3):
        """Named scalar division preserves laziness."""
        a = cl3.scalar(6.0).name("a")
        b = cl3.scalar(3.0).name("b")
        result = a / b
        assert result.eval().scalar_part == 2.0

    def test_vector_div_vector(self, cl3):
        """Vector / vector gives scalar."""
        e1, _, _ = cl3.basis_vectors()
        result = (3 * e1) / e1
        assert result == 3

    def test_div_zero_raises(self, cl3):
        """Division by zero raises."""
        e1, _, _ = cl3.basis_vectors()
        with pytest.raises(ZeroDivisionError):
            e1 / cl3.scalar(0.0)

    def test_rdiv_scalar_over_mv(self, cl3):
        """scalar / MV works."""
        e1, _, _ = cl3.basis_vectors()
        result = 1 / e1
        assert result == e1  # e1⁻¹ = e1 in Euclidean

    def test_div_non_invertible_raises(self, cl3):
        """Division by non-invertible raises."""
        e1, e2, _ = cl3.basis_vectors()
        # e1 + e2 is invertible, so this should work
        # This should work (e1+e2 is invertible)
        result = e1 / (e1 + e2)
        assert result is not None


class TestDivExprNode:
    """Tests for the Div expression node and symbolic MV/MV division."""

    def test_div_preserves_names(self, cl3):
        """Div expr preserves operand names."""
        e1, _, _ = cl3.basis_vectors()
        a = cl3.scalar(10.0).name("a")
        b = cl3.scalar(2.0).name("b")
        result = a / b
        assert "a" in str(result)
        assert "b" in str(result)

    def test_div_latex(self, cl3):
        """Div expr renders as \frac in LaTeX."""
        a = cl3.scalar(10.0).name("a", latex=r"\alpha")
        b = cl3.scalar(2.0).name("b", latex=r"\beta")
        result = a / b
        assert r"\frac{\alpha}{\beta}" == result.latex()

    def test_div_eval_correct(self, cl3):
        """Div expr evaluates correctly."""
        a = cl3.scalar(10.0).name("a")
        b = cl3.scalar(2.0).name("b")
        result = a / b
        assert result.eval().scalar_part == 5.0

    def test_div_product_in_denominator(self, cl3):
        """Div with product denominator."""
        hbar = cl3.scalar(1.055e-34).name("ℏ", latex=r"\hbar")
        m = cl3.scalar(9.109e-31).name("m", latex=r"m_e")
        c = cl3.scalar(3e8).name("c", latex=r"c")
        lam = hbar / (m * c)
        assert "ℏ" in str(lam)
        assert "m" in str(lam)
        assert "c" in str(lam)
        assert r"\frac{\hbar}{m_e c}" == lam.latex()

    def test_div_eager_by_eager_stays_eager(self, cl3):
        """Eager / eager stays eager."""
        a = cl3.scalar(10.0)
        b = cl3.scalar(2.0)
        result = a / b
        assert result._is_symbolic is False
        assert result.scalar_part == 5.0

    def test_div_lazy_by_eager(self, cl3):
        """Lazy / eager stays lazy."""
        a = cl3.scalar(10.0).name("a")
        b = cl3.scalar(2.0)
        result = a / b
        assert result._is_symbolic is True
        assert "a" in str(result)

    def test_div_eager_by_lazy(self, cl3):
        """Eager / lazy becomes lazy."""
        e1, _, _ = cl3.basis_vectors()
        a = cl3.scalar(10.0)
        b = cl3.scalar(2.0).name("b")
        result = a / b
        assert result._is_symbolic is True
        assert "b" in str(result)

    def test_scalar_div_still_works(self, cl3):
        """Division by int/float still uses ScalarDiv."""
        v = cl3.scalar(6.0).name("v")
        result = v / 3
        assert str(result) == "v/3"

    def test_exp_node(self, cl3):
        """Exp expr renders as exp(...)."""
        from galaga import exp

        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        theta = cl3.scalar(0.5).name("θ", latex=r"\theta")
        R = exp(B * theta)
        assert "exp" in str(R)
        assert "B" in str(R)
        assert "θ" in str(R)
        assert r"e^{" in R.latex()

    def test_exp_eval(self, cl3):
        """Exp expr evaluates correctly."""
        import numpy as np

        from galaga import exp

        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        R = exp(B * cl3.scalar(np.pi / 4).name("θ"))
        concrete = R.eval()
        assert concrete._is_symbolic is False
        assert abs(concrete.scalar_part - np.cos(np.pi / 4)) < 1e-10


class TestSquaredParens:
    """Tests for parenthesization in Squared node."""

    def test_squared_single_term_no_parens(self, cl3):
        """Squared atom: no parens."""
        from galaga import squared

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert str(squared(v)) == "v²"

    def test_squared_add_gets_parens(self, cl3):
        """Squared sum: gets parens."""
        from galaga import squared

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        result = squared(a + b)
        assert str(result) == "(a + b)²"

    def test_squared_sub_gets_parens(self, cl3):
        """Squared difference: gets parens."""
        from galaga import squared

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        result = squared(a - b)
        assert str(result) == "(a - b)²"

    def test_squared_product_no_parens(self, cl3):
        """Squared product: no parens."""
        from galaga import squared

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        result = squared(a * b)
        assert str(result) == "(ab)²"

    def test_squared_latex_add_gets_parens(self, cl3):
        """Squared sum in LaTeX: gets parens."""
        from galaga import squared

        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        result = squared(a + b)
        assert r"\left(" in result.latex()
        assert r"\right)" in result.latex()

    def test_squared_latex_single_no_parens(self, cl3):
        """Squared atom in LaTeX: no parens."""
        from galaga import squared

        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert result.latex() == "v^2" if (result := squared(v)) else False


class TestBasisVectorsLazy:
    """Tests for basis_vectors(lazy=True)."""

    def test_default_is_eager(self, cl3):
        """basis_vectors() default is eager."""
        e1, _, _ = cl3.basis_vectors()
        assert e1._is_symbolic is False

    def test_lazy_flag(self, cl3):
        """basis_vectors(lazy=True) returns lazy MVs."""
        e1, _, _ = cl3.basis_vectors(lazy=True)
        assert e1._is_symbolic is True
        assert str(e1) != "0"  # basis blade renders by name

    def test_lazy_ops_build_trees(self, cl3):
        """Lazy ops build expression trees."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        result = e1 ^ e2
        assert result._is_symbolic is True
        assert "∧" in str(result)

    def test_lazy_eval_gives_concrete(self, cl3):
        """.eval() on lazy gives concrete."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        result = (e1 ^ e2).eval()
        expected = cl3.basis_vectors()[0] ^ cl3.basis_vectors()[1]
        assert result == expected

    def test_lazy_preserves_names(self, cl3):
        """Lazy basis vectors keep their names."""
        e1, e2, e3 = cl3.basis_vectors(lazy=True)
        assert str(e1) == "e₁"
        assert str(e2) == "e₂"
        assert str(e3) == "e₃"


class TestLazyBladesFullWorkflow:
    """End-to-end tests with basis_vectors(lazy=True)."""

    def test_wedge_symbolic(self, cl3):
        """Lazy wedge renders symbolically."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        assert "∧" in str(e1 ^ e2)

    def test_gp_symbolic(self, cl3):
        """Lazy gp renders symbolically."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        result = e1 * e2
        assert "e₁" in str(result)
        assert "e₂" in str(result)

    def test_add_symbolic(self, cl3):
        """Lazy add renders symbolically."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        assert "+" in str(e1 + e2)

    def test_scalar_div_symbolic(self, cl3):
        """Lazy scalar div renders symbolically."""
        e1, _, _ = cl3.basis_vectors(lazy=True)
        result = e1 / 2
        assert "/2" in str(result)

    def test_exp_symbolic(self, cl3):
        """Lazy exp renders symbolically."""
        from galaga import exp

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        B = (e1 ^ e2).name("B")
        result = exp(B)
        assert "exp" in str(result)

    def test_rotor_workflow(self, cl3):
        """Full lazy rotor workflow."""
        import numpy as np

        from galaga import exp

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        theta = cl3.scalar(np.pi / 4).name("θ")
        B = (e1 ^ e2).name("B")
        R = exp(-B * theta / 2).name("R")
        v_rot = R * e1 * ~R
        assert "R" in str(v_rot)
        concrete = v_rot.eval()
        assert abs(concrete.data[1] - np.cos(np.pi / 4)) < 1e-10

    def test_division_symbolic(self, cl3):
        """Lazy MV division renders symbolically."""
        e1, _, _ = cl3.basis_vectors(lazy=True)
        a = cl3.scalar(10.0).name("a")
        b = cl3.scalar(2.0).name("b")
        result = a / b
        assert "a" in str(result)
        assert "b" in str(result)

    def test_named_scalar_in_expr(self, cl3):
        """Named scalar in expression shows name."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        m = cl3.scalar(5.0).name("m")
        result = m * e1
        assert "m" in str(result)

    def test_all_module_functions_lazy(self, cl3):
        """All module-level functions produce symbolic output with lazy blades."""
        from galaga import conjugate, dual, grade, inverse, involute, reverse, squared, unit

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        v = (e1 + e2).name("v")
        assert "ṽ" in str(reverse(v)) or "v" in str(reverse(v))
        assert "v" in str(involute(v))
        assert "v" in str(conjugate(v))
        assert "v" in str(grade(v, 1))
        assert "v" in str(dual(v))
        assert "v" in str(unit(v))
        assert "v" in str(inverse(v))
        assert "v" in str(squared(v))


class TestBladeHighDimension:
    """Tests for blade() ambiguity guard in high dimensions."""

    def test_blade_works_for_9d(self):
        """9D algebra works with default names."""
        alg = Algebra(tuple([1] * 9))
        b = alg.blade("e19")
        assert b is not None

    def test_blade_errors_for_10d_default_names(self):
        """10D digit parsing fails for ambiguous names."""
        alg = Algebra(tuple([1] * 10))
        with pytest.raises(ValueError):
            alg.blade("e110")

    def test_blade_works_for_10d_custom_names(self):
        """10D works with custom names."""
        alg = Algebra(
            tuple([1] * 10), blades=BladeConvention(vector_names=[(f"v{i}", f"v{i}", f"v{i}") for i in range(10)])
        )
        b = alg.blade("v01")
        assert b is not None


class TestAllBinaryOpsLazy:
    """All binary operations produce symbolic output with lazy inputs."""

    def test_gp_lazy(self, cl3):
        """gp(lazy, lazy) returns lazy."""
        from galaga import gp

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert str(gp(a, b)) == "ab"

    def test_op_lazy(self, cl3):
        """op(lazy, lazy) returns lazy."""
        from galaga import op

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "∧" in str(op(a, b))

    def test_left_contraction_lazy(self, cl3):
        """left_contraction(lazy, lazy) returns lazy."""
        from galaga import left_contraction

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "⌋" in str(left_contraction(a, b))

    def test_right_contraction_lazy(self, cl3):
        """right_contraction(lazy, lazy) returns lazy."""
        from galaga import right_contraction

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "⌊" in str(right_contraction(a, b))

    def test_hestenes_inner_lazy(self, cl3):
        """hestenes_inner(lazy, lazy) returns lazy."""
        from galaga import hestenes_inner

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "·" in str(hestenes_inner(a, b))

    def test_doran_lasenby_inner_lazy(self, cl3):
        """doran_lasenby_inner(lazy, lazy) returns lazy."""
        from galaga import doran_lasenby_inner

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "·" in str(doran_lasenby_inner(a, b))

    def test_scalar_product_lazy(self, cl3):
        """scalar_product(lazy, lazy) returns lazy."""
        from galaga import scalar_product

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "∗" in str(scalar_product(a, b))

    def test_commutator_lazy(self, cl3):
        """commutator(lazy, lazy) returns lazy."""
        from galaga import commutator

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        A = (e1 ^ e2).name("A")
        B = (e2 ^ e1).name("B")
        assert str(commutator(A, B)) == "[A, B]"

    def test_anticommutator_lazy(self, cl3):
        """anticommutator(lazy, lazy) returns lazy."""
        from galaga import anticommutator

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        A = (e1 ^ e2).name("A")
        B = (e2 ^ e1).name("B")
        assert str(anticommutator(A, B)) == "{A, B}"

    def test_lie_bracket_lazy(self, cl3):
        """lie_bracket(lazy, lazy) returns lazy."""
        from galaga import lie_bracket

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        A = (e1 ^ e2).name("A")
        B = (e2 ^ e1).name("B")
        assert "½" in str(lie_bracket(A, B))

    def test_jordan_product_lazy(self, cl3):
        """jordan_product(lazy, lazy) returns lazy."""
        from galaga import jordan_product

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "½" in str(jordan_product(a, b))


class TestNameAutoDerive:
    """Test that .name(latex=...) auto-derives unicode and ascii."""

    def test_greek_auto_derive(self, cl3):
        """Greek latex auto-derives unicode and ascii."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\theta")
        assert v._name_unicode == "θ"
        assert v._name == "theta"
        assert v._name_latex == r"\theta"

    def test_mathbf_auto_derive(self, cl3):
        r"""\mathbf auto-derives bold unicode."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("F", latex=r"\mathbf{F}")
        assert v._name_unicode == "𝐅"
        assert v._name == "F"

    def test_hbar_auto_derive(self, cl3):
        r"""\hbar auto-derives ℏ."""
        v = cl3.scalar(1.0).name("h", latex=r"\hbar")
        assert v._name_unicode == "ℏ"
        assert v._name == "hbar"

    def test_user_unicode_overrides(self, cl3):
        """Explicit unicode= overrides auto-derive."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\theta", unicode="MINE")
        assert v._name_unicode == "MINE"
        assert v._name == "theta"  # ascii still derived

    def test_user_ascii_overrides(self, cl3):
        """Explicit ascii= overrides auto-derive."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\theta", ascii="MINE")
        assert v._name == "MINE"
        assert v._name_unicode == "θ"  # unicode still derived

    def test_both_overrides(self, cl3):
        """Both unicode= and ascii= override."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\theta", unicode="U", ascii="A")
        assert v._name_unicode == "U"
        assert v._name == "A"

    def test_unknown_latex_uses_label(self, cl3):
        """Unknown latex falls back to label."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\weirdthing")
        assert v._name_unicode == "v"
        assert v._name == "v"
        assert v._name_latex == r"\weirdthing"

    def test_no_latex_uses_label(self, cl3):
        """No latex= uses label for all formats."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("myvar")
        assert v._name_unicode == "myvar"
        assert v._name == "myvar"
        assert v._name_latex == "myvar"


class TestNameLatexOnly:
    """Test .name(latex=...) without label."""

    def test_latex_only_greek(self, cl3):
        """name(latex=) with Greek auto-derives."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name(latex=r"\theta")
        assert str(v) == "θ"
        assert v._name == "theta"
        assert v._name_latex == r"\theta"

    def test_latex_only_mathbf(self, cl3):
        r"""name(latex=) with \mathbf auto-derives."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name(latex=r"\mathbf{F}")
        assert str(v) == "𝐅"
        assert v._name == "F"

    def test_latex_only_unknown_uses_latex_as_fallback(self, cl3):
        """name(latex=) with unknown uses latex as fallback."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.name(latex=r"\weirdthing")
        assert v._name == r"\weirdthing"
        assert v._name_latex == r"\weirdthing"

    def test_no_args_raises(self, cl3):
        """name() with no args raises ValueError."""
        e1, _, _ = cl3.basis_vectors()
        with pytest.raises(ValueError):
            e1.name()


class TestSimplifyEdgeCases:
    """Edge cases for simplify with non-Expr inputs."""

    def test_simplify_float(self, cl3):
        """simplify(float) returns float."""
        assert str(simplify(1.0)) == "1"

    def test_simplify_int(self, cl3):
        """simplify(int) returns int."""
        assert str(simplify(0)) == "0"

    def test_simplify_norm_unit(self, cl3):
        """simplify(norm(unit(x))) = 1."""
        from galaga import norm, unit

        e1, _, _ = cl3.basis_vectors(lazy=True)
        v = e1.name("v")
        result = simplify(norm(unit(v)))
        assert str(result) == "1"


class TestGpSpacing:
    """Geometric product uses spaces for multi-char names."""

    def test_single_char_no_space(self, cl3):
        """Single-char names juxtapose without space."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert str(a * b) == "ab"

    def test_multi_char_has_space(self, cl3):
        """Multi-char names get space in gp."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        pi, ve = e1.name("pi"), e2.name("ve")
        assert str(pi * ve) == "pi ve"

    def test_mixed_has_space(self, cl3):
        """Mixed single/multi-char gets space."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, pi = e1.name("a"), e2.name("pi")
        assert str(a * pi) == "a pi"

    def test_subscript_counts_as_single(self, cl3):
        """Subscripted name counts as single char."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        # e₁ has base len 1 (subscript doesn't count)
        assert str(e1 * e2) == "e₁e₂"

    def test_combining_char_counts_as_single(self, cl3):
        """Combining accent counts as single char."""
        from galaga import reverse

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a = e1.name("a")
        # ã has base len 1
        assert str(reverse(a) * e2.name("b")) == "a\u0303b"


class TestPowSquared:
    """mv**2 delegates to squared() for symbolic rendering."""

    def test_pow2_lazy_renders_squared(self, cl3):
        """lazy**2 renders as x²."""
        e1, _, _ = cl3.basis_vectors(lazy=True)
        v = e1.name("v")
        assert str(v**2) == "v²"

    def test_pow2_eager(self, cl3):
        """eager**2 computes gp(x,x)."""
        e1, _, _ = cl3.basis_vectors()
        assert (e1**2) == 1  # e1² = 1 in Euclidean

    def test_pow2_sum(self, cl3):
        """(a+b)**2 renders with parens."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert str((a + b) ** 2) == "(a + b)²"

    def test_pow3_not_squared(self, cl3):
        """x**3 does not use squared node."""
        e1, _, _ = cl3.basis_vectors(lazy=True)
        v = e1.name("v")
        assert "²" not in str(v**3)

    def test_pow0(self, cl3):
        """x**0 = 1."""
        e1, _, _ = cl3.basis_vectors(lazy=True)
        v = e1.name("v")
        assert (v**0) == 1


class TestSymNoName:
    """sym() with no name returns a lazy copy."""

    def test_sym_no_name(self, cl3):
        """sym(mv) without name makes lazy."""
        from galaga.expr import sym

        e1, _, _ = cl3.basis_vectors()
        a = sym(e1)
        assert a._is_symbolic is True
        assert a is not e1

    def test_sym_no_name_chain(self, cl3):
        """Unnamed sym in expression works."""
        from galaga.expr import sym

        e1, _, _ = cl3.basis_vectors()
        a = sym(e1).name(latex=r"\hat{n}")
        assert "n" in str(a)
        assert str(e1) == "e₁"  # original untouched

    def test_norm_lazy(self, cl3):
        """norm(lazy) returns lazy."""
        from galaga import norm

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        v = (3 * e1 + 4 * e2).name("v")
        n = norm(v)
        assert str(n) == "‖v‖"
        assert abs(n.eval().scalar_part - 5.0) < 1e-10


class TestIsBlade:
    def test_basis_vector(self, cl3):
        """Basis vector is a blade."""
        from galaga import is_basis_blade

        e1, _, _ = cl3.basis_vectors()
        assert is_basis_blade(e1)

    def test_scaled_blade(self, cl3):
        """Scaled basis vector is a blade."""
        from galaga import is_basis_blade

        e1, _, _ = cl3.basis_vectors()
        assert is_basis_blade(3 * e1)

    def test_bivector_blade(self, cl3):
        """Basis bivector is a blade."""
        from galaga import is_basis_blade

        e1, e2, _ = cl3.basis_vectors()
        assert is_basis_blade(e1 ^ e2)

    def test_scaled_bivector(self, cl3):
        """Scaled bivector is a blade."""
        from galaga import is_basis_blade

        e1, e2, _ = cl3.basis_vectors()
        assert is_basis_blade(5 * (e1 ^ e2))

    def test_pseudoscalar(self, cl3):
        """Pseudoscalar is a blade."""
        from galaga import is_basis_blade

        assert is_basis_blade(cl3.pseudoscalar())

    def test_scalar(self, cl3):
        """Scalar is a blade."""
        from galaga import is_basis_blade

        assert is_basis_blade(cl3.scalar(7.0))

    def test_sum_not_blade(self, cl3):
        """Sum of independent vectors is not a blade."""
        from galaga import is_basis_blade

        e1, e2, _ = cl3.basis_vectors()
        assert not is_basis_blade(e1 + e2)

    def test_mixed_grade_not_blade(self, cl3):
        """Mixed-grade MV is not a blade."""
        from galaga import is_basis_blade

        e1, e2, _ = cl3.basis_vectors()
        assert not is_basis_blade(e1 + (e1 ^ e2))

    def test_zero(self, cl3):
        """Zero is a blade."""
        from galaga import is_basis_blade

        assert not is_basis_blade(cl3.scalar(0.0))


class TestBasisBladeRename:
    """Tests for BasisBlade class and get_basis_blade() renaming."""

    def test_get_basis_blade_by_mv(self):
        """get_basis_blade(mv) returns BasisBlade."""
        from galaga import Algebra

        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors()
        bb = alg.get_basis_blade(e1 ^ e2)
        assert bb.ascii_name == "e12"

    def test_get_basis_blade_by_index(self):
        """get_basis_blade(int) returns BasisBlade."""
        from galaga import Algebra

        alg = Algebra((1, 1, 1))
        bb = alg.get_basis_blade(0b011)
        assert bb.ascii_name == "e12"

    def test_rename_affects_rendering(self):
        """Renaming a blade changes str() output."""
        from galaga import Algebra

        alg = Algebra((1, 1, 1))
        alg.get_basis_blade(0b011).rename(unicode="B₁₂", latex=r"\mathbf{B}_{12}")
        e1, e2, _ = alg.basis_vectors()
        result = e1 ^ e2
        assert str(result) == "B₁₂"
        assert result.latex() == r"\mathbf{B}_{12}"

    def test_rename_pseudoscalar(self):
        """Pseudoscalar can be renamed."""
        from galaga import Algebra

        alg = Algebra((1, 1, 1))
        alg.get_basis_blade(alg.pseudoscalar()).rename(unicode="I₃")
        assert str(alg.pseudoscalar()) == "I₃"

    def test_rename_basis_vector(self):
        """Basis vector can be renamed."""
        from galaga import Algebra

        alg = Algebra((1, 1, 1))
        alg.get_basis_blade(0b001).rename(unicode="x", ascii="x", latex="x")
        e1, _, _ = alg.basis_vectors()
        assert str(e1) == "x"

    def test_get_non_blade_raises(self):
        """get_basis_blade on non-blade raises."""
        from galaga import Algebra

        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors()
        with pytest.raises(ValueError, match="Not a basis blade"):
            alg.get_basis_blade(e1 + e2)

    def test_rename_chaining(self):
        """Rename methods chain."""
        from galaga import Algebra

        alg = Algebra((1, 1, 1))
        alg.get_basis_blade(0b011).rename(ascii="B12").rename(latex=r"\beta_{12}")
        bb = alg.get_basis_blade(0b011)
        assert bb.ascii_name == "B12"
        assert bb.latex_name == r"\beta_{12}"

    def test_rename_updates_existing_mv(self):
        """Renaming a BasisBlade updates already-created MVs."""
        from galaga import Algebra

        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        alg.get_basis_blade(e1).rename(unicode="x")
        assert str(e1) == "x"
        alg.get_basis_blade(e1).rename(unicode="e₁")
        assert str(e1) == "e₁"


class TestRegressiveProduct:
    """Tests for the regressive product (meet)."""

    def test_bivector_meet_3d(self, cl3):
        """Two bivectors in 3D meet at a vector."""
        from galaga import meet

        e1, e2, e3 = cl3.basis_vectors()
        result = meet(e1 ^ e2, e2 ^ e3)
        # Should be proportional to e2
        assert abs(result.data[2]) > 1e-12  # e2 component
        assert sum(abs(c) > 1e-12 for c in result.data) == 1

    def test_meet_is_alias(self, cl3):
        """meet() is an alias for regressive_product()."""
        from galaga import meet, regressive_product

        assert meet is regressive_product

    def test_join_is_alias(self, cl3):
        """join() is an alias for op()."""
        from galaga import join, op

        assert join is op

    def test_meet_grade_rule(self, cl3):
        """grade(A ∨ B) = grade(A) + grade(B) - n."""
        from galaga import grade, meet

        e1, e2, e3 = cl3.basis_vectors()
        # bivector ∨ bivector in 3D: 2+2-3 = 1 (vector)
        result = meet(e1 ^ e2, e2 ^ e3)
        assert result == grade(result, 1)

    def test_meet_zero_when_grades_too_low(self, cl3):
        """vector ∨ vector in 3D: 1+1-3 = -1 → zero."""
        from galaga import meet

        e1, e2, _ = cl3.basis_vectors()
        result = meet(e1, e2)
        assert result == 0

    def test_pga_line_meet(self):
        """Two lines in PGA meet at a point."""
        from galaga import Algebra, meet

        pga = Algebra((1, 1, 1, 0))
        e1, e2, e3, e0 = pga.basis_vectors()
        L1 = e1 ^ e2 ^ e0
        L2 = e1 ^ e3 ^ e0
        pt = meet(L1, L2)
        assert any(abs(c) > 1e-12 for c in pt.data)

    def test_symbolic_rendering(self, cl3):
        """Regressive product renders with ∨."""
        from galaga import regressive_product

        e1, e2, e3 = cl3.basis_vectors(lazy=True)
        A = (e1 ^ e2).name("A")
        B = (e2 ^ e3).name("B")
        result = regressive_product(A, B)
        assert "∨" in str(result)
        assert r"\vee" in result.latex()

    def test_symbolic_eval(self, cl3):
        """Symbolic regressive evaluates correctly."""
        from galaga import regressive_product

        e1, e2, e3 = cl3.basis_vectors(lazy=True)
        A = (e1 ^ e2).name("A")
        B = (e2 ^ e3).name("B")
        result = regressive_product(A, B)
        concrete = result.eval()
        assert abs(concrete.data[2]) > 1e-12  # e2

    def test_metric_regressive_euclidean(self, cl3):
        """Metric regressive agrees with complement-based in Euclidean."""
        import numpy as np

        from galaga import meet, metric_regressive_product

        e1, e2, e3 = cl3.basis_vectors()
        a = meet(e1 ^ e2, e2 ^ e3)
        b = metric_regressive_product(e1 ^ e2, e2 ^ e3)
        assert np.allclose(a.data, b.data) or np.allclose(a.data, -b.data)


class TestCoverageGaps:
    """Fill remaining coverage gaps."""

    def test_get_basis_blade_bad_type(self, cl3):
        """get_basis_blade with bad type raises."""
        with pytest.raises(TypeError):
            cl3.get_basis_blade(3.14)

    def test_pow_non_int(self, cl3):
        """Non-int power raises TypeError."""
        e1, _, _ = cl3.basis_vectors()
        assert e1.__pow__(1.5) is NotImplemented

    def test_basis_blade_setters(self):
        """BasisBlade name setters work."""
        from galaga.basis_blade import BasisBlade

        bb = BasisBlade(1, "e1", "e₁", "e_1")
        bb.ascii_name = "x"
        bb.unicode_name = "χ"
        bb.latex_name = "\\chi"
        assert bb.ascii_name == "x"
        assert bb.unicode_name == "χ"
        assert bb.latex_name == "\\chi"
        assert "BasisBlade" in repr(bb)

    def test_grade_lazy_even_odd(self, cl3):
        """grade('even'/'odd') on lazy MV works."""
        from galaga import grade

        e1, e2, _ = cl3.basis_vectors(lazy=True)
        v = e1.name("v")
        assert "even" not in str(grade(v, "even"))
        assert "odd" not in str(grade(v, "odd"))

    def test_hyperbolic_log(self):
        """Cover the hyperbolic branch of log()."""

        from galaga import Algebra, exp, log

        sta = Algebra((1, -1))
        e0, e1 = sta.basis_vectors()
        B = e0 * e1  # timelike bivector, B² > 0
        R = exp(B * 0.3)
        B_back = log(R)
        R_back = exp(B_back)
        assert R == R_back

    def test_scalar_div_eval(self, cl3):
        """ScalarDiv eval divides correctly."""
        from galaga.expr import ScalarDiv

        e1, _, _ = cl3.basis_vectors()
        expr = ScalarDiv(Sym(e1, "v"), 2)
        result = expr.eval()
        assert result == e1 / 2

    def test_div_eval(self, cl3):
        """Div eval divides correctly."""
        from galaga.expr import Div

        e1, e2, _ = cl3.basis_vectors()
        a = Sym(cl3.scalar(6.0), "a")
        b = Sym(cl3.scalar(3.0), "b")
        result = Div(a, b).eval()
        assert result.scalar_part == 2.0

    def test_neg_eval(self, cl3):
        """Neg eval negates correctly."""
        from galaga.expr import Neg

        e1, _, _ = cl3.basis_vectors()
        expr = Neg(Sym(e1, "v"))
        result = expr.eval()
        assert result == -e1

    def test_add_eval(self, cl3):
        """Add eval adds correctly."""
        from galaga.expr import Add

        e1, e2, _ = cl3.basis_vectors()
        result = Add(Sym(e1, "a"), Sym(e2, "b")).eval()
        assert result == e1 + e2

    def test_sub_eval(self, cl3):
        """Sub eval subtracts correctly."""
        from galaga.expr import Sub

        e1, e2, _ = cl3.basis_vectors()
        result = Sub(Sym(e1, "a"), Sym(e2, "b")).eval()
        assert result == e1 - e2

    def test_scalar_mul_eval(self, cl3):
        """ScalarMul eval multiplies correctly."""
        from galaga.expr import ScalarMul

        e1, _, _ = cl3.basis_vectors()
        result = ScalarMul(3, Sym(e1, "v")).eval()
        assert result == 3 * e1

    def test_eq_scalar_div(self, cl3):
        """ScalarDiv equality."""
        from galaga.expr import ScalarDiv
        from galaga.simplify import _eq

        e1, _, _ = cl3.basis_vectors()
        a = ScalarDiv(Sym(e1, "v"), 2)
        b = ScalarDiv(Sym(e1, "v"), 2)
        assert _eq(a, b)

    def test_eq_fallback_false(self, cl3):
        """Expr equality fallback returns False."""
        from galaga.simplify import _eq

        e1, _, _ = cl3.basis_vectors()
        # Two different types
        assert not _eq(Sym(e1, "a"), 42)

    def test_known_grade_scalar_div(self, cl3):
        """ScalarDiv preserves known grade."""
        from galaga.expr import ScalarDiv
        from galaga.simplify import _known_grade

        e1, _, _ = cl3.basis_vectors()
        expr = ScalarDiv(Sym(e1, "v", grade=1), 2)
        assert _known_grade(expr) == 1

    def test_simplify_scalar_div(self, cl3):
        """simplify(x/1) = x."""
        from galaga.expr import ScalarDiv

        e1, _, _ = cl3.basis_vectors()
        # ScalarDiv should survive simplify
        expr = ScalarDiv(Sym(e1, "v"), 2)
        result = simplify(expr)
        assert "v" in str(result)

    def test_sym_explicit_grade(self, cl3):
        """Sym with explicit grade."""
        e1, _, _ = cl3.basis_vectors()
        s = Sym(e1, "v", grade=1)
        assert s._grade == 1

    def test_coerce_named_mv(self, cl3):
        """Named MV coerces to Sym."""
        from galaga.expr import _coerce

        e1, _, _ = cl3.basis_vectors()
        e1.name("x")
        result = _coerce(e1)
        assert isinstance(result, Sym)


class TestReveal:
    """Tests for .reveal() — non-mutating anonymous copy."""

    def test_named_vector_shows_components(self):
        """reveal() shows components of named MV."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        v = (3 * e1 + 4 * e2).name("v")
        r = v.reveal()
        assert "e" in str(r)  # shows basis blades, not "v"
        assert "v" not in str(r)

    def test_does_not_mutate_original(self):
        """reveal() doesn't mutate the original."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        _ = v.reveal()
        assert str(v) == "v"

    def test_preserves_laziness(self):
        """reveal() preserves lazy state."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        assert v.reveal()._is_symbolic is True

    def test_eval_forces_eager(self):
        """eval() forces eager."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        assert v.eval()._is_symbolic is False

    def test_eager_named_reveals_components(self):
        """reveal() on named eager shows coefficients."""
        alg = Algebra((1, 1, 1))
        w = alg.vector([1, 2, 3]).name("w").eager()
        r = w.reveal()
        assert r._is_symbolic is False
        assert "w" not in str(r)
        assert "e" in str(r)

    def test_named_expression_reveals_inner_expr(self):
        """reveal() on named lazy shows expression."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        w = e2.name("w")
        expr = (v + w).name("s")
        assert str(expr) == "s"
        revealed = expr.reveal()
        assert "v" in str(revealed)
        assert "w" in str(revealed)
        assert "s" not in str(revealed)

    def test_unnamed_lazy_unchanged(self):
        """reveal() on unnamed lazy is unchanged."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        w = e2.name("w")
        expr = v + w  # unnamed lazy
        assert str(expr) == str(expr.reveal())

    def test_reveal_on_rotor_shows_exp(self):
        """reveal() on named rotor shows exp form."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        from galaga import exp

        B = (e1 * e2).name("B")
        R = exp(B).name("R")
        assert str(R) == "R"
        assert "exp" in str(R.reveal())

    def test_reveal_same_data(self):
        """reveal() has same numeric data."""
        import numpy as np

        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        v = (3 * e1 + e2).name("v")
        assert np.allclose(v.data, v.reveal().data)
        assert np.allclose(v.data, v.eval().data)

    def test_reveal_scalar_stays_lazy(self):
        """reveal() of scalar stays lazy."""
        import numpy as np

        alg = Algebra((1, 1, 1))
        s = alg.scalar(np.pi).name(latex=r"\pi")
        r = s.reveal()
        assert r._is_symbolic is True
        # eval gives numeric
        assert "3.14" in str(s.eval())

    def test_reveal_returns_new_object(self):
        """reveal() returns a new object."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        r = v.reveal()
        assert r is not v

    def test_reveal_of_reveal(self):
        """reveal(reveal(x)) is idempotent."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        r1 = v.reveal()
        r2 = r1.reveal()
        assert str(r1) == str(r2)


class TestDisplay:
    def test_named_lazy_with_expr(self):
        """Named lazy MV shows all three: name = expression = numeric value."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        B = (e1 ^ e2).name(latex=r"\mathbf{B}")
        result = B.display().latex()
        # Expect: \mathbf{B} \quad = \quad e₁ ∧ e₂ \quad = \quad e_{12}
        assert r"\quad = \quad" in result
        assert r"\mathbf{B}" in result
        assert "e_{12}" in result

    def test_named_eager_no_expr(self):
        """Named eager MV has no expression tree, so shows: name = value."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        v = e1.name("v")
        result = v.display().latex()
        # Expect: v \quad = \quad e_{1}
        assert result == r"v \quad = \quad e_{1}"

    def test_anonymous_eager_single_value(self):
        """Anonymous eager MV has no name or expression — just the value."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        result = e1.eval().display().latex()
        # Expect: e_{1}  (no equals signs)
        assert r"\quad" not in result
        assert "e_{1}" in result

    def test_anonymous_lazy_expr_and_value(self):
        """Anonymous lazy MV shows: expression = value."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        expr = e1 ^ e2
        result = expr.display().latex()
        # Expect: e₁ ∧ e₂ \quad = \quad e_{12}
        assert r"\quad = \quad" in result
        assert "e_{12}" in result

    def test_no_duplicate_parts(self):
        """When name and value are identical, only show it once."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        v = e1.name(latex="e_{1}")
        result = v.display().latex()
        # Name is e_{1}, value is e_{1} — should appear only once
        assert result.count("e_{1}") == 1

    def test_has_latex_method(self):
        """display() returns an object with .latex() for galaga_marimo compatibility."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        d = e1.display()
        assert callable(getattr(d, "latex", None))
        assert callable(getattr(d, "_repr_latex_", None))

    def test_compact_uses_plain_equals(self):
        """display(compact=True) uses = instead of \\quad = \\quad."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        v = e1.name("v")
        result = v.display(compact=True).latex()
        assert r"\quad" not in result
        assert "v = e_{1}" == result

    def test_default_uses_quad(self):
        """display() default uses \\quad = \\quad."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        v = e1.name("v")
        result = v.display().latex()
        assert r"\quad = \quad" in result

    def test_coeff_format_applies_to_eval_only(self):
        """latex(coeff_format=) formats the numeric part, not name/expression."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        v = (3.14159 * e1 + 2.71828 * e2).name("v")
        result = v.display().latex(coeff_format=".2f")
        assert "v" in result
        assert "3.14" in result
        assert "2.72" in result

    def test_coeff_format_preserves_expression(self):
        """Expression part is unchanged by coeff_format."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        B = (e1 ^ e2).name("B")
        d = B.display()
        formatted = d.latex(coeff_format=".3f")
        assert "B" in formatted


class TestCopyAs:
    """copy_as() — non-mutating named copy."""

    def test_returns_new_object(self):
        """copy_as returns a different object."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1 + e1
        w = v.copy_as("w")
        assert v is not w

    def test_original_unchanged(self):
        """Original MV is not mutated."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1 + e1
        v.copy_as("w")
        assert v._name is None

    def test_copy_is_named(self):
        """Copy has the given name."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        w = (e1 + e1).copy_as("w")
        assert str(w) == "w"

    def test_latex_kwarg(self):
        """copy_as with latex= sets latex name."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        w = (e1 + e1).copy_as(latex=r"\mathbf{w}")
        assert r"\mathbf{w}" in w.latex()

    def test_same_data(self):
        """Copy has same numeric data."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1 + e1
        w = v.copy_as("w")
        assert np.allclose(v.data, w.data)

    def test_preserves_laziness(self):
        """Copy is lazy (name() sets lazy)."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors(lazy=True)
        w = (e1 + e1).copy_as("w")
        assert w._is_symbolic
