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
        "Reverse",
        "Involute",
        "Conjugate",
        "Dual",
        "Undual",
        "Inverse",
        "Squared",
        "Neg",
        "ScalarMul",
        "ScalarDiv",
        "Gp",
        "Op",
        "Lc",
        "Rc",
        "Hi",
        "Dli",
        "Sp",
        "Div",
        "Regressive",
        "Add",
        "Sub",
        "Grade",
        "Norm",
        "Unit",
        "Exp",
        "Even",
        "Odd",
        "Commutator",
        "Anticommutator",
        "LieBracket",
        "JordanProduct",
    ]

    @pytest.mark.parametrize("name", NODE_TYPES)
    def test_unicode_rule_exists(self, n, name):
        """Every node type has a unicode rule."""
        assert n.get(name, "unicode") is not None

    @pytest.mark.parametrize("name", NODE_TYPES)
    def test_latex_rule_exists(self, n, name):
        """Every node type has a latex rule."""
        assert n.get(name, "latex") is not None

    @pytest.mark.parametrize("name", NODE_TYPES)
    def test_ascii_rule_exists(self, n, name):
        """Every node type has an ascii rule."""
        assert n.get(name, "ascii") is not None


# ============================================================
# Accent rules (reverse, involute, conjugate)
# ============================================================


class TestAccentDefaults:
    def test_reverse_unicode_atom(self, n):
        """Reverse uses combining tilde accent."""
        r = n.get("Reverse", "unicode")
        assert r.kind == "accent"
        assert r.combining == "\u0303"

    def test_reverse_unicode_fallback(self, n):
        """Reverse falls back to ~ prefix for compounds."""
        r = n.get("Reverse", "unicode")
        assert r.fallback_prefix == "~"

    def test_reverse_latex_atom(self, n):
        """Reverse uses \tilde / \\widetilde in LaTeX."""
        r = n.get("Reverse", "latex")
        assert r.kind == "accent"
        assert r.latex_cmd == r"\tilde"
        assert r.latex_wide_cmd == r"\widetilde"

    def test_involute_unicode(self, n):
        """Involute uses combining circumflex."""
        r = n.get("Involute", "unicode")
        assert r.kind == "accent"
        assert r.combining == "\u0302"

    def test_conjugate_unicode(self, n):
        """Conjugate uses combining overline."""
        r = n.get("Conjugate", "unicode")
        assert r.kind == "accent"
        assert r.combining == "\u0304"

    def test_conjugate_latex(self, n):
        """Conjugate uses \bar / \\overline in LaTeX."""
        r = n.get("Conjugate", "latex")
        assert r.latex_cmd == r"\bar"
        assert r.latex_wide_cmd == r"\overline"


# ============================================================
# Postfix rules (dual, inverse, squared, undual)
# ============================================================


class TestPostfixDefaults:
    def test_dual_unicode(self, n):
        """Dual renders as postfix ⋆."""
        r = n.get("Dual", "unicode")
        assert r.kind == "postfix"
        assert r.symbol == "⋆"

    def test_inverse_unicode(self, n):
        """Inverse renders as postfix ⁻¹."""
        r = n.get("Inverse", "unicode")
        assert r.kind == "postfix"
        assert r.symbol == "⁻¹"

    def test_squared_unicode(self, n):
        """Squared renders as postfix ²."""
        r = n.get("Squared", "unicode")
        assert r.kind == "postfix"
        assert r.symbol == "²"

    def test_dual_latex(self, n):
        """Dual renders as ^* in LaTeX."""
        r = n.get("Dual", "latex")
        assert r.kind == "postfix"
        assert r.symbol == "^*"

    def test_inverse_latex(self, n):
        """Inverse renders as ^{-1} in LaTeX."""
        r = n.get("Inverse", "latex")
        assert r.symbol == "^{-1}"

    def test_squared_latex(self, n):
        """Squared renders as ^2 in LaTeX."""
        r = n.get("Squared", "latex")
        assert r.symbol == "^2"


# ============================================================
# Prefix rules (neg)
# ============================================================


