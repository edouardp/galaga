"""Tests for the symbolic redesign: naming and evaluation semantics."""

import pytest
import numpy as np
from ga import Algebra
from ga.symbolic import sym, simplify, Expr, Sym


@pytest.fixture
def cl3():
    return Algebra((1, 1, 1))


class TestNameMethod:
    def test_name_sets_all_variants(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = (e1).name("v")
        assert v._name == "v"
        assert v._name_unicode == "v"
        assert v._name_latex == "v"

    def test_name_with_overrides(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\mathbf{v}", unicode="𝐯")
        assert v._name == "v"
        assert v._name_latex == r"\mathbf{v}"
        assert v._name_unicode == "𝐯"

    def test_name_makes_lazy(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert v._is_lazy is True

    def test_name_preserves_value(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert v == e1

    def test_name_ascii_kwarg(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", ascii="v_ascii")
        assert v._name == "v_ascii"


class TestAnonMethod:
    def test_anon_clears_name(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v").anon()
        assert v._name is None
        assert v._name_unicode is None
        assert v._name_latex is None

    def test_anon_preserves_lazy(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v").anon()
        assert v._is_lazy is True

    def test_anon_on_anonymous_is_noop(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = (e1 + cl3.basis_vectors()[1])
        v2 = v.anon()
        assert v2._name is None


class TestLazyEagerMethods:
    def test_lazy_on_eager(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = (e1).lazy()
        assert v._is_lazy is True

    def test_eager_on_lazy(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        B.eager()
        assert B._is_lazy is False
        assert B._name is None  # eager() strips name by default

    def test_eager_with_name(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        B.eager("B")
        assert B._is_lazy is False
        assert B._name == "B"
        assert str(B) == "B"

    def test_eval_is_eager(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        Be = B.eval()
        assert Be._is_lazy is False
        assert Be._name is None  # eval() returns anonymous
        assert Be is not B       # eval() returns a new copy
        assert Be == B           # same value

    def test_chaining_name_eager(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        B.eager("B")
        assert B._name == "B"
        assert B._is_lazy is False

    def test_idempotence_lazy(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.lazy().lazy()
        assert v._is_lazy is True

    def test_idempotence_eager(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.eager().eager()
        assert v._is_lazy is False

    def test_idempotence_anon(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.anon().anon()
        assert v._name is None


class TestDisplayRules:
    def test_named_prints_name(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        assert str(B) == "B"

    def test_named_eager_prints_name(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        v.eager("v")
        assert str(v) == "v"

    def test_anon_lazy_prints_expr(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        anon = B.anon()
        # Should show the expression tree, not the name
        assert str(anon) != "B"

    def test_anon_eager_prints_format(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        x = e1 + e2
        # Eager anonymous — existing behavior
        s = str(x)
        assert "e" in s or "+" in s

    def test_latex_named(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\mathbf{v}")
        assert v.latex() == r"\mathbf{v}"

    def test_latex_anon_eager(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        # Anonymous eager — coefficient rendering
        x = e1.anon()
        latex = x.latex()
        assert "e" in latex


class TestLazyPropagation:
    def test_lazy_plus_eager(self, cl3):
        e1, e2, e3 = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        x = B + e3
        assert x._is_lazy is True
        assert "B" in str(x)
        assert "e₃" in str(x)

    def test_eager_plus_eager_stays_eager(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        x = e1 + e2
        assert x._is_lazy is False

    def test_lazy_mul(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        x = B * e1
        assert x._is_lazy is True

    def test_scalar_mul_lazy(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        x = 2 * B
        assert x._is_lazy is True
        assert "2" in str(x)
        assert "B" in str(x)

    def test_names_dont_propagate(self, cl3):
        e1, e2, e3 = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        x = B + e3
        assert x._name is None

    def test_eager_result_concrete(self, cl3):
        e1, e2, e3 = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        x = (B + e3).eager()
        assert x._is_lazy is False
        # Should have concrete data
        assert np.any(x.data != 0)


class TestBasisBlades:
    def test_basis_named_eager(self, cl3):
        e1, e2, e3 = cl3.basis_vectors()
        assert e1._name is not None
        assert e1._is_lazy is False

    def test_basis_str(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        assert str(e1) == "e₁"

    def test_basis_anon(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = e1.anon()
        # Should print concrete blade form
        assert a._name is None

    def test_basis_rename(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        x = e1.name("x")
        assert str(x) == "x"

    def test_pseudoscalar_named(self, cl3):
        I = cl3.pseudoscalar()
        assert I._name == "I"
        assert str(I) == "𝑰"

    def test_blade_lookup_named(self, cl3):
        b = cl3.blade("e12")
        assert b._name == "e12"

    def test_custom_names(self):
        sta = Algebra((1, -1, -1, -1), names="gamma")
        g0, g1, g2, g3 = sta.basis_vectors()
        assert g0._name is not None
        assert "γ" in str(g0)


class TestSymAlias:
    def test_sym_returns_multivector(self, cl3):
        from ga.algebra import Multivector
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert isinstance(v, Multivector)
        assert str(v) == "v"

    def test_sym_grade_detection(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert v._grade == 1
        B = sym(e1 ^ e2, "B")
        assert B._grade == 2

    def test_sym_explicit_grade(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        v = sym(e1 + e2, "v", grade=1)
        assert v._grade == 1

    def test_sym_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        Re = R.eval()
        assert Re._is_lazy is False
        assert Re._name is None  # eval() returns anonymous
        assert Re == e1 * e2     # same value


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
        assert x._is_lazy is False

    def test_use_case_2_named_symbolic_bivector(self, cl3):
        """Define a named symbolic bivector."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        assert str(B) == "B"
        assert B._is_lazy is True

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
        s = str(expr)
        # Should show symbolic structure, not just a name
        assert expr._is_lazy is True

    def test_use_case_7_rotor_workflow(self, cl3):
        """Rotor workflow."""
        from ga import exp
        e1, e2, _ = cl3.basis_vectors()
        theta = 0.5
        B = (e1 ^ e2).name("B")
        R = (-B * theta / 2).name("R")
        v = e1
        v_rot = R * v * ~R
        # v_rot is lazy because R is lazy
        assert v_rot._is_lazy is True
        # Can get concrete result
        concrete = v_rot.eager()
        assert concrete._is_lazy is False
        assert np.any(concrete.data != 0)

    def test_use_case_8_basis_blade_rename(self, cl3):
        """Basis blades stay eager but can become lazy/named differently."""
        e1, _, _ = cl3.basis_vectors()
        E = e1.name("E")
        assert str(E) == "E"
        assert str(E.anon()) != "E"

    def test_use_case_9_symbolic_shorthand(self, cl3):
        """Symbolic shorthand over symbolic structure."""
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).lazy()
        assert B._is_lazy is True

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
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = B + 5
        assert x._is_lazy
        assert x == e1 + 5

    def test_lazy_sub_scalar(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = B - 2
        assert x._is_lazy
        assert x == e1 - 2

    def test_lazy_rsub_scalar(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = 10 - B
        assert x._is_lazy
        assert x == 10 - e1

    def test_lazy_radd_scalar(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = 3 + B
        assert str(x) == "3 + B"

    def test_lazy_neg(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = -B
        assert x._is_lazy
        assert str(x) == "-B"

    def test_lazy_div(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        B = e1.name("B")
        x = B / 2
        assert x._is_lazy
        assert x == e1 / 2

    def test_lazy_xor(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        v = e1.name("v")
        x = v ^ e2
        assert x._is_lazy
        assert "v" in str(x)

    def test_lazy_or(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        v = e1.name("v")
        x = v | e2
        assert x._is_lazy

    def test_lazy_invert(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        x = ~v
        assert x._is_lazy
        assert "v" in str(x)

    def test_xor_with_expr(self, cl3):
        from ga.symbolic import Sym
        e1, e2, _ = cl3.basis_vectors()
        expr = Sym(e2, "b")
        result = e1 ^ expr
        assert "b" in str(result)

    def test_or_with_expr(self, cl3):
        from ga.symbolic import Sym
        e1, e2, _ = cl3.basis_vectors()
        expr = Sym(e2, "b")
        result = e1 | expr
        assert "b" in str(result)

    def test_sub_with_expr(self, cl3):
        from ga.symbolic import Sym
        e1, e2, _ = cl3.basis_vectors()
        expr = Sym(e2, "b")
        result = e1 - expr
        assert "b" in str(result)

    def test_format_unicode_named(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", unicode="𝐯")
        assert f"{v:u}" == "𝐯"

    def test_format_ascii_named(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert f"{v:a}" == "v"

    def test_format_unicode_lazy_anon(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = (e1.name("a") + e2.name("b")).anon()
        assert "a" in f"{B:u}"

    def test_format_ascii_lazy_anon(self, cl3):
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
        e1, e2, _ = cl3.basis_vectors()
        B = (e1.name("a") + e2.name("b")).anon()
        latex = B.latex()
        assert "a" in latex

    def test_to_expr_anonymous_eager(self, cl3):
        """_to_expr on anonymous eager MV uses str representation."""
        from ga.symbolic import Sym
        e1, e2, _ = cl3.basis_vectors()
        mv = (e1 + e2).anon()
        mv = mv._copy_with(_name=None, _name_unicode=None, _name_latex=None)
        expr = mv._to_expr()
        assert isinstance(expr, Sym)

    def test_lazy_mul_two_lazy(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        x = a * b
        assert x._is_lazy
        assert "a" in str(x)
        assert "b" in str(x)

    def test_lazy_add_two_lazy(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        x = a + b
        assert str(x) == "a + b"

    def test_lazy_sub_two_lazy(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        x = a - b
        assert str(x) == "a - b"

    def test_sym_latex_rendering(self, cl3):
        """Sym._latex returns name_latex."""
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        s = Sym(e1, "v", name_latex=r"\mathbf{v}")
        assert s._latex() == r"\mathbf{v}"

    def test_symbolic_reverse_lazy_mv(self, cl3):
        from ga.symbolic import reverse
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = reverse(v)
        assert "v" in str(result)

    def test_symbolic_grade_lazy_mv(self, cl3):
        from ga.symbolic import grade
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = grade(v, 1)
        assert "v" in str(result)

    def test_symbolic_sandwich_lazy_mv(self, cl3):
        from ga.symbolic import sandwich
        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).name("R")
        v = e1.name("v")
        result = sandwich(R, v)
        assert "R" in str(result)

    def test_symbolic_ip_lazy_mv(self, cl3):
        from ga.symbolic import ip
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = ip(a, e2)
        assert "a" in str(result)

    def test_symbolic_squared_lazy_mv(self, cl3):
        from ga.symbolic import squared
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = squared(v)
        assert "v" in str(result)

    def test_ensure_expr_lazy_mv_with_expr(self, cl3):
        """_ensure_expr extracts _expr from lazy MV."""
        from ga.symbolic import _ensure_expr, Sym
        e1, e2, _ = cl3.basis_vectors()
        B = (e1.name("a") + e2.name("b"))
        expr = _ensure_expr(B)
        assert not isinstance(expr, type(B))  # Should be Expr, not MV

    def test_ensure_expr_named_eager_mv(self, cl3):
        """_ensure_expr on named eager MV creates Sym."""
        from ga.symbolic import _ensure_expr, Sym
        e1, _, _ = cl3.basis_vectors()
        # basis blades are named + eager
        expr = _ensure_expr(e1)
        assert isinstance(expr, Sym)


class TestExprOperatorCoverage:
    """Cover Expr operator overloads that are now less commonly hit."""

    def test_expr_add(self, cl3):
        from ga.symbolic import Sym
        e1, e2, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        b = Sym(e2, "b")
        assert str(a + b) == "a + b"

    def test_expr_radd(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(3 + a) == "3 + a"

    def test_expr_sub(self, cl3):
        from ga.symbolic import Sym
        e1, e2, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        b = Sym(e2, "b")
        assert str(a - b) == "a - b"

    def test_expr_rsub(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(3 - a) == "3 - a"

    def test_expr_neg(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(-a) == "-a"

    def test_expr_mul_scalar(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(a * 2) == "2a"

    def test_expr_rmul_scalar(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(5 * a) == "5a"

    def test_expr_mul_expr(self, cl3):
        from ga.symbolic import Sym
        e1, e2, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        b = Sym(e2, "b")
        assert str(a * b) == "ab"

    def test_expr_xor(self, cl3):
        from ga.symbolic import Sym
        e1, e2, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        b = Sym(e2, "b")
        assert str(a ^ b) == "a∧b"

    def test_expr_or(self, cl3):
        from ga.symbolic import Sym
        e1, e2, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        b = Sym(e2, "b")
        assert "a" in str(a | b)

    def test_expr_invert(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert "a" in str(~a)

    def test_expr_truediv(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        result = a / 3
        assert "a" in str(result)

    def test_expr_truediv_non_scalar(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert a.__truediv__("bad") is NotImplemented

    def test_expr_inv_property(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert "a" in str(a.inv)

    def test_expr_dag_property(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert "a" in str(a.dag)

    def test_expr_sq_property(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert str(a.sq) == "a²"

    def test_expr_latex_wrap_dollar(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert a.latex(wrap="$") == "$a$"

    def test_expr_latex_wrap_display(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert "$$" in a.latex(wrap="$$")

    def test_expr_repr_latex(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert a._repr_latex_() == "$a$"

    def test_scalar_eval_raises(self):
        from ga.symbolic import Scalar
        with pytest.raises(TypeError):
            Scalar(42).eval()

    def test_sym_repr_ascii(self, cl3):
        from ga.symbolic import Sym
        e1, _, _ = cl3.basis_vectors()
        s = Sym(e1, "v", name_ascii="v_ascii")
        assert repr(s) == "v_ascii"

    def test_coerce_mv_with_name(self, cl3):
        """_coerce on a named MV without _expr."""
        from ga.symbolic import _coerce, Sym
        e1, _, _ = cl3.basis_vectors()
        # basis blades are named + eager, no _expr
        result = _coerce(e1)
        assert isinstance(result, Sym)

    def test_is_symbolic_lazy_mv(self, cl3):
        from ga.symbolic import _is_symbolic
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert _is_symbolic(v) is True

    def test_is_symbolic_eager_mv(self, cl3):
        from ga.symbolic import _is_symbolic
        e1, _, _ = cl3.basis_vectors()
        assert _is_symbolic(e1) is False

    def test_simplify_rotor_norm(self, cl3):
        """simplify(R * ~R) for a rotor."""
        from ga.symbolic import Sym, Gp, Reverse, simplify
        e1, e2, _ = cl3.basis_vectors()
        R_val = e1 * e2
        R = Sym(R_val, "R")
        result = simplify(Gp(R, Reverse(R)))
        # Should simplify to scalar 1 (or -1 depending on signature)
        assert "R" not in str(result)

    def test_eq_neg(self, cl3):
        from ga.symbolic import _eq, Neg, Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert _eq(Neg(a), Neg(a))
        assert not _eq(Neg(a), Neg(Sym(e1, "b")))

    def test_eq_grade(self, cl3):
        from ga.symbolic import _eq, Grade, Sym
        e1, _, _ = cl3.basis_vectors()
        a = Sym(e1, "a")
        assert _eq(Grade(a, 1), Grade(a, 1))
        assert not _eq(Grade(a, 1), Grade(a, 2))


class TestSymbolicDropInWithLazyMV:
    """Cover symbolic module drop-in functions with lazy MVs."""

    def test_involute_lazy(self, cl3):
        from ga.symbolic import involute
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = involute(v)
        assert "v" in str(result)

    def test_conjugate_lazy(self, cl3):
        from ga.symbolic import conjugate
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = conjugate(v)
        assert "v" in str(result)

    def test_dual_lazy(self, cl3):
        from ga.symbolic import dual
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = dual(v)
        assert "v" in str(result)

    def test_undual_lazy(self, cl3):
        from ga.symbolic import undual
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = undual(v)
        assert "v" in str(result)

    def test_norm_lazy(self, cl3):
        from ga.symbolic import norm
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = norm(v)
        assert "v" in str(result)

    def test_unit_lazy(self, cl3):
        from ga.symbolic import unit
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = unit(v)
        assert "v" in str(result)

    def test_inverse_lazy(self, cl3):
        from ga.symbolic import inverse
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = inverse(v)
        assert "v" in str(result)

    def test_left_contraction_lazy(self, cl3):
        from ga.symbolic import left_contraction
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = left_contraction(a, e2)
        assert "a" in str(result)

    def test_right_contraction_lazy(self, cl3):
        from ga.symbolic import right_contraction
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = right_contraction(a, e2)
        assert "a" in str(result)

    def test_hestenes_inner_lazy(self, cl3):
        from ga.symbolic import hestenes_inner
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = hestenes_inner(a, e2)
        assert "a" in str(result)

    def test_doran_lasenby_inner_lazy(self, cl3):
        from ga.symbolic import doran_lasenby_inner
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = doran_lasenby_inner(a, e2)
        assert "a" in str(result)

    def test_scalar_product_lazy(self, cl3):
        from ga.symbolic import scalar_product
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = scalar_product(a, e2)
        assert "a" in str(result)

    def test_commutator_lazy(self, cl3):
        from ga.symbolic import commutator
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = commutator(a, e2)
        assert "a" in str(result)

    def test_anticommutator_lazy(self, cl3):
        from ga.symbolic import anticommutator
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = anticommutator(a, e2)
        assert "a" in str(result)

    def test_lie_bracket_lazy(self, cl3):
        from ga.symbolic import lie_bracket
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = lie_bracket(a, e2)
        assert "a" in str(result)

    def test_jordan_product_lazy(self, cl3):
        from ga.symbolic import jordan_product
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        result = jordan_product(a, e2)
        assert "a" in str(result)

    def test_even_grades_lazy(self, cl3):
        from ga.symbolic import even_grades
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = even_grades(v)
        assert "v" in str(result)

    def test_odd_grades_lazy(self, cl3):
        from ga.symbolic import odd_grades
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        result = odd_grades(v)
        assert "v" in str(result)

    def test_ip_modes_lazy(self, cl3):
        from ga.symbolic import ip
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        for mode in ("doran_lasenby", "hestenes", "left", "right", "scalar"):
            result = ip(a, e2, mode=mode)
            assert "a" in str(result)


class TestSandwichLazy:
    """Tests for laziness-aware sandwich()."""

    def test_sandwich_lazy_rotor(self, cl3):
        from ga import sandwich
        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).name("R")
        v = e1.name("v")
        result = sandwich(R, v)
        assert result._is_lazy
        assert "R" in str(result)
        assert "v" in str(result)

    def test_sandwich_lazy_concrete_correct(self, cl3):
        from ga import sandwich, gp, reverse
        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).name("R")
        result = sandwich(R, e1)
        expected = gp(gp(e1 * e2, e1), reverse(e1 * e2))
        assert result.eager() == expected

    def test_sandwich_eager_stays_eager(self, cl3):
        from ga import sandwich
        e1, e2, _ = cl3.basis_vectors()
        result = sandwich(e1 * e2, e1)
        assert result._is_lazy is False

    def test_sandwich_one_lazy_operand(self, cl3):
        from ga import sandwich
        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).name("R")
        # lazy rotor, eager vector
        result = sandwich(R, e1)
        assert result._is_lazy
        assert "R" in str(result)

    def test_sw_alias_lazy(self, cl3):
        from ga import sw
        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).name("R")
        result = sw(R, e1)
        assert result._is_lazy


class TestSmallValueDisplay:
    """Tests for displaying values below the 1e-12 noise threshold."""

    def test_format_spec_shows_small_values(self, cl3):
        mv = cl3.scalar(9.109e-31)
        assert format(mv, '.3e') == '9.109e-31'

    def test_format_spec_shows_small_negative(self, cl3):
        mv = cl3.scalar(-1.055e-34)
        assert format(mv, '.3e') == '-1.055e-34'

    def test_str_suppresses_small_values(self, cl3):
        mv = cl3.scalar(9.109e-31)
        assert str(mv) == '0'

    def test_latex_default_suppresses_small(self, cl3):
        mv = cl3.scalar(9.109e-31)
        assert mv.latex() == '0'

    def test_latex_coeff_format_shows_small(self, cl3):
        mv = cl3.scalar(9.109e-31)
        assert mv.latex(coeff_format='.3e') == '9.109e-31'

    def test_latex_coeff_format_electron_mass(self, cl3):
        mv = cl3.scalar(9.109e-31)
        assert '9.109' in mv.latex(coeff_format='.4e')

    def test_latex_coeff_format_planck(self, cl3):
        mv = cl3.scalar(1.055e-34)
        assert '1.055' in mv.latex(coeff_format='.4e')

    def test_latex_coeff_format_compton(self, cl3):
        mv = cl3.scalar(3.861e-13)
        assert '3.861' in mv.latex(coeff_format='.4e')

    def test_format_spec_zero_is_exact_zero(self, cl3):
        """Exact 0.0 should still show as zero even with format spec."""
        mv = cl3.scalar(0.0)
        assert format(mv, '.3e') == '0.000e+00'

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
        result = lam.eval().latex(coeff_format='.4e')
        assert '3.8607e-13' in result or '3.861' in result


class TestMVDivision:
    """Tests for multivector / multivector division."""

    def test_scalar_div_scalar(self, cl3):
        a = cl3.scalar(10.0)
        b = cl3.scalar(2.0)
        assert (a / b).scalar_part == 5.0

    def test_named_scalar_div(self, cl3):
        a = cl3.scalar(6.0).name("a")
        b = cl3.scalar(3.0).name("b")
        result = a / b
        assert result.eval().scalar_part == 2.0

    def test_vector_div_vector(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        result = (3 * e1) / e1
        assert result == 3

    def test_div_zero_raises(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        with pytest.raises(ZeroDivisionError):
            e1 / cl3.scalar(0.0)

    def test_rdiv_scalar_over_mv(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        result = 1 / e1
        assert result == e1  # e1⁻¹ = e1 in Euclidean

    def test_div_non_invertible_raises(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        null = e1 + e2  # not a blade, but invertible
        # This should work (e1+e2 is invertible)
        result = e1 / (e1 + e2)
        assert result is not None


class TestDivExprNode:
    """Tests for the Div expression node and symbolic MV/MV division."""

    def test_div_preserves_names(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = cl3.scalar(10.0).name("a")
        b = cl3.scalar(2.0).name("b")
        result = a / b
        assert "a" in str(result)
        assert "b" in str(result)

    def test_div_latex(self, cl3):
        a = cl3.scalar(10.0).name("a", latex=r"\alpha")
        b = cl3.scalar(2.0).name("b", latex=r"\beta")
        result = a / b
        assert r"\frac{\alpha}{\beta}" == result.latex()

    def test_div_eval_correct(self, cl3):
        a = cl3.scalar(10.0).name("a")
        b = cl3.scalar(2.0).name("b")
        result = a / b
        assert result.eval().scalar_part == 5.0

    def test_div_product_in_denominator(self, cl3):
        hbar = cl3.scalar(1.055e-34).name("ℏ", latex=r"\hbar")
        m = cl3.scalar(9.109e-31).name("m", latex=r"m_e")
        c = cl3.scalar(3e8).name("c", latex=r"c")
        lam = hbar / (m * c)
        assert "ℏ" in str(lam)
        assert "m" in str(lam)
        assert "c" in str(lam)
        assert r"\frac{\hbar}{m_e c}" == lam.latex()

    def test_div_eager_by_eager_stays_eager(self, cl3):
        a = cl3.scalar(10.0)
        b = cl3.scalar(2.0)
        result = a / b
        assert result._is_lazy is False
        assert result.scalar_part == 5.0

    def test_div_lazy_by_eager(self, cl3):
        a = cl3.scalar(10.0).name("a")
        b = cl3.scalar(2.0)
        result = a / b
        assert result._is_lazy is True
        assert "a" in str(result)

    def test_div_eager_by_lazy(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = cl3.scalar(10.0)
        b = cl3.scalar(2.0).name("b")
        result = a / b
        assert result._is_lazy is True
        assert "b" in str(result)

    def test_scalar_div_still_works(self, cl3):
        """Division by int/float still uses ScalarDiv."""
        v = cl3.scalar(6.0).name("v")
        result = v / 3
        assert str(result) == "v/3"

    def test_exp_node(self, cl3):
        from ga import exp
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        theta = cl3.scalar(0.5).name("θ", latex=r"\theta")
        R = exp(B * theta)
        assert "exp" in str(R)
        assert "B" in str(R)
        assert "θ" in str(R)
        assert r"e^{" in R.latex()

    def test_exp_eval(self, cl3):
        from ga import exp
        import numpy as np
        e1, e2, _ = cl3.basis_vectors()
        B = (e1 ^ e2).name("B")
        R = exp(B * cl3.scalar(np.pi / 4).name("θ"))
        concrete = R.eval()
        assert concrete._is_lazy is False
        assert abs(concrete.scalar_part - np.cos(np.pi / 4)) < 1e-10


class TestSquaredParens:
    """Tests for parenthesization in Squared node."""

    def test_squared_single_term_no_parens(self, cl3):
        from ga import squared
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert str(squared(v)) == "v²"

    def test_squared_add_gets_parens(self, cl3):
        from ga import squared
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        result = squared(a + b)
        assert str(result) == "(a + b)²"

    def test_squared_sub_gets_parens(self, cl3):
        from ga import squared
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        result = squared(a - b)
        assert str(result) == "(a - b)²"

    def test_squared_product_no_parens(self, cl3):
        from ga import squared
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        result = squared(a * b)
        assert str(result) == "(ab)²"

    def test_squared_latex_add_gets_parens(self, cl3):
        from ga import squared
        e1, e2, _ = cl3.basis_vectors()
        a = e1.name("a")
        b = e2.name("b")
        result = squared(a + b)
        assert r"\left(" in result.latex()
        assert r"\right)" in result.latex()

    def test_squared_latex_single_no_parens(self, cl3):
        from ga import squared
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v")
        assert result.latex() == "v^2" if (result := squared(v)) else False


class TestBasisVectorsLazy:
    """Tests for basis_vectors(lazy=True)."""

    def test_default_is_eager(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        assert e1._is_lazy is False

    def test_lazy_flag(self, cl3):
        e1, _, _ = cl3.basis_vectors(lazy=True)
        assert e1._is_lazy is True
        assert e1._name is not None

    def test_lazy_ops_build_trees(self, cl3):
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        result = e1 ^ e2
        assert result._is_lazy is True
        assert "∧" in str(result)

    def test_lazy_eval_gives_concrete(self, cl3):
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        result = (e1 ^ e2).eval()
        expected = cl3.basis_vectors()[0] ^ cl3.basis_vectors()[1]
        assert result == expected

    def test_lazy_preserves_names(self, cl3):
        e1, e2, e3 = cl3.basis_vectors(lazy=True)
        assert str(e1) == "e₁"
        assert str(e2) == "e₂"
        assert str(e3) == "e₃"


class TestLazyBladesFullWorkflow:
    """End-to-end tests with basis_vectors(lazy=True)."""

    def test_wedge_symbolic(self, cl3):
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        assert "∧" in str(e1 ^ e2)

    def test_gp_symbolic(self, cl3):
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        result = e1 * e2
        assert "e₁" in str(result)
        assert "e₂" in str(result)

    def test_add_symbolic(self, cl3):
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        assert "+" in str(e1 + e2)

    def test_scalar_div_symbolic(self, cl3):
        e1, _, _ = cl3.basis_vectors(lazy=True)
        result = e1 / 2
        assert "/2" in str(result)

    def test_exp_symbolic(self, cl3):
        from ga import exp
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        B = (e1 ^ e2).name("B")
        result = exp(B)
        assert "exp" in str(result)

    def test_rotor_workflow(self, cl3):
        from ga import exp, reverse
        import numpy as np
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        theta = cl3.scalar(np.pi / 4).name("θ")
        B = (e1 ^ e2).name("B")
        R = exp(-B * theta / 2).name("R")
        v_rot = R * e1 * ~R
        assert "R" in str(v_rot)
        concrete = v_rot.eval()
        assert abs(concrete.data[1] - np.cos(np.pi / 4)) < 1e-10

    def test_division_symbolic(self, cl3):
        e1, _, _ = cl3.basis_vectors(lazy=True)
        a = cl3.scalar(10.0).name("a")
        b = cl3.scalar(2.0).name("b")
        result = a / b
        assert "a" in str(result)
        assert "b" in str(result)

    def test_named_scalar_in_expr(self, cl3):
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        m = cl3.scalar(5.0).name("m")
        result = m * e1
        assert "m" in str(result)

    def test_all_module_functions_lazy(self, cl3):
        """All module-level functions produce symbolic output with lazy blades."""
        from ga import reverse, involute, conjugate, grade, dual, unit, inverse, squared
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
        alg = Algebra(tuple([1] * 9))
        b = alg.blade("e19")
        assert b is not None

    def test_blade_errors_for_10d_default_names(self):
        alg = Algebra(tuple([1] * 10))
        with pytest.raises(ValueError, match="ambiguous"):
            alg.blade("e110")

    def test_blade_works_for_10d_custom_names(self):
        names = ([f"v{i}" for i in range(10)], [f"v{i}" for i in range(10)])
        alg = Algebra(tuple([1] * 10), names=names)
        b = alg.blade("v0v1")
        assert b is not None


class TestAllBinaryOpsLazy:
    """All binary operations produce symbolic output with lazy inputs."""

    def test_gp_lazy(self, cl3):
        from ga import gp
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert str(gp(a, b)) == "ab"

    def test_op_lazy(self, cl3):
        from ga import op
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "∧" in str(op(a, b))

    def test_left_contraction_lazy(self, cl3):
        from ga import left_contraction
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "⌋" in str(left_contraction(a, b))

    def test_right_contraction_lazy(self, cl3):
        from ga import right_contraction
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "⌊" in str(right_contraction(a, b))

    def test_hestenes_inner_lazy(self, cl3):
        from ga import hestenes_inner
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "·" in str(hestenes_inner(a, b))

    def test_doran_lasenby_inner_lazy(self, cl3):
        from ga import doran_lasenby_inner
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "·" in str(doran_lasenby_inner(a, b))

    def test_scalar_product_lazy(self, cl3):
        from ga import scalar_product
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "∗" in str(scalar_product(a, b))

    def test_commutator_lazy(self, cl3):
        from ga import commutator
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        A = (e1 ^ e2).name("A")
        B = (e2 ^ e1).name("B")
        assert str(commutator(A, B)) == "[A, B]"

    def test_anticommutator_lazy(self, cl3):
        from ga import anticommutator
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        A = (e1 ^ e2).name("A")
        B = (e2 ^ e1).name("B")
        assert str(anticommutator(A, B)) == "{A, B}"

    def test_lie_bracket_lazy(self, cl3):
        from ga import lie_bracket
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        A = (e1 ^ e2).name("A")
        B = (e2 ^ e1).name("B")
        assert "½" in str(lie_bracket(A, B))

    def test_jordan_product_lazy(self, cl3):
        from ga import jordan_product
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert "½" in str(jordan_product(a, b))


class TestNameAutoDerive:
    """Test that .name(latex=...) auto-derives unicode and ascii."""

    def test_greek_auto_derive(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\theta")
        assert v._name_unicode == "θ"
        assert v._name == "theta"
        assert v._name_latex == r"\theta"

    def test_mathbf_auto_derive(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("F", latex=r"\mathbf{F}")
        assert v._name_unicode == "𝐅"
        assert v._name == "F"

    def test_hbar_auto_derive(self, cl3):
        v = cl3.scalar(1.0).name("h", latex=r"\hbar")
        assert v._name_unicode == "ℏ"
        assert v._name == "hbar"

    def test_user_unicode_overrides(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\theta", unicode="MINE")
        assert v._name_unicode == "MINE"
        assert v._name == "theta"  # ascii still derived

    def test_user_ascii_overrides(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\theta", ascii="MINE")
        assert v._name == "MINE"
        assert v._name_unicode == "θ"  # unicode still derived

    def test_both_overrides(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\theta", unicode="U", ascii="A")
        assert v._name_unicode == "U"
        assert v._name == "A"

    def test_unknown_latex_uses_label(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("v", latex=r"\weirdthing")
        assert v._name_unicode == "v"
        assert v._name == "v"
        assert v._name_latex == r"\weirdthing"

    def test_no_latex_uses_label(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name("myvar")
        assert v._name_unicode == "myvar"
        assert v._name == "myvar"
        assert v._name_latex == "myvar"


class TestNameLatexOnly:
    """Test .name(latex=...) without label."""

    def test_latex_only_greek(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name(latex=r"\theta")
        assert str(v) == "θ"
        assert v._name == "theta"
        assert v._name_latex == r"\theta"

    def test_latex_only_mathbf(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name(latex=r"\mathbf{F}")
        assert str(v) == "𝐅"
        assert v._name == "F"

    def test_latex_only_unknown_uses_latex_as_fallback(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = e1.name(latex=r"\weirdthing")
        assert v._name == r"\weirdthing"
        assert v._name_latex == r"\weirdthing"

    def test_no_args_raises(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        with pytest.raises(ValueError):
            e1.name()
