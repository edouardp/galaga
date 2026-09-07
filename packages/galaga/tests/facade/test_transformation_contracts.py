"""Archived helper evidence and coefficient-first public compositions."""

import json
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
from galaga.expression import evaluate

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/transformation-contracts-v1.json").read_text())
GRAMS = (
    np.eye(3),
    np.array([[2, 0.5, 0], [0.5, -1, 0.25], [0, 0.25, 3]]),
    np.diag([1, 1, 0]),
)
ROTOR_GRAMS = (
    ((1, 0), (0, 1)),
    ((2, 0.5), (0.5, 1)),
    ((1, 0), (0, -1)),
    ((1, 0), (0, 0)),
)


def assert_data(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape
    assert np.isfinite(actual).all() and np.isfinite(expected).all()
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-10)


def projector(gram, columns):
    return columns @ np.linalg.solve(columns.T @ gram @ columns, columns.T @ gram)


def reflection(gram, normal):
    return np.eye(len(normal)) - 2 * np.outer(normal, normal @ gram) / (normal @ gram @ normal)


def exterior_blade(algebra, columns, expr):
    blade = algebra.scalar(1, expr=expr)
    for column in columns.T:
        blade = blade ^ algebra.vector(column, expr=expr)
    return blade


def check_value(value, expected, expr, target):
    assert_data(value.data, expected)
    expression, value_hash = value.expr, hash(value)
    assert value.display(f"full/{target}")
    assert_data(value.data, expected)
    assert value.expr is expression and hash(value) == value_hash
    if expr:
        assert_data(evaluate(expression, algebra=value.algebra).data, expected)
    else:
        assert expression is None


@pytest.mark.parametrize("row", ARCHIVE["seeded_cases"], ids=lambda row: row["id"])
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_seeded_legacy_cases_replay_against_archive_and_coordinate_oracles(row, expr, target):
    algebra = ga.Algebra(row["n"])
    vector = algebra.vector(row["vector"], expr=expr)
    if row["kind"] == "projection":
        columns = np.asarray(row["columns"]).T
        expected = projector(algebra.gram, columns) @ vector.vector_part
        blade = exterior_blade(algebra, columns, expr)
        assert_data(blade.data, row["blade"])
        parallel = ga.left_contraction(vector, blade) * ga.inverse(blade)
        perpendicular = vector - parallel
        assert_data(parallel.vector_part, expected)
        check_value(parallel, row["projection"], expr, target)
        check_value(perpendicular, row["rejection"], expr, target)
    elif row["kind"] == "reflection":
        normal = algebra.vector(row["normal"], expr=expr)
        matrix = reflection(algebra.gram, normal.vector_part)
        result = -normal * vector * ga.inverse(normal)
        assert_data(result.vector_part, matrix @ vector.vector_part)
        check_value(result, row["reflection"], expr, target)
        if "other_vector" in row:
            other = algebra.vector(row["other_vector"], expr=expr)
            transformed = -normal * other * ga.inverse(normal)
            check_value(transformed, row["other_reflection"], expr, target)
            assert float(ga.scalar_product(result, transformed)) == pytest.approx(row["pairing"], abs=1e-10)
    elif row["kind"] == "double_reflection":
        first, second = (algebra.vector(data, expr=expr) for data in row["normals"])
        expected = reflection(algebra.gram, second.vector_part) @ reflection(algebra.gram, first.vector_part)
        rotor = second * first
        assert_data(rotor.data, row["rotor"])
        result = rotor * vector * ga.inverse(rotor)
        assert_data(result.vector_part, expected @ vector.vector_part)
        check_value(result, row["result"], expr, target)
    else:
        assert row["kind"] == "plane_normal_reflection"
        columns = np.asarray(row["columns"]).T
        expected = (np.eye(algebra.n) - 2 * projector(algebra.gram, columns)) @ vector.vector_part
        blade = exterior_blade(algebra, columns, expr)
        assert_data(blade.data, row["blade"])
        result = blade * vector * ga.inverse(blade)
        assert_data(result.vector_part, expected)
        check_value(result, row["result"], expr, target)


