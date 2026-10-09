"""Named arithmetic shares numeric values and provenance with Python operators."""

import operator

import numpy as np
import pytest

import galaga as ga

ARITHMETIC = {
    "add": operator.add,
    "subtract": operator.sub,
    "divide": operator.truediv,
    "negate": operator.neg,
    "power": operator.pow,
    "scalar_multiply": operator.mul,
    "scalar_divide": operator.truediv,
}


@pytest.fixture(params=[(2, 0, 0), (1, 1, 0), (0, 0, 2)])
def algebra(request):
    return ga.Algebra(*request.param, user_config_files=False)


@pytest.mark.parametrize("name", ARITHMETIC)
@pytest.mark.parametrize("tracked", [False, True])
def test_named_arithmetic_matches_operators_and_core(algebra, name, tracked):
    e1, e2 = algebra.basis_vectors()
    left, right = 3 + e1, 4 + e2
    if tracked:
        left, right = left.named("A"), right.named("B")
    if name == "negate":
        operands = (left,)
    elif name == "power":
        operands = (left, -2)
    elif name in ("scalar_multiply", "scalar_divide"):
        operands = (left, np.float64(2))
    else:
        operands = (left, right)

    function = getattr(ga, name)
    assert function is getattr(ga.facade, name)
    assert name in ga.__all__
    result = function(*operands)
    expected = ARITHMETIC[name](*operands)
    numeric = tuple(value.numeric if isinstance(value, ga.Multivector) else value for value in operands)
    reference = ARITHMETIC[name](*numeric)
    np.testing.assert_allclose(result.data, reference.data)
    assert result.almost_equal(expected)
    assert result.algebra is algebra
    assert result.expr == expected.expr
    if tracked:
        assert result.expr.operation_id == name
        replayed = ga.evaluate(result.expr, algebra=algebra, environment={"A": left, "B": right})
        assert replayed.almost_equal(result)
        assert result.latex(content="expr") == expected.latex(content="expr")
    else:
        assert result.expr is None


@pytest.mark.parametrize("name", ["add", "subtract", "divide"])
@pytest.mark.parametrize("scalar_first", [False, True])
@pytest.mark.parametrize("tracked", [False, True])
def test_scalar_operands_match_operator_coercion(algebra, name, scalar_first, tracked):
    value = 3 + algebra.basis_vectors()[0]
    if tracked:
        value = value.named("A")
    operands = (2, value) if scalar_first else (value, 2)
    result = getattr(ga, name)(*operands)
    expected = ARITHMETIC[name](*operands)
    assert result.almost_equal(expected)
    assert result.expr == expected.expr
    assert result.algebra is algebra


@pytest.mark.parametrize("name", ["add", "subtract", "divide"])
def test_binary_arithmetic_rejects_foreign_algebras_and_invalid_operands(algebra, name):
    value = algebra.basis_vectors()[0]
    foreign = ga.Algebra(2, user_config_files=False).basis_vectors()[0]
    function = getattr(ga, name)
    with pytest.raises(ValueError, match="different algebras"):
        function(value, foreign)
    for operands in [(value, "x"), ("x", value), (2, 3)]:
        with pytest.raises(TypeError):
            function(*operands)


@pytest.mark.parametrize("name", ["scalar_multiply", "scalar_divide"])
def test_scalar_functions_reject_multivector_scalar_and_invalid_value(algebra, name):
    value = algebra.basis_vectors()[0]
    function = getattr(ga, name)
    with pytest.raises(TypeError):
        function(value, value)
    with pytest.raises(TypeError):
        function(3, 2)


@pytest.mark.parametrize("tracked", [False, True])
def test_division_zero_and_noninvertible_boundaries(tracked):
    algebra = ga.Algebra(0, 0, 2, user_config_files=False)
    null = algebra.basis_vectors()[0]
    value = algebra.identity.named("A") if tracked else algebra.identity
    for divisor in (0, algebra.scalar(0)):
        with pytest.raises(ZeroDivisionError):
            ga.divide(value, divisor)
    with pytest.raises(ZeroDivisionError):
        ga.scalar_divide(value, 0)
    with pytest.raises(ValueError, match="invertible"):
        ga.divide(value, null)


def test_division_uses_right_inverse_and_preserves_tiny_scalar_division():
    algebra = ga.Algebra(2, user_config_files=False)
    e1, e2 = algebra.basis_vectors()
    left, right = 3 + e1, 4 + e2
    quotient = ga.divide(left, right)
    assert quotient.almost_equal(left * ga.inverse(right))
    assert (quotient * right).almost_equal(left)
    assert not quotient.almost_equal(ga.inverse(right) * left)
    tiny = algebra.scalar(1e-320)
    assert ga.divide(tiny, tiny) == algebra.identity


@pytest.mark.parametrize("exponent", [0, 2, -2, np.int64(3)])
def test_integer_power_matches_operator(algebra, exponent):
    value = (3 + algebra.basis_vectors()[0]).named("A")
    result = ga.power(value, exponent)
    assert result.almost_equal(value**exponent)
    assert result.expr == (value**exponent).expr


@pytest.mark.parametrize("exponent", [True, np.bool_(True), "2", 1j, 1.5])
def test_general_metric_power_rejects_unsupported_exponents(exponent):
    value = ga.Algebra(2, user_config_files=False).identity
    with pytest.raises(TypeError):
        ga.power(value, exponent)


def test_exterior_real_power_and_square_root():
    algebra = ga.Algebra(0, 0, 3, user_config_files=False)
    e1, e2, e3 = algebra.basis_vectors()
    value = (4 + e1 + (e2 ^ e3)).named("A")
    root = ga.power(value, 0.5)
    assert (root * root).almost_equal(value)
    assert root.almost_equal(ga.sqrt(value))
    for exponent in [1.5, -1 / 3, np.float64(2.5)]:
        result = ga.power(value, exponent)
        assert result.almost_equal(value**exponent)
        assert result.expr == (value**exponent).expr
    for invalid in [-algebra.identity, e1]:
        with pytest.raises(ValueError):
            ga.power(invalid, 0.5)


@pytest.mark.parametrize("name, operands", [("negate", (2,)), ("power", (2, 3))])
def test_unary_arithmetic_requires_multivector(name, operands):
    with pytest.raises(TypeError):
        getattr(ga, name)(*operands)
