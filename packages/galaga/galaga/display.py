"""Public Galaga 2 display policy and rendering pipeline."""

from __future__ import annotations

from typing import Any

from .expression import Expr
from .presentation import Notation, PresentationConfig
from .rendering import ascii as ascii_emitter
from .rendering import latex as latex_emitter
from .rendering import unicode as unicode_emitter
from .rendering._build import content_tree, expression_tree
from .rendering.tree import Node

_CONTENTS = {"name", "expr", "value", "full"}
_TARGETS = {"ascii", "unicode", "latex"}


def build_tree(
    value: Any,
    format_spec: str = "",
    *,
    content: str | None = None,
    target: str | None = None,
    presentation: PresentationConfig | None = None,
    notation: Notation | None = None,
) -> tuple[Node, str]:
    """Resolve display policy and return a semantic tree plus output target."""
    spec_content, spec_target = _parse_format_spec(format_spec)
    if content is not None and spec_content is not None and content != spec_content:
        raise ValueError("content= conflicts with the format specification")
    if target is not None and spec_target is not None and target != spec_target:
        raise ValueError("target= conflicts with the format specification")
    selected_content = content or spec_content
    selected_target = target or spec_target

    if isinstance(value, Expr):
        if presentation is None:
            raise TypeError("rendering an Expr directly requires presentation=")
        selected_presentation = _presentation(presentation)
        if notation is not None:
            selected_presentation = selected_presentation.with_notation(_notation(notation))
        selected_target = selected_target or selected_presentation.display.target
        if selected_content not in {None, "expr"}:
            raise ValueError("a standalone Expr can only render expression content")
        return expression_tree(value, selected_presentation, target=selected_target), selected_target

    algebra = getattr(value, "algebra", None)
    resolve = getattr(algebra, "resolve_presentation", None)
    if resolve is None or not callable(resolve):
        raise TypeError("render expects a facade Multivector or an Expr with presentation=")
    selected_presentation = _presentation(resolve(presentation))
    if notation is not None:
        selected_presentation = selected_presentation.with_notation(_notation(notation))
    selected_target = selected_target or selected_presentation.display.target
    selected_content = selected_content or selected_presentation.display.content
    if selected_content == "auto":
        selected_content = _automatic_content(value)
    if selected_content not in _CONTENTS:
        raise ValueError("render content must be 'name', 'expr', 'value', or 'full'")
    if selected_target not in _TARGETS:
        raise ValueError("render target must be 'ascii', 'unicode', or 'latex'")
    return (
        content_tree(
            value,
            content=selected_content,
            presentation=selected_presentation,
            target=selected_target,
        ),
        selected_target,
    )


def render(
    value: Any,
    format_spec: str = "",
    *,
    content: str | None = None,
    target: str | None = None,
    presentation: PresentationConfig | None = None,
    notation: Notation | None = None,
) -> str:
    """Render a facade value or standalone expression through the shared tree."""
    tree, selected_target = build_tree(
        value,
        format_spec,
        content=content,
        target=target,
        presentation=presentation,
        notation=notation,
    )
    return emit(tree, selected_target)


def emit(tree: Node, target: str) -> str:
    """Emit an already-built semantic tree for one target."""
    if target == "ascii":
        return ascii_emitter.emit(tree)
    if target == "unicode":
        return unicode_emitter.emit(tree)
    if target == "latex":
        return latex_emitter.emit(tree)
    raise ValueError("render target must be 'ascii', 'unicode', or 'latex'")


def _parse_format_spec(spec: str) -> tuple[str | None, str | None]:
    if not isinstance(spec, str):
        raise TypeError("format specification must be a string")
    if spec in {"", "s"}:
        return None, None
    aliases = {"a": "ascii", "u": "unicode"}
    spec = aliases.get(spec, spec)
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


def _automatic_content(value: Any) -> str:
    # Names opt into an explanatory equality.  Expression tracking on its own
    # remains provenance rather than a request to replace the concrete value.
    return "full" if getattr(value, "name", None) is not None else "value"


def _presentation(value: Any) -> PresentationConfig:
    if not isinstance(value, PresentationConfig):
        raise TypeError("presentation must be a PresentationConfig")
    return value


def _notation(value: Any) -> Notation:
    if not isinstance(value, Notation):
        raise TypeError("notation must be a Notation")
    return value


__all__ = ["build_tree", "emit", "render"]
