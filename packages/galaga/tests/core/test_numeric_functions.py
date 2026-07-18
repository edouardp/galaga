"""Numerical functions that cannot be reduced to finite algebraic helpers."""

from __future__ import annotations

import numpy as np
import pytest

from galaga.core import (
    Algebra,
    Multivector,
    exp,
    geometric_product,
    log,
    outercos,
    outerexp,
    outersin,
    outertan,
    scalar_sqrt,
    sqrt,
)


def taylor_exponential(value: Multivector, *, max_terms: int = 160) -> Multivector:
    """Evaluate an independent, unscaled geometric Taylor series."""
    result = value.algebra.identity
    term = value.algebra.identity
    for order in range(1, max_terms + 1):
        term = geometric_product(term, value) / order
        result = result + term
        if np.max(np.abs(term.data)) <= 1e-16:
            break
    return result


class TestSquareRoots:
    def test_scalar_sqrt_preserves_numeric_or_algebra_context(self) -> None:
        algebra = Algebra(2)

        assert scalar_sqrt(9) == 3.0
        assert scalar_sqrt(algebra.scalar(2)).almost_equal(algebra.scalar(np.sqrt(2)))

        with pytest.raises(ValueError, match="negative"):
            scalar_sqrt(-1)
        with pytest.raises(ValueError, match="finite"):
            scalar_sqrt(np.inf)
        with pytest.raises(ValueError, match="scalar multivector"):
            scalar_sqrt(algebra.basis_vectors()[0])
        with pytest.raises(TypeError, match="real number"):
            scalar_sqrt("4")  # type: ignore[arg-type]

        assert sqrt(4.0) == 2.0
        with pytest.raises(TypeError, match="real number"):
            sqrt("4")  # type: ignore[arg-type]

    def test_study_sqrt_handles_elliptic_and_hyperbolic_rotors(self) -> None:
        euclidean = Algebra(2)
        e1, e2 = euclidean.basis_vectors()
        elliptic = exp(0.7 * (e1 ^ e2))

        split = Algebra(1, 1)
        ep, en = split.basis_vectors()
        hyperbolic = exp(0.3 * (ep ^ en))

        for value in (elliptic, hyperbolic):
            root = sqrt(value)
            assert isinstance(root, type(value))
            assert (root * root).almost_equal(value)

    def test_study_sqrt_handles_a_null_pga_translator(self) -> None:
        pga = Algebra(2, 0, 1)
        e0, e1, _ = pga.basis_vectors()
        translator = pga.identity + 0.5 * (e0 ^ e1)

        root = sqrt(translator)

        assert not isinstance(root, float)
        assert (root * root).almost_equal(translator)
        assert root.almost_equal(pga.identity + 0.25 * (e0 ^ e1))

    def test_study_sqrt_rejects_unsupported_real_branches(self) -> None:
        algebra = Algebra(3)
        e1, e2, e3 = algebra.basis_vectors()
        non_study = 1 + e1 + (e1 ^ e2) + (e1 ^ e2 ^ e3)

        with pytest.raises(ValueError, match="Study number"):
            sqrt(non_study)
        with pytest.raises(ValueError, match="negative"):
            sqrt(algebra.scalar(-1))
        with pytest.raises(ValueError, match="singular"):
            sqrt(Algebra(1, 0, 1).basis_vectors()[0])

        positive = Algebra(1)
        ep = positive.basis_vectors()[0]
        with pytest.raises(ValueError, match="no square root in the real algebra"):
            sqrt(ep)
        with pytest.raises(ValueError, match="no principal real square root"):
            sqrt(-2 + ep)


