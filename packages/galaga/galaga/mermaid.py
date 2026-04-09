"""Generate Mermaid graph diagrams from lazy Multivector expression trees.

Walks the Expr tree and produces a Mermaid flowchart string showing every
node's rendered unicode expression and its evaluated numeric value.
"""

from __future__ import annotations

from galaga.expr import Expr, Scalar, Sym
from galaga.render import render


def _escape(s: str) -> str:
    return s.replace('"', "#quot;")


def _render_node(node: Expr) -> str:
    """Render the node as unicode text."""
    return render(node)


def _value_str(node: Expr) -> str:
    try:
        mv = node.eval()
        return str(mv.eval())  # .eval() strips name → shows numeric coefficients
    except Exception:
        return "?"


def expr_to_mermaid(expr: Expr, *, direction: str = "TD", show_values: bool = True) -> str:
    """Convert an Expr tree to a Mermaid flowchart string.

    Each node shows its rendered unicode expression and optionally
    the evaluated numeric value on a second line.
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

        label = _escape(_render_node(node))
        if show_values:
            val = _escape(_value_str(node))
            label = f"{label}<br>{val}"
        lines.append(f'    {node_id}["{label}"]')

        if isinstance(node, (Sym, Scalar)):
            pass
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
    """Generate a Mermaid diagram from a lazy Multivector."""
    expr = mv._to_expr()
    return expr_to_mermaid(expr, **kwargs)
