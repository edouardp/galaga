"""Tests for the ga library — golden tests and property tests."""

import numpy as np
import pytest

from galaga import (
    Algebra,
    Multivector,
    conjugate,
    doran_lasenby_inner,
    dorst_inner,
    dual,
    exp,
    geometric_product,
    gp,
    grade,
    grades,
    hestenes_inner,
    inverse,
    involute,
    is_bivector,
    is_even,
    is_scalar,
    is_vector,
    left_contraction,
    log,
    norm,
    norm2,
    op,
    project,
    reflect,
    reject,
    rev,
    reverse,
    right_contraction,
    scalar_product,
    scalar_sqrt,
    undual,
    unit,
    wedge,
)

# ---- Fixtures ----


@pytest.fixture
def cl2():
    return Algebra((1, 1))


@pytest.fixture
def cl3():
    return Algebra((1, 1, 1))


@pytest.fixture
def sta():
    return Algebra((1, -1, -1, -1))


# ---- Phase 1: Algebra construction ----


class TestAlgebra:
    def test_cl3_dimensions(self, cl3):
        """Cl(3,0) has n=3, dim=8."""
        assert cl3.n == 3
        assert cl3.dim == 8
        assert cl3.signature == (1, 1, 1)

    def test_cl2_dimensions(self, cl2):
        """Cl(2,0) has n=2, dim=4."""
        assert cl2.n == 2
        assert cl2.dim == 4

    def test_sta_dimensions(self, sta):
        """Cl(1,3) has n=4, dim=16."""
        assert sta.n == 4
        assert sta.dim == 16
        assert sta.signature == (1, -1, -1, -1)

    def test_repr(self, cl3, sta):
        """Algebra repr shows signature summary."""
        assert repr(cl3) == "Cl(3,0)"
        assert repr(sta) == "Cl(1,3)"

    def test_basis_vectors(self, cl3):
        """Basis vectors have unit coefficient at correct index."""
        e1, e2, e3 = cl3.basis_vectors()
        assert e1.data[1] == 1.0
        assert e2.data[2] == 1.0
        assert e3.data[4] == 1.0

    def test_pseudoscalar(self, cl3):
        """Pseudoscalar is the highest-grade blade."""
        I = cl3.pseudoscalar()
        assert I.data[7] == 1.0  # e123 = 0b111 = 7

    def test_blade_lookup(self, cl3):
        """blade() returns correct basis blade by name."""
        e12 = cl3.blade("e12")
        assert e12.data[3] == 1.0  # 0b011 = 3

    def test_scalar_constructor(self, cl3):
        """().scalar_part creates a pure grade-0 multivector."""
        s = cl3.scalar(5.0)
        assert s.data[0] == 5.0
        assert np.allclose(s.data[1:], 0)

    def test_vector_constructor(self, cl3):
        """vector() places coefficients at grade-1 indices."""
        v = cl3.vector([1, 2, 3])
        assert v.data[1] == 1.0
        assert v.data[2] == 2.0
        assert v.data[4] == 3.0


# ---- Phase 2: Multivector basics ----


