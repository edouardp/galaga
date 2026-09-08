"""Public inner-product contracts with frozen v1 dispatcher evidence.

The mode dispatcher stays retired. Independent Gram minors check scalar
pairings; grade-filtered reference left actions check the four contractions.
"""

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
import galaga.core as core

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/inner-products-v1.json").read_text())
OPERATIONS = (
    "doran_lasenby_inner",
    "hestenes_inner",
    "left_contraction",
    "right_contraction",
    "scalar_product",
    "metric_inner_product",
)
GRAMS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    ((2, 0.5, -0.25), (0.5, -1, 0.75), (-0.25, 0.75, 3)),
    ((1, 1, 0), (1, 1, 0), (0, 0, 0)),
)
SPELLINGS = {
    "doran_lasenby_inner": ("a | b", "a · b", r"a \cdot b"),
    "hestenes_inner": ("hestenes_inner(a, b)", "hestenes_inner(a, b)", r"a \cdot b"),
    "left_contraction": ("a _| b", "a ⌋ b", r"a \mathbin{\rfloor} b"),
    "right_contraction": ("a |_ b", "a ⌊ b", r"a \mathbin{\lfloor} b"),
    "scalar_product": ("a * b", "a * b", "a * b"),
    "metric_inner_product": (
        "metric_inner_product(a, b)",
        "metric_inner_product(a, b)",
        r"\operatorname{metric\_inner\_product}(a,\, b)",
    ),
}
TARGETS = ("ascii", "unicode", "latex")


