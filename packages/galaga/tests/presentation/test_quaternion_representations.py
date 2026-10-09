"""Quaternion representations share Hamilton arithmetic and retain GA semantics."""

import numpy as np
import pytest

from galaga import (
    Algebra,
    Presenter,
    clifford_conjugate,
    evaluate,
    exp,
    grade_involution,
    inverse,
    log,
    norm2,
    presets,
    quaternion_blade_convention,
    quaternion_display_order,
    reverse,
    sqrt,
)
from galaga.presets import QuaternionPreset


@pytest.fixture(params=("bivector", "direct"))
def algebra(request):
    return Algebra(config=presets.quaternion(representation=request.param), user_config_files=False)


def units(algebra):
    return algebra.blades("quaternion_i", "quaternion_j", "quaternion_k")


def from_coordinates(algebra, coordinates):
    scalar, *imaginary = coordinates
    return scalar * algebra.identity + sum(coefficient * unit for coefficient, unit in zip(imaginary, units(algebra)))


def hamilton_product(left, right):
    a, u = left[0], np.asarray(left[1:])
    b, v = right[0], np.asarray(right[1:])
    return np.concatenate(([a * b - np.dot(u, v)], a * v + b * u + np.cross(u, v)))


def test_unit_names_and_roles_match_native_products(algebra):
    vectors = algebra.basis_vectors()
    native = (
        (vectors[1] ^ vectors[2], vectors[0] ^ vectors[2], vectors[0] ^ vectors[1])
        if algebra.n == 3
        else (vectors[0], vectors[1], vectors[0] ^ vectors[1])
    )
    i, j, k = units(algebra)
    assert (i, j, k) == native
    for name, unit in zip("ijk", native):
        assert algebra.locals()[name] == algebra.blade(name) == unit
        assert unit * unit == -algebra.identity
        for target in ("ascii", "unicode", "latex"):
            assert unit.display(f"value/{target}") == name
    assert i * j == k
    assert j * k == i
    assert k * i == j
    assert i * j * k == -algebra.identity
    assert j * i == -k
    assert k * j == -i
    assert i * k == -j
    assert algebra.model.id == "quaternion"
    for name, unit in zip("ijk", native):
        ref = dict(algebra.model.roles)[f"quaternion_{name}"]
        assert algebra.blade(ref.mask) * ref.orientation == unit


def test_default_representation_is_unchanged():
    assert presets.quaternion() == presets.quaternion(representation="bivector") == QuaternionPreset()
    algebra = Algebra(config=presets.quaternion(), user_config_files=False)
    assert algebra.signature == (1, 1, 1)
    assert algebra.numeric.id == "quaternion-cl3"
    assert algebra.dim == 8
    assert quaternion_display_order().masks == (0, 6, 5, 3, 1, 2, 4, 7)
    assert all(unit.homogeneous_grade() == 2 for unit in units(algebra))
    for alias, unit in zip(("e23", "e13", "e12"), units(algebra)):
        assert algebra.blade(alias) == unit
    assert all(vector.homogeneous_grade() == 1 for vector in algebra.basis_vectors())


def test_direct_representation_exposes_vectors_i_j_and_pseudoscalar_k():
    algebra = Algebra(config=presets.quaternion(representation="direct"), user_config_files=False)
    assert algebra.signature == (-1, -1)
    assert algebra.numeric.id == "quaternion-cl02"
    assert algebra.dim == 4
    assert list(algebra.locals()) == ["i", "j", "k"]
    i, j = algebra.basis_vectors()
    assert (i, j, algebra.I) == units(algebra)
    assert algebra.locals()["k"] == algebra.I == i ^ j
    assert algebra.basis_blades(2) == (algebra.I,)
    for alias, unit in zip(("e1", "e2", "e12"), units(algebra)):
        assert algebra.blade(alias) == unit
    assert quaternion_display_order(representation="direct").masks == (0, 1, 2, 3)
    assert (1 + 2 * i + 3 * j + 4 * algebra.I).display("value/ascii") == "1 + 2i + 3j + 4k"


