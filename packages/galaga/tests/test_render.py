"""Public mixed-precedence rendering contracts; historical test IDs retained.

V1 observations and bindings are archived in render-contracts-v1.json.
ADR-103 records intentional v2 spellings and simplification differences.
"""

import pytest

import galaga as ga
from galaga.expression import Call, ScalarLiteral, Symbol


def _unicode(expr, notation=None):
    presentation = ga.Algebra(3).presentation
    if notation is not None:
        presentation = presentation.with_notation(notation)
    return ga.render(expr, target="unicode", presentation=presentation)


def _latex(expr, notation=None):
    presentation = ga.Algebra(3).presentation
    if notation is not None:
        presentation = presentation.with_notation(notation)
    return ga.render(expr, target="latex", presentation=presentation)


@pytest.fixture
def alg():
    return ga.Algebra((1, 1, 1))


@pytest.fixture
def syms():
    return (Symbol("a"), Symbol("b"), Symbol("c"))


class TestAtoms:
    def test_sym(self, syms):
        a, _, _ = syms
        assert _unicode(a) == "a"

    def test_scalar_int(self):
        assert _unicode(ScalarLiteral(3)) == "3"

    def test_scalar_float(self):
        assert _unicode(ScalarLiteral(2.5)) == "2.5"

    def test_scalar_neg(self):
        assert _unicode(ScalarLiteral(-1)) == "-1"


class TestNeg:
    def test_neg_atom(self, syms):
        a, _, _ = syms
        assert _unicode(Call("negate", (a,))) == "-a"

    def test_neg_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("negate", (Call("add", (a, b)),))) == "-(a + b)"

    def test_neg_product(self, syms):
        a, b, _ = syms
        assert _unicode(Call("negate", (Call("geometric_product", (a, b)),))) == "-(ab)"

    def test_double_neg(self, syms):
        a, _, _ = syms
        assert _unicode(Call("negate", (Call("negate", (a,)),))) == "a"


class TestScalarMulDiv:
    def test_scalar_mul(self, syms):
        a, _, _ = syms
        assert _unicode(Call("scalar_multiply", (a,), {"scalar": 3})) == "3a"

    def test_scalar_mul_neg1(self, syms):
        a, _, _ = syms
        assert _unicode(Call("scalar_multiply", (a,), {"scalar": -1})) == "-a"

    def test_scalar_mul_pos1(self, syms):
        a, _, _ = syms
        assert _unicode(Call("scalar_multiply", (a,), {"scalar": 1})) == "a"

    def test_scalar_mul_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("scalar_multiply", (Call("add", (a, b)),), {"scalar": 2})) == "2(a + b)"

    def test_scalar_div(self, syms):
        a, _, _ = syms
        assert _unicode(Call("scalar_divide", (a,), {"scalar": 2})) == "a / 2"

    def test_scalar_div_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("scalar_divide", (Call("add", (a, b)),), {"scalar": 2})) == "(a + b) / 2"


class TestGp:
    def test_two_atoms(self, syms):
        a, b, _ = syms
        assert _unicode(Call("geometric_product", (a, b))) == "ab"

    def test_three_atoms(self, syms):
        a, b, c = syms
        assert _unicode(Call("geometric_product", (Call("geometric_product", (a, b)), c))) == "abc"

    def test_sum_left(self, syms):
        a, b, c = syms
        assert _unicode(Call("geometric_product", (Call("add", (a, b)), c))) == "(a + b)c"

    def test_sum_right(self, syms):
        a, b, c = syms
        assert _unicode(Call("geometric_product", (a, Call("add", (b, c))))) == "a(b + c)"

    def test_sum_both(self, syms):
        a, b, c = syms
        assert _unicode(Call("geometric_product", (Call("add", (a, b)), Call("add", (b, c))))) == "(a + b)(b + c)"

    def test_wedge_in_gp(self, syms):
        a, b, c = syms
        assert _unicode(Call("geometric_product", (Call("outer_product", (a, b)), c))) == "(a ∧ b)c"

    def test_gp_of_wedge_right(self, syms):
        a, b, c = syms
        assert _unicode(Call("geometric_product", (a, Call("outer_product", (b, c))))) == "a(b ∧ c)"


