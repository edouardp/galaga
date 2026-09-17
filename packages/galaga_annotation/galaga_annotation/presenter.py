"""Presenter adapters that preserve annotation rules (SPEC-015)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from galaga import Presenter

from .view import Annotated

__all__ = ["AnnotationPresenter"]


@dataclass(frozen=True, slots=True)
class AnnotationPresenter:
    """Apply a Galaga presenter to an annotated view without dropping rules.

    Ordinary ``galaga.Presenter`` instances also compose with annotated views
    through the ``__galaga_present__`` adapter protocol.
    """

    base: Presenter

    def __post_init__(self) -> None:
        if not isinstance(self.base, Presenter):
            raise TypeError("AnnotationPresenter base must be a galaga Presenter")

    def __call__(self, value: Any) -> Any:
        if isinstance(value, Annotated):
            return Annotated(self.base(value.value), value.rules)
        return self.base(value)