class TestMultivector:
    def test_add(self, cl3):
        """MV addition combines coefficients."""
        e1, e2, _ = cl3.basis_vectors()
        r = e1 + e2
        assert r.data[1] == 1.0
        assert r.data[2] == 1.0

    def test_scalar_add(self, cl3):
        """Scalar + MV adds to grade-0."""
        e1, _, _ = cl3.basis_vectors()
        r = 3 + e1
        assert r.data[0] == 3.0
        assert r.data[1] == 1.0

    def test_sub(self, cl3):
        """MV subtraction."""
        e1, e2, _ = cl3.basis_vectors()
        r = e1 - e2
        assert r.data[1] == 1.0
        assert r.data[2] == -1.0

    def test_scalar_mul(self, cl3):
        """Scalar * MV scales coefficients."""
        e1, _, _ = cl3.basis_vectors()
        r = 3 * e1
        assert r.data[1] == 3.0

    def test_neg(self, cl3):
        """Unary negation."""
        e1, _, _ = cl3.basis_vectors()
        r = -e1
        assert r.data[1] == -1.0

    def test_div(self, cl3):
        """MV / scalar divides coefficients."""
        e1, _, _ = cl3.basis_vectors()
        r = (2 * e1) / 2
        assert r.data[1] == 1.0

    def test_pow_zero(self, cl3):
        """x**0 = 1."""
        e1, _, _ = cl3.basis_vectors()
        assert (2 * e1) ** 0 == cl3.scalar(1.0)

    def test_pow_one(self, cl3):
        """x**1 = x."""
        e1, _, _ = cl3.basis_vectors()
        v = 2 * e1
        assert v**1 == v

    def test_pow_two(self, cl3):
        """x**2 = x*x."""
        e1, e2, _ = cl3.basis_vectors()
        v = 2 * e1 + 3 * e2
        assert v**2 == v * v

    def test_pow_three(self, cl3):
        """x**3 = x*x*x."""
        e1, _, _ = cl3.basis_vectors()
        assert e1**3 == e1 * e1 * e1

    def test_pow_negative(self, cl3):
        """x**-1 = inverse(x)."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor(e1 ^ e2, radians=0.5)
        assert R**-1 == R.inv

    def test_pow_negative_two(self, cl3):
        """x**-2 = inv(x)*inv(x)."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor(e1 ^ e2, radians=0.5)
        assert R**-2 == R.inv * R.inv

    def test_pow_float_returns_not_implemented(self, cl3):
        """Non-integer powers raise TypeError."""
        e1, _, _ = cl3.basis_vectors()
        with pytest.raises(TypeError):
            e1**0.5

    def test_repr_nonzero(self, cl3):
        """repr includes all nonzero components."""
        e1, e2, _ = cl3.basis_vectors()
        r = 3 + 2 * e1 - e2
        s = repr(r)
        assert "3" in s
        assert "e₁" in s
        assert "e₂" in s

    def test_repr_zero(self, cl3):
        """Zero MV displays as '0'."""
        z = cl3.scalar(0)
        assert repr(z) == "0"

    def test_repr_matches_str(self, cl3):
        """repr and str produce the same output."""
        e1, _, _ = cl3.basis_vectors()
        assert repr(e1) == str(e1)

    def test_repr_unicode_true(self):
        """repr_unicode=True makes repr use unicode."""
        alg = Algebra((1, 1, 1), repr_unicode=True)
        e1, e2, _ = alg.basis_vectors()
        v = 3 * e1 + 4 * e2
        assert repr(v) == str(v)
        assert "e₁" in repr(v)

    def test_repr_unicode_pseudoscalar(self):
        """Pseudoscalar repr with repr_unicode."""
        alg = Algebra((1, 1, 1), repr_unicode=True)
        assert repr(alg.I) == str(alg.I)

    def test_repr_unicode_with_names(self):
        """Named algebras use their names in repr."""
        sta = Algebra((1, -1, -1, -1), names="gamma", repr_unicode=True)
        g0, g1, _, _ = sta.basis_vectors()
        assert "γ" in repr(g0 * g1)

    # --- __format__ tests ---

    def test_format_empty_spec(self, cl3):
        """Empty format spec matches str()."""
        e1, _, _ = cl3.basis_vectors()
        assert f"{e1}" == str(e1)

    def test_format_numeric_spec(self, cl3):
        """Numeric format spec controls coefficient precision."""
        e1, e2, _ = cl3.basis_vectors()
        v = 3.14159 * e1 + 2.71828 * e2
        result = f"{v:.3f}"
        assert "3.142" in result
        assert "2.718" in result

    def test_format_1f(self, cl3):
        """:.1f rounds to one decimal."""
        e1, _, _ = cl3.basis_vectors()
        v = 3.14159 * e1
        assert "3.1" in f"{v:.1f}"

    def test_format_scalar(self, cl3):
        """Format spec works on pure scalars."""
        s = cl3.scalar(3.14159)
        assert f"{s:.2f}" == "3.14"

    def test_format_zero(self, cl3):
        """Zero formats with the given precision."""
        z = cl3.scalar(0.0)
        assert f"{z:.3f}" == "0.000"

    def test_format_latex_spec(self, cl3):
        """:latex format spec returns latex()."""
        e1, _, _ = cl3.basis_vectors()
        assert f"{e1:latex}" == e1.latex()

    def test_format_unicode_spec(self, cl3):
        """:unicode format spec returns str()."""
        e1, _, _ = cl3.basis_vectors()
        assert f"{e1:unicode}" == str(e1)

    def test_format_ascii_spec(self, cl3):
        """:ascii format spec returns ASCII-only output."""
        e1, _, _ = cl3.basis_vectors()
        result = f"{e1:ascii}"
        assert "e1" in result
        assert "₁" not in result

    def test_format_negative_coeff(self, cl3):
        """Negative coefficients render with minus sign."""
        e1, e2, _ = cl3.basis_vectors()
        v = e1 - 2.5 * e2
        result = f"{v:.1f}"
        assert "1.0" in result
        assert "2.5" in result
        assert "-" in result

    def test_format_multivector_mixed(self, cl3):
        """Mixed-grade MV formats all components."""
        e1, e2, _ = cl3.basis_vectors()
        mv = cl3.scalar(1.0) + 2.0 * e1 + 3.0 * (e1 ^ e2)
        result = f"{mv:.0f}"
        assert "1" in result
        assert "2" in result
        assert "3" in result

    def test_algebra_mismatch(self, cl2, cl3):
        """Operations on MVs from different algebras raise ValueError."""
        e1_2d = cl2.basis_vectors()[0]
        e1_3d = cl3.basis_vectors()[0]
        with pytest.raises(ValueError, match="different algebras"):
            gp(e1_2d, e1_3d)


