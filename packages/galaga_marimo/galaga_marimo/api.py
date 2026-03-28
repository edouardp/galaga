"""Public API for galaga_marimo.

Provides md(), inline(), block(), and explicit wrappers.
"""

from __future__ import annotations

from string.templatelib import Template
from typing import Any

from galaga_marimo.renderer import _get_latex, _has_latex, render_template


def md(template: Template) -> Any:
    """Render a t-string template as marimo markdown.

    GA objects with a .latex() method are automatically rendered as
    inline LaTeX. Use format specs to override:

        gm.md(t"Vector: {v}")           # auto inline LaTeX
        gm.md(t"Equation: {expr:block}")  # display block LaTeX
        gm.md(t"Debug: {mv!r}")          # repr as text
        gm.md(t"Value: {x:.3f}")         # numeric formatting

    Returns a marimo Html object if marimo is available, otherwise
    returns the rendered markdown string.
    """
    markdown = render_template(template)
    import textwrap

    markdown = textwrap.dedent(markdown).strip()
    try:
        import marimo as mo

        return mo.md(markdown)
    except ImportError:
        return markdown


def inline(template: Template) -> Any:
    """Render a t-string as a single inline LaTeX expression.

    All interpolations with .latex() are joined; the whole result
    is wrapped in $...$.

        gm.inline(t"R = {R}")  →  $R = e_{12}$
    """
    parts: list[str] = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
        else:
            from string.templatelib import Interpolation

            if isinstance(item, Interpolation) and _has_latex(item.value):
                parts.append(_get_latex(item.value))
            elif isinstance(item, Interpolation):
                parts.append(str(item.value))
    raw = "".join(parts)
    markdown = f"${raw}$"
    try:
        import marimo as mo

        return mo.md(markdown)
    except ImportError:
        return markdown


def block(template: Template) -> Any:
    """Render a t-string as a display-mode LaTeX block.

    All interpolations with .latex() are joined; the whole result
    is wrapped in $$...$$.

        gm.block(t"{expr}")  →  $$e_{12} + e_{13}$$
    """
    parts: list[str] = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
        else:
            from string.templatelib import Interpolation

            if isinstance(item, Interpolation) and _has_latex(item.value):
                parts.append(_get_latex(item.value))
            elif isinstance(item, Interpolation):
                parts.append(str(item.value))
    raw = "".join(parts)
    markdown = f"$${raw}$$"
    try:
        import marimo as mo

        return mo.md(markdown)
    except ImportError:
        return markdown


class _LatexWrapper:
    """Wraps a value to force inline LaTeX rendering."""

    def __init__(self, obj: Any):
        self._obj = obj

    def latex(self) -> str:
        if _has_latex(self._obj):
            return _get_latex(self._obj)
        return str(self._obj)


class _BlockLatexWrapper:
    """Wraps a value to force block LaTeX rendering."""

    def __init__(self, obj: Any):
        self._obj = obj

    def latex(self) -> str:
        if _has_latex(self._obj):
            return _get_latex(self._obj)
        return str(self._obj)

    # Sentinel so renderer picks block mode
    _galaga_block = True


class _TextWrapper:
    """Wraps a value to force plain text rendering (no LaTeX)."""

    def __init__(self, obj: Any):
        self._obj = obj

    def __str__(self) -> str:
        return str(self._obj)


def latex(obj: Any) -> _LatexWrapper:
    """Force an object to render as inline LaTeX in md().

    gm.md(t"Result: {gm.latex(value)}")
    """
    return _LatexWrapper(obj)


def block_latex(obj: Any) -> _BlockLatexWrapper:
    """Force an object to render as block LaTeX in md().

    gm.md(t"Equation: {gm.block_latex(expr)}")
    """
    return _BlockLatexWrapper(obj)


def text(obj: Any) -> _TextWrapper:
    """Force an object to render as plain text in md().

    gm.md(t"Debug: {gm.text(mv)}")
    """
    return _TextWrapper(obj)


def _to_marimo(markdown: str) -> Any:
    """Pass markdown to mo.md() if marimo is available, else return string."""
    try:
        import marimo as mo

        return mo.md(markdown)
    except ImportError:
        return markdown


class Doc:
    """Builder for assembling markdown from multiple t-strings.

    Use when you need loops, conditionals, or programmatic content::

        with gm.doc() as d:
            d.md(t"# Results")
            for name, e in exprs:
                d.md(t"**{name}:** {e} = {e.eval()}")

    The context manager returns a marimo Html object on exit.
    You can also call d.render() explicitly.
    """

    def __init__(self):
        self._parts: list[str] = []
        self._result = None

    def md(self, template: Template) -> None:
        """Append a rendered t-string as a markdown paragraph."""
        import textwrap

        rendered = render_template(template)
        self._parts.append(textwrap.dedent(rendered).strip())

    def inline(self, template: Template) -> None:
        """Append a t-string rendered as inline LaTeX ($...$)."""
        parts: list[str] = []
        for item in template:
            if isinstance(item, str):
                parts.append(item)
            else:
                from string.templatelib import Interpolation

                if isinstance(item, Interpolation) and _has_latex(item.value):
                    parts.append(_get_latex(item.value))
                elif isinstance(item, Interpolation):
                    parts.append(str(item.value))
        self._parts.append(f"${''.join(parts)}$")

    def block(self, template: Template) -> None:
        """Append a t-string rendered as block LaTeX ($$...$$)."""
        parts: list[str] = []
        for item in template:
            if isinstance(item, str):
                parts.append(item)
            else:
                from string.templatelib import Interpolation

                if isinstance(item, Interpolation) and _has_latex(item.value):
                    parts.append(_get_latex(item.value))
                elif isinstance(item, Interpolation):
                    parts.append(str(item.value))
        self._parts.append(f"$${''.join(parts)}$$")

    def text(self, s: str) -> None:
        """Append raw markdown text as a new paragraph (double newline separated)."""
        self._parts.append(s)

    def line(self, s: str) -> None:
        """Append a raw line that continues the previous block (single newline).

        Use for table rows, list items, or any content that must be on
        consecutive lines without a paragraph break.
        """
        if self._parts:
            self._parts[-1] += "\n" + s
        else:
            self._parts.append(s)

    def render(self) -> Any:
        """Join all parts and return as marimo Html or string."""
        markdown = "\n\n".join(self._parts)
        self._result = _to_marimo(markdown)
        return self._result

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self._result is None:
            self.render()
        return False


def doc() -> Doc:
    """Create a markdown builder for loop/conditional content.

    Usage::

        with gm.doc() as d:
            d.md(t"# Title")
            for name, expr in items:
                d.md(t"**{name}:** {expr} = {expr.eval()}")

    Returns a marimo Html object when the context manager exits.
    """
    return Doc()
