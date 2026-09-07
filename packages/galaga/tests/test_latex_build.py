"""Public expression-to-LaTeX contracts, replacing the v1 three-pass suite.

Historical cases (including retired private Sym flags and mutable scientific
style) are captured in latex-build-contracts-v1.json; ADR-102 records differences.
"""

import numpy as np
import pytest

import galaga as ga
from galaga.expression import Call, ScalarLiteral, Symbol, evaluate
from galaga.rendering import Fraction, Group, Identifier, Literal, Power, Product, Sum, SumTerm
from galaga.rendering.latex import emit

A, B = Symbol("a"), Symbol("b")
THETA = Symbol(ga.Name("theta", "θ", r"\theta"))


def call(operation, *operands, **parameters):
    return Call(operation, operands, parameters)


def fraction(operand, denominator=2):
    return call("scalar_divide", operand, scalar=denominator)


def latex(expression, notation=None):
    presentation = ga.Algebra(3).presentation
    if notation is not None:
        presentation = presentation.with_notation(notation)
    return ga.render(expression, target="latex", presentation=presentation)


@pytest.mark.parametrize(
    "expression, expected",
    (
        (A, "a"),
        (THETA, r"\theta"),
        (ScalarLiteral(3.14), "3.14"),
        (ScalarLiteral(2), "2"),
        (call("add", A, B), "a + b"),
        (call("subtract", A, B), "a - b"),
        (call("negate", A), "-a"),
        (call("negate", call("add", A, B)), r"-\left(a + b\right)"),
        (call("scalar_multiply", A, scalar=3), "3 a"),
        (call("scalar_multiply", A, scalar=-1), "-a"),
        (call("scalar_multiply", A, scalar=1), "a"),
        (fraction(A), r"\frac{a}{2}"),
        (call("geometric_product", A, B), "a b"),
        (call("outer_product", A, B), r"a \wedge b"),
        (call("left_contraction", A, B), r"a \mathbin{\rfloor} b"),
        (call("right_contraction", A, B), r"a \mathbin{\lfloor} b"),
        (call("regressive_product", A, B), r"a \vee b"),
        (call("grade", A, target=1), r"\langle a \rangle_{1}"),
        (call("norm", A), r"\lVert a \rVert"),
        (call("even_grades", A), r"\langle a \rangle_{\text{even}}"),
        (call("odd_grades", A), r"\langle a \rangle_{\text{odd}}"),
        (call("unit", A), r"\widehat{a}"),
        (call("unit", call("add", A, B)), r"\widehat{\left(a + b\right)}"),
        (call("exp", A), "e^{a}"),
        (call("exp", fraction(THETA)), r"e^{\theta/2}"),
        (call("log", A), r"\log\left(a\right)"),
        (call("log", call("exp", A)), r"\log\left(e^{a}\right)"),
        (call("commutator", A, B), r"[a,\, b]"),
        (call("anticommutator", A, B), r"\{a,\, b\}"),
        (call("geometric_product", call("add", A, B), A), r"\left(a + b\right) a"),
        (call("add", call("geometric_product", A, B), A), "a b + a"),
    ),
)
def test_expression_layout(expression, expected):
    assert latex(expression) == expected


@pytest.mark.parametrize(
    "operation, expected",
    (
        ("reverse", r"\widetilde{a}"),
        ("grade_involution", r"\widehat{a}"),
        ("conjugate", r"\overline{a}"),
        ("dual", "a^*"),
        ("undual", "a^{*^{-1}}"),
        ("complement", r"a^{\complement}"),
        ("uncomplement", r"a^{\complement^{-1}}"),
        ("inverse", "a^{-1}"),
        ("squared", "a^2"),
    ),
)
def test_unary_layout(operation, expected):
    assert latex(call(operation, A)) == expected


@pytest.mark.parametrize("operation, command", (("reverse", r"\widetilde"), ("conjugate", r"\overline")))
@pytest.mark.parametrize(
    "operand, body",
    ((A, "a"), (THETA, r"\theta"), (Symbol("AB"), "AB"), (call("add", A, B), "a + b")),
)
def test_accent_policy_is_consistently_wide(operation, command, operand, body):
    assert latex(call(operation, operand)) == command + "{" + body + "}"


@pytest.mark.parametrize(
    "outer, inner, expected",
    (
        ("undual", "dual", r"\left(a^*\right)^{*^{-1}}"),
        ("inverse", "dual", r"\left(a^*\right)^{-1}"),
        ("dual", "inverse", r"\left(a^{-1}\right)^*"),
    ),
)
def test_nested_operation_scripts_keep_semantic_parentheses(outer, inner, expected):
    assert latex(call(outer, call(inner, A))) == expected


