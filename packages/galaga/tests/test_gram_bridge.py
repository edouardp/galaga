"""Numeric parity tests for the opt-in core-backed facade."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest

from galaga import core
from galaga.gram_bridge import (
    EXCLUDED_PUBLIC_NAMES,
    OPERATIONS,
    Algebra,
    LeftFoldCall,
    Multivector,
    anticommutator,
    commutator,
    doran_lasenby_inner,
    geometric_product,
    grade,
    hestenes_inner,
    left_contraction,
    metric_inner_product,
    outer_product,
    reverse,
    right_contraction,
    scalar_part,
    scalar_product,
)


def native_cga_gram() -> np.ndarray:
    metric = np.eye(5)
    metric[3:, 3:] = np.array([[0.0, -1.0], [-1.0, 0.0]])
    return metric


class TestConstructionAndValues:
    def test_wraps_native_gram_algebra_without_copying_public_metadata(self) -> None:
        algebra = Algebra(gram=native_cga_gram())

        assert isinstance(algebra.numeric, core.Algebra)
        assert np.array_equal(algebra.gram, native_cga_gram())
        assert algebra.inertia == (4, 1, 0)
        assert not algebra.is_orthogonal_basis
        assert not algebra.gram.flags.writeable

    def test_factories_return_cached_immutable_facade_values(self) -> None:
        algebra = Algebra(3)
        first = algebra.basis_vectors()
        second = algebra.basis_vectors()

        assert first is second
        assert all(isinstance(value, Multivector) for value in first)
        assert all(value.algebra is algebra for value in first)
        assert not first[0].data.flags.writeable

    def test_scalar_extraction_is_a_standalone_composition(self) -> None:
        algebra = Algebra(2)
        e1, _ = algebra.basis_vectors()
        value = 3 + e1

        assert not hasattr(value, "scalar_part")
        assert scalar_part(value) == 3.0
        assert scalar_part(value) == float(grade(value, 0))
        with pytest.raises(TypeError):
            float(value)

    def test_operators_delegate_and_preserve_checked_scalar_conversion(self) -> None:
        algebra = Algebra(2)
        e1, e2 = algebra.basis_vectors()

        assert (e1 * e2).numeric == e1.numeric * e2.numeric
        assert (e1 ^ e2).numeric == e1.numeric ^ e2.numeric
        assert (e1 | e2).numeric == e1.numeric | e2.numeric
        assert (~(e1 ^ e2)).numeric == ~(e1.numeric ^ e2.numeric)
        assert float(2 * algebra.identity) == 2.0

    def test_mixed_algebras_are_rejected_before_numeric_dispatch(self) -> None:
        left = Algebra(2).basis_vectors()[0]
        right = Algebra(2).basis_vectors()[0]

        with pytest.raises(ValueError, match="different algebras"):
            geometric_product(left, right)


class TestCatalogAndParity:
    @pytest.mark.parametrize(
        ("facade_operation", "numeric_operation"),
        (
            (outer_product, core.outer_product),
            (scalar_product, core.scalar_product),
            (metric_inner_product, core.metric_inner_product),
            (left_contraction, core.left_contraction),
            (right_contraction, core.right_contraction),
            (hestenes_inner, core.hestenes_inner),
            (doran_lasenby_inner, core.doran_lasenby_inner),
            (commutator, core.commutator),
            (anticommutator, core.anticommutator),
        ),
        ids=lambda operation: getattr(operation, "__name__", str(operation)),
    )
    def test_binary_operation_matches_direct_gram_evaluation(
        self,
        facade_operation: Callable[[Multivector, Multivector], Multivector],
        numeric_operation: Callable[[core.Multivector, core.Multivector], core.Multivector],
    ) -> None:
        algebra = Algebra(
            gram=np.array(
                [
                    [2.0, 0.5, -0.25],
                    [0.5, 1.0, 0.75],
                    [-0.25, 0.75, -1.0],
                ]
            )
        )
        left = algebra.multivector(np.arange(algebra.dim) - 3)
        right = algebra.multivector(np.arange(algebra.dim)[::-1] - 2)

        result = facade_operation(left, right)

        assert result.numeric.algebra is algebra.numeric
        np.testing.assert_allclose(
            result.data,
            numeric_operation(left.numeric, right.numeric).data,
            rtol=0.0,
            atol=1e-12,
        )

    def test_unary_operation_matches_direct_gram_evaluation(self) -> None:
        algebra = Algebra(3)
        value = algebra.multivector(np.arange(algebra.dim) - 2)

        assert reverse(value).numeric == core.reverse(value.numeric)

    def test_catalog_separates_binary_arity_from_variadic_call_policy(self) -> None:
        for name in ("geometric_product", "outer_product"):
            operation = OPERATIONS[name]
            assert operation.arity == 2
            assert isinstance(operation.call_policy, LeftFoldCall)

    def test_every_core_public_name_is_cataloged_or_deliberately_excluded(
        self,
    ) -> None:
        core_public = set(core.__all__)
        classified_public = (set(OPERATIONS) & core_public) | set(EXCLUDED_PUBLIC_NAMES)

        assert core_public == classified_public
        assert set(OPERATIONS).isdisjoint(EXCLUDED_PUBLIC_NAMES)
        assert all(EXCLUDED_PUBLIC_NAMES.values())
        assert set(OPERATIONS) - core_public == {
            "add",
            "negate",
            "power",
            "scalar_divide",
            "scalar_multiply",
            "subtract",
        }

    def test_variadic_products_lower_to_deterministic_left_folds(self) -> None:
        algebra = Algebra(3)
        e1, e2, e3 = algebra.basis_vectors()

        assert geometric_product(e1) is e1
        assert outer_product(e1) is e1
        assert geometric_product(e1, e2, e3) == (e1 * e2) * e3
        assert outer_product(e1, e2, e3) == (e1 ^ e2) ^ e3

        with pytest.raises(TypeError, match="at least 1"):
            geometric_product()
        with pytest.raises(TypeError, match="at least 1"):
            outer_product()
