"""Executable design specification for native Gram-matrix construction.

These tests deliberately cover more than input/output examples. They pin down
the representation choices that a future Galaga implementation will rely on:

* every constructor normalizes to one immutable Gram matrix;
* ``Cl(p, q, r)`` and an explicitly ordered diagonal signature remain
  different input contracts;
* native basis vectors retain Galaga's one-hot exterior bitmask storage;
* all metric information, including off-diagonal null pairings, comes from the
  Gram matrix; and
* native null-basis CGA is the same abstract Clifford algebra as orthogonal
  ``Cl(4, 1)``, expressed in a different basis.

The suite tests the algebra before any geometric-product implementation is
added. That isolates metric construction errors from future multiplication
table errors and provides ground truth for that later work.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaga.core import Algebra, Multivector, scalar_product


def native_cga_gram() -> np.ndarray:
    """Return the desired native origin/infinity metric for 3D CGA.

    The first three vectors form the Euclidean spatial frame. The last two are
    individually null because their diagonal entries vanish, but they pair to
    -1 through the off-diagonal block. That block is nondegenerate: its
    eigenvalues are +1 and -1. Consequently, this is a nondegenerate
    ``Cl(4, 1)`` metric even though two stored basis vectors are null.

    Keeping this matrix in one helper ensures all CGA tests examine precisely
    the same convention and normalization.
    """
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


class TestPqrConstruction:
    """Prove the legacy ``Cl(p, q, r)`` constructor's normalization rules.

    ``p``, ``q``, and ``r`` describe counts, not an explicitly ordered basis.
    Galaga's established convention places null directions first, positive
    directions second, and negative directions last. Moving to a Gram-native
    engine must preserve that ordering for backward compatibility.
    """

    @pytest.mark.parametrize(
        ("args", "expected_diagonal"),
        [
            ((3,), (1, 1, 1)),
            ((1, 3), (1, -1, -1, -1)),
            ((3, 0, 1), (0, 1, 1, 1)),
            ((0, 2, 2), (0, 0, -1, -1)),
        ],
    )
    def test_pqr_constructs_null_positive_negative_diagonal(
        self,
        args: tuple[int, ...],
        expected_diagonal: tuple[int, ...],
    ) -> None:
        """Each count form must produce the documented diagonal Gram matrix.

        This checks both normalization layers exposed by the prototype:
        ``gram`` is the new canonical representation, while ``signature`` is
        the compatibility view available for normalized diagonal metrics. If
        either assertion fails, different parts of Galaga could disagree about
        which stored bit represents which metric direction.
        """
        algebra = Algebra(*args)

        assert np.array_equal(algebra.gram, np.diag(expected_diagonal))
        assert algebra.signature == expected_diagonal

    def test_dimension_is_dimension_of_full_exterior_algebra(self) -> None:
        """Five generating vectors require 32 multivector coefficients.

        The Gram matrix has shape ``n x n``, but basis blades are still indexed
        by subsets of those ``n`` vectors. There are therefore ``2**n`` scalar,
        vector, bivector, and higher-grade coefficient slots. This guards
        against the mistaken design of using an ``n x n`` array as each
        multivector's storage.
        """
        algebra = Algebra(4, 1)

        assert algebra.n == 5
        assert algebra.dim == 32

    def test_optional_id_names_the_algebra_without_affecting_its_metric(self) -> None:
        """An ID is stable descriptive metadata, not algebraic input.

        Names are useful in parameterized tests, examples, diagnostics, and
        applications that manage several models. Giving an algebra a name must
        not alter its Gram matrix, basis ordering, or products.
        """
        unnamed = Algebra(3)
        named = Algebra(3, id="euclidean-3d")

        assert unnamed.id is None
        assert named.id == "euclidean-3d"
        assert np.array_equal(named.gram, unnamed.gram)


class TestSignatureConstruction:
    """Specify the contract for an explicitly ordered diagonal metric.

    Unlike ``p, q, r``, ``signature=`` preserves the caller's order exactly.
    This matters for models such as RGA, where the null vector's position fixes
    blade bitmasks and orientation. ``sig=`` is purely a spelling alias and may
    not acquire separate semantics.
    """

    def test_explicit_signature_preserves_the_callers_basis_order(self) -> None:
        """Do not reorder an explicit signature into canonical p/q/r order.

        The final zero is intentionally kept at the final basis position. A
        normalization step that sorted by sign would describe an isomorphic
        algebra, but it would silently change every user-visible blade index.
        """
        algebra = Algebra(signature=(1, 1, 1, 0))

        assert np.array_equal(algebra.gram, np.diag((1, 1, 1, 0)))
        assert algebra.signature == (1, 1, 1, 0)

    def test_numpy_signature_is_supported(self) -> None:
        """Accept array-like inputs but canonicalize storage to float64.

        Future product tables will use NumPy floating-point coefficients.
        Normalizing an ``int8`` input here prevents constructor-dependent dtypes
        from leaking into multiplication, while preserving its exact values.
        """
        algebra = Algebra(signature=np.array((1, -1, 0), dtype=np.int8))

        assert algebra.gram.dtype == np.float64
        assert np.array_equal(algebra.gram, np.diag((1, -1, 0)))

    def test_sig_is_a_short_alias_for_signature(self) -> None:
        """The short spelling must be exactly equivalent to the long spelling.

        An alias is safe only if it enters the same normalization path. Testing
        final Gram matrices, rather than merely accepted syntax, prevents the
        two spellings from drifting as validation evolves.
        """
        long_form = Algebra(signature=[1, 0, -1])
        short_form = Algebra(sig=[1, 0, -1])

        assert np.array_equal(short_form.gram, long_form.gram)

    def test_rejects_both_signature_aliases_together(self) -> None:
        """Reject ambiguous duplicate inputs instead of choosing precedence.

        Even identical values would establish an undesirable precedence rule;
        later, two conflicting values would make the chosen metric surprising.
        Exactly one metric-description channel must own construction.
        """
        with pytest.raises(TypeError, match="aliases; provide only one"):
            Algebra(signature=[1, 1], sig=[1, 1])

    def test_signature_is_keyword_only(self) -> None:
        """Reserve positional arguments exclusively for p, q, and r.

        The former polymorphic first argument made the public signature harder
        to understand and type-check. Requiring ``signature=`` or ``sig=``
        makes the chosen metric model explicit at every call site.
        """
        with pytest.raises(TypeError, match="use signature= or sig="):
            Algebra((1, 1, 1))  # type: ignore[arg-type]


class TestGramConstruction:
    """Prove the invariants unique to a general symmetric Gram matrix.

    A native Gram matrix is more expressive than a diagonal signature because
    off-diagonal entries participate in the Clifford relation. These tests
    ensure construction preserves that information and freezes it before any
    multiplication data can be derived from it.
    """

    def test_preserves_a_symmetric_nonorthogonal_metric(self) -> None:
        """Store cross terms exactly instead of diagonalizing them away.

        The zeros on the last two diagonal entries make both CGA vectors null;
        their -1 cross term makes them a reciprocal pair. ``basis_squares`` is
        intentionally only the diagonal and cannot replace ``gram``. The
        orthogonality flag must therefore inspect off-diagonal entries.
        """
        expected = native_cga_gram()
        algebra = Algebra(gram=expected)

        assert np.array_equal(algebra.gram, expected)
        assert np.array_equal(algebra.basis_squares, (1, 1, 1, 0, 0))
        assert not algebra.is_orthogonal_basis

    def test_input_is_copied_and_result_is_read_only(self) -> None:
        """Metric state must be immutable after Algebra construction.

        Galaga will precompute products from the Gram matrix. If the caller
        could mutate either the original input or a returned view afterward,
        ``algebra.gram`` and those cached products would contradict each other.
        The diagonal view is frozen for the same reason.
        """
        source = np.array([[1.0, 0.25], [0.25, -1.0]])
        algebra = Algebra(gram=source)
        source[0, 0] = 99.0

        assert algebra.gram[0, 0] == 1.0
        with pytest.raises(ValueError, match="read-only"):
            algebra.gram[0, 0] = 2.0
        with pytest.raises(ValueError, match="read-only"):
            algebra.basis_squares[0] = 2.0

    def test_numerical_asymmetry_within_tolerance_is_canonicalized(self) -> None:
        """Tolerate floating-point noise while storing one symmetric form.

        A real Clifford metric is symmetric, but a matrix produced by numeric
        transformations can differ from its transpose by rounding error.
        Construction accepts that tiny discrepancy and averages both entries.
        Exact symmetry afterward is important because ``scalar_product(ei,
        ej)`` and ``scalar_product(ej, ei)`` must agree and produce a valid
        Clifford relation.
        """
        source = np.array([[1.0, 0.5 + 1e-14], [0.5, -1.0]])
        algebra = Algebra(gram=source)

        assert np.array_equal(algebra.gram, algebra.gram.T)
        assert algebra.gram[0, 1] == pytest.approx(0.5 + 0.5e-14)

    def test_signature_refuses_to_discard_cross_terms(self) -> None:
        """Do not fabricate a legacy signature for a non-orthogonal basis.

        Returning only ``diag(G)`` would lose metric information; returning an
        eigenvalue signature would describe a different basis. Raising forces
        callers to ask for ``gram``, ``basis_squares``, or eventually inertia,
        according to the mathematical fact they actually require.
        """
        algebra = Algebra(gram=np.array([[1.0, 0.25], [0.25, -1.0]]))

        with pytest.raises(ValueError, match="only defined for normalized diagonal"):
            _ = algebra.signature


class TestNativeCgaMathematics:
    """Establish algebraic ground truth for native null-basis CGA.

    These tests connect three layers: constructor normalization, one-hot
    exterior storage, and the bilinear form. They also prove by change of basis
    that the proposed null frame is not a different algebra from the existing
    orthogonal ``Cl(4, 1)`` representation.
    """

    @pytest.mark.parametrize(
        "algebra",
        [
            Algebra(3, 0, 1),
            Algebra(sig=[1, 1, 1, 0]),
            Algebra(gram=native_cga_gram()),
        ],
        ids=("pqr", "signature", "gram"),
    )
    def test_basis_pairing_table_matches_gram_for_every_constructor(self, algebra: Algebra) -> None:
        """All constructor forms must feed one common basis-vector mechanism.

        The three parameters deliberately describe different metrics, but in
        every case the complete scalar-product table must reproduce the
        canonical Gram matrix owned by that algebra. This proves downstream
        product code does not branch on how the algebra was constructed.
        """
        vectors = algebra.basis_vectors()
        actual = np.array([[scalar_product(left, right).scalar_part for right in vectors] for left in vectors])

        assert np.array_equal(actual, algebra.gram)

    def test_basis_vectors_are_native_one_hot_multivector_coefficients(self) -> None:
        """Native vectors occupy the grade-1 bitmask slots of 32-space.

        For vector index ``i``, Galaga stores coefficient 1 at multivector index
        ``1 << i``. In particular, CGA's null ``e4`` and ``e5`` become true
        one-hot basis values rather than two-term combinations of ``ep`` and
        ``em``. The data arrays are read-only so cached canonical basis values
        cannot be corrupted by a caller.
        """
        algebra = Algebra(gram=native_cga_gram())
        vectors = algebra.basis_vectors()

        assert len(vectors) == 5
        for index, vector in enumerate(vectors):
            expected = np.zeros(32)
            expected[1 << index] = 1.0
            assert isinstance(vector, Multivector)
            assert vector.algebra is algebra
            assert np.array_equal(vector.data, expected)
            assert not vector.data.flags.writeable

    def test_every_basis_vector_inner_product_equals_its_gram_entry(self) -> None:
        """Verify the defining interpretation ``G[i,j] = ei dot ej``.

        Checking all 25 entries catches index transposition, one-based versus
        zero-based errors, and accidental use of only the diagonal. This is the
        first metric-consistency test a future product engine must continue to
        satisfy.
        """
        algebra = Algebra(gram=native_cga_gram())
        vectors = algebra.basis_vectors()
        actual = np.array([[scalar_product(left, right).scalar_part for right in vectors] for left in vectors])

        assert np.array_equal(actual, algebra.gram)

    def test_native_e4_and_e5_have_the_required_null_pairing(self) -> None:
        """Prove the characteristic conformal null-plane identities directly.

        Null does not mean zero: each vector has zero norm but their mutual
        product is nonzero. This reciprocal pairing is what lets CGA encode
        origin and infinity while the complete metric remains nondegenerate.
        Both orders are checked because the metric is symmetric.
        """
        algebra = Algebra(gram=native_cga_gram())
        _, _, _, e4, e5 = algebra.basis_vectors()

        assert scalar_product(e4, e4).scalar_part == 0
        assert scalar_product(e5, e5).scalar_part == 0
        assert scalar_product(e4, e5).scalar_part == -1
        assert scalar_product(e5, e4).scalar_part == -1

    def test_scalar_product_rejects_a_different_algebra(self) -> None:
        """Metric operations require identity of the owning Algebra object.

        Two algebras can happen to contain equal matrices while owning distinct
        naming conventions, multiplication tables, or future caches. Silently
        combining their values would weaken Galaga's existing same-algebra
        invariant and could make later products internally inconsistent.
        """
        left = Algebra(3).basis_vectors()[0]
        right = Algebra(3).basis_vectors()[0]

        with pytest.raises(ValueError, match="different algebras"):
            scalar_product(left, right)

    def test_null_cga_gram_is_congruent_to_orthogonal_cl41(self) -> None:
        """Prove the native null frame is a basis change of orthogonal Cl(4,1).

        Starting with ``ep²=+1`` and ``em²=-1``, the final two rows encode
        ``eo=(em-ep)/2`` and ``einf=em+ep``. A bilinear form transforms as
        ``T G T.T`` when rows of ``T`` contain the new basis vectors. Obtaining
        the proposed matrix proves it preserves every scalar product implied by
        that established construction, not only the three hand-picked null
        identities.
        """
        orthogonal = Algebra(4, 1).gram
        change_of_basis = np.eye(5)
        # eo = (em - ep) / 2; einf = em + ep
        change_of_basis[3] = (0, 0, 0, -0.5, 0.5)
        change_of_basis[4] = (0, 0, 0, 1.0, 1.0)

        transformed = change_of_basis @ orthogonal @ change_of_basis.T

        assert np.array_equal(transformed, native_cga_gram())

    @pytest.mark.parametrize(
        ("origin_scale", "infinity_scale"),
        [
            (0.5, 1.0),
            (1.0, 0.5),
            (1 / np.sqrt(2), 1 / np.sqrt(2)),
        ],
        ids=("conventional", "factor-on-infinity", "symmetric"),
    )
    def test_all_normalized_null_pair_scalings_give_the_same_gram(
        self,
        origin_scale: float,
        infinity_scale: float,
    ) -> None:
        """Prove that only the product of the two null scales is fixed.

        For ``eo=a(em-ep)`` and ``einf=b(em+ep)``, their pairing is
        ``-2ab``. Each parameter pair satisfies ``ab=1/2``: the traditional
        factor on origin, the factor moved to infinity, and equal square-root
        factors. Congruence with the orthogonal metric must consequently yield
        the same native null Gram matrix in every case. This is the executable
        ground truth behind the dedicated null-pair scaling document.
        """
        orthogonal = Algebra(4, 1).gram
        change_of_basis = np.eye(5)
        change_of_basis[3] = (0, 0, 0, -origin_scale, origin_scale)
        change_of_basis[4] = (0, 0, 0, infinity_scale, infinity_scale)

        transformed = change_of_basis @ orthogonal @ change_of_basis.T

        assert origin_scale * infinity_scale == pytest.approx(0.5)
        assert np.allclose(transformed, native_cga_gram())

    def test_null_cga_gram_has_cl41_inertia(self) -> None:
        """Two null basis vectors do not make the CGA metric degenerate.

        Sylvester inertia classifies a real quadratic form independently of
        basis. Four positive and one negative eigenvalue prove this matrix
        still defines ``Cl(4,1)`` and has no radical. This guards against
        incorrectly counting zeros on ``diag(G)`` as null eigenvalues.
        """
        eigenvalues = np.linalg.eigvalsh(native_cga_gram())

        assert np.count_nonzero(eigenvalues > 0) == 4
        assert np.count_nonzero(eigenvalues < 0) == 1
        assert np.count_nonzero(eigenvalues == 0) == 0

    def test_clifford_anticommutator_coefficients_are_twice_the_gram(self) -> None:
        """Connect metric construction to the future geometric-product law.

        The defining relation is ``ei*ej + ej*ei = 2 G[i,j]``. This prototype
        intentionally has no geometric-product backend yet, so symmetrizing
        the stored bilinear table proves the scalar coefficients that backend
        must generate. Once multiplication exists, this test should be upgraded
        to compute the left side from actual basis-vector products.
        """
        algebra = Algebra(gram=native_cga_gram())
        anticommutator_scalars = algebra.gram + algebra.gram.T

        assert np.array_equal(anticommutator_scalars, 2 * native_cga_gram())


class TestValidation:
    """Reject inputs whose mathematical meaning would be ambiguous or invalid.

    Validation is part of the algebra's design contract. Failing early is
    essential because construction will eventually precompute large tables;
    discovering a malformed metric only after those allocations would obscure
    the actual user error and risk partially initialized state.
    """

    @pytest.mark.parametrize(
        "args",
        [
            (-1,),
            (1, -1),
            (1, 0, -1),
            (1.5,),
            (True,),
        ],
    )
    def test_rejects_invalid_pqr_counts(self, args: tuple[object, ...]) -> None:
        """p, q, and r are nonnegative integer counts, never coefficients.

        Negative counts have no dimensional meaning. Floats are rejected even
        when numerically integral so the API remains explicit, and booleans are
        rejected despite ``bool`` being an ``int`` subclass in Python. The
        chosen exception distinguishes an invalid value from an invalid type.
        """
        error = ValueError if any(isinstance(value, int) and value < 0 for value in args) else TypeError
        with pytest.raises(error):
            Algebra(*args)

    @pytest.mark.parametrize(
        "signature",
        [
            (),
            (1, 2, -1),
            (1, np.nan),
        ],
    )
    def test_rejects_invalid_signatures(self, signature: tuple[float, ...]) -> None:
        """A legacy signature is a nonempty sequence containing only -1/0/+1.

        General scales and cross terms belong in ``gram=``. Keeping the legacy
        form normalized makes its meaning, compatibility property, and fast
        diagonal multiplication rules unambiguous. Non-finite values can never
        define reliable precomputed products.
        """
        with pytest.raises(ValueError):
            Algebra(signature=signature)

    @pytest.mark.parametrize(
        "gram",
        [
            [[1, 0, 0], [0, 1, 0]],
            [[1, 1], [0, 1]],
            [[1, np.inf], [np.inf, 1]],
            [[1 + 1j]],
        ],
    )
    def test_rejects_invalid_gram_matrices(self, gram: object) -> None:
        """A real Clifford Gram matrix must be finite, square, and symmetric.

        The cases cover a rectangular array, a genuinely asymmetric bilinear
        form, non-finite entries, and complex coefficients. Supporting any of
        these would require a different algebraic contract than the proposed
        real symmetric Clifford algebra.
        """
        with pytest.raises((TypeError, ValueError)):
            Algebra(gram=gram)

    def test_rejects_mixed_constructor_forms(self) -> None:
        """Exactly one source of metric truth may be supplied.

        Combining p/q/r with ``gram=`` or ``signature=`` raises rather than
        defining precedence. Otherwise the constructor could accept two
        contradictory metrics, making it unclear which one should control
        basis ordering, cached products, and display conventions.
        """
        with pytest.raises(TypeError, match="cannot be combined"):
            Algebra(3, gram=np.eye(3))

        with pytest.raises(TypeError, match="cannot be combined"):
            Algebra(gram=np.eye(3), q=1)

        with pytest.raises(TypeError, match="cannot be combined"):
            Algebra(3, signature=[1, 1, 1])

    @pytest.mark.parametrize("invalid_id", ["", "   ", 42])
    def test_rejects_invalid_algebra_ids(self, invalid_id: object) -> None:
        """IDs must be meaningful strings when supplied.

        Empty labels provide no diagnostic value, while accepting arbitrary
        objects would make test IDs and serialized metadata unpredictable.
        ``None`` remains the explicit unnamed default.
        """
        with pytest.raises((TypeError, ValueError)):
            Algebra(3, id=invalid_id)  # type: ignore[arg-type]
