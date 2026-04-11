"""Backward-compatibility shim — use galaga.symbolic instead."""

from .symbolic import symbolic_binary as lazy_binary
from .symbolic import symbolic_unary as lazy_unary

__all__ = ["lazy_unary", "lazy_binary"]
