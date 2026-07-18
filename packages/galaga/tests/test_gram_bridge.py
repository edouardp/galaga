"""Numeric parity tests for the opt-in core-backed facade."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest

import galaga.gram_bridge as bridge
from galaga import core
from galaga.gram_bridge import (
    EXCLUDED_PUBLIC_NAMES,
    OPERATIONS,
    Algebra,
    LeftFoldCall,
    Multivector,
    OperationSpec,
    geometric_product,
    get_operation,
    grade,
    grade_involution,
    involute,
    outer_product,
    scalar_part,
)


@pytest.fixture(autouse=True)
def forbid_legacy_numeric_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make every direct facade test fail if it falls back to the v1 engine."""
    import galaga.algebra as legacy

    def reject(*args: object, **kwargs: object) -> None:
        raise AssertionError("Gram facade test constructed galaga.algebra.Algebra")

    monkeypatch.setattr(legacy.Algebra, "__init__", reject)


def test_legacy_numeric_constructor_guard_is_active() -> None:
    import galaga.algebra as legacy

    with pytest.raises(AssertionError, match="Gram facade test constructed"):
        legacy.Algebra(2)


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
        assert algebra.blade(3) == first[0] ^ first[1]

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

    def test_forwards_metric_identity_and_backend_diagnostics(self) -> None:
        algebra = Algebra(2, 1, id="cl21")

        assert algebra.id == "cl21"
        assert algebra.basis_squares.tolist() == [1.0, 1.0, -1.0]
        assert algebra.metric_rank == 3
        assert algebra.metric_determinant == -1.0
        assert not algebra.is_degenerate
        assert algebra.product_backend == "diagonal"
        assert algebra.packed_product_byte_estimate > 0
        assert algebra.product_cache_info is None
        assert algebra.left_action(algebra.identity).shape == (algebra.dim, algebra.dim)
        assert algebra.extended_metric_matrix().shape == (algebra.dim, algebra.dim)
        assert algebra.metric_antiexomorphism_matrix().shape == (algebra.dim, algebra.dim)
        assert "Algebra(numeric=" in repr(algebra)

    def test_from_numeric_defines_equivalent_and_distinct_ownership(self) -> None:
        numeric = core.Algebra(2)
        left_algebra = Algebra.from_numeric(numeric)
        right_algebra = Algebra.from_numeric(numeric)
        left = left_algebra.basis_vectors()[0]
        right = right_algebra.basis_vectors()[0]

        result = geometric_product(left, right)

        assert result.algebra is left_algebra
        assert result == 1
        with pytest.raises(TypeError, match="core.Algebra"):
            Algebra.from_numeric(object())  # type: ignore[arg-type]

        distinct = Algebra(2).basis_vectors()[0]
        with pytest.raises(ValueError, match="different algebras"):
            geometric_product(left, distinct)

    def test_construction_and_linear_action_reject_ambiguous_owners(self) -> None:
        algebra = Algebra(2)
        other = Algebra(2)

        with pytest.raises(ValueError, match="symmetric"):
            Algebra(gram=[[1, 2], [0, 1]])
        with pytest.raises(ValueError, match="shape"):
            algebra.multivector([1, 2])
        with pytest.raises(TypeError, match="facade Algebra"):
            Multivector(object(), algebra.identity.numeric)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="core.Multivector"):
            Multivector(algebra, object())  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="different algebra"):
            Multivector(algebra, other.identity.numeric)
        with pytest.raises(TypeError, match="facade Multivector"):
            algebra.left_action(np.ones(algebra.dim))  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="different numeric algebra"):
            algebra.left_action(other.identity)

    def test_value_inspection_equality_hashing_and_repr(self) -> None:
        numeric = core.Algebra(2)
        first_algebra = Algebra.from_numeric(numeric)
        second_algebra = Algebra.from_numeric(numeric)
        first = first_algebra.multivector([1.0, 2.0, 0.0, 0.0])
        same = second_algebra.multivector([1.0, 2.0, 0.0, 0.0])
        near = second_algebra.multivector([1.0, 2.0 + 1e-13, 0.0, 0.0])

        assert first.coefficient(1) == 2.0
        assert first.vector_part.tolist() == [2.0, 0.0]
        assert first.homogeneous_grade() is None
        assert first.grade(1) == grade(first, 1)
        assert first == same
        assert hash(first) == hash(same)
        assert first != near
        assert first.almost_equal(near)
        assert not first.almost_equal(Algebra(2).identity)
        assert first != object()
        assert first_algebra.scalar(2) == 2
        assert abs(first_algebra.scalar(-2)) == 2
        assert "Multivector(numeric=" in repr(first)


