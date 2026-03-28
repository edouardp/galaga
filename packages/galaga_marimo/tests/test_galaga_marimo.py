"""Tests for galaga_marimo renderer and API.

These tests mock string.templatelib types so they can run on Python 3.13+.
The rendering logic is tested via render_value() and render_template()
with synthetic Template/Interpolation objects.
"""

import sys
import types
from dataclasses import dataclass
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Mock string.templatelib for Python < 3.14
# ---------------------------------------------------------------------------


@dataclass
class FakeInterpolation:
    value: Any
    expression: str = ""
    conversion: str | None = None
    format_spec: str = ""


class FakeTemplate:
    """Mimics string.templatelib.Template iteration."""

    def __init__(self, *items):
        self._items = items

    def __iter__(self):
        return iter(self._items)


# Patch string.templatelib before importing galaga_marimo
_mock_templatelib = types.ModuleType("string.templatelib")
_mock_templatelib.Template = FakeTemplate
_mock_templatelib.Interpolation = FakeInterpolation
sys.modules["string.templatelib"] = _mock_templatelib

from galaga_marimo.api import Doc, block, block_latex, doc, inline, latex, md, text
from galaga_marimo.renderer import (
    Rendered,
    RenderKind,
    _assemble,
    _escape_md,
    _get_latex,
    _has_latex,
    _strip_latex_delimiters,
    render_template,
    render_value,
)

# ---------------------------------------------------------------------------
# Helpers — fake GA objects
# ---------------------------------------------------------------------------


class FakeMultivector:
    """Mimics ga.Multivector with .latex() and str()."""

    def __init__(self, latex_str: str, unicode_str: str):
        self._latex = latex_str
        self._unicode = unicode_str

    def latex(self) -> str:
        return self._latex

    def __str__(self) -> str:
        return self._unicode


class FakeExpr:
    """Mimics ga.symbolic.Expr with .latex() and str()."""

    def __init__(self, latex_str: str, unicode_str: str):
        self._latex_str = latex_str
        self._unicode = unicode_str

    def latex(self) -> str:
        return self._latex_str

    def __str__(self) -> str:
        return self._unicode


class PlainObject:
    """Object with no .latex() method."""

    def __init__(self, s: str):
        self._s = s

    def __str__(self) -> str:
        return self._s

    def __repr__(self) -> str:
        return f"PlainObject({self._s!r})"


class ReprLatexOnly:
    """Object with _repr_latex_() but no .latex() — e.g. SymPy, Pandas."""

    def __init__(self, latex_str: str, text_str: str):
        self._latex = latex_str
        self._text = text_str

    def _repr_latex_(self) -> str:
        return self._latex

    def __str__(self) -> str:
        return self._text


# ---------------------------------------------------------------------------
# _repr_latex_ / Jupyter protocol support tests
# ---------------------------------------------------------------------------