# ---- Phase 3: Core operations ----


class TestGeometricProduct:
    def test_basis_vector_squares_cl3(self, cl3):
        """In Cl(3,0), e_i^2 = +1."""
        for e in cl3.basis_vectors():
            r = gp(e, e)
            assert np.isclose((r).scalar_part, 1.0)

    def test_basis_vector_squares_sta(self, sta):
        """In Cl(1,3), e0^2=+1, e1^2=e2^2=e3^2=-1."""
        vecs = sta.basis_vectors()
        assert np.isclose((gp(vecs[0], vecs[0])).scalar_part, 1.0)
        for i in range(1, 4):
            assert np.isclose((gp(vecs[i], vecs[i])).scalar_part, -1.0)

    def test_anticommutativity(self, cl3):
        """e_i * e_j = -e_j * e_i for i != j."""
        e1, e2, e3 = cl3.basis_vectors()
        assert gp(e1, e2) == -gp(e2, e1)
        assert gp(e1, e3) == -gp(e3, e1)
        assert gp(e2, e3) == -gp(e3, e2)

    def test_associativity(self, cl3):
        """gp is associative: (ab)c = a(bc)."""
        e1, e2, e3 = cl3.basis_vectors()
        a = 1 + 2 * e1
        b = e2 + 3 * e3
        c = e1 + e2 + e3
        assert gp(gp(a, b), c) == gp(a, gp(b, c))

    def test_distributivity(self, cl3):
        """gp distributes over addition."""
        e1, e2, e3 = cl3.basis_vectors()
        a = e1 + e2
        b = e2
        c = e3
        assert gp(a, b + c) == gp(a, b) + gp(a, c)

    def test_pseudoscalar_square_cl3(self, cl3):
        """I^2 = -1 in Cl(3,0)."""
        I = cl3.pseudoscalar()
        assert np.isclose((gp(I, I)).scalar_part, -1.0)

    def test_operator_star(self, cl3):
        """* operator maps to gp()."""
        e1, e2, _ = cl3.basis_vectors()
        assert e1 * e2 == gp(e1, e2)


class TestOuterProduct:
    def test_basis_wedge(self, cl3):
        """e1∧e2 produces the e12 blade."""
        e1, e2, _ = cl3.basis_vectors()
        e12 = op(e1, e2)
        assert e12.data[3] == 1.0  # e12 = index 3

    def test_wedge_anticommutative(self, cl3):
        """a∧b = -(b∧a)."""
        e1, e2, _ = cl3.basis_vectors()
        assert op(e1, e2) == -op(e2, e1)

    def test_wedge_self_zero(self, cl3):
        """a∧a = 0."""
        e1, _, _ = cl3.basis_vectors()
        r = op(e1, e1)
        assert np.allclose(r.data, 0)

    def test_operator_xor(self, cl3):
        """^ operator maps to op()."""
        e1, e2, _ = cl3.basis_vectors()
        assert (e1 ^ e2) == op(e1, e2)


