"""Tests for the ga library — golden tests and property tests."""

import numpy as np
import pytest

from galaga import (
    Algebra,
    Multivector,
    b_default,
    b_gamma,
    b_sta,
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
    outercos,
    outerexp,
    outersin,
    outertan,
    project,
    reflect,
    reject,
    rev,
    reverse,
    right_contraction,
    scalar_product,
    scalar_sqrt,
    sqrt,
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

    def test_pqr_euclidean(self):
        """Algebra(3) == Algebra((1,1,1))."""
        assert Algebra(3).signature == (1, 1, 1)

    def test_pqr_sta(self):
        """Algebra(1, 3) == Algebra((1,-1,-1,-1))."""
        assert Algebra(1, 3).signature == (1, -1, -1, -1)

    def test_pqr_pga(self):
        """Algebra(3, 0, 1) places null first: (0,1,1,1)."""
        assert Algebra(3, 0, 1).signature == (0, 1, 1, 1)

    def test_pqr_p_only(self):
        """Algebra(0) gives the trivial algebra."""
        assert Algebra(0).signature == ()
        assert Algebra(0).dim == 1

    def test_pqr_with_blades(self):
        """Algebra(1, 3, blades=b_gamma()) works."""
        sta = Algebra(1, 3, blades=b_gamma())
        assert sta.signature == (1, -1, -1, -1)
        e0, _, _, _ = sta.basis_vectors()
        assert "γ" in str(e0)

    def test_pqr_matches_signature_form(self):
        """Algebra(p,q,r) produces same multiplication tables as Algebra(sig)."""
        a1 = Algebra(2, 1, 1)
        a2 = Algebra((0, 1, 1, -1))
        assert np.array_equal(a1._mul_sign, a2._mul_sign)

    def test_constructor_string_raises(self):
        """String as first arg raises TypeError."""
        with pytest.raises(TypeError, match="signature tuple/list or an int"):
            Algebra("hello")

    def test_constructor_float_raises(self):
        """Float as p raises TypeError."""
        with pytest.raises(TypeError, match="signature tuple/list or an int"):
            Algebra(3.0)

    def test_constructor_float_q_raises(self):
        """Float as q raises TypeError."""
        with pytest.raises(TypeError, match="q and r must be integers"):
            Algebra(3, 1.5)

    def test_constructor_negative_p_raises(self):
        """Negative p raises ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            Algebra(-1)

    def test_constructor_bool_raises(self):
        """Bool raises TypeError (not treated as int)."""
        with pytest.raises(TypeError, match="got bool"):
            Algebra(True)

    def test_constructor_bad_sig_value_raises(self):
        """Signature with value other than +1/-1/0 raises ValueError."""
        with pytest.raises(ValueError, match="must be .1, -1, or 0"):
            Algebra([1, 2, -1])

    def test_constructor_sig_with_q_raises(self):
        """Passing q with an explicit signature raises TypeError."""
        with pytest.raises(TypeError, match="q and r cannot be used"):
            Algebra((1, 1), 1)

    def test_constructor_none_raises(self):
        """None raises TypeError."""
        with pytest.raises(TypeError, match="signature tuple/list or an int"):
            Algebra(None)

    def test_constructor_fractional_sig_raises(self):
        """Signature with 0.5 raises ValueError (not silently truncated)."""
        with pytest.raises(ValueError, match="must be .1, -1, or 0"):
            Algebra([1, -1, 0.5])

    def test_constructor_float_sig_coerced(self):
        """Float signature values 1.0/-1.0/0.0 are coerced to int."""
        alg = Algebra([1.0, -1.0, 0.0])
        assert alg.signature == (1, -1, 0)

    def test_constructor_float_q_exact_raises(self):
        """Float q even if whole number raises TypeError."""
        with pytest.raises(TypeError, match="q and r must be integers"):
            Algebra(1, 1.0)

    def test_tuple_preserves_ordering(self):
        """Tuple constructor preserves exact basis ordering."""
        alg = Algebra([1, -1, 0])
        assert alg.signature == (1, -1, 0)
        sqs = [gp(e, e).scalar_part for e in alg.basis_vectors()]
        assert sqs == [1.0, -1.0, 0.0]

    def test_tuple_null_first(self):
        """Tuple with null first is not reordered."""
        alg = Algebra((0, 1, 1))
        assert alg.signature == (0, 1, 1)

    def test_tuple_exotic_metric(self):
        """Exotic interleaved metric preserves ordering."""
        sig = (0, 1, 0, 1, 0, -1, 0, -1)
        alg = Algebra(sig)
        assert alg.signature == sig
        sqs = [gp(e, e).scalar_part for e in alg.basis_vectors()]
        assert sqs == [float(s) for s in sig]

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

    def test_basis_blades_grade1(self, cl3):
        """basis_blades(1) returns the same blades as basis_vectors()."""
        vecs = cl3.basis_vectors()
        blades = cl3.basis_blades(1)
        assert len(blades) == len(vecs)
        for v, b in zip(vecs, blades):
            assert np.array_equal(v.data, b.data)

    def test_basis_blades_grade2(self, cl3):
        """basis_blades(2) returns all 3 bivectors in Cl(3,0)."""
        bivectors = cl3.basis_blades(2)
        assert len(bivectors) == 3
        # e12=0b011=3, e13=0b101=5, e23=0b110=6
        assert bivectors[0].data[3] == 1.0
        assert bivectors[1].data[5] == 1.0
        assert bivectors[2].data[6] == 1.0

    def test_basis_blades_grade0_and_max(self, cl3):
        """basis_blades(0) is the scalar, basis_blades(n) is the pseudoscalar."""
        scalars = cl3.basis_blades(0)
        assert len(scalars) == 1
        assert scalars[0].data[0] == 1.0
        trivectors = cl3.basis_blades(3)
        assert len(trivectors) == 1
        assert trivectors[0].data[7] == 1.0

    def test_basis_blades_lazy(self, cl3):
        """basis_blades with lazy=True returns lazy multivectors."""
        e12, e13, e23 = cl3.basis_blades(2, lazy=True)
        assert e12._is_symbolic

    def test_locals_all(self, cl3):
        """locals() returns all non-scalar blades keyed by Python local name."""
        d = cl3.locals()
        assert set(d.keys()) == {"e1", "e2", "e3", "e12", "e13", "e23", "e123"}
        assert d["e12"].data[3] == 1.0

    def test_locals_filtered(self, cl3):
        """locals(grades=[1]) returns only vectors."""
        d = cl3.locals(grades=[1])
        assert set(d.keys()) == {"e1", "e2", "e3"}

    def test_locals_lazy(self, cl3):
        """locals(lazy=True) returns lazy multivectors."""
        d = cl3.locals(lazy=True)
        assert d["e1"]._is_symbolic

    def test_locals_gamma_convention(self):
        """locals() uses compact Python names derived from the blade convention."""
        alg = Algebra(1, 3, blades=b_gamma())
        d = alg.locals(grades=[1])
        assert set(d.keys()) == {"g0", "g1", "g2", "g3"}

    def test_locals_gamma_prefix_override(self):
        """locals(prefix=...) overrides generated Python names, not rendering."""
        alg = Algebra(1, 3, blades=b_gamma())
        d = alg.locals(grades=[1, 2], prefix="g")

        assert {"g0", "g1", "g2", "g3"}.issubset(d)
        assert "g01" in d
        assert "y0" not in d
        assert str(d["g0"]) == "γ₀"
        assert str(d["g01"]) == "γ₀γ₁"

    def test_locals_prefix_override_applies_uniformly(self):
        """prefix= applies to all blades without variable hints, including those with display overrides."""
        alg = Algebra(1, 3, blades=b_sta(sigmas=True))
        d = alg.locals(prefix="g")

        # All blades use the g prefix uniformly (display overrides like σ don't affect locals)
        assert {"g0", "g1", "g2", "g3"}.issubset(d)
        assert "g01" in d  # was σ₁ in display, but local is g01
        assert "s1" not in d  # display override does NOT leak into locals
        assert "y0" not in d
        # PSS comes from variable_hint on b_sta()
        assert "i" in d

    def test_locals_empty_prefix_override_uses_suffixes(self):
        """An empty prefix is valid for named-axis notebook variables."""
        alg = Algebra(3, blades=b_default(subscripts="xyz"))
        d = alg.locals(prefix="")

        assert list(d.keys()) == ["x", "y", "xy", "z", "xz", "yz", "xyz"]

    def test_locals_prefix_must_be_string(self):
        """locals(prefix=...) is a Python-local prefix, not an arbitrary label."""
        alg = Algebra(1, 3, blades=b_sta(sigmas=True))

        with pytest.raises(TypeError, match="prefix must be a string or None"):
            alg.locals(grades=[2], prefix=123)

    def test_locals_wedge_display_uses_compact_python_keys(self):
        """locals() keys are Python names, not blade-rendering names."""
        from galaga.blade_convention import BladeConvention

        alg = Algebra(
            3,
            blades=BladeConvention(
                prefix="v",
                style="wedge",
                overrides={"pss": "I"},
                variable_hints={"pss": "I"},
            ),
        )
        d = alg.locals()

        assert list(d.keys()) == ["v1", "v2", "v12", "v3", "v13", "v23", "I"]
        assert all(name.isidentifier() for name in d)
        assert str(d["v12"]) == "v₁∧v₂"
        assert str(d["I"]) == "I"

    def test_locals_juxtapose_display_uses_compact_python_keys(self):
        """Juxtapose rendering should not produce local names like e1e2."""
        alg = Algebra(3, blades=b_default(style="juxtapose"))
        d = alg.locals()

        assert "e12" in d
        assert "e1e2" not in d
        assert str(d["e12"]) == "e₁e₂"

    def test_locals_preserves_safe_explicit_aliases(self):
        """Variable hints provide idiomatic local names independent of display."""
        from galaga.blade_convention import BladeConvention

        alg = Algebra(
            3,
            blades=BladeConvention(
                overrides={"+1+2": "B", "pss": "I"},
                variable_hints={"+1+2": "B", "pss": "I"},
            ),
        )
        d = alg.locals()

        assert "B" in d
        assert "I" in d

    def test_locals_display_overrides_dont_affect_keys(self):
        """Display overrides no longer leak into locals() keys."""
        alg = Algebra(3, blades=b_default(overrides={"+1+2": "class"}))
        d = alg.locals()

        # Display override "class" does NOT become a local key
        assert "_class" not in d
        assert "class" not in d
        # Instead the blade gets its prefix+subscript name
        assert "e12" in d

    def test_locals_respects_blade_sign(self):
        """locals() applies BasisBlade.sign so σ₁ = γ₁γ₀ has correct coefficient."""
        alg = Algebra(1, 3, blades=b_sta(sigmas=True))
        g0, g1, g2, g3 = alg.basis_vectors()
        d = alg.locals(grades=[2])
        # Blade at bitmask 0b0011 (γ₀∧γ₁) has sign from σ₁ = γ₁γ₀ convention
        assert d["g01"] == g1 * g0  # σ₁ = γ₁γ₀
        assert d["g02"] == g2 * g0
        assert d["g03"] == g3 * g0

    def test_basis_blades_respects_blade_sign(self):
        """basis_blades() applies BasisBlade.sign for signed conventions."""
        alg = Algebra(1, 3, blades=b_sta(sigmas=True))
        g0, g1, g2, g3 = alg.basis_vectors()
        bivs = alg.basis_blades(2)
        # First bivector (bitmask 0b0011 = γ₀γ₁) should equal γ₁γ₀ = σ₁
        assert bivs[0] == g1 * g0

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
        sta = Algebra((1, -1, -1, -1), blades=b_gamma(), repr_unicode=True)
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


class TestGeneralInverse:
    """General multivector inverse via Hitzer (d≤5) / Shirokov (d≥6)."""

    def test_inverse_general_mv_cl3(self, cl3):
        """General MV inverse in Cl(3,0): (1 + e1 + e12 + e123) has a true inverse."""
        e1, e2, e3 = cl3.basis_vectors()
        mv = cl3.scalar(1) + e1 + (e1 ^ e2) + (e1 ^ e2 ^ e3)
        assert np.allclose(gp(mv, inverse(mv)).data, cl3.scalar(1.0).data)

    def test_inverse_d0(self):
        """Scalar inverse in Cl(0,0)."""
        cl0 = Algebra(())
        s = cl0.scalar(3.0)
        assert np.allclose(gp(s, inverse(s)).data, cl0.scalar(1.0).data)

    def test_inverse_d1(self):
        """General MV inverse in Cl(1,0)."""
        cl1 = Algebra((1,))
        (e1,) = cl1.basis_vectors()
        mv = cl1.scalar(2) + 3 * e1
        assert np.allclose(gp(mv, inverse(mv)).data, cl1.scalar(1.0).data)

    def test_inverse_d2(self):
        """General MV inverse in Cl(2,0)."""
        cl2 = Algebra((1, 1))
        e1, e2 = cl2.basis_vectors()
        mv = cl2.scalar(1) + 2 * e1 + 3 * e2 + 4 * (e1 ^ e2)
        assert np.allclose(gp(mv, inverse(mv)).data, cl2.scalar(1.0).data)

    def test_inverse_d4_sta(self):
        """General MV inverse in Cl(1,3) (STA)."""
        sta = Algebra((1, -1, -1, -1))
        e0, e1, e2, e3 = sta.basis_vectors()
        mv = sta.scalar(2) + e0 + e1 + (e0 ^ e1) + (e1 ^ e2 ^ e3)
        assert np.allclose(gp(mv, inverse(mv)).data, sta.scalar(1.0).data)

    def test_inverse_d5(self):
        """General MV inverse in Cl(5,0)."""
        cl5 = Algebra((1, 1, 1, 1, 1))
        es = cl5.basis_vectors()
        mv = cl5.scalar(2) + es[0] + 0.5 * (es[0] ^ es[1])
        assert np.allclose(gp(mv, inverse(mv)).data, cl5.scalar(1.0).data)

    def test_inverse_d6_shirokov(self):
        """General MV inverse in Cl(6,0) uses Shirokov algorithm."""
        cl6 = Algebra((1, 1, 1, 1, 1, 1))
        es = cl6.basis_vectors()
        mv = cl6.scalar(3) + 2 * es[0] + es[1] + 0.5 * (es[0] ^ es[2])
        assert np.allclose(gp(mv, inverse(mv)).data, cl6.scalar(1.0).data)

    def test_inverse_versor_still_works(self, cl3):
        """Versor inverse still works (rotor)."""
        e1, e2, _ = cl3.basis_vectors()
        R = exp(0.5 * (e1 ^ e2))
        assert np.allclose(gp(R, inverse(R)).data, cl3.scalar(1.0).data)

    def test_inverse_non_invertible_raises(self, cl3):
        """Non-invertible MV raises ValueError."""
        with pytest.raises(ValueError, match="not invertible"):
            inverse(cl3.scalar(0))

    def test_inverse_pga_versor(self):
        """Versor inverse in PGA Cl(3,0,1)."""
        pga = Algebra((1, 1, 1, 0))
        e1, e2, _, _ = pga.basis_vectors()
        v = 2 * e1 + 3 * e2
        assert np.allclose(gp(v, inverse(v)).data, pga.scalar(1.0).data)

    def test_inverse_right_inverse(self, cl3):
        """inv(x) * x = 1 (right inverse = left inverse)."""
        e1, e2, e3 = cl3.basis_vectors()
        mv = cl3.scalar(1) + e1 + (e1 ^ e2) + (e1 ^ e2 ^ e3)
        assert np.allclose(gp(inverse(mv), mv).data, cl3.scalar(1.0).data)

    def test_inverse_pga_null_vector_raises(self):
        """Null vector in PGA is not invertible."""
        pga = Algebra((1, 1, 1, 0))
        _, _, _, e0 = pga.basis_vectors()
        with pytest.raises(ValueError, match="not invertible"):
            inverse(e0)

    def test_inverse_non_invertible_shirokov_raises(self):
        """Non-invertible MV in d≥6 raises ValueError."""
        cl6 = Algebra((1, 1, 1, 1, 1, 1))
        with pytest.raises(ValueError, match="not invertible"):
            inverse(cl6.scalar(0))

    def test_inverse_pure_scalar(self, cl3):
        """Inverse of a pure scalar in a higher-dim algebra."""
        s = cl3.scalar(5.0)
        assert np.allclose(gp(s, inverse(s)).data, cl3.scalar(1.0).data)

    def test_inverse_roundtrip(self, cl3):
        """inverse(inverse(x)) == x."""
        e1, e2, e3 = cl3.basis_vectors()
        mv = cl3.scalar(1) + e1 + (e1 ^ e2) + (e1 ^ e2 ^ e3)
        assert np.allclose(inverse(inverse(mv)).data, mv.data)

    def test_inverse_via_property(self, cl3):
        """.inv property uses the general inverse."""
        e1, e2, e3 = cl3.basis_vectors()
        mv = cl3.scalar(1) + e1 + (e1 ^ e2) + (e1 ^ e2 ^ e3)
        assert np.allclose(gp(mv, mv.inv).data, cl3.scalar(1.0).data)

    def test_inverse_via_pow(self, cl3):
        """x**-1 uses the general inverse."""
        e1, e2, e3 = cl3.basis_vectors()
        mv = cl3.scalar(1) + e1 + (e1 ^ e2) + (e1 ^ e2 ^ e3)
        assert np.allclose(gp(mv, mv**-1).data, cl3.scalar(1.0).data)


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


class TestOuterTranscendentals:
    """Outer (wedge) exponential, sine, cosine, tangent."""

    def test_outerexp_simple_bivector(self, cl3):
        """outerexp(B) = 1 + B for a simple bivector (B∧B = 0)."""
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        assert np.allclose(outerexp(B).data, (cl3.scalar(1) + B).data)

    def test_outerexp_vector(self, cl3):
        """outerexp(v) = 1 + v for any vector (v∧v = 0)."""
        e1, _, _ = cl3.basis_vectors()
        assert np.allclose(outerexp(e1).data, (cl3.scalar(1) + e1).data)

    def test_outerexp_non_simple_bivector(self):
        """outerexp of non-simple bivector in 4D includes B∧B/2 term."""
        cl4 = Algebra((1, 1, 1, 1))
        es = cl4.basis_vectors()
        B = (es[0] ^ es[1]) + (es[2] ^ es[3])
        oe = outerexp(B)
        expected = cl4.scalar(1) + B + op(B, B) / 2
        assert np.allclose(oe.data, expected.data)

    def test_outerexp_equals_cos_plus_sin(self):
        """outerexp(x) = outercos(x) + outersin(x)."""
        cl4 = Algebra((1, 1, 1, 1))
        es = cl4.basis_vectors()
        B = (es[0] ^ es[1]) + (es[2] ^ es[3])
        assert np.allclose(outerexp(B).data, (outercos(B) + outersin(B)).data)

    def test_outercos_even_grades(self):
        """outercos contains only even-grade terms."""
        cl4 = Algebra((1, 1, 1, 1))
        es = cl4.basis_vectors()
        B = (es[0] ^ es[1]) + (es[2] ^ es[3])
        oc = outercos(B)
        for k in range(cl4.n + 1):
            if k % 2 == 1:
                assert np.allclose(grade(oc, k).data, 0)

    def test_outersin_odd_grades(self):
        """outersin contains only odd-grade terms (relative to input grade)."""
        cl4 = Algebra((1, 1, 1, 1))
        es = cl4.basis_vectors()
        B = (es[0] ^ es[1]) + (es[2] ^ es[3])
        os_ = outersin(B)
        # B is grade 2, so outersin has grade 2 only (B^B^B would be grade 6, beyond dim)
        assert np.allclose(os_.data, B.data)

    def test_outertan_simple(self, cl3):
        """outertan(B) = B for a simple bivector (outercos = 1)."""
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        assert np.allclose(outertan(B).data, B.data)

    def test_outertan_non_invertible_cos_raises(self):
        """outertan raises when outercos is not invertible."""
        cl4 = Algebra((1, 1, 1, 1))
        es = cl4.basis_vectors()
        B = (es[0] ^ es[1]) + (es[2] ^ es[3])
        with pytest.raises(ValueError, match="not invertible"):
            outertan(B)

    def test_outerexp_scalar(self, cl3):
        """outerexp(0) = 1."""
        assert np.allclose(outerexp(cl3.scalar(0)).data, cl3.scalar(1).data)


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


class TestExpNonSimpleBivector:
    """exp() must handle non-simple bivectors correctly (n >= 4). GH #11."""

    def _taylor_exp(self, B, N=40):
        """Ground-truth exp via Taylor series."""
        alg = B.algebra
        R = alg.scalar(1.0)
        term = alg.scalar(1.0)
        for k in range(1, N):
            term = term * B * alg.scalar(1.0 / k)
            R = R + term
            if np.max(np.abs(term.data)) < 1e-15:
                break
        return R

    def test_cl40_commuting_orthogonal_planes(self):
        """exp(0.3·e12 + 0.5·e34) in Cl(4,0) must include the e1234 cross term."""
        alg = Algebra(4)
        e = alg.basis_vectors()
        B = 0.3 * (e[0] * e[1]) + 0.5 * (e[2] * e[3])
        R = exp(B)
        R_expected = self._taylor_exp(B)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_cl41_commuting_orthogonal_planes(self):
        """exp(0.3·e12 + 0.5·e34) in Cl(4,1) — same bug, different algebra."""
        alg = Algebra(4, 1)
        e = alg.basis_vectors()
        B = 0.3 * (e[0] * e[1]) + 0.5 * (e[2] * e[3])
        R = exp(B)
        R_expected = self._taylor_exp(B)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_cl13_boost_plus_rotation(self):
        """STA boost + rotation in orthogonal planes: exp(0.5·γ₀γ₁ + 0.3·γ₂γ₃)."""
        alg = Algebra(1, 3)
        e = alg.basis_vectors()
        B = 0.5 * (e[0] * e[1]) + 0.3 * (e[2] * e[3])
        R = exp(B)
        R_expected = self._taylor_exp(B)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_cl22_commuting_orthogonal_planes(self):
        """Cl(2,2) with commuting bivectors in disjoint planes."""
        alg = Algebra(2, 2)
        e = alg.basis_vectors()
        B = 0.3 * (e[0] * e[1]) + 0.5 * (e[2] * e[3])
        R = exp(B)
        R_expected = self._taylor_exp(B)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_result_is_rotor(self):
        """exp(B) must satisfy R·~R = 1 for any bivector B."""
        alg = Algebra(4, 1)
        e = alg.basis_vectors()
        B = 0.3 * (e[0] * e[1]) + 0.5 * (e[2] * e[3]) + 0.1 * (e[0] * e[4])
        R = exp(B)
        RRr = R * reverse(R)
        assert np.isclose(RRr.scalar_part, 1.0, atol=1e-10)
        assert np.allclose(RRr.data[1:], 0, atol=1e-10)

    def test_product_of_individual_exps(self):
        """For commuting B1, B2: exp(B1+B2) = exp(B1)·exp(B2)."""
        alg = Algebra(4)
        e = alg.basis_vectors()
        B1 = 0.3 * (e[0] * e[1])
        B2 = 0.5 * (e[2] * e[3])
        R_sum = exp(B1 + B2)
        R_product = exp(B1) * exp(B2)
        assert np.allclose(R_sum.data, R_product.data, atol=1e-10)

    def test_simple_bivectors_unchanged(self):
        """Simple bivectors must still work (regression guard)."""
        alg = Algebra(4)
        e = alg.basis_vectors()
        B = 0.7 * (e[0] * e[1])
        R = exp(B)
        expected = alg.scalar(np.cos(0.7)) + np.sin(0.7) * (e[0] * e[1])
        assert np.allclose(R.data, expected.data, atol=1e-10)

    def test_3d_bivector_unchanged(self):
        """In Cl(3,0) all bivectors are simple — must still be correct."""
        alg = Algebra(3)
        e = alg.basis_vectors()
        B = 0.3 * (e[0] * e[1]) + 0.5 * (e[1] * e[2])
        R = exp(B)
        R_expected = self._taylor_exp(B)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    @pytest.mark.parametrize("seed", range(5))
    def test_random_bivector_cl41(self, seed):
        """Random bivectors in Cl(4,1) must match Taylor and produce valid rotors."""
        alg = Algebra(4, 1)
        np.random.seed(seed)
        e = alg.basis_vectors()
        B = alg.scalar(0.0)
        for i in range(5):
            for j in range(i + 1, 5):
                B = B + np.random.uniform(-0.5, 0.5) * (e[i] * e[j])
        R = exp(B)
        R_expected = self._taylor_exp(B, N=80)
        assert np.allclose(R.data, R_expected.data, atol=1e-10), "exp(B) differs from Taylor"
        RRr = R * reverse(R)
        assert np.isclose(RRr.scalar_part, 1.0, atol=1e-10), f"R~R scalar = {RRr.scalar_part}"
        assert np.allclose(RRr.data[1:], 0, atol=1e-10), "R~R has non-scalar components"


class TestExpGeneralInputs:
    """exp() on non-bivector inputs: vectors, scalars, mixed-grade, pseudoscalars."""

    def _taylor_exp(self, X, N=50):
        """Ground-truth exp via Taylor series."""
        alg = X.algebra
        R = alg.scalar(1.0)
        term = alg.scalar(1.0)
        for k in range(1, N):
            term = term * X * alg.scalar(1.0 / k)
            R = R + term
            if np.max(np.abs(term.data)) < 1e-15:
                break
        return R

    # ── Scalars ──

    def test_exp_positive_scalar(self):
        """exp(a) = e^a for positive scalar."""
        alg = Algebra(3)
        assert np.isclose(exp(alg.scalar(2.0)).scalar_part, np.exp(2.0))

    def test_exp_negative_scalar(self):
        """exp(a) = e^a for negative scalar."""
        alg = Algebra(3)
        assert np.isclose(exp(alg.scalar(-1.5)).scalar_part, np.exp(-1.5))

    def test_exp_zero_scalar(self):
        """exp(0) = 1."""
        alg = Algebra(3)
        R = exp(alg.scalar(0.0))
        assert np.isclose(R.scalar_part, 1.0)
        assert np.allclose(R.data[1:], 0)

    # ── Vectors ──

    def test_exp_euclidean_vector(self):
        """exp(v) for v²>0 gives cosh+sinh form."""
        alg = Algebra(3)
        e1 = alg.basis_vectors()[0]
        v = 0.7 * e1  # v² = 0.49 > 0
        R = exp(v)
        expected = alg.scalar(np.cosh(0.7)) + np.sinh(0.7) * e1
        assert np.allclose(R.data, expected.data, atol=1e-10)

    def test_exp_antieuclidean_vector(self):
        """exp(v) for v²<0 gives cos+sin form."""
        alg = Algebra(1, 3)
        e1 = alg.basis_vectors()[1]  # spacelike, e1²=-1
        v = 0.7 * e1
        R = exp(v)
        R_expected = self._taylor_exp(v)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_exp_null_vector(self):
        """exp(v) for v²=0 gives 1+v."""
        pga = Algebra(2, 0, 1)
        e = pga.basis_vectors()
        v = e[0]  # null vector, e0²=0 (degenerate direction comes first)
        R = exp(v)
        expected = pga.scalar(1.0) + v
        assert np.allclose(R.data, expected.data)

    def test_exp_vector_sum_cl3(self):
        """exp(e1+e2) in Cl(3,0) where (e1+e2)²=2."""
        alg = Algebra(3)
        e = alg.basis_vectors()
        v = e[0] + e[1]
        R = exp(v)
        R_expected = self._taylor_exp(v)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    # ── Pseudoscalar ──

    def test_exp_pseudoscalar_cl3(self):
        """exp(I) in Cl(3,0) where I²=-1."""
        alg = Algebra(3)
        e = alg.basis_vectors()
        I = e[0] * e[1] * e[2]
        R = exp(I)
        expected = alg.scalar(np.cos(1.0)) + np.sin(1.0) * I
        assert np.allclose(R.data, expected.data, atol=1e-10)

    def test_exp_pseudoscalar_sta(self):
        """exp(I) in Cl(1,3) where I²=-1."""
        sta = Algebra(1, 3)
        e = sta.basis_vectors()
        I = e[0] * e[1] * e[2] * e[3]
        R = exp(I)
        R_expected = self._taylor_exp(I)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_exp_pseudoscalar_cl4(self):
        """exp(I) in Cl(4,0) where I²=+1."""
        alg = Algebra(4)
        e = alg.basis_vectors()
        I = e[0] * e[1] * e[2] * e[3]
        R = exp(I)
        # I²=+1 → exp(I) = cosh(1) + sinh(1)*I
        expected = alg.scalar(np.cosh(1.0)) + np.sinh(1.0) * I
        assert np.allclose(R.data, expected.data, atol=1e-10)

    # ── Mixed grade ──

    def test_exp_scalar_plus_vector(self):
        """exp(1 + e1) in Cl(3,0) — mixed grade, X² non-scalar."""
        alg = Algebra(3)
        e = alg.basis_vectors()
        X = alg.scalar(1.0) + e[0]
        R = exp(X)
        R_expected = self._taylor_exp(X)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_exp_vector_plus_bivector(self):
        """exp(e1 + e12) in Cl(3,0) — mixed odd+even grade."""
        alg = Algebra(3)
        e = alg.basis_vectors()
        X = e[0] + e[0] * e[1]
        R = exp(X)
        R_expected = self._taylor_exp(X)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_exp_scalar_plus_bivector(self):
        """exp(1 + e12) in Cl(3,0) — scalar + bivector."""
        alg = Algebra(3)
        e = alg.basis_vectors()
        X = alg.scalar(1.0) + e[0] * e[1]
        R = exp(X)
        R_expected = self._taylor_exp(X)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_exp_mixed_grade_sta(self):
        """exp(1 + γ₀) in Cl(1,3) — scalar + timelike vector."""
        sta = Algebra(1, 3)
        e = sta.basis_vectors()
        X = sta.scalar(1.0) + e[0]
        R = exp(X)
        R_expected = self._taylor_exp(X)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_exp_mixed_scalar_bivector_pseudoscalar_cl3(self):
        """exp(scalar + bivector + pseudoscalar) in Cl(3,0)."""
        alg = Algebra(3)
        e = alg.basis_vectors()
        I = e[0] * e[1] * e[2]
        X = alg.scalar(0.5) + 0.3 * (e[0] * e[1]) + 0.2 * I
        R = exp(X)
        R_expected = self._taylor_exp(X)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    # ── Trivectors and higher ──

    def test_exp_trivector_positive_square(self):
        """exp(trivector) with X²>0."""
        sta = Algebra(1, 3)
        e = sta.basis_vectors()
        X = e[1] * e[2] * e[3]  # grade-3
        R = exp(X)
        R_expected = self._taylor_exp(X)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_exp_trivector_negative_square(self):
        """exp(trivector) with X²<0."""
        sta = Algebra(1, 3)
        e = sta.basis_vectors()
        X = e[0] * e[1] * e[2]  # grade-3, involves timelike
        R = exp(X)
        R_expected = self._taylor_exp(X)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    def test_exp_non_simple_trivector_cl5(self):
        """exp(pure grade-3 X) in Cl(5,0) where X² has a grade-4 part."""
        alg = Algebra(5)
        e = alg.basis_vectors()
        X = (e[0] * e[1] * e[2]) + (e[0] * e[3] * e[4])
        X2 = X * X

        assert np.allclose(grade(X, 3).data, X.data)
        assert np.max(np.abs(grade(X2, 4).data)) > 1e-12

        R = exp(X)
        R_expected = self._taylor_exp(X, N=80)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    # ── Small coefficients (ħ-scale) ──

    def test_exp_tiny_bivector(self):
        """exp(ε·B) ≈ 1 + ε·B for very small ε."""
        alg = Algebra(3)
        e = alg.basis_vectors()
        eps = 1e-30
        B = eps * (e[0] * e[1])
        R = exp(B)
        expected = alg.scalar(1.0) + B  # cos(ε)≈1, sin(ε)≈ε
        assert np.allclose(R.data, expected.data, atol=1e-40)

    def test_exp_tiny_non_simple(self):
        """exp(ε·(e12+e34)) for ħ-scale ε still produces valid rotor."""
        alg = Algebra(4)
        e = alg.basis_vectors()
        eps = 1e-30
        B = eps * (e[0] * e[1]) + eps * (e[2] * e[3])
        R = exp(B)
        R_expected = self._taylor_exp(B)
        assert np.allclose(R.data, R_expected.data, atol=1e-40)

    # ── Parametrized random ──

    @pytest.mark.parametrize("seed", range(5))
    def test_random_multivector_cl3(self, seed):
        """Random full MV in Cl(3,0) — exp matches Taylor."""
        alg = Algebra(3)
        np.random.seed(seed + 500)
        data = 0.3 * np.random.randn(alg.dim)
        X = Multivector(alg, data)
        R = exp(X)
        R_expected = self._taylor_exp(X)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)

    @pytest.mark.parametrize("seed", range(5))
    def test_random_multivector_cl13(self, seed):
        """Random full MV in Cl(1,3) — exp matches Taylor."""
        alg = Algebra(1, 3)
        np.random.seed(seed + 600)
        data = 0.2 * np.random.randn(alg.dim)
        X = Multivector(alg, data)
        R = exp(X)
        R_expected = self._taylor_exp(X)
        assert np.allclose(R.data, R_expected.data, atol=1e-10)