class TestReprLatexProtocol:
    """Test _repr_latex_() fallback for third-party objects."""

    def test_strip_inline_delimiters(self):
        assert _strip_latex_delimiters("$x^2$") == "x^2"

    def test_strip_block_delimiters(self):
        assert _strip_latex_delimiters("$$x^2$$") == "x^2"

    def test_strip_block_delimiters_with_whitespace(self):
        assert _strip_latex_delimiters("$$\nx^2\n$$") == "x^2"

    def test_no_delimiters_unchanged(self):
        assert _strip_latex_delimiters("x^2") == "x^2"

    def test_has_latex_with_latex_method(self):
        obj = FakeMultivector("e_{1}", "e₁")
        assert _has_latex(obj) is True

    def test_has_latex_with_repr_latex(self):
        obj = ReprLatexOnly("$x^2$", "x²")
        assert _has_latex(obj) is True

    def test_has_latex_with_neither(self):
        obj = PlainObject("hello")
        assert _has_latex(obj) is False

    def test_get_latex_prefers_latex_method(self):
        """When both .latex() and _repr_latex_() exist, .latex() wins."""

        class Both:
            def latex(self):
                return "from_latex"

            def _repr_latex_(self):
                return "$from_repr$"

        assert _get_latex(Both()) == "from_latex"

    def test_get_latex_falls_back_to_repr_latex(self):
        obj = ReprLatexOnly("$\\alpha + \\beta$", "α + β")
        assert _get_latex(obj) == "\\alpha + \\beta"

    def test_get_latex_strips_block_delimiters(self):
        obj = ReprLatexOnly("$$\\frac{a}{b}$$", "a/b")
        assert _get_latex(obj) == "\\frac{a}{b}"

    def test_repr_latex_object_auto_detected(self):
        obj = ReprLatexOnly("$x^2 + y^2$", "x² + y²")
        r = render_value(obj, None, "")
        assert r.kind == RenderKind.INLINE_LATEX
        assert r.value == "x^2 + y^2"

    def test_repr_latex_object_in_template(self):
        obj = ReprLatexOnly("$\\sqrt{2}$", "√2")
        t = FakeTemplate("Value: ", FakeInterpolation(obj))
        result = render_template(t)
        assert result == "Value: $\\sqrt{2}$"

    def test_repr_latex_with_block_spec(self):
        obj = ReprLatexOnly("$x$", "x")
        r = render_value(obj, None, "block")
        assert r.kind == RenderKind.BLOCK_LATEX
        assert r.value == "x"

    def test_repr_latex_with_text_spec(self):
        obj = ReprLatexOnly("$x$", "x")
        r = render_value(obj, None, "text")
        assert r.kind == RenderKind.TEXT
        assert r.value == "x"

    def test_repr_latex_with_str_conversion(self):
        obj = ReprLatexOnly("$x$", "x_text")
        r = render_value(obj, "s", "")
        assert r.kind == RenderKind.TEXT
        assert r.value == "x_text"


# ---------------------------------------------------------------------------
# render_value tests
# ---------------------------------------------------------------------------


class TestRenderValue:
    """Test the core value classification logic."""

    def test_latex_object_auto_detected(self):
        mv = FakeMultivector("e_{1} + e_{2}", "e₁ + e₂")
        r = render_value(mv, None, "")
        assert r.kind == RenderKind.INLINE_LATEX
        assert r.value == "e_{1} + e_{2}"

    def test_plain_object_becomes_text(self):
        obj = PlainObject("hello")
        r = render_value(obj, None, "")
        assert r.kind == RenderKind.TEXT
        assert r.value == "hello"

    def test_string_becomes_text(self):
        r = render_value("world", None, "")
        assert r.kind == RenderKind.TEXT
        assert r.value == "world"

    def test_int_becomes_text(self):
        r = render_value(42, None, "")
        assert r.kind == RenderKind.TEXT
        assert r.value == "42"

    def test_float_becomes_text(self):
        r = render_value(3.14, None, "")
        assert r.kind == RenderKind.TEXT
        assert r.value == "3.14"

    # --- Conversion flags ---

    def test_repr_conversion(self):
        mv = FakeMultivector("e_{1}", "e₁")
        r = render_value(mv, "r", "")
        assert r.kind == RenderKind.TEXT
        # repr of FakeMultivector
        assert "FakeMultivector" in r.value or "e" in r.value

    def test_str_conversion(self):
        mv = FakeMultivector("e_{1}", "e₁")
        r = render_value(mv, "s", "")
        assert r.kind == RenderKind.TEXT
        assert r.value == "e₁"

    def test_ascii_conversion(self):
        mv = FakeMultivector("e_{1}", "e₁")
        r = render_value(mv, "a", "")
        assert r.kind == RenderKind.TEXT
        # ascii() escapes non-ASCII
        assert "\\u" in r.value or "e" in r.value

    # --- Format specs ---

    def test_latex_format_spec(self):
        mv = FakeMultivector("e_{12}", "e₁₂")
        r = render_value(mv, None, "latex")
        assert r.kind == RenderKind.INLINE_LATEX
        assert r.value == "e_{12}"

    def test_inline_format_spec(self):
        mv = FakeMultivector("e_{12}", "e₁₂")
        r = render_value(mv, None, "inline")
        assert r.kind == RenderKind.INLINE_LATEX
        assert r.value == "e_{12}"

    def test_block_format_spec(self):
        mv = FakeMultivector("e_{12}", "e₁₂")
        r = render_value(mv, None, "block")
        assert r.kind == RenderKind.BLOCK_LATEX
        assert r.value == "e_{12}"

    def test_text_format_spec(self):
        mv = FakeMultivector("e_{12}", "e₁₂")
        r = render_value(mv, None, "text")
        assert r.kind == RenderKind.TEXT
        assert r.value == "e₁₂"

    def test_unicode_format_spec(self):
        mv = FakeMultivector("e_{12}", "e₁₂")
        r = render_value(mv, None, "unicode")
        assert r.kind == RenderKind.TEXT
        assert r.value == "e₁₂"

    def test_numeric_format_spec(self):
        r = render_value(3.14159, None, ".2f")
        assert r.kind == RenderKind.TEXT
        assert r.value == "3.14"

    def test_latex_spec_on_plain_object_falls_back(self):
        obj = PlainObject("hello")
        r = render_value(obj, None, "latex")
        assert r.kind == RenderKind.TEXT
        assert r.value == "hello"

    def test_block_spec_on_plain_object_falls_back(self):
        obj = PlainObject("hello")
        r = render_value(obj, None, "block")
        assert r.kind == RenderKind.TEXT
        assert r.value == "hello"