@pytest.mark.parametrize(
    "left,right",
    [
        ((1, 2, 3, 4), (2, -1, 1, -3)),
        ((0, 0, 0, 0), (1, 2, 0, 0)),
        ((2, 0, 0, 0), (0, 0, -3, 0)),
        ((0.5, -0.25, 1.5, -2), (-1, 0.5, 0.25, 2)),
    ],
)
@pytest.mark.parametrize("expr", [False, True])
def test_arithmetic_matches_hamilton_coordinates(algebra, left, right, expr):
    left, right = np.asarray(left), np.asarray(right)
    q, r = from_coordinates(algebra, left), from_coordinates(algebra, right)
    q, r = (q.with_expr(), r.with_expr()) if expr else (q.without_expr(), r.without_expr())
    conjugate = left * (1, -1, -1, -1)
    inverse_right = right * (1, -1, -1, -1) / np.dot(right, right)
    results = (
        (q + r, left + right),
        (q - r, left - right),
        (q * r, hamilton_product(left, right)),
        (clifford_conjugate(q), conjugate),
        (inverse(r), inverse_right),
        (q / r, hamilton_product(left, inverse_right)),
        (q**2, hamilton_product(left, left)),
    )
    for result, expected in results:
        np.testing.assert_allclose(result.data, from_coordinates(algebra, expected).data, atol=1e-12)
        if expr:
            assert evaluate(result.expr, algebra=algebra) == result
    assert float(q * clifford_conjugate(q)) == pytest.approx(np.dot(left, left))
    np.testing.assert_allclose((r * inverse(r)).data, algebra.identity.data, atol=1e-12)
    np.testing.assert_allclose((inverse(r) * r).data, algebra.identity.data, atol=1e-12)
    np.testing.assert_allclose(((q / r) * r).data, q.data, atol=1e-12)


def test_ga_involutions_and_norm_follow_metric_and_grades(algebra):
    i, j, k = units(algebra)
    q = 1 + 2 * i + 3 * j + 4 * k
    assert reverse(q) == sum(((-1) ** (grade * (grade - 1) // 2)) * q[grade] for grade in range(algebra.n + 1))
    assert clifford_conjugate(q) == 1 - 2 * i - 3 * j - 4 * k
    assert norm2(q) == float((q * reverse(q))[0])
    if algebra.n == 3:
        assert reverse(q) == clifford_conjugate(q)
        assert grade_involution(q) == q
        assert norm2(q) == 30
    else:
        assert reverse(q) == 1 + 2 * i + 3 * j - 4 * k
        assert grade_involution(q) == 1 - 2 * i - 3 * j + 4 * k
        assert norm2(q) == 4
        assert norm2(1 + i) == 0
        assert (1 + i) * inverse(1 + i) == algebra.identity


def test_supported_transcendentals_agree_with_quaternion_formulas(algebra):
    i, j, k = units(algebra)
    vector = 2 * i + 3 * j + 4 * k
    radius = np.sqrt(29)
    q = 1 + vector
    expected_exp = np.exp(1) * (np.cos(radius) + np.sin(radius) * vector / radius)
    expected_log = np.log(np.sqrt(30)) + np.arctan2(radius, 1) * vector / radius
    np.testing.assert_allclose(exp(q).data, expected_exp.data, atol=1e-12)
    np.testing.assert_allclose(log(q).data, expected_log.data, atol=1e-12)
    np.testing.assert_allclose(exp(log(q)).data, q.data, atol=1e-12)
    root = sqrt(q)
    np.testing.assert_allclose((root * root).data, q.data, atol=1e-12)
    assert root.coefficient(0) > 0


def test_blade_recipe_and_presenter_use_selected_representation(algebra):
    representation = "direct" if algebra.n == 2 else "bivector"
    recipe = presets.blades.quaternion(representation=representation)
    raw = Algebra(algebra.signature, blades=recipe, user_config_files=False)
    assert raw.presentation.blades == algebra.presentation.blades
    assert quaternion_blade_convention(representation=representation) == algebra.presentation.blades
    value = from_coordinates(raw, (1, 2, 3, 4))
    presenter = presets.presenters.values() | recipe
    expected = "1 + 2i + 3j + 4k" if algebra.n == 2 else "1 + 4k + 3j + 2i"
    assert presenter(value).ascii() == expected
    assert Presenter(blades=recipe)(value).ascii(content="value") == expected
    ordered = presenter | quaternion_display_order(representation=representation)
    assert ordered(value).ascii() == "1 + 2i + 3j + 4k"
    with pytest.raises(ValueError, match="requires dimension"):
        Algebra(3 if algebra.n == 2 else 2, blades=recipe, user_config_files=False)


def test_blade_recipe_keeps_target_metric():
    algebra = Algebra(2, blades=presets.blades.quaternion(representation="direct"), user_config_files=False)
    i, j = algebra.basis_vectors()
    assert i * i == j * j == algebra.identity
    assert (i * j) ** 2 == -algebra.identity


@pytest.mark.parametrize("invalid", ["vector", "even", "", True, None, 1])
def test_unknown_representations_are_rejected(invalid):
    for factory in (
        presets.quaternion,
        QuaternionPreset,
        presets.blades.quaternion,
        quaternion_blade_convention,
        quaternion_display_order,
    ):
        with pytest.raises(ValueError, match="'bivector' or 'direct'"):
            factory(representation=invalid)