class TestOp:
    def test_two_atoms(self, syms):
        a, b, _ = syms
        assert _unicode(Call("outer_product", (a, b))) == "a ∧ b"

    def test_sum_in_wedge(self, syms):
        a, b, c = syms
        assert _unicode(Call("outer_product", (Call("add", (a, b)), c))) == "(a + b) ∧ c"

    def test_scalar_mul_in_wedge(self, syms):
        a, b, _ = syms
        assert _unicode(Call("outer_product", (Call("scalar_multiply", (a,), {"scalar": 2}), b))) == "(2a) ∧ b"

    def test_scalar_mul_of_wedge(self, syms):
        a, b, _ = syms
        assert _unicode(Call("scalar_multiply", (Call("outer_product", (a, b)),), {"scalar": 2})) == "2a ∧ b"

    def test_associative_left(self, syms):
        a, b, c = syms
        assert _unicode(Call("outer_product", (Call("outer_product", (a, b)), c))) == "a ∧ b ∧ c"

    def test_associative_right(self, syms):
        a, b, c = syms
        assert _unicode(Call("outer_product", (a, Call("outer_product", (b, c))))) == "a ∧ b ∧ c"

    def test_associative_both(self, syms):
        a, b, c = syms
        d = Symbol("d")
        assert (
            _unicode(Call("outer_product", (Call("outer_product", (a, b)), Call("outer_product", (c, d)))))
            == "a ∧ b ∧ c ∧ d"
        )


class TestAddSub:
    def test_add(self, syms):
        a, b, _ = syms
        assert _unicode(Call("add", (a, b))) == "a + b"

    def test_sub(self, syms):
        a, b, _ = syms
        assert _unicode(Call("subtract", (a, b))) == "a - b"

    def test_add_three(self, syms):
        a, b, c = syms
        assert _unicode(Call("add", (Call("add", (a, b)), c))) == "a + b + c"

    def test_sub_of_sum(self, syms):
        a, b, c = syms
        assert _unicode(Call("subtract", (a, Call("add", (b, c))))) == "a - (b + c)"


class TestPostfixUnary:
    def test_reverse_atom(self, syms):
        a, _, _ = syms
        assert _unicode(Call("reverse", (a,))) == "ã"

    def test_reverse_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("reverse", (Call("add", (a, b)),))) == "(a + b)̃"

    def test_reverse_product(self, syms):
        a, b, _ = syms
        assert _unicode(Call("reverse", (Call("geometric_product", (a, b)),))) == "(ab)̃"

    def test_involute_atom(self, syms):
        a, _, _ = syms
        assert _unicode(Call("grade_involution", (a,))) == "â"

    def test_involute_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("grade_involution", (Call("add", (a, b)),))) == "(a + b)̂"

    def test_conjugate_atom(self, syms):
        a, _, _ = syms
        assert _unicode(Call("conjugate", (a,))) == "a̅"

    def test_conjugate_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("conjugate", (Call("add", (a, b)),))) == "(a + b)̅"

    def test_dual_atom(self, syms):
        a, _, _ = syms
        assert _unicode(Call("dual", (a,))) == "a^★"

    def test_dual_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("dual", (Call("add", (a, b)),))) == "(a + b)^★"

    def test_dual_product(self, syms):
        a, b, _ = syms
        assert _unicode(Call("dual", (Call("geometric_product", (a, b)),))) == "(ab)^★"

    def test_undual_atom(self, syms):
        a, _, _ = syms
        assert _unicode(Call("undual", (a,))) == "a^(★⁻¹)"

    def test_inverse_atom(self, syms):
        a, _, _ = syms
        assert _unicode(Call("inverse", (a,))) == "a⁻¹"

    def test_inverse_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("inverse", (Call("add", (a, b)),))) == "(a + b)⁻¹"

    def test_inverse_product(self, syms):
        a, b, _ = syms
        assert _unicode(Call("inverse", (Call("geometric_product", (a, b)),))) == "(ab)⁻¹"

    def test_squared_atom(self, syms):
        a, _, _ = syms
        assert _unicode(Call("squared", (a,))) == "a²"

    def test_squared_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("squared", (Call("add", (a, b)),))) == "(a + b)²"

    def test_squared_product(self, syms):
        a, b, _ = syms
        assert _unicode(Call("squared", (Call("geometric_product", (a, b)),))) == "(ab)²"


