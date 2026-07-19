from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

from galaga.display import emit, render
from galaga.expression import Call as ExpressionCall
from galaga.expression import Symbol
from galaga.names import Name
from galaga.presentation import default_presentation
from galaga.rendering import (
    Accent,
    Call,
    Delimited,
    Equality,
    Fraction,
    Group,
    Identifier,
    Infix,
    Literal,
    MathClass,
    Postfix,
    Power,
    Prefix,
    Product,
    Subscript,
    Sum,
    SumTerm,
    Text,
    Underset,
    Wrapper,
)


@pytest.mark.parametrize(
    ("node", "ascii", "unicode", "latex"),
    (
        (Identifier(Name("alpha", "α", r"\alpha")), "alpha", "α", r"\alpha"),
        (Literal(2.5), "2.5", "2.5", "2.5"),
        (Text("a_b%"), "a_b%", "a_b%", r"a\_b\%"),
        (
            Group(Infix((Identifier("a"), Identifier("b")), "+")),
            "(a + b)",
            "(a + b)",
            r"\left(a + b\right)",
        ),
        (Sum((SumTerm(Identifier("a")), SumTerm(Identifier("b"), True))), "a - b", "a - b", "a - b"),
        (
            Product((Literal(2), Identifier(Name("e1", "e₁", r"e_{1}")))),
            "2e1",
            "2e₁",
            r"2 e_{1}",
        ),
        (Fraction(Identifier("a"), Identifier("b")), "a / b", "a / b", r"\frac{a}{b}"),
        (Power(Identifier("x"), Literal(2)), "x^2", "x²", r"x^2"),
        (Subscript(Identifier("x"), Literal(2)), "x[2]", "x₂", r"x_{2}"),
        (
            Call("metric_inner_product", (Identifier("a"), Identifier("b"))),
            "metric_inner_product(a, b)",
            "metric_inner_product(a, b)",
            r"\operatorname{metric\_inner\_product}\left(a, b\right)",
        ),
        (Prefix("-", Identifier("x")), "-x", "-x", "-x"),
        (Postfix(Identifier("x"), Name("dag", "†", r"^{\dagger}")), "xdag", "x†", r"x^{\dagger}"),
        (
            Infix((Identifier("a"), Identifier("b")), Name("^", "∧", r"\wedge")),
            "a ^ b",
            "a ∧ b",
            r"a \wedge b",
        ),
        (Accent(Identifier("x"), Name("~", "\u0303", r"\widetilde")), "~x", "x̃", r"\widetilde{x}"),
        (
            MathClass(Underset(Identifier(Name("wedge", "⩓", r"\text{⩓}")), Literal(1)), "binary"),
            "wedge[1]",
            "⩓₁",
            r"\mathbin{\underset{1}{\text{⩓}}}",
        ),
        (
            Wrapper(
                Identifier("x"),
                Name("|", "|", r"\lvert"),
                Name("|", "|", r"\rvert"),
            ),
            "|x|",
            "|x|",
            r"\left\lvert x \right\rvert",
        ),
        (
            Delimited((Literal(1), Literal(2)), opening="[", closing="]"),
            "[1, 2]",
            "[1, 2]",
            r"\left[1, 2\right]",
        ),
        (
            Equality((Identifier("x"), Literal(2))),
            "x = 2",
            "x = 2",
            r"x \quad = \quad 2",
        ),
    ),
)
def test_every_semantic_node_is_consumed_by_all_three_emitters(
    node: object,
    ascii: str,
    unicode: str,
    latex: str,
) -> None:
    assert emit(node, "ascii") == ascii  # type: ignore[arg-type]
    assert emit(node, "unicode") == unicode  # type: ignore[arg-type]
    assert emit(node, "latex") == latex  # type: ignore[arg-type]