@lru_cache
def oracle_tensor(operation, gram):
    """Use minors for pairings, never either scalar-product implementation."""
    metric = np.array(gram)
    n, dim = len(gram), 1 << len(gram)
    indices = [tuple(index for index in range(n) if mask & (1 << index)) for mask in range(dim)]
    grades = np.array([len(index) for index in indices])
    tensor = np.zeros((dim, dim, dim))
    if operation in {"scalar_product", "metric_inner_product"}:
        for i, rows in enumerate(indices):
            for j, cols in enumerate(indices):
                if len(rows) == len(cols):
                    sign = (-1) ** (len(rows) * (len(rows) - 1) // 2) if operation == "scalar_product" else 1
                    tensor[0, i, j] = sign * np.linalg.det(metric[np.ix_(rows, cols)])
    else:
        reference = core.Algebra(gram=gram, product_backend="reference")
        for i, r in enumerate(grades):
            action = reference.left_action(reference.blade(i))
            for j, s in enumerate(grades):
                if operation == "doran_lasenby_inner":
                    grade = abs(r - s)
                elif operation == "hestenes_inner":
                    grade = abs(r - s) if r and s else -1
                elif operation == "left_contraction":
                    grade = s - r
                else:
                    assert operation == "right_contraction"
                    grade = r - s
                tensor[:, i, j] = np.where(grades == grade, action[:, j], 0)
    tensor.flags.writeable = False
    return tensor


def expected_coefficients(operation, gram, left, right):
    return np.einsum("i,kij,j->k", left, oracle_tensor(operation, gram), right)


def assert_coefficients(actual, expected):
    expected = np.asarray(expected)
    assert expected.shape == actual.data.shape
    assert np.isfinite(expected).all()
    np.testing.assert_allclose(actual.data, expected, rtol=0, atol=1e-12)


@pytest.fixture
def cl3():
    return ga.Algebra(3)


class TestIpFunction:
    """Historical method IDs now specify the explicit v2 replacement."""

    def test_ip_default_is_doran_lasenby(self, cl3):
        e1 = cl3.blade(1)
        assert (2 + e1) | e1 == 1 + 2 * e1
        assert ga.doran_lasenby_inner(2 + e1, e1) == 1 + 2 * e1

    def test_ip_hestenes(self, cl3):
        e1 = cl3.blade(1)
        assert ga.hestenes_inner(2 + e1, 3 + e1) == 1

    def test_ip_left(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        assert ga.left_contraction(e1, e1 ^ e2) == e2

    def test_ip_right(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        assert ga.right_contraction(e1 ^ e2, e1) == -e2

    def test_ip_scalar(self, cl3):
        B = cl3.blade(3)
        assert ga.scalar_product(2 + B, 3 + B) == 5
        assert ga.metric_inner_product(2 + B, 3 + B) == 7

    def test_ip_bad_mode(self, cl3):
        with pytest.raises(AttributeError, match="does not select an ambiguous inner product"):
            _ = ga.ip


class TestSymbolicIp:
    def test_ip_hestenes(self, cl3):
        # The original misleadingly named test called the Doran-Lasenby default.
        a, b = (2 + cl3.blade(1)).named("a"), (3 + cl3.blade(1)).named("b")
        result = ga.hestenes_inner(a, b)
        assert result == 1
        assert result.expr == ga.Call("hestenes_inner", (ga.Symbol("a"), ga.Symbol("b")))
        assert ga.evaluate(result.expr, algebra=cl3, environment={"a": a, "b": b}) == result

    def test_ip_left(self, cl3):
        a, b = cl3.blade(1).named("a"), cl3.blade(3).named("b")
        result = ga.left_contraction(a, b)
        assert result == cl3.blade(2)
        assert result.display("expr/unicode") == "a ⌋ b"

    def test_ip_right(self, cl3):
        a, b = cl3.blade(3).named("a"), cl3.blade(1).named("b")
        result = ga.right_contraction(a, b)
        assert result == -cl3.blade(2)
        assert result.display("expr/latex") == r"a \mathbin{\lfloor} b"

    def test_ip_scalar(self, cl3):
        a, b = cl3.blade(3).named("a"), cl3.blade(3).named("b")
        result = ga.scalar_product(a, b)
        assert result == -1
        assert result.expr.operation_id == "scalar_product"
        assert result.display("expr/latex") == "a * b"

    def test_ip_bad_mode(self, cl3):
        a = cl3.blade(1).named("a")
        with pytest.raises(TypeError, match="mode"):
            ga.hestenes_inner(a, a, mode="bogus")

    def test_ip_numeric_fallback(self, cl3):
        result = ga.doran_lasenby_inner(cl3.blade(1), cl3.blade(1))
        assert type(result) is ga.Multivector and result == 1
        assert result.expr is None

    def test_ip_numeric_modes(self, cl3):
        a, b = cl3.multivector([2, 1, -2, 3, 1, -1, 2, -2]), cl3.multivector([-1, 3, 1, -2, 2, 1, -1, 3])
        for operation in OPERATIONS:
            result = getattr(ga, operation)(a, b)
            assert_coefficients(result, expected_coefficients(operation, GRAMS[0], a.data, b.data))
            assert result.expr is None


@pytest.mark.parametrize("case", ARCHIVE["cases"], ids=lambda case: case["id"])
@pytest.mark.parametrize("named", (False, True))
def test_archived_modes_replay_through_explicit_public_operations(case, named):
    algebra = ga.Algebra(signature=case["signature"])
    gram = tuple(map(tuple, algebra.gram))
    a, b = algebra.multivector(case["left"]), algebra.multivector(case["right"])
    if named:
        a, b = a.named("a"), b.named("b")
    for row in case["results"]:
        operation = row["operation"]
        result = getattr(ga, operation)(a, b)
        assert type(result) is ga.Multivector
        assert_coefficients(result, expected_coefficients(operation, gram, a.data, b.data))
        assert_coefficients(result, row["data"])
        assert_coefficients(result, row["symbolic_data"])
        if named:
            assert result.expr == ga.Call(operation, (ga.Symbol("a"), ga.Symbol("b")))
            for target, spelling in zip(TARGETS, SPELLINGS[operation], strict=True):
                assert result.display(content="expr", target=target) == spelling
            assert_coefficients(ga.evaluate(result.expr, algebra=algebra, environment={"a": a, "b": b}), result.data)
        else:
            assert result.expr is None
    default = ga.doran_lasenby_inner(a, b)
    assert_coefficients(default, case["default_data"])
    assert_coefficients(default, case["dorst_data"])
    assert (a | b) == default == ga.dorst_inner(a, b)


@pytest.mark.parametrize("gram", GRAMS, ids=("euclidean", "oblique-indefinite", "degenerate"))
@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("state", ("anonymous", "literal", "named"))
@pytest.mark.parametrize("target", TARGETS)
def test_every_grade_pair_and_mixed_values_match_metric_and_reference_oracles(gram, operation, state, target):
    algebra = ga.Algebra(gram=gram)
    grades = np.array([mask.bit_count() for mask in range(algebra.dim)])
    left, right = np.array([2, 1, -2, 3, 1, -1, 2, -2]), np.array([-1, 3, 1, -2, 2, 1, -1, 3])
    inputs = [(left * (grades == r), right * (grades == s)) for r in range(4) for s in range(4)]
    inputs.append((left, right))
    for lc, rc in inputs:
        a, b = algebra.multivector(lc), algebra.multivector(rc)
        if state == "literal":
            a, b = a.with_expr(), b.with_expr()
        elif state == "named":
            a, b = a.named("a"), b.named("b")
        result = getattr(ga, operation)(a, b)
        expected = expected_coefficients(operation, gram, lc, rc)
        assert_coefficients(result, expected)
        expression, value_hash = result.expr, hash(result)
        with algebra.use_presentation(algebra.presentation.with_notation(ga.Notation.functional())):
            rendered = result.display(content="value", target=target)
            assert type(rendered) is str and rendered
            if state == "anonymous":
                assert expression is None
            else:
                assert expression.operation_id == operation
                assert result.display(content="expr", target=target)
                replay = ga.evaluate(expression, algebra=algebra, environment={"a": a, "b": b})
                assert_coefficients(replay, expected)
                if state == "named":
                    changed = ga.evaluate(expression, algebra=algebra, environment={"a": b, "b": a})
                    assert_coefficients(changed, expected_coefficients(operation, gram, rc, lc))
        assert result.expr is expression and hash(result) == value_hash
        assert_coefficients(result, expected)


@pytest.mark.parametrize("gram", GRAMS)
def test_vector_blade_contractions_follow_coordinate_pairings_and_operand_order(gram):
    algebra = ga.Algebra(gram=gram)
    x, u, v = np.array([2, -1, 1]), np.array([1, 2, -1]), np.array([-1, 1, 3])
    X, U, V = map(algebra.vector, (x, u, v))
    B = U ^ V
    left = (x @ algebra.gram @ u) * v - (x @ algebra.gram @ v) * u
    right = (v @ algebra.gram @ x) * u - (u @ algebra.gram @ x) * v
    np.testing.assert_allclose(ga.left_contraction(X, B).vector_part, left, rtol=0, atol=1e-12)
    np.testing.assert_allclose(ga.right_contraction(B, X).vector_part, right, rtol=0, atol=1e-12)
    assert ga.left_contraction(B, X) == ga.right_contraction(X, B) == 0
    np.testing.assert_allclose(left, -right, rtol=0, atol=1e-12)
    restricted = np.column_stack((u, v)).T @ algebra.gram @ np.column_stack((u, v))
    volume_pair = np.linalg.det(restricted)
    assert_coefficients(ga.metric_inner_product(B, B), [volume_pair, 0, 0, 0, 0, 0, 0, 0])
    assert_coefficients(ga.scalar_product(B, B), [-volume_pair, 0, 0, 0, 0, 0, 0, 0])


@pytest.mark.parametrize("namespace", (ga, ga.facade, core), ids=lambda module: module.__name__)
@pytest.mark.parametrize("name", ("ip", "inner_product"))
def test_ambiguous_dispatchers_are_absent_from_public_namespaces(namespace, name):
    assert name not in namespace.__all__
    with pytest.raises(AttributeError):
        getattr(namespace, name)


@pytest.mark.parametrize("operation", OPERATIONS)
def test_named_functions_reject_mode_flags_foreign_algebras_and_bare_expression_operands(operation):
    function = getattr(ga, operation)
    algebra = ga.Algebra(2)
    a = algebra.blade(1).named("a")
    with pytest.raises(TypeError, match="mode"):
        function(a, a, mode="left")
    with pytest.raises(ValueError, match="different algebras"):
        function(a, ga.Algebra(2).blade(1))
    with pytest.raises(TypeError):
        function(a, ga.Symbol("b"))


def test_pipe_and_local_alias_have_one_fixed_meaning_even_for_scalar_inputs():
    from galaga import doran_lasenby_inner as ip

    algebra = ga.Algebra(2)
    v = algebra.blade(1).named("v")
    assert ip is ga.doran_lasenby_inner is ga.dorst_inner
    assert 2 | v == v | 2 == 2 * v
    assert ip(algebra.scalar(2), v) == 2 * v
    assert (2 | v).expr == ga.Call("doran_lasenby_inner", (ga.ScalarLiteral(2), ga.Symbol("v")))
    assert (v | 2).expr == ga.Call("doran_lasenby_inner", (ga.Symbol("v"), ga.ScalarLiteral(2)))
    assert ga.hestenes_inner(algebra.scalar(2), v) == 0
    assert v.__or__("bad") is v.__ror__("bad") is NotImplemented
