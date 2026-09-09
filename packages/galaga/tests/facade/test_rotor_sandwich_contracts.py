"""Public exponential recipes and sandwich contracts, with complete v1 evidence."""

import json
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
import galaga.core as core

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/rotor-sandwich-v1.json").read_text())
GRAMS = (
    ((1, 0), (0, 1)),
    ((2, 0.5), (0.5, 1)),
    ((2, 0.5), (0.5, -1)),
    ((1, 1), (1, 1)),
)
TARGETS = ("ascii", "unicode", "latex")
RETIRED = ("rotor", "rotor_from_bivector", "rotor_from_plane_angle")


def assert_data(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.ndim == expected.ndim == 1 and actual.shape == expected.shape
    assert np.isfinite(actual).all() and np.isfinite(expected).all()
    np.testing.assert_allclose(actual, expected, rtol=0, atol=3e-12)


def check_value(value, expected, expr, target, environment=None):
    assert_data(value.data, expected)
    expression, value_hash = value.expr, hash(value)
    assert value.display("full/" + target)
    assert_data(value.data, expected)
    assert hash(value) == value_hash and value.expr is expression
    if expr:
        assert_data(ga.evaluate(expression, algebra=value.algebra, environment=environment).data, expected)
    else:
        assert expression is None


def rotation_row(key):
    return next(row for row in ARCHIVE["rotations"] if row["id"] == key)


def domain_row(key):
    return next(row for row in ARCHIVE["domains"] if row["id"] == key)


def matrix_exp(matrix):
    """Independent, unscaled series for the small coordinate oracles here."""
    result, term = np.eye(len(matrix)), np.eye(len(matrix))
    for order in range(1, 80):
        term = term @ matrix / order
        result += term
    return result


@pytest.fixture
def cl3():
    return ga.Algebra(3)


class TestRotorFromPlaneAngle:
    def test_90_degree_rotation(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        rotor = ga.exp(-np.pi / 4 * (e1 ^ e2))
        assert_data(ga.sandwich(rotor, e1).data, e2.data)

    def test_180_degree_rotation(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        rotor = ga.exp(-np.pi / 2 * (e1 ^ e2))
        assert_data(ga.sandwich(rotor, e1).data, (-e1).data)

    def test_zero_rotation(self, cl3):
        rotor = ga.exp(0 * cl3.blade(3))
        assert rotor == 1 and ga.sandwich(rotor, cl3.blade(1)) == cl3.blade(1)

    def test_rotor_is_rotor(self, cl3):
        rotor = ga.exp(-1.23 / 2 * cl3.blade(3))
        assert_data((rotor * ~rotor).data, cl3.identity.data)
        assert ga.is_rotor(rotor)


class TestRotorValidation:
    """Historical rejection names belong to the retired helper, not generic exp."""

    def test_rejects_vector(self, cl3):
        assert not hasattr(cl3, "rotor")
        vector = cl3.blade(1)
        assert vector * vector == 1
        result = ga.exp(-0.25 * vector)
        assert_data(result.data, (np.cosh(0.25) - np.sinh(0.25) * vector).data)
        assert not ga.is_even(result) and not ga.is_rotor(result)

    def test_rejects_trivector(self, cl3):
        assert not hasattr(cl3, "rotor")
        volume = cl3.pseudoscalar()
        assert volume * volume == -1
        result = ga.exp(-0.25 * volume)
        assert_data(result.data, (np.cos(0.25) - np.sin(0.25) * volume).data)
        assert not ga.is_even(result) and not ga.is_rotor(result)

    def test_accepts_bivector(self, cl3):
        assert ga.is_rotor(ga.exp(-0.25 * cl3.blade(3)))

    def test_rejects_scalar(self, cl3):
        assert not hasattr(cl3, "rotor")
        result = ga.exp(cl3.scalar(-0.25))
        assert float(result) == pytest.approx(np.exp(-0.25))
        assert ga.is_even(result) and not ga.is_rotor(result)

    def test_normalizes_non_unit_bivector(self, cl3):
        plane = 3 * cl3.blade(3)
        square = float(plane * plane)
        assert square < 0
        normalized = plane / np.sqrt(-square)
        assert_data(ga.exp(-0.25 * normalized).data, rotation_row("rotor_normalized")["data"])
        # exp itself preserves the generator's magnitude.
        assert not ga.exp(-0.25 * plane).almost_equal(ga.exp(-0.25 * normalized))

    def test_sta_pseudoscalar_u1(self):
        sta = ga.Algebra((1, -1, -1, -1))
        volume = sta.pseudoscalar()
        phase = ga.exp(-0.25 * volume)
        assert volume * volume == -1 and ~volume == volume
        assert ga.is_even(phase) and not ga.is_rotor(phase)
        row = domain_row("sta_phase")["result"]
        assert_data(phase.data, row["data"])
        assert_data((phase * ~phase).data, row["reverse_product"])
        assert not (phase * ~phase).almost_equal(sta.identity)

    def test_scaled_rotor_not_rotor(self, cl3):
        rotor = ga.exp(-0.25 * cl3.blade(3))
        assert_data((2 * rotor * ~(2 * rotor)).data, cl3.scalar(4).data)
        assert not ga.is_rotor(2 * rotor)


class TestSandwich:
    def test_symbolic_sandwich(self, cl3):
        rotor, vector = cl3.blade(3).named("R").with_expr(), cl3.blade(1).named("v").with_expr()
        result = ga.sandwich(rotor, vector)
        assert result.expr == ga.Call("sandwich", (ga.Symbol("R"), ga.Symbol("v")))
        assert result.display("expr/ascii") == "Rv~R"
        assert result.display("expr/unicode") == "RvR̃"
        assert result.display("expr/latex") == r"R v \widetilde{R}"
        assert_data(result.data, (-vector).data)

    def test_symbolic_sandwich_eval(self, cl3):
        rotor = ga.exp(-np.pi / 4 * cl3.blade(3)).named("R").with_expr()
        vector = cl3.blade(1).named("v").with_expr()
        result = ga.sandwich(rotor, vector)
        check_value(result, cl3.blade(2).data, True, "latex", {"R": rotor, "v": vector})
        changed = ga.evaluate(result.expr, algebra=cl3, environment={"R": rotor, "v": cl3.blade(2)})
        assert_data(changed.data, (-cl3.blade(1)).data)
        assert_data(result.data, cl3.blade(2).data)

    def test_symbolic_sw_alias(self, cl3):
        assert ga.sw is ga.sandwich
        rotor, vector = cl3.blade(3).named("R").with_expr(), cl3.blade(1).named("v").with_expr()
        assert ga.sw(rotor, vector).expr == ga.sandwich(rotor, vector).expr
        assert ga.sw(rotor, vector).display("expr/unicode") == "RvR̃"
        assert_data(ga.sw(rotor, vector).data, (-vector).data)


class TestCoverageGaps:
    def test_rotor_from_plane_degrees(self, cl3):
        result = ga.exp(-np.deg2rad(90) / 2 * cl3.blade(3))
        assert_data(result.data, rotation_row("rotor_from_plane_angle_degrees")["data"])

    def test_rotor_from_plane_angle_error(self, cl3):
        # No radians/degrees dispatch remains to validate. Old errors are data.
        assert all(not hasattr(cl3, name) for name in RETIRED)
        assert ga.exp(0 * cl3.blade(3)) == 1
        errors = {row["id"]: row for row in ARCHIVE["errors"]}
        assert errors["missing_angle"]["message"] == "Specify radians= or degrees="
        assert errors["two_angles"]["message"] == "Specify radians= or degrees=, not both"

    def test_rotor_from_plane_angle_positional(self, cl3):
        # Despite its old docstring, v1 DID accept positional radians.
        assert_data(
            rotation_row("rotor_from_plane_angle_positional")["data"],
            rotation_row("rotor_from_plane_angle_quarter")["data"],
        )
        assert_data(ga.exp(-np.pi / 4 * cl3.blade(3)).data, rotation_row("rotor_from_plane_angle_positional")["data"])

    def test_rotor_canonical_name(self, cl3):
        assert not hasattr(cl3, "rotor")
        rotor = ga.exp(-np.pi / 4 * cl3.blade(3))
        assert_data(ga.sandwich(rotor, cl3.blade(1)).data, cl3.blade(2).data)

    def test_rotor_degrees(self, cl3):
        radians = np.deg2rad(90)
        assert radians == np.pi / 2
        assert_data(ga.exp(-radians / 2 * cl3.blade(3)).data, rotation_row("rotor_degrees")["data"])

    def test_rotor_from_bivector_alias(self, cl3):
        assert all(not hasattr(cl3, name) for name in RETIRED)
        result = ga.exp(-0.5 * cl3.blade(3))
        for name in RETIRED:
            assert_data(result.data, rotation_row(name + "_alias")["data"])


@pytest.mark.parametrize("row", ARCHIVE["rotations"], ids=lambda row: row["id"])
@pytest.mark.parametrize("expr", (False, True))
def test_every_archived_rotation_uses_explicit_angle_units_and_normalization(row, expr):
    algebra = ga.Algebra(3)
    e1, e2, _ = algebra.basis_vectors(expr=expr)
    plane = row["scale"] * (e1 ^ e2)
    square = float(plane * plane)
    assert square == -(row["scale"] ** 2)
    unit_plane = plane / np.sqrt(-square)
    theta = row["theta"]
    rotor = ga.exp(-theta / 2 * unit_plane)
    assert_data(rotor.data, (np.cos(theta / 2) - np.sin(theta / 2) * unit_plane).data)
    assert_data(e1.data, row["input"])
    assert row["is_even"] and row["is_rotor"] and ga.is_even(rotor) and ga.is_rotor(rotor)
    assert_data((rotor * ~rotor).data, row["reverse_product"])
    sign = np.sign(row["scale"])
    expected = np.cos(theta) * e1 + sign * np.sin(theta) * e2
    assert_data(expected.data, row["sandwich"])
    for target in TARGETS:
        check_value(rotor, row["data"], expr, target)
        check_value(ga.sandwich(rotor, e1), expected.data, expr, target)


@pytest.mark.parametrize("row", ARCHIVE["sandwiches"], ids=lambda row: row["id"])
@pytest.mark.parametrize("target", TARGETS)
def test_archived_named_sandwiches_replay_with_explicit_bindings(row, target):
    algebra = ga.Algebra(3)
    rotor = algebra.multivector(row["rotor"]).named("R").with_expr()
    vector = algebra.multivector(row["vector"]).named("v").with_expr()
    result = getattr(ga, row["method"])(rotor, vector)
    check_value(result, row["data"], True, target, {"R": rotor, "v": vector})
    assert result.display("expr/unicode") == row["unicode"]
    assert result.display("expr/latex") == row["latex"].replace(r"\tilde", r"\widetilde")


@pytest.mark.parametrize("row", ARCHIVE["domains"], ids=lambda row: row["id"])
def test_legacy_domain_observations_are_evidence_not_rotor_guarantees(row):
    algebra = ga.Algebra(row["signature"])
    plane = algebra.multivector(row["generator"])
    assert_data((plane * plane).data, row["square"])
    assert_data((~plane).data, row["reverse"])
    if row["id"] == "null":
        assert row["error"] == {"type": "ValueError", "message": "Cannot normalize near-zero multivector"}
        result = ga.exp(-row["theta"] / 2 * plane)
        assert_data(result.data, (1 - row["theta"] / 2 * plane).data)
        assert ga.is_rotor(result)
        return
    historical = row["result"]
    old_result = algebra.multivector(historical["data"])
    # Reproduce the old trigonometric recipe without invoking the old engine.
    magnitude = np.sqrt(abs(float(ga.grade(plane * ~plane, 0))))
    assert_data(old_result.data, (np.cos(row["theta"] / 2) - np.sin(row["theta"] / 2) * plane / magnitude).data)
    assert_data((old_result * ~old_result).data, historical["reverse_product"])
    assert_data(ga.sandwich(old_result, algebra.multivector(historical["input"])).data, historical["sandwich"])
    assert ga.is_even(old_result) == historical["is_even"]
    assert ga.is_rotor(old_result) == (row["id"] == "elliptic")
    if row["id"] == "nonsimple":
        # V1 checked only the scalar norm and missed the grade-four defect.
        assert historical["is_rotor"] and not ga.is_rotor(old_result)
        assert np.linalg.norm(ga.grade(old_result * ~old_result, 4).data) > 0.05
    else:
        assert ga.is_rotor(old_result) == historical["is_rotor"]


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("scale", (-3, 0.5, 2))
@pytest.mark.parametrize("expr", (False, True))
def test_metric_and_generator_scale_determine_angle_rapidity_or_null_parameter(gram, scale, expr):
    algebra = ga.Algebra(gram=gram)
    a, b = algebra.basis_vectors(expr=expr)
    plane = scale * (a ^ b)
    square = scale**2 * (gram[0][1] ** 2 - gram[0][0] * gram[1][1])
    assert_data((plane * plane).data, algebra.scalar(square).data)
    parameter = -0.3
    rotor = ga.exp(parameter * plane)
    if square < 0:
        magnitude = np.sqrt(-square)
        expected = np.cos(parameter * magnitude) + np.sin(parameter * magnitude) / magnitude * plane
    elif square > 0:
        magnitude = np.sqrt(square)
        expected = np.cosh(parameter * magnitude) + np.sinh(parameter * magnitude) / magnitude * plane
    else:
        expected = 1 + parameter * plane
    action = 2 * scale * np.array([[gram[0][1], gram[1][1]], [-gram[0][0], -gram[0][1]]])
    matrix = matrix_exp(parameter * action)
    np.testing.assert_allclose(matrix.T @ np.asarray(gram) @ matrix, gram, rtol=0, atol=3e-12)
    assert_data((rotor * ~rotor).data, algebra.identity.data)
    assert ga.is_rotor(rotor)
    assert_data(ga.log(rotor).data, (parameter * plane).data)
    for target in TARGETS:
        check_value(rotor, expected.data, expr, target)
        for index, vector in enumerate((a, b)):
            check_value(ga.sandwich(rotor, vector), algebra.vector(matrix[:, index]).data, expr, target)


@pytest.mark.parametrize("signature", ((1, 1, 1, 1), (1, -1, -1, -1), (1, 1, -1, -1)))
@pytest.mark.parametrize("expr", (False, True))
def test_nonsimple_bivector_exp_keeps_the_grade_four_cross_term(signature, expr):
    algebra = ga.Algebra(signature)
    first, second = algebra.blade(3, expr=expr), algebra.blade(12, expr=expr)
    generator = -0.2 * first - 0.35 * second
    assert first * second == second * first
    assert np.linalg.norm(ga.grade(generator * generator, 4).data) > 0.1
    rotor = ga.exp(generator)
    factored = ga.exp(-0.2 * first) * ga.exp(-0.35 * second)
    assert np.linalg.norm(ga.grade(rotor, 4).data) > 0.05
    reference = core.Algebra(gram=algebra.gram, product_backend="reference")
    exponential_action = matrix_exp(reference.left_action(reference.multivector(generator.data)))
    assert_data(rotor.data, exponential_action[:, 0])
    assert_data((rotor * ~rotor).data, algebra.identity.data)
    assert ga.is_rotor(rotor)
    assert_data(ga.log(rotor).data, generator.data)
    assert_data(ga.rotor_generator(rotor).data, generator.data)
    for target in TARGETS:
        check_value(rotor, factored.data, expr, target)


@pytest.mark.parametrize("expr", (False, True))
def test_sta_phase_is_even_but_reverse_is_not_inverse(expr):
    sta = ga.Algebra((1, -1, -1, -1))
    volume, vector = sta.pseudoscalar(expr=expr), sta.blade(1, expr=expr)
    assert volume * volume == -1 and ~volume == volume
    assert volume * vector == -vector * volume
    phase = ga.exp(-0.25 * volume)
    assert ga.is_even(phase) and not ga.is_rotor(phase)
    assert_data((phase * ~phase).data, ga.exp(-0.5 * volume).data)
    assert_data((phase * ga.inverse(phase)).data, sta.identity.data)
    assert not ga.reverse(phase).almost_equal(ga.inverse(phase))
    # A reverse sandwich fixes vectors here, but not all grades.
    assert_data(ga.sandwich(phase, vector).data, vector.data)
    plane = sta.blade(3, expr=expr)
    assert_data(ga.sandwich(phase, plane).data, (plane * ga.exp(-0.5 * volume)).data)
    conjugated = phase * vector * ga.inverse(phase)
    assert np.linalg.norm(ga.grade(conjugated, 3).data) > 0.4
    for target in TARGETS:
        check_value(conjugated, (vector * ga.exp(0.5 * volume)).data, expr, target)


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("expr", (False, True))
def test_sandwich_preserves_all_input_grades_and_uses_reverse_even_when_scaled(gram, expr):
    algebra = ga.Algebra(gram=gram)
    value = algebra.multivector([0.3, 0.5, -0.7, 1.1], expr=expr)
    rotor = ga.exp(-0.2 * algebra.blade(3, expr=expr))
    scaled = 2 * rotor
    reference = core.Algebra(gram=gram, product_backend="reference")
    left = reference.left_action(reference.multivector(scaled.data))
    grades = np.array([mask.bit_count() for mask in range(algebra.dim)])
    reverse_data = scaled.data * (-1.0) ** (grades * (grades - 1) // 2)
    right = np.column_stack(
        [reference.left_action(reference.blade(mask)) @ reverse_data for mask in range(reference.dim)]
    )
    expected = left @ right @ value.data
    assert not ga.is_rotor(scaled)
    assert_data((scaled * value * ga.inverse(scaled)).data, ga.sandwich(rotor, value).data)
    assert_data(expected, 4 * ga.sandwich(rotor, value).data)
    for target in TARGETS:
        check_value(ga.sandwich(scaled, value), expected, expr, target)
        check_value(ga.sw(scaled, value), expected, expr, target)


@pytest.mark.parametrize("expr", (False, True))
def test_is_rotor_rejects_high_dimensional_unit_even_nonrotor(expr):
    algebra = ga.Algebra(6)
    volume, vector = algebra.pseudoscalar(expr=expr), algebra.blade(1, expr=expr)
    reverse_sign = (-1) ** (algebra.n * (algebra.n - 1) // 2)
    square = reverse_sign * np.linalg.det(algebra.gram)
    assert_data((volume * volume).data, algebra.scalar(square).data)
    assert ~volume == reverse_sign * volume and volume * vector == -vector * volume
    value = ga.exp(-0.25 * volume)
    assert ga.is_even(value)
    assert_data((value * ~value).data, algebra.identity.data)
    result = ga.sandwich(value, vector)
    expected = np.cos(0.5) * vector + np.sin(0.5) * vector * volume
    assert np.linalg.norm(ga.grade(result, 5).data) > 0.4
    assert not ga.is_rotor(value)
    assert_data(ga.log(value).data, (-0.25 * volume).data)
    with pytest.raises(ValueError, match="normalized rotor"):
        ga.rotor_generator(value)
    for target in TARGETS:
        check_value(result, expected.data, expr, target)


@pytest.mark.parametrize("expr", (False, True))
def test_rotor_predicate_and_generator_forward_absolute_action_tolerance(expr):
    algebra = ga.Algebra(6)
    generator = 8e-13 * algebra.pseudoscalar(expr=expr)
    value = ga.exp(generator)
    assert_data((value * ~value).data, algebra.identity.data)
    assert not ga.is_rotor(value)
    assert ga.is_rotor(value, atol=1e-10)
    with pytest.raises(ValueError, match="normalized rotor"):
        ga.rotor_generator(value)
    np.testing.assert_allclose(ga.log(value, atol=1e-10).data, generator.data, rtol=0, atol=1e-25)
    np.testing.assert_allclose(ga.rotor_generator(value, atol=1e-10).data, generator.data, rtol=0, atol=1e-25)
