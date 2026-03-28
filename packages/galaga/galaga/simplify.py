"""Algebraic simplification of symbolic expression trees.

Rewrites Expr trees using algebraic identities — double involution,
identity elimination, self-cancellation, scalar collapse, term collection,
grade-aware projection, etc. This is distinct from the LaTeX render tree
rewrites (latex_rewrite.py), which are purely cosmetic.

The simplifier runs fixed-point iteration: apply rules bottom-up until
the tree stops changing, capped at 100 iterations.
"""

from __future__ import annotations

import galaga.algebra as _alg
from galaga.expr import (
    Add,
    Anticommutator,
    Commutator,
    Conjugate,
    Div,
    Dli,
    Dual,
    Even,
    Exp,
    Expr,
    Gp,
    Grade,
    Hi,
    Inverse,
    Involute,
    JordanProduct,
    Lc,
    LieBracket,
    Neg,
    Norm,
    Odd,
    Op,
    Rc,
    Reverse,
    Scalar,
    ScalarDiv,
    ScalarMul,
    Sp,
    Squared,
    Sub,
    Sym,
    Undual,
    Unit,
    _ensure_expr,
)


def _eq(a: Expr, b: Expr) -> bool:
    """Structural equality for expression nodes (used by simplify).

    This is NOT numeric equality — it checks whether two expression trees
    have the same structure and leaf values. For example, ``Sym("v")`` equals
    ``Sym("v")`` but not ``Sym("w")``, even if they wrap the same multivector.

    Why structural and not numeric? Because simplification rules are algebraic
    identities (``x - x → 0``, ``~~x → x``) that should work regardless of
    the concrete values. Numeric comparison would require evaluation, which
    defeats the purpose of symbolic manipulation.
    """
    if type(a) is not type(b):
        return False
    if isinstance(a, Sym):
        return a._name == b._name
    if isinstance(a, Scalar):
        return a._value == b._value
    if isinstance(a, ScalarMul):
        return a.k == b.k and _eq(a.x, b.x)
    if isinstance(a, ScalarDiv):
        return a.k == b.k and _eq(a.x, b.x)
    if isinstance(a, Neg):
        return _eq(a.x, b.x)
    if isinstance(a, (Reverse, Involute, Conjugate, Dual, Undual, Norm, Unit, Inverse, Squared, Even, Odd, Exp)):
        return _eq(a.x, b.x)
    if isinstance(
        a, (Gp, Op, Lc, Rc, Hi, Dli, Sp, Commutator, Anticommutator, LieBracket, JordanProduct, Add, Sub, Div)
    ):
        return _eq(a.a, b.a) and _eq(a.b, b.b)
    if isinstance(a, Grade):
        return _eq(a.x, b.x) and a.k == b.k
    return False


def simplify(expr) -> Expr:
    """Apply algebraic rewrite rules to simplify an expression tree.

    Accepts an ``Expr`` or a lazy ``Multivector`` (extracts its expression tree).

    Runs ``_simplify()`` repeatedly until the tree stops changing (fixed-point
    iteration). This handles cascading rules like ``a - (-a) → a + a → 2a``.

    Current rewrite rules include:
    - Double involution: ``~~x → x``, ``involute(involute(x)) → x``, etc.
    - Identity elimination: ``1 * x → x``, ``x + 0 → x``
    - Self-cancellation: ``x - x → 0``, ``x ^ x → 0``
    - Scalar collapse: ``k * (j * x) → (k*j) * x``
    - Collection: ``x + x → 2x``
    - Rotor normalisation: ``R * ~R → 1`` (evaluated numerically)
    - Norm of unit: ``‖unit(x)‖ → 1``
    - Grade-aware projection: ``grade(v, 1) → v`` if v is known grade-1,
      ``grade(v, 2) → 0`` if v has no grade-2 component
    - Even/odd projection with known grades
    """
    if isinstance(expr, _alg.Multivector):
        expr = _ensure_expr(expr)
    elif not isinstance(expr, Expr):
        expr = _ensure_expr(expr)
    prev = None
    e = expr
    for _ in range(100):
        if prev is not None and _eq(prev, e):
            break
        prev = e
        e = _simplify(e)
    return e


def _is_scalar(e: Expr, val: float) -> bool:
    return isinstance(e, Scalar) and e._value == val


