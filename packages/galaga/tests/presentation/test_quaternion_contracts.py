"""Archived convention evidence and independent complex/Hamilton arithmetic."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
from galaga.expression import BladeLiteral, evaluate

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/quaternion-conventions-v1.json").read_text())
Q_MASKS = (0, 6, 5, 3)  # Hamilton coordinates (a,b,c,d) -> native exterior masks.
Q_PAIRS = (
    ((1, 2, 3, 4), (2, -1, 1, -3)),
    ((0, 0, 0, 0), (1, 2, 0, 0)),
    ((2, 0, 0, 0), (0, 0, -3, 0)),
    ((0.5, -0.25, 1.5, -2), (-1, 0.5, 0.25, 2)),
)
COMPLEX_PAIRS = ((3 + 4j, 1 - 2j), (0j, 2j), (2 + 0j, -3 + 0j), (0.5 - 1.25j, -2 + 0.5j))
GRAMS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    ((2, 0.5, 0), (0.5, -1, 0.25), (0, 0.25, 3)),
    ((1, 1, 0), (1, 1, 0), (0, 0, 0)),
)


def coefficients(coordinates):
    data = np.zeros(8)
    data[list(Q_MASKS)] = coordinates
    return data


def hamilton_product(left, right):
    """Scalar/dot/cross formula independent of Galaga operations and tables."""
    a, u = left[0], np.asarray(left[1:])
    b, v = right[0], np.asarray(right[1:])
    return np.concatenate(([a * b - np.dot(u, v)], a * v + b * u + np.cross(u, v)))


def xyz_view():
    algebra = ga.Algebra(config=ga.p_quaternion())
    original = algebra.presentation.blades
    labels = list(original.labels)
    for mask, name in ((1, ga.Name("x")), (2, ga.Name("y")), (4, ga.Name("z")), (7, ga.Name("xyz", "xyz", "x y z"))):
        labels[mask] = replace(labels[mask], name=name)
    return algebra.with_blades(ga.BladeConvention(3, labels, aliases=original.aliases, roles=original.roles))


def observed_values():
    algebra = ga.Algebra(config=ga.p_quaternion())
    e1, e2, e3 = algebra.basis_vectors()
    i, j, k = e2 ^ e3, e1 ^ e3, e1 ^ e2
    complex_algebra = ga.Algebra(config=ga.p_complex())
    c1, c2 = complex_algebra.basis_vectors()
    imaginary = c1 ^ c2
    return {
        "e2_e3": e2 * e3,
        "e1_e3": e1 * e3,
        "e1_e2": e1 * e2,
        "e3_e2": e3 * e2,
        "e3_e1": e3 * e1,
        "e2_e1": e2 * e1,
        "i_j": i * j,
        "j_i": j * i,
        "j_k": j * k,
        "k_j": k * j,
        "k_i": k * i,
        "i_k": i * k,
        "lookup_i": algebra.blade("i"),
        "lookup_metric_role": algebra.blade("quaternion_i"),
        "lookup_multivector": algebra.blade(i),
        "lookup_lazy": algebra.blade("i", expr=True),
        "imaginary": imaginary,
        "complex_number": 3 + 4 * imaginary,
        "complex_reverse": ga.reverse(3 + 4 * imaginary),
    }


def assert_data(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape
    assert np.isfinite(actual).all() and np.isfinite(expected).all()
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)


@pytest.mark.parametrize("row", ARCHIVE["observations"], ids=lambda row: row["id"])
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_archived_observations_preserve_coefficients_and_rendering(row, target):
    value = observed_values()[row["id"]]
    assert_data(value.data, row["coefficients"])
    assert value.display(f"value/{target}") == row[target]


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda table: table["id"])
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_complete_archived_basis_tables_preserve_values_and_names(table, target):
    algebra = {
        "quaternion": ga.Algebra(config=ga.p_quaternion()),
        "complex": ga.Algebra(config=ga.p_complex()),
        "xyz": xyz_view(),
    }[table["id"]]
    assert tuple(table["signature"]) == algebra.signature
    assert len(table["basis"]) == algebra.dim
    for mask, row in enumerate(table["basis"]):
        assert row["id"] == str(mask)
        assert_data(algebra.blade(mask).data, row["coefficients"])
        assert algebra.blade(mask).display(f"value/{target}") == row[target]
        assert algebra.blade_label(mask).name.for_target(target) == row[target]


def test_hamilton_coordinates_are_derived_from_actual_exterior_products():
    algebra = ga.Algebra(config=ga.p_quaternion())
    e1, e2, e3 = algebra.basis_vectors()
    actual = (algebra.scalar(1), e2 ^ e3, e1 ^ e3, e1 ^ e2)
    np.testing.assert_array_equal([value.data for value in actual], np.eye(8)[list(Q_MASKS)])
    assert actual[1] * actual[2] == actual[3]
    assert actual[2] * actual[3] == actual[1]
    assert actual[3] * actual[1] == actual[2]
    assert actual[1] * actual[2] * actual[3] == -1
    assert algebra.blades("quaternion_i", "quaternion_j", "quaternion_k") == actual[1:]
    assert algebra.basis_blades(2) == tuple(reversed(actual[1:]))


@pytest.mark.parametrize("pair", Q_PAIRS)
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_quaternion_arithmetic_matches_independent_hamilton_coordinates(pair, expr, target):
    left, right = (np.asarray(row, dtype=float) for row in pair)
    conjugate_left = left * (1, -1, -1, -1)
    inverse_right = right * (1, -1, -1, -1) / np.dot(right, right)
    expected = {
        "sum": left + right,
        "product": hamilton_product(left, right),
        "reverse": conjugate_left,
        "conjugate": conjugate_left,
        "inverse": inverse_right,
        "division": hamilton_product(left, inverse_right),
    }
    algebra = ga.Algebra(config=ga.p_quaternion())
    q = algebra.multivector(coefficients(left), expr=expr)
    r = algebra.multivector(coefficients(right), expr=expr)
    results = {
        "sum": q + r,
        "product": q * r,
        "reverse": ga.reverse(q),
        "conjugate": ga.conjugate(q),
        "inverse": ga.inverse(r),
        "division": q / r,
    }
    for operation, value in results.items():
        assert_data(value.data, coefficients(expected[operation]))
        assert not np.any(value.data[[1, 2, 4, 7]])  # Closed even subalgebra.
        expression, value_hash = value.expr, hash(value)
        assert value.display(f"full/{target}")
        assert_data(value.data, coefficients(expected[operation]))
        assert value.expr is expression and hash(value) == value_hash
        if expr:
            assert_data(evaluate(expression, algebra=algebra).data, value.data)
        else:
            assert expression is None
    assert float(ga.norm(q)) == pytest.approx(np.linalg.norm(left))
    assert_data((r * results["inverse"]).data, algebra.scalar(1).data)
    assert_data((results["division"] * r).data, q.data)


@pytest.mark.parametrize("pair", COMPLEX_PAIRS)
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_complex_arithmetic_matches_python_complex_numbers(pair, expr, target):
    left, right = pair
    expected = (left + right, left * right, left / right, left.conjugate(), 1 / right)
    algebra = ga.Algebra(config=ga.p_complex())
    q = algebra.multivector([left.real, 0, 0, left.imag], expr=expr)
    r = algebra.multivector([right.real, 0, 0, right.imag], expr=expr)
    for value, number in zip((q + r, q * r, q / r, ga.reverse(q), ga.inverse(r)), expected, strict=True):
        assert_data(value.data, [number.real, 0, 0, number.imag])
        expression, value_hash = value.expr, hash(value)
        assert value.display(f"full/{target}")
        assert value.expr is expression and hash(value) == value_hash
        assert_data(value.data, [number.real, 0, 0, number.imag])
        if expr:
            assert_data(evaluate(expression, algebra=algebra).data, value.data)
        else:
            assert expression is None
    assert float(ga.norm(q)) == pytest.approx(abs(left))


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_quaternion_labels_do_not_override_gram_derived_blade_squares(gram, target):
    algebra = ga.Algebra(gram=gram, product_backend="reference")
    vectors = algebra.basis_vectors()
    expected = tuple(
        (vectors[a] ^ vectors[b], gram[a][b] ** 2 - gram[a][a] * gram[b][b]) for a, b in ((1, 2), (0, 2), (0, 1))
    )
    view = algebra.with_blades(ga.quaternion_blade_convention())
    assert view.numeric is algebra.numeric
    for role, (blade, square) in zip(("quaternion_i", "quaternion_j", "quaternion_k"), expected, strict=True):
        value = view.blade(role, expr=True)
        assert value == blade
        assert value * value == algebra.scalar(square)
        assert isinstance(value.expr, BladeLiteral)
        assert evaluate(value.expr, algebra=view) == blade
        assert value.display(f"value/{target}") in ("i", "j", "k")
    assert view.blade("i").display(f"value/{target}") == "i"
    assert [float(value * value) for value, _ in expected] == [square for _, square in expected]


@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_reverse_and_conjugate_agree_only_on_the_even_subalgebra(target):
    algebra = ga.Algebra(config=ga.p_quaternion())
    e1, e2, e3 = algebra.basis_vectors(expr=True)
    q = 1 + 2 * (e2 ^ e3) + 3 * (e1 ^ e3) + 4 * (e1 ^ e2)
    assert ga.reverse(q) == ga.conjugate(q)
    mixed = q + 5 * e1 + 7 * (e1 ^ e2 ^ e3)
    reverse_signs = [(-1) ** (mask.bit_count() * (mask.bit_count() - 1) // 2) for mask in range(algebra.dim)]
    conjugate_signs = [(-1) ** (mask.bit_count() * (mask.bit_count() + 1) // 2) for mask in range(algebra.dim)]
    reversed_value, conjugated_value = ga.reverse(mixed), ga.conjugate(mixed)
    assert_data(reversed_value.data, mixed.data * reverse_signs)
    assert_data(conjugated_value.data, mixed.data * conjugate_signs)
    assert reversed_value != conjugated_value
    for value in (reversed_value, conjugated_value):
        assert value.display(f"full/{target}")
        assert_data(evaluate(value.expr, algebra=algebra).data, value.data)


def test_custom_names_preserve_roles_aliases_order_and_numeric_identity():
    view = xyz_view()
    original = ga.Algebra.from_numeric(view.numeric, presentation=ga.p_quaternion().build().presentation)
    assert view.numeric is original.numeric
    assert view.display_order == original.display_order
    for role, alias, expected in zip(
        ("quaternion_i", "quaternion_j", "quaternion_k"),
        ("e23", "e13", "e12"),
        (view.blade(2) ^ view.blade(4), view.blade(1) ^ view.blade(4), view.blade(1) ^ view.blade(2)),
        strict=True,
    ):
        assert view.blade(role) == view.blade(alias) == expected
        assert hash(view.blade(role)) == hash(original.blade(role))
    assert original.blade(4).latex() == "e_{3}" and view.blade(4).latex() == "z"
    assert view.presentation.local_names == original.presentation.local_names
    renamed = view.with_local_names(ga.LocalNamePolicy.from_convention(view.presentation.blades))
    assert {"x", "y", "z", "i", "j", "k", "xyz"} == set(renamed.locals())
