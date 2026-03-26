"""Symbolic expression tree for pretty-printing and algebraic manipulation.

This module provides a lazy expression tree that sits on top of the numeric
core in ``ga.algebra``. It serves two purposes:

1. **Pretty-printing.** Instead of computing ``R * v * ~R`` immediately and
   showing the numeric result, you can wrap the operands as symbols
   (``sym(R, "R")``) and get ``RvR̃`` as output — in Unicode, LaTeX, or
   Jupyter's ``_repr_latex_``.

2. **Algebraic simplification.** The ``simplify()`` function applies rewrite
   rules (double-reverse cancellation, rotor normalisation, grade-aware
   projection, etc.) to expression trees, running to a fixed point.

Architecture
------------
Every GA operation has a corresponding ``Expr`` subclass (``Gp``, ``Op``,
``Grade``, ``Reverse``, etc.) that stores its operands as child nodes.
The tree is built lazily via operator overloads on ``Expr``:

    R * v * ~R  →  Gp(Gp(Sym("R"), Sym("v")), Reverse(Sym("R")))

Each node implements:
- ``eval()``    → recursively evaluates to a concrete ``Multivector``
- ``__str__()`` → Unicode rendering (``RvR̃``)
- ``_latex()``  → LaTeX rendering (``R v \\tilde{R}``)

Drop-in API
-----------
The module re-exports every function from ``ga.algebra`` (``gp``, ``grade``,
``reverse``, etc.) as a wrapper that detects ``Expr`` arguments:

- If any argument is an ``Expr``, it builds a tree node.
- If all arguments are plain ``Multivector``s, it delegates directly to the
  numeric implementation with zero overhead.

This means users can ``from ga.symbolic import gp, grade, reverse`` and use
the same function names for both symbolic and numeric work.

Grade tracking
--------------
``Sym`` nodes auto-detect the homogeneous grade of their wrapped multivector
(e.g., ``sym(e1, "v")`` knows it's grade-1). This enables ``simplify()`` to
resolve ``grade(v, 1) → v`` and ``grade(v, 2) → 0`` without evaluation.

Usage:
    from ga import Algebra
    from ga.symbolic import sym, grade, reverse

    alg = Algebra((1,1,1))
    e1, e2, e3 = alg.basis_vectors()

    R = sym(e1 * e2, "R")
    v = sym(e1 + 2*e2, "v")

    expr = grade(R * v * ~R, 1)
    print(expr)          # ⟨RvR̃⟩₁
    print(expr.eval())   # concrete Multivector result
    print(expr.latex())  # \\langle R v \\tilde{R} \\rangle_{1}
"""

from __future__ import annotations

from typing import Union
import ga.algebra as _alg

_SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

# Unicode combining characters for postfix decorations.
# These are appended directly after a character to modify its appearance.
# E.g., "R" + _REVERSE → "R̃" (R with combining tilde above).
_REVERSE = "\u0303"      # combining tilde: R̃
_HAT = "\u0302"          # combining circumflex: x̂
_INVOLUTE = "\u0302"     # same hat for involute (standard notation)
_CONJUGATE = "\u0304"    # combining macron: x̄
_DAGGER = "\u0020\u0334" # †


def _coerce(x):
    """Coerce a value to Expr if needed. Used by node constructors."""
    if isinstance(x, Expr):
        return x
    if isinstance(x, _alg.Multivector):
        # Deferred to avoid forward reference — _ensure_expr is defined later
        if x._expr is not None:
            return x._expr
        if x._name is not None:
            return Sym(x, x._name_unicode or x._name,
                       name_latex=x._name_latex, name_ascii=x._name)
        return Sym(x, str(x))
    return x