class TestBracketOps:
    def test_grade(self, syms):
        a, _, _ = syms
        assert _unicode(Call("grade", (a,), {"target": 1})) == "⟨a⟩₁"

    def test_grade_of_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("grade", (Call("add", (a, b)),), {"target": 2})) == "⟨a + b⟩₂"

    def test_norm(self, syms):
        a, _, _ = syms
        assert _unicode(Call("norm", (a,))) == "‖a‖"

    def test_unit_atom(self, syms):
        a, _, _ = syms
        assert _unicode(Call("unit", (a,))) == "â"

    def test_unit_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("unit", (Call("add", (a, b)),))) == "(a + b)̂"

    def test_exp(self, syms):
        a, _, _ = syms
        assert _unicode(Call("exp", (a,))) == "exp(a)"

    def test_exp_sum(self, syms):
        a, b, _ = syms
        assert _unicode(Call("exp", (Call("add", (a, b)),))) == "exp(a + b)"


class TestInnerProducts:
    def test_left_contraction(self, syms):
        a, b, _ = syms
        assert _unicode(Call("left_contraction", (a, b))) == "a ⌋ b"

    def test_right_contraction(self, syms):
        a, b, _ = syms
        assert _unicode(Call("right_contraction", (a, b))) == "a ⌊ b"

    def test_hestenes(self, syms):
        a, b, _ = syms
        assert _unicode(Call("hestenes_inner", (a, b))) == "hestenes_inner(a, b)"

    def test_doran_lasenby(self, syms):
        a, b, _ = syms
        assert _unicode(Call("doran_lasenby_inner", (a, b))) == "a · b"

    def test_scalar_product(self, syms):
        a, b, _ = syms
        assert _unicode(Call("scalar_product", (a, b))) == "a * b"

    def test_contraction_of_sum(self, syms):
        a, b, c = syms
        assert _unicode(Call("left_contraction", (Call("add", (a, b)), c))) == "(a + b) ⌋ c"


class TestCommutators:
    def test_commutator(self, syms):
        a, b, _ = syms
        assert _unicode(Call("commutator", (a, b))) == "[a, b]"

    def test_anticommutator(self, syms):
        a, b, _ = syms
        assert _unicode(Call("anticommutator", (a, b))) == "{a, b}"

    def test_lie_bracket(self, syms):
        a, b, _ = syms
        assert _unicode(Call("lie_bracket", (a, b))) == "[a, b]"

    def test_jordan_product(self, syms):
        a, b, _ = syms
        assert _unicode(Call("jordan_product", (a, b))) == "{a, b}"


class TestDiv:
    def test_div_atoms(self, syms):
        a, b, _ = syms
        assert _unicode(Call("geometric_product", (a, Call("inverse", (b,))))) == "ab⁻¹"

    def test_div_sum_numerator(self, syms):
        a, b, c = syms
        assert _unicode(Call("geometric_product", (Call("add", (a, b)), Call("inverse", (c,))))) == "(a + b)c⁻¹"

    def test_div_sum_denominator(self, syms):
        a, b, c = syms
        assert _unicode(Call("geometric_product", (a, Call("inverse", (Call("add", (b, c)),))))) == "a(b + c)⁻¹"

    def test_div_product_denominator(self, syms):
        a, b, c = syms
        assert (
            _unicode(Call("geometric_product", (a, Call("inverse", (Call("geometric_product", (b, c)),))))) == "a(bc)⁻¹"
        )


