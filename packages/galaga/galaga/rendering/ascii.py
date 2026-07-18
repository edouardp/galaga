"""Plain-ASCII semantic-tree emitter."""

from ._emit import emit as _emit
from .tree import Node


def emit(node: Node) -> str:
    """Serialize ``node`` as portable plain text."""
    return _emit(node, "ascii")


__all__ = ["emit"]
