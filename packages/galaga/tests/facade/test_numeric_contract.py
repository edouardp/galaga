"""Public facade contracts with historical numeric evidence, not a live v1 engine.

The direct core suite owns exhaustive mathematical correctness. These tests
exercise the public value protocol and retain seeded v1 observations alongside
forced core-reference comparisons. Deliberate v2 corrections have independent
algebraic expectations instead of conditional compatibility assertions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga.core as core
import galaga.facade as facade

BASELINE_PATH = Path(__file__).parents[2] / "tools/baselines/numeric-contract-v1.json"
BASELINE = json.loads(BASELINE_PATH.read_text())


def assert_coefficients_close(actual: Any, expected: Any, *, atol: float = 1e-12) -> None:
    np.testing.assert_allclose(actual.data, expected.data, rtol=0.0, atol=atol)


class TestFacadeNumericContract:
    def test_algebra_construction_and_factories(self) -> None:
        algebra: Any = facade.Algebra(2, 1, 1)

        assert algebra.n == 4
        assert algebra.dim == 16
        assert len(algebra.basis_vectors()) == 4
        assert len(algebra.basis_blades(2)) == 6
        assert algebra.identity == algebra.scalar(1)
        assert algebra.I == algebra.pseudoscalar()

        vector = algebra.vector([2, -1, 3, 0.5])
        np.testing.assert_array_equal(vector.vector_part, [2, -1, 3, 0.5])
        assert vector.homogeneous_grade() == 1
        assert algebra.pseudoscalar().homogeneous_grade() == algebra.n

        explicit: Any = facade.Algebra(signature=(1, -1, 0))
        e1, e2, e3 = explicit.basis_vectors()
        assert e1 * e1 == 1
        assert e2 * e2 == -1
        assert e3 * e3 == 0

    def test_python_operators_and_checked_scalar_conversion(self) -> None:
        api = facade
        algebra: Any = facade.Algebra(3)
        e1, e2, e3 = algebra.basis_vectors()
        value = 2 + e1 - 3 * (e2 ^ e3)

        assert value + e2 == e2 + value
        assert value - e2 == -(e2 - value)
        assert value * e1 == api.geometric_product(value, e1)
        assert value ^ e1 == api.outer_product(value, e1)
        assert value | e1 == api.doran_lasenby_inner(value, e1)
        assert ~value == api.reverse(value)
        assert value[2] == api.grade(value, 2)
        assert value**0 == algebra.identity
        assert (value / 2) * 2 == value
        assert float(algebra.scalar(3.5)) == 3.5
        with pytest.raises(TypeError):
            float(value)

    def test_grade_operations_reconstruct_the_value(self) -> None:
        api = facade
        algebra: Any = facade.Algebra(4)
        e1, e2, e3, e4 = algebra.basis_vectors()
        value = 2 + e1 - 3 * (e2 ^ e3) + 0.5 * (e1 ^ e2 ^ e4)

        reconstructed = sum((api.grade(value, grade) for grade in range(5)), algebra.scalar(0))
        assert reconstructed == value
        assert api.grades(value, [0, 2]) == api.grade(value, 0) + api.grade(value, 2)
        assert api.even_grades(value) == api.grades(value, [0, 2, 4])
        assert api.odd_grades(value) == api.grades(value, [1, 3])
        assert api.grade(value, 5) == 0

    def test_named_products_obey_their_defining_conventions(self) -> None:
        api = facade
        algebra: Any = facade.Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        e12 = e1 ^ e2

        assert api.outer_product(e1, e2) == -api.outer_product(e2, e1)
        assert api.scalar_product(e12, e12) == -1
        assert api.metric_inner_product(e12, e12) == 1
        assert api.left_contraction(e1, e12) == e2
        assert api.right_contraction(e12, e2) == e1
        assert api.hestenes_inner(algebra.scalar(2), e1) == 0
        assert api.doran_lasenby_inner(algebra.scalar(2), e1) == 2 * e1
        assert api.transwedge(e1, e2, 0) == e12
        assert api.transwedge(e1, e1, 1) == 1
        assert api.antiwedge(e1, e2) == api.regressive_product(e1, e2)

    def test_involutions_and_dualities_round_trip(self) -> None:
        api = facade
        algebra: Any = facade.Algebra(3)
        e1, e2, e3 = algebra.basis_vectors()
        value = 2 + e1 - 3 * (e1 ^ e2) + 0.5 * (e1 ^ e2 ^ e3)

        assert api.reverse(api.reverse(value)) == value
        assert api.grade_involution(api.grade_involution(value)) == value
        assert api.conjugate(value) == api.grade_involution(api.reverse(value))
        assert api.uncomplement(api.complement(value)) == value
        assert api.undual(api.dual(value)) == value
        assert api.right_hodge_dual(value) == api.right_complement(api.metric_apply(value))
        assert api.left_weight_dual(value) == api.left_complement(api.antimetric_apply(value))

    def test_inverse_predicates_and_norms(self) -> None:
        api = facade
        algebra: Any = facade.Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        value = 2 + e1 + 0.25 * (e1 ^ e2)
        value_inverse = api.inverse(value)

        assert_coefficients_close(api.geometric_product(value, value_inverse), algebra.identity)
        assert_coefficients_close(api.geometric_product(value_inverse, value), algebra.identity)
        assert api.norm2(value) == api.metric_inner_product(value, value)
        assert np.isclose(float(api.norm(api.unit(value))), 1.0)
        assert api.is_scalar(algebra.scalar(2))
        assert api.is_vector(e1 + e2)
        assert api.is_bivector(e1 ^ e2)
        assert api.is_even(1 + (e1 ^ e2))
        assert api.is_rotor(api.exp(0.2 * (e1 ^ e2)))
        assert api.is_basis_blade(3 * (e1 ^ e2))
        assert not api.is_basis_blade(e1 + e2)

    def test_numeric_functions_use_the_same_owned_algebra(self) -> None:
        api = facade
        algebra: Any = facade.Algebra(3)
        e1, e2, e3 = algebra.basis_vectors()
        generator = 0.3 * (e1 ^ e2)
        rotor = api.exp(generator)

        assert_coefficients_close(api.log(rotor), generator)
        root = api.sqrt(rotor)
        assert isinstance(root, facade.Multivector)
        assert_coefficients_close(api.squared(root), rotor)
        assert api.scalar_sqrt(algebra.scalar(9)) == 3

        exterior_argument = e1 + (e2 ^ e3)
        assert api.outerexp(exterior_argument) == api.outercos(exterior_argument) + api.outersin(exterior_argument)
        assert_coefficients_close(
            api.geometric_product(api.outertan(exterior_argument), api.outercos(exterior_argument)),
            api.outersin(exterior_argument),
        )


class TestV2CorrectionLedger:
    def test_facade_supports_the_normal_unary_plus_protocol(self) -> None:
        value = facade.Algebra(2).basis_vectors()[0]

        assert +value is value

    def test_bracket_scaling_is_an_explicit_legacy_difference(self) -> None:
        historical = BASELINE["corrections"]
        facade_algebra = facade.Algebra(signature=historical["signature"])
        facade_e1, facade_e2 = facade_algebra.basis_vectors()

        # Derive the two defining products independently of the bracket aliases.
        reference = core.Algebra(gram=facade_algebra.gram, product_backend="reference")
        first, second = reference.basis_vectors()
        forward = reference.left_action(first) @ second.data
        backward = reference.left_action(second) @ first.data
        commutator = forward - backward
        anticommutator = 2 * (reference.left_action(first) @ first.data)
        np.testing.assert_array_equal(historical["commutator_e1_e2"], commutator)
        np.testing.assert_array_equal(historical["lie_bracket_e1_e2"], commutator / 2)
        np.testing.assert_array_equal(historical["anticommutator_e1_e1"], anticommutator)
        np.testing.assert_array_equal(historical["jordan_product_e1_e1"], anticommutator / 2)

        for operation in ("lie_bracket", "commutator"):
            np.testing.assert_array_equal(getattr(facade, operation)(facade_e1, facade_e2).data, commutator)
        for operation in ("jordan_product", "anticommutator"):
            np.testing.assert_array_equal(getattr(facade, operation)(facade_e1, facade_e1).data, anticommutator)
        np.testing.assert_array_equal(facade.half_commutator(facade_e1, facade_e2).data, commutator / 2)
        np.testing.assert_array_equal(facade.half_anticommutator(facade_e1, facade_e1).data, anticommutator / 2)

        assert facade.lie_bracket(facade_e1, facade_e2) == facade.commutator(facade_e1, facade_e2)
        assert facade.jordan_product(facade_e1, facade_e1) == facade.anticommutator(facade_e1, facade_e1)
        assert facade.half_commutator(facade_e1, facade_e2) == 0.5 * facade.commutator(facade_e1, facade_e2)
        assert facade.half_anticommutator(facade_e1, facade_e1) == 0.5 * facade.anticommutator(
            facade_e1,
            facade_e1,
        )

    def test_value_boundary_corrections_are_visible(self) -> None:
        historical = BASELINE["corrections"]
        facade_value = facade.Algebra(2).identity

        assert historical["identity_has_scalar_part"] is True
        assert not hasattr(facade_value, "scalar_part")
        assert historical["identity_coefficients_writeable"] is True
        assert not facade_value.data.flags.writeable
        with pytest.raises(ValueError, match="read-only"):
            facade_value.data[0] = 2

        facade_e1 = facade_value.algebra.basis_vectors()[0]
        assert historical["identity_equals_nearby_vector"] is True
        assert historical["vector_perturbation"] == 1e-10
        assert facade_value != facade_value + 1e-10 * facade_e1

    @pytest.mark.parametrize("perturbation", (1e-10, np.finfo(float).eps, np.nextafter(0.0, 1.0)))
    def test_exact_equality_never_uses_the_historical_comparison_tolerance(self, perturbation: float) -> None:
        algebra = facade.Algebra(2)
        value = algebra.identity
        nearby = value + perturbation * algebra.basis_vectors()[0]

        assert nearby.data[1] == perturbation
        assert value != nearby
        assert value == algebra.multivector(value.data.copy())


SEEDED_DIAGONAL_CASES = (
    ((1, 1), 1729),
    ((1, -1, -1), 2718),
    ((0, 1, 1), 3141),
    ((1, 1, 1, 1), 5772),
)
SEEDED_CASE_IDS = ("cl20-seed1729", "cl12-seed2718", "cl201-seed3141", "cl40-seed5772")
BINARY_OPERATIONS = (
    "geometric_product",
    "outer_product",
    "scalar_product",
    "metric_inner_product",
    "left_contraction",
    "right_contraction",
    "hestenes_inner",
    "doran_lasenby_inner",
    "commutator",
    "anticommutator",
    "antidot_product",
    "geometric_antiproduct",
    "regressive_product",
    "antiwedge",
    "left_interior_product",
    "right_interior_product",
)
UNARY_OPERATIONS = (
    "metric_apply",
    "antimetric_apply",
    "bulk_part",
    "weight_part",
    "right_hodge_dual",
    "left_hodge_dual",
    "right_weight_dual",
    "left_weight_dual",
    "reverse",
    "grade_involution",
    "conjugate",
    "complement",
    "uncomplement",
    "antireverse",
    "squared",
    "norm2",
    "even_grades",
    "odd_grades",
)
SAMPLES = {sample["id"]: sample for sample in BASELINE["cases"]}
SAMPLED_OPERATIONS = tuple(
    (case_id, operation)
    for case_id, (signature, _) in zip(SEEDED_CASE_IDS, SEEDED_DIAGONAL_CASES, strict=True)
    for operation in (
        *BINARY_OPERATIONS,
        *UNARY_OPERATIONS,
        "transwedge",
        *(("dual", "undual") if 0 not in signature else ()),
    )
)


def _sample_arguments(algebra: Any, sample: dict[str, Any], operation: str) -> tuple[Any, ...]:
    left = algebra.multivector(sample["left"])
    if operation in BINARY_OPERATIONS or operation == "transwedge":
        right = algebra.multivector(sample["right"])
        return (left, right, 1) if operation == "transwedge" else (left, right)
    if operation in (*UNARY_OPERATIONS, "dual", "undual"):
        return (left,)
    raise ValueError(f"operation is not in the historical numeric contract: {operation}")


def _assert_sample_coefficients(actual: np.ndarray, expected: np.ndarray, *, label: str) -> None:
    """Keep numeric regression tolerance separate from exact public equality."""
    assert actual.shape == expected.shape, f"{label}: coefficient shape changed"
    assert np.isfinite(actual).all() and np.isfinite(expected).all(), f"{label}: nonfinite coefficients"
    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12, equal_nan=False, err_msg=label)


def test_historical_numeric_inventory_preserves_every_original_sample() -> None:
    assert BASELINE["schema_version"] == 1
    assert BASELINE["source_commit"] == "fe99fd5d6fddee02af31a9f1278965b2606e7bc0"
    assert BASELINE["source_test"] == "packages/galaga/tests/facade/test_numeric_contract.py"
    assert BASELINE["captured_on"] == "2026-09-06"
    assert BASELINE["python"] == "3.14.4" and BASELINE["numpy"] == "2.5.2"
    assert BASELINE["comparison"] == {"rtol": 1e-12, "atol": 1e-12}
    assert tuple(BASELINE["binary_operations"]) == BINARY_OPERATIONS
    assert tuple(BASELINE["unary_operations"]) == UNARY_OPERATIONS
    assert len(BASELINE["cases"]) == len(SAMPLES) == len(SEEDED_CASE_IDS)
    assert tuple(SAMPLES) == SEEDED_CASE_IDS
    assert len(SAMPLED_OPERATIONS) == 146
    for case_id, (signature, seed) in zip(SEEDED_CASE_IDS, SEEDED_DIAGONAL_CASES, strict=True):
        sample = SAMPLES[case_id]
        algebra = core.Algebra(signature=signature)
        assert tuple(sample["signature"]) == signature and sample["seed"] == seed
        assert set(sample["results"]) == {operation for key, operation in SAMPLED_OPERATIONS if key == case_id}
        for data in (sample["left"], sample["right"], *sample["results"].values()):
            coefficients = np.asarray(data)
            assert coefficients.shape == (algebra.dim,) and np.isfinite(coefficients).all()


@pytest.mark.parametrize(
    ("case_id", "operation"),
    SAMPLED_OPERATIONS,
    ids=[f"{case_id}/{operation}" for case_id, operation in SAMPLED_OPERATIONS],
)
def test_seeded_diagonal_contract_matches_history_and_core_reference(case_id: str, operation: str) -> None:
    """Both current paths must match the pre-retirement observation independently."""
    sample = SAMPLES[case_id]
    expected = np.asarray(sample["results"][operation])
    algebra = facade.Algebra(signature=sample["signature"])
    reference = core.Algebra(gram=algebra.gram, product_backend="reference")
    assert reference.product_backend == "reference"
    assert expected.shape == (algebra.dim,)

    actual = getattr(facade, operation)(*_sample_arguments(algebra, sample, operation))
    reference_result = getattr(core, operation)(*_sample_arguments(reference, sample, operation))

    assert isinstance(actual, facade.Multivector) and actual.algebra is algebra
    assert isinstance(reference_result, core.Multivector) and reference_result.algebra is reference
    _assert_sample_coefficients(actual.data, expected, label=f"{case_id}/{operation}/facade")
    _assert_sample_coefficients(reference_result.data, expected, label=f"{case_id}/{operation}/reference")


@pytest.mark.parametrize("case_id", SEEDED_CASE_IDS)
def test_seeded_product_and_reverse_have_independent_algebraic_checks(case_id: str) -> None:
    sample = SAMPLES[case_id]
    algebra = facade.Algebra(signature=sample["signature"])
    reference = core.Algebra(gram=algebra.gram, product_backend="reference")
    left = algebra.multivector(sample["left"])
    right = algebra.multivector(sample["right"])
    reference_left = reference.multivector(sample["left"])

    product = reference.left_action(reference_left) @ right.data
    grades = np.array([mask.bit_count() for mask in range(algebra.dim)])
    reverse_signs = np.where((grades * (grades - 1) // 2) % 2, -1, 1)
    reversed_data = left.data * reverse_signs

    _assert_sample_coefficients(facade.geometric_product(left, right).data, product, label=f"{case_id}/left-action")
    _assert_sample_coefficients(facade.reverse(left).data, reversed_data, label=f"{case_id}/grade-law")


def test_singular_duality_errors_remain_explicit_instead_of_disappearing_with_v1() -> None:
    sample = SAMPLES["cl201-seed3141"]
    assert "dual" not in sample["results"] and "undual" not in sample["results"]
    algebra = facade.Algebra(signature=sample["signature"])
    value = algebra.multivector(sample["left"])

    for operation in ("dual", "undual"):
        with pytest.raises(ValueError, match="degenerate"):
            getattr(facade, operation)(value)


def test_numeric_contract_has_left_the_legacy_construction_allowlist() -> None:
    assert "facade/test_numeric_contract.py" not in LEGACY_ORACLE_TESTS


def test_every_cataloged_numeric_operation_has_a_public_facade_callable() -> None:
    structural_operator_ids = {
        "add",
        "negate",
        "power",
        "scalar_divide",
        "scalar_multiply",
        "subtract",
    }
    public_operation_ids = set(facade.OPERATIONS) - structural_operator_ids

    assert public_operation_ids <= set(facade.__all__)
    assert all(callable(getattr(facade, operation_id)) for operation_id in public_operation_ids)
