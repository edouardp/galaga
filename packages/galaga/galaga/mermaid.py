"""Generate Mermaid graph diagrams from lazy Multivector expression trees.

Walks the Expr tree and produces a Mermaid flowchart string showing every
node's rendered unicode expression and its evaluated numeric value.
"""

from __future__ import annotations

from galaga.expr import (
    Complement,
    Conjugate,
    Dual,
    Expr,
    Inverse,
    Involute,
    Reverse,
    Scalar,
    Sym,
    Uncomplement,
    Undual,
)
from galaga.render import render

# Unary postfix ops that decorate a single operand (R̃, B*, etc.)
_POSTFIX_OPS = (Reverse, Involute, Conjugate, Dual, Undual, Complement, Uncomplement, Inverse)


def _escape(s: str) -> str:
    return s.replace('"', "#quot;")


def _value_str(node: Expr) -> str:
    try:
        mv = node.eval()
        return str(mv.eval())
    except Exception:
        return "?"


def _inner_tree(node: Sym) -> Expr | None:
    """Get the inner expression tree of a named Sym, if any."""
    if node._inner_expr is not None:
        return node._inner_expr
    if node._mv._expr is not None:
        inner = node._mv._expr
        if isinstance(inner, Sym) and inner._name == node._name:
            return None
        return inner
    return None


def _is_named_sym(node: Expr) -> bool:
    return isinstance(node, Sym) and _inner_tree(node) is not None


def _collect_significant_children(node: Expr) -> list[Expr]:
    """Walk an expression tree, collecting the nearest Sym/Scalar descendants."""
    result: list[Expr] = []

    def walk(n: Expr):
        if isinstance(n, (Sym, Scalar)):
            result.append(n)
            return
        # Postfix op on a Sym is significant (e.g. Reverse(R) → R̃)
        if isinstance(n, _POSTFIX_OPS) and isinstance(n.x, Sym):
            result.append(n)
            return
        if hasattr(n, "a") and hasattr(n, "b"):
            walk(n.a)
            walk(n.b)
        elif hasattr(n, "x"):
            walk(n.x)

    if isinstance(node, Sym):
        inner = _inner_tree(node)
        if inner is not None:
            walk(inner) if not isinstance(inner, (Sym, Scalar)) else result.append(inner)
    elif hasattr(node, "a") and hasattr(node, "b"):
        walk(node.a)
        walk(node.b)
    elif hasattr(node, "x"):
        walk(node.x)
    return result


def expr_to_mermaid(expr: Expr, *, direction: str = "TD", show_values: bool = True, compact: bool = False) -> str:
    """Convert an Expr tree to a Mermaid flowchart string.

    Args:
        expr: Root expression node.
        direction: Mermaid graph direction (TD, LR, BT, RL).
        show_values: If True, include evaluated values on each node.
        compact: If True, collapse intermediate unnamed nodes so only
                 named variables and leaf basis blades appear.
    """
    lines: list[str] = [f"graph {direction}"]
    counter = [0]
    node_ids: dict[int, str] = {}
    edges: set[tuple[str, str]] = set()
    named_ids: list[str] = []
    blade_ids: list[str] = []
    scalar_ids: list[str] = []

    def make_label(node: Expr) -> str:
        label = _escape(render(node))
        if show_values:
            val = _escape(_value_str(node))
            if _is_named_sym(node):
                inner = _inner_tree(node)
                label = f"{node._name} = {_escape(render(inner))}"
            if label != val:
                label = f"{label}<br>{val}"
        return label

    def classify(node: Expr, node_id: str):
        if isinstance(node, Sym) and node._name is not None:
            if _is_named_sym(node):
                named_ids.append(node_id)
            elif node._grade == 0:
                scalar_ids.append(node_id)
            else:
                blade_ids.append(node_id)

    def make_node(node: Expr) -> str:
        # Named Syms sharing the same underlying MV collapse to one node
        if isinstance(node, Sym) and node._name is not None:
            nid = id(node._mv)
        else:
            nid = id(node)
        if nid in node_ids:
            return node_ids[nid]
        counter[0] += 1
        node_id = f"n{counter[0]}"
        node_ids[nid] = node_id
        lines.append(f'    {node_id}["{make_label(node)}"]')
        classify(node, node_id)
        return node_id

    def add_edge(from_id: str, to_id: str):
        if (from_id, to_id) not in edges:
            edges.add((from_id, to_id))
            lines.append(f"    {to_id} --> {from_id}")

    if compact:

        def visit_compact(node: Expr) -> str:
            node_id = make_node(node)
            for child in _collect_significant_children(node):
                child_id = visit_compact(child)
                add_edge(node_id, child_id)
            return node_id

        visit_compact(expr)
    else:

        def visit(node: Expr) -> str:
            node_id = make_node(node)
            if isinstance(node, Sym):
                inner = _inner_tree(node)
                if inner is not None:
                    add_edge(node_id, visit(inner))
            elif isinstance(node, Scalar):
                pass
            elif hasattr(node, "a") and hasattr(node, "b"):
                add_edge(node_id, visit(node.a))
                add_edge(node_id, visit(node.b))
            elif hasattr(node, "x"):
                add_edge(node_id, visit(node.x))
            return node_id

        visit(expr)

    for nid in named_ids:
        lines.append(f"    style {nid} fill:#e0f0ff,stroke:#4a90d9")
    for nid in blade_ids:
        lines.append(f"    style {nid} fill:#f0ffe0,stroke:#6a9a30")
    for nid in scalar_ids:
        lines.append(f"    style {nid} fill:#fff0e0,stroke:#d9a04a")
    return "\n".join(lines)


def mv_to_mermaid(mv, **kwargs) -> str:
    """Generate a Mermaid diagram from a lazy Multivector."""
    return expr_to_mermaid(mv._to_expr(), **kwargs)
