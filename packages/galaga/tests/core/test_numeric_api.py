"""Pure numeric compatibility operations layered on the product backends."""

from __future__ import annotations

import numpy as np
import pytest

from galaga.core import (
    Algebra,
    anticommutator,
    commutator,
    conjugate,
    even_grades,
    grade,
    grade_involution,
    grades,
    half_anticommutator,
    half_commutator,
    inverse,
    is_basis_blade,
    is_bivector,
    is_even,
    is_rotor,
    is_scalar,
    is_vector,
    jordan_product,
    lie_bracket,
    norm,
    norm2,
    odd_grades,
    sandwich,
    squared,
    unit,
)


class TestGradeDecomposition:
    def test_single_multiple_and_parity_projections(self) -> None:
        algebra = Algebra(3)
        e1, e2, e3 = algebra.basis_vectors()
        value = 3 + 2 * e1 - e2 + 4 * (e1 ^ e3) + algebra.I

        assert grade(value, 0) == 3
        assert value[1] == 2 * e1 - e2
        assert grades(value, [0, 2]) == 3 + 4 * (e1 ^ e3)
        assert grade(value, "even") == even_grades(value)
        assert value["odd"] == odd_grades(value)
        assert even_grades(value) + odd_grades(value) == value

        assert grade(value, -1) == 0
        assert grade(value, 99) == 0
        assert grades(value, [-1, 1, 99]) == grade(value, 1)

    def test_projection_validation_is_explicit(self) -> None:
        value = Algebra(2).scalar(1)

        with pytest.raises(TypeError, match="integer, 'even', or 'odd'"):
            grade(value, "middle")
        with pytest.raises(TypeError, match="iterable"):
            grades(value, 1)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="every grade"):
            grades(value, [0, 1.5])  # type: ignore[list-item]


class TestInvolutions:
    def test_grade_signs_and_convenience_properties(self) -> None:
        algebra = Algebra(4)
        e1, e2, e3, e4 = algebra.basis_vectors()
        scalar = algebra.scalar(2)
        vector = e1
        bivector = e1 ^ e2
        trivector = e1 ^ e2 ^ e3
        pseudoscalar = e1 ^ e2 ^ e3 ^ e4

        for value, reverse_sign, involute_sign, conjugate_sign in (
            (scalar, 1, 1, 1),
            (vector, 1, -1, -1),
            (bivector, -1, 1, -1),
            (trivector, -1, -1, 1),
            (pseudoscalar, 1, 1, 1),
        ):
            assert value.dag == reverse_sign * value
            assert grade_involution(value) == involute_sign * value
            assert value.bar == conjugate_sign * value

    def test_automorphism_laws_hold_in_a_nonorthogonal_basis(self) -> None:
        algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, -1.0]]))
        e1, e2 = algebra.basis_vectors()
        left = 1 + 2 * e1 + (e1 ^ e2)
        right = -2 + e2 - 0.25 * (e1 ^ e2)

        assert grade_involution(left * right).almost_equal(grade_involution(left) * grade_involution(right))
        assert conjugate(left * right).almost_equal(conjugate(right) * conjugate(left))


class TestMultivectorConveniences:
    def test_zero_dimensional_algebra_is_the_scalar_algebra(self) -> None:
        algebra = Algebra(0)
        value = algebra.scalar(3)

        assert algebra.n == 0
        assert algebra.dim == 1
        assert algebra.signature == ()
        assert algebra.inertia == (0, 0, 0)
        assert algebra.metric_rank == 0
        assert algebra.metric_determinant == 1
        assert not algebra.is_degenerate
        assert algebra.basis_vectors() == ()
        assert algebra.I == algebra.identity
        assert value * value == 9
        assert inverse(value) == algebra.scalar(1 / 3)

    def test_vector_factory_and_value_inspection(self) -> None:
        algebra = Algebra(3)
        vector = algebra.vector([1, -2, 0.5])
        e1, e2, e3 = algebra.basis_vectors()

        assert vector == e1 - 2 * e2 + 0.5 * e3
        assert np.array_equal(vector.vector_part, [1, -2, 0.5])
        copied = vector.vector_part
        copied[0] = 99
        assert vector.coefficient(1) == 1
        assert vector.homogeneous_grade() == 1
        assert (2 + vector).homogeneous_grade() is None
        assert algebra.scalar(0).homogeneous_grade() is None

        with pytest.raises(ValueError, match=r"shape \(3,\)"):
            algebra.vector([1, 2])

    def test_float_abs_hash_and_named_properties(self) -> None:
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        scalar = algebra.scalar(-3.5)
        bivector = e1 ^ e2

        assert float(scalar) == -3.5
        assert np.float64(scalar) == np.float64(-3.5)
        assert abs(scalar) == 3.5
        assert float(algebra.scalar(0)) == 0
        assert hash(scalar) == hash(algebra.scalar(-3.5))
        assert bivector.sq == squared(bivector)
        assert bivector.dag == ~bivector
        assert not hasattr(type(scalar), "__array__")
        assert not hasattr(type(scalar), "__array_ufunc__")

        with pytest.raises(TypeError, match="grade-2"):
            float(bivector)
        with pytest.raises(TypeError, match="mixed-grade"):
            float(1 + bivector)

    def test_powers_inverse_and_multivector_division(self) -> None:
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        value = 2 + 0.25 * e1 + 0.5 * (e1 ^ e2)

        assert value**0 == algebra.identity
        assert value**2 == value * value
        assert value**3 == value * value * value
        assert (value * value.inv).almost_equal(algebra.identity)
        assert (value**-1).almost_equal(inverse(value))
        assert (value / value).almost_equal(algebra.identity)
        assert (3 / value).almost_equal(3 * inverse(value))
        assert (value / algebra.scalar(2)).almost_equal(value / 2)


