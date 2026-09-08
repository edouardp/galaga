"""Public expression-helper contracts extracted from the mixed legacy suite."""

import json
from dataclasses import FrozenInstanceError
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
import galaga.core as core

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/expression-helpers-v1.json").read_text())
GRAMS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    ((2, 0.5, -0.25), (0.5, -1, 0.75), (-0.25, 0.75, 3)),
    ((1, 1, 0), (1, 1, 0), (0, 0, 0)),
)
MIXED = np.array([2, 1, -2, 0.5, 1, 0.25, -0.5, 0.125])
KNOWN = {
    "scalar": ga.ScalarLiteral(5),
    "grade": ga.Call("grade", (ga.Symbol("v"),), {"target": 2}),
    "reverse": ga.Call("reverse", (ga.Symbol("v"),)),
    "negate": ga.Call("negate", (ga.Symbol("v"),)),
    "scalar_multiply": ga.Call("scalar_multiply", (ga.Symbol("v"),), {"scalar": 3}),
    "unit": ga.Call("unit", (ga.Symbol("v"),)),
    "add": ga.Call("add", (ga.Symbol("a"), ga.Symbol("b"))),
}


@lru_cache
def metadata(gram):
    reference = core.Algebra(gram=gram, product_backend="reference")
    product = np.stack([reference.left_action(reference.blade(mask)) for mask in range(reference.dim)], axis=1)
    indices = [tuple(i for i in range(reference.n) if mask & (1 << i)) for mask in range(reference.dim)]
    degrees = np.array([len(index) for index in indices])
    pairing = np.zeros((reference.dim, reference.dim))
    for i, rows in enumerate(indices):
        for j, cols in enumerate(indices):
            if len(rows) == len(cols):
                pairing[i, j] = np.linalg.det(np.asarray(gram)[np.ix_(rows, cols)])
    return product, pairing, degrees