@pytest.mark.parametrize(
    "operation, suffix",
    (("dual", "^*"), ("inverse", "^{-1}"), ("squared", "^2"), ("complement", r"^{\complement}")),
)
def test_script_on_exponential_braces_the_existing_power(operation, suffix):
    assert latex(call(operation, call("exp", A))) == "{e^{a}}" + suffix


@pytest.mark.parametrize(
    "kind, symbol, operand, expected",
    (
        ("prefix", r"\tilde", A, r"\tilde a"),
        ("prefix", r"\tilde", call("add", A, B), r"\tilde \left(a + b\right)"),
        ("prefix", "-", A, "-a"),
        ("prefix", r"{\sim}", A, r"{\sim}a"),
        ("superscript", r"\dagger", A, r"a^{\dagger}"),
        ("superscript", r"\dagger", call("add", A, B), r"\left(a + b\right)^{\dagger}"),
        ("superscript", r"\dagger", call("exp", A), r"{e^{a}}^{\dagger}"),
        ("superscript", "R", A, "a^R"),
    ),
)
def test_target_specific_custom_rules(kind, symbol, operand, expected):
    original = ga.Notation.default()
    custom = original.with_rule("reverse", ga.RenderRule(kind, symbol=symbol), target="latex")
    assert latex(call("reverse", operand), custom) == expected
    assert original == ga.Notation.default()


@pytest.mark.parametrize(
    "operation, spelling, expected",
    (
        ("undual", r"B^\star", r"{B^\star}^{*^{-1}}"),
        ("inverse", "x^2", "{x^2}^{-1}"),
        ("dual", r"a \wedge b", r"\left(a \wedge b\right)^*"),
        ("complement", r"a \wedge b", r"\left(a \wedge b\right)^{\complement}"),
        ("dual", "a+b", r"\left(a+b\right)^*"),
        ("dual", "B", "B^*"),
    ),
)
def test_scripted_and_compound_name_layout(operation, spelling, expected):
    symbol = Symbol(ga.Name("X", latex=spelling))
    assert latex(call(operation, symbol)) == expected


@pytest.mark.parametrize(
    "expression, expected",
    (
        (fraction(A), r"\frac{a}{2}"),
        (call("geometric_product", fraction(A), B), r"\left(\frac{a}{2}\right) b"),
        (call("inverse", fraction(A)), r"\left(\frac{a}{2}\right)^{-1}"),
        (call("dual", fraction(A)), r"\left(\frac{a}{2}\right)^*"),
        (call("exp", fraction(A)), "e^{a/2}"),
        (call("exp", fraction(call("geometric_product", A, B))), "e^{a b/2}"),
        (call("exp", call("geometric_product", fraction(A), B)), r"e^{\left(a/2\right) b}"),
        (call("exp", call("geometric_product", A, fraction(B))), r"e^{a \left(b/2\right)}"),
        (call("exp", call("geometric_product", fraction(A), fraction(B, 3))), r"e^{\left(a/2\right) \left(b/3\right)}"),
        (call("exp", fraction(call("negate", A))), "e^{-a/2}"),
        (call("exp", fraction(call("negate", call("geometric_product", A, THETA)))), r"e^{-\left(a \theta\right)/2}"),
        (call("geometric_product", fraction(ScalarLiteral(1)), A), "0.5 a"),
        (call("squared", fraction(ScalarLiteral(1))), "0.5^2"),
        (call("add", fraction(ScalarLiteral(1)), A), "0.5 + a"),
        (call("geometric_product", A, call("inverse", B)), "a b^{-1}"),
    ),
)
def test_fractions_keep_builder_grouping_and_script_slash_disambiguation(expression, expected):
    assert latex(expression) == expected


@pytest.mark.parametrize(
    "tree, expected",
    (
        (Product((Fraction(Literal(1), Literal(2)), Identifier("a"))), r"\frac{1}{2} a"),
        (Sum((SumTerm(Fraction(Literal(1), Literal(2))), SumTerm(Identifier("a")))), r"\frac{1}{2} + a"),
        (Product((Fraction(Literal(1), Literal(2)), Fraction(Literal(1), Literal(3)))), r"\frac{1}{2} \frac{1}{3}"),
        (Power(Group(Fraction(Literal(1), Literal(2))), Literal(2)), r"\left(\frac{1}{2}\right)^2"),
    ),
)
def test_explicit_fraction_layout_is_independent_of_expression_constant_folding(tree, expected):
    assert emit(tree) == expected


@pytest.mark.parametrize(
    "expression, expected",
    (
        (ScalarLiteral(1.2e-7), r"1.2 \times 10^{-7}"),
        (ScalarLiteral(3.14), "3.14"),
        (ScalarLiteral(1e-10), r"10^{-10}"),
        (call("scalar_multiply", A, scalar=5.5e-8), r"5.5 \times 10^{-8} a"),
        (call("scalar_multiply", A, scalar=2.5), "2.5 a"),
        (fraction(A, 1.2e-7), r"\frac{a}{1.2 \times 10^{-7}}"),
    ),
)
def test_scientific_literals_and_coefficients(expression, expected):
    assert latex(expression) == expected