class TestPrefixDefaults:
    def test_neg_unicode(self, n):
        """Negation is prefix -."""
        r = n.get("Neg", "unicode")
        assert r.kind == "prefix"
        assert r.symbol == "-"

    def test_neg_latex(self, n):
        """Negation is prefix - in LaTeX."""
        r = n.get("Neg", "latex")
        assert r.kind == "prefix"
        assert r.symbol == "-"


# ============================================================
# Infix rules (binary ops)
# ============================================================


class TestInfixDefaults:
    def test_op_unicode(self, n):
        """Wedge uses ∧ separator."""
        r = n.get("Op", "unicode")
        assert r.kind == "infix"
        assert r.separator == "∧"

    def test_op_latex(self, n):
        r"""Wedge uses \wedge in LaTeX."""
        r = n.get("Op", "latex")
        assert r.separator == r" \wedge "

    def test_add_unicode(self, n):
        """Add uses + separator."""
        r = n.get("Add", "unicode")
        assert r.separator == " + "

    def test_sub_unicode(self, n):
        """Sub uses - separator."""
        r = n.get("Sub", "unicode")
        assert r.separator == " - "

    def test_lc_unicode(self, n):
        """Left contraction uses ⌋."""
        r = n.get("Lc", "unicode")
        assert r.separator == "⌋"

    def test_hi_unicode(self, n):
        """Hestenes inner uses ·."""
        r = n.get("Hi", "unicode")
        assert r.separator == "·"

    def test_sp_unicode(self, n):
        """Scalar product uses ∗."""
        r = n.get("Sp", "unicode")
        assert r.separator == "∗"

    def test_div_unicode(self, n):
        """Division uses /."""
        r = n.get("Div", "unicode")
        assert r.separator == "/"


# ============================================================
# Juxtaposition (Gp)
# ============================================================


class TestJuxtaposition:
    def test_gp_unicode(self, n):
        """Geometric product uses juxtaposition."""
        r = n.get("Gp", "unicode")
        assert r.kind == "juxtaposition"

    def test_gp_latex(self, n):
        """Geometric product uses space separator in LaTeX."""
        r = n.get("Gp", "latex")
        assert r.kind == "juxtaposition"
        assert r.separator == " "


# ============================================================
# Wrap rules (grade, norm, exp, etc.)
# ============================================================


class TestWrapDefaults:
    def test_grade_unicode(self, n):
        """Grade projection uses ⟨⟩ delimiters."""
        r = n.get("Grade", "unicode")
        assert r.kind == "wrap"
        assert r.open == "⟨"
        assert r.close.startswith("⟩")

    def test_norm_unicode(self, n):
        """Norm uses ‖‖ delimiters."""
        r = n.get("Norm", "unicode")
        assert r.kind == "wrap"
        assert r.open == "‖"
        assert r.close == "‖"

    def test_exp_unicode(self, n):
        """Exp uses exp() wrap."""
        r = n.get("Exp", "unicode")
        assert r.kind == "wrap"
        assert r.open == "exp("
        assert r.close == ")"

    def test_commutator_unicode(self, n):
        """Commutator uses [] delimiters."""
        r = n.get("Commutator", "unicode")
        assert r.kind == "wrap"
        assert r.open == "["
        assert r.close == "]"

    def test_anticommutator_unicode(self, n):
        """Anticommutator uses {} delimiters."""
        r = n.get("Anticommutator", "unicode")
        assert r.open == "{"
        assert r.close == "}"


# ============================================================
# ScalarMul / ScalarDiv
# ============================================================


class TestScalarOps:
    def test_scalar_mul_unicode(self, n):
        """ScalarMul is a prefix rule."""
        r = n.get("ScalarMul", "unicode")
        assert r.kind == "prefix"

    def test_scalar_div_unicode(self, n):
        """ScalarDiv is a postfix rule with /."""
        r = n.get("ScalarDiv", "unicode")
        assert r.kind == "postfix"
        assert "/" in r.symbol


# ============================================================
# Override rules
# ============================================================


class TestOverride:
    def test_override_reverse_unicode(self, n):
        """set() overrides a single format."""
        n.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
        r = n.get("Reverse", "unicode")
        assert r.kind == "postfix"
        assert r.symbol == "†"

    def test_override_does_not_affect_other_formats(self, n):
        """Overriding unicode leaves latex unchanged."""
        original_latex = n.get("Reverse", "latex")
        n.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
        assert n.get("Reverse", "latex") == original_latex

    def test_override_dual_to_prefix(self, n):
        """Dual can be overridden to prefix style."""
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
        """copy() produces an independent notation."""
        n2 = n.copy()
        n2.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
        assert n.get("Reverse", "unicode").kind == "accent"  # original unchanged