def expected(expression, gram, bindings):
    product, pairing, degrees = metadata(gram)
    if isinstance(expression, ga.Symbol):
        return np.array(bindings[expression.identifier], copy=True)
    if isinstance(expression, ga.ScalarLiteral):
        result = np.zeros(2 ** len(gram))
        result[0] = expression.value
        return result
    assert isinstance(expression, ga.Call)
    values = tuple(expected(operand, gram, bindings) for operand in expression.operands)
    a = values[0]
    parameters = dict(expression.parameters)
    operation = expression.operation_id
    if operation == "geometric_product":
        return np.einsum("i,kij,j->k", a, product, values[1])
    if operation == "add":
        return a + values[1]
    if operation == "negate":
        return -a
    if operation == "scalar_multiply":
        return parameters["scalar"] * a
    if operation == "reverse":
        return (-1.0) ** (degrees * (degrees - 1) // 2) * a
    if operation == "grade_involution":
        return (-1.0) ** degrees * a
    if operation == "conjugate":
        return (-1.0) ** (degrees * (degrees + 1) // 2) * a
    if operation == "grade":
        return np.where(degrees == parameters["target"], a, 0)
    if operation in {"even_grades", "odd_grades"}:
        return np.where(degrees % 2 == (operation == "odd_grades"), a, 0)
    if operation == "unit":
        magnitude = np.sqrt(abs(float(a @ pairing @ a)))
        if magnitude <= 1e-12:
            raise ValueError("null magnitude")
        return a / magnitude
    assert operation == "dual"
    determinant = np.linalg.det(gram)
    if determinant == 0:
        raise ValueError("singular pseudoscalar")
    n = len(gram)
    volume = np.zeros(2**n)
    volume[-1] = 1 / ((-1) ** (n * (n - 1) // 2) * determinant)
    return np.einsum("i,kij,j->k", a, product, volume)


def assert_value(value, coefficients):
    coefficients = np.asarray(coefficients)
    assert coefficients.ndim == 1 and np.isfinite(coefficients).all()
    assert isinstance(value, ga.Multivector)
    assert value.data.shape == coefficients.shape
    np.testing.assert_allclose(value.data, coefficients, rtol=0, atol=2e-12)


def assert_equal_nodes(left, right):
    assert left == right and right == left
    assert hash(left) == hash(right)
    assert len({left, right}) == 1
    assert {left: "saved"}[right] == "saved"


def check_known(recipe, gram=GRAMS[0], bindings=None):
    algebra = ga.Algebra(gram=gram)
    if bindings is None:
        bindings = ARCHIVE["tables"][0]["bindings"]
    expression = KNOWN[recipe]
    value = ga.evaluate(
        expression, algebra=algebra, environment={key: algebra.multivector(data) for key, data in bindings.items()}
    )
    coefficients = expected(expression, gram, bindings)
    assert_value(value, coefficients)
    support = {i.bit_count() for i, c in enumerate(coefficients) if abs(c) > 1e-12}
    assert value.homogeneous_grade() == (next(iter(support)) if len(support) == 1 else None)
    assert not hasattr(expression, "_grade")
    return value


def check_pair(operation):
    a, b = ga.Symbol("a"), ga.Symbol("b")
    parameters = {"target": 1} if operation == "grade" else {}
    left = ga.Call(operation, (a,), parameters)
    same = ga.Call(operation, [ga.Symbol(ga.Name("a"))], list(parameters.items()))
    different = ga.Call(operation, (b,), parameters)
    assert_equal_nodes(left, same)
    assert left != different and len({left, different}) == 2
    algebra = ga.Algebra(3)
    bindings = {"a": MIXED, "b": MIXED}
    environment = {key: algebra.multivector(data) for key, data in bindings.items()}
    for node in (left, same, different):
        assert_value(ga.evaluate(node, algebra=algebra, environment=environment), expected(node, GRAMS[0], bindings))
    assert ga.evaluate(left, algebra=algebra, environment=environment) == ga.evaluate(
        different, algebra=algebra, environment=environment
    )
    if operation == "grade":
        changed = ga.Call("grade", (a,), {"target": 2})
        assert changed != left
        assert_value(
            ga.evaluate(changed, algebra=algebra, environment=environment), expected(changed, GRAMS[0], bindings)
        )


class TestCoverageGaps:
    def test_expr_rmul_expr(self):
        algebra = ga.Algebra(3)
        a, b = algebra.vector((1, 2, 3)).named("a"), algebra.vector((-1, 0.5, 1)).named("b")
        value = a.__rmul__(b)
        expression = ga.Call("geometric_product", (ga.Symbol("b"), ga.Symbol("a")))
        assert value.expr == expression and value.display("expr/unicode") == "ba"
        assert_value(value, expected(expression, GRAMS[0], {"a": a.data, "b": b.data}))
        assert value != a * b

    def test_expr_rmul_scalar(self):
        algebra = ga.Algebra(3)
        a = algebra.multivector(MIXED).named("a")
        value = 5 * a
        assert value.expr == ga.Call("scalar_multiply", (ga.Symbol("a"),), {"scalar": 5})
        assert_value(value, 5 * MIXED)
        assert value.display("expr/unicode") == "5a"

    def test_sym_explicit_grade(self):
        algebra = ga.Algebra(3)
        vector = algebra.vector((1, 1, 0))
        with pytest.raises(TypeError, match="grade"):
            ga.Symbol("v", grade=2)
        with pytest.raises(TypeError, match="grade"):
            vector.named("v", grade=2)
        assert vector.named("v").homogeneous_grade() == 1

    def test_scalar_str(self):
        leaf = ga.ScalarLiteral(42)
        assert str(leaf) == repr(leaf) == "ScalarLiteral(value=42.0)"
        algebra = ga.Algebra(3)
        for target in ("ascii", "unicode", "latex"):
            assert ga.render(leaf, presentation=algebra.presentation, target=target) == "42"
        assert ga.evaluate(leaf, algebra=algebra) == 42

    def test_ensure_expr_bad_type(self):
        with pytest.raises(TypeError, match="expression nodes"):
            ga.Call("reverse", ([1, 2, 3],))
        with pytest.raises(TypeError, match="real number"):
            ga.ScalarLiteral([1, 2, 3])

    def test_eq_conjugate(self):
        check_pair("conjugate")

    def test_eq_grade(self):
        check_pair("grade")

    def test_eq_fallback(self):
        check_pair("dual")

    def test_known_grade_scalar(self):
        assert check_known("scalar").homogeneous_grade() == 0

    def test_known_grade_grade_node(self):
        assert check_known("grade").homogeneous_grade() is None

    def test_known_grade_reverse(self):
        check_known("reverse")

    def test_known_grade_neg(self):
        check_known("negate")

    def test_known_grade_scalarmul(self):
        check_known("scalar_multiply")

    def test_known_grade_unit(self):
        check_known("unit")

    def test_known_grade_unknown(self):
        assert check_known("add").homogeneous_grade() == 1

    def test_simplify_odd_known_grade(self):
        algebra = ga.Algebra(3)
        for operation in ("even_grades", "odd_grades"):
            for name, value in (("v", algebra.blade(1)), ("B", algebra.blade(3))):
                node = ga.Call(operation, (ga.Symbol(name),))
                assert ga.simplify(node) == node
                assert_value(
                    ga.evaluate(node, algebra=algebra, environment={name: value}),
                    expected(node, GRAMS[0], {name: value.data}),
                )
                mixed = algebra.multivector(MIXED)
                assert_value(
                    ga.evaluate(node, algebra=algebra, environment={name: mixed}),
                    expected(node, GRAMS[0], {name: MIXED}),
                )

    def test_eq_involute(self):
        check_pair("grade_involution")


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda t: str(t["signature"]))
@pytest.mark.parametrize("index", range(7))
def test_archived_known_grade_observations_retain_numeric_owners(table, index):
    row = table["known_grades"][index]
    gram = tuple(map(tuple, np.diag(table["signature"])))
    value = check_known(row["id"], gram, table["bindings"])
    coefficients = row.get("data")
    if coefficients is None:
        coefficients = np.zeros(8)
        coefficients[0] = row["scalar"]
    assert_value(value, coefficients)


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda t: str(t["signature"]))
@pytest.mark.parametrize("index", range(8))
def test_archived_private_equalities_use_public_structure_and_explicit_replay(table, index):
    row = table["equalities"][index]
    operation, variant = row["id"].split(":")
    left = ga.Call(operation, (ga.Symbol("a"),), {"target": 1} if operation == "grade" else {})
    right = (
        ga.Call("grade", (ga.Symbol("a"),), {"target": int(variant)})
        if operation == "grade"
        else ga.Call(operation, (ga.Symbol("a" if variant == "same" else "b"),))
    )
    assert (left == right) is row["equal"]
    if row["equal"]:
        assert_equal_nodes(left, right)
    algebra = ga.Algebra(signature=table["signature"])
    gram = tuple(map(tuple, algebra.gram))
    bindings = table["equality_bindings"]
    for key, node in (("left", left), ("right", right)):
        value = ga.evaluate(
            node, algebra=algebra, environment={name: algebra.multivector(data) for name, data in bindings.items()}
        )
        assert_value(value, expected(node, gram, bindings))
        assert_value(value, row[key]["data"])


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda t: str(t["signature"]))
@pytest.mark.parametrize("index", range(2))
def test_archived_reflected_products_keep_their_operand_order(table, index):
    algebra = ga.Algebra(signature=table["signature"])
    a, b = (algebra.multivector(table["bindings"][name]).named(name) for name in ("a", "b"))
    row = table["reflected"][index]
    value = a.__rmul__(b) if row["id"] == "geometric_product" else 5 * a
    expression = (
        ga.Call("geometric_product", (ga.Symbol("b"), ga.Symbol("a")))
        if row["id"] == "geometric_product"
        else ga.Call("scalar_multiply", (ga.Symbol("a"),), {"scalar": 5})
    )
    assert value.expr == expression
    assert_value(value, expected(expression, tuple(map(tuple, algebra.gram)), table["bindings"]))
    assert_value(value, row["data"])


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda t: str(t["signature"]))
@pytest.mark.parametrize("index", range(4))
def test_archived_parity_values_survive_without_grade_based_symbol_rewrites(table, index):
    row = table["parity"][index]
    operation, name = row["id"].split(":")
    expression = ga.Call(operation, (ga.Symbol(name),))
    assert ga.simplify(expression) == expression
    algebra = ga.Algebra(signature=table["signature"])
    value = ga.evaluate(expression, algebra=algebra, environment={name: algebra.multivector(table["bindings"][name])})
    for observation in (row["original"], row["simplified"]):
        if "data" in observation:
            assert_value(value, observation["data"])
        else:
            assert value == observation["scalar"]


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("recipe", KNOWN)
@pytest.mark.parametrize("kind", ("vector", "bivector", "mixed"))
def test_known_grade_replacements_inspect_rebound_values_in_general_metrics(gram, recipe, kind):
    degrees = np.array([i.bit_count() for i in range(8)])
    data = MIXED if kind == "mixed" else np.where(degrees == (1 if kind == "vector" else 2), MIXED, 0)
    bindings = {key: data for key in ("v", "a", "b")}
    node = KNOWN[recipe]
    before = hash(node)
    try:
        expected(node, gram, bindings)
    except ValueError:
        with pytest.raises(ValueError):
            check_known(recipe, gram, bindings)
        return
    value = check_known(recipe, gram, bindings)
    assert hash(node) == before
    assert_value(value, expected(node, gram, bindings))