class TestContractions:
    def test_left_contraction_vector_bivector(self, cl3):
        """e1⌋e12 = e2."""
        e1, e2, e3 = cl3.basis_vectors()
        e12 = e1 ^ e2
        # e1 ⌋ e12 = e2
        r = left_contraction(e1, e12)
        assert r == e2

    def test_left_contraction_vector_vector(self, cl3):
        """Vector⌋vector gives dot product."""
        e1, e2, _ = cl3.basis_vectors()
        # e1 ⌋ e1 = 1 (dot product)
        r = left_contraction(e1, e1)
        assert np.isclose((r).scalar_part, 1.0)
        # e1 ⌋ e2 = 0
        r = left_contraction(e1, e2)
        assert np.isclose((r).scalar_part, 0.0)

    def test_right_contraction(self, cl3):
        """e12⌊e2 = e1."""
        e1, e2, _ = cl3.basis_vectors()
        e12 = e1 ^ e2
        # e12 ⌊ e2 = e1
        r = right_contraction(e12, e2)
        assert r == e1

    def test_hestenes_inner_vectors(self, cl3):
        """Hestenes inner on vectors matches dot product."""
        e1, e2, _ = cl3.basis_vectors()
        assert np.isclose((hestenes_inner(e1, e1)).scalar_part, 1.0)
        assert np.isclose((hestenes_inner(e1, e2)).scalar_part, 0.0)

    def test_hestenes_inner_scalar_gives_zero(self, cl3):
        """Hestenes kills scalar operands."""
        s = cl3.scalar(5.0)
        e1, _, _ = cl3.basis_vectors()
        r = hestenes_inner(s, e1)
        assert np.allclose(r.data, 0)

    def test_doran_lasenby_inner_vectors(self, cl3):
        """DL inner on vectors matches dot product."""
        e1, e2, _ = cl3.basis_vectors()
        assert np.isclose((doran_lasenby_inner(e1, e1)).scalar_part, 1.0)
        assert np.isclose((doran_lasenby_inner(e1, e2)).scalar_part, 0.0)

    def test_doran_lasenby_inner_scalar_includes(self, cl3):
        """Unlike Hestenes, Doran–Lasenby does NOT kill scalars."""
        s = cl3.scalar(3.0)
        e1, _, _ = cl3.basis_vectors()
        r = doran_lasenby_inner(s, e1)
        assert r == 3.0 * e1

    def test_dorst_inner_is_alias(self):
        """dorst_inner is doran_lasenby_inner."""
        assert dorst_inner is doran_lasenby_inner

    def test_scalar_product(self, cl3):
        """Scalar product of orthonormal vectors."""
        e1, e2, _ = cl3.basis_vectors()
        assert np.isclose((scalar_product(e1, e1)).scalar_part, 1.0)
        assert np.isclose((scalar_product(e1, e2)).scalar_part, 0.0)

    def test_operator_pipe(self, cl3):
        """| operator maps to doran_lasenby_inner()."""
        e1, e2, _ = cl3.basis_vectors()
        e12 = e1 ^ e2
        assert (e1 | e12) == doran_lasenby_inner(e1, e12)

    # --- Mixed-grade cases where the three inner products diverge ---

    def test_left_contraction_bivector_on_vector_is_zero(self, cl3):
        """grade(a) > grade(b) → left contraction vanishes."""
        e1, e2, _ = cl3.basis_vectors()
        e12 = e1 ^ e2
        r = left_contraction(e12, e1)
        assert np.allclose(r.data, 0)

    def test_right_contraction_vector_on_bivector_is_zero(self, cl3):
        """grade(a) < grade(b) → right contraction vanishes."""
        e1, e2, _ = cl3.basis_vectors()
        e12 = e1 ^ e2
        r = right_contraction(e1, e12)
        assert np.allclose(r.data, 0)

    def test_hestenes_bivector_on_vector_nonzero(self, cl3):
        """grade(a) > grade(b) → Hestenes uses |r-s|, so this is nonzero."""
        e1, e2, _ = cl3.basis_vectors()
        e12 = e1 ^ e2
        r = hestenes_inner(e12, e1)
        # |2-1| = 1, so result is grade-1
        assert r == -e2

    def test_left_contraction_scalar_passes_through(self, cl3):
        """Scalar ⌋ x = scalar * x (left contraction allows grade-0 left)."""
        e1, _, _ = cl3.basis_vectors()
        s = cl3.scalar(3.0)
        r = left_contraction(s, e1)
        assert r == 3 * e1

    def test_hestenes_scalar_is_zero(self, cl3):
        """Hestenes kills scalar operands on either side."""
        e1, _, _ = cl3.basis_vectors()
        s = cl3.scalar(3.0)
        assert np.allclose(hestenes_inner(s, e1).data, 0)
        assert np.allclose(hestenes_inner(e1, s).data, 0)

    def test_right_contraction_scalar_right(self, cl3):
        """x ⌊ scalar = scalar * x (right contraction allows grade-0 right)."""
        e1, _, _ = cl3.basis_vectors()
        s = cl3.scalar(3.0)
        r = right_contraction(e1, s)
        assert r == 3 * e1

    def test_left_contraction_bivector_on_bivector(self, cl3):
        """Bivector ⌋ bivector → scalar (grade 2-2=0)."""
        e1, e2, e3 = cl3.basis_vectors()
        e12 = e1 ^ e2
        e13 = e1 ^ e3
        # e12 ⌋ e12 = -1 (scalar)
        r = left_contraction(e12, e12)
        assert np.isclose((r).scalar_part, -1.0)
        # e12 ⌋ e13 = 0 (gp gives grade-2, not grade-0)
        r = left_contraction(e12, e13)
        assert np.allclose(r.data, 0)

    def test_hestenes_bivector_on_bivector(self, cl3):
        """Hestenes bivector·bivector → scalar (|2-2|=0), same as left."""
        e1, e2, e3 = cl3.basis_vectors()
        e12 = e1 ^ e2
        r = hestenes_inner(e12, e12)
        assert np.isclose((r).scalar_part, -1.0)

    def test_left_contraction_vector_on_trivector(self, cl3):
        """Vector ⌋ trivector → bivector (grade 3-1=2)."""
        e1, e2, e3 = cl3.basis_vectors()
        e123 = e1 ^ e2 ^ e3
        r = left_contraction(e1, e123)
        assert r == e2 ^ e3

    def test_right_contraction_trivector_on_vector(self, cl3):
        """Trivector ⌊ vector → bivector (grade 3-1=2)."""
        e1, e2, e3 = cl3.basis_vectors()
        e123 = e1 ^ e2 ^ e3
        r = right_contraction(e123, e1)
        assert r == e2 ^ e3

    def test_contractions_asymmetry(self, cl3):
        """Left and right contraction are NOT symmetric — key difference."""
        e1, e2, _ = cl3.basis_vectors()
        e12 = e1 ^ e2
        lc = left_contraction(e1, e12)  # grade 2-1=1 → e2
        rc = right_contraction(e1, e12)  # grade 1-2<0 → 0
        assert lc == e2
        assert np.allclose(rc.data, 0)

    def test_hestenes_vs_left_contraction_mixed_grade(self, cl3):
        """On mixed-grade multivectors, Hestenes and left contraction differ."""
        e1, e2, e3 = cl3.basis_vectors()
        # a = scalar + bivector, b = vector
        a = cl3.scalar(2.0) + (e1 ^ e2)
        b = e1
        lc = left_contraction(a, b)  # scalar⌋vector = 2*e1, bivector⌋vector = 0
        hi = hestenes_inner(a, b)  # scalar·anything = 0 in Hestenes, bivector·vector = -e2
        assert lc == 2 * e1
        assert hi == -e2


