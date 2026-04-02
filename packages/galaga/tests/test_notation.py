"""Tests for the Notation class — write first, implement to pass."""

import pytest

from galaga import (
    Algebra,
    anticommutator,
    commutator,
    complement,
    conjugate,
    dual,
    even_grades,
    exp,
    grade,
    hestenes_inner,
    inverse,
    involute,
    jordan_product,
    left_contraction,
    lie_bracket,
    log,
    norm,
    odd_grades,
    reverse,
    right_contraction,
    scalar_product,
    scalar_sqrt,
    squared,
    undual,
    unit,
)
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

    def test_set_returns_self(self, n):
        """set() returns self for chaining."""
        result = n.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
        assert result is n

    def test_chaining(self, n):
        """Multiple set() calls can be chained."""
        n.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†")).set(
            "Dual", "unicode", NotationRule(kind="prefix", symbol="*")
        )
        assert n.get("Reverse", "unicode").symbol == "†"
        assert n.get("Dual", "unicode").symbol == "*"

    def test_with_scientific_returns_self(self, n):
        """with_scientific() returns self for chaining."""
        result = n.with_scientific("cdot")
        assert result is n
        assert n.scientific == "cdot"

    def test_invalid_format_raises(self, n):
        """set() with unknown format raises ValueError."""
        with pytest.raises(ValueError, match="format"):
            n.set("Reverse", "klingon", NotationRule(kind="postfix", symbol="†"))

    def test_invalid_kind_raises(self, n):
        """set() with unknown kind raises ValueError."""
        with pytest.raises(ValueError, match="kind"):
            n.set("Reverse", "unicode", NotationRule(kind="banana", symbol="†"))

    def test_invalid_scientific_raises(self, n):
        """Invalid scientific style raises ValueError."""
        with pytest.raises(ValueError):
            n.scientific = "banana"

    def test_unknown_node_name_accepted(self, n):
        """Unknown node names are accepted — extensibility."""
        n.set("CustomOp", "unicode", NotationRule(kind="postfix", symbol="!"))
        assert n.get("CustomOp", "unicode").symbol == "!"


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

    @pytest.fixture
    def fn_alg(self):
        from galaga.notation import Notation

        return Algebra((1, 1, 1), notation=Notation.functional())

    @pytest.fixture
    def ab(self, fn_alg):
        e1, e2, _ = fn_alg.basis_vectors(lazy=True)
        return e1.name("a"), e2.name("b")

    @pytest.fixture
    def s(self, fn_alg):
        return fn_alg.scalar(2.0).name("s")

    # --- Binary operations ---

    def test_gp_unicode(self, ab):
        """geometric_product(a, b) in unicode."""
        a, b = ab
        assert str(a * b) == "geometric_product(a, b)"

    def test_gp_latex(self, ab):
        """\\operatorname{geometric_product}(a, b) in LaTeX."""
        a, b = ab
        assert r"\operatorname{geometric\_product}" in (a * b).latex()

    def test_op_unicode(self, ab):
        """outer_product(a, b) in unicode."""
        a, b = ab
        assert str(a ^ b) == "outer_product(a, b)"

    def test_op_latex(self, ab):
        """\\operatorname{outer_product}(a, b) in LaTeX."""
        a, b = ab
        assert r"\operatorname{outer\_product}" in (a ^ b).latex()

    def test_dli_unicode(self, ab):
        """doran_lasenby_inner(a, b) in unicode."""
        a, b = ab
        assert str(a | b) == "doran_lasenby_inner(a, b)"

    def test_lc_unicode(self, ab):
        """left_contraction(a, b) in unicode."""
        a, b = ab
        assert str(left_contraction(a, b)) == "left_contraction(a, b)"

    def test_rc_unicode(self, ab):
        """right_contraction(a, b) in unicode."""
        a, b = ab
        assert str(right_contraction(a, b)) == "right_contraction(a, b)"

    def test_hi_unicode(self, ab):
        """hestenes_inner(a, b) in unicode."""
        a, b = ab
        assert str(hestenes_inner(a, b)) == "hestenes_inner(a, b)"

    def test_sp_unicode(self, ab):
        """scalar_product(a, b) in unicode."""
        a, b = ab
        assert str(scalar_product(a, b)) == "scalar_product(a, b)"

    def test_commutator_unicode(self, ab):
        """commutator(a, b) in unicode."""
        a, b = ab
        assert str(commutator(a, b)) == "commutator(a, b)"

    def test_anticommutator_unicode(self, ab):
        """anticommutator(a, b) in unicode."""
        a, b = ab
        assert str(anticommutator(a, b)) == "anticommutator(a, b)"

    def test_lie_bracket_unicode(self, ab):
        """lie_bracket(a, b) in unicode."""
        a, b = ab
        assert str(lie_bracket(a, b)) == "lie_bracket(a, b)"

    def test_jordan_product_unicode(self, ab):
        """jordan_product(a, b) in unicode."""
        a, b = ab
        assert str(jordan_product(a, b)) == "jordan_product(a, b)"

    # --- Unary operations ---

    def test_reverse_unicode(self, ab):
        """reverse(a) in unicode."""
        a, _ = ab
        assert str(reverse(a)) == "reverse(a)"

    def test_reverse_latex(self, ab):
        """\\operatorname{reverse}(a) in LaTeX."""
        a, _ = ab
        assert reverse(a).latex() == r"\operatorname{reverse}(a)"

    def test_involute_unicode(self, ab):
        """involute(a) in unicode."""
        a, _ = ab
        assert str(involute(a)) == "involute(a)"

    def test_conjugate_unicode(self, ab):
        """conjugate(a) in unicode."""
        a, _ = ab
        assert str(conjugate(a)) == "conjugate(a)"

    def test_dual_unicode(self, ab):
        """dual(a) in unicode."""
        a, _ = ab
        assert str(dual(a)) == "dual(a)"

    def test_undual_unicode(self, ab):
        """undual(a) in unicode."""
        a, _ = ab
        assert str(undual(a)) == "undual(a)"

    def test_complement_unicode(self, ab):
        """complement(a) in unicode."""
        a, _ = ab
        assert str(complement(a)) == "complement(a)"

    def test_inverse_unicode(self, ab):
        """inverse(a) in unicode."""
        a, _ = ab
        assert str(inverse(a)) == "inverse(a)"

    def test_squared_unicode(self, ab):
        """squared(a) in unicode."""
        a, _ = ab
        assert str(squared(a)) == "squared(a)"

    # --- Wrap operations (were broken before fix) ---

    def test_norm_unicode(self, ab):
        """norm(a) in unicode."""
        a, _ = ab
        assert str(norm(a)) == "norm(a)"

    def test_norm_latex(self, ab):
        """\\operatorname{norm}(a) in LaTeX."""
        a, _ = ab
        assert norm(a).latex() == r"\operatorname{norm}(a)"

    def test_unit_unicode(self, ab):
        """unit(a) in unicode."""
        a, _ = ab
        assert str(unit(a)) == "unit(a)"

    def test_unit_latex(self, ab):
        """\\operatorname{unit}(a) in LaTeX."""
        a, _ = ab
        assert unit(a).latex() == r"\operatorname{unit}(a)"

    def test_exp_unicode(self, ab):
        """exp(outer_product(a, b)) in unicode."""
        a, b = ab
        assert str(exp(a ^ b)) == "exp(outer_product(a, b))"

    def test_exp_latex(self, ab):
        """\\operatorname{exp}(...) in LaTeX."""
        a, b = ab
        assert r"\operatorname{exp}" in exp(a ^ b).latex()

    def test_log_unicode(self, ab):
        """log(a) in unicode."""
        a, _ = ab
        assert str(log(a)) == "log(a)"

    def test_log_latex(self, ab):
        """\\operatorname{log}(a) in LaTeX."""
        a, _ = ab
        assert log(a).latex() == r"\operatorname{log}(a)"

    def test_scalar_sqrt_unicode(self, s):
        """scalar_sqrt(s) in unicode."""
        assert str(scalar_sqrt(s)) == "scalar_sqrt(s)"

    def test_scalar_sqrt_latex(self, s):
        """scalar_sqrt in LaTeX operatorname."""
        assert scalar_sqrt(s).latex() == r"\operatorname{scalar\_sqrt}(s)"

    def test_grade_unicode(self, ab):
        """grade(geometric_product(a, b), 1) in unicode."""
        a, b = ab
        assert str(grade(a * b, 1)) == "grade(geometric_product(a, b), 1)"

    def test_grade_latex(self, ab):
        """\\operatorname{grade}(\\operatorname{geometric_product}(a, b), 1) in LaTeX."""
        a, b = ab
        latex = grade(a * b, 1).latex()
        assert r"\operatorname{grade}" in latex
        assert "1" in latex

    def test_even_grades_unicode(self, ab):
        """even_grades(a) in unicode."""
        a, _ = ab
        assert str(even_grades(a)) == "even_grades(a)"

    def test_odd_grades_unicode(self, ab):
        """odd_grades(a) in unicode."""
        a, _ = ab
        assert str(odd_grades(a)) == "odd_grades(a)"

    # --- Composition ---

    def test_nested_expression(self, ab):
        """Nested: grade(geometric_product(a, reverse(b)), 1)."""
        a, b = ab
        result = str(grade(a * reverse(b), 1))
        assert "grade(" in result
        assert "geometric_product(" in result
        assert "reverse(" in result

    # --- Default not affected ---

    def test_default_not_affected(self):
        """Default notation still uses juxtaposition."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert str(a * b) == "ab"


class TestFunctionalShortPreset:
    """Notation.functional_short() uses short-form function names."""

    @pytest.fixture
    def fn_alg(self):
        return Algebra((1, 1, 1), notation=Notation.functional_short())

    @pytest.fixture
    def ab(self, fn_alg):
        e1, e2, _ = fn_alg.basis_vectors(lazy=True)
        return e1.name("a"), e2.name("b")

    def test_gp_unicode(self, ab):
        """gp(a, b) in unicode."""
        a, b = ab
        assert str(a * b) == "gp(a, b)"

    def test_op_unicode(self, ab):
        """op(a, b) in unicode."""
        a, b = ab
        assert str(a ^ b) == "op(a, b)"

    def test_lc_unicode(self, ab):
        """lc(a, b) in unicode."""
        a, b = ab
        assert str(left_contraction(a, b)) == "lc(a, b)"

    def test_reverse_short(self, ab):
        """Short form uses rev() not reverse()."""
        a, _ = ab
        assert str(reverse(a)) == "rev(a)"

    def test_gp_latex(self, ab):
        """\\operatorname{gp} in LaTeX."""
        a, b = ab
        assert r"\operatorname{gp}" in (a * b).latex()


class TestUnitFractionNotation:
    """unit_fraction notation kind renders as x/‖x‖."""

    def test_unicode(self):
        """B/‖B‖ in unicode."""
        from galaga.notation import NotationRule

        alg = Algebra((1, 1, 1))
        alg.notation.set("Unit", "unicode", NotationRule(kind="unit_fraction"))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        B = (e1 ^ e2).name("B")
        assert str(unit(B)) == "B/‖B‖"

    def test_latex(self):
        r"""\\frac{B}{\\lVert B \\rVert} in LaTeX."""
        from galaga.notation import NotationRule

        alg = Algebra((1, 1, 1))
        alg.notation.set("Unit", "latex", NotationRule(kind="unit_fraction"))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        B = (e1 ^ e2).name("B")
        assert unit(B).latex() == r"\frac{B}{\lVert B \rVert}"

    def test_compound_wraps(self):
        """Compound expression gets parenthesised in numerator."""
        from galaga.notation import NotationRule

        alg = Algebra((1, 1, 1))
        alg.notation.set("Unit", "unicode", NotationRule(kind="unit_fraction"))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        a, b = e1.name("a"), e2.name("b")
        assert str(unit(a + b)) == "(a + b)/‖a + b‖"

    def test_display_shows_fraction(self):
        """display() shows fraction form distinct from hat name."""
        from galaga.notation import NotationRule

        alg = Algebra((1, 1, 1))
        alg.notation.set("Unit", "latex", NotationRule(kind="unit_fraction"))
        e1, e2, _ = alg.basis_vectors(lazy=True)
        B = (e1 ^ e2).name("B")
        Bhat = unit(B).name(latex=r"\hat{B}")
        d = Bhat.display().latex()
        assert r"\hat{B}" in d
        assert r"\frac{B}" in d