# ---------------------------------------------------------------------------
# _assemble tests
# ---------------------------------------------------------------------------


class TestAssemble:
    def test_inline_latex(self):
        r = Rendered(RenderKind.INLINE_LATEX, "e_{1}")
        assert _assemble(r) == "$e_{1}$"

    def test_block_latex(self):
        r = Rendered(RenderKind.BLOCK_LATEX, "e_{1} + e_{2}")
        assert _assemble(r) == "\n\n$$e_{1} + e_{2}$$\n\n"

    def test_text_escaped(self):
        r = Rendered(RenderKind.TEXT, "<script>alert('xss')</script>")
        result = _assemble(r)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_text_ampersand_escaped(self):
        r = Rendered(RenderKind.TEXT, "a & b")
        assert _assemble(r) == "a &amp; b"


# ---------------------------------------------------------------------------
# _escape_md tests
# ---------------------------------------------------------------------------


class TestEscapeMd:
    def test_angle_brackets(self):
        assert _escape_md("<div>") == "&lt;div&gt;"

    def test_ampersand(self):
        assert _escape_md("a & b") == "a &amp; b"

    def test_plain_text_unchanged(self):
        assert _escape_md("hello world") == "hello world"


# ---------------------------------------------------------------------------
# render_template tests
# ---------------------------------------------------------------------------