class TestUnaryOps:
    def test_reverse_vector(self, cl3):
        """Reverse of a vector is itself."""
        e1, _, _ = cl3.basis_vectors()
        assert reverse(e1) == e1

    def test_reverse_bivector(self, cl3):
        """Reverse of a bivector negates it."""
        e1, e2, _ = cl3.basis_vectors()
        e12 = e1 ^ e2
        assert reverse(e12) == -e12

    def test_reverse_product_identity(self, cl3):
        """reverse(a*b) == reverse(b) * reverse(a)."""
        e1, e2, e3 = cl3.basis_vectors()
        a = 1 + 2 * e1 + 3 * (e1 ^ e2)
        b = e2 + e3
        assert gp(reverse(b), reverse(a)) == reverse(gp(a, b))

    def test_involute(self, cl3):
        """Grade involution: negate odd grades, keep even."""
        e1, e2, _ = cl3.basis_vectors()
        e12 = e1 ^ e2
        mv = 1 + e1 + e12
        inv = involute(mv)
        # scalar unchanged, vector negated, bivector unchanged
        assert np.isclose(inv.data[0], 1.0)
        assert np.isclose(inv.data[1], -1.0)
        assert np.isclose(inv.data[3], 1.0)

    def test_conjugate(self, cl3):
        """Conjugate = involute(reverse(x))."""
        e1, _, _ = cl3.basis_vectors()
        # conjugate = involute(reverse(x))
        mv = 1 + e1
        assert conjugate(mv) == involute(reverse(mv))

    def test_tilde_operator(self, cl3):
        """~ operator maps to reverse()."""
        e1, e2, _ = cl3.basis_vectors()
        e12 = e1 ^ e2
        assert ~e12 == reverse(e12)


class TestGradeOps:
    def test_grade_projection(self, cl3):
        """Grade projection extracts each grade."""
        e1, e2, _ = cl3.basis_vectors()
        mv = 3 + 2 * e1 + (e1 ^ e2)
        assert grade(mv, 0) == cl3.scalar(3)
        assert grade(mv, 1) == 2 * e1
        assert grade(mv, 2) == e1 ^ e2

    def test_grade_idempotent(self, cl3):
        """Projecting twice gives the same result."""
        e1, e2, _ = cl3.basis_vectors()
        mv = 3 + 2 * e1 + (e1 ^ e2)
        assert grade(grade(mv, 1), 1) == grade(mv, 1)

    def test_grades_multi(self, cl3):
        """Multi-grade projection selects multiple grades."""
        e1, e2, _ = cl3.basis_vectors()
        mv = 3 + 2 * e1 + (e1 ^ e2)
        r = grades(mv, [0, 2])
        assert r == 3 + (e1 ^ e2)

    def test_scalar_extraction(self, cl3):
        """.scalar_part extracts grade-0 as float."""
        mv = cl3.scalar(7.0)
        assert mv.scalar_part == 7.0


