"""Public grade inspection and bounded simplification contracts from the mixed v1 suite."""

import json
from functools import lru_cache, partial
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
import galaga.core as core

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/grade-simplification-v1.json").read_text())
GRAMS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    ((2, 0.5, -0.25), (0.5, -1, 0.75), (-0.25, 0.75, 3)),
    ((1, 1, 0), (1, 1, 0), (0, 0, 0)),
)
LEFT = np.array([2, 1, -2, 0.5, 1, 0.25, -0.5, 0.125])
RIGHT = np.array([-0.5, 2, 0.5, -1, -1, 0.75, 0.5, -0.25])
RENAMED = {"gp": "geometric_product", "involute": "grade_involution"}


def call(operation, *operands, **parameters):
    return ga.Call(operation, operands, parameters)


def recipes():
    v, w, B, R = (ga.Symbol(name) for name in ("v", "w", "B", "R"))
    zero, one = ga.ScalarLiteral(0), ga.ScalarLiteral(1)
    neg = partial(call, "negate")
    mul = partial(call, "geometric_product")
    add = partial(call, "add")
    sub = partial(call, "subtract")

    def scale(x, k):
        return call("scalar_multiply", x, scalar=k)

    def select(x, k):
        return call("grade", x, target=k)

    return {
        "double_reverse": call("reverse", call("reverse", v)),
        "double_neg": neg(neg(v)),
        "mul_identity_right": mul(v, one),
        "mul_identity_left": mul(one, v),
        "mul_zero_right": mul(v, zero),
        "mul_zero_left": mul(zero, v),
        "add_zero_right": add(v, zero),
        "add_zero_left": add(zero, v),
        "sub_self": sub(v, v),
        "scalar_mul_zero": scale(v, 0),
        "scalar_mul_one": scale(v, 1),
        "r_times_r_reverse": mul(R, call("reverse", R)),
        "grade_idempotent": select(select(v, 1), 1),
        "nested": add(call("reverse", call("reverse", v)), zero),
        "double_involute": call("grade_involution", call("grade_involution", v)),
        "double_conjugate": call("conjugate", call("conjugate", v)),
        "double_inverse": call("inverse", call("inverse", v)),
        "wedge_self": call("outer_product", v, v),
        "norm_unit": call("norm", call("unit", v)),
        "add_self": add(v, v),
        "sub_neg": sub(v, neg(w)),
        "add_neg_self": add(v, neg(v)),
        "scalar_mul_collapse": scale(scale(v, 2), 3),
        "grade_known_match": select(v, 1),
        "grade_known_mismatch": select(v, 2),
        "even_bivector": call("even_grades", B),
        "odd_bivector": call("odd_grades", B),
        "even_vector": call("even_grades", v),
        "odd_vector": call("odd_grades", v),
        "cascade": sub(v, neg(v)),
    }


RECIPES = recipes()
# Deliberately reviewed v2 reductions, not copied v1 output strings.
REDUCED = {
    "double_neg": ga.Symbol("v"),
    "add_zero_right": ga.Symbol("v"),
    "add_zero_left": ga.Symbol("v"),
    "scalar_mul_zero": ga.ScalarLiteral(0),
    "scalar_mul_one": ga.Symbol("v"),
    "nested": call("reverse", call("reverse", ga.Symbol("v"))),
}


@lru_cache
def metadata(gram):
    reference = core.Algebra(gram=gram, product_backend="reference")
    dim, n = reference.dim, reference.n
    degrees = np.array([mask.bit_count() for mask in range(dim)])
    product = np.stack([reference.left_action(reference.blade(mask)) for mask in range(dim)], axis=1)
    exterior = np.zeros_like(product)
    pairing = np.zeros((dim, dim))
    complement = np.zeros((dim, dim))
    indices = [tuple(i for i in range(n) if mask & (1 << i)) for mask in range(dim)]
    for i, rows in enumerate(indices):
        for j, cols in enumerate(indices):
            if not i & j:
                exterior[i | j, i, j] = (-1) ** sum(r > c for r in rows for c in cols)
            if len(rows) == len(cols):
                pairing[i, j] = np.linalg.det(np.asarray(gram)[np.ix_(rows, cols)])
        complement[(dim - 1) ^ i, i] = exterior[-1, i, (dim - 1) ^ i]
    return product, exterior, pairing, complement, degrees