class Expr:
    """Base class for all symbolic GA expression tree nodes.

    Every node in the expression tree inherits from this. The class provides:
    - Operator overloads that build tree nodes (``__mul__`` → ``Gp``, etc.)
    - ``eval()`` to recursively compute the concrete ``Multivector`` result
    - Rendering via ``ga.render`` (unicode and LaTeX)
    - ``_repr_latex_()`` for automatic Jupyter/marimo rendering
    - Convenience properties (``.inv``, ``.dag``, ``.sq``) matching ``Multivector``

    Subclasses must implement ``eval()``.
    """

    def eval(self) -> _alg.Multivector:
        raise NotImplementedError

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        from ga.render import render
        return render(self)

    def latex(self, wrap: str | None = None) -> str:
        """Return LaTeX representation."""
        from ga.render import render_latex
        raw = render_latex(self)
        if wrap == "$":
            return f"${raw}$"
        if wrap == "$$":
            return f"$$\n{raw}\n$$"
        return raw

    def _repr_latex_(self) -> str:
        """Jupyter notebook integration."""
        return f"${self.latex()}$"

    # --- Operators build expression trees ---

    def __add__(self, other):
        other = _ensure_expr(other)
        return Add(self, other)

    def __radd__(self, other):
        return _ensure_expr(other).__add__(self)

    def __sub__(self, other):
        other = _ensure_expr(other)
        return Sub(self, other)

    def __rsub__(self, other):
        return _ensure_expr(other).__sub__(self)

    def __neg__(self):
        return Neg(self)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return ScalarMul(other, self)
        other = _ensure_expr(other)
        return Gp(self, other)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return ScalarMul(other, self)
        return _ensure_expr(other).__mul__(self)

    def __xor__(self, other):
        return Op(self, _ensure_expr(other))

    def __or__(self, other):
        return Hi(self, _ensure_expr(other))

    def __invert__(self):
        return Reverse(self)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return ScalarDiv(self, other)
        return NotImplemented

    # Convenience properties matching Multivector
    @property
    def inv(self) -> Expr:
        return Inverse(self)

    @property
    def dag(self) -> Expr:
        return Reverse(self)

    @property
    def sq(self) -> Expr:
        return Squared(self)


class Sym(Expr):
    """A named multivector — leaf node of the expression tree.

    Wraps a concrete ``Multivector`` with a display name. This is the entry
    point for building symbolic expressions: ``sym(e1, "v")`` creates a
    ``Sym`` that prints as "v" but evaluates to ``e1``.

    Grade auto-detection: if the wrapped multivector is homogeneous (all
    nonzero coefficients are the same grade), that grade is recorded in
    ``_grade``. This enables ``simplify()`` to resolve grade projections
    without numeric evaluation — e.g., ``grade(v, 1) → v`` when v is
    known to be grade-1, and ``grade(v, 2) → 0``.
    """

    def __init__(self, mv: _alg.Multivector, name: str, grade: int | None = None,
                 name_latex: str | None = None, name_ascii: str | None = None):
        self._mv = mv
        self._name = name
        self._name_latex = name_latex or name
        self._name_ascii = name_ascii or name
        # Auto-detect grade if not provided
        if grade is not None:
            self._grade = grade
        else:
            self._grade = mv.homogeneous_grade()

    def eval(self) -> _alg.Multivector:
        return self._mv



    def __repr__(self) -> str:
        return self._name_ascii


class Scalar(Expr):
    """A numeric scalar leaf — represents a plain number in the expression tree.

    Created automatically by ``_ensure_expr()`` when a Python int/float
    appears in an expression (e.g., ``3 * sym_v`` creates ``ScalarMul(3, sym_v)``
    but ``sym_v + 3`` creates ``Add(sym_v, Scalar(3))``).

    Note: ``eval()`` raises TypeError because a bare scalar has no algebra
    context. Scalars only make sense combined with ``Sym`` nodes that carry
    an algebra reference.
    """

    def __init__(self, value: Numeric):
        self._value = value

    def eval(self) -> _alg.Multivector:
        raise TypeError("Scalar has no algebra context; use in combination with Sym nodes")




# --- Binary ops ---

