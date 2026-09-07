"""Under-accents distinguish one-argument commands from annotation glyphs."""

import numpy as np
import pytest

import galaga as ga
from galaga.display import emit
from galaga.expression import evaluate
from galaga.rendering import Accent, Group, Identifier, Infix


@pytest.mark.parametrize("symbol", ("*", "?", r"\sim", r"\star", r"\text{mark}"))
@pytest.mark.parametrize("compound", (False, True))
def test_arbitrary_underaccent_symbols_use_underset(symbol, compound):
    body = Group(Infix((Identifier("a"), Identifier("b")), "+")) if compound else Identifier("a")
    node = Accent(body, ga.Name("mark", "\u0330", symbol), position="under")
    before = hash(node)
    rendered_body = r"\left(a + b\right)" if compound else "a"
    assert emit(node, "latex") == rf"\underset{{{symbol}}}{{{rendered_body}}}"
    assert emit(node, "ascii") == ("mark((a + b))" if compound else "mark(a)")
    assert emit(node, "unicode") == ("(a + b)\u0330" if compound else "a\u0330")
    assert hash(node) == before


@pytest.mark.parametrize(
    "command",
    (r"\underline", r"\utilde", r"\underbrace", r"\underleftarrow", r"\underrightarrow", r"\underleftrightarrow"),
)
def test_native_underaccent_commands_keep_their_one_argument_form(command):
    assert emit(Accent(Identifier("x"), command, position="under"), "latex") == rf"{command}{{x}}"


@pytest.mark.parametrize("symbol, expected", ((r"\widehat", r"\widehat{x}"), ("*", r"\overset{*}{x}")))
def test_overaccents_keep_the_existing_command_and_annotation_forms(symbol, expected):
    assert emit(Accent(Identifier("x"), symbol), "latex") == expected


@pytest.mark.parametrize("signature", ((1, 1, 1, 0), (1, -1, 1, 1)))
@pytest.mark.parametrize("compound", (False, True))
def test_custom_underaccent_preserves_numeric_value_provenance_and_other_targets(signature, compound):
    algebra = ga.Algebra(signature)
    # Compute first with no expression or naming.
    a, b = algebra.blade(3), algebra.blade(9)
    source = a + b if compound else a
    expected = ga.antireverse(source)
    a, b = a.named("A"), b.named("B")
    result = ga.antireverse(a + b if compound else a)
    expression, before = result.expr, result.data.copy()
    original = ga.Notation.lengyel()
    notation = original.with_rule(
        "antireverse", ga.RenderRule("underaccent", symbol=ga.Name("sim", "\u0330", r"\sim")), target="latex"
    )
    body = r"\left(A + B\right)" if compound else "A"
    assert result.display("expr/latex", notation=notation) == rf"\underset{{\sim}}{{{body}}}"
    assert result.display("expr/latex", notation=original) == (r"\utilde{A + B}" if compound else r"\utilde{A}")
    for target in ("ascii", "unicode"):
        assert result.display(f"expr/{target}", notation=notation) == result.display(
            f"expr/{target}", notation=original
        )
    assert result == expected
    np.testing.assert_array_equal(result.data, before)
    assert result.expr is expression
    assert evaluate(expression, algebra=algebra, environment={"A": a, "B": b}) == result
    assert hash(result) == hash(expected)
