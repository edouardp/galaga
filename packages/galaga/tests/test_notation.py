"""Tests for the Notation class — write first, implement to pass."""

import pytest
from galaga.notation import Notation, NotationRule


@pytest.fixture
def n():
    return Notation()


# ============================================================
# Default rules exist for all node types
# ============================================================

class TestDefaultsExist:
    """Every node type has rules for all three formats."""

    NODE_TYPES = [
        "Reverse", "Involute", "Conjugate", "Dual", "Undual",
        "Inverse", "Squared", "Neg", "ScalarMul", "ScalarDiv",
        "Gp", "Op", "Lc", "Rc", "Hi", "Dli", "Sp", "Div",
        "Regressive",
        "Add", "Sub",
        "Grade", "Norm", "Unit", "Exp", "Even", "Odd",
        "Commutator", "Anticommutator", "LieBracket", "JordanProduct",
    ]

    @pytest.mark.parametrize("name", NODE_TYPES)
    def test_unicode_rule_exists(self, n, name):
        assert n.get(name, "unicode") is not None

    @pytest.mark.parametrize("name", NODE_TYPES)
    def test_latex_rule_exists(self, n, name):
        assert n.get(name, "latex") is not None

    @pytest.mark.parametrize("name", NODE_TYPES)
    def test_ascii_rule_exists(self, n, name):
        assert n.get(name, "ascii") is not None


# ============================================================
# Accent rules (reverse, involute, conjugate)
# ============================================================

class TestAccentDefaults:
    def test_reverse_unicode_atom(self, n):
        r = n.get("Reverse", "unicode")
        assert r.kind == "accent"
        assert r.combining == "\u0303"

    def test_reverse_unicode_fallback(self, n):
        r = n.get("Reverse", "unicode")
        assert r.fallback_prefix == "~"

    def test_reverse_latex_atom(self, n):
        r = n.get("Reverse", "latex")
        assert r.kind == "accent"
        assert r.latex_cmd == r"\tilde"
        assert r.latex_wide_cmd == r"\widetilde"

    def test_involute_unicode(self, n):
        r = n.get("Involute", "unicode")
        assert r.kind == "accent"
        assert r.combining == "\u0302"

    def test_conjugate_unicode(self, n):
        r = n.get("Conjugate", "unicode")
        assert r.kind == "accent"
        assert r.combining == "\u0304"

    def test_conjugate_latex(self, n):
        r = n.get("Conjugate", "latex")
        assert r.latex_cmd == r"\bar"
        assert r.latex_wide_cmd == r"\overline"


# ============================================================
# Postfix rules (dual, inverse, squared, undual)
# ============================================================

class TestPostfixDefaults:
    def test_dual_unicode(self, n):
        r = n.get("Dual", "unicode")
        assert r.kind == "postfix"
        assert r.symbol == "⋆"

    def test_inverse_unicode(self, n):
        r = n.get("Inverse", "unicode")
        assert r.kind == "postfix"
        assert r.symbol == "⁻¹"

    def test_squared_unicode(self, n):
        r = n.get("Squared", "unicode")
        assert r.kind == "postfix"
        assert r.symbol == "²"

    def test_dual_latex(self, n):
        r = n.get("Dual", "latex")
        assert r.kind == "postfix"
        assert r.symbol == "^*"

    def test_inverse_latex(self, n):
        r = n.get("Inverse", "latex")
        assert r.symbol == "^{-1}"

    def test_squared_latex(self, n):
        r = n.get("Squared", "latex")
        assert r.symbol == "^2"


# ============================================================
# Prefix rules (neg)
# ============================================================

class TestPrefixDefaults:
    def test_neg_unicode(self, n):
        r = n.get("Neg", "unicode")
        assert r.kind == "prefix"
        assert r.symbol == "-"

    def test_neg_latex(self, n):
        r = n.get("Neg", "latex")
        assert r.kind == "prefix"
        assert r.symbol == "-"


# ============================================================
# Infix rules (binary ops)
# ============================================================

class TestInfixDefaults:
    def test_op_unicode(self, n):
        r = n.get("Op", "unicode")
        assert r.kind == "infix"
        assert r.separator == "∧"

    def test_op_latex(self, n):
        r = n.get("Op", "latex")
        assert r.separator == r" \wedge "

    def test_add_unicode(self, n):
        r = n.get("Add", "unicode")
        assert r.separator == " + "

    def test_sub_unicode(self, n):
        r = n.get("Sub", "unicode")
        assert r.separator == " - "

    def test_lc_unicode(self, n):
        r = n.get("Lc", "unicode")
        assert r.separator == "⌋"

    def test_hi_unicode(self, n):
        r = n.get("Hi", "unicode")
        assert r.separator == "·"

    def test_sp_unicode(self, n):
        r = n.get("Sp", "unicode")
        assert r.separator == "∗"

    def test_div_unicode(self, n):
        r = n.get("Div", "unicode")
        assert r.separator == "/"