def _known_grade(e: Expr) -> int | None:
    """Return the known homogeneous grade of an expression, or None if mixed/unknown.

    This propagates grade information through the tree without evaluation:
    - ``Sym`` nodes carry auto-detected grade from construction
    - ``Scalar`` is always grade 0
    - ``Grade(x, k)`` is grade k by definition
    - ``Reverse``, ``Involute``, ``Conjugate`` preserve grade
    - ``Neg`` and ``ScalarMul`` preserve grade
    - ``Unit`` preserves grade (normalising doesn't change grade)

    Returns None for binary operations (products, sums) since the result
    grade depends on the operands in ways we can't determine statically.
    """
    if isinstance(e, Sym):
        return e._grade
    if isinstance(e, Scalar):
        return 0
    if isinstance(e, Grade):
        return e.k if isinstance(e.k, int) else None
    if isinstance(e, (Reverse, Involute, Conjugate)):
        return _known_grade(e.x)
    if isinstance(e, Neg):
        return _known_grade(e.x)
    if isinstance(e, ScalarMul):
        return _known_grade(e.x)
    if isinstance(e, ScalarDiv):
        return _known_grade(e.x)
    if isinstance(e, Unit):
        return _known_grade(e.x)
    return None


def _simplify(e: Expr) -> Expr:
    """Single-pass rewrite of an expression tree (called repeatedly by simplify)."""
    # --- Phase 1: recurse into children first (bottom-up rewriting) ---
    if isinstance(
        e, (Gp, Op, Lc, Rc, Hi, Dli, Sp, Commutator, Anticommutator, LieBracket, JordanProduct, Add, Sub, Div)
    ):
        e = type(e)(_simplify(e.a), _simplify(e.b))
    elif isinstance(e, ScalarMul):
        e = ScalarMul(e.k, _simplify(e.x))
    elif isinstance(e, ScalarDiv):
        e = ScalarDiv(_simplify(e.x), e.k)
    elif isinstance(e, (Reverse, Involute, Conjugate, Dual, Undual, Norm, Unit, Inverse, Squared, Even, Odd, Exp)):
        e = type(e)(_simplify(e.x))
    elif isinstance(e, Neg):
        e = Neg(_simplify(e.x))
    elif isinstance(e, Grade):
        e = Grade(_simplify(e.x), e.k)

    # --- Phase 2: apply rewrite rules to the current node ---

    # Double involution cancellations
    if isinstance(e, Reverse) and isinstance(e.x, Reverse):
        return e.x.x
    if isinstance(e, Involute) and isinstance(e.x, Involute):
        return e.x.x
    if isinstance(e, Conjugate) and isinstance(e.x, Conjugate):
        return e.x.x
    if isinstance(e, Inverse) and isinstance(e.x, Inverse):
        return e.x.x
    if isinstance(e, Neg) and isinstance(e.x, Neg):
        return e.x.x

    # Geometric product identities
    if isinstance(e, Gp):
        if _is_scalar(e.a, 1):
            return e.b
        if _is_scalar(e.b, 1):
            return e.a
        if _is_scalar(e.a, 0) or _is_scalar(e.b, 0):
            return Scalar(0)
        # Rotor normalisation: x * ~x → evaluate numerically
        if isinstance(e.b, Reverse) and _eq(e.a, e.b.x):
            try:
                val = e.eval()
                return Sym(val, str(val))
            except Exception:  # nosec B110 — intentional fallback when eval fails
                pass

    # Scalar multiplication identities
    if isinstance(e, ScalarMul):
        if e.k == 0:
            return Scalar(0)
        if e.k == 1:
            return e.x
        if isinstance(e.x, ScalarMul):
            return ScalarMul(e.k * e.x.k, e.x.x)

    # Addition identities
    if isinstance(e, Add):
        if _is_scalar(e.a, 0):
            return e.b
        if _is_scalar(e.b, 0):
            return e.a
        if _eq(e.a, e.b):
            return ScalarMul(2, e.a)

    # Subtraction identities
    if isinstance(e, Sub):
        if _eq(e.a, e.b):
            return Scalar(0)
        if isinstance(e.b, Neg):
            return Add(e.a, e.b.x)

    # Additive cancellation: x + (-x) → 0
    if isinstance(e, Add) and isinstance(e.b, Neg) and _eq(e.a, e.b.x):
        return Scalar(0)

    # Wedge self-annihilation: x ∧ x → 0
    if isinstance(e, Op) and _eq(e.a, e.b):
        return Scalar(0)

    # Norm of unit is 1
    if isinstance(e, Norm) and isinstance(e.x, Unit):
        return Scalar(1)

    # --- Grade-aware rules ---
    if isinstance(e, Grade) and isinstance(e.k, int):
        g = _known_grade(e.x)
        if g is not None:
            if g == e.k:
                return e.x
            else:
                return Scalar(0)

    if isinstance(e, Grade) and isinstance(e.x, Grade) and e.k == e.x.k:
        return e.x

    if isinstance(e, Even):
        g = _known_grade(e.x)
        if g is not None:
            return e.x if g % 2 == 0 else Scalar(0)

    if isinstance(e, Odd):
        g = _known_grade(e.x)
        if g is not None:
            return e.x if g % 2 == 1 else Scalar(0)

    # Jordan product of two vectors → inner product
    if isinstance(e, JordanProduct):
        ga = _known_grade(e.a)
        gb = _known_grade(e.b)
        if ga == 1 and gb == 1:
            return Hi(e.a, e.b)

    return e
