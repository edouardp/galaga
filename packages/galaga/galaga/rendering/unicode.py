"""Unicode semantic-tree emitter."""

from ._emit import emit as _emit
from .tree import Node


def emit(node: Node) -> str:
    """Serialize ``node`` as Unicode mathematical text."""
    return _emit(node, "unicode")


__all__ = ["emit"]
