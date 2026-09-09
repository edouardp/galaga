"""Public logarithm/generator separation includes rendering and replay."""

import numpy as np
import pytest

import galaga as ga
import galaga.core as core
import galaga.facade as facade


@pytest.mark.parametrize("operation", ("log", "rotor_generator", "is_rotor_generator"))
def test_core_facade_and_top_level_expose_one_canonical_operation(operation):
    assert getattr(ga, operation) is getattr(facade, operation)
    assert operation in ga.__all__ and operation in core.__all__
    assert ga.get_operation(operation).evaluate is getattr(core, operation)


@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("atol", (1e-12, 1e-10))
def test_algebra_log_and_rotor_generator_are_independent_operations(expr, atol):
    algebra = ga.Algebra(6)
    volume = algebra.pseudoscalar(expr=expr)
    value = (1 + volume) / np.sqrt(2)
    logarithm = ga.log(value, atol=atol)
    np.testing.assert_allclose(logarithm.data, (np.pi / 4 * volume).data, rtol=0, atol=1e-12)
    assert (logarithm.expr is not None) == expr
    assert not ga.is_rotor_generator(logarithm, atol=atol)
    with pytest.raises(ValueError, match="normalized rotor"):
        ga.rotor_generator(value, atol=atol)


@pytest.mark.parametrize("operation", ("log", "rotor_generator"))
@pytest.mark.parametrize("atol", (1e-12, 1e-10))
def test_named_logarithms_and_generators_have_distinct_replayable_expressions(operation, atol):
    algebra = ga.Algebra(4)
    first, second = algebra.blade(3), algebra.blade(12)
    generator = 0.2 * first + 0.3 * second
    rotor = ga.exp(generator).named("R").with_expr()
    result = getattr(ga, operation)(rotor, atol=atol)
    parameters = {} if atol == 1e-12 else {"atol": atol}
    assert result.expr == ga.Call(operation, (ga.Symbol("R"),), parameters)
    data_before, expression_before = result.data.copy(), result.expr
    for target in ("ascii", "unicode", "latex"):
        assert result.display("expr/" + target)
        np.testing.assert_array_equal(result.data, data_before)
        assert result.expr is expression_before
    changed = ga.exp(-0.1 * first + 0.4 * second)
    replayed = ga.evaluate(result.expr, algebra=algebra, environment={"R": changed})
    np.testing.assert_allclose(replayed.data, (-0.1 * first + 0.4 * second).data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(result.data, generator.data, rtol=0, atol=1e-12)


def test_generator_predicate_expression_replays_with_new_bindings():
    algebra = ga.Algebra(6)
    expression = ga.Call("is_rotor_generator", (ga.Symbol("B"),), {"atol": 1e-12})
    assert ga.evaluate(expression, algebra=algebra, environment={"B": algebra.blade(3)})
    assert not ga.evaluate(expression, algebra=algebra, environment={"B": algebra.I})


def test_generator_error_does_not_claim_no_alternative_branch_exists():
    algebra = ga.Algebra(6)
    with pytest.raises(ValueError, match="alternative branch may exist"):
        ga.rotor_generator(algebra.I)
    alternative = np.pi / 2 * (algebra.blade(3) + algebra.blade(12) + algebra.blade(48))
    assert ga.is_rotor_generator(alternative)
    np.testing.assert_allclose(ga.exp(alternative).data, algebra.I.data, rtol=0, atol=1e-12)
