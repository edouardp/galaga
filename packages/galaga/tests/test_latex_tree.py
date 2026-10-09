"""Immutable semantic-tree layout and exact LaTeX emission.

V2 escapes Text, uses explicit mathematical identifiers, and performs
script-fraction layout during emission. It does not mutate/rewrite layout
trees to hoist signs, erase division by one, or collapse explicit groups.
"""

import pytest

from galaga import Name
from galaga.rendering import tree as t
from galaga.rendering.latex import emit

A, B, C, E, X, Y = (t.Identifier(name) for name in ("a", "b", "c", "e", "x", "y"))
THETA = t.Identifier(Name.from_latex(r"\theta"))
AB = t.Sum((t.SumTerm(A), t.SumTerm(B)))
HALF = t.Fraction(A, t.Literal(2))
NEG_A = t.Prefix("-", A)
TILDE = Name("tilde", "̃", r"\tilde")
WIDE = Name("tilde", "̃", r"\widetilde")

# Exact emission examples for atomic and nested layouts.
CASES = (
    ("TestEmitText.test_plain", t.Text("x"), "x"),
    ("TestEmitText.test_latex_command", t.Identifier(Name.from_latex(r"\alpha")), r"\alpha"),
    ("TestEmitText.test_empty", t.Text(""), ""),
    ("TestEmitSeq.test_two_children", t.Product((A, B)), "a b"),
    ("TestEmitSeq.test_separator", AB, "a + b"),
    ("TestEmitSeq.test_three_children", t.Product((A, B, C), separator=","), "a , b , c"),
    ("TestEmitSeq.test_single_child", t.Product((X,)), "x"),
    ("TestEmitSeq.test_empty", t.Text(""), ""),
    ("TestEmitSeq.test_nested", t.Sum((t.SumTerm(t.Product((X, Y))), t.SumTerm(t.Identifier("z")))), "x y + z"),
    ("TestEmitFrac.test_simple", t.Fraction(A, B), r"\frac{a}{b}"),
    ("TestEmitFrac.test_small", t.Fraction(A, B), r"\frac{a}{b}"),
    ("TestEmitFrac.test_nested_num", t.Fraction(t.Sum((t.SumTerm(X), t.SumTerm(Y))), t.Literal(2)), r"\frac{x + y}{2}"),
    ("TestEmitSup.test_simple", t.Power(E, X), "e^x"),
    ("TestEmitSup.test_complex_base", t.Power(t.Group(AB), t.Literal(2)), r"\left(a + b\right)^2"),
    ("TestEmitSup.test_complex_exp", t.Power(E, t.Prefix("-", THETA)), r"e^{-\theta}"),
    (
        "TestEmitSup.test_sup_on_sup_braces",
        t.Power(t.Power(E, X), t.Identifier(Name("dagger", latex=r"\dagger"))),
        r"{e^x}^{\dagger}",
    ),
    ("TestEmitSup.test_sup_on_non_sup_no_braces", t.Power(A, t.Literal(2)), "a^2"),
    ("TestEmitParens.test_simple", t.Group(X), r"\left(x\right)"),
    ("TestEmitParens.test_nested", t.Group(t.Group(A)), r"\left(\left(a\right)\right)"),
    ("TestEmitCommand.test_tilde", t.Accent(A, TILDE), r"\tilde{a}"),
    ("TestEmitCommand.test_widetilde", t.Accent(AB, WIDE), r"\widetilde{a + b}"),
    ("TestEmitCommand.test_hat", t.Accent(t.Identifier("v"), Name("hat", "̂", r"\hat")), r"\hat{v}"),
    (
        "TestEmitCommand.test_operatorname",
        t.Identifier(Name("rev", latex=r"\operatorname{rev}")),
        r"\operatorname{rev}",
    ),
    ("TestEmitDeepNesting.test_frac_in_sup", t.Power(E, t.Fraction(THETA, t.Literal(2))), r"e^{\theta/2}"),
    ("TestEmitDeepNesting.test_command_around_frac", t.Accent(t.Fraction(A, B), WIDE), r"\widetilde{\frac{a}{b}}"),
    (
        "TestRewriteFracInSup.test_frac_becomes_slash_in_sup",
        t.Power(E, t.Fraction(THETA, t.Literal(2))),
        r"e^{\theta/2}",
    ),
    ("TestRewriteFracInSup.test_frac_outside_sup_unchanged", t.Fraction(A, B), r"\frac{a}{b}"),
    (
        "TestRewriteFracInSup.test_nested_frac_in_sup",
        t.Power(E, t.Product((t.Fraction(t.Prefix("-", THETA), t.Literal(2)), t.Identifier("B")))),
        r"e^{\left(-\theta/2\right) B}",
    ),
    (
        "TestRewriteFracInSup.test_frac_in_sup_in_frac_outer_unchanged",
        t.Fraction(t.Power(E, HALF), B),
        r"\frac{e^{a/2}}{b}",
    ),
    ("TestRewriteFracInSup.test_already_small_in_sup_becomes_slash", t.Power(E, t.Fraction(A, B)), "e^{a/b}"),
    ("TestRewriteFracInSup.test_deeply_nested_sup", t.Power(E, t.Group(t.Fraction(X, Y))), r"e^{\left(x/y\right)}"),
    (
        "TestRewriteFracInSup.test_no_sup_no_change",
        t.Sum((t.SumTerm(t.Fraction(A, B)), t.SumTerm(t.Accent(X, TILDE)))),
        r"\frac{a}{b} + \tilde{x}",
    ),
    ("TestRewriteNestedParens.test_double_parens", t.Group(t.Group(A)), r"\left(\left(a\right)\right)"),
    (
        "TestRewriteNestedParens.test_triple_parens",
        t.Group(t.Group(t.Group(X))),
        r"\left(\left(\left(x\right)\right)\right)",
    ),
    ("TestRewriteNestedParens.test_parens_around_non_parens_unchanged", t.Group(AB), r"\left(a + b\right)"),
    (
        "TestRewriteNestedParens.test_parens_in_seq_collapsed",
        t.Sum((t.SumTerm(t.Group(t.Group(A))), t.SumTerm(B))),
        r"\left(\left(a\right)\right) + b",
    ),
    ("TestRewriteHoistNeg.test_neg_num_hoisted", t.Fraction(NEG_A, B), r"\frac{-a}{b}"),
    ("TestRewriteHoistNeg.test_neg_text_hoisted", t.Fraction(t.Text("-a"), t.Literal(2)), r"\frac{-a}{2}"),
    ("TestRewriteHoistNeg.test_no_neg_unchanged", t.Fraction(A, B), r"\frac{a}{b}"),
    (
        "TestRewriteHoistNeg.test_neg_in_sup_frac_hoisted_before_slash",
        t.Power(E, t.Fraction(NEG_A, t.Literal(2))),
        "e^{-a/2}",
    ),
    ("TestRewriteFracOne.test_frac_over_1", t.Fraction(A, t.Literal(1)), r"\frac{a}{1}"),
    ("TestRewriteFracOne.test_frac_complex_over_1", t.Fraction(AB, t.Literal(1)), r"\frac{a + b}{1}"),
    ("TestRewriteFracOne.test_frac_over_1_in_sup", t.Power(E, t.Fraction(X, t.Literal(1))), "e^{x/1}"),
    ("TestRewriteFracOne.test_frac_normal_denom_unchanged", HALF, r"\frac{a}{2}"),
    ("TestRewriteIdempotent.test_double_rewrite", t.Power(E, t.Fraction(THETA, t.Literal(2))), r"e^{\theta/2}"),
)


@pytest.mark.parametrize("identifier, tree, expected", CASES, ids=[row[0] for row in CASES])
def test_tree_layout_is_immutable_and_matches_exact_latex(identifier, tree, expected):
    before = repr(tree), hash(tree)
    assert emit(tree) == expected
    assert emit(tree) == expected
    assert (repr(tree), hash(tree)) == before


def test_empty_sequences_and_small_fraction_flags_are_not_implicit_legacy_adapters():
    assert emit(t.Text("")) == ""
    with pytest.raises(ValueError, match="at least"):
        t.Product(())
    with pytest.raises(TypeError):
        t.Fraction(A, B, small=True)
    assert not hasattr(t, "rewrite")


def test_text_is_escaped_and_explicit_math_identifiers_are_distinct():
    assert emit(t.Text(r"\alpha")) == r"\textbackslash{}alpha"
    assert emit(t.Text("a_b")) == r"a\_b"
    assert emit(t.Identifier(Name.from_latex(r"\alpha"))) == r"\alpha"
    assert emit(t.Call("rev", (A,))) == r"\operatorname{rev}\left(a\right)"
