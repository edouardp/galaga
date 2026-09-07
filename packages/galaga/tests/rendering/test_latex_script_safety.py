"""LaTeX spelling guards must preserve the whole operand without evaluation."""

import pytest

import galaga as ga
from galaga.expression import Call, Symbol
from galaga.rendering import Identifier, Literal, Power, Prefix, Subscript, Wrapper
from galaga.rendering.latex import emit


@pytest.mark.parametrize(
    "spelling, expected",
    (
        ("a", "a^*"),
        (r"\theta", r"\theta^*"),
        ("x^2", "{x^2}^*"),
        (r"B^\star", r"{B^\star}^*"),
        (r"{x^2}", r"{x^2}^*"),
        (r"\widehat{x^2}", r"\widehat{x^2}^*"),
        (r"x_{i^2}", r"x_{i^2}^*"),
        (r"x_\star", r"x_\star^*"),
        (r"\text{a + b}", r"\text{a + b}^*"),
        (r"\text{a \{ + b}", r"\text{a \{ + b}^*"),
        (r"a\wedge b", r"\left(a\wedge b\right)^*"),
        (r"a \vee b", r"\left(a \vee b\right)^*"),
        ("a+b", r"\left(a+b\right)^*"),
        ("a-b", r"\left(a-b\right)^*"),
        ("a/b", r"\left(a/b\right)^*"),
        (r"a \cdot b", r"\left(a \cdot b\right)^*"),
        (r"a \times b", r"\left(a \times b\right)^*"),
        (r"a \mathbin{+} b", r"\left(a \mathbin{+} b\right)^*"),
        (r"a+b^2", r"\left(a+b^2\right)^*"),
        (r"x^\dagger", r"{x^\dagger}^*"),
        (r"x^+", r"{x^+}^*"),
        (r"x_+", r"x_+^*"),
        (r"\^", r"\^^*"),
    ),
)
def test_script_on_opaque_name_protects_top_level_syntax_only(spelling, expected):
    assert emit(Power(Identifier(ga.Name("x", latex=spelling)), Identifier("*"))) == expected


@pytest.mark.parametrize(
    "operator, expected",
    (
        (r"\tilde", r"\tilde a"),
        (r"\mathord{}\dagger", r"\mathord{}\dagger a"),
        (r"\tilde ", r"\tilde a"),
        (r"{\sim}", r"{\sim}a"),
        ("-", "-a"),
        (r"\\", r"\\a"),
        (r"\!", r"\!a"),
    ),
)
def test_prefix_command_tokens_do_not_merge_with_operand(operator, expected):
    assert emit(Prefix(ga.Name("~", latex=operator), Identifier("a"))) == expected


@pytest.mark.parametrize("operation, suffix", (("dual", "^*"), ("inverse", "^{-1}"), ("squared", "^2")))
def test_scripts_on_exponentials_use_one_complete_base(operation, suffix):
    expression = Call(operation, (Call("exp", (Symbol("a"),)),))
    assert ga.render(expression, target="latex", presentation=ga.Algebra(1).presentation) == "{e^{a}}" + suffix


@pytest.mark.parametrize(
    "base, expected",
    (
        (Identifier(ga.Name("x", latex="x_i")), "{x_i}_{j}"),
        (Identifier(ga.Name("x", latex=r"x_{\text{a_b}}")), r"{x_{\text{a_b}}}_{j}"),
        (Identifier(ga.Name("x", latex=r"\text{a_b}")), r"\text{a_b}_{j}"),
        (Identifier(ga.Name("x", latex=r"\_")), r"\__{j}"),
        (Identifier(ga.Name("x", latex="a+b")), r"\left(a+b\right)_{j}"),
        (Subscript(Identifier("x"), Identifier("i")), "{x_{i}}_{j}"),
        (Wrapper(Identifier("x"), "e^{", "}", scalable=False, script_style=True), "e^{x}_{j}"),
    ),
)
def test_subscript_guard_respects_braces_escapes_and_other_script(base, expected):
    assert emit(Subscript(base, Identifier("j"))) == expected


@pytest.mark.parametrize("value, expected", ((1e-10, "{10^{-10}}^2"), (1.2e-7, r"\left(1.2 \times 10^{-7}\right)^2")))
def test_script_on_scientific_literal_covers_mantissa_and_existing_exponent(value, expected):
    assert emit(Power(Literal(value), Literal(2))) == expected


@pytest.mark.parametrize("target, expected", (("ascii", "x^*"), ("unicode", "x^★")))
def test_latex_spelling_does_not_change_other_target_names(target, expected):
    expression = Call("dual", (Symbol(ga.Name("x", latex=r"a \wedge b")),))
    assert ga.render(expression, target=target, presentation=ga.Algebra(1).presentation) == expected