class TestCompositions:
    def test_sandwich(self, syms):
        a, b, _ = syms
        expr = Call("geometric_product", (Call("geometric_product", (a, b)), Call("reverse", (a,))))
        expected = "ab" + "a" + "̃"
        assert _unicode(expr) == expected

    def test_sandwich_named(self, alg):
        R = Symbol("R")
        v = Symbol("v")
        expr = Call("geometric_product", (Call("geometric_product", (R, v)), Call("reverse", (R,))))
        assert _unicode(expr) == "RvR̃"

    def test_reverse_of_sum_in_product(self, syms):
        a, b, c = syms
        expr = Call("geometric_product", (Call("reverse", (Call("add", (a, b)),)), c))
        assert _unicode(expr) == "(a + b)̃c"

    def test_product_times_reverse_sum(self, syms):
        a, b, c = syms
        expr = Call("geometric_product", (c, Call("reverse", (Call("add", (a, b)),))))
        assert _unicode(expr) == "c(a + b)̃"

    def test_sum_sandwich(self, syms):
        a, b, c = syms
        expr = Call(
            "geometric_product",
            (Call("geometric_product", (Call("add", (a, b)), c)), Call("reverse", (Call("add", (a, b)),))),
        )
        assert _unicode(expr) == "(a + b)c(a + b)̃"

    def test_scalar_mul_in_exp(self, syms):
        a, b, _ = syms
        expr = Call(
            "exp", (Call("scalar_divide", (Call("negate", (Call("geometric_product", (a, b)),)),), {"scalar": 2}),)
        )
        assert _unicode(expr) == "exp(-(ab) / 2)"

    def test_grade_of_sandwich(self, syms):
        a, b, _ = syms
        R, v = (a, b)
        expr = Call(
            "grade",
            (Call("geometric_product", (Call("geometric_product", (R, v)), Call("reverse", (R,)))),),
            {"target": 1},
        )
        assert _unicode(expr) == "⟨abã⟩₁"

    def test_nested_reverse(self, syms):
        a, _, _ = syms
        expr = Call("reverse", (Call("reverse", (a,)),))
        s = _unicode(expr)
        assert s == "(ã)̃"

    def test_wedge_plus_scalar_wedge(self, syms):
        a, b, c = syms
        expr = Call(
            "add",
            (Call("outer_product", (a, b)), Call("scalar_multiply", (Call("outer_product", (b, c)),), {"scalar": 2})),
        )
        assert _unicode(expr) == "a ∧ b + 2b ∧ c"

    def test_neg_scalar_mul_in_product(self, syms):
        a, b, _ = syms
        expr = Call("geometric_product", (Call("scalar_multiply", (a,), {"scalar": -1}), b))
        assert _unicode(expr) == "-ab"


class TestLatex:
    def test_sym(self, syms):
        a, _, _ = syms
        assert _latex(a) == "a"

    def test_gp(self, syms):
        a, b, _ = syms
        assert _latex(Call("geometric_product", (a, b))) == "a b"

    def test_wedge(self, syms):
        a, b, _ = syms
        assert _latex(Call("outer_product", (a, b))) == "a \\wedge b"

    def test_add(self, syms):
        a, b, _ = syms
        assert _latex(Call("add", (a, b))) == "a + b"

    def test_reverse(self, syms):
        a, _, _ = syms
        assert _latex(Call("reverse", (a,))) == "\\widetilde{a}"

    def test_reverse_sum(self, syms):
        a, b, _ = syms
        assert _latex(Call("reverse", (Call("add", (a, b)),))) == "\\widetilde{a + b}"

    def test_grade(self, syms):
        a, _, _ = syms
        assert _latex(Call("grade", (a,), {"target": 1})) == "\\langle a \\rangle_{1}"

    def test_scalar_div(self, syms):
        a, _, _ = syms
        assert _latex(Call("scalar_divide", (a,), {"scalar": 2})) == "\\frac{a}{2}"

    def test_div(self, syms):
        a, b, _ = syms
        assert _latex(Call("geometric_product", (a, Call("inverse", (b,))))) == "a b^{-1}"

    def test_exp(self, syms):
        a, _, _ = syms
        assert _latex(Call("exp", (a,))) == "e^{a}"

    def test_squared(self, syms):
        a, _, _ = syms
        assert _latex(Call("squared", (a,))) == "a^2"

    def test_squared_sum(self, syms):
        a, b, _ = syms
        assert _latex(Call("squared", (Call("add", (a, b)),))) == "\\left(a + b\\right)^2"

    def test_inverse_product(self, syms):
        a, b, _ = syms
        assert _latex(Call("inverse", (Call("geometric_product", (a, b)),))) == "\\left(a b\\right)^{-1}"

    def test_sandwich_latex(self, alg):
        R = Symbol("R")
        v = Symbol("v")
        expr = Call("geometric_product", (Call("geometric_product", (R, v)), Call("reverse", (R,))))
        assert _latex(expr) == "R v \\widetilde{R}"