@pytest.mark.parametrize("operation", ("conjugate", "grade_involution", "dual", "grade"))
@pytest.mark.parametrize("gram", GRAMS)
def test_equal_nodes_replay_with_new_bindings_without_becoming_cached_values(operation, gram):
    algebra = ga.Algebra(gram=gram)
    parameters = {"target": 2} if operation == "grade" else {}
    node = ga.Call(operation, (ga.Symbol("a"),), parameters)
    duplicate = ga.Call(operation, [ga.Symbol("a")], parameters.items())
    assert_equal_nodes(node, duplicate)
    changed = MIXED * 2
    if operation == "dual" and np.linalg.det(gram) == 0:
        with pytest.raises(ValueError):
            ga.evaluate(node, algebra=algebra, environment={"a": algebra.multivector(MIXED)})
        with pytest.raises(ValueError):
            expected(node, gram, {"a": MIXED})
        return
    first = ga.evaluate(node, algebra=algebra, environment={"a": algebra.multivector(MIXED)})
    second = ga.evaluate(duplicate, algebra=algebra, environment={"a": algebra.multivector(changed)})
    assert first != second
    assert_value(first, expected(node, gram, {"a": MIXED}))
    assert_value(second, expected(node, gram, {"a": changed}))
    for target in ("ascii", "unicode", "latex"):
        assert ga.render(node, presentation=algebra.presentation, target=target)
    assert_equal_nodes(node, duplicate)


