"""Tests for the BladeConvention system (SPEC-010)."""

import pytest

from galaga import (
    Algebra,
    BladeConvention,
    b_cga,
    b_default,
    b_gamma,
    b_pga,
    b_sigma,
    b_sigma_xyz,
    b_sta,
)

# ---- 1. Factory defaults ----


class TestFactoryDefaults:
    def test_b_default_compact(self):
        """b_default: 1-based, compact."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        assert str(e1 ^ e2) == "e₁₂"
        assert str(e1 ^ e2 ^ e3) == "e₁₂₃"

    def test_b_default_latex(self):
        """b_default compact produces e_{12} in LaTeX."""
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        assert "e_{12}" in (e1 ^ e2).latex()

    def test_b_gamma(self):
        """b_gamma: 0-based, juxtapose."""
        alg = Algebra(1, 3, blades=b_gamma())
        g0, g1, _, _ = alg.basis_vectors()
        assert str(g0) == "γ₀"
        assert str(g1) == "γ₁"
        assert "γ₀γ₁" in str(g0 * g1)

    def test_b_sigma(self):
        """b_sigma: 1-based, juxtapose."""
        alg = Algebra(3, blades=b_sigma())
        s1, s2, _ = alg.basis_vectors()
        assert str(s1) == "σ₁"
        assert str(s2) == "σ₂"

    def test_b_sigma_xyz(self):
        """b_sigma_xyz: letter subscripts."""
        alg = Algebra(3, blades=b_sigma_xyz())
        sx, sy, sz = alg.basis_vectors()
        assert str(sx) == "σₓ"
        assert str(sy) == "σᵧ"

    def test_b_pga(self):
        """b_pga: 0-based, compact, PSS → I."""
        alg = Algebra(3, 0, 1, blades=b_pga())
        e0, e1, e2, e3 = alg.basis_vectors()
        assert str(e0) == "e₀"
        assert str(e0 ^ e1) == "e₀₁"
        assert str(alg.pseudoscalar()) == "I"

    def test_b_sta_basic(self):
        """b_sta: gamma vectors, PSS → i."""
        alg = Algebra(1, 3, blades=b_sta())
        g0, _, _, _ = alg.basis_vectors()
        assert str(g0) == "γ₀"
        assert str(alg.pseudoscalar()) == "i"

    def test_b_sta_sigmas(self):
        """b_sta(sigmas=True): adds σ and iσ bivector aliases."""
        alg = Algebra(1, 3, blades=b_sta(sigmas=True))
        g0, g1, g2, g3 = alg.basis_vectors()
        # σ₁ labels the canonical γ₀γ₁ blade
        assert str(g0 * g1) == "σ₁"
        # iσ₃ labels the canonical γ₁γ₂ blade
        assert str(g1 * g2) == "iσ₃"

    def test_b_sta_pseudovectors(self):
        """b_sta(pseudovectors=True): names grade-3 trivectors as iγₖ."""
        alg = Algebra(1, 3, blades=b_sta(pseudovectors=True))
        g0, g1, g2, g3 = alg.basis_vectors()
        trivec = g1 * g2 * g3
        assert "iγ" in str(trivec)

    def test_b_cga(self):
        """b_cga: eₒ, e∞ names, E₀ for null pair, PSS → I."""
        alg = Algebra(4, 1, blades=b_cga())
        es = alg.basis_vectors()
        assert str(es[3]) == "eₒ"
        assert str(es[4]) == "e∞"
        assert str(alg.pseudoscalar()) == "I"

    def test_b_cga_plus_minus(self):
        """b_cga(null_basis='plus_minus'): e₊, e₋."""
        alg = Algebra(4, 1, blades=b_cga(null_basis="plus_minus"))
        es = alg.basis_vectors()
        assert str(es[3]) == "e₊"
        assert str(es[4]) == "e₋"


# ---- 2. Style variations ----


class TestStyleVariations:
    def test_compact_unicode(self):
        alg = Algebra(3, blades=b_default(style="compact"))
        e1, e2, _ = alg.basis_vectors()
        assert str(e1 ^ e2) == "e₁₂"

    def test_compact_ascii(self):
        alg = Algebra(3, blades=b_default(style="compact"))
        e1, e2, _ = alg.basis_vectors()
        assert format(e1 ^ e2, "a") == "e12"

    def test_compact_latex(self):
        alg = Algebra(3, blades=b_default(style="compact"))
        e1, e2, _ = alg.basis_vectors()
        assert "e_{12}" in (e1 ^ e2).latex()

    def test_juxtapose_unicode(self):
        alg = Algebra(3, blades=b_default(style="juxtapose"))
        e1, e2, _ = alg.basis_vectors()
        assert str(e1 ^ e2) == "e₁e₂"

    def test_juxtapose_ascii(self):
        alg = Algebra(3, blades=b_default(style="juxtapose"))
        e1, e2, _ = alg.basis_vectors()
        assert format(e1 ^ e2, "a") == "e1e2"

    def test_juxtapose_latex(self):
        alg = Algebra(3, blades=b_default(style="juxtapose"))
        e1, e2, _ = alg.basis_vectors()
        assert "e_{1} e_{2}" in (e1 ^ e2).latex()

    def test_wedge_unicode(self):
        alg = Algebra(3, blades=b_default(style="wedge"))
        e1, e2, _ = alg.basis_vectors()
        assert "∧" in str(e1 ^ e2)

    def test_wedge_ascii(self):
        alg = Algebra(3, blades=b_default(style="wedge"))
        e1, e2, _ = alg.basis_vectors()
        assert "^" in format(e1 ^ e2, "a")

    def test_wedge_latex(self):
        alg = Algebra(3, blades=b_default(style="wedge"))
        e1, e2, _ = alg.basis_vectors()
        assert r"\wedge" in (e1 ^ e2).latex()


# ---- 3. Overrides ----


class TestOverrides:
    def test_pss_override(self):
        """pss key overrides pseudoscalar."""
        alg = Algebra(3, blades=b_default(overrides={"pss": "I"}))
        assert str(alg.pseudoscalar()) == "I"

    def test_bivector_override(self):
        """Metric-role key overrides a bivector."""
        alg = Algebra(3, blades=b_default(overrides={"+1+2": "B"}))
        e1, e2, _ = alg.basis_vectors()
        assert str(e1 ^ e2) == "B"

    def test_override_3tuple(self):
        """Override with (ascii, unicode, latex) tuple."""
        alg = Algebra(
            3,
            blades=b_default(
                overrides={
                    "+1+2": ("B12", "B₁₂", r"B_{12}"),
                }
            ),
        )
        e1, e2, _ = alg.basis_vectors()
        assert format(e1 ^ e2, "a") == "B12"
        assert str(e1 ^ e2) == "B₁₂"
        assert "B_{12}" in (e1 ^ e2).latex()

    def test_override_spaces_optional(self):
        """Spaces in metric-role key are optional."""
        alg1 = Algebra(3, blades=b_default(overrides={"+1+2": "X"}))
        alg2 = Algebra(3, blades=b_default(overrides={"+1 +2": "X"}))
        e1a, e2a, _ = alg1.basis_vectors()
        e1b, e2b, _ = alg2.basis_vectors()
        assert str(e1a ^ e2a) == str(e1b ^ e2b) == "X"

    def test_null_vector_override(self):
        """Override with null vector in PGA."""
        alg = Algebra(3, 0, 1, blades=b_pga(overrides={"_1+1": "L"}))
        e0, e1, _, _ = alg.basis_vectors()
        assert str(e0 ^ e1) == "L"

    def test_factory_overrides_merge(self):
        """User overrides merge with factory defaults (user wins)."""
        alg = Algebra(3, 0, 1, blades=b_pga(overrides={"_1+1": "L"}))
        # pss → I from factory should still be there
        assert str(alg.pseudoscalar()) == "I"
        e0, e1, _, _ = alg.basis_vectors()
        assert str(e0 ^ e1) == "L"

    def test_user_override_wins_on_conflict(self):
        """User override replaces factory default on same key."""
        alg = Algebra(3, 0, 1, blades=b_pga(overrides={"pss": "𝐈"}))
        assert str(alg.pseudoscalar()) == "𝐈"


# ---- 4. Error cases ----


class TestErrors:
    def test_override_nonexistent_vector(self):
        """Override referencing nonexistent vector raises."""
        with pytest.raises(ValueError):
            Algebra(2, blades=b_default(overrides={"+3+4": "X"}))

    def test_override_invalid_key(self):
        """Invalid metric-role string raises."""
        with pytest.raises(ValueError):
            Algebra(3, blades=b_default(overrides={"foo": "X"}))

    def test_incompatible_sta_sigmas(self):
        """b_sta(sigmas=True) on algebra with no negative vectors raises."""
        with pytest.raises(ValueError):
            Algebra(3, blades=b_sta(sigmas=True))

    def test_compact_mixed_prefix_fallback(self):
        """Compact with mixed prefixes falls back to juxtapose."""
        alg = Algebra(
            (1, 1),
            blades=BladeConvention(
                vector_names=[("x", "x", "x"), ("y", "y", "y")],
                style="compact",
            ),
        )
        e1, e2 = alg.basis_vectors()
        # No common prefix → juxtapose fallback
        assert str(e1 ^ e2) == "xy"

    def test_invalid_blades_type(self):
        """Non-BladeConvention blades= raises TypeError."""
        with pytest.raises(TypeError):
            Algebra(3, blades="bogus")

    def test_too_few_vector_names(self):
        """Too few vector_names raises ValueError."""
        with pytest.raises(ValueError, match="need at least"):
            Algebra(3, blades=BladeConvention(vector_names=[("a", "a", "a")]))


# ---- 5. Blade lookup ----


class TestBladeLookup:
    def test_metric_role_string(self):
        """blade() accepts metric-role string."""
        sta = Algebra(1, 3, blades=b_sta(sigmas=True))
        g0, g1, _, _ = sta.basis_vectors()
        assert sta.blade("+1-1") == g0 ^ g1

    def test_display_name_match(self):
        """blade() matches display names."""
        sta = Algebra(1, 3, blades=b_sta(sigmas=True))
        g0, g1, _, _ = sta.basis_vectors()
        assert sta.blade("σ₁") == g0 ^ g1

    def test_pss_shorthand(self):
        """blade('pss') returns pseudoscalar."""
        alg = Algebra(3)
        assert alg.blade("pss") == alg.pseudoscalar()

    def test_0based_digit_parsing(self):
        """blade('e01') works with 0-based indexing."""
        pga = Algebra(3, 0, 1, blades=b_pga())
        e0, e1, _, _ = pga.basis_vectors()
        assert pga.blade("e01") == e0 ^ e1

    def test_1based_digit_parsing(self):
        """blade('e12') works with 1-based indexing."""
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        assert alg.blade("e12") == e1 ^ e2

    def test_invalid_name_raises(self):
        """blade() with unknown name raises ValueError."""
        alg = Algebra(3)
        with pytest.raises(ValueError):
            alg.blade("e99")

    def test_nonsense_raises(self):
        """blade() with nonsense raises ValueError."""
        alg = Algebra(3)
        with pytest.raises(ValueError):
            alg.blade("nonsense")


# ---- 6. get_basis_blade ----


class TestGetBasisBlade:
    def test_metric_role_string(self):
        """get_basis_blade accepts metric-role string."""
        alg = Algebra(1, 3, blades=b_sta())
        g0, g1, _, _ = alg.basis_vectors()
        assert alg.get_basis_blade("+1-1") is alg.get_basis_blade(g0 ^ g1)

    def test_bitmask_int(self):
        """get_basis_blade accepts bitmask int."""
        alg = Algebra(1, 3, blades=b_sta())
        g0, g1, _, _ = alg.basis_vectors()
        assert alg.get_basis_blade(0b0011) is alg.get_basis_blade(g0 ^ g1)

    def test_pss_string(self):
        """get_basis_blade('pss') returns pseudoscalar blade."""
        alg = Algebra(3)
        assert alg.get_basis_blade("pss") is alg.get_basis_blade(alg.pseudoscalar())


# ---- 7. Post-hoc rename ----


class TestRename:
    def test_rename_string(self):
        """rename(str) sets all three formats."""
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        alg.get_basis_blade("+1+2").rename("B")
        assert str(e1 ^ e2) == "B"
        assert format(e1 ^ e2, "a") == "B"

    def test_rename_3tuple(self):
        """rename((ascii, unicode, latex)) sets each format."""
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        alg.get_basis_blade("+1+2").rename(("B12", "B₁₂", r"B_{12}"))
        assert str(e1 ^ e2) == "B₁₂"
        assert format(e1 ^ e2, "a") == "B12"

    def test_rename_keyword(self):
        """rename(unicode=...) sets one format."""
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        alg.get_basis_blade("+1+2").rename(unicode="X")
        assert str(e1 ^ e2) == "X"

    def test_rename_is_live(self):
        """Rename affects existing multivectors."""
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        mv = e1 ^ e2
        alg.get_basis_blade("+1+2").rename("Z")
        assert str(mv) == "Z"


# ---- 8. repr_unicode ----


class TestReprUnicode:
    def test_repr_unicode_true(self):
        """repr_unicode=True uses unicode subscripts in repr."""
        alg = Algebra(3, repr_unicode=True)
        e1, e2, _ = alg.basis_vectors()
        assert "₁₂" in repr(e1 ^ e2)

    def test_repr_unicode_false(self):
        """repr_unicode=False uses ascii in repr."""
        alg = Algebra(3, repr_unicode=False)
        e1, e2, _ = alg.basis_vectors()
        r = repr(e1 ^ e2)
        assert "12" in r
        assert "₁₂" not in r

    def test_str_always_unicode(self):
        """str() always uses unicode regardless of repr_unicode."""
        alg = Algebra(3, repr_unicode=False)
        e1, e2, _ = alg.basis_vectors()
        assert "₁₂" in str(e1 ^ e2)


# ---- 9. Factory keyword overrides ----


class TestFactoryKeywords:
    def test_prefix(self):
        """b_default(prefix='v') uses v prefix."""
        alg = Algebra(3, blades=b_default(prefix="v"))
        assert str(alg.basis_vectors()[0]) == "v₁"

    def test_start_0(self):
        """b_default(start=0) uses 0-based indexing."""
        alg = Algebra(3, blades=b_default(start=0))
        assert str(alg.basis_vectors()[0]) == "e₀"

    def test_gamma_start_1(self):
        """b_gamma(start=1) uses 1-based gamma."""
        alg = Algebra(4, blades=b_gamma(start=1))
        assert str(alg.basis_vectors()[0]) == "γ₁"

    def test_pga_custom_pseudoscalar(self):
        """b_pga(pseudoscalar='𝐈') uses custom PSS name."""
        alg = Algebra(3, 0, 1, blades=b_pga(pseudoscalar="𝐈"))
        assert str(alg.pseudoscalar()) == "𝐈"

    def test_style_override_on_factory(self):
        """Style can be overridden on any factory."""
        alg = Algebra(3, blades=b_gamma(style="compact"))
        g1, g2, _ = alg.basis_vectors()
        assert str(g1 ^ g2) == "γ₀₁"


# ---- 10. Cross-library compatibility ----


class TestCrossLibrary:
    def test_clifford_style(self):
        """clifford: e₁₂ compact."""
        alg = Algebra(3, blades=b_default(style="compact"))
        e1, e2, _ = alg.basis_vectors()
        assert str(e1 ^ e2) == "e₁₂"

    def test_ganja_style(self):
        """ganja.js / kingdon: e₀₁ 0-based compact."""
        alg = Algebra(3, blades=b_default(start=0, style="compact"))
        e0, e1, _ = alg.basis_vectors()
        assert str(e0 ^ e1) == "e₀₁"

    def test_galgebra_style(self):
        """galgebra: e₁∧e₂ wedge."""
        alg = Algebra(3, blades=b_default(style="wedge"))
        e1, e2, _ = alg.basis_vectors()
        assert "∧" in str(e1 ^ e2)

    def test_julia_style(self):
        """GeometricAlgebra.jl / Grassmann.jl: v₁₂ compact."""
        alg = Algebra(3, blades=b_default(prefix="v", style="compact"))
        v1, v2, _ = alg.basis_vectors()
        assert str(v1 ^ v2) == "v₁₂"


# ---- Coverage gap tests ----


class TestCoverageGaps:
    def test_override_2tuple(self):
        """Override with (ascii, unicode) 2-tuple."""
        alg = Algebra(
            3,
            blades=b_default(
                overrides={
                    "+1+2": ("B12", "B₁₂"),
                }
            ),
        )
        e1, e2, _ = alg.basis_vectors()
        assert format(e1 ^ e2, "a") == "B12"
        assert str(e1 ^ e2) == "B₁₂"
        # latex derived from unicode
        assert "B₁₂" in (e1 ^ e2).latex()

    def test_override_invalid_value_type(self):
        """Override with invalid value type raises."""
        with pytest.raises(ValueError, match="str, 2-tuple, or 3-tuple"):
            Algebra(3, blades=b_default(overrides={"+1+2": 42}))

    def test_override_negative_out_of_range(self):
        """Override referencing too many negative vectors raises."""
        with pytest.raises(ValueError, match="Negative vector index"):
            Algebra(3, blades=b_default(overrides={"-1-2": "X"}))

    def test_b_sta_with_user_overrides(self):
        """b_sta merges user overrides with factory defaults."""
        alg = Algebra(1, 3, blades=b_sta(overrides={"+1-1": "MyBlade"}))
        g0, g1, _, _ = alg.basis_vectors()
        assert str(g0 * g1) == "MyBlade"
        # pss → i from factory still present
        assert str(alg.pseudoscalar()) == "i"

    def test_b_cga_with_user_overrides(self):
        """b_cga merges user overrides."""
        alg = Algebra(4, 1, blades=b_cga(overrides={"+1+2": "Euc12"}))
        e1, e2, _, _, _ = alg.basis_vectors()
        assert str(e1 ^ e2) == "Euc12"
        # pss → I still present
        assert str(alg.pseudoscalar()) == "I"

    def test_b_cga_invalid_null_basis(self):
        """b_cga with invalid null_basis raises."""
        with pytest.raises(ValueError, match="Unknown null_basis"):
            b_cga(null_basis="bogus")

    def test_rename_2tuple(self):
        """BasisBlade.rename with 2-tuple."""
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        alg.get_basis_blade("+1+2").rename(("B12", "B₁₂"))
        assert format(e1 ^ e2, "a") == "B12"
        assert str(e1 ^ e2) == "B₁₂"

    def test_rename_invalid_value(self):
        """BasisBlade.rename with invalid value raises."""
        alg = Algebra(3)
        with pytest.raises(ValueError, match="str, 2-tuple, or 3-tuple"):
            alg.get_basis_blade("+1+2").rename(42)

    def test_basis_blade_property_setters(self):
        """BasisBlade property setters work."""
        from galaga.basis_blade import BasisBlade

        bb = BasisBlade(0b011, "e12", "e₁₂", "e_{12}")
        bb.ascii_name = "X"
        assert bb.ascii_name == "X"
        bb.unicode_name = "Y"
        assert bb.unicode_name == "Y"
        bb.latex_name = "Z"
        assert bb.latex_name == "Z"

    def test_basis_blade_repr(self):
        """BasisBlade __repr__."""
        from galaga.basis_blade import BasisBlade

        bb = BasisBlade(0b011, "e12", "e₁₂", "e_{12}")
        assert "BasisBlade" in repr(bb)
        assert "e12" in repr(bb)

    def test_null_vector_out_of_range(self):
        """Override referencing nonexistent null vector raises."""
        with pytest.raises(ValueError, match="Null vector index"):
            Algebra(3, blades=b_default(overrides={"_1": "X"}))