class TestPresets:
    def test_default_preset(self):
        """default() preset uses accent for reverse."""
        n = Notation.default()
        assert n.get("Reverse", "unicode").kind == "accent"

    def test_hestenes_reverse_is_dagger(self):
        """Hestenes preset uses † for reverse."""
        n = Notation.hestenes()
        r = n.get("Reverse", "unicode")
        assert r.kind == "postfix"
        assert r.symbol == "†"

    def test_hestenes_latex_dagger(self):
        r"""Hestenes preset uses \dagger in LaTeX."""
        n = Notation.hestenes()
        r = n.get("Reverse", "latex")
        assert "dagger" in r.symbol

    def test_doran_lasenby_reverse_is_tilde(self):
        """Doran-Lasenby preset uses tilde for reverse."""
        n = Notation.doran_lasenby()
        r = n.get("Reverse", "unicode")
        assert r.kind == "accent"
        assert r.combining == "\u0303"

    def test_preset_with_algebra(self):
        """Notation preset integrates with Algebra rendering."""
        from galaga import Algebra, reverse

        alg = Algebra((1, 1, 1), notation=Notation.hestenes())
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        assert str(reverse(v)) == "v†"


class TestFunctionStyle:
    def test_wedge_as_function(self):
        """Op can render as function style: wedge(a, b)."""
        from galaga import Algebra
        from galaga.notation import NotationRule

        alg = Algebra((1, 1, 1))
        alg.notation.set("Op", "unicode", NotationRule(kind="function", symbol="wedge"))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        assert str(e1 ^ e2) == "wedge(e₁, e₂)"

    def test_reverse_as_function(self):
        """Reverse can render as function style: rev(v)."""
        from galaga import Algebra, reverse
        from galaga.notation import NotationRule

        alg = Algebra((1, 1, 1))
        alg.notation.set("Reverse", "unicode", NotationRule(kind="function", symbol="rev"))
        e1, _, _ = alg.basis_vectors(lazy=True)
        v = e1.name("v")
        assert str(reverse(v)) == "rev(v)"

    def test_function_style_latex(self):
        r"""Function style uses \operatorname in LaTeX."""
        from galaga import Algebra
        from galaga.notation import NotationRule

        alg = Algebra((1, 1, 1))
        alg.notation.set("Op", "latex", NotationRule(kind="function", symbol="wedge"))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        result = e1 ^ e2
        assert r"\operatorname{wedge}" in result.latex()


class TestFunctionalPreset:
    """Notation.functional() renders everything as function calls."""

    def test_gp_unicode(self):
        """gp(a, b) in unicode."""
        from galaga import Algebra
        from galaga.notation import Notation

        alg = Algebra((1, 1, 1), notation=Notation.functional())
        e1, e2, _ = alg.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert str(a * b) == "gp(a, b)"

    def test_op_unicode(self):
        """op(a, b) in unicode."""
        from galaga import Algebra
        from galaga.notation import Notation

        alg = Algebra((1, 1, 1), notation=Notation.functional())
        e1, e2, _ = alg.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert str(a ^ b) == "op(a, b)"

    def test_reverse_unicode(self):
        """reverse(a) in unicode."""
        from galaga import Algebra, reverse
        from galaga.notation import Notation

        alg = Algebra((1, 1, 1), notation=Notation.functional())
        e1, _, _ = alg.basis_vectors(lazy=True)
        a = e1.name("a")
        assert str(reverse(a)) == "reverse(a)"

    def test_gp_latex(self):
        """\\operatorname{gp}(a, b) in LaTeX."""
        from galaga import Algebra
        from galaga.notation import Notation

        alg = Algebra((1, 1, 1), notation=Notation.functional())
        e1, e2, _ = alg.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert r"\operatorname{gp}" in (a * b).latex()

    def test_default_not_affected(self):
        """Default notation still uses juxtaposition."""
        from galaga import Algebra

        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert str(a * b) == "ab"