def test_numeric_equality_and_identical_rendering_do_not_imply_equal_histories():
    algebra = ga.Algebra(3)
    vector = algebra.vector((1, 2, -1))
    left = 5 * vector.named("left", latex="x")
    right = 5 * vector.named("right", latex="x")
    assert left == right and hash(left) == hash(right)
    assert {left: "value"}[right] == "value"
    assert left.expr != right.expr and len({left.expr, right.expr}) == 2
    assert left.display("expr/latex") == right.display("expr/latex") == "5 x"
    assert left.display("expr/ascii") != right.display("expr/ascii")
    assert_value(left, 5 * vector.data)


def test_all_name_spellings_participate_in_symbol_identity_not_only_ascii():
    plain = ga.Symbol("a")
    unicode_variant = ga.Symbol(ga.Name("a", "α", "a"))
    latex_variant = ga.Symbol(ga.Name("a", "a", r"\alpha"))
    assert plain != unicode_variant and plain != latex_variant and unicode_variant != latex_variant
    assert len({plain, unicode_variant, latex_variant}) == 3
    algebra = ga.Algebra(1)
    for node in (plain, unicode_variant, latex_variant):
        assert node.identifier == "a"
        assert ga.evaluate(node, algebra=algebra, environment={"a": 2}) == 2
    # Exact semantic Name keys take precedence over the ASCII fallback.
    assert ga.evaluate(unicode_variant, algebra=algebra, environment={"a": 2, unicode_variant.name: 3}) == 3


@pytest.mark.parametrize(
    "pair", ((0.0, -0.0), (1, 1.0), (1.0, np.nextafter(1.0, 2.0)), (0.0, 1e-30), (0.0, np.nextafter(0.0, 1.0)))
)
def test_float_literal_equality_is_exact_and_equal_hashes_support_lookup(pair):
    a, b = pair
    nodes = (
        (ga.ScalarLiteral(a), ga.ScalarLiteral(b)),
        (ga.MultivectorLiteral([a, 0]), ga.MultivectorLiteral([b, -0.0])),
        (
            ga.Call("scalar_multiply", (ga.Symbol("a"),), {"scalar": a}),
            ga.Call("scalar_multiply", (ga.Symbol("a"),), {"scalar": b}),
        ),
    )
    for left, right in nodes:
        assert (left == right) == (float(a) == float(b))
        if float(a) == float(b):
            assert_equal_nodes(left, right)
        else:
            assert len({left, right}) == 2
    algebra = ga.Algebra(1)
    for value in pair:
        leaf = ga.ScalarLiteral(value)
        replay = ga.evaluate(leaf, algebra=algebra)
        assert replay.data[0] == leaf.value == value


