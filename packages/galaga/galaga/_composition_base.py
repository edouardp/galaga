"""Leaf-level operator hook shared by presentation components."""

from __future__ import annotations

from typing import Any


class PresentationComposable:
    """Dispatch ``|`` to the composition policy without importing it at startup."""

    def __or__(self, other: object) -> Any:
        from .composition import compose

        return compose(self, other)

    def __ror__(self, other: object) -> Any:
        from .composition import compose

        return compose(other, self)
