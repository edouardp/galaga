"""Content selection replaces mutable reveal/display helpers without losing scope."""

import numpy as np
import pytest

import galaga as ga

TARGETS = ("ascii", "unicode", "latex")
VALUES = ("e12", "e₁₂", "e_{12}")
EXPRESSIONS = ("e1 ^ e2", "e₁ ∧ e₂", r"e_{1} \wedge e_{2}")
NAMES = ("B", "B", r"\mathbf{B}")


@pytest.mark.parametrize("index, target", tuple(enumerate(TARGETS)))
@pytest.mark.parametrize("named", (False, True))
@pytest.mark.parametrize("tracked", (False, True))
def test_display_content_is_explicit_and_rendering_is_an_immutable_snapshot(index, target, named, tracked):
    algebra = ga.Algebra(3)
    value = algebra.blade(1, expr=tracked) ^ algebra.blade(2, expr=tracked)
    if named:
        value = value.named("B", latex=r"\mathbf{B}")
    before = value.data.copy(), value.name, value.expr, hash(value)
    assert value.display("value/" + target) == VALUES[index]
    assert value.display("name/" + target) == (NAMES[index] if named else VALUES[index])
    assert value.display("expr/" + target) == (EXPRESSIONS[index] if tracked else VALUES[index])
    parts = ([NAMES[index]] if named else []) + ([EXPRESSIONS[index]] if tracked else []) + [VALUES[index]]
    separator = r" \quad = \quad " if target == "latex" else " = "
    full = separator.join(parts)
    assert value.display("full/" + target) == full
    assert value.display(target) == (full if named else VALUES[index])
    assert isinstance(full, str) and not hasattr(full, "latex")
    renamed = value.named("new")
    assert value.display("full/" + target) == full
    assert renamed.display("full/" + target) != full
    np.testing.assert_array_equal(value.data, before[0])
    assert (value.name, value.expr, hash(value)) == before[1:]
    if tracked:
        assert ga.evaluate(value.expr, algebra=algebra) == value


@pytest.mark.parametrize("target", TARGETS)
def test_reveal_is_content_selection_or_unnaming_not_an_evaluation_step(target):
    algebra = ga.Algebra(3)
    a, b, _ = algebra.basis_vectors()
    original = ga.exp(-0.25 * (a ^ b).named("B")).named("R")
    revealed = original.unnamed()
    assert revealed.expr is original.expr and revealed.numeric is original.numeric
    assert revealed.display("expr/" + target) == original.display("expr/" + target)
    assert revealed.display("expr/" + target) != original.display("name/" + target)
    assert original.name == ga.Name("R")
    assert revealed.unnamed() == revealed and revealed.unnamed().expr == revealed.expr
    assert ga.evaluate(revealed.expr, algebra=algebra, environment={"B": a ^ b}) == original


POWER_CASES = (
    ("single", lambda a, b: a, ("a^2", "a²", "a^2")),
    ("add", lambda a, b: a + b, ("(a + b)^2", "(a + b)²", r"\left(a + b\right)^2")),
    ("subtract", lambda a, b: a - b, ("(a - b)^2", "(a - b)²", r"\left(a - b\right)^2")),
    ("product", lambda a, b: a * b, ("(ab)^2", "(ab)²", r"\left(a b\right)^2")),
)


@pytest.mark.parametrize("case, recipe, expected", POWER_CASES, ids=[row[0] for row in POWER_CASES])
@pytest.mark.parametrize("index, target", tuple(enumerate(TARGETS)))
def test_squares_group_the_entire_operand_and_preserve_numeric_scope(case, recipe, expected, index, target):
    algebra = ga.Algebra(gram=((2, 0.5), (0.5, -1)))
    a, b = algebra.basis_vectors()
    value = recipe(a.named("a"), b.named("b"))
    squared = value**2
    reference = ga.core.Algebra(gram=algebra.gram, product_backend="reference")
    expected_data = reference.left_action(reference.multivector(value.data)) @ value.data
    np.testing.assert_allclose(squared.data, expected_data, rtol=2e-15, atol=2e-15)
    assert squared.display("expr/" + target) == expected[index]
    assert squared.expr == ga.Call("power", (value.expr or ga.Symbol("a"),), {"exponent": 2})
    assert ga.evaluate(squared.expr, algebra=algebra, environment={"a": a, "b": b}) == squared
    assert ga.squared(value) == squared


@pytest.mark.parametrize("exponent", (0, 2, 3))
@pytest.mark.parametrize("tracked", (False, True))
def test_powers_use_the_shared_integer_power_contract(exponent, tracked):
    algebra = ga.Algebra(3)
    value = algebra.vector((1, 2, 0), expr=tracked)
    result = value**exponent
    expected = algebra.identity
    for _ in range(exponent):
        expected = expected * value
    assert result == expected
    if tracked:
        assert ga.evaluate(result.expr, algebra=algebra) == expected
        assert result.expr.parameters == (("exponent", exponent),)
    else:
        assert result.expr is None


@pytest.mark.parametrize("left, right", (("a", "b"), ("pi", "ve"), ("a", "pi"), ("e₁", "e₂"), ("â", "b")))
def test_product_spacing_is_not_an_identifier_parser(left, right):
    algebra = ga.Algebra(2)
    a, b = algebra.basis_vectors()
    result = a.named(left) * b.named(right)
    assert result.display("expr/unicode") == left + right
    assert result.expr == ga.Call("geometric_product", (ga.Symbol(left), ga.Symbol(right)))
    assert ga.evaluate(result.expr, algebra=algebra, environment={left: a, right: b}) == a * b
    # Choose a visible separator explicitly when adjacent names could confuse.
    notation = algebra.presentation.notation.with_rule(
        "geometric_product", ga.RenderRule("infix", symbol=ga.Name("*", "·", r"\cdot"), precedence=60)
    )
    assert "·" in result.display("expr/unicode", notation=notation)
    assert result == a * b


def test_legacy_display_controls_are_replaced_by_explicit_policy_and_python_scalar_formatting():
    algebra = ga.Algebra(3)
    a, b, _ = algebra.basis_vectors(expr=True)
    value = (3.14159 * a + 2.71828 * b).named("v")
    presentation = algebra.presentation.with_display(ga.DisplayPolicy(coefficient_precision=3))
    expr = value.expr
    full = value.display("full/latex", presentation=presentation)
    assert "3.14" in full and "2.72" in full
    # Precision applies to numeric literals in expressions too; their stored
    # coefficients and the immutable expression itself remain untouched.
    assert value.display("expr/latex", presentation=presentation) == "3.14 e_{1} + 2.72 e_{2}"
    assert value.expr is expr
    assert ga.evaluate(expr, algebra=algebra) == value
    assert algebra.blade(1).named("e1", latex="e_{1}").display("full/latex") == "e_{1}"
    for kwargs in ({"compact": True}, {"coeff_format": ".3f"}):
        with pytest.raises(TypeError):
            value.display(**kwargs)
    with pytest.raises(ValueError):
        format(value, ".3e")
    tiny = algebra.scalar(1.055e-34)
    assert format(float(tiny), ".3e") == "1.055e-34"
    assert tiny.latex(content="value") == "0"
    visible = algebra.presentation.with_display(ga.DisplayPolicy(zero_tolerance=0))
    assert tiny.display("value/latex", presentation=visible) != "0"
    assert float(tiny) == 1.055e-34 and tiny != 0