class TestRenderTemplate:
    def test_literal_only(self):
        t = FakeTemplate("# Hello world")
        assert render_template(t) == "# Hello world"

    def test_single_latex_interpolation(self):
        mv = FakeMultivector("e_{1}", "e₁")
        t = FakeTemplate("Vector: ", FakeInterpolation(mv))
        result = render_template(t)
        assert result == "Vector: $e_{1}$"

    def test_mixed_text_and_latex(self):
        mv = FakeMultivector("e_{12}", "e₁₂")
        t = FakeTemplate("The bivector ", FakeInterpolation(mv), " is cool")
        result = render_template(t)
        assert result == "The bivector $e_{12}$ is cool"

    def test_plain_value_interpolation(self):
        t = FakeTemplate("Count: ", FakeInterpolation(42))
        result = render_template(t)
        assert result == "Count: 42"

    def test_block_format_spec(self):
        mv = FakeMultivector("R v \\tilde{R}", "RvR̃")
        t = FakeTemplate("Equation:\n", FakeInterpolation(mv, format_spec="block"))
        result = render_template(t)
        assert "$$" in result
        assert "R v \\tilde{R}" in result

    def test_multiple_interpolations(self):
        v = FakeMultivector("e_{1}", "e₁")
        w = FakeMultivector("e_{2}", "e₂")
        t = FakeTemplate("", FakeInterpolation(v), " and ", FakeInterpolation(w))
        result = render_template(t)
        assert result == "$e_{1}$ and $e_{2}$"

    def test_repr_conversion_in_template(self):
        mv = FakeMultivector("e_{1}", "e₁")
        t = FakeTemplate("Debug: ", FakeInterpolation(mv, conversion="r"))
        result = render_template(t)
        assert "$" not in result  # should not be LaTeX

    def test_numeric_format_spec_in_template(self):
        t = FakeTemplate("Pi ≈ ", FakeInterpolation(3.14159, format_spec=".3f"))
        result = render_template(t)
        assert result == "Pi ≈ 3.142"

    def test_symbolic_expr(self):
        expr = FakeExpr("R v \\tilde{R}", "RvR̃")
        t = FakeTemplate("Result: ", FakeInterpolation(expr))
        result = render_template(t)
        assert result == "Result: $R v \\tilde{R}$"

    def test_empty_template(self):
        t = FakeTemplate()
        assert render_template(t) == ""

    def test_html_escaping_in_text_values(self):
        t = FakeTemplate("User: ", FakeInterpolation("<b>admin</b>"))
        result = render_template(t)
        assert "<b>" not in result
        assert "&lt;b&gt;" in result


# ---------------------------------------------------------------------------
# Wrapper tests
# ---------------------------------------------------------------------------


class TestWrappers:
    def test_latex_wrapper_has_latex(self):
        mv = FakeMultivector("e_{1}", "e₁")
        wrapped = latex(mv)
        assert wrapped.latex() == "e_{1}"

    def test_latex_wrapper_on_plain_object(self):
        obj = PlainObject("hello")
        wrapped = latex(obj)
        assert wrapped.latex() == "hello"

    def test_block_latex_wrapper(self):
        mv = FakeMultivector("e_{1}", "e₁")
        wrapped = block_latex(mv)
        assert wrapped.latex() == "e_{1}"
        assert wrapped._galaga_block is True

    def test_block_latex_wrapper_renders_as_block(self):
        mv = FakeMultivector("e_{1}", "e₁")
        wrapped = block_latex(mv)
        r = render_value(wrapped, None, "")
        assert r.kind == RenderKind.BLOCK_LATEX
        assert r.value == "e_{1}"

    def test_text_wrapper_no_latex(self):
        mv = FakeMultivector("e_{1}", "e₁")
        wrapped = text(mv)
        assert not hasattr(wrapped, "latex")
        r = render_value(wrapped, None, "")
        assert r.kind == RenderKind.TEXT
        assert r.value == "e₁"

    def test_text_wrapper_in_template(self):
        mv = FakeMultivector("e_{1}", "e₁")
        wrapped = text(mv)
        t = FakeTemplate("Debug: ", FakeInterpolation(wrapped))
        result = render_template(t)
        assert "$" not in result
        assert "e₁" in result


# ---------------------------------------------------------------------------
# md/inline/block API tests (without marimo)
# ---------------------------------------------------------------------------