@pytest.mark.parametrize("value", (float("inf"), float("-inf"), float("nan"), True, "2", object()))
@pytest.mark.parametrize("kind", ("scalar", "multivector", "parameter"))
def test_invalid_literal_and_parameter_inputs_are_rejected_before_evaluation(value, kind):
    error = ValueError if isinstance(value, float) else TypeError
    with pytest.raises(error):
        if kind == "scalar":
            ga.ScalarLiteral(value)
        elif kind == "multivector":
            ga.MultivectorLiteral([0, value])
        else:
            ga.Call("scalar_multiply", (ga.Symbol("a"),), {"scalar": value})


@pytest.mark.parametrize("input_value", (2**53 + 1, Fraction(1, 10)))
def test_literal_construction_rounds_once_but_numeric_comparison_does_not_round_again(input_value):
    rounded = float(input_value)
    node = ga.ScalarLiteral(input_value)
    assert node.value == rounded
    assert_equal_nodes(node, ga.ScalarLiteral(rounded))
    assert_equal_nodes(ga.MultivectorLiteral([input_value, 0]), ga.MultivectorLiteral([rounded, 0]))
    assert_equal_nodes(
        ga.Call("scalar_multiply", (ga.Symbol("a"),), {"scalar": input_value}),
        ga.Call("scalar_multiply", (ga.Symbol("a"),), {"scalar": rounded}),
    )
    value = ga.evaluate(node, algebra=ga.Algebra(1))
    assert value == rounded
    assert value != input_value


def test_node_construction_snapshots_input_containers_and_parameters():
    coefficients = [1, 2, 3, 4]
    literal = ga.MultivectorLiteral(coefficients)
    operands = [literal]
    targets = [0, 2]
    parameters = {"targets": targets}
    node = ga.Call("grades", operands, parameters)
    duplicate = ga.Call("grades", (ga.MultivectorLiteral((1, 2, 3, 4)),), (("targets", (0, 2)),))
    before = hash(node)
    coefficients[0] = 99
    operands[0] = ga.ScalarLiteral(9)
    targets.append(1)
    parameters["targets"] = [1]
    assert_equal_nodes(node, duplicate)
    assert hash(node) == before
    assert node.operands == (ga.MultivectorLiteral((1, 2, 3, 4)),)
    algebra = ga.Algebra(2)
    assert_value(ga.evaluate(node, algebra=algebra), [1, 0, 0, 4])
    for instance, field, replacement in (
        (ga.Symbol("a"), "name", ga.Name("b")),
        (ga.ScalarLiteral(1), "value", 2),
        (ga.BladeLiteral(1), "mask", 2),
        (literal, "coefficients", (0, 0)),
        (node, "operands", (ga.ScalarLiteral(0),)),
        (node, "parameters", ()),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(instance, field, replacement)


def test_explicit_nodes_retain_context_checks_instead_of_a_private_coercion_helper():
    algebra, foreign = ga.Algebra(2), ga.Algebra(3)
    with pytest.raises(TypeError, match="expression nodes"):
        ga.Call("reverse", (algebra.blade(1),))
    with pytest.raises(ValueError, match="different algebra"):
        ga.evaluate(ga.Symbol("a"), algebra=algebra, environment={"a": foreign.blade(1)})
    with pytest.raises(ValueError, match="coefficient count"):
        ga.evaluate(ga.MultivectorLiteral([1, 0]), algebra=algebra)
    with pytest.raises(ValueError, match="outside algebra"):
        ga.evaluate(ga.BladeLiteral(8), algebra=algebra)
    with pytest.raises(TypeError, match="unsupported expression"):
        ga.evaluate(ga.Expr(), algebra=algebra)
    literal = ga.BladeLiteral(3, -1)
    assert_equal_nodes(literal, ga.BladeLiteral(np.int64(3), np.int64(-1)))
    assert_value(ga.evaluate(literal, algebra=algebra), [0, 0, 0, -1])