# ============================================================
# Juxtaposition (Gp)
# ============================================================

class TestJuxtaposition:
    def test_gp_unicode(self, n):
        r = n.get("Gp", "unicode")
        assert r.kind == "juxtaposition"

    def test_gp_latex(self, n):
        r = n.get("Gp", "latex")
        assert r.kind == "juxtaposition"
        assert r.separator == " "


# ============================================================
# Wrap rules (grade, norm, exp, etc.)
# ============================================================

class TestWrapDefaults:
    def test_grade_unicode(self, n):
        r = n.get("Grade", "unicode")
        assert r.kind == "wrap"
        assert r.open == "⟨"
        assert r.close.startswith("⟩")

    def test_norm_unicode(self, n):
        r = n.get("Norm", "unicode")
        assert r.kind == "wrap"
        assert r.open == "‖"
        assert r.close == "‖"

    def test_exp_unicode(self, n):
        r = n.get("Exp", "unicode")
        assert r.kind == "wrap"
        assert r.open == "exp("
        assert r.close == ")"

    def test_commutator_unicode(self, n):
        r = n.get("Commutator", "unicode")
        assert r.kind == "wrap"
        assert r.open == "["
        assert r.close == "]"

    def test_anticommutator_unicode(self, n):
        r = n.get("Anticommutator", "unicode")
        assert r.open == "{"
        assert r.close == "}"


# ============================================================
# ScalarMul / ScalarDiv
# ============================================================

class TestScalarOps:
    def test_scalar_mul_unicode(self, n):
        r = n.get("ScalarMul", "unicode")
        assert r.kind == "prefix"

    def test_scalar_div_unicode(self, n):
        r = n.get("ScalarDiv", "unicode")
        assert r.kind == "postfix"
        assert "/" in r.symbol


# ============================================================
# Override rules
# ============================================================

class TestOverride:
    def test_override_reverse_unicode(self, n):
        n.set("Reverse", "unicode", NotationRule(
            kind="postfix", symbol="†"
        ))
        r = n.get("Reverse", "unicode")
        assert r.kind == "postfix"
        assert r.symbol == "†"

    def test_override_does_not_affect_other_formats(self, n):
        original_latex = n.get("Reverse", "latex")
        n.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
        assert n.get("Reverse", "latex") == original_latex

    def test_override_dual_to_prefix(self, n):
        n.set("Dual", "unicode", NotationRule(kind="prefix", symbol="*"))
        r = n.get("Dual", "unicode")
        assert r.kind == "prefix"
        assert r.symbol == "*"

    def test_override_gp_to_infix(self, n):
        """Some notations use explicit dot or space for gp."""
        n.set("Gp", "unicode", NotationRule(kind="infix", separator=" "))
        r = n.get("Gp", "unicode")
        assert r.kind == "infix"


# ============================================================
# Copy / isolation
# ============================================================

class TestCopy:
    def test_copy_is_independent(self, n):
        n2 = n.copy()
        n2.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
        assert n.get("Reverse", "unicode").kind == "accent"  # original unchanged


class TestPresets:
    def test_default_preset(self):
        n = Notation.default()
        assert n.get("Reverse", "unicode").kind == "accent"

    def test_hestenes_reverse_is_dagger(self):
        n = Notation.hestenes()
        r = n.get("Reverse", "unicode")
        assert r.kind == "postfix"
        assert r.symbol == "†"

    def test_hestenes_latex_dagger(self):
        n = Notation.hestenes()
        r = n.get("Reverse", "latex")
        assert "dagger" in r.symbol

    def test_doran_lasenby_reverse_is_tilde(self):
        n = Notation.doran_lasenby()
        r = n.get("Reverse", "unicode")
        assert r.kind == "accent"
        assert r.combining == "\u0303"

    def test_preset_with_algebra(self):
        from galaga import Algebra, reverse
        alg = Algebra((1, 1, 1), notation=Notation.hestenes())
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        assert str(reverse(v)) == "v†"


class TestFunctionStyle:
    def test_wedge_as_function(self):
        from galaga import Algebra, op
        from galaga.notation import NotationRule
        alg = Algebra((1, 1, 1))
        alg.notation.set("Op", "unicode", NotationRule(kind="function", symbol="wedge"))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        assert str(e1 ^ e2) == "wedge(e₁, e₂)"

    def test_reverse_as_function(self):
        from galaga import Algebra, reverse
        from galaga.notation import NotationRule
        alg = Algebra((1, 1, 1))
        alg.notation.set("Reverse", "unicode", NotationRule(kind="function", symbol="rev"))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        assert str(reverse(v)) == "rev(v)"

    def test_function_style_latex(self):
        from galaga import Algebra
        from galaga.notation import NotationRule
        alg = Algebra((1, 1, 1))
        alg.notation.set("Op", "latex", NotationRule(kind="function", symbol="wedge"))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        result = (e1 ^ e2)
        assert r"\operatorname{wedge}" in result.latex()