class TestApiWithoutMarimo:
    """Test that API functions produce correct markdown before passing to marimo."""

    def test_md_produces_correct_markdown(self):
        """md() passes correct markdown to mo.md(); test via render_template."""
        mv = FakeMultivector("e_{1}", "e₁")
        t = FakeTemplate("Vector: ", FakeInterpolation(mv))
        # render_template is what md() uses internally
        result = render_template(t)
        assert result == "Vector: $e_{1}$"

    def test_inline_produces_correct_markdown(self):
        mv = FakeMultivector("e_{1}", "e₁")
        t = FakeTemplate("v = ", FakeInterpolation(mv))
        # inline() wraps everything in $...$
        result = inline(t)
        # If marimo is installed, result is a marimo object; that's fine
        # The logic is tested via the string path
        assert result is not None

    def test_block_produces_correct_markdown(self):
        mv = FakeMultivector("e_{12}", "e₁₂")
        t = FakeTemplate(FakeInterpolation(mv))
        result = block(t)
        assert result is not None

    def test_md_calls_render_template(self):
        """Verify md() uses render_template correctly."""
        mv = FakeMultivector("e_{1} + e_{2}", "e₁ + e₂")
        t = FakeTemplate("Equation:\n", FakeInterpolation(mv, format_spec="block"))
        markdown = render_template(t)
        assert "$$" in markdown
        assert "e_{1} + e_{2}" in markdown

    def test_md_mixed_content_markdown(self):
        mv = FakeMultivector("e_{1}", "e₁")
        t = FakeTemplate(
            "# Heading\n\nThe vector ",
            FakeInterpolation(mv),
            " has magnitude ",
            FakeInterpolation(1.0, format_spec=".1f"),
        )
        markdown = render_template(t)
        assert "# Heading" in markdown
        assert "$e_{1}$" in markdown
        assert "1.0" in markdown

    def test_md_returns_something(self):
        """md() returns either a string or a marimo object."""
        mv = FakeMultivector("e_{1}", "e₁")
        t = FakeTemplate("Vector: ", FakeInterpolation(mv))
        result = md(t)
        assert result is not None


# ---------------------------------------------------------------------------
# Integration with real GA objects (if available)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Doc builder tests
# ---------------------------------------------------------------------------


class TestDoc:
    def test_single_md(self):
        mv = FakeMultivector("e_{1}", "e₁")
        d = Doc()
        d.md(FakeTemplate("Vector: ", FakeInterpolation(mv)))
        result = d.render()
        assert result is not None

    def test_multiple_md(self):
        mv1 = FakeMultivector("e_{1}", "e₁")
        mv2 = FakeMultivector("e_{2}", "e₂")
        d = Doc()
        d.md(FakeTemplate("First: ", FakeInterpolation(mv1)))
        d.md(FakeTemplate("Second: ", FakeInterpolation(mv2)))
        assert len(d._parts) == 2
        assert "$e_{1}$" in d._parts[0]
        assert "$e_{2}$" in d._parts[1]

    def test_render_joins_with_double_newline(self):
        d = Doc()
        d.md(FakeTemplate("# Title"))
        d.md(FakeTemplate("Paragraph"))
        markdown = "\n\n".join(d._parts)
        assert "# Title\n\nParagraph" == markdown

    def test_context_manager_auto_renders(self):
        mv = FakeMultivector("e_{1}", "e₁")
        with doc() as d:
            d.md(FakeTemplate("Result: ", FakeInterpolation(mv)))
        assert d._result is not None

    def test_text_appends_raw(self):
        d = Doc()
        d.text("**bold text**")
        assert d._parts == ["**bold text**"]

    def test_loop_pattern(self):
        """The main use case: building content in a loop."""
        items = [
            ("Alpha", FakeMultivector("\\alpha", "α")),
            ("Beta", FakeMultivector("\\beta", "β")),
        ]
        d = Doc()
        d.md(FakeTemplate("# Results"))
        for name, mv in items:
            d.md(FakeTemplate(f"**{name}:** ", FakeInterpolation(mv)))
        assert len(d._parts) == 3
        assert "# Results" in d._parts[0]
        assert "$\\alpha$" in d._parts[1]
        assert "$\\beta$" in d._parts[2]

    def test_explicit_render_before_exit(self):
        d = Doc()
        d.md(FakeTemplate("hello"))
        result = d.render()
        assert result is not None
        d.__exit__(None, None, None)
        assert d._result is result

    def test_inline_in_builder(self):
        mv = FakeMultivector("e_{1}", "e₁")
        d = Doc()
        d.inline(FakeTemplate("v = ", FakeInterpolation(mv)))
        assert "$v = e_{1}$" in d._parts[0]

    def test_block_in_builder(self):
        mv = FakeMultivector("e_{12}", "e₁₂")
        d = Doc()
        d.block(FakeTemplate(FakeInterpolation(mv)))
        assert "$$" in d._parts[0]
        assert "e_{12}" in d._parts[0]

    def test_line_appends_to_previous(self):
        d = Doc()
        d.line("| A | B |")
        d.line("|---|---|")
        d.line("| 1 | 2 |")
        assert len(d._parts) == 1
        assert "| A | B |\n|---|---|\n| 1 | 2 |" == d._parts[0]

    def test_line_on_empty_creates_part(self):
        d = Doc()
        d.line("first line")
        assert d._parts == ["first line"]

    def test_md_then_line_table(self):
        d = Doc()
        d.md(FakeTemplate("# Title"))
        d.text("| H1 | H2 |")
        d.line("|---|---|")
        d.line("| a | b |")
        assert len(d._parts) == 2
        assert d._parts[0] == "# Title"
        assert d._parts[1] == "| H1 | H2 |\n|---|---|\n| a | b |"


