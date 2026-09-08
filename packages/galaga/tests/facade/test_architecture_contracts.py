"""Live v2 owners of the architectural identities formerly in test_coverage.

The public numeric catalog owns call shapes, not a second symbolic registry.
Import guards scan every lexical scope and work with source and wheel resources.
"""

import ast
import inspect
from dataclasses import replace
from importlib.resources import files
from importlib.util import resolve_name

import numpy as np
import pytest

import galaga as ga
import galaga.core as core
from galaga.facade import EXCLUDED_PUBLIC_NAMES, OPERATIONS, LeftFoldCall, get_operation

STRUCTURAL = {"add", "subtract", "divide", "negate", "scalar_multiply", "scalar_divide", "power"}
PARAMETERS = {
    "scalar": 2,
    "exponent": 3,
    "target": 2,
    "targets": [2, 0],
    "order": 1,
    "atol": 1e-9,
    "rtol": 1e-7,
}


def python_sources(root, package):
    """Read Python resources recursively, including from a zipped wheel."""
    for entry in sorted(root.iterdir(), key=lambda item: item.name):
        if entry.is_dir():
            yield from python_sources(entry, f"{package}.{entry.name}")
        elif entry.name.endswith(".py"):
            module = package if entry.name == "__init__.py" else f"{package}.{entry.name[:-3]}"
            yield module, package, entry.read_text(encoding="utf-8")


def galaga_imports(source, package):
    """Resolve absolute/relative imports at every scope; ignore text mentions."""
    imports = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            module = resolve_name(module, package)
            names = [f"{module}.{alias.name}" for alias in node.names]
        else:
            continue
        imports.extend((node.lineno, name) for name in names if name == "galaga" or name.startswith("galaga."))
    return imports


def assert_core_only_imports(source, package):
    forbidden = [
        (line, name)
        for line, name in galaga_imports(source, package)
        if name != "galaga.core" and not name.startswith("galaga.core.")
    ]
    assert not forbidden, f"{package} imports outside the numeric core: {forbidden}"


def parameter_values(operation, include_optional=True):
    return {
        parameter.name: PARAMETERS[parameter.name]
        for parameter in operation.parameters
        if include_optional or parameter.required
    }


def assert_catalog_complete(operations, excluded):
    public = set(core.__all__)
    assert set(operations).isdisjoint(excluded)
    assert public == (set(operations) & public) | set(excluded)
    assert set(operations) - public == STRUCTURAL
    assert all(excluded.values())
    assert all(key == operation.id for key, operation in operations.items())


class TestArchitecturalInvariants:
    """Retain the seven historical method identities with their v2 owners."""

    def test_ops_never_imports_expr(self):
        source = files("galaga.facade").joinpath("catalog.py").read_text(encoding="utf-8")
        assert_core_only_imports(source, "galaga.facade")

    def test_algebra_never_imports_expr(self):
        sources = list(python_sources(files("galaga.core"), "galaga.core"))
        assert sources
        for _module, package, source in sources:
            assert_core_only_imports(source, package)

    def test_every_ga_op_has_handler(self):
        for name, operation in OPERATIONS.items():
            assert get_operation(name) is operation
            assert callable(operation.evaluate)
            assert callable(operation.call_policy.invoke)
            with pytest.raises(AttributeError):
                operation.arity = 99

    def test_ga_ops_count(self):
        # Completeness follows the API, not the historical number 45.
        assert_catalog_complete(OPERATIONS, EXCLUDED_PUBLIC_NAMES)

    def test_handler_map_covers_ga_ops(self):
        for name in OPERATIONS.keys() - STRUCTURAL:
            assert callable(getattr(ga, name))
            assert getattr(ga, name) is getattr(ga.facade, name)
        assert set(ga.OPERATION_ALIASES).isdisjoint(OPERATIONS)
        for alias, canonical in ga.OPERATION_ALIASES.items():
            assert canonical in OPERATIONS
            assert getattr(ga, alias) is getattr(ga, canonical)

    def test_node_names_match_ga_ops(self):
        for name, operation in OPERATIONS.items():
            operands = tuple(ga.Symbol(f"x{index}") for index in range(operation.expression_arity))
            node = ga.Call(name, operands, parameter_values(operation))
            assert type(node) is ga.Call
            assert node.operation_id == name
            assert node.operands == operands

    def test_node_names_arity_matches_ga_ops(self):
        for operation in OPERATIONS.values():
            assert operation.expression_arity + sum(p.positional for p in operation.parameters) == operation.arity
            if isinstance(operation.call_policy, LeftFoldCall):
                assert operation.arity == operation.expression_arity == 2
                assert not operation.parameters


