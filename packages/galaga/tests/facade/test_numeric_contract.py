"""Implementation-neutral contracts for the legacy and v2 numeric APIs.

The direct core suite owns exhaustive mathematical correctness.  These tests
exercise the public value protocol twice: once through the retained v1 engine
and once through the composition facade that will become Galaga 2.  Deliberate
v2 differences are kept in separate tests instead of hidden in the adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType
from typing import Any

import numpy as np
import pytest

import galaga.algebra as legacy
import galaga.gram_bridge as facade


@dataclass(frozen=True, slots=True)
class NumericImplementation:
    """The small construction adapter shared by numeric contract tests."""

    id: str
    namespace: ModuleType
    wraps_core: bool

    def algebra(self, p: int, q: int = 0, r: int = 0) -> Any:
        return self.namespace.Algebra(p, q, r)

    def signature_algebra(self, signature: tuple[int, ...]) -> Any:
        if self.wraps_core:
            return self.namespace.Algebra(signature=signature)
        return self.namespace.Algebra(signature)

    def multivector(self, algebra: Any, data: np.ndarray) -> Any:
        if self.wraps_core:
            return algebra.multivector(data)
        return self.namespace.Multivector(algebra, data)


IMPLEMENTATIONS = (
    NumericImplementation("legacy-v1", legacy, False),
    NumericImplementation("gram-facade-v2", facade, True),
)


@pytest.fixture(params=IMPLEMENTATIONS, ids=lambda implementation: implementation.id)
def implementation(request: pytest.FixtureRequest) -> NumericImplementation:
    return request.param


def assert_coefficients_close(actual: Any, expected: Any, *, atol: float = 1e-12) -> None:
    np.testing.assert_allclose(actual.data, expected.data, rtol=0.0, atol=atol)


class TestSharedNumericContract:
    def test_algebra_construction_and_factories(self, implementation: NumericImplementation) -> None:
        algebra = implementation.algebra(2, 1, 1)

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

        explicit = implementation.signature_algebra((1, -1, 0))
        e1, e2, e3 = explicit.basis_vectors()
        assert e1 * e1 == 1
        assert e2 * e2 == -1
        assert e3 * e3 == 0

    def test_python_operators_and_checked_scalar_conversion(
        self,
        implementation: NumericImplementation,
    ) -> None:
        api = implementation.namespace
        algebra = implementation.algebra(3)
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

    def test_grade_operations_reconstruct_the_value(self, implementation: NumericImplementation) -> None:
        api = implementation.namespace
        algebra = implementation.algebra(4)
        e1, e2, e3, e4 = algebra.basis_vectors()
        value = 2 + e1 - 3 * (e2 ^ e3) + 0.5 * (e1 ^ e2 ^ e4)

        reconstructed = sum((api.grade(value, grade) for grade in range(5)), algebra.scalar(0))
        assert reconstructed == value
        assert api.grades(value, [0, 2]) == api.grade(value, 0) + api.grade(value, 2)
        assert api.even_grades(value) == api.grades(value, [0, 2, 4])
        assert api.odd_grades(value) == api.grades(value, [1, 3])
        assert api.grade(value, 5) == 0

    def test_named_products_obey_their_defining_conventions(
        self,
        implementation: NumericImplementation,
    ) -> None:
        api = implementation.namespace
        algebra = implementation.algebra(3)
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

    def test_involutions_and_dualities_round_trip(self, implementation: NumericImplementation) -> None:
        api = implementation.namespace
        algebra = implementation.algebra(3)
        e1, e2, e3 = algebra.basis_vectors()
        value = 2 + e1 - 3 * (e1 ^ e2) + 0.5 * (e1 ^ e2 ^ e3)

        assert api.reverse(api.reverse(value)) == value
        assert api.grade_involution(api.grade_involution(value)) == value
        assert api.conjugate(value) == api.grade_involution(api.reverse(value))
        assert api.uncomplement(api.complement(value)) == value
        assert api.undual(api.dual(value)) == value
        assert api.right_hodge_dual(value) == api.right_complement(api.metric_apply(value))
        assert api.left_weight_dual(value) == api.left_complement(api.antimetric_apply(value))

    def test_inverse_predicates_and_norms(self, implementation: NumericImplementation) -> None:
        api = implementation.namespace
        algebra = implementation.algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        value = 2 + e1 + 0.25 * (e1 ^ e2)
        value_inverse = api.inverse(value)

        assert_coefficients_close(api.geometric_product(value, value_inverse), algebra.identity)
        assert_coefficients_close(api.geometric_product(value_inverse, value), algebra.identity)
        assert api.norm2(value) == api.metric_inner_product(value, value)
        assert np.isclose(api.norm(api.unit(value)), 1.0)
        assert api.is_scalar(algebra.scalar(2))
        assert api.is_vector(e1 + e2)
        assert api.is_bivector(e1 ^ e2)
        assert api.is_even(1 + (e1 ^ e2))
        assert api.is_rotor(api.exp(0.2 * (e1 ^ e2)))
        assert api.is_basis_blade(3 * (e1 ^ e2))
        assert not api.is_basis_blade(e1 + e2)

    def test_numeric_functions_use_the_same_owned_algebra(self, implementation: NumericImplementation) -> None:
        api = implementation.namespace
        algebra = implementation.algebra(3)
        e1, e2, e3 = algebra.basis_vectors()
        generator = 0.3 * (e1 ^ e2)
        rotor = api.exp(generator)

        assert_coefficients_close(api.log(rotor), generator)
        root = api.sqrt(rotor)
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
        legacy_algebra = legacy.Algebra(2)
        legacy_e1, legacy_e2 = legacy_algebra.basis_vectors()
        facade_algebra = facade.Algebra(2)
        facade_e1, facade_e2 = facade_algebra.basis_vectors()

        assert legacy.lie_bracket(legacy_e1, legacy_e2) == 0.5 * legacy.commutator(legacy_e1, legacy_e2)
        assert legacy.jordan_product(legacy_e1, legacy_e1) == 0.5 * legacy.anticommutator(legacy_e1, legacy_e1)

        assert facade.lie_bracket(facade_e1, facade_e2) == facade.commutator(facade_e1, facade_e2)
        assert facade.jordan_product(facade_e1, facade_e1) == facade.anticommutator(facade_e1, facade_e1)
        assert facade.half_commutator(facade_e1, facade_e2) == 0.5 * facade.commutator(facade_e1, facade_e2)
        assert facade.half_anticommutator(facade_e1, facade_e1) == 0.5 * facade.anticommutator(
            facade_e1,
            facade_e1,
        )

    def test_value_boundary_corrections_are_visible(self) -> None:
        legacy_value = legacy.Algebra(2).identity
        facade_value = facade.Algebra(2).identity

        assert hasattr(legacy_value, "scalar_part")
        assert not hasattr(facade_value, "scalar_part")
        assert legacy_value.data.flags.writeable
        assert not facade_value.data.flags.writeable

        legacy_e1 = legacy_value.algebra.basis_vectors()[0]
        facade_e1 = facade_value.algebra.basis_vectors()[0]
        assert legacy_value == legacy_value + 1e-10 * legacy_e1
        assert facade_value != facade_value + 1e-10 * facade_e1


SEEDED_DIAGONAL_CASES = (
    ((1, 1), 1729),
    ((1, -1, -1), 2718),
    ((0, 1, 1), 3141),
    ((1, 1, 1, 1), 5772),
)


@pytest.mark.parametrize(
    ("signature", "seed"),
    SEEDED_DIAGONAL_CASES,
    ids=("cl20-seed1729", "cl12-seed2718", "cl201-seed3141", "cl40-seed5772"),
)
def test_seeded_diagonal_differential_contract(signature: tuple[int, ...], seed: int) -> None:
    """The facade retains v1 diagonal results outside ledgered corrections."""
    legacy_api = NumericImplementation("legacy-v1", legacy, False)
    facade_api = NumericImplementation("gram-facade-v2", facade, True)
    legacy_algebra = legacy_api.signature_algebra(signature)
    facade_algebra = facade_api.signature_algebra(signature)
    generator = np.random.default_rng(seed)
    left_data = generator.normal(size=legacy_algebra.dim)
    right_data = generator.normal(size=legacy_algebra.dim)
    legacy_left = legacy_api.multivector(legacy_algebra, left_data)
    legacy_right = legacy_api.multivector(legacy_algebra, right_data)
    facade_left = facade_api.multivector(facade_algebra, left_data)
    facade_right = facade_api.multivector(facade_algebra, right_data)

    binary_operations = (
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
    for operation_name in binary_operations:
        legacy_result = getattr(legacy, operation_name)(legacy_left, legacy_right)
        facade_result = getattr(facade, operation_name)(facade_left, facade_right)
        np.testing.assert_allclose(
            facade_result.data,
            legacy_result.data,
            rtol=1e-12,
            atol=1e-12,
            err_msg=operation_name,
        )

    unary_operations = (
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
    for operation_name in unary_operations:
        legacy_result = getattr(legacy, operation_name)(legacy_left)
        facade_result = getattr(facade, operation_name)(facade_left)
        np.testing.assert_allclose(
            facade_result.data,
            legacy_result.data,
            rtol=1e-12,
            atol=1e-12,
            err_msg=operation_name,
        )

    np.testing.assert_allclose(
        facade.transwedge(facade_left, facade_right, 1).data,
        legacy.transwedge(legacy_left, legacy_right, 1).data,
        rtol=1e-12,
        atol=1e-12,
    )
    if 0 not in signature:
        for operation_name in ("dual", "undual"):
            legacy_result = getattr(legacy, operation_name)(legacy_left)
            facade_result = getattr(facade, operation_name)(facade_left)
            np.testing.assert_allclose(
                facade_result.data,
                legacy_result.data,
                rtol=1e-12,
                atol=1e-12,
                err_msg=operation_name,
            )


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