class TestGeometricExponential:
    def test_scalar_and_scalar_square_closed_forms(self) -> None:
        positive = Algebra(1)
        ep = positive.basis_vectors()[0]
        negative = Algebra(0, 1)
        en = negative.basis_vectors()[0]
        degenerate = Algebra(1, 0, 1)
        e0 = degenerate.basis_vectors()[0]

        assert exp(positive.scalar(-1.5)).almost_equal(positive.scalar(np.exp(-1.5)))
        assert exp(0.7 * ep).almost_equal(positive.scalar(np.cosh(0.7)) + np.sinh(0.7) * ep)
        assert exp(0.7 * en).almost_equal(negative.scalar(np.cos(0.7)) + np.sin(0.7) * en)
        assert exp(0.7 * e0) == degenerate.identity + 0.7 * e0

    def test_general_series_handles_non_simple_and_mixed_inputs(self) -> None:
        algebra = Algebra(4)
        e1, e2, e3, e4 = algebra.basis_vectors()
        first = 0.3 * (e1 ^ e2)
        second = 0.5 * (e3 ^ e4)

        assert exp(first + second).almost_equal(exp(first) * exp(second))

        mixed = algebra.scalar(1) + 0.4 * e1
        expected = np.e * (algebra.scalar(np.cosh(0.4)) + np.sinh(0.4) * e1)
        assert exp(mixed).almost_equal(expected)

    def test_scalar_square_fast_path_is_native_gram_aware(self) -> None:
        algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, 1.5]]))
        vector = algebra.vector([0.3, -0.2])
        square = float(vector * vector)
        magnitude = np.sqrt(square)
        expected = algebra.scalar(np.cosh(magnitude)) + (np.sinh(magnitude) / magnitude) * vector

        assert exp(vector).almost_equal(expected)

    def test_general_series_agrees_across_general_gram_backends(self) -> None:
        gram = np.array([[2.0, 0.5], [0.5, -1.0]])
        results = []
        for backend in ("packed", "lazy", "reference"):
            algebra = Algebra(gram=gram, product_backend=backend)
            value = algebra.multivector([0.2, -0.3, 0.1, 0.4])
            results.append(exp(value).data)

        for result in results[1:]:
            assert np.allclose(result, results[0], rtol=0.0, atol=1e-13)

    @pytest.mark.parametrize(
        "case",
        (
            "nonsimple-euclidean-bivector",
            "sta-boost-plus-rotation",
            "nonsimple-trivector",
            "random-cl3-multivector",
            "random-sta-multivector",
            "oblique-multivector",
        ),
    )
    def test_general_exponential_matches_independent_taylor_series(
        self,
        case: str,
    ) -> None:
        if case == "nonsimple-euclidean-bivector":
            algebra = Algebra(4)
            e1, e2, e3, e4 = algebra.basis_vectors()
            value = 0.3 * (e1 ^ e2) + 0.5 * (e3 ^ e4)
        elif case == "sta-boost-plus-rotation":
            algebra = Algebra(1, 3)
            e0, e1, e2, e3 = algebra.basis_vectors()
            value = 0.4 * (e0 ^ e1) + 0.25 * (e2 ^ e3)
        elif case == "nonsimple-trivector":
            algebra = Algebra(5)
            e1, e2, e3, e4, e5 = algebra.basis_vectors()
            value = 0.2 * (e1 ^ e2 ^ e3) + 0.15 * (e1 ^ e4 ^ e5)
        elif case == "random-cl3-multivector":
            algebra = Algebra(3)
            value = algebra.multivector(0.3 * np.random.default_rng(500).standard_normal(algebra.dim))
        elif case == "random-sta-multivector":
            algebra = Algebra(1, 3)
            value = algebra.multivector(0.2 * np.random.default_rng(600).standard_normal(algebra.dim))
        else:
            algebra = Algebra(
                gram=np.array(
                    [
                        [2.0, 0.5, 0.0],
                        [0.5, 1.0, 0.25],
                        [0.0, 0.25, -1.5],
                    ]
                )
            )
            value = algebra.multivector(0.2 * np.random.default_rng(700).standard_normal(algebra.dim))

        np.testing.assert_allclose(
            exp(value).data,
            taylor_exponential(value).data,
            rtol=0.0,
            atol=2e-11,
        )

    def test_tiny_nonzero_generators_are_not_discarded(self) -> None:
        algebra = Algebra(2)
        e1, e2 = algebra.basis_vectors()
        generator = 1e-30 * (e1 ^ e2)

        assert exp(generator) == algebra.identity + generator

        algebra4 = Algebra(4)
        e1, e2, e3, e4 = algebra4.basis_vectors()
        nonsimple = 1e-30 * ((e1 ^ e2) + (e3 ^ e4))
        np.testing.assert_allclose(
            exp(nonsimple).data,
            (algebra4.identity + nonsimple).data,
            rtol=0.0,
            atol=1e-40,
        )

    def test_exp_rejects_non_multivectors(self) -> None:
        with pytest.raises(TypeError, match="Multivector"):
            exp(1.0)  # type: ignore[arg-type]


