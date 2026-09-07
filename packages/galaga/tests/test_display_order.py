"""Display order changes presentation, never native basis enumeration or data."""

from __future__ import annotations

import numpy as np
import pytest

from galaga import Algebra, DisplayOrder, DisplayPolicy, p_quaternion


def _quaternion_units(algebra):
    e1, e2, e3 = algebra.basis_vectors()
    units = (e2 ^ e3, e1 ^ e3, e1 ^ e2)
    # Establish numeric meaning before using the conventional labels.
    for unit, role in zip(units, ("quaternion_i", "quaternion_j", "quaternion_k"), strict=True):
        assert unit == algebra.blade(role)
    return units


def test_valid_permutation_is_accepted_without_changing_blade_vocabulary() -> None:
    algebra = Algebra(2)
    changed = algebra.with_display_order(DisplayOrder(2, (0, 2, 1, 3)))
    assert changed.display_order == (0, 2, 1, 3)
    assert changed.presentation.blades is algebra.presentation.blades
    assert changed.numeric is algebra.numeric


def test_default_order_is_native_bitmask_order_and_grade_order_is_explicit() -> None:
    algebra = Algebra(3)
    assert algebra.display_order == tuple(range(algebra.dim))
    grade_order = tuple(sorted(range(algebra.dim), key=lambda mask: (mask.bit_count(), mask)))
    changed = algebra.with_display_order(DisplayOrder(algebra.n, grade_order))
    e1, e2, e3 = algebra.basis_vectors()
    value = 1 + e1 + e2 + (e1 ^ e2) + e3
    assert str(value) == "1 + e₁ + e₂ + e₁₂ + e₃"
    assert str(changed.multivector(value.data)) == "1 + e₁ + e₂ + e₃ + e₁₂"
    assert changed.multivector(value.data) == value


@pytest.mark.parametrize(
    "masks",
    ((0, 1, 2), (0, 0, 1, 3), (0, 1, 2, 99), (0, 1, 2, -1), (False, 1, 2, 3), (0, 1, 2, 3.0)),
    ids=("length", "duplicate", "range", "negative", "boolean", "noninteger"),
)
def test_invalid_display_permutations_are_rejected(masks) -> None:
    with pytest.raises(ValueError, match="every mask"):
        DisplayOrder(2, masks)


def test_display_order_must_match_the_algebra_dimension() -> None:
    with pytest.raises(ValueError, match="dimensions must match"):
        Algebra(2, display_order=DisplayOrder(3))


def test_default_vector_rendering_is_unchanged() -> None:
    e1, e2, e3 = Algebra(3).basis_vectors()
    assert str(e1 + 2 * e2 + 3 * e3) == "e₁ + 2e₂ + 3e₃"


@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
@pytest.mark.parametrize("negative", (False, True))
def test_quaternion_rendering_uses_conventional_order_and_preserves_signs(target: str, negative: bool) -> None:
    algebra = Algebra(config=p_quaternion())
    i, j, k = _quaternion_units(algebra)
    value = 1 - 2 * i + 3 * j - 4 * k if negative else 1 + 2 * i + 3 * j + 4 * k
    expected = "1 - 2i + 3j - 4k" if negative else "1 + 2i + 3j + 4k"
    if target == "latex":
        expected = "1 - 2 i + 3 j - 4 k" if negative else "1 + 2 i + 3 j + 4 k"
    assert value.display(f"value/{target}") == expected
    assert format(value, f"value/{target}") == expected


def test_precision_policy_keeps_quaternion_term_order() -> None:
    algebra = Algebra(config=p_quaternion(), display=DisplayPolicy(coefficient_precision=3))
    i, j, k = _quaternion_units(algebra)
    value = 1 + 2.3456 * i + 3.4567 * j + 4.5678 * k
    assert str(value) == "1 + 2.35i + 3.46j + 4.57k"
    assert value.latex() == "1 + 2.35 i + 3.46 j + 4.57 k"


@pytest.mark.parametrize("grade", (0, 1, 2, 3))
@pytest.mark.parametrize("tracked", (False, True))
def test_basis_blades_remain_native_masks_despite_display_order(grade: int, tracked: bool) -> None:
    algebra = Algebra(config=p_quaternion())
    blades = algebra.basis_blades(grade, expr=tracked)
    masks = [mask for mask in range(algebra.dim) if mask.bit_count() == grade]
    np.testing.assert_array_equal([blade.data for blade in blades], np.eye(algebra.dim)[masks])
    assert all((blade.expr is not None) == tracked for blade in blades)
    if grade == 2:
        assert [str(blade) for blade in blades] == ["k", "j", "i"]
        assert [str(algebra.blade(role)) for role in ("quaternion_i", "quaternion_j", "quaternion_k")] == [
            "i",
            "j",
            "k",
        ]


def test_default_basis_blades_retain_native_names() -> None:
    assert [str(blade) for blade in Algebra(3).basis_blades(2)] == ["e₁₂", "e₁₃", "e₂₃"]


def test_quaternion_data_and_products_are_independent_of_display_order() -> None:
    algebra = Algebra(config=p_quaternion())
    i, j, k = _quaternion_units(algebra)
    # Compute products independently through the public numeric left action.
    for left, right, expected in ((i, j, k), (j, k, i), (k, i, j), (i, i, -algebra.identity)):
        np.testing.assert_array_equal(left.numeric.algebra.left_action(left.numeric) @ right.data, expected.data)
        assert left * right == expected
    for unit, indices in ((i, (1, 2)), (j, (0, 2)), (k, (0, 1))):
        expected_data = np.zeros(algebra.dim)
        expected_data[sum(1 << index for index in indices)] = 1.0
        np.testing.assert_array_equal(unit.data, expected_data)

    changed = algebra.with_display_order(DisplayOrder(algebra.n))
    value = 1 + 2 * i + 3 * j + 4 * k
    presented = changed.multivector(value.data)
    assert str(presented) == "1 + 4k + 3j + 2i"
    assert value == presented and hash(value) == hash(presented)
    np.testing.assert_array_equal((value * value).data, (presented * presented).data)
    assert not presented.data.flags.writeable


@pytest.mark.parametrize(
    "gram", (np.eye(2), np.diag([1.0, 0.0]), [[2.0, 0.5], [0.5, -1.0]], [[0.0, -1.0], [-1.0, 0.0]])
)
def test_scoped_order_changes_only_rendering_for_general_metrics(gram) -> None:
    algebra = Algebra(gram=gram)
    value = algebra.multivector([1.0, 2.0, 3.0, 4.0]).with_expr()
    original_data, original_expression, original_hash = value.data.copy(), value.expr, hash(value)
    product = value * value
    scoped = algebra.presentation.with_display_order(DisplayOrder(algebra.n, reversed(range(algebra.dim))))
    with algebra.use_presentation(scoped):
        assert str(value) == "4e₁₂ + 3e₂ + 2e₁ + 1"
        assert [str(vector) for vector in algebra.basis_vectors()] == ["e₁", "e₂"]
        np.testing.assert_array_equal([vector.data for vector in algebra.basis_vectors()], np.eye(algebra.dim)[[1, 2]])
        assert value * value == product
    assert str(value) == "1 + 2e₁ + 3e₂ + 4e₁₂"
    assert value.expr is original_expression and hash(value) == original_hash
    np.testing.assert_array_equal(value.data, original_data)