def oracle(operation, gram, operands, parameters=()):
    product, exterior, pairing, complement, degrees = metadata(gram)
    parameters = dict(parameters)
    a = operands[0]
    scalar = np.zeros(len(a))
    scalar[0] = 1
    if operation == "negate":
        return -a
    if operation == "add":
        return a + operands[1]
    if operation == "subtract":
        return a - operands[1]
    if operation == "scalar_multiply":
        return a * parameters["scalar"]
    if operation == "reverse":
        return (-1.0) ** (degrees * (degrees - 1) // 2) * a
    if operation == "grade_involution":
        return (-1.0) ** degrees * a
    if operation == "conjugate":
        return (-1.0) ** (degrees * (degrees + 1) // 2) * a
    if operation in {"grade", "grades", "even_grades", "odd_grades"}:
        if operation == "grade":
            target = parameters["target"]
            selected = (
                degrees % 2 == 0 if target == "even" else degrees % 2 == 1 if target == "odd" else degrees == target
            )
        elif operation == "grades":
            selected = np.isin(degrees, parameters["targets"])
        else:
            selected = degrees % 2 == (operation == "odd_grades")
        return np.where(selected, a, 0)
    if operation == "complement":
        return complement @ a
    if operation == "regressive_product":
        left, right = (complement @ value for value in operands)
        return complement.T @ np.einsum("i,kij,j->k", left, exterior, right)
    if operation == "dual":
        determinant = np.linalg.det(gram)
        if determinant == 0:
            raise ValueError("singular metric")
        volume = np.zeros(len(a))
        n = len(gram)
        volume[-1] = 1 / ((-1) ** (n * (n - 1) // 2) * determinant)
        return np.einsum("i,kij,j->k", a, product, volume)
    if operation in {"norm", "unit"}:
        magnitude = np.sqrt(abs(float(a @ pairing @ a)))
        if operation == "norm":
            return scalar * magnitude
        if magnitude <= 1e-12:
            raise ValueError("null magnitude")
        return a / magnitude
    if operation == "inverse":
        action = np.einsum("i,kij->kj", a, product)
        try:
            result = np.linalg.solve(action, scalar)
        except np.linalg.LinAlgError as error:
            raise ValueError("singular value") from error
        np.testing.assert_allclose(action @ result, scalar, rtol=0, atol=2e-12)
        return result
    if operation == "outer_product":
        return np.einsum("i,kij,j->k", a, exterior, operands[1])
    if operation == "geometric_product":
        return np.einsum("i,kij,j->k", a, product, operands[1])
    r, s = degrees[:, None], degrees[None, :]
    if operation == "left_contraction":
        selected = degrees[:, None, None] == (s - r)[None, :, :]
    elif operation == "right_contraction":
        selected = degrees[:, None, None] == (r - s)[None, :, :]
    elif operation == "scalar_product":
        selected = degrees[:, None, None] == np.zeros_like(r + s)[None, :, :]
    else:
        assert operation in {"hestenes_inner", "doran_lasenby_inner"}
        selected = degrees[:, None, None] == abs(r - s)[None, :, :]
        if operation == "hestenes_inner":
            selected &= (r > 0) & (s > 0)
    return np.einsum("i,kij,j->k", a, product * selected, operands[1])


def oracle_expression(expression, gram, environment):
    if isinstance(expression, ga.Symbol):
        return environment[expression.identifier]
    if isinstance(expression, ga.ScalarLiteral):
        result = np.zeros(2 ** len(gram))
        result[0] = expression.value
        return result
    assert isinstance(expression, ga.Call)
    return oracle(
        expression.operation_id,
        gram,
        tuple(oracle_expression(x, gram, environment) for x in expression.operands),
        expression.parameters,
    )


def assert_value(value, expected):
    expected = np.asarray(expected)
    assert expected.ndim == 1 and np.isfinite(expected).all()
    assert isinstance(value, ga.Multivector)
    assert value.data.shape == expected.shape
    np.testing.assert_allclose(value.data, expected, rtol=0, atol=2e-12)


def support(data, atol=1e-12):
    occupied = {mask.bit_count() for mask, coefficient in enumerate(data) if abs(coefficient) > atol}
    return next(iter(occupied)) if len(occupied) == 1 else None


def check_grade_case(recipe, table=ARCHIVE["tables"][0]):
    row = next(row for row in table["grades"] if row["id"] == recipe)
    algebra = ga.Algebra(signature=table["signature"])
    operands = tuple(algebra.multivector(x["data"]).named(x["name"]) for x in row["inputs"])
    operation = RENAMED.get(recipe, recipe)
    value = getattr(ga, operation)(*operands)
    gram = tuple(map(tuple, algebra.gram))
    expected = oracle(operation, gram, tuple(x.data for x in operands))
    assert_value(value, expected)
    assert_value(value, row["data"])
    assert value.homogeneous_grade() == support(expected)
    assert value.expr == call(operation, *(ga.Symbol(x.name) for x in operands))
    assert_value(ga.evaluate(value.expr, algebra=algebra, environment={x.name: x for x in operands}), expected)
    return value


def check_simplification(recipe, gram=GRAMS[0], bindings=None):
    algebra = ga.Algebra(gram=gram)
    if bindings is None:
        bindings = ARCHIVE["tables"][0]["bindings"]
    arrays = {key: np.asarray(value) for key, value in bindings.items()}
    environment = {key: algebra.multivector(value) for key, value in arrays.items()}
    expression = RECIPES[recipe]
    before_hash = hash(expression)
    simplified = ga.simplify(expression)
    assert simplified == REDUCED.get(recipe, expression)
    assert ga.simplify(simplified) == simplified
    assert hash(expression) == before_hash and expression == RECIPES[recipe]
    try:
        expected = oracle_expression(expression, gram, arrays)
    except ValueError:
        for node in (expression, simplified):
            with pytest.raises(ValueError):
                ga.evaluate(node, algebra=algebra, environment=environment)
        return
    for node in (expression, simplified):
        value = ga.evaluate(node, algebra=algebra, environment=environment)
        assert_value(value, expected)
        for target in ("ascii", "unicode", "latex"):
            assert ga.render(node, presentation=algebra.presentation, target=target)
        assert_value(value, expected)
    return value


class TestSymbolicGradeEvenOdd:
    def test_sym_grade_even(self):
        check_projection("grade", "even")

    def test_sym_grade_odd(self):
        check_projection("grade", "odd")

    def test_sym_even_grades(self):
        check_projection("even_grades", "even")

    def test_sym_odd_grades(self):
        check_projection("odd_grades", "odd")


def check_projection(operation, target):
    algebra = ga.Algebra(3)
    value = algebra.multivector(LEFT).named("v")
    result = ga.grade(value, target) if operation == "grade" else getattr(ga, operation)(value)
    parameters = {"target": target} if operation == "grade" else {}
    assert result.expr == call(operation, ga.Symbol("v"), **parameters)
    assert_value(result, oracle(operation, GRAMS[0], (LEFT,), parameters))
    expected = (
        (f"<v>[{target}]", f"⟨v⟩_[{target}]", rf"\langle v \rangle_{{{target}}}")
        if operation == "grade"
        else (f"<v>{target}", "⟨v⟩₊" if target == "even" else "⟨v⟩₋", rf"\langle v \rangle_{{\text{{{target}}}}}")
    )
    for language, text in zip(("ascii", "unicode", "latex"), expected, strict=True):
        assert result.display(content="expr", target=language) == text


class TestGradePropagation:
    def test_op_grade(self):
        check_grade_case("outer_product")

    def test_left_contraction_grade(self):
        check_grade_case("left_contraction")

    def test_right_contraction_grade(self):
        check_grade_case("right_contraction")

    def test_doran_lasenby_inner_grade(self):
        check_grade_case("doran_lasenby_inner")

    def test_hestenes_inner_grade(self):
        check_grade_case("hestenes_inner")

    def test_scalar_product_grade(self):
        check_grade_case("scalar_product")

    def test_reverse_grade(self):
        check_grade_case("reverse")

    def test_involute_grade(self):
        check_grade_case("involute")

    def test_conjugate_grade(self):
        check_grade_case("conjugate")

    def test_dual_grade(self):
        check_grade_case("dual")

    def test_complement_grade(self):
        check_grade_case("complement")

    def test_unit_grade(self):
        check_grade_case("unit")

    def test_inverse_grade(self):
        check_grade_case("inverse")

    def test_regressive_product_grade(self):
        check_grade_case("regressive_product")

    def test_gp_no_grade(self):
        # The old comment called this mixed, but e1*e2 is a pure bivector.
        assert check_grade_case("gp").homogeneous_grade() == 2


class TestSimplify:
    def test_double_reverse(self):
        check_simplification("double_reverse")

    def test_double_neg(self):
        check_simplification("double_neg")

    def test_mul_identity_right(self):
        check_simplification("mul_identity_right")

    def test_mul_identity_left(self):
        check_simplification("mul_identity_left")

    def test_mul_zero(self):
        for side in ("left", "right"):
            check_simplification(f"mul_zero_{side}")

    def test_add_zero(self):
        for side in ("left", "right"):
            check_simplification(f"add_zero_{side}")

    def test_sub_self(self):
        check_simplification("sub_self")

    def test_scalar_mul_zero(self):
        check_simplification("scalar_mul_zero")

    def test_scalar_mul_one(self):
        check_simplification("scalar_mul_one")

    def test_r_times_r_reverse(self):
        check_simplification("r_times_r_reverse")

    def test_grade_idempotent(self):
        check_simplification("grade_idempotent")

    def test_nested(self):
        check_simplification("nested")

    def test_double_involute(self):
        check_simplification("double_involute")

    def test_double_conjugate(self):
        check_simplification("double_conjugate")

    def test_double_inverse(self):
        check_simplification("double_inverse")

    def test_wedge_self(self):
        check_simplification("wedge_self")

    def test_norm_unit(self):
        check_simplification("norm_unit")

    def test_add_self(self):
        check_simplification("add_self")

    def test_sub_neg(self):
        check_simplification("sub_neg")

    def test_add_neg_self(self):
        check_simplification("add_neg_self")

    def test_scalar_mul_collapse(self):
        check_simplification("scalar_mul_collapse")

    def test_grade_known_match(self):
        check_simplification("grade_known_match")

    def test_grade_known_mismatch(self):
        check_simplification("grade_known_mismatch")

    def test_even_bivector(self):
        check_simplification("even_bivector")

    def test_odd_bivector(self):
        check_simplification("odd_bivector")

    def test_even_vector(self):
        check_simplification("even_vector")

    def test_odd_vector(self):
        check_simplification("odd_vector")

    def test_cascade(self):
        check_simplification("cascade")

    def test_auto_grade_detection(self):
        algebra = ga.Algebra(3)
        for value, degree in ((algebra.blade(1), 1), (algebra.blade(3), 2), (algebra.scalar(5), 0)):
            for wrapped in (value, value.with_expr(), value.named("x")):
                assert wrapped.homogeneous_grade() == degree
                assert not hasattr(ga.Symbol("x"), "_grade")


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda x: str(x["signature"]))
@pytest.mark.parametrize("index", range(15))
def test_archived_grade_results_have_live_numeric_owners(table, index):
    check_grade_case(table["grades"][index]["id"], table)


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda x: str(x["signature"]))
@pytest.mark.parametrize("index", range(30))
def test_archived_simplified_values_replay_with_explicit_bindings(table, index):
    row = table["simplifications"][index]
    gram = tuple(map(tuple, np.diag(table["signature"])))
    value = check_simplification(row["id"], gram, table["bindings"])
    if "data" in row:
        assert_value(value, row["data"])
    old = row["simplified"]
    if "data" in old:
        assert_value(value, old["data"])
    else:
        expected = np.zeros(8)
        expected[0] = old["scalar"]
        assert_value(value, expected)


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("kind", ("vector", "bivector", "mixed"))
@pytest.mark.parametrize("recipe", RECIPES)
def test_simplification_is_valid_under_new_grades_and_metric_bindings(gram, kind, recipe):
    degrees = np.array([mask.bit_count() for mask in range(8)])
    a, b = LEFT, RIGHT
    if kind != "mixed":
        selected = degrees == (1 if kind == "vector" else 2)
        a, b = np.where(selected, LEFT, 0), np.where(selected, RIGHT, 0)
    check_simplification(recipe, gram, {"v": a, "w": b, "B": b, "R": a})


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("state", ("plain", "literal", "named"))
@pytest.mark.parametrize("row", ARCHIVE["tables"][0]["grades"], ids=lambda x: x["id"])
def test_grade_inspection_uses_computed_values_not_operation_or_symbol_assumptions(gram, state, row):
    algebra = ga.Algebra(gram=gram)
    a, b = algebra.multivector(LEFT), algebra.multivector(RIGHT)
    if state == "literal":
        a, b = a.with_expr(), b.with_expr()
    elif state == "named":
        a, b = a.named("a"), b.named("b")
    operands = (a, b) if len(row["inputs"]) == 2 else (a,)
    operation = RENAMED.get(row["id"], row["id"])
    if operation == "dual" and np.linalg.det(gram) == 0:
        with pytest.raises(ValueError):
            getattr(ga, operation)(*operands)
        with pytest.raises(ValueError):
            oracle(operation, gram, tuple(x.data for x in operands))
        return
    expected = oracle(operation, gram, tuple(x.data for x in operands))
    value = getattr(ga, operation)(*operands)
    assert_value(value, expected)
    assert value.homogeneous_grade() == support(expected)
    if state == "plain":
        assert value.expr is None
    else:
        leaves = tuple(ga.Symbol(x.name) if x.name else x.expr for x in operands)
        assert value.expr == call(operation, *leaves)
        changed = {"a": algebra.blade(1), "b": algebra.blade(2)}
        replay = ga.evaluate(value.expr, algebra=algebra, environment=changed)
        effective = tuple(changed[x.name.ascii].data if x.name else x.data for x in operands)
        assert_value(replay, oracle(operation, gram, effective))
        assert_value(value, expected)


@pytest.mark.parametrize("target", (-1, 0, 1, 2, 3, 4, "even", "odd"))
@pytest.mark.parametrize("gram", GRAMS)
def test_projection_and_grade_inspection_are_separate_even_for_zero_results(gram, target):
    algebra = ga.Algebra(gram=gram)
    x = algebra.multivector(LEFT).named("x")
    expression = call("grade", ga.Symbol("x"), target=target)
    projected = ga.grade(x, target)
    expected = oracle("grade", gram, (LEFT,), {"target": target})
    assert_value(projected, expected)
    assert projected.expr == expression and ga.simplify(expression) == expression
    assert projected.homogeneous_grade() == support(expected)
    assert_value(ga.evaluate(expression, algebra=algebra, environment={"x": x}), expected)
    union = ga.grades(x, [2, 0, 2, -1, 8])
    assert union.expr == call("grades", ga.Symbol("x"), targets=(2, 0, 2, -1, 8))
    assert_value(union, oracle("grades", gram, (LEFT,), {"targets": [0, 2]}))


@pytest.mark.parametrize("coefficient", (1e-13, 1e-12, np.nextafter(1e-12, np.inf), 1e-11))
def test_grade_inspection_tolerance_does_not_change_storage_or_exact_equality(coefficient):
    algebra = ga.Algebra(3)
    value = algebra.scalar(1) + coefficient * algebra.blade(1)
    assert value != 1 and value.data[1] == coefficient
    assert value.homogeneous_grade() == (0 if coefficient <= 1e-12 else None)
    assert value.homogeneous_grade(atol=0) is None
    tiny = coefficient * algebra.blade(1)
    assert tiny != 0 and tiny.homogeneous_grade(atol=0) == 1
    assert algebra.scalar(0).homogeneous_grade() is None


def test_wedge_self_requires_actual_grade_information_not_a_symbol_name():
    case = ARCHIVE["wedge_counterexample"]
    algebra = ga.Algebra(signature=case["signature"])
    B = algebra.multivector(case["operand"]).named("B")
    expression = call("outer_product", ga.Symbol("B"), ga.Symbol("B"))
    simplified = ga.simplify(expression)
    assert simplified == expression
    gram = tuple(map(tuple, algebra.gram))
    expected = oracle("outer_product", gram, (B.data, B.data))
    assert np.count_nonzero(expected) == 1 and expected[-1] != 0
    assert_value(B ^ B, expected)
    assert_value(B ^ B, case["data"])
    assert_value(ga.evaluate(simplified, algebra=algebra, environment={"B": B}), expected)
    assert B.homogeneous_grade() == 2 and (B ^ B).homogeneous_grade() == 4
    assert_value(ga.evaluate(simplified, algebra=algebra, environment={"B": algebra.blade(1)}), np.zeros(16))


def test_homogeneous_bivector_inverse_can_have_more_than_one_grade():
    algebra = ga.Algebra(6)
    B = algebra.blade(3) + 2 * algebra.blade(12) + 4 * algebra.blade(48)
    inverted = ga.inverse(B.named("B"))
    reference = core.Algebra(6, product_backend="reference")
    expected = np.linalg.solve(reference.left_action(reference.multivector(B.data)), reference.identity.data)
    assert_value(inverted, expected)
    assert B.homogeneous_grade() == 2 and inverted.homogeneous_grade() is None
    assert {i.bit_count() for i, c in enumerate(expected) if abs(c) > 1e-12} == {2, 6}
    assert_value(B * inverted, algebra.identity.data)
    assert_value(inverted * B, algebra.identity.data)


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda x: str(x["signature"]))
@pytest.mark.parametrize("index", range(4))
def test_archived_even_odd_projections_preserve_values_not_old_node_types(table, index):
    row = table["projections"][index]
    algebra = ga.Algebra(signature=table["signature"])
    v = algebra.multivector(table["bindings"]["v"]).named("v")
    if row["id"].startswith("grade_"):
        target = row["id"].split("_")[1]
        value = ga.grade(v, target)
        expected = call("grade", ga.Symbol("v"), target=target)
    else:
        value = getattr(ga, row["id"])(v)
        expected = call(row["id"], ga.Symbol("v"))
    assert value.expr == expected
    assert_value(value, row["data"])
    assert_value(ga.evaluate(expected, algebra=algebra, environment={"v": v}), row["data"])


def test_fixed_point_reduction_does_not_need_symbol_values():
    v = ga.Symbol("v")
    expression = call("scalar_multiply", call("add", call("negate", v), ga.ScalarLiteral(0)), scalar=-1)
    assert ga.simplify(expression) == v
    assert ga.simplify(ga.simplify(expression)) == v
    with pytest.raises(TypeError, match="Expr"):
        ga.simplify(ga.Algebra(1).blade(1))
    with pytest.raises(KeyError):
        ga.evaluate(expression, algebra=ga.Algebra(1))