class TestRotorLogarithm:
    @pytest.mark.parametrize("kind", ["elliptic", "hyperbolic", "null"])
    def test_log_exp_roundtrip_for_each_generator_square(self, kind: str) -> None:
        if kind == "elliptic":
            algebra = Algebra(2)
            e1, e2 = algebra.basis_vectors()
            generator = 0.7 * (e1 ^ e2)
        elif kind == "hyperbolic":
            algebra = Algebra(1, 1)
            ep, en = algebra.basis_vectors()
            generator = 0.3 * (ep ^ en)
        else:
            algebra = Algebra(2, 0, 1)
            e0, e1, _ = algebra.basis_vectors()
            generator = 0.4 * (e0 ^ e1)

        assert log(exp(generator)).almost_equal(generator)

    def test_log_roundtrip_works_in_an_oblique_basis(self) -> None:
        algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, 1.5]]))
        e1, e2 = algebra.basis_vectors()
        unit_plane = (e1 ^ e2) / np.sqrt(np.linalg.det(algebra.gram))
        generator = 0.37 * unit_plane

        assert log(exp(generator)).almost_equal(generator)

    def test_log_validates_its_real_study_rotor_domain(self) -> None:
        algebra = Algebra(4)
        e1, e2, e3, e4 = algebra.basis_vectors()
        general_rotor = exp(0.3 * (e1 ^ e2) + 0.5 * (e3 ^ e4))

        with pytest.raises(ValueError, match="normalized rotor"):
            log(e1)
        with pytest.raises(ValueError, match="Study-number rotor"):
            log(general_rotor)
        with pytest.raises(ValueError, match="undefined without a plane"):
            log(-algebra.identity)

        with pytest.raises(TypeError, match="Multivector"):
            log(1.0)  # type: ignore[arg-type]

        assert log(algebra.identity) == 0

    def test_log_rejects_real_branches_outside_its_principal_domain(self) -> None:
        pga = Algebra(2, 0, 1)
        e0, e1, _ = pga.basis_vectors()
        negative_translator = -pga.identity + 0.25 * (e0 ^ e1)
        with pytest.raises(ValueError, match=r"scalar part \+1"):
            log(negative_translator)

        split = Algebra(1, 1)
        ep, en = split.basis_vectors()
        negative_boost = -exp(0.3 * (ep ^ en))
        with pytest.raises(ValueError, match="principal real branch"):
            log(negative_boost)


class TestOuterTranscendentals:
    def test_one_dimensional_outer_series_reaches_top_grade(self) -> None:
        algebra = Algebra(1)
        vector = algebra.basis_vectors()[0]

        assert outerexp(vector) == 1 + vector

    def test_non_simple_bivector_series_terminates_by_dimension(self) -> None:
        algebra = Algebra(4)
        e1, e2, e3, e4 = algebra.basis_vectors()
        bivector = (e1 ^ e2) + (e3 ^ e4)
        expected = algebra.identity + bivector + (bivector ^ bivector) / 2

        assert outerexp(bivector) == expected
        assert outerexp(bivector).almost_equal(outercos(bivector) + outersin(bivector))

    def test_scalar_part_uses_the_infinite_scalar_series_exactly(self) -> None:
        algebra = Algebra(2)
        e1, _ = algebra.basis_vectors()
        value = algebra.scalar(0.4) + e1

        assert outerexp(value).almost_equal(np.exp(0.4) * (1 + e1))
        assert outercos(value).almost_equal(algebra.scalar(np.cosh(0.4)) + np.sinh(0.4) * e1)
        assert outersin(value).almost_equal(algebra.scalar(np.sinh(0.4)) + np.cosh(0.4) * e1)

    def test_outer_series_is_metric_independent(self) -> None:
        diagonal = Algebra(3)
        oblique = Algebra(gram=np.array([[2.0, 0.5, 0.0], [0.5, 1.0, 0.2], [0.0, 0.2, -1.0]]))
        data = np.arange(diagonal.dim, dtype=np.float64) / 10
        diagonal_value = diagonal.multivector(data)
        oblique_value = oblique.multivector(data)

        assert np.array_equal(
            outerexp(diagonal_value).data,
            outerexp(oblique_value).data,
        )

    def test_outertan_is_the_quotient_and_reports_noninvertibility(self) -> None:
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        simple = e1 ^ e2

        assert outertan(simple) == simple

        algebra4 = Algebra(4)
        f1, f2, f3, f4 = algebra4.basis_vectors()
        zero_divisor_cosine = (f1 ^ f2) + (f3 ^ f4)
        with pytest.raises(ValueError, match="not invertible"):
            outertan(zero_divisor_cosine)

    @pytest.mark.parametrize("function", [outerexp, outersin, outercos, outertan])
    def test_outer_functions_reject_non_multivectors(self, function) -> None:
        with pytest.raises(TypeError, match="Multivector"):
            function(1.0)