@pytest.mark.parametrize("style", ("cdot", "raw"))
def test_retired_mutable_scientific_selector_is_not_a_v2_option(style):
    with pytest.raises(TypeError, match="scientific"):
        ga.Notation(scientific=style)


@pytest.mark.parametrize("gram", (((1, 0), (0, 1)), ((2, 0.5), (0.5, 1))))
@pytest.mark.parametrize("angle", (0.4, np.pi / 4))
def test_rotor_fraction_display_retains_metric_derived_values_and_replay(gram, angle):
    algebra = ga.Algebra(gram=gram)
    plane = algebra.blade(3)
    # Compute independently before naming: the exterior bivector squares to
    # minus the Gram determinant, even when the native basis is oblique.
    square = -np.linalg.det(gram)
    np.testing.assert_allclose((plane * plane).data, square * algebra.identity.data, atol=1e-14)
    frequency = np.sqrt(-square)
    expected = (
        np.cos(angle * frequency / 2) * algebra.identity.data - np.sin(angle * frequency / 2) / frequency * plane.data
    )
    theta = algebra.scalar(angle).named(ga.Name.from_latex(r"\theta"))
    bivector = plane.named("B")
    rotor = ga.exp((-theta / 2) * bivector)
    expression, data, before_hash = rotor.expr, rotor.data.copy(), hash(rotor)
    np.testing.assert_allclose(data, expected, atol=1e-14)
    assert rotor.display("expr/latex") == r"e^{\left(-\theta/2\right) B}"
    np.testing.assert_allclose(
        evaluate(expression, algebra=algebra, environment={"theta": theta, "B": plane}).data, expected
    )
    assert rotor.expr is expression and hash(rotor) == before_hash
    np.testing.assert_array_equal(rotor.data, data)
    logarithm = ga.log(rotor)
    np.testing.assert_allclose(logarithm.data, -angle / 2 * plane.data, atol=1e-14)
    assert logarithm.expr == call("log", expression)
    assert logarithm.display("expr/latex") == r"\log\left(e^{\left(-\theta/2\right) B}\right)"


def test_complement_is_eager_but_keeps_explicit_provenance():
    algebra = ga.Algebra(3)
    vector = algebra.blade(1).named("v")
    result = ga.complement(vector)
    assert result.expr == call("complement", Symbol("v"))
    np.testing.assert_array_equal((vector ^ result).data, algebra.blade(algebra.dim - 1).data)
    assert result.display("expr/latex") == r"v^{\complement}"
    np.testing.assert_array_equal(evaluate(result.expr, algebra=algebra, environment={"v": vector}).data, result.data)


@pytest.mark.parametrize(
    "name, expected",
    (
        (ga.Name("B"), "B^*"),
        (ga.Name("wedge", latex=r"a \wedge b"), r"\left(a \wedge b\right)^*"),
        (ga.Name("sum", latex="a + b"), r"\left(a + b\right)^*"),
        (ga.Name("star", latex=r"B^\star"), r"{B^\star}^*"),
    ),
)
@pytest.mark.parametrize("tracked", (False, True))
def test_names_do_not_hide_bindings_or_change_the_value_expression(name, expected, tracked):
    algebra = ga.Algebra(gram=((2, 0.5), (0.5, 1)))
    a, b = algebra.blade(1), algebra.blade(2)
    original = a.named("a") ^ b.named("b") if tracked else algebra.blade(3)
    named = original.named(name)
    assert named.numeric is original.numeric and named.expr is original.expr
    assert named.expr == (call("outer_product", A, B) if tracked else None)
    result = ga.dual(named)
    assert result.expr == call("dual", Symbol(name))
    assert result.display("expr/latex") == expected
    with pytest.raises(KeyError):
        evaluate(result.expr, algebra=algebra)
    np.testing.assert_array_equal(
        evaluate(result.expr, algebra=algebra, environment={name.ascii: original}).data, result.data
    )


def test_unbound_compound_names_render_without_numeric_evaluation(monkeypatch):
    def reject(*args, **kwargs):
        raise AssertionError("unexpected evaluation")

    monkeypatch.setattr(ga, "evaluate", reject)
    monkeypatch.setattr(ga, "dual", reject)
    for operation in (ga.evaluate, ga.dual):
        with pytest.raises(AssertionError, match="unexpected evaluation"):
            operation(None)
    expression = call("dual", Symbol(ga.Name("X", latex=r"a \wedge b")))
    assert latex(expression) == r"\left(a \wedge b\right)^*"
