"""Generate Mermaid graph diagrams from lazy Multivector expression trees.

Walks the Expr tree and produces a Mermaid flowchart string showing every
node, its operation type, and the evaluated numeric value at each level.
"""

from __future__ import annotations

from galaga.expr import Expr, Grade, Scalar, ScalarDiv, ScalarMul, Sym


def _node_label(node: Expr) -> str:
    """Human-readable label for a single node (no children)."""
    t = type(node).__name__
    if isinstance(node, Sym):
        return f"{t}: {node._name_ascii}"
    if isinstance(node, Scalar):
        return f"{t}: {node._value:g}"
    if isinstance(node, ScalarMul):
        return f"{t}: k={node.k:g}"
    if isinstance(node, ScalarDiv):
        return f"{t}: k={node.k:g}"
    if isinstance(node, Grade):
        return f"{t}: k={node.k}"
    return t


def _value_str(node: Expr) -> str:
    """Compact string of the evaluated value."""
    try:
        mv = node.eval()
        return str(mv)
    except Exception:
        return "?"


def expr_to_mermaid(expr: Expr, *, direction: str = "TD", show_values: bool = True) -> str:
    """Convert an Expr tree to a Mermaid flowchart string.

    Args:
        expr: Root expression node.
        direction: Mermaid graph direction (TD, LR, BT, RL).
        show_values: If True, include evaluated values on each node.

    Returns:
        A complete Mermaid graph definition string.
    """
    lines: list[str] = [f"graph {direction}"]
    counter = [0]
    node_ids: dict[int, str] = {}

    def visit(node: Expr) -> str:
        nid = id(node)
        if nid in node_ids:
            return node_ids[nid]

        counter[0] += 1
        node_id = f"n{counter[0]}"
        node_ids[nid] = node_id

        label = _node_label(node)
        if show_values:
            val = _value_str(node)
            # Escape quotes for mermaid
            val = val.replace('"', "#quot;")
            label = f"{label}\\n= {val}"
        label = label.replace('"', "#quot;")
        lines.append(f'    {node_id}["{label}"]')

        # Recurse into children
        if isinstance(node, (Sym, Scalar)):
            pass  # leaves
        elif hasattr(node, "a") and hasattr(node, "b"):
            a_id = visit(node.a)
            b_id = visit(node.b)
            lines.append(f"    {node_id} --> {a_id}")
            lines.append(f"    {node_id} --> {b_id}")
        elif hasattr(node, "x"):
            x_id = visit(node.x)
            lines.append(f"    {node_id} --> {x_id}")

        return node_id

    visit(expr)
    return "\n".join(lines)


def mv_to_mermaid(mv, **kwargs) -> str:
    """Generate a Mermaid diagram from a lazy Multivector.

    Args:
        mv: A Multivector (lazy with expression tree).
        **kwargs: Passed to expr_to_mermaid.

    Returns:
        Mermaid graph string.
    """
    expr = mv._to_expr()
    return expr_to_mermaid(expr, **kwargs)