class TestPythonProtocolBoundary:
    def test_supported_scalar_positions_and_multivector_division(self) -> None:
        algebra = Algebra(2)
        e1, e2 = algebra.basis_vectors()
        value = 1 + e1

        assert 2 + value == value + 2
        assert 2 - value == -(value - 2)
        assert 2 * value == value * 2
        assert value / 2 == 0.5 * value
        assert value / algebra.scalar(2) == 0.5 * value
        assert value / e1 == value * e1
        assert 2 / e1 == 2 * e1
        assert value ^ 2 == 2 * value
        assert 2 ^ value == 2 * value
        assert value | 2 == 2 * value
        assert 2 | value == 2 * value
        assert value**2 == value * value
        assert -(e1 * e2) == (-1) * (e1 * e2)

    @pytest.mark.parametrize(
        "expression",
        (
            lambda value, bad: value + bad,
            lambda value, bad: bad + value,
            lambda value, bad: value - bad,
            lambda value, bad: bad - value,
            lambda value, bad: value * bad,
            lambda value, bad: bad * value,
            lambda value, bad: value / bad,
            lambda value, bad: bad / value,
            lambda value, bad: value**bad,
            lambda value, bad: value ^ bad,
            lambda value, bad: bad ^ value,
            lambda value, bad: value | bad,
            lambda value, bad: bad | value,
        ),
        ids=(
            "add",
            "reflected-add",
            "subtract",
            "reflected-subtract",
            "multiply",
            "reflected-multiply",
            "divide",
            "reflected-divide",
            "power",
            "outer",
            "reflected-outer",
            "inner",
            "reflected-inner",
        ),
    )
    def test_unsupported_operands_return_control_to_python(
        self,
        expression: Callable[[Multivector, object], object],
    ) -> None:
        with pytest.raises(TypeError):
            expression(Algebra(2).identity, object())

    def test_scalar_and_multivector_zero_division_remain_distinct(self) -> None:
        algebra = Algebra(2)

        with pytest.raises(ZeroDivisionError, match="by zero"):
            _ = algebra.identity / 0
        with pytest.raises(ZeroDivisionError, match="zero scalar multivector"):
            _ = algebra.identity / algebra.scalar(0)
        with pytest.raises(ValueError, match="different algebras"):
            _ = algebra.identity / Algebra(2).identity


