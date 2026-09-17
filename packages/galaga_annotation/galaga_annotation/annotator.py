"""Immutable callable annotation recipes (ADR-142).

``annotator(*rules)`` builds a reusable recipe. Calling it binds a value and
returns a rendering-only :class:`~galaga_annotation.view.Annotated` view.
Functional ``on(...)`` rules and the fluent ``.highlight``/``.label``/``.mark``
builders produce the same ordered plan and never mutate prior recipes.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from .model import Annotation, on
from .targets import WholeExpression

__all__ = ["Annotator", "annotate", "annotator"]


@dataclass(frozen=True, slots=True)
class Annotator:
    """An immutable ordered tuple of annotation rules."""

    rules: tuple[Annotation, ...] = ()

    def __post_init__(self) -> None:
        rules = tuple(self.rules)
        if any(not isinstance(rule, Annotation) for rule in rules):
            raise TypeError("annotator rules must be Annotation instances")
        object.__setattr__(self, "rules", rules)

    def __call__(self, value: Any):
        from .view import Annotated

        return Annotated(value, self.rules)

    def __len__(self) -> int:
        return len(self.rules)

    def _with(self, rule: Annotation) -> Annotator:
        return replace(self, rules=(*self.rules, rule))

    def highlight(self, target: Any | None = None, **fields: Any) -> Annotator:
        """Append a text/fill/border annotation without a label."""
        if "label" in fields:
            raise TypeError("highlight does not accept a label; use label or mark")
        return self._with(on(target, **fields))

    def label(self, text: str, *, target: Any | None = None, **fields: Any) -> Annotator:
        """Append a label and optional marker for one target."""
        if not isinstance(text, str):
            raise TypeError("annotation label text must be a string")
        if "label" in fields:
            raise TypeError("label text is positional; do not pass label=")
        return self._with(on(target, label=text, **fields))

    def mark(self, target: Any | None = None, *, label: str | None = None, **fields: Any) -> Annotator:
        """Append a combined highlight and label rule."""
        if "label" in fields:
            raise TypeError("label text is positional; do not pass label=")
        return self._with(on(target, label=label, **fields))

    def add(self, *rules: Annotation) -> Annotator:
        """Append several rules and return a new recipe."""
        recipe = self
        for rule in rules:
            if not isinstance(rule, Annotation):
                raise TypeError("annotator rules must be Annotation instances")
            recipe = recipe._with(rule)
        return recipe


def annotator(*rules: Annotation) -> Annotator:
    """Construct an immutable, callable annotation recipe."""
    return Annotator(tuple(rules))


def annotate(value: Any, *rules: Annotation, **fields: Any):
    """One-off spelling of ``annotator(*rules)(value)``.

    Keyword fields construct one additional whole-expression/value rule.
    """

    recipe = annotator(*rules)
    if fields:
        recipe = recipe._with(on(WholeExpression(), **fields))
    return recipe(value)