@pytest.mark.parametrize("operation", OPERATIONS.values(), ids=OPERATIONS.keys())
@pytest.mark.parametrize("include_optional", (False, True), ids=("required", "with-options"))
def test_catalog_binding_and_replay_forward_the_same_operands_and_parameters(operation, include_optional):
    operands = tuple(object() for _ in range(operation.expression_arity))
    supplied = parameter_values(operation, include_optional)
    positional = tuple(supplied[p.name] for p in operation.parameters if p.positional)
    keywords = {p.name: supplied[p.name] for p in operation.parameters if p.name in supplied and not p.positional}
    expected_parameters = operation.normalize_expression_parameters(supplied)
    expected_positional = tuple(dict(expected_parameters)[p.name] for p in operation.parameters if p.positional)
    expected_keywords = {
        p.name: dict(expected_parameters)[p.name]
        for p in operation.parameters
        if p.name in supplied and not p.positional
    }
    # Check the real evaluator's signature before substituting a routing spy.
    inspect.signature(operation.evaluate).bind(*operands, *expected_positional, **expected_keywords)
    bound, normalized = operation.bind_expression_call((*operands, *positional), keywords)
    assert bound == operands and normalized == expected_parameters

    calls = []
    sentinel = object()

    def record(*args, **kwargs):
        calls.append((args, kwargs))
        return sentinel

    routed = replace(operation, evaluate=record)
    assert routed.invoke_expression(bound, normalized) is sentinel
    assert calls == [(operands + expected_positional, expected_keywords)]

    symbols = tuple(ga.Symbol(f"x{index}") for index in range(operation.expression_arity))
    node = ga.Call(operation.id, symbols, supplied)
    assert node.parameters == normalized
    with pytest.raises(ValueError, match="expects"):
        ga.Call(operation.id, symbols[:-1], supplied)
    with pytest.raises(ValueError, match="expects"):
        ga.Call(operation.id, (*symbols, ga.Symbol("extra")), supplied)
    with pytest.raises(ValueError, match="no expression parameter"):
        ga.Call(operation.id, symbols, {**supplied, "unknown": 1})


@pytest.mark.parametrize(
    "operation",
    [op for op in OPERATIONS.values() if any(p.required for p in op.parameters)],
    ids=lambda operation: operation.id,
)
def test_generic_calls_reject_missing_required_parameters(operation):
    operands = (ga.Symbol("x"),) * operation.expression_arity
    with pytest.raises(ValueError, match="requires expression parameter"):
        ga.Call(operation.id, operands)


@pytest.mark.parametrize("gram", (((1, 0), (0, 1)), ((2, 0.5), (0.5, -1)), ((1, 0), (0, 0))))
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_catalog_provenance_replays_gram_derived_values_without_rendering_state(gram, target):
    algebra = ga.Algebra(gram=gram)
    xc, yc = np.array([2, 1]), np.array([-1, 3])
    x, y = algebra.vector(xc).named("x"), algebra.vector(yc).named("y")
    pairing = float(xc @ algebra.gram @ yc)
    area = float(np.linalg.det(np.column_stack((xc, yc))))
    product = x * y
    expected = np.array([pairing, 0, 0, area])
    np.testing.assert_allclose(product.data, expected, rtol=0, atol=1e-12)
    assert product.expr == ga.Call("geometric_product", (ga.Symbol("x"), ga.Symbol("y")))
    projected = ga.grade(product, 2)
    assert projected.expr == ga.Call("grade", (product.expr,), {"target": 2})
    contracted = ga.transwedge(x, y, 1)
    assert contracted.expr == ga.Call("transwedge", (ga.Symbol("x"), ga.Symbol("y")), {"order": 1})
    folded = ga.geometric_product(x, y, x)
    assert folded.expr == ga.Call("geometric_product", (product.expr, ga.Symbol("x")))
    # xyx = 2(x.G.y)x - (x.G.x)y, independently of dispatch/replay.
    folded_coordinates = 2 * pairing * xc - float(xc @ algebra.gram @ xc) * yc
    squared_norm = float(xc @ algebra.gram @ xc)
    norm = ga.norm(x)
    assert norm.expr == ga.Call("norm", (ga.Symbol("x"),))
    assert type(ga.is_vector(x)) is bool
    predicate = ga.Call("is_vector", (ga.Symbol("x"),))
    assert ga.evaluate(predicate, algebra=algebra, environment={"x": x}) is True

    cases = (
        (product, expected),
        (projected, [0, 0, 0, area]),
        (contracted, [pairing, 0, 0, 0]),
        (folded, [0, *folded_coordinates, 0]),
        (norm, [np.sqrt(abs(squared_norm)), 0, 0, 0]),
    )
    for value, coefficients in cases:
        expression, before_hash = value.expr, hash(value)
        np.testing.assert_allclose(value.data, coefficients, rtol=0, atol=1e-12)
        with algebra.use_presentation(algebra.presentation.with_notation(ga.Notation.functional())):
            rendered = value.display(content="expr", target=target)
            assert type(rendered) is str and rendered
            replay = ga.evaluate(expression, algebra=algebra, environment={"x": x, "y": y})
            np.testing.assert_allclose(replay.data, coefficients, rtol=0, atol=1e-12)
        assert value.expr is expression and hash(value) == before_hash

    # Named replay must follow new bindings, not return a cached eager value.
    changed = ga.evaluate(product.expr, algebra=algebra, environment={"x": y, "y": x})
    np.testing.assert_allclose(changed.data, [pairing, 0, 0, -area], rtol=0, atol=1e-12)
    np.testing.assert_allclose(product.data, expected, rtol=0, atol=1e-12)