class TestCatalogAndParity:
    def test_catalog_metadata_and_lookup_validate_the_public_call_contract(self) -> None:
        identity = core.Algebra(2).identity

        with pytest.raises(ValueError, match="must not be empty"):
            OperationSpec("", 1, lambda value: value)
        with pytest.raises(ValueError, match="must be positive"):
            OperationSpec("invalid", 0, lambda: None)
        with pytest.raises(KeyError, match="unknown core facade operation"):
            get_operation("missing")
        with pytest.raises(TypeError, match="expects 2 positional arguments"):
            get_operation("grade").invoke(identity)
        with pytest.raises(TypeError, match="does not accept fold keywords"):
            get_operation("geometric_product").invoke(identity, identity, unexpected=True)
        with pytest.raises(TypeError):
            OPERATIONS["missing"] = get_operation("reverse")  # type: ignore[index]

    @pytest.mark.parametrize(
        "operation_name",
        (
            "geometric_product",
            "outer_product",
            "scalar_product",
            "metric_inner_product",
            "antidot_product",
            "left_contraction",
            "right_contraction",
            "hestenes_inner",
            "doran_lasenby_inner",
            "commutator",
            "anticommutator",
            "half_commutator",
            "half_anticommutator",
            "lie_bracket",
            "jordan_product",
            "regressive_product",
            "antiwedge",
            "metric_regressive_product",
            "geometric_antiproduct",
            "left_interior_product",
            "right_interior_product",
            "sandwich",
        ),
    )
    def test_binary_operation_matches_direct_gram_evaluation(
        self,
        operation_name: str,
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

        result = getattr(bridge, operation_name)(left, right)
        expected = getattr(core, operation_name)(left.numeric, right.numeric)

        assert result.numeric.algebra is algebra.numeric
        np.testing.assert_allclose(
            result.data,
            expected.data,
            rtol=0.0,
            atol=1e-12,
        )

    @pytest.mark.parametrize(
        "operation_name",
        (
            "antimetric_apply",
            "antireverse",
            "bulk_part",
            "complement",
            "conjugate",
            "dual",
            "even_grades",
            "exp",
            "grade_involution",
            "inverse",
            "is_basis_blade",
            "is_bivector",
            "is_even",
            "is_rotor",
            "is_scalar",
            "is_vector",
            "left_complement",
            "left_hodge_dual",
            "left_weight_dual",
            "metric_apply",
            "norm",
            "norm2",
            "odd_grades",
            "outercos",
            "outerexp",
            "outersin",
            "outertan",
            "reverse",
            "right_complement",
            "right_hodge_dual",
            "right_weight_dual",
            "squared",
            "uncomplement",
            "undual",
            "unit",
            "weight_part",
        ),
    )
    def test_unary_operation_matches_direct_oblique_gram_evaluation(self, operation_name: str) -> None:
        algebra = Algebra(
            gram=np.array(
                [
                    [2.0, 0.5, -0.25],
                    [0.5, 1.5, 0.25],
                    [-0.25, 0.25, 1.0],
                ]
            )
        )
        coefficients = 0.03 * (np.arange(algebra.dim) - 2)
        coefficients[0] += 1.0
        value = algebra.multivector(coefficients)

        result = getattr(bridge, operation_name)(value)
        expected = getattr(core, operation_name)(value.numeric)

        if isinstance(result, Multivector):
            assert isinstance(expected, core.Multivector)
            np.testing.assert_allclose(result.data, expected.data, rtol=0.0, atol=1e-12)
        elif isinstance(result, float):
            assert np.isclose(result, expected, rtol=0.0, atol=1e-12)
        else:
            assert result == expected

    @pytest.mark.parametrize("operation_name", ("log", "sqrt"))
    def test_study_number_operation_matches_direct_oblique_gram_evaluation(self, operation_name: str) -> None:
        algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, 1.0]]))
        e1, e2 = algebra.basis_vectors()
        value = bridge.exp(0.2 * (e1 ^ e2))

        result = getattr(bridge, operation_name)(value)
        expected = getattr(core, operation_name)(value.numeric)

        assert isinstance(result, Multivector)
        assert isinstance(expected, core.Multivector)
        np.testing.assert_allclose(result.data, expected.data, rtol=0.0, atol=1e-12)

    def test_scalar_sqrt_matches_direct_core_for_plain_and_owned_values(self) -> None:
        algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, 1.0]]))

        assert bridge.scalar_sqrt(9.0) == core.scalar_sqrt(9.0)
        result = bridge.scalar_sqrt(algebra.scalar(9))
        expected = core.scalar_sqrt(algebra.scalar(9).numeric)

        assert isinstance(result, Multivector)
        assert isinstance(expected, core.Multivector)
        assert result.data.tolist() == expected.data.tolist()

    @pytest.mark.parametrize(
        ("operation_name", "value"), (("inverse", 0.0), ("unit", 0.0), ("log", -1.0), ("sqrt", -1.0))
    )
    def test_numeric_domain_errors_are_preserved(self, operation_name: str, value: float) -> None:
        algebra = Algebra(2)
        facade_value = algebra.scalar(value)

        with pytest.raises(ValueError) as facade_error:
            getattr(bridge, operation_name)(facade_value)
        with pytest.raises(ValueError) as core_error:
            getattr(core, operation_name)(facade_value.numeric)

        assert str(facade_error.value) == str(core_error.value)

    def test_parameterized_operations_match_direct_oblique_gram_evaluation(self) -> None:
        algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, 1.0]]))
        left = algebra.multivector(np.arange(algebra.dim) - 1)
        right = algebra.multivector(np.arange(algebra.dim)[::-1] - 2)

        cases = (
            (bridge.grade(left, 2), core.grade(left.numeric, 2)),
            (bridge.grades(left, [0, 2]), core.grades(left.numeric, [0, 2])),
            (bridge.transwedge(left, right, 1), core.transwedge(left.numeric, right.numeric, 1)),
            (
                bridge.transwedge_antiproduct(left, right, 1),
                core.transwedge_antiproduct(left.numeric, right.numeric, 1),
            ),
        )
        for result, expected in cases:
            np.testing.assert_allclose(result.data, expected.data, rtol=0.0, atol=1e-12)

    def test_catalog_separates_binary_arity_from_variadic_call_policy(self) -> None:
        for name in ("geometric_product", "outer_product"):
            operation = OPERATIONS[name]
            assert operation.arity == 2
            assert isinstance(operation.call_policy, LeftFoldCall)

    def test_grade_involution_is_the_canonical_catalog_operation(self) -> None:
        assert get_operation("grade_involution").evaluate is core.grade_involution
        assert "involute" not in OPERATIONS
        assert involute is grade_involution

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
