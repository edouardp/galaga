"""LaTeX semantic-tree emitter."""

from ._emit import emit as _emit
from .tree import Node


def emit(node: Node) -> str:
    """Serialize ``node`` as KaTeX-compatible LaTeX."""
    return _emit(node, "latex")


__all__ = ["emit"]
