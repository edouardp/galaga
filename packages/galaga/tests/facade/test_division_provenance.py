"""Division preserves both operand histories and recomputes on explicit replay."""

import numpy as np
import pytest

import galaga as ga
from galaga.facade import get_operation


@pytest.mark.parametrize("numerator_tracked", (False, True))
@pytest.mark.parametrize("denominator_tracked", (False, True))
def test_scalar_multivector_division_preserves_both_operand_expressions(numerator_tracked, denominator_tracked):
    algebra = ga.Algebra(2)
    a = algebra.scalar(6, expr=numerator_tracked)
    b = algebra.scalar(3, expr=denominator_tracked)
    quotient = a / b
    assert quotient == 2
    if numerator_tracked or denominator_tracked:
        assert quotient.expr == ga.Call("divide", (ga.ScalarLiteral(6), ga.ScalarLiteral(3)))
        assert ga.evaluate(quotient.expr, algebra=algebra) == 2
    else:
        assert quotient.expr is None


@pytest.mark.parametrize("reflected", (False, True))
def test_named_scalar_denominator_remains_a_rebindable_operand(reflected):
    algebra = ga.Algebra(2)
    a, b = algebra.scalar(6).named("a"), algebra.scalar(3).named("b")
    quotient = 6 / b if reflected else a / b
    left = ga.ScalarLiteral(6) if reflected else ga.Symbol("a")
    assert quotient.expr == ga.Call("divide", (left, ga.Symbol("b")))
    before = quotient.data.copy(), hash(quotient)
    assert ga.evaluate(quotient.expr, algebra=algebra, environment={"a": a, "b": 3}) == 2
    assert ga.evaluate(quotient.expr, algebra=algebra, environment={"a": a, "b": -2}) == -3
    # Scalar status belongs to the current binding, not the recorded operation.
    vector = algebra.blade(1)
    assert ga.evaluate(quotient.expr, algebra=algebra, environment={"a": a, "b": 2 * vector}) == 3 * vector
    np.testing.assert_array_equal(quotient.data, before[0])
    assert hash(quotient) == before[1]
    with pytest.raises(KeyError, match="b"):
        ga.evaluate(quotient.expr, algebra=algebra, environment={"a": a})
    with pytest.raises(ZeroDivisionError):
        ga.evaluate(quotient.expr, algebra=algebra, environment={"a": a, "b": 0})
    with pytest.raises(ValueError, match="different algebra"):
        ga.evaluate(quotient.expr, algebra=algebra, environment={"a": a, "b": ga.Algebra(1).scalar(2)})


def test_division_preserves_an_unnamed_denominator_expression_and_tiny_numeric_values():
    algebra = ga.Algebra(3)
    hbar = algebra.scalar(1.055e-34).named(ga.Name("hbar", "ℏ", r"\hbar"))
    mass = algebra.scalar(9.109e-31).named(ga.Name("m", "m", r"m_e"))
    speed = algebra.scalar(3e8).named("c")
    quotient = hbar / (mass * speed)
    expected = 1.055e-34 / (9.109e-31 * 3e8)
    assert float(quotient) == pytest.approx(expected, rel=2e-15, abs=0)
    assert quotient.expr == ga.Call(
        "divide", (ga.Symbol(hbar.name), ga.Call("geometric_product", (ga.Symbol(mass.name), ga.Symbol(speed.name))))
    )
    assert quotient.latex(content="expr") == r"\frac{\hbar}{m_e c}"
    for target in ("ascii", "unicode", "latex"):
        assert quotient.display("expr/" + target)
    original = ga.evaluate(quotient.expr, algebra=algebra, environment={"hbar": hbar, "m": mass, "c": speed})
    rebound = ga.evaluate(quotient.expr, algebra=algebra, environment={"hbar": hbar, "m": 2 * mass, "c": speed})
    assert float(original) == pytest.approx(expected, rel=2e-15, abs=0)
    assert float(rebound) == pytest.approx(expected / 2, rel=2e-15, abs=0)
    assert float(quotient) == float(original)


@pytest.mark.parametrize("tracked", (False, True))
@pytest.mark.parametrize("reflected", (False, True))
def test_subnormal_scalar_division_remains_finite_on_the_facade_and_on_replay(tracked, reflected):
    algebra = ga.Algebra(2)
    tiny = float(np.nextafter(0.0, 1.0))
    numerator, denominator = algebra.scalar(tiny, expr=tracked), algebra.scalar(tiny, expr=tracked)
    with np.errstate(over="raise", invalid="raise"):
        quotient = tiny / denominator if reflected else numerator / denominator
        assert quotient == 1
        if tracked:
            assert ga.evaluate(quotient.expr, algebra=algebra) == 1


@pytest.mark.parametrize("tracked", (False, True))
def test_near_scalar_denominators_keep_tiny_vector_components_on_the_facade(tracked):
    algebra = ga.Algebra(gram=((2, 0.5), (0.5, -1)))
    epsilon = 5e-13
    denominator = algebra.scalar(1, expr=tracked) + epsilon * algebra.blade(1, expr=tracked)
    result = algebra.scalar(1) / denominator
    expected = np.array([1, -epsilon, 0, 0]) / (1 - 2 * epsilon**2)
    np.testing.assert_allclose(result.data, expected, rtol=2e-15, atol=0)
    if tracked:
        np.testing.assert_allclose(ga.evaluate(result.expr, algebra=algebra).data, expected, rtol=2e-15, atol=0)


def test_catalog_division_has_two_operands_and_noncommutative_right_division_semantics():
    algebra = ga.Algebra(2)
    a, b = algebra.blade(1).named("a"), (1 + algebra.blade(3)).named("b")
    operation = get_operation("divide")
    assert operation.arity == operation.expression_arity == 2 and operation.parameters == ()
    result = a / b
    np.testing.assert_allclose((result * b).data, a.data, rtol=0, atol=2e-15)
    assert not result.almost_equal(ga.inverse(b) * a)
    assert result.latex(content="expr") == r"\frac{a}{b}"
    for target in ("ascii", "unicode"):
        assert result.display("expr/" + target) == "a / b"
    assert result.display("expr/ascii", notation=ga.Notation.functional()) == "divide(a, b)"
    with pytest.raises(ValueError, match="2 operands"):
        ga.Call("divide", (ga.Symbol("a"),))
    with pytest.raises(ValueError, match="parameter"):
        ga.Call("divide", (ga.Symbol("a"), ga.Symbol("b")), {"scalar": 2})


def test_plain_real_division_retains_the_scalar_parameter_contract_and_operator_fallbacks():
    algebra = ga.Algebra(2)
    value = algebra.blade(1).named("a")
    assert (value / 2).expr == ga.Call("scalar_divide", (ga.Symbol("a"),), {"scalar": 2})
    assert value.__truediv__("bad") is NotImplemented
    assert value.__rtruediv__("bad") is NotImplemented
    with pytest.raises(ValueError, match="different algebras"):
        value / ga.Algebra(1).scalar(1)
    with pytest.raises(ZeroDivisionError):
        value / algebra.scalar(0)
    with pytest.raises(ZeroDivisionError):
        1 / algebra.scalar(0)
