"""Tests for the symbolic expression tree."""

import pytest
import numpy as np
from galaga import Algebra
from galaga import gp as _gp, op as _op, grade as _grade, reverse as _reverse
from galaga.symbolic import (
    sym, gp, op, grade, reverse, involute, conjugate,
    left_contraction, right_contraction, hestenes_inner, scalar_product,
    commutator, anticommutator, lie_bracket, jordan_product,
    dual, undual, norm, unit, inverse, simplify,
    Expr, Sym, Gp, Op, Grade, Reverse, Inverse,
    Commutator, Anticommutator, LieBracket, JordanProduct, Hi,
)


@pytest.fixture
def cl3():
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors()
    return alg, e1, e2, e3


class TestSymRendering:
    def test_sym_str(self, cl3):
        alg, e1, e2, e3 = cl3
        R = sym(e1 * e2, "R")
        assert str(R) == "R"

    def test_gp_str(self, cl3):
        _, e1, e2, _ = cl3
        R = sym(e1 * e2, "R")
        v = sym(e1, "v")
        assert str(R * v) == "Rv"

    def test_sandwich_str(self, cl3):
        _, e1, e2, _ = cl3
        R = sym(e1 * e2, "R")
        v = sym(e1, "v")
        assert str(R * v * ~R) == "RvR̃"

    def test_grade_str(self, cl3):
        _, e1, e2, _ = cl3
        R = sym(e1 * e2, "R")
        v = sym(e1, "v")
        assert str(grade(R * v * ~R, 0)) == "⟨RvR̃⟩₀"
        assert str(grade(R * v * ~R, 1)) == "⟨RvR̃⟩₁"
        assert str(grade(R * v * ~R, 2)) == "⟨RvR̃⟩₂"

    def test_wedge_str(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(a ^ b) == "a∧b"

    def test_left_contraction_str(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(left_contraction(a, b)) == "a⌋b"

    def test_right_contraction_str(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(right_contraction(a, b)) == "a⌊b"

    def test_hestenes_inner_str(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "A")
        b = sym(e2, "B")
        assert str(hestenes_inner(a, b)) == "A·B"

    def test_scalar_product_str(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "A")
        b = sym(e2, "B")
        assert str(scalar_product(a, b)) == "A∗B"

    def test_reverse_str(self, cl3):
        _, e1, e2, _ = cl3
        R = sym(e1 * e2, "R")
        assert str(reverse(R)) == "R̃"
        assert str(~R) == "R̃"

    def test_involute_str(self, cl3):
        _, e1, _, _ = cl3
        v = sym(e1, "v")
        assert str(involute(v)) == "v̂"

    def test_conjugate_str(self, cl3):
        _, e1, _, _ = cl3
        v = sym(e1, "v")
        assert str(conjugate(v)) == "v̄"

    def test_dual_str(self, cl3):
        _, e1, _, _ = cl3
        v = sym(e1, "v")
        assert str(dual(v)) == "v⋆"

    def test_undual_str(self, cl3):
        _, e1, _, _ = cl3
        v = sym(e1, "v")
        assert str(undual(v)) == "v⋆⁻¹"

    def test_norm_str(self, cl3):
        _, e1, _, _ = cl3
        v = sym(e1, "v")
        assert str(norm(v)) == "‖v‖"

    def test_unit_str(self, cl3):
        _, e1, _, _ = cl3
        v = sym(e1, "v")
        assert str(unit(v)) == "v̂"

    def test_inverse_str(self, cl3):
        _, e1, _, _ = cl3
        v = sym(e1, "v")
        assert str(inverse(v)) == "v⁻¹"
        assert str(v.inv) == "v⁻¹"

    def test_dag_str(self, cl3):
        _, e1, e2, _ = cl3
        R = sym(e1 * e2, "R")
        assert str(R.dag) == "R̃"

    def test_sq_str(self, cl3):
        _, e1, e2, _ = cl3
        R = sym(e1 * e2, "R")
        assert str(R.sq) == "R²"

    def test_add_str(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(a + b) == "a + b"

    def test_sub_str(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(a - b) == "a - b"

    def test_neg_str(self, cl3):
        _, e1, _, _ = cl3
        a = sym(e1, "a")
        assert str(-a) == "-a"

    def test_scalar_mul_str(self, cl3):
        _, e1, _, _ = cl3
        a = sym(e1, "a")
        assert str(2 * a) == "2a"
        assert str(-1 * a) == "-a"

    def test_parens_in_product(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "a")
        b = sym(e2, "b")
        c = sym(e1 + e2, "c")
        # (a + b) * c should parenthesise the sum
        expr = (a + b) * c
        assert str(expr) == "(a + b)c"


class TestSymEval:
    """Verify that .eval() produces correct numeric results."""

    def test_gp_eval(self, cl3):
        _, e1, e2, _ = cl3
        R = sym(e1 * e2, "R")
        v = sym(e1, "v")
        result = (R * v).eval()
        expected = _gp(e1 * e2, e1)
        assert np.allclose(result.data, expected.data)

    def test_sandwich_eval(self, cl3):
        _, e1, e2, _ = cl3
        R = sym(e1 * e2, "R")
        v = sym(e1, "v")
        result = (R * v * ~R).eval()
        expected = _gp(_gp(e1 * e2, e1), _reverse(e1 * e2))
        assert np.allclose(result.data, expected.data)

    def test_grade_eval(self, cl3):
        _, e1, e2, _ = cl3
        A = sym(e1, "A")
        B = sym(e2, "B")
        result = grade(A * B, 2).eval()
        expected = _grade(_gp(e1, e2), 2)
        assert np.allclose(result.data, expected.data)

    def test_wedge_eval(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = (a ^ b).eval()
        expected = _op(e1, e2)
        assert np.allclose(result.data, expected.data)

    def test_left_contraction_eval(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "a")
        e12 = sym(e1 * e2, "B")
        result = left_contraction(a, e12).eval()
        assert np.allclose(result.data, e2.data)

    def test_reverse_eval(self, cl3):
        _, e1, e2, _ = cl3
        B = sym(e1 * e2, "B")
        result = reverse(B).eval()
        expected = _reverse(e1 * e2)
        assert np.allclose(result.data, expected.data)

    def test_inverse_eval(self, cl3):
        _, e1, _, _ = cl3
        v = sym(2 * e1, "v")
        result = (v * v.inv).eval()
        alg = cl3[0]
        assert np.allclose(result.data, alg.scalar(1.0).data)

    def test_add_eval(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = (a + b).eval()
        assert np.allclose(result.data, (e1 + e2).data)

    def test_sub_eval(self, cl3):
        _, e1, e2, _ = cl3
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = (a - b).eval()
        assert np.allclose(result.data, (e1 - e2).data)

    def test_neg_eval(self, cl3):
        _, e1, _, _ = cl3
        a = sym(e1, "a")
        result = (-a).eval()
        assert np.allclose(result.data, (-e1).data)

    def test_scalar_mul_eval(self, cl3):
        _, e1, _, _ = cl3
        a = sym(e1, "a")
        result = (3 * a).eval()
        assert np.allclose(result.data, (3 * e1).data)

    def test_norm_eval(self, cl3):
        alg, e1, e2, _ = cl3
        v = sym(alg.vector([3, 4, 0]), "v")
        result = norm(v).eval()
        assert np.isclose(result.scalar_part, 5.0)

    def test_dual_eval(self, cl3):
        _, e1, _, _ = cl3
        from galaga import dual as _dual
        v = sym(e1, "v")
        result = dual(v).eval()
        expected = _dual(e1)
        assert np.allclose(result.data, expected.data)


class TestSymFallback:
    """Verify that symbolic functions fall back to numeric for plain Multivectors."""

    def test_gp_numeric(self, cl3):
        _, e1, e2, _ = cl3
        result = gp(e1, e2)
        assert not isinstance(result, Expr)
        assert np.allclose(result.data, _gp(e1, e2).data)

    def test_grade_numeric(self, cl3):
        _, e1, _, _ = cl3
        result = grade(e1, 1)
        assert not isinstance(result, Expr)

    def test_reverse_numeric(self, cl3):
        _, e1, _, _ = cl3
        result = reverse(e1)
        assert not isinstance(result, Expr)


class TestCommutatorSymbolic:
    """Tests for symbolic commutator/anticommutator/lie_bracket/jordan_product."""

    def test_commutator_builds_tree(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        result = commutator(a, b)
        assert isinstance(result, Commutator)

    def test_commutator_str(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        assert str(commutator(a, b)) == "[a, b]"

    def test_commutator_latex(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        assert r"\," in commutator(a, b).latex()

    def test_commutator_eval(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        result = commutator(a, b).eval()
        expected = _gp(e1, e2) - _gp(e2, e1)
        assert np.allclose(result.data, expected.data)

    def test_anticommutator_builds_tree(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        result = anticommutator(a, b)
        assert isinstance(result, Anticommutator)

    def test_anticommutator_str(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        assert str(anticommutator(a, b)) == "{a, b}"

    def test_lie_bracket_builds_tree(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        result = lie_bracket(a, b)
        assert isinstance(result, LieBracket)

    def test_lie_bracket_eval(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        result = lie_bracket(a, b).eval()
        expected = (_gp(e1, e2) - _gp(e2, e1)) * 0.5
        assert np.allclose(result.data, expected.data)

    def test_jordan_product_builds_tree(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        result = jordan_product(a, b)
        assert isinstance(result, JordanProduct)

    def test_jordan_product_str(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        assert str(jordan_product(a, b)) == "½{a, b}"

    def test_jordan_product_latex(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        assert r"\tfrac{1}{2}" in jordan_product(a, b).latex()

    def test_jordan_product_eval(self, cl3):
        _, e1, e2, _ = cl3
        a, b = sym(e1, "a"), sym(e2, "b")
        result = jordan_product(a, b).eval()
        expected = (_gp(e1, e2) + _gp(e2, e1)) * 0.5
        assert np.allclose(result.data, expected.data)

    def test_jordan_simplifies_to_inner_for_vectors(self, cl3):
        """jordan_product(v, w) simplifies to hestenes_inner for grade-1 inputs."""
        _, e1, e2, _ = cl3
        a = sym(e1, "a", grade=1)
        b = sym(e2, "b", grade=1)
        result = simplify(jordan_product(a, b))
        assert isinstance(result, Hi)

    def test_jordan_no_simplify_for_bivectors(self, cl3):
        _, e1, e2, e3 = cl3
        B1 = sym(e1 ^ e2, "B₁", grade=2)
        B2 = sym(e2 ^ e3, "B₂", grade=2)
        result = simplify(jordan_product(B1, B2))
        assert isinstance(result, JordanProduct)

    def test_commutator_numeric_fallback(self, cl3):
        _, e1, e2, _ = cl3
        result = commutator(e1, e2)
        assert not isinstance(result, Expr)

    def test_lie_bracket_numeric_fallback(self, cl3):
        _, e1, e2, _ = cl3
        result = lie_bracket(e1, e2)
        assert not isinstance(result, Expr)

    def test_jordan_product_numeric_fallback(self, cl3):
        _, e1, e2, _ = cl3
        result = jordan_product(e1, e2)
        assert not isinstance(result, Expr)
