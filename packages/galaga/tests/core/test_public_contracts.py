"""Public boundary contracts whose failure would create ambiguous GA values."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest

from galaga.core import (
    Algebra,
    Multivector,
    antidot_product,
    antimetric_apply,
    antireverse,
    complement,
    conjugate,
    doran_lasenby_inner,
    dual,
    even_grades,
    geometric_antiproduct,
    geometric_product,
    grade,
    grades,
    inverse,
    involute,
    is_basis_blade,
    is_bivector,
    is_even,
    is_scalar,
    is_vector,
    left_interior_product,
    metric_apply,
    metric_inner_product,
    norm2,
    odd_grades,
    outer_product,
    reverse,
    right_interior_product,
    scalar_product,
    squared,
    transwedge_antiproduct,
    uncomplement,
    undual,
)


class TestConstructionAndInspectionBoundaries:
    def test_multivector_shape_and_blade_indices_are_checked(self) -> None:
        """A coefficient array or mask must identify one unambiguous value."""
        algebra = Algebra(3)
        value = algebra.identity

        with pytest.raises(ValueError, match=r"shape \(8,\)"):
            algebra.multivector([1, 2])
        with pytest.raises(TypeError, match="bitmask must be an integer"):
            value.coefficient(True)
        with pytest.raises(ValueError, match=r"\[0, 8\)"):
            value.coefficient(8)
        with pytest.raises(TypeError, match="bitmask must be an integer"):
            algebra.blade(1.5)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match=r"\[0, 8\)"):
            algebra.blade(-1)

    def test_basis_blades_enumerate_exactly_one_requested_grade(self) -> None:
        """The factory is stricter than projection and preserves mask order."""
        algebra = Algebra(4)
        bivectors = algebra.basis_blades(2)

        assert len(bivectors) == 6
        assert [int(np.flatnonzero(value.data)[0]) for value in bivectors] == [
            3,
            5,
            6,
            9,
            10,
            12,
        ]
        assert all(value.homogeneous_grade() == 2 for value in bivectors)

        with pytest.raises(TypeError, match="grade must be an integer"):
            algebra.basis_blades(True)
        with pytest.raises(ValueError, match=r"\[0, 4\]"):
            algebra.basis_blades(5)

    def test_factories_reject_inputs_without_a_well_defined_real_value(self) -> None:
        """Construction must not guess a metric, scalar type, or coefficients."""
        with pytest.raises(TypeError, match="provide p"):
            Algebra()

        algebra = Algebra(2)
        with pytest.raises(TypeError, match="scalar value must be real"):
            algebra.scalar("1")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="real numeric values"):
            algebra.vector(["left", "right"])
        with pytest.raises(TypeError, match="one-dimensional"):
            Algebra(signature=[[1, -1]])
        with pytest.raises(TypeError, match="two-dimensional"):
            Algebra(gram=[1, -1])
        with pytest.raises(TypeError, match="q must be an integer"):
            Algebra(2, q=1.0)  # type: ignore[arg-type]

    def test_backend_diagnostics_and_left_action_have_stable_boundaries(
        self,
    ) -> None:
        """Diagnostics distinguish non-cached backends and reject raw arrays."""
        algebra = Algebra(2)

        assert algebra.product_cache_info is None
        with pytest.raises(TypeError, match="left_action expects a Multivector"):
            algebra.left_action(np.ones(algebra.dim))  # type: ignore[arg-type]


class TestPythonProtocolAndConvenienceSurface:
    def test_methods_and_named_functions_share_the_same_semantics(self) -> None:
        """Method spellings are conveniences, never separate implementations."""
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        value = 2 + e1 + (e1 ^ e2)

        assert value.grade(1) == grade(value, 1)
        assert value.geometric_product(e2) == geometric_product(value, e2)
        assert value.outer_product(e2) == outer_product(value, e2)
        assert value.doran_lasenby_inner(e2) == doran_lasenby_inner(value, e2)
        assert +value is value

    def test_real_scalars_participate_in_documented_outer_and_inner_operators(
        self,
    ) -> None:
        """Both operand orders must coerce scalars into the owning algebra."""
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        bivector = e1 ^ e2

        assert (bivector ^ 2) == 2 * bivector
        assert (2 ^ bivector) == 2 * bivector
        assert (bivector | 2) == 2 * bivector
        assert (2 | bivector) == 2 * bivector

    @pytest.mark.parametrize(
        "expression",
        [
            lambda value, bad: value + bad,
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
        ],
        ids=(
            "add",
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
    def test_unsupported_python_operands_return_control_to_the_protocol(
        self,
        expression: Callable[[Multivector, object], object],
    ) -> None:
        """Unsupported operands must become normal Python `TypeError`s."""
        value = Algebra(2).identity

        with pytest.raises(TypeError):
            expression(value, object())

    def test_division_reports_both_forms_of_zero_scalar(self) -> None:
        value = Algebra(2).identity

        with pytest.raises(ZeroDivisionError, match="by zero"):
            _ = value / 0
        with pytest.raises(ZeroDivisionError, match="zero scalar multivector"):
            _ = value / value.algebra.scalar(0)

    def test_equality_with_unrelated_values_is_false(self) -> None:
        assert Algebra(2).identity != object()


UNARY_MULTIVECTOR_OPERATIONS = (
    metric_apply,
    antimetric_apply,
    reverse,
    involute,
    conjugate,
    complement,
    uncomplement,
    antireverse,
    dual,
    undual,
    squared,
    norm2,
    inverse,
    is_scalar,
    is_vector,
    is_bivector,
    is_even,
    is_basis_blade,
)

BINARY_MULTIVECTOR_OPERATIONS = (
    geometric_product,
    outer_product,
    scalar_product,
    metric_inner_product,
    antidot_product,
    geometric_antiproduct,
    left_interior_product,
    right_interior_product,
)


class TestNamedOperationTypeBoundary:
    @pytest.mark.parametrize(
        "operation",
        UNARY_MULTIVECTOR_OPERATIONS,
        ids=lambda operation: operation.__name__,
    )
    def test_unary_named_operations_do_not_guess_an_algebra(
        self,
        operation: Callable[[Multivector], object],
    ) -> None:
        """A raw number has no metric or exterior dimension to inherit."""
        with pytest.raises(TypeError, match="Multivector"):
            operation(1.0)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "operation",
        BINARY_MULTIVECTOR_OPERATIONS,
        ids=lambda operation: operation.__name__,
    )
    def test_binary_named_operations_require_explicit_multivectors(
        self,
        operation: Callable[[Multivector, Multivector], Multivector],
    ) -> None:
        """Named operations stay stricter than scalar-coercing operators."""
        value = Algebra(2).identity
        with pytest.raises(TypeError, match="Multivector"):
            operation(value, 1.0)  # type: ignore[arg-type]

    def test_grade_families_require_an_owned_multivector(self) -> None:
        with pytest.raises(TypeError, match="grade expects a Multivector"):
            grade(1.0, 0)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="grades expects a Multivector"):
            grades(1.0, [0])  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="even_grades expects a Multivector"):
            even_grades(1.0)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="odd_grades expects a Multivector"):
            odd_grades(1.0)  # type: ignore[arg-type]

    def test_antiproduct_order_family_requires_explicit_multivectors(self) -> None:
        value = Algebra(2).identity
        with pytest.raises(TypeError, match="two Multivectors"):
            transwedge_antiproduct(value, 1.0, 0)  # type: ignore[arg-type]

    def test_undual_fails_directly_for_a_degenerate_metric(self) -> None:
        """The inverse-pseudoscalar dual family must not hide a complement."""
        pga = Algebra(2, 0, 1)
        with pytest.raises(ValueError, match="invertible pseudoscalar"):
            undual(pga.identity)
