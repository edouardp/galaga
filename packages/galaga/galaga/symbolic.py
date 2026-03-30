"""Backward-compatibility shim — re-exports from galaga.expr and galaga.simplify.

All symbols that were previously in galaga.symbolic now live in:
- galaga.expr: Expr nodes, sym(), _is_symbolic(), _coerce, _ensure_expr
- galaga.simplify: simplify(), _eq, _known_grade
"""

from galaga.expr import *  # noqa: F401, F403
from galaga.expr import _coerce, _ensure_expr, _is_symbolic, sym  # noqa: F401
from galaga.simplify import _eq, _known_grade, simplify  # noqa: F401
