"""Computed public replacements for the ten original redesign use cases."""

import runpy
from pathlib import Path

import numpy as np
import pytest

import galaga as ga

STATE = runpy.run_path(str(Path(__file__).parents[1] / "presentation/test_redesign_state_contracts.py"))
ARCHIVE = STATE["ARCHIVE"]
CASES = (
    ("test_use_case_1_plain_numeric", "x", lambda a, b, c: 2 * a + 3 * b),
    ("test_use_case_2_named_symbolic_bivector", "B", lambda a, b, c: (a ^ b).named("B")),
    ("test_use_case_3_reveal_structure", "B", lambda a, b, c: (a ^ b).named("B").unnamed()),
    ("test_use_case_4_evaluate_keep_name", "B", lambda a, b, c: (a ^ b).named("B").without_expr()),
    ("test_use_case_5_rename", "B2", lambda a, b, c: (a ^ b).named("B").named("plane")),
    ("test_use_case_6_lazy_unnamed", "expr", lambda a, b, c: (a + b) ^ c),
    # V1's "R" was a scaled generator, not its exponential. Preserve that fact.
    ("test_use_case_7_rotor_workflow", "concrete", lambda a, b, c: (-0.25 * (a ^ b)) * a * ~(-0.25 * (a ^ b))),
    ("test_use_case_8_basis_basis_blade_rename", "E", lambda a, b, c: a.named("E")),
    ("test_use_case_9_symbolic_shorthand", "B", lambda a, b, c: (a ^ b).with_expr().named("B")),
    (
        "test_use_case_10_evaluate_without_losing_labels",
        "psi",
        lambda a, b, c: (3 * a + 4 * b).named("psi").without_expr(),
    ),
)


@pytest.mark.parametrize("identifier, local, recipe", CASES, ids=[row[0] for row in CASES])
@pytest.mark.parametrize("tracked", (False, True))
def test_ten_archived_workflows_keep_numeric_results_with_explicit_state_choices(identifier, local, recipe, tracked):
    algebra = ga.Algebra(3)
    operands = algebra.basis_vectors(expr=tracked)
    result = recipe(*operands)
    old = STATE["observation"]("TestSpecUseCases." + identifier, local)
    STATE["assert_data"](result.data, STATE["sparse_data"](old))
    before = result.data.copy(), result.name, result.expr, hash(result)
    if result.expr is not None:
        STATE["assert_data"](ga.evaluate(result.expr, algebra=algebra).data, result.data)
    for target in ("ascii", "unicode", "latex"):
        for content in ("value", "full"):
            assert result.display(content + "/" + target)
    STATE["assert_data"](result.data, before[0])
    assert (result.name, result.expr, hash(result)) == before[1:]
    assert all(value.name is None for value in operands)


def test_a_scaled_generator_is_not_the_exponentiated_rotor_in_the_old_spec():
    algebra = ga.Algebra(3)
    a, b, _ = algebra.basis_vectors()
    plane = a ^ b
    assert plane * plane == -1
    generator = -0.25 * plane
    assert not ga.is_rotor(generator)
    assert generator * ~generator == 0.0625
    rotor = ga.exp(generator.named("K"))
    assert ga.is_rotor(rotor)
    expected = np.cos(0.5) * a + np.sin(0.5) * b
    np.testing.assert_allclose(ga.sandwich(rotor, a).data, expected.data, rtol=2e-15, atol=2e-15)
    assert ga.evaluate(rotor.expr, algebra=algebra, environment={"K": generator}) == rotor
    rebound = ga.evaluate(rotor.expr, algebra=algebra, environment={"K": 2 * generator})
    np.testing.assert_allclose(ga.sandwich(rebound, a).data, (np.cos(1) * a + np.sin(1) * b).data, atol=2e-15)


@pytest.mark.parametrize("binding", ("vector", "scaled_plane", "mixed"))
def test_symbolic_rotor_norm_cannot_be_simplified_using_one_old_binding(binding):
    algebra = ga.Algebra(3)
    symbol = ga.Symbol("R")
    expression = ga.Call("geometric_product", (symbol, ga.Call("reverse", (symbol,))))
    reduced = ga.simplify(expression)
    a, b, _ = algebra.basis_vectors()
    assert ga.evaluate(reduced, algebra=algebra, environment={"R": a ^ b}) == 1
    value = {"vector": 3 * a, "scaled_plane": 2 * (a ^ b), "mixed": 1 + a}[binding]
    replay = ga.evaluate(reduced, algebra=algebra, environment={"R": value})
    assert replay == value * ~value and replay != 1


def test_symbolic_shorthand_means_named_values_or_explicit_nodes_not_grade_promises():
    algebra = ga.Algebra(3)
    a, b, _ = algebra.basis_vectors()
    value = (a + b).named("v").with_expr()
    assert isinstance(value, ga.Multivector)
    assert value.expr == ga.Symbol("v")
    assert value.homogeneous_grade() == 1
    rebound = ga.evaluate(value.expr, algebra=algebra, environment={"v": 1 + (a ^ b)})
    assert rebound.homogeneous_grade() is None
    assert rebound == 1 + (a ^ b)
    assert value.unnamed().without_expr() == a + b
    assert not hasattr(ga, "sym") and not hasattr(ga, "Sym")
    with pytest.raises(TypeError):
        ga.Symbol("v", grade=1)


@pytest.mark.parametrize("number", (3, 3.5))
def test_scalar_simplification_requires_an_explicit_context_free_literal(number):
    with pytest.raises(TypeError, match="Expr"):
        ga.simplify(number)
    literal = ga.ScalarLiteral(number)
    assert ga.simplify(literal) == literal
    assert ga.evaluate(literal, algebra=ga.Algebra(1)) == number


@pytest.mark.parametrize(
    "operation, parameters", (("negate", {}), ("grade", {"target": 1}), ("scalar_divide", {"scalar": 2}))
)
def test_private_node_helpers_are_replaced_by_structure_and_rebound_numeric_inspection(operation, parameters):
    algebra = ga.Algebra(3)
    symbol = ga.Symbol("v")
    node = ga.Call(operation, (symbol,), parameters)
    duplicate = ga.Call(operation, [ga.Symbol("v")], parameters)
    assert node == duplicate and hash(node) == hash(duplicate)
    assert node != ga.Call(operation, (ga.Symbol("w"),), parameters) and node != 42
    reduced = ga.simplify(node)
    for value in (algebra.blade(1), algebra.blade(3), 1 + algebra.blade(1)):
        result = ga.evaluate(reduced, algebra=algebra, environment={"v": value})
        expected = {"negate": -value, "grade": value[1], "scalar_divide": value / 2}[operation]
        assert result == expected
        assert result.homogeneous_grade() == expected.homogeneous_grade()
    if parameters:
        key = next(iter(parameters))
        assert node != ga.Call(operation, (symbol,), {key: parameters[key] + 1})