class TestMixedInfixPostfix:
    def test_reverse_in_gp_left(self, syms):
        a, b, _ = syms
        expr = Call("geometric_product", (Call("reverse", (a,)), b))
        assert _unicode(expr) == "ãb"

    def test_reverse_in_gp_right(self, syms):
        a, b, _ = syms
        expr = Call("geometric_product", (a, Call("reverse", (b,))))
        assert _unicode(expr) == "ab̃"

    def test_reverse_of_gp(self, syms):
        a, b, _ = syms
        expr = Call("reverse", (Call("geometric_product", (a, b)),))
        assert _unicode(expr) == "(ab)̃"

    def test_inverse_in_gp(self, syms):
        a, b, _ = syms
        expr = Call("geometric_product", (Call("inverse", (a,)), b))
        assert _unicode(expr) == "a⁻¹b"

    def test_inverse_of_gp(self, syms):
        a, b, _ = syms
        expr = Call("inverse", (Call("geometric_product", (a, b)),))
        assert _unicode(expr) == "(ab)⁻¹"

    def test_squared_in_gp(self, syms):
        a, b, _ = syms
        expr = Call("geometric_product", (Call("squared", (a,)), b))
        assert _unicode(expr) == "a²b"

    def test_squared_of_gp(self, syms):
        a, b, _ = syms
        expr = Call("squared", (Call("geometric_product", (a, b)),))
        assert _unicode(expr) == "(ab)²"

    def test_dual_in_wedge(self, syms):
        a, b, _ = syms
        expr = Call("outer_product", (Call("dual", (a,)), b))
        assert _unicode(expr) == "a^★ ∧ b"

    def test_dual_of_wedge(self, syms):
        a, b, _ = syms
        expr = Call("dual", (Call("outer_product", (a, b)),))
        assert _unicode(expr) == "(a ∧ b)^★"

    def test_reverse_in_add(self, syms):
        a, b, _ = syms
        expr = Call("add", (Call("reverse", (a,)), b))
        assert _unicode(expr) == "ã + b"

    def test_reverse_of_add(self, syms):
        a, b, _ = syms
        expr = Call("reverse", (Call("add", (a, b)),))
        assert _unicode(expr) == "(a + b)̃"

    def test_neg_of_reverse(self, syms):
        a, _, _ = syms
        expr = Call("negate", (Call("reverse", (a,)),))
        assert _unicode(expr) == "-ã"

    def test_reverse_of_neg(self, syms):
        a, _, _ = syms
        expr = Call("reverse", (Call("negate", (a,)),))
        assert _unicode(expr) == "(-a)̃"

    def test_scalar_mul_of_reverse(self, syms):
        a, _, _ = syms
        expr = Call("scalar_multiply", (Call("reverse", (a,)),), {"scalar": 3})
        assert _unicode(expr) == "3ã"

    def test_reverse_of_scalar_mul(self, syms):
        a, _, _ = syms
        expr = Call("reverse", (Call("scalar_multiply", (a,), {"scalar": 3}),))
        assert _unicode(expr) == "(3a)̃"

    def test_inverse_of_sum_in_gp(self, syms):
        a, b, c = syms
        expr = Call("geometric_product", (Call("inverse", (Call("add", (a, b)),)), c))
        assert _unicode(expr) == "(a + b)⁻¹c"

    def test_gp_of_inverse_sum(self, syms):
        a, b, c = syms
        expr = Call("geometric_product", (c, Call("inverse", (Call("add", (a, b)),))))
        assert _unicode(expr) == "c(a + b)⁻¹"

    def test_sandwich_with_reverse(self, alg):
        R = Symbol("R")
        v = Symbol("v")
        expr = Call("geometric_product", (Call("geometric_product", (R, v)), Call("reverse", (R,))))
        assert _unicode(expr) == "RvR̃"

    def test_grade_of_sandwich(self, alg):
        R = Symbol("R")
        v = Symbol("v")
        expr = Call(
            "grade",
            (Call("geometric_product", (Call("geometric_product", (R, v)), Call("reverse", (R,)))),),
            {"target": 1},
        )
        assert _unicode(expr) == "⟨RvR̃⟩₁"

    def test_exp_of_neg_product_div(self, syms):
        a, b, _ = syms
        expr = Call(
            "exp", (Call("scalar_divide", (Call("negate", (Call("geometric_product", (a, b)),)),), {"scalar": 2}),)
        )
        assert _unicode(expr) == "exp(-(ab) / 2)"

    def test_squared_of_sum_in_gp(self, syms):
        a, b, c = syms
        expr = Call("geometric_product", (Call("squared", (Call("add", (a, b)),)), c))
        assert _unicode(expr) == "(a + b)²c"