def test_teaching_equality_deduplicates_after_target_specific_rendering() -> None:
    equality = Equality(
        (
            Identifier(Name("x", "same", "x")),
            Identifier(Name("y", "same", "y")),
            Literal(2),
            Literal(2),
        )
    )

    assert emit(equality, "ascii") == "x = y = 2"
    assert emit(equality, "unicode") == "same = 2"
    assert emit(equality, "latex") == r"x \quad = \quad y \quad = \quad 2"


def test_compact_calls_and_fraction_bars_own_their_target_specific_grouping() -> None:
    compact = Call("f", (Identifier("a"), Identifier("b")), scalable=False)
    numerator = Infix((Identifier("a"), Identifier("b")), "+", precedence=20)
    fraction = Fraction(numerator, Literal(3))

    assert emit(compact, "latex") == r"\operatorname{f}(a,\, b)"
    assert emit(fraction, "latex") == r"\frac{a + b}{3}"
    assert emit(fraction, "ascii") == "(a + b) / 3"


def test_unicode_preserves_position_for_symbols_without_script_codepoints() -> None:
    star = Identifier(Name("star", "★", r"\text{★}"))
    bulk = Identifier(Name("bulk", "●", r"\text{●}"))

    assert emit(Power(Identifier("a"), star), "unicode") == "a^★"
    assert emit(Subscript(Identifier("a"), star), "unicode") == "a_★"
    assert emit(Subscript(Identifier("a"), bulk), "unicode") == "a_●"


@pytest.mark.parametrize(
    ("expression", "expected"),
    (
        (
            ExpressionCall(
                "geometric_product",
                (ExpressionCall("add", (Symbol("a"), Symbol("b"))), Symbol("c")),
            ),
            "(a + b)c",
        ),
        (
            ExpressionCall(
                "subtract",
                (Symbol("a"), ExpressionCall("subtract", (Symbol("b"), Symbol("c")))),
            ),
            "a - (b - c)",
        ),
        (
            ExpressionCall(
                "subtract",
                (ExpressionCall("subtract", (Symbol("a"), Symbol("b"))), Symbol("c")),
            ),
            "a - b - c",
        ),
        (
            ExpressionCall(
                "outer_product",
                (Symbol("a"), ExpressionCall("geometric_product", (Symbol("b"), Symbol("c")))),
            ),
            "a ^ (bc)",
        ),
        (
            ExpressionCall("reverse", (ExpressionCall("add", (Symbol("a"), Symbol("b"))),)),
            "~(a + b)",
        ),
    ),
)
def test_golden_ascii_parenthesization_preserves_expression_meaning(
    expression: ExpressionCall,
    expected: str,
) -> None:
    assert render(expression, target="ascii", presentation=default_presentation(1)) == expected


def test_scientific_literals_and_ordinary_text_are_rewritten_only_by_emitters() -> None:
    assert emit(Literal(1.25e20), "ascii") == "1.25e+20"
    assert emit(Literal(1.25e20), "latex") == r"1.25 \times 10^{20}"
    assert emit(Text(r"x_1 & 50%"), "latex") == r"x\_1 \& 50\%"


def test_emitters_have_no_dependency_on_legacy_numeric_or_rendering_modules() -> None:
    package = Path(__file__).parents[2] / "galaga" / "rendering"
    forbidden = {"algebra", "latex_build", "latex_emit", "render"}

    for source_path in (package / "_emit.py", package / "ascii.py", package / "unicode.py", package / "latex.py"):
        tree = ast.parse(source_path.read_text())
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.rsplit(".", 1)[-1] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.rsplit(".", 1)[-1])
        assert imports.isdisjoint(forbidden), source_path.name


@pytest.mark.parametrize(
    "program",
    (
        "from galaga.rendering.tree import Identifier; assert Identifier('x').name.ascii == 'x'",
        "import galaga.rendering; import galaga.facade; import galaga.display",
        "import galaga.facade; import galaga.display; import galaga.rendering",
    ),
)
def test_rendering_facade_and_display_modules_import_in_either_direction(program: str) -> None:
    result = subprocess.run(
        [sys.executable, "-c", program],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
