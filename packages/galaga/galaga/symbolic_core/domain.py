"""Lightweight symbolic domain registry.

The first MatrixRepr implementation uses explicit matrix node classes, but this
registry gives future domains a shared place to map operator keys to expression
node classes without coupling those domains to GA's ``ga_op`` registry.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class SymbolicDomain:
    """Operator and evaluator registry for one symbolic domain."""

    name: str
    operators: dict[str, type] = field(default_factory=dict)
    evaluators: dict[type, Callable] = field(default_factory=dict)

    def register_operator(self, op_key: str, node_type: type) -> None:
        self.operators[op_key] = node_type

    def register_evaluator(self, node_type: type, evaluator: Callable) -> None:
        self.evaluators[node_type] = evaluator

    def build_operator(self, op_key: str, *exprs):
        try:
            node_type = self.operators[op_key]
        except KeyError as exc:
            raise TypeError(f"Domain {self.name!r} has no symbolic operator {op_key!r}") from exc
        return node_type(*exprs)

    def evaluate(self, node):
        evaluator = self.evaluators.get(type(node))
        if evaluator is not None:
            return evaluator(node)
        return node.eval()