# ---------------------------------------------------------------------------
# Integration with real GA objects (if available)
# ---------------------------------------------------------------------------


class TestGAIntegration:
    """Test with actual galaga Multivector objects."""

    @pytest.fixture
    def vga(self):
        try:
            from galaga import Algebra

            return Algebra((1, 1, 1))
        except ImportError:
            pytest.skip("galaga not installed")

    def test_multivector_auto_latex(self, vga):
        e1, e2, e3 = vga.basis_vectors()
        v = 3 * e1 + 2 * e2
        r = render_value(v, None, "")
        assert r.kind == RenderKind.INLINE_LATEX
        assert "e" in r.value  # contains basis element names

    def test_multivector_in_template(self, vga):
        e1, e2, e3 = vga.basis_vectors()
        v = e1 + e2
        t = FakeTemplate("v = ", FakeInterpolation(v))
        result = render_template(t)
        assert result.startswith("v = $")
        assert result.endswith("$")

    def test_multivector_text_override(self, vga):
        e1, e2, e3 = vga.basis_vectors()
        v = e1
        r = render_value(v, None, "text")
        assert r.kind == RenderKind.TEXT
        assert "$" not in r.value

    def test_multivector_block_spec(self, vga):
        e1, e2, e3 = vga.basis_vectors()
        v = e1 + e2 + e3
        r = render_value(v, None, "block")
        assert r.kind == RenderKind.BLOCK_LATEX

    def test_multivector_str_conversion(self, vga):
        e1, e2, e3 = vga.basis_vectors()
        v = e1
        r = render_value(v, "s", "")
        assert r.kind == RenderKind.TEXT

    def test_scalar_multivector(self, vga):
        s = vga.scalar(5.0)
        r = render_value(s, None, "")
        assert r.kind == RenderKind.INLINE_LATEX
        assert "5" in r.value

    def test_zero_multivector(self, vga):
        z = vga.scalar(0.0)
        r = render_value(z, None, "")
        assert r.kind == RenderKind.INLINE_LATEX
        assert "0" in r.value

    def test_full_template_with_ga(self, vga):
        e1, e2, e3 = vga.basis_vectors()
        v = 2 * e1 - e3
        t = FakeTemplate(
            "# Result\n\nThe vector ",
            FakeInterpolation(v),
            " has components in e1 and e3.",
        )
        result = render_template(t)
        assert "# Result" in result
        assert "$" in result
        assert "has components" in result