class TestMixedInfixPostfixLatex:
    def test_reverse_of_gp_latex(self, syms):
        a, b, _ = syms
        expr = Call("reverse", (Call("geometric_product", (a, b)),))
        assert _latex(expr) == "\\widetilde{a b}"

    def test_inverse_of_gp_latex(self, syms):
        a, b, _ = syms
        expr = Call("inverse", (Call("geometric_product", (a, b)),))
        assert _latex(expr) == "\\left(a b\\right)^{-1}"

    def test_sandwich_latex(self, alg):
        R = Symbol("R")
        v = Symbol("v")
        expr = Call("geometric_product", (Call("geometric_product", (R, v)), Call("reverse", (R,))))
        assert _latex(expr) == "R v \\widetilde{R}"

    def test_dual_of_sum_latex(self, syms):
        a, b, _ = syms
        expr = Call("dual", (Call("add", (a, b)),))
        assert _latex(expr) == "\\left(a + b\\right)^*"

    def test_conjugate_of_sum_latex(self, syms):
        a, b, _ = syms
        expr = Call("conjugate", (Call("add", (a, b)),))
        assert _latex(expr) == "\\overline{a + b}"


class TestNotationOverrideRendering:
    def test_prefix_unary_dual(self, alg):
        alg = alg.with_notation(
            alg.presentation.notation.with_rule("dual", ga.RenderRule(kind="prefix", symbol="*"), target="unicode")
        )
        v = Symbol("v")
        assert _unicode(Call("dual", (v,)), alg.presentation.notation) == "*v"

    def test_prefix_unary_dual_latex(self, alg):
        alg = alg.with_notation(
            alg.presentation.notation.with_rule("dual", ga.RenderRule(kind="prefix", symbol="*"), target="latex")
        )
        v = Symbol("v")
        assert _latex(Call("dual", (v,)), alg.presentation.notation) == "*v"

    def test_postfix_reverse_dagger(self, alg):
        alg = alg.with_notation(
            alg.presentation.notation.with_rule("reverse", ga.RenderRule(kind="postfix", symbol="†"), target="unicode")
        )
        v = Symbol("v")
        assert _unicode(Call("reverse", (v,)), alg.presentation.notation) == "v†"

    def test_postfix_reverse_compound(self, alg):
        alg = alg.with_notation(
            alg.presentation.notation.with_rule("reverse", ga.RenderRule(kind="postfix", symbol="†"), target="unicode")
        )
        a, b = (Symbol("a"), Symbol("b"))
        assert _unicode(Call("reverse", (Call("geometric_product", (a, b)),)), alg.presentation.notation) == "(ab)†"

    def test_function_unary_reverse(self, alg):
        alg = alg.with_notation(
            alg.presentation.notation.with_rule(
                "reverse", ga.RenderRule(kind="function", symbol="rev"), target="unicode"
            )
        )
        v = Symbol("v")
        assert _unicode(Call("reverse", (v,)), alg.presentation.notation) == "rev(v)"

    def test_function_binary_wedge(self, alg):
        alg = alg.with_notation(
            alg.presentation.notation.with_rule(
                "outer_product", ga.RenderRule(kind="function", symbol="wedge"), target="unicode"
            )
        )
        a, b = (Symbol("a"), Symbol("b"))
        assert _unicode(Call("outer_product", (a, b)), alg.presentation.notation) == "wedge(a, b)"

    def test_function_binary_latex(self, alg):
        alg = alg.with_notation(
            alg.presentation.notation.with_rule(
                "outer_product", ga.RenderRule(kind="function", symbol="wedge"), target="latex"
            )
        )
        a, b = (Symbol("a"), Symbol("b"))
        result = _latex(Call("outer_product", (a, b)), alg.presentation.notation)
        assert result == "\\operatorname{wedge}\\left(a, b\\right)"

    def test_infix_override(self, alg):
        alg = alg.with_notation(
            alg.presentation.notation.with_rule(
                "outer_product", ga.RenderRule(kind="infix", symbol="AND"), target="unicode"
            )
        )
        a, b = (Symbol("a"), Symbol("b"))
        assert _unicode(Call("outer_product", (a, b)), alg.presentation.notation) == "a AND b"

    def test_hestenes_preset_sandwich(self, alg):
        n = ga.Notation.hestenes()
        R, v = (Symbol("R"), Symbol("v"))
        expr = Call("geometric_product", (Call("geometric_product", (R, v)), Call("reverse", (R,))))
        assert _unicode(expr, n) == "RvR†"

    def test_notation_does_not_leak(self):
        alg1 = ga.Algebra((1, 1, 1))
        alg2 = ga.Algebra((1, 1, 1))
        alg1 = alg1.with_notation(
            alg1.presentation.notation.with_rule("reverse", ga.RenderRule(kind="postfix", symbol="†"), target="unicode")
        )
        v = Symbol("v")
        assert _unicode(Call("reverse", (v,)), alg1.presentation.notation) == "v†"
        assert _unicode(Call("reverse", (v,)), alg2.presentation.notation) != "v†"