class TestDualNormInverse:
    def test_dual_undual_roundtrip(self, cl3):
        """undual(dual(x)) = x."""
        e1, _, _ = cl3.basis_vectors()
        assert undual(dual(e1)) == e1

    def test_norm_basis_vector(self, cl3):
        """Basis vectors have unit norm."""
        e1, _, _ = cl3.basis_vectors()
        assert np.isclose(norm(e1), 1.0)

    def test_norm2_vector(self, cl3):
        """norm2 gives squared magnitude."""
        v = cl3.vector([3, 4, 0])
        assert np.isclose(norm2(v), 25.0)

    def test_unit(self, cl3):
        """unit() normalizes to norm 1."""
        v = cl3.vector([3, 4, 0])
        u = unit(v)
        assert np.isclose(norm(u), 1.0)

    def test_inverse_vector(self, cl3):
        """v * inverse(v) = 1."""
        e1, _, _ = cl3.basis_vectors()
        v = 2 * e1
        assert gp(v, inverse(v)) == cl3.scalar(1.0)

    def test_inverse_zero_raises(self, cl3):
        """Inverse of zero raises ValueError."""
        with pytest.raises(ValueError, match="not invertible"):
            inverse(cl3.scalar(0))


class TestPredicates:
    def test_is_scalar(self, cl3):
        """is_scalar detects pure grade-0."""
        assert is_scalar(cl3.scalar(5))
        assert not is_scalar(cl3.basis_vectors()[0])

    def test_is_vector(self, cl3):
        """is_vector detects pure grade-1."""
        assert is_vector(cl3.vector([1, 2, 3]))
        assert not is_vector(cl3.scalar(1))

    def test_is_bivector(self, cl3):
        """is_bivector detects pure grade-2."""
        e1, e2, _ = cl3.basis_vectors()
        assert is_bivector(e1 ^ e2)
        assert not is_bivector(e1)

    def test_is_even(self, cl3):
        """is_even detects even-graded MVs."""
        e1, e2, _ = cl3.basis_vectors()
        assert is_even(cl3.scalar(1) + (e1 ^ e2))
        assert not is_even(e1)


class TestAliases:
    def test_aliases(self, cl3):
        """Long-name aliases match short-name functions."""
        e1, e2, _ = cl3.basis_vectors()
        assert geometric_product(e1, e2) == gp(e1, e2)
        assert wedge(e1, e2) == op(e1, e2)
        assert rev(e1) == reverse(e1)


# ---- Golden tests: known identities ----


class TestGoldenCl2:
    """Known results in Cl(2,0)."""

    def test_complex_structure(self):
        """e12² = -1 in Cl(2,0) — complex structure."""
        alg = Algebra((1, 1))
        e1, e2 = alg.basis_vectors()
        e12 = e1 * e2
        # e12^2 = -1 (acts like imaginary unit)
        assert np.isclose((e12 * e12).scalar_part, -1.0)


class TestGoldenCl3:
    """Known results in Cl(3,0) — 3D Euclidean."""

    def test_cross_product_via_dual(self, cl3):
        """a × b = dual(a ∧ b) in 3D Euclidean (with our left-contraction dual)."""
        e1, e2, e3 = cl3.basis_vectors()
        # e1 × e2 should be e3
        w = op(e1, e2)
        cross = dual(w)
        assert cross == e3

    def test_rotation(self, cl3):
        """Rotate e1 by 90° in the e1e2 plane → e2."""
        e1, e2, e3 = cl3.basis_vectors()
        theta = np.pi / 2
        B = e1 ^ e2
        R = cl3.scalar(np.cos(theta / 2)) - np.sin(theta / 2) * B
        v_rot = gp(gp(R, e1), reverse(R))
        # Should be approximately e2
        assert np.allclose(v_rot.data, e2.data, atol=1e-12)


class TestGoldenSTA:
    """Known results in Cl(1,3) — Spacetime Algebra."""

    def test_timelike_spacelike(self, sta):
        """γ0²=+1 (timelike), γ1²=-1 (spacelike)."""
        vecs = sta.basis_vectors()
        # gamma_0^2 = +1
        assert np.isclose((vecs[0] * vecs[0]).scalar_part, 1.0)
        # gamma_1^2 = -1
        assert np.isclose((vecs[1] * vecs[1]).scalar_part, -1.0)

    def test_pseudoscalar_square(self, sta):
        """I^2 = -1 in Cl(1,3) with standard blade ordering."""
        I = sta.pseudoscalar()
        assert np.isclose((I * I).scalar_part, -1.0)