class TestSqrt:
    """Square root via Study number decomposition."""

    def test_sqrt_scalar(self, cl3):
        """sqrt of a scalar MV returns scalar."""
        s = cl3.scalar(9.0)
        assert np.isclose(sqrt(s).scalar_part, 3.0)

    def test_sqrt_number(self):
        """sqrt of a plain number."""
        assert sqrt(4.0) == 2.0

    def test_sqrt_int(self):
        """sqrt of a plain int."""
        assert sqrt(4) == 2

    def test_sqrt_rotor(self, cl3):
        """sqrt(R)^2 = R for a rotor."""
        e1, e2, _ = cl3.basis_vectors()
        R = exp(0.7 * (e1 ^ e2))
        sqR = sqrt(R)
        assert np.allclose(gp(sqR, sqR).data, R.data)

    def test_sqrt_lazy_rotor(self, cl3):
        """sqrt of a lazy rotor returns lazy with correct data."""
        e1, e2, _ = cl3.basis_vectors(lazy=True)
        R = exp(0.7 * (e1 ^ e2))
        sqR = sqrt(R)
        assert sqR._is_symbolic
        assert np.allclose(gp(sqR, sqR).data, R.data)

    def test_sqrt_pga_translator(self):
        """sqrt(T)^2 = T for a PGA translator (null bI² path)."""
        pga = Algebra((1, 1, 1, 0))
        e1, _, _, e0 = pga.basis_vectors()
        T = pga.scalar(1) + 0.5 * (e0 ^ e1)
        sqT = sqrt(T)
        assert np.allclose(gp(sqT, sqT).data, T.data)

    def test_sqrt_half_angle(self, cl3):
        """sqrt of a rotor halves the rotation angle."""
        e1, e2, _ = cl3.basis_vectors()
        theta = 1.2
        R = exp(-theta / 2 * (e1 ^ e2))
        sqR = sqrt(R)
        R_half = exp(-theta / 4 * (e1 ^ e2))
        assert np.allclose(sqR.data, R_half.data)

    def test_sqrt_non_study_raises(self, cl3):
        """sqrt of a non-Study-number raises ValueError."""
        e1, e2, e3 = cl3.basis_vectors()
        mv = cl3.scalar(1) + e1 + (e1 ^ e2) + (e1 ^ e2 ^ e3)
        with pytest.raises(ValueError, match="Study number"):
            sqrt(mv)

    def test_sqrt_negative_scalar_raises(self, cl3):
        """sqrt of a negative scalar raises ValueError."""
        with pytest.raises(ValueError, match="negative"):
            sqrt(cl3.scalar(-4.0))

    def test_sqrt_negative_number_raises(self):
        """sqrt of a negative plain number raises ValueError."""
        with pytest.raises(ValueError, match="negative"):
            sqrt(-4.0)

    def test_sqrt_bad_type_raises(self):
        """sqrt of a non-MV/non-number raises TypeError."""
        with pytest.raises(TypeError, match="sqrt expects"):
            sqrt("hello")

    def test_sqrt_identity(self, cl3):
        """sqrt(1) = 1."""
        one = cl3.scalar(1.0)
        assert np.allclose(sqrt(one).data, one.data)

    def test_sqrt_hyperbolic_rotor(self):
        """sqrt of a hyperbolic rotor (STA boost) squares back."""
        sta = Algebra((1, -1, -1, -1))
        g0, g1, _, _ = sta.basis_vectors()
        B = 0.3 * (g0 * g1)  # timelike bivector, B² > 0
        R = exp(B)
        sqR = sqrt(R)
        assert np.allclose(gp(sqR, sqR).data, R.data)


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
        assert result._is_symbolic
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