def test_low_dimensional_observations_preserve_values_and_named_provenance():
    one, two, three = ga.Algebra(1), ga.Algebra(2), ga.Algebra(3)
    (e,) = one.basis_vectors()
    e1, e2 = two.basis_vectors()
    rotor = ga.exp(-np.pi / 4 * (e1 ^ e2))
    a, _, _ = three.basis_vectors(expr=True)
    pseudoscalar = three.pseudoscalar(expr=True).named("I")
    values = {
        "project_self": ga.left_contraction(e, e) * ga.inverse(e),
        "reject_self": e - ga.left_contraction(e, e) * ga.inverse(e),
        "reflect_self": -e * e * ga.inverse(e),
        "quarter_turn_rotor": rotor,
        "quarter_turn_result": ga.sandwich(rotor, e1),
        "pseudoscalar": pseudoscalar,
        "named_pseudoscalar_product": a * pseudoscalar,
    }
    for row in ARCHIVE["low_dim"]:
        assert values[row["id"]].algebra.n == row["n"]
        assert_data(values[row["id"]].data, row["data"])
    value = values["named_pseudoscalar_product"]
    assert value.display("expr/latex") == ARCHIVE["low_dim"][-1]["latex"]
    assert ARCHIVE["low_dim"][-1]["unicode"] == "e₁I"  # V1's unspaced product.
    assert evaluate(value.expr, algebra=three, environment={"I": pseudoscalar}) == three.blade(6)


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("grade", (1, 2))
@pytest.mark.parametrize("scale", (-3, 0.5, 2))
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_non_euclidean_projection_uses_the_restricted_metric_and_is_scale_invariant(gram, grade, scale, target):
    columns = np.eye(3)[:, :grade]
    matrix = projector(gram, columns)
    coordinates = np.array([2.0, -1, 3])
    expected = matrix @ coordinates
    assert_data(matrix @ matrix, matrix)
    assert_data(matrix.T @ gram, gram @ matrix)
    algebra = ga.Algebra(gram=gram)
    vector = algebra.vector(coordinates, expr=True)
    blade = scale * exterior_blade(algebra, columns, True)
    parallel = ga.left_contraction(vector, blade) * ga.inverse(blade)
    perpendicular = vector - parallel
    check_value(parallel, algebra.vector(expected).data, True, target)
    check_value(perpendicular, algebra.vector(coordinates - expected).data, True, target)
    assert_data((parallel ^ blade).data, np.zeros(algebra.dim))
    assert_data(ga.left_contraction(perpendicular, blade).data, np.zeros(algebra.dim))
    assert_data(((vector ^ blade) * ga.inverse(blade)).data, perpendicular.data)
    assert_data((ga.left_contraction(parallel, blade) * ga.inverse(blade)).data, parallel.data)


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("scale", (-3, 0.5, 2))
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_scaled_and_negative_square_normals_require_the_inverse_not_reverse(gram, scale, target):
    coordinates, normal_coordinates = np.array([2.0, -1, 3]), np.array([0.0, scale, 0])
    matrix = reflection(gram, normal_coordinates)
    assert_data(matrix @ matrix, np.eye(3))
    assert_data(matrix.T @ gram @ matrix, gram)
    algebra = ga.Algebra(gram=gram)
    vector, normal = (algebra.vector(data, expr=True) for data in (coordinates, normal_coordinates))
    result = -normal * vector * ga.inverse(normal)
    check_value(result, algebra.vector(matrix @ coordinates).data, True, target)
    assert_data((-normal * result * ga.inverse(normal)).data, vector.data)
    # sandwich uses reversion, not inverse. None of these scaled normals
    # has square +1, including the negative-square frame.
    assert not result.almost_equal(-ga.sandwich(normal, vector))


@pytest.mark.parametrize("gram", ROTOR_GRAMS)
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_bivector_exponentials_use_elliptic_hyperbolic_or_null_branches(gram, expr, target):
    square, parameter = gram[0][1] ** 2 - gram[0][0] * gram[1][1], -0.3
    if square < 0:
        frequency = np.sqrt(-square)
        scalar, factor = np.cos(parameter * frequency), np.sin(parameter * frequency) / frequency
    elif square > 0:
        frequency = np.sqrt(square)
        scalar, factor = np.cosh(parameter * frequency), np.sinh(parameter * frequency) / frequency
    else:
        scalar, factor = 1, parameter
    # The vector commutator action follows directly from Gram entries.
    generator = 2 * np.array([[gram[0][1], gram[1][1]], [-gram[0][0], -gram[0][1]]])
    expected_matrix, term = np.eye(2), np.eye(2)
    for order in range(1, 50):
        term = term @ (parameter * generator) / order
        expected_matrix += term
    assert_data(expected_matrix.T @ np.asarray(gram) @ expected_matrix, gram)
    algebra = ga.Algebra(gram=gram)
    e1, e2 = algebra.basis_vectors(expr=expr)
    plane = e1 ^ e2
    assert plane * plane == square
    rotor = ga.exp(parameter * plane)
    check_value(rotor, [scalar, 0, 0, factor], expr, target)
    assert_data((rotor * ga.reverse(rotor)).data, algebra.scalar(1).data)
    assert ga.is_rotor(rotor)
    for index, vector in enumerate((e1, e2)):
        result = ga.sandwich(rotor, vector)
        check_value(result, algebra.vector(expected_matrix[:, index]).data, expr, target)


@pytest.mark.parametrize("gram, normal", ((((1, 0), (0, -1)), (1, 1)), (((1, 0), (0, 0)), (0, 1))))
def test_null_normals_and_blades_fail_instead_of_silently_using_a_pseudoinverse(gram, normal):
    algebra = ga.Algebra(gram=gram)
    vector = algebra.blade(1, expr=True)
    null = algebra.vector(normal, expr=True)
    assert null * null == 0
    with pytest.raises(ValueError, match="not invertible"):
        ga.left_contraction(vector, null) * ga.inverse(null)
    with pytest.raises(ValueError, match="not invertible"):
        -null * vector * ga.inverse(null)


def test_singular_ambient_metric_can_still_have_an_invertible_projection_blade():
    algebra = ga.Algebra(gram=GRAMS[2])
    e1, e2, e3 = algebra.basis_vectors()
    assert algebra.is_degenerate
    assert ga.inverse(e1 ^ e2) == -(e1 ^ e2)
    with pytest.raises(ValueError, match="not invertible"):
        ga.inverse(e1 ^ e3)


def test_zero_dimensional_scalar_projection_and_helper_retirement_are_explicit():
    algebra = ga.Algebra(0)
    value, blade = algebra.scalar(3), algebra.scalar(2)
    assert ga.left_contraction(value, blade) * ga.inverse(blade) == value
    assert float(ga.exp(value)) == pytest.approx(np.exp(3))
    assert not ga.is_rotor(ga.exp(value))
    for name in ("project", "reject", "reflect"):
        assert not hasattr(ga, name)
    for name in ("rotor", "rotor_from_bivector", "rotor_from_plane_angle"):
        assert not hasattr(algebra, name)