class TestExpLog:
    def test_exp_euclidean_bivector(self, cl3):
        """exp(B) produces a unit rotor."""
        e1, e2, _ = cl3.basis_vectors()
        B = (np.pi / 4) * (e1 ^ e2)
        R = exp(B)
        assert np.isclose((R * ~R).scalar_part, 1.0)

    def test_exp_matches_rotor(self, cl3):
        """exp(-θ/2 B) matches rotor(B, θ)."""
        e1, e2, _ = cl3.basis_vectors()
        theta = np.pi / 3
        R1 = cl3.rotor(e1 ^ e2, radians=theta)
        R2 = exp(-theta / 2 * (e1 ^ e2))
        assert np.allclose(R1.data, R2.data)

    def test_exp_null_bivector(self):
        """exp(B) = 1+B when B²=0 (PGA translation)."""
        pga = Algebra((1, 1, 1, 0))
        e1, e2, e3, e4 = pga.basis_vectors()
        B = e1 ^ e4  # degenerate direction, B² = 0
        R = exp(B)
        expected = pga.scalar(1.0) + B
        assert np.allclose(R.data, expected.data)

    def test_exp_timelike_bivector(self):
        """exp of timelike bivector gives unit rotor (cosh/sinh)."""
        sta = Algebra((1, -1, -1, -1))
        g0, g1, _, _ = sta.basis_vectors()
        B = 0.5 * (g0 * g1)  # timelike bivector, B² > 0
        R = exp(B)
        assert np.isclose((R * ~R).scalar_part, 1.0)

    def test_log_roundtrip(self, cl3):
        """log(exp(B)) = B."""
        e1, e2, _ = cl3.basis_vectors()
        B = 0.7 * (e1 ^ e2)
        R = exp(B)
        B_back = log(R)
        assert np.allclose(B.data, B_back.data, atol=1e-12)

    def test_exp_log_roundtrip(self, cl3):
        """exp(log(R)) = R."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor(e1 ^ e2, radians=1.2)
        R_back = exp(log(R))
        assert np.allclose(R.data, R_back.data, atol=1e-12)

    def test_log_identity(self, cl3):
        """log(1) = 0."""
        R = cl3.scalar(1.0)
        B = log(R)
        assert np.allclose(B.data, 0, atol=1e-12)


class TestProjectReject:
    def test_project_vector_onto_vector(self, cl3):
        """Project onto a vector keeps the parallel part."""
        e1, e2, _ = cl3.basis_vectors()
        v = 3 * e1 + 4 * e2
        p = project(v, e1)
        assert np.allclose(p.data, (3 * e1).data)

    def test_project_vector_onto_bivector(self, cl3):
        """Project onto a plane keeps the in-plane part."""
        e1, e2, e3 = cl3.basis_vectors()
        v = 3 * e1 + 4 * e2 + 5 * e3
        p = project(v, e1 ^ e2)
        assert np.allclose(p.data, (3 * e1 + 4 * e2).data)

    def test_reject_is_complement(self, cl3):
        """project + reject = original."""
        e1, e2, e3 = cl3.basis_vectors()
        v = 3 * e1 + 4 * e2 + 5 * e3
        B = e1 ^ e2
        p = project(v, B)
        r = reject(v, B)
        assert np.allclose((p + r).data, v.data)

    def test_reject_perpendicular(self, cl3):
        """Reject from a plane gives the perpendicular part."""
        e1, e2, e3 = cl3.basis_vectors()
        v = 3 * e1 + 4 * e2 + 5 * e3
        r = reject(v, e1 ^ e2)
        assert np.allclose(r.data, (5 * e3).data)


class TestReflect:
    def test_reflect_parallel(self, cl3):
        """Parallel component is negated."""
        e1, e2, _ = cl3.basis_vectors()
        # Reflecting e1 in hyperplane orthogonal to e1 → -e1
        r = reflect(e1, e1)
        assert np.allclose(r.data, (-e1).data)

    def test_reflect_perpendicular(self, cl3):
        """Perpendicular component is unchanged."""
        e1, e2, _ = cl3.basis_vectors()
        # Reflecting e2 in hyperplane orthogonal to e1 → e2 (unchanged)
        r = reflect(e2, e1)
        assert np.allclose(r.data, e2.data)

    def test_reflect_mixed(self, cl3):
        """Mixed vector: parallel negated, perp unchanged."""
        e1, e2, _ = cl3.basis_vectors()
        v = e1 + e2
        r = reflect(v, e1)
        assert np.allclose(r.data, (-e1 + e2).data)

    def test_reflect_involutory(self, cl3):
        """Double reflection is identity."""
        e1, e2, e3 = cl3.basis_vectors()
        v = 2 * e1 + 3 * e2 + e3
        n = unit(e1 + e2)
        # Double reflection is identity
        r = reflect(reflect(v, n), n)
        assert np.allclose(r.data, v.data, atol=1e-12)


class TestScalarSqrt:
    """scalar_sqrt() on scalar multivectors."""

    def test_perfect_square(self):
        """sqrt(9) = 3."""
        alg = Algebra((1, 1, 1))
        assert np.isclose((scalar_sqrt(alg.scalar(9.0))).scalar_part, 3.0)

    def test_non_perfect(self):
        """sqrt(2) ≈ 1.414."""
        alg = Algebra((1, 1, 1))
        assert np.isclose((scalar_sqrt(alg.scalar(2.0))).scalar_part, np.sqrt(2.0))

    def test_zero(self):
        """sqrt(0) = 0."""
        alg = Algebra((1, 1, 1))
        assert np.isclose((scalar_sqrt(alg.scalar(0.0))).scalar_part, 0.0)

    def test_one(self):
        """sqrt(1) = 1."""
        alg = Algebra((1, 1, 1))
        assert np.isclose((scalar_sqrt(alg.scalar(1.0))).scalar_part, 1.0)

    def test_rejects_vector(self):
        """Non-scalar input raises ValueError."""
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        with pytest.raises(ValueError, match="pure scalar"):
            scalar_sqrt(e1)

    def test_rejects_negative(self):
        """Negative scalar raises ValueError."""
        alg = Algebra((1, 1, 1))
        with pytest.raises(ValueError, match="negative"):
            scalar_sqrt(alg.scalar(-4.0))

    def test_returns_multivector(self):
        """Result is a Multivector, not a float."""
        alg = Algebra((1, 1, 1))
        result = scalar_sqrt(alg.scalar(4.0))
        assert isinstance(result, Multivector)

    def test_roundtrip_with_squared(self):
        """scalar_sqrt(v*v) recovers norm for a vector."""
        alg = Algebra((1, 1, 1))
        v = alg.vector([3, 4, 0])
        assert np.isclose((scalar_sqrt(alg.scalar(norm2(v)))).scalar_part, norm(v))

    def test_accepts_float(self):
        """scalar_sqrt(9.0) returns 3.0."""
        assert np.isclose(scalar_sqrt(9.0), 3.0)

    def test_accepts_int(self):
        """scalar_sqrt(16) returns 4."""
        assert scalar_sqrt(16) == 4

    def test_float_negative_raises(self):
        """scalar_sqrt(-1.0) raises ValueError."""
        with pytest.raises(ValueError, match="negative"):
            scalar_sqrt(-1.0)

    def test_bad_type_raises(self):
        """scalar_sqrt('hello') raises TypeError."""
        with pytest.raises(TypeError):
            scalar_sqrt("hello")


class TestScalarSqrtSymbolic:
    """scalar_sqrt() symbolic rendering."""

    def test_lazy_builds_tree(self):
        """scalar_sqrt of lazy MV returns lazy with Sqrt expr."""
        alg = Algebra((1, 1, 1))
        s = alg.scalar(9.0).name("s")
        result = scalar_sqrt(s)
        assert result._is_lazy
        assert result._expr is not None

    def test_unicode_rendering(self):
        """Renders as √(s) in unicode."""
        alg = Algebra((1, 1, 1))
        s = alg.scalar(9.0).name("s")
        assert "√" in str(scalar_sqrt(s))

    def test_latex_rendering(self):
        """Renders as \\sqrt{s} in LaTeX."""
        alg = Algebra((1, 1, 1))
        s = alg.scalar(9.0).name("s")
        assert r"\sqrt{s}" in scalar_sqrt(s).latex()

    def test_compound_expression(self):
        """√(m² + p²) renders correctly."""
        alg = Algebra((1, 1, 1))
        m = alg.scalar(3.0).name("m")
        p = alg.scalar(4.0).name("p")
        E = scalar_sqrt(m**2 + p**2)
        assert r"\sqrt" in E.latex()
        assert np.isclose((E.eval()).scalar_part, 5.0)

    def test_display_dedup(self):
        """display() shows name = expr = value without duplicates."""
        alg = Algebra((1, 1, 1))
        m = alg.scalar(3.0).name("m")
        p = alg.scalar(4.0).name("p")
        E = scalar_sqrt(m**2 + p**2).name("E")
        d = E.display().latex()
        assert "E" in d
        assert r"\sqrt" in d
        assert "5" in d


class TestNearUnitCoefficientSuppression:
    """Coefficients very close to ±1 should be suppressed in display."""

    def test_near_minus_one_str(self):
        """Coefficient -0.9999999999999998 displays as -e₂ not -1e₂."""
        import numpy as np

        from galaga import Algebra, exp

        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        B = e1 ^ e2
        R = exp(-B * alg.scalar(np.radians(180)) / 2)
        vp = (R * (e1 + e2) * ~R).eval()
        s = str(vp)
        assert "-1e" not in s
        assert s == "-e₁ - e₂"

    def test_near_minus_one_latex(self):
        """Same check for LaTeX rendering."""
        import numpy as np

        from galaga import Algebra, exp

        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        B = e1 ^ e2
        R = exp(-B * alg.scalar(np.radians(180)) / 2)
        vp = (R * (e1 + e2) * ~R).eval()
        latex = vp.latex()
        assert "-1 e" not in latex
        assert latex == "-e_{1} - e_{2}"