class TestDerivedProducts:
    def test_full_and_half_brackets_have_explicit_scaling(self) -> None:
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()

        assert commutator(e1, e2) == 2 * (e1 ^ e2)
        assert anticommutator(e1, e1) == 2
        assert half_commutator(e1, e2) == e1 ^ e2
        assert half_anticommutator(e1, e1) == 1
        assert lie_bracket(e1, e2) == commutator(e1, e2)
        assert jordan_product(e1, e1) == anticommutator(e1, e1)
        assert half_commutator(e1, e2) + half_anticommutator(e1, e2) == e1 * e2

    def test_vector_half_anticommutator_is_the_gram_pairing(self) -> None:
        algebra = Algebra(gram=np.array([[2.0, 0.75], [0.75, -1.0]]))
        e1, e2 = algebra.basis_vectors()

        assert anticommutator(e1, e2) == 1.5
        assert half_anticommutator(e1, e2) == 0.75

    def test_norm_unit_and_rotor_predicates(self) -> None:
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        vector = 3 * e1 + 4 * e2
        rotor = (1 - (e1 ^ e2)) / np.sqrt(2)

        assert norm2(vector) == 25
        assert norm(vector) == pytest.approx(5)
        assert norm(unit(vector)) == pytest.approx(1)
        assert is_rotor(rotor)
        assert sandwich(rotor, e1).almost_equal(e2)

        with pytest.raises(ValueError, match="near-zero"):
            unit(algebra.scalar(0))

    def test_norm_retains_indefinite_and_degenerate_information(self) -> None:
        sta = Algebra(1, 1)
        timelike, spacelike = sta.basis_vectors()
        pga = Algebra(1, 0, 1)
        null, _ = pga.basis_vectors()

        assert norm2(timelike) == 1
        assert norm2(spacelike) == -1
        assert norm(spacelike) == 1
        assert norm2(null) == 0

    def test_inverse_works_in_oblique_and_degenerate_algebras(self) -> None:
        oblique = Algebra(gram=np.array([[2.0, 0.5], [0.5, 1.0]]))
        e1, e2 = oblique.basis_vectors()
        value = 1 + 0.2 * e1 - 0.3 * e2 + 0.1 * (e1 ^ e2)
        candidate = inverse(value)

        assert (value * candidate).almost_equal(oblique.identity)
        assert (candidate * value).almost_equal(oblique.identity)

        pga = Algebra(1, 0, 1)
        null, _ = pga.basis_vectors()
        with pytest.raises(ValueError, match="not invertible"):
            inverse(null)

    @pytest.mark.parametrize(
        "signature",
        (
            (),
            (1,),
            (1, 1),
            (1, 1, 1),
            (1, -1, -1, -1),
            (1, 1, 1, 1, 1),
            (1, 1, 1, -1, -1, -1),
        ),
        ids=("Cl0", "Cl1", "Cl2", "Cl3", "STA", "Cl5", "Cl33"),
    )
    def test_general_inverse_is_two_sided_across_dimensions(
        self,
        signature: tuple[int, ...],
    ) -> None:
        algebra = Algebra(0) if not signature else Algebra(signature=signature)
        rng = np.random.default_rng(900 + algebra.n)
        data = 0.03 * rng.standard_normal(algebra.dim)
        data[0] += 2.0
        value = algebra.multivector(data)
        candidate = inverse(value)

        assert (value * candidate).almost_equal(algebra.identity)
        assert (candidate * value).almost_equal(algebra.identity)
        assert inverse(candidate).almost_equal(value)

    def test_grade_predicates(self) -> None:
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        bivector = e1 ^ e2

        assert is_scalar(algebra.scalar(3))
        assert is_vector(e1 + 2 * e2)
        assert is_bivector(bivector)
        assert is_even(1 + bivector)
        assert is_basis_blade(-3 * bivector)
        assert not is_scalar(e1)
        assert not is_vector(1 + e1)
        assert not is_bivector(e1)
        assert not is_even(e1)
        assert not is_basis_blade(e1 + e2)
