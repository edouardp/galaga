"""Rendering-only annotated views.

An annotated view binds immutable rules to an eager value or presented view.
It has no arithmetic: use ``.value`` for further calculations. Plain-text
targets render undecorated; only the LaTeX target is annotated.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any

from galaga import Multivector, PresentedMultivector
from galaga.rendering import RenderDocument, content_document

from .katex import KatexResult, render_katex
from .model import Annotation

__all__ = ["Annotated"]

_CONTENTS = {"name", "expr", "value", "full"}
_TARGETS = {"ascii", "unicode", "latex"}
_ALIASES = {"a": "ascii", "u": "unicode"}


def _parse_format_spec(spec: str) -> tuple[str | None, str | None]:
    if not isinstance(spec, str):
        raise TypeError("format specification must be a string")
    if spec in {"", "s"}:
        return None, None
    spec = _ALIASES.get(spec, spec)
    if "/" not in spec:
        if spec in _CONTENTS:
            return spec, None
        if spec in _TARGETS:
            return None, spec
        raise ValueError("format specification must be a content, a target, or '<content>/<target>'")
    if spec.count("/") != 1:
        raise ValueError("compound format specification must contain exactly one slash")
    content, target = spec.split("/")
    if content not in _CONTENTS or target not in _TARGETS:
        raise ValueError("compound format specification must be '<name|expr|value|full>/<ascii|unicode|latex>'")
    return content, target


@dataclass(frozen=True, slots=True)
class Annotated:
    """A value plus immutable annotation rules, with no arithmetic behavior."""

    value: Multivector | PresentedMultivector
    rules: tuple[Annotation, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.value, (Multivector, PresentedMultivector)):
            raise TypeError("Annotated expects a Galaga Multivector or PresentedMultivector")
        rules = tuple(self.rules)
        if any(not isinstance(rule, Annotation) for rule in rules):
            raise TypeError("Annotated rules must be Annotation instances")
        object.__setattr__(self, "rules", rules)

    @property
    def plain(self) -> Multivector:
        """The original multivector, without presentation or annotation state."""
        return self.value.value if isinstance(self.value, PresentedMultivector) else self.value

    def document(
        self,
        *,
        content: str | None = None,
        presentation: Any = None,
        notation: Any = None,
        target: str = "latex",
    ) -> RenderDocument:
        """Build the semantic document that the rules resolve against."""
        if isinstance(self.value, PresentedMultivector):
            return self.value.render_document(
                content=content, target=target, presentation=presentation, notation=notation
            )
        return content_document(
            self.value, content=content, presentation=presentation, notation=notation, target=target
        )

    def katex(
        self,
        *,
        content: str | None = None,
        presentation: Any = None,
        notation: Any = None,
    ) -> KatexResult:
        """Render annotated LaTeX plus the solved label layout."""
        document = self.document(content=content, presentation=presentation, notation=notation, target="latex")
        return render_katex(document, self.rules, value=self.plain)

    def latex(
        self,
        *,
        content: str | None = None,
        presentation: Any = None,
        notation: Any = None,
    ) -> str:
        """Raw annotated LaTeX; suitable for direct Markdown interpolation."""
        return self.katex(content=content, presentation=presentation, notation=notation).text

    def unicode(self, *, content: str | None = None) -> str:
        return self.value.display(content=content, target="unicode")

    def ascii(self, *, content: str | None = None) -> str:
        return self.value.display(content=content, target="ascii")

    def display(
        self,
        format_spec: str = "",
        *,
        content: str | None = None,
        target: str | None = None,
        presentation: Any = None,
        notation: Any = None,
    ) -> str:
        spec_content, spec_target = _parse_format_spec(format_spec)
        if content is not None and spec_content is not None and content != spec_content:
            raise ValueError("content= conflicts with the format specification")
        if target is not None and spec_target is not None and target != spec_target:
            raise ValueError("target= conflicts with the format specification")
        selected_content = content or spec_content
        selected_target = target or spec_target
        if selected_target == "latex":
            return self.latex(content=selected_content, presentation=presentation, notation=notation)
        return self.value.display(
            content=selected_content,
            target=selected_target,
            presentation=presentation,
            notation=notation,
        )

    def __galaga_present__(self, presenter: Any) -> Annotated:
        """Adapter used by ``galaga.Presenter``; preserves the captured rules."""
        return Annotated(presenter(self.value), self.rules)

    def _repr_latex_(self) -> str:
        return f"${self.latex()}$"

    def _repr_html_(self) -> str | None:
        """Marimo inline math markup for direct rich display.

        Fill and overlay lowering re-enter math with delimiters that Marimo's
        Markdown preprocessor would split when `_repr_latex_` is routed
        through `mo.md`. Rich display hands the raw math to the frontend
        instead, keeping the default inline presentation. Other environments
        fall back to `_repr_latex_`.
        """
        try:
            import marimo  # noqa: F401
        except ImportError:
            return None
        latex = escape(self.latex(), quote=True)
        return f'<marimo-tex class="arithmatex">||({latex}||)</marimo-tex>'

    def __str__(self) -> str:
        return self.unicode()

    def __repr__(self) -> str:
        return self.ascii()

    def __format__(self, format_spec: str) -> str:
        return self.display(format_spec)