class TestRegressive:
    def test_regressive_unicode(self, syms):
        a, b, _ = syms
        assert _unicode(Call("regressive_product", (a, b))) == "a ∨ b"

    def test_regressive_latex(self, syms):
        a, b, _ = syms
        assert _latex(Call("regressive_product", (a, b))) == "a \\vee b"

    def test_regressive_associative(self, syms):
        a, b, c = syms
        assert _unicode(Call("regressive_product", (Call("regressive_product", (a, b)), c))) == "(a ∨ b) ∨ c"

    def test_regressive_sum_needs_parens(self, syms):
        a, b, c = syms
        assert _unicode(Call("regressive_product", (Call("add", (a, b)), c))) == "(a + b) ∨ c"


class TestAddNegativeCoeff:
    def test_add_neg_scalar_mul_unicode(self, syms):
        a, b, _ = syms
        assert _unicode(Call("add", (a, Call("scalar_multiply", (b,), {"scalar": -3})))) == "a - 3b"

    def test_add_neg_one_scalar_mul_unicode(self, syms):
        a, b, _ = syms
        assert _unicode(Call("add", (a, Call("scalar_multiply", (b,), {"scalar": -1})))) == "a - b"

    def test_add_neg_node_unicode(self, syms):
        a, b, _ = syms
        assert _unicode(Call("add", (a, Call("negate", (b,))))) == "a - b"

    def test_add_positive_unchanged(self, syms):
        a, b, _ = syms
        assert _unicode(Call("add", (a, Call("scalar_multiply", (b,), {"scalar": 3})))) == "a + 3b"

    def test_add_neg_scalar_mul_latex(self, syms):
        a, b, _ = syms
        assert _latex(Call("add", (a, Call("scalar_multiply", (b,), {"scalar": -3})))) == "a - 3 b"

    def test_add_neg_one_scalar_mul_latex(self, syms):
        a, b, _ = syms
        assert _latex(Call("add", (a, Call("scalar_multiply", (b,), {"scalar": -1})))) == "a - b"

    def test_add_neg_node_latex(self, syms):
        a, b, _ = syms
        assert _latex(Call("add", (a, Call("negate", (b,))))) == "a - b"
