"""Algebra-law tests for the Gram-native multivector prototype.

The tests are organized as a mathematical proof ladder:

1. storage and Python operators create immutable multivectors;
2. every basis-vector pair satisfies the Clifford relation supplied by its
   algebra's Gram matrix;
3. geometric and exterior products satisfy their general algebra laws;
4. familiar low-dimensional, STA, PGA, and CGA identities hold; and
5. native-null CGA is exhaustively equivalent to orthogonal CGA under the
   documented change of basis.

This ordering matters. Model-specific identities are persuasive only after the
generic metric consistency and associativity tests establish that the product
engine is coherent for every requested algebra.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pytest

from galaga.core import (
    Algebra,
    Multivector,
    geometric_product,
    grade,
    outer_product,
    reverse,
    scalar_product,
)

# One documented root seed makes every random-looking test reproducible. Each
# property test adds a small offset so it receives a distinct deterministic
# stream, while ``algebra.n`` distinguishes dimensions. Algebras of the same
# dimension intentionally receive the same coefficients, which makes their
# different metric behavior easier to compare.
RNG_SEED = 42


def native_cga_gram() -> np.ndarray:
    """The normalized ``(e1,e2,e3,eo,einf)`` Gram matrix."""
    return np.array(
        [
            [1, 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, -1],
            [0, 0, 0, -1, 0],
        ],
        dtype=np.float64,
    )


REQUESTED_ALGEBRAS = [
    Algebra(2, id="cl2-euclidean"),
    Algebra(3, id="cl3-euclidean"),
    Algebra(1, 3, id="sta-cl13"),
    Algebra(3, 0, 1, id="pga-cl301"),
    Algebra(4, id="cl4-euclidean"),
    Algebra(4, 1, id="cga-orthogonal-cl41"),
    Algebra(gram=native_cga_gram(), id="cga-native-null"),
]


def assert_mv_close(
    actual: Multivector,
    expected: Multivector | float | int,
    *,
    atol: float = 1e-11,
) -> None:
    """Compare multivectors without hiding an algebra mismatch.

    NumPy tolerances are appropriate because the rotor, boost, and symmetric
    null-pair tests introduce square roots and hyperbolic functions. Requiring
    object identity of the parent algebra remains exact: equal coefficient
    arrays from different product systems are not interchangeable values.
    """
    if not isinstance(expected, Multivector):
        expected = actual.algebra.scalar(expected)
    assert actual.algebra is expected.algebra
    np.testing.assert_allclose(actual.data, expected.data, rtol=0.0, atol=atol)


def random_multivector(algebra: Algebra, rng: np.random.Generator) -> Multivector:
    """Create a small dense value that exercises every exterior grade."""
    return algebra.multivector(rng.integers(-2, 3, size=algebra.dim))


def conformal_point(
    x: Multivector,
    eo: Multivector,
    einf: Multivector,
) -> Multivector:
    """Embed a Euclidean vector using the normalized CGA null pair."""
    x_squared = scalar_product(x, x).scalar_part
    return eo + x + 0.5 * x_squared * einf


def outermorphism(value: Multivector, images: Sequence[Multivector]) -> Multivector:
    """Extend a vector-basis map to all exterior blades.

    A source bitmask means a wedge of its selected basis vectors. Replacing
    each selected vector by its image and wedging in canonical order constructs
    the induced map on blades. Linearity then maps an arbitrary multivector.
    This deliberately uses only the outer product: a basis transformation is
    metric-independent and must not introduce geometric-product contractions.
    """
    if len(images) != value.algebra.n:
        raise ValueError("one image is required for every source basis vector")
    target = images[0].algebra
    result = target.scalar(0)
    for bitmask in np.flatnonzero(value.data):
        blade = target.scalar(1)
        for index, image in enumerate(images):
            if bitmask & (1 << index):
                blade = blade ^ image
        result = result + value.data[bitmask] * blade
    return result


class TestMultivectorRepresentationAndOperators:
    """Pin down storage, immutability, and the requested Python syntax."""

    def test_basis_vectors_are_multivectors_in_bitmask_slots(self) -> None:
        """``basis_vectors`` must return native grade-1 Multivectors.

        The metric determines products but does not alter exterior storage.
        Vector ``i`` therefore has one coefficient at ``1 << i`` even when it
        is null or non-orthogonal to another basis vector.
        """
        algebra = Algebra(gram=native_cga_gram())

        for index, vector in enumerate(algebra.basis_vectors()):
            expected = np.zeros(32)
            expected[1 << index] = 1
            assert isinstance(vector, Multivector)
            assert vector.algebra is algebra
            assert np.array_equal(vector.data, expected)
            assert not vector.data.flags.writeable

    def test_addition_subtraction_and_scaling_compose_new_values(self) -> None:
        """Linear arithmetic must compose coefficients without mutating inputs.

        Scalars occupy bitmask zero, vectors occupy one-bit masks, and a wedge
        occupies a multi-bit mask. Combining all three proves that arithmetic
        works uniformly across grades rather than only for basis vectors.
        """
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        e12 = e1 ^ e2
        value = 3 + 2 * e1 - e2 + 0.5 * e12

        assert isinstance(value, Multivector)
        assert value.coefficient(0) == 3
        assert value.coefficient(0b001) == 2
        assert value.coefficient(0b010) == -1
        assert value.coefficient(0b011) == 0.5
        assert_mv_close((value - 3 + e2 - 0.5 * e12) / 2, e1)

        # Cached basis values are canonical inputs and must remain untouched.
        assert np.array_equal(e1.data, algebra.blade(0b001).data)
        assert np.array_equal(e2.data, algebra.blade(0b010).data)

    def test_products_and_versor_composition_return_multivectors(self) -> None:
        """Products of vectors/versors stay inside the same value type.

        A versor is formed by geometric products of vectors. The prototype
        does not need a separate Versor class: closure of the Clifford algebra
        means its result is an ordinary, composable Multivector.
        """
        algebra = Algebra(3)
        e1, e2, e3 = algebra.basis_vectors()

        bivector = e1 ^ e2
        versor = e1 * e2 * e3

        assert isinstance(bivector, Multivector)
        assert isinstance(versor, Multivector)
        assert bivector.algebra is algebra
        assert versor.algebra is algebra
        assert_mv_close(versor, algebra.pseudoscalar())

    def test_named_functions_and_operators_are_equivalent(self) -> None:
        """The explicit API and convenience operators must share one engine."""
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()

        assert_mv_close(e1 * e2, geometric_product(e1, e2))
        assert_mv_close(e1 ^ e2, outer_product(e1, e2))
        assert_mv_close(~(e1 ^ e2), reverse(e1 ^ e2))

    def test_operations_reject_values_from_different_algebras(self) -> None:
        """Equal dimensions and metrics do not imply shared product identity.

        Each Algebra owns its Gram matrix and precomputed action matrices.
        Mixing values from separate instances could combine incompatible
        conventions or caches, so every binary multivector operation rejects
        it explicitly.
        """
        left = Algebra(3).basis_vectors()[0]
        right = Algebra(3).basis_vectors()[0]

        with pytest.raises(ValueError, match="different algebras"):
            _ = left + right
        with pytest.raises(ValueError, match="different algebras"):
            _ = left * right
        with pytest.raises(ValueError, match="different algebras"):
            _ = left ^ right


class TestGeneralAlgebraLaws:
    """Prove the product construction for every requested metric model."""

    @pytest.mark.parametrize("algebra", REQUESTED_ALGEBRAS, ids=lambda algebra: algebra.id)
    def test_every_basis_pair_satisfies_the_clifford_relation(self, algebra: Algebra) -> None:
        """Compute first: ``ei*ej + ej*ei`` must equal ``2 Gij``.

        This is the defining relation of the Clifford algebra and the most
        important test in the suite. It checks diagonal squares, null vectors,
        anticommutation of orthogonal vectors, and nonzero cross terms in the
        native CGA basis using one uniform assertion.
        """
        vectors = algebra.basis_vectors()
        for i, left in enumerate(vectors):
            for j, right in enumerate(vectors):
                assert_mv_close(
                    left * right + right * left,
                    2 * algebra.gram[i, j],
                )

    @pytest.mark.parametrize("algebra", REQUESTED_ALGEBRAS, ids=lambda algebra: algebra.id)
    def test_vector_product_splits_into_scalar_and_outer_parts(self, algebra: Algebra) -> None:
        """For vectors, ``ei*ej = Gij + ei^ej`` in every basis.

        Orthogonal implementations can accidentally assume the scalar term is
        absent whenever ``i != j``. Native CGA disproves that shortcut because
        ``eo*einf`` contains both scalar and bivector components.
        """
        vectors = algebra.basis_vectors()
        for i, left in enumerate(vectors):
            for j, right in enumerate(vectors):
                assert_mv_close(
                    left * right,
                    algebra.gram[i, j] + (left ^ right),
                )

    @pytest.mark.parametrize("algebra", REQUESTED_ALGEBRAS, ids=lambda algebra: algebra.id)
    def test_outer_product_is_alternating_and_antisymmetric(self, algebra: Algebra) -> None:
        """The exterior product must remain independent of the Gram matrix."""
        vectors = algebra.basis_vectors()
        for left in vectors:
            assert_mv_close(left ^ left, 0)
        for i, left in enumerate(vectors):
            for right in vectors[i + 1 :]:
                assert_mv_close(left ^ right, -(right ^ left))

    @pytest.mark.parametrize("algebra", REQUESTED_ALGEBRAS, ids=lambda algebra: algebra.id)
    def test_geometric_product_is_associative_for_dense_values(self, algebra: Algebra) -> None:
        """Associativity tests the entire precomputed blade-action table.

        Basis-vector relations alone are not sufficient: an incorrect
        higher-blade recurrence can satisfy all generator squares yet fail when
        products are regrouped. Dense random values exercise every grade and
        many simultaneous contraction paths, including degenerate PGA paths.
        """
        rng = np.random.default_rng(RNG_SEED + 100 + algebra.n)
        for _ in range(3):
            a = random_multivector(algebra, rng)
            b = random_multivector(algebra, rng)
            c = random_multivector(algebra, rng)
            assert_mv_close((a * b) * c, a * (b * c), atol=2e-10)

    @pytest.mark.parametrize("algebra", REQUESTED_ALGEBRAS, ids=lambda algebra: algebra.id)
    def test_products_are_distributive_and_outer_product_is_associative(
        self,
        algebra: Algebra,
    ) -> None:
        """Check the bilinear extension from basis blades to multivectors."""
        rng = np.random.default_rng(RNG_SEED + 200 + algebra.n)
        a = random_multivector(algebra, rng)
        b = random_multivector(algebra, rng)
        c = random_multivector(algebra, rng)

        assert_mv_close(a * (b + c), a * b + a * c)
        assert_mv_close((a + b) * c, a * c + b * c)
        assert_mv_close(a ^ (b + c), (a ^ b) + (a ^ c))
        assert_mv_close((a ^ b) ^ c, a ^ (b ^ c))

    @pytest.mark.parametrize("algebra", REQUESTED_ALGEBRAS, ids=lambda algebra: algebra.id)
    def test_reverse_is_an_anti_automorphism(self, algebra: Algebra) -> None:
        """Reversing a product must reverse the factor order.

        This simultaneously checks the grade-dependent reverse signs and their
        interaction with contractions in diagonal, degenerate, and general
        Gram metrics.
        """
        rng = np.random.default_rng(RNG_SEED + 300 + algebra.n)
        a = random_multivector(algebra, rng)
        b = random_multivector(algebra, rng)

        assert_mv_close(~(a * b), (~b) * (~a), atol=2e-10)
        assert_mv_close(~~a, a)

    @pytest.mark.parametrize("algebra", REQUESTED_ALGEBRAS, ids=lambda algebra: algebra.id)
    def test_grade_projection_partitions_every_multivector(self, algebra: Algebra) -> None:
        """Bitmask popcount remains the grade definition for every metric."""
        rng = np.random.default_rng(RNG_SEED + 400 + algebra.n)
        value = random_multivector(algebra, rng)
        reconstructed = sum((grade(value, k) for k in range(algebra.n + 1)), algebra.scalar(0))

        assert_mv_close(reconstructed, value)
        for k in range(algebra.n + 1):
            projected = grade(value, k)
            for bitmask, coefficient in enumerate(projected.data):
                if bitmask.bit_count() != k:
                    assert coefficient == 0


class TestRequestedAlgebraIdentities:
    """Check recognizable identities particular to each requested model."""

    def test_cl2_euclidean_bivector_and_rotor(self) -> None:
        """Cl(2,0) has a unit plane bivector squaring to -1.

        The normalized even versor ``(1-e12)/sqrt(2)`` must have unit reverse
        norm and rotate ``e1`` into ``e2`` by sandwiching. This exercises
        addition, scaling, wedge, geometric composition, and reverse together.
        """
        algebra = Algebra(2)
        e1, e2 = algebra.basis_vectors()
        e12 = e1 ^ e2
        rotor = (1 - e12) / np.sqrt(2)

        assert_mv_close(e12 * e12, -1)
        assert_mv_close(rotor * ~rotor, 1)
        assert_mv_close(rotor * e1 * ~rotor, e2)

    def test_cl3_euclidean_pseudoscalar_and_blade_composition(self) -> None:
        """Cl(3,0) must reproduce familiar bivector and pseudoscalar signs."""
        algebra = Algebra(3)
        e1, e2, e3 = algebra.basis_vectors()
        e12 = e1 ^ e2
        e23 = e2 ^ e3
        e13 = e1 ^ e3

        assert_mv_close(e12 * e23, e13)
        assert_mv_close(algebra.pseudoscalar() * algebra.pseudoscalar(), -1)

    def test_sta_signature_pseudoscalar_and_boost_versor(self) -> None:
        """STA Cl(1,3) distinguishes timelike and spacelike generators.

        A timelike-spacelike bivector squares to +1, so its exponential uses
        hyperbolic rather than circular functions. The manually constructed
        boost versor must still have unit reverse norm.
        """
        sta = Algebra(1, 3)
        g0, g1, g2, g3 = sta.basis_vectors()
        boost_plane = g0 ^ g1
        rapidity = 0.7
        boost = np.cosh(rapidity / 2) + np.sinh(rapidity / 2) * boost_plane

        assert_mv_close(g0 * g0, 1)
        for spacelike in (g1, g2, g3):
            assert_mv_close(spacelike * spacelike, -1)
        assert_mv_close(boost_plane * boost_plane, 1)
        assert_mv_close(sta.pseudoscalar() * sta.pseudoscalar(), -1)
        assert_mv_close(boost * ~boost, 1)

    def test_pga_null_dimension_and_nilpotent_translator(self) -> None:
        """PGA Cl(3,0,1) puts its degenerate vector first.

        A bivector containing the null vector is nilpotent. Consequently a
        translator of the form ``1 + dB/2`` has inverse/reverse ``1 - dB/2``
        without an infinite series. This proves degenerate products survive the
        same Gram-native engine.
        """
        pga = Algebra(3, 0, 1)
        e0, e1, _, _ = pga.basis_vectors()
        ideal_line = e0 ^ e1
        distance = 3.0
        translator = 1 + 0.5 * distance * ideal_line

        assert pga.signature == (0, 1, 1, 1)
        assert_mv_close(e0 * e0, 0)
        assert_mv_close(ideal_line * ideal_line, 0)
        assert_mv_close(pga.pseudoscalar() * pga.pseudoscalar(), 0)
        assert_mv_close(translator * ~translator, 1)

    def test_cl4_pseudoscalar_and_commuting_orthogonal_planes(self) -> None:
        """Disjoint even blades commute and compose to the 4D pseudoscalar."""
        algebra = Algebra(4)
        e1, e2, e3, e4 = algebra.basis_vectors()
        e12 = e1 ^ e2
        e34 = e3 ^ e4
        pseudoscalar = algebra.pseudoscalar()

        assert_mv_close(e12 * e34, pseudoscalar)
        assert_mv_close(e34 * e12, pseudoscalar)
        assert_mv_close(pseudoscalar * pseudoscalar, 1)

    @pytest.mark.parametrize("native", [False, True], ids=("orthogonal-derived", "native-null"))
    def test_both_cga_models_satisfy_null_and_point_identities(self, native: bool) -> None:
        """Derived and native null pairs must support identical CGA formulas.

        The orthogonal model obtains ``eo`` and ``einf`` as two-term
        multivectors. The Gram-native model returns them as one-hot basis
        vectors. The null products and conformal point embedding must not care
        which representation supplied the pair.
        """
        if native:
            algebra = Algebra(gram=native_cga_gram())
            e1, e2, e3, eo, einf = algebra.basis_vectors()
        else:
            algebra = Algebra(4, 1)
            e1, e2, e3, ep, em = algebra.basis_vectors()
            eo = 0.5 * (em - ep)
            einf = em + ep

        assert_mv_close(eo * eo, 0)
        assert_mv_close(einf * einf, 0)
        assert_mv_close(scalar_product(eo, einf), -1)
        assert_mv_close(eo * einf, -1 + (eo ^ einf))
        assert_mv_close(einf * eo, -1 - (eo ^ einf))

        x = e1 + 2 * e2 - 0.5 * e3
        point = conformal_point(x, eo, einf)
        assert_mv_close(point * point, 0)
        assert_mv_close(scalar_product(point, einf), -1)

    def test_derived_and_native_cga_vectors_have_different_storage(self) -> None:
        """The representation change is visible even though the algebra agrees.

        In orthogonal CGA, each null vector is a linear combination occupying
        the ``ep`` and ``em`` coefficient slots. In native CGA, ``eo`` and
        ``einf`` are themselves the one-hot grade-1 basis vectors at those
        bitmask positions; their pairing moves into the Gram matrix.
        """
        orthogonal = Algebra(4, 1)
        _, _, _, ep, em = orthogonal.basis_vectors()
        derived_eo = 0.5 * (em - ep)
        derived_einf = em + ep

        native = Algebra(gram=native_cga_gram())
        _, _, _, native_eo, native_einf = native.basis_vectors()

        assert np.count_nonzero(derived_eo.data) == 2
        assert np.count_nonzero(derived_einf.data) == 2
        assert np.count_nonzero(native_eo.data) == 1
        assert np.count_nonzero(native_einf.data) == 1
        assert native_eo.coefficient(0b01000) == 1
        assert native_einf.coefficient(0b10000) == 1


class TestCgaChangeOfBasisExhaustively:
    """Prove the complete native CGA algebra against orthogonal Cl(4,1)."""

    def test_all_basis_blade_products_intertwine(self) -> None:
        """Compare all 1,024 geometric and outer basis-blade products.

        The vector map sends native ``eo,einf`` to their documented derived
        values in orthogonal Cl(4,1). Its outermorphism maps every one of the 32
        native exterior basis blades. A valid Clifford-algebra isomorphism must
        satisfy ``F(A*B)=F(A)*F(B)``; checking every basis pair proves the rule
        for every multivector by bilinearity. The parallel wedge assertion
        proves the exterior-basis convention and orientation signs as well.
        """
        orthogonal = Algebra(4, 1)
        e1, e2, e3, ep, em = orthogonal.basis_vectors()
        derived_eo = 0.5 * (em - ep)
        derived_einf = em + ep

        native = Algebra(gram=native_cga_gram())
        images = (e1, e2, e3, derived_eo, derived_einf)
        mapped_blades = tuple(outermorphism(native.blade(bitmask), images) for bitmask in range(native.dim))

        for left_mask in range(native.dim):
            left = native.blade(left_mask)
            for right_mask in range(native.dim):
                right = native.blade(right_mask)

                mapped_gp = outermorphism(left * right, images)
                expected_gp = mapped_blades[left_mask] * mapped_blades[right_mask]
                assert_mv_close(mapped_gp, expected_gp)

                mapped_op = outermorphism(left ^ right, images)
                expected_op = mapped_blades[left_mask] ^ mapped_blades[right_mask]
                assert_mv_close(mapped_op, expected_op)

    def test_conformal_point_embedding_intertwines(self) -> None:
        """The basis isomorphism maps a native point to the derived-frame point."""
        orthogonal = Algebra(4, 1)
        old_e1, old_e2, old_e3, ep, em = orthogonal.basis_vectors()
        derived_eo = 0.5 * (em - ep)
        derived_einf = em + ep

        native = Algebra(gram=native_cga_gram())
        new_e1, new_e2, new_e3, native_eo, native_einf = native.basis_vectors()
        images = (old_e1, old_e2, old_e3, derived_eo, derived_einf)

        native_x = new_e1 - 2 * new_e2 + 0.25 * new_e3
        native_point = conformal_point(native_x, native_eo, native_einf)

        old_x = old_e1 - 2 * old_e2 + 0.25 * old_e3
        derived_point = conformal_point(old_x, derived_eo, derived_einf)

        assert_mv_close(outermorphism(native_point, images), derived_point)