class Gp(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.gp(self.a.eval(), self.b.eval())




class Op(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.op(self.a.eval(), self.b.eval())




class Lc(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.left_contraction(self.a.eval(), self.b.eval())




class Rc(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.right_contraction(self.a.eval(), self.b.eval())




class Hi(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.hestenes_inner(self.a.eval(), self.b.eval())




class Dli(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.doran_lasenby_inner(self.a.eval(), self.b.eval())




class Sp(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.scalar_product(self.a.eval(), self.b.eval())




class Commutator(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.commutator(self.a.eval(), self.b.eval())




class Anticommutator(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.anticommutator(self.a.eval(), self.b.eval())




class LieBracket(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.lie_bracket(self.a.eval(), self.b.eval())




class JordanProduct(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return _alg.jordan_product(self.a.eval(), self.b.eval())




class Add(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return self.a.eval() + self.b.eval()




class Sub(Expr):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return self.a.eval() - self.b.eval()




class ScalarMul(Expr):
    def __init__(self, k: Numeric, x):
        self.k, self.x = k, _coerce(x)

    def eval(self):
        return self.x.eval() * self.k




class ScalarDiv(Expr):
    """Division by a scalar: x / k."""
    def __init__(self, x, k: Numeric):
        self.x, self.k = _coerce(x), k

    def eval(self):
        return self.x.eval() / self.k




class Div(Expr):
    """Division of two expressions: a / b."""
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return self.a.eval() / self.b.eval()




class Neg(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return -self.x.eval()




# --- Unary ops ---

class Reverse(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.reverse(self.x.eval())




class Involute(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.involute(self.x.eval())




class Conjugate(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.conjugate(self.x.eval())




class Grade(Expr):
    def __init__(self, x, k: int):
        self.x, self.k = _coerce(x), k

    def eval(self):
        return _alg.grade(self.x.eval(), self.k)




class Dual(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.dual(self.x.eval())




class Undual(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.undual(self.x.eval())




class Norm(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.norm(self.x.eval())




class Unit(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.unit(self.x.eval())




class Inverse(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.inverse(self.x.eval())




class Squared(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.gp(self.x.eval(), self.x.eval())




class Exp(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.exp(self.x.eval())




class Even(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.even_grades(self.x.eval())




class Odd(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.odd_grades(self.x.eval())




# --- Helper ---

def _ensure_expr(x) -> Expr:
    """Coerce a value into an Expr node.

    - ``Expr`` → returned as-is
    - ``int``/``float`` → wrapped in ``Scalar``
    - ``Multivector`` with ``_expr`` → returns the expression tree
    - ``Multivector`` with ``_name`` → wrapped in ``Sym`` with its name
    - ``Multivector`` (anonymous eager) → wrapped in ``Sym`` with its string representation

    This is called by every operator overload to handle mixed-type expressions
    like ``sym_v + 3`` or ``sym_R * e1`` transparently.
    """
    if isinstance(x, Expr):
        return x
    if isinstance(x, (int, float)):
        return Scalar(x)
    if isinstance(x, _alg.Multivector):
        if x._expr is not None:
            return x._expr
        if x._name is not None:
            return Sym(x, x._name_unicode or x._name,
                       name_latex=x._name_latex, name_ascii=x._name)
        return Sym(x, str(x))
    raise TypeError(f"Cannot convert {type(x)} to symbolic expression")


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
    if isinstance(a, (Gp, Op, Lc, Rc, Hi, Dli, Sp, Commutator, Anticommutator, LieBracket, JordanProduct, Add, Sub, Div)):
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
    if isinstance(e, (Gp, Op, Lc, Rc, Hi, Dli, Sp, Commutator, Anticommutator, LieBracket, JordanProduct, Add, Sub, Div)):
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

    # Double involution cancellations: applying the same involution twice is identity.
    # ~~x → x
    if isinstance(e, Reverse) and isinstance(e.x, Reverse):
        return e.x.x

    # involute(involute(x)) → x
    if isinstance(e, Involute) and isinstance(e.x, Involute):
        return e.x.x

    # conjugate(conjugate(x)) → x
    if isinstance(e, Conjugate) and isinstance(e.x, Conjugate):
        return e.x.x

    # inverse(inverse(x)) → x
    if isinstance(e, Inverse) and isinstance(e.x, Inverse):
        return e.x.x

    # -(-x) → x
    if isinstance(e, Neg) and isinstance(e.x, Neg):
        return e.x.x

    # Geometric product identities
    # x * 1 → x, 1 * x → x, x * 0 → 0
    if isinstance(e, Gp):
        if _is_scalar(e.a, 1):
            return e.b
        if _is_scalar(e.b, 1):
            return e.a
        if _is_scalar(e.a, 0) or _is_scalar(e.b, 0):
            return Scalar(0)
        # Rotor normalisation: x * ~x → evaluate numerically.
        # This catches R*~R = 1 for rotors, which is the most common case.
        # We fall back to numeric evaluation because the algebraic proof
        # requires knowing the metric, which the symbolic layer doesn't track.
        if isinstance(e.b, Reverse) and _eq(e.a, e.b.x):
            try:
                val = e.eval()
                return Sym(val, str(val))
            except Exception:
                pass

    # Scalar multiplication identities
    # k * (j * x) → (k*j) * x  (collapse nested scalar multiplications)
    if isinstance(e, ScalarMul):
        if e.k == 0:
            return Scalar(0)
        if e.k == 1:
            return e.x
        if isinstance(e.x, ScalarMul):
            return ScalarMul(e.k * e.x.k, e.x.x)

    # Addition identities
    # x + 0 → x, 0 + x → x, x + x → 2x (term collection)
    if isinstance(e, Add):
        if _is_scalar(e.a, 0):
            return e.b
        if _is_scalar(e.b, 0):
            return e.a
        if _eq(e.a, e.b):
            return ScalarMul(2, e.a)

    # Subtraction identities
    # x - x → 0, a - (-b) → a + b (double negation in subtraction)
    if isinstance(e, Sub):
        if _eq(e.a, e.b):
            return Scalar(0)
        if isinstance(e.b, Neg):
            return Add(e.a, e.b.x)

    # Additive cancellation: x + (-x) → 0
    if isinstance(e, Add) and isinstance(e.b, Neg) and _eq(e.a, e.b.x):
        return Scalar(0)

    # Wedge self-annihilation: x ∧ x → 0 (fundamental antisymmetry property)
    if isinstance(e, Op) and _eq(e.a, e.b):
        return Scalar(0)

    # Norm of unit vector is always 1 (by definition of unit)
    # norm(unit(x)) → 1
    if isinstance(e, Norm) and isinstance(e.x, Unit):
        return Scalar(1)

    # --- Grade-aware rules (use _known_grade to avoid numeric evaluation) ---

    # grade(x, k) → x  if x is known to be pure grade k
    # grade(x, k) → 0  if x is known to have no grade-k component
    # This avoids numeric evaluation by using the grade metadata from Sym nodes.
    if isinstance(e, Grade) and isinstance(e.k, int):
        g = _known_grade(e.x)
        if g is not None:
            if g == e.k:
                return e.x
            else:
                return Scalar(0)

    # grade(grade(x, k), k) → grade(x, k)
    if isinstance(e, Grade) and isinstance(e.x, Grade) and e.k == e.x.k:
        return e.x

    # even(x) → x if x is known grade 0 or 2 or 4...
    if isinstance(e, Even):
        g = _known_grade(e.x)
        if g is not None:
            return e.x if g % 2 == 0 else Scalar(0)

    # odd(x) → x if x is known grade 1 or 3 or 5...
    if isinstance(e, Odd):
        g = _known_grade(e.x)
        if g is not None:
            return e.x if g % 2 == 1 else Scalar(0)

    # Jordan product of two vectors → inner product (a ∘ b = a · b for grade 1)
    if isinstance(e, JordanProduct):
        ga = _known_grade(e.a)
        gb = _known_grade(e.b)
        if ga == 1 and gb == 1:
            return Hi(e.a, e.b)

    return e


# ============================================================
# Public API: drop-in replacements for ga.algebra functions
# ============================================================
#
# Each function below checks if any argument is an Expr. If so, it builds
# the corresponding tree node. If all arguments are plain Multivectors,
# it delegates directly to ga.algebra with zero overhead.
#
# This design means users can import from ga.symbolic instead of ga and
# get symbolic behaviour automatically when working with Sym-wrapped values,
# while keeping full numeric performance for unwrapped multivectors.
# ============================================================

def _is_symbolic(x) -> bool:
    """Check if x is an Expr or a lazy Multivector."""
    if isinstance(x, Expr):
        return True
    if isinstance(x, _alg.Multivector) and x._is_lazy:
        return True
    return False


def sym(mv: _alg.Multivector, name: str, grade: int | None = None) -> _alg.Multivector:
    """Wrap a concrete multivector with a display name.

    Returns a **copy** with the name set (does not mutate the original).

    Args:
        name: Display name for all formats.
        grade: If provided, asserts the homogeneous grade for simplification.
               If omitted, auto-detected from the multivector data.
    """
    result = mv._copy_with()  # copy first
    result.name(name)
    if grade is not None:
        result._grade = grade
    if result._expr is not None and isinstance(result._expr, Sym):
        result._expr._grade = result._grade
    return result


def gp(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return Gp(_ensure_expr(a), _ensure_expr(b))
    return _alg.gp(a, b)


def op(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return Op(_ensure_expr(a), _ensure_expr(b))
    return _alg.op(a, b)


def left_contraction(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return Lc(_ensure_expr(a), _ensure_expr(b))
    return _alg.left_contraction(a, b)


def right_contraction(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return Rc(_ensure_expr(a), _ensure_expr(b))
    return _alg.right_contraction(a, b)


def hestenes_inner(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return Hi(_ensure_expr(a), _ensure_expr(b))
    return _alg.hestenes_inner(a, b)


def doran_lasenby_inner(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return Dli(_ensure_expr(a), _ensure_expr(b))
    return _alg.doran_lasenby_inner(a, b)


dorst_inner = doran_lasenby_inner


def scalar_product(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return Sp(_ensure_expr(a), _ensure_expr(b))
    return _alg.scalar_product(a, b)


def commutator(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return Commutator(_ensure_expr(a), _ensure_expr(b))
    return _alg.commutator(a, b)


def anticommutator(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return Anticommutator(_ensure_expr(a), _ensure_expr(b))
    return _alg.anticommutator(a, b)


def lie_bracket(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return LieBracket(_ensure_expr(a), _ensure_expr(b))
    return _alg.lie_bracket(a, b)


def jordan_product(a, b):
    if _is_symbolic(a) or _is_symbolic(b):
        return JordanProduct(_ensure_expr(a), _ensure_expr(b))
    return _alg.jordan_product(a, b)


def reverse(x):
    if _is_symbolic(x):
        return Reverse(_ensure_expr(x))
    return _alg.reverse(x)


def involute(x):
    if _is_symbolic(x):
        return Involute(_ensure_expr(x))
    return _alg.involute(x)


def conjugate(x):
    if _is_symbolic(x):
        return Conjugate(_ensure_expr(x))
    return _alg.conjugate(x)


def grade(x, k):
    if _is_symbolic(x):
        e = _ensure_expr(x)
        if k == "even":
            return Even(e)
        if k == "odd":
            return Odd(e)
        return Grade(e, k)
    return _alg.grade(x, k)


def dual(x):
    if _is_symbolic(x):
        return Dual(_ensure_expr(x))
    return _alg.dual(x)


def undual(x):
    if _is_symbolic(x):
        return Undual(_ensure_expr(x))
    return _alg.undual(x)


def norm(x):
    if _is_symbolic(x):
        return Norm(_ensure_expr(x))
    return _alg.norm(x)


def unit(x):
    if _is_symbolic(x):
        return Unit(_ensure_expr(x))
    return _alg.unit(x)


def inverse(x):
    if _is_symbolic(x):
        return Inverse(_ensure_expr(x))
    return _alg.inverse(x)


normalize = unit
normalise = unit


def ip(a, b, mode: str = "doran_lasenby"):
    if _is_symbolic(a) or _is_symbolic(b):
        a, b = _ensure_expr(a), _ensure_expr(b)
        match mode:
            case "doran_lasenby" | "dorst":
                return Dli(a, b)
            case "hestenes":
                return Hi(a, b)
            case "left":
                return Lc(a, b)
            case "right":
                return Rc(a, b)
            case "scalar":
                return Sp(a, b)
            case _:
                raise ValueError(f"Unknown inner product mode: {mode!r}")
    return _alg.ip(a, b, mode=mode)


def squared(x):
    if _is_symbolic(x):
        return Squared(_ensure_expr(x))
    return _alg.squared(x)


def sandwich(r, x):
    if _is_symbolic(r) or _is_symbolic(x):
        re = _ensure_expr(r)
        xe = _ensure_expr(x)
        return Gp(Gp(re, xe), Reverse(re))
    return _alg.sandwich(r, x)


sw = sandwich


def even_grades(x):
    if _is_symbolic(x):
        return Even(_ensure_expr(x))
    return _alg.even_grades(x)


def odd_grades(x):
    if _is_symbolic(x):
        return Odd(_ensure_expr(x))
    return _alg.odd_grades(x)


