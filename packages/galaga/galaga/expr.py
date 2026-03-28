"""Expression tree nodes for symbolic geometric algebra.

Pure data structures with no dependency on ga.algebra at import time.
Each node stores its children and implements eval() by delegating to
ga.algebra (resolved lazily via the _alg module reference).

Node categories:
    Leaf:   Sym (named MV), Scalar (numeric constant)
    Binary: Gp, Op, Add, Sub, Div, Lc, Rc, Hi, Dli, Sp, Regressive,
            Commutator, Anticommutator, LieBracket, JordanProduct
    Unary:  Reverse, Involute, Conjugate, Dual, Undual, Complement,
            Uncomplement, Norm, Unit, Inverse, Exp, Log, Even, Odd
    Other:  Neg, ScalarMul, ScalarDiv, Grade, Squared
"""

from __future__ import annotations

import galaga.algebra as _alg

Numeric = int | float


# ── Coercion ──


def _coerce(x):
    """Coerce a value to Expr if needed. Used by node constructors."""
    if isinstance(x, Expr):
        return x
    if isinstance(x, _alg.Multivector):
        if x._expr is not None:
            return x._expr
        if x._name is not None:
            return Sym(x, x._name_unicode or x._name, name_latex=x._name_latex, name_ascii=x._name)
        return Sym(x, str(x))
    return x


# ── Base class ──


class Expr:
    """Base class for all symbolic GA expression tree nodes.

    Subclasses must implement eval(). Operator overloads build tree nodes.
    Rendering delegates to ga.render (unicode and LaTeX).
    """

    def eval(self) -> _alg.Multivector:
        raise NotImplementedError

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        from galaga.render import render

        return render(self)

    def latex(self, wrap: str | None = None) -> str:
        from galaga.render import render_latex

        raw = render_latex(self)
        if wrap == "$":
            return f"${raw}$"
        if wrap == "$$":
            return f"$$\n{raw}\n$$"
        return raw

    def _repr_latex_(self) -> str:
        return f"${self.latex()}$"

    # Operators build expression trees
    def __add__(self, other):
        return Add(self, _ensure_expr(other))

    def __radd__(self, other):
        return _ensure_expr(other).__add__(self)

    def __sub__(self, other):
        return Sub(self, _ensure_expr(other))

    def __rsub__(self, other):
        return _ensure_expr(other).__sub__(self)

    def __neg__(self):
        return Neg(self)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return ScalarMul(other, self)
        return Gp(self, _ensure_expr(other))

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

    @property
    def inv(self) -> Expr:
        return Inverse(self)

    @property
    def dag(self) -> Expr:
        return Reverse(self)

    @property
    def sq(self) -> Expr:
        return Squared(self)


# ── Leaf nodes ──


class Sym(Expr):
    """Named multivector — leaf node wrapping a concrete MV with a display name.

    Grade auto-detection: if the wrapped MV is homogeneous, that grade is
    recorded for use by simplify() (e.g. grade(v,1) → v when v is grade-1).
    """

    def __init__(
        self,
        mv: _alg.Multivector,
        name: str,
        grade: int | None = None,
        name_latex: str | None = None,
        name_ascii: str | None = None,
    ):
        self._mv = mv
        self._name = name
        self._name_latex = name_latex or name
        self._name_ascii = name_ascii or name
        self._grade = grade if grade is not None else mv.homogeneous_grade()

    def eval(self) -> _alg.Multivector:
        return self._mv

    def __repr__(self) -> str:
        return self._name_ascii


class Scalar(Expr):
    """Numeric scalar leaf — a plain number in the expression tree."""

    def __init__(self, value: Numeric):
        self._value = value

    def eval(self) -> _alg.Multivector:
        raise TypeError("Scalar has no algebra context; use with Sym nodes")


# ── Generated binary/unary nodes ──
#
# Most nodes are identical: __init__ coerces args, eval() delegates to
# ga.algebra. Generated from tables to eliminate boilerplate.


def _make_binary_expr(name, alg_func_name):
    def __init__(self, a, b):
        self.a, self.b = _coerce(a), _coerce(b)

    def eval(self):
        return getattr(_alg, alg_func_name)(self.a.eval(), self.b.eval())

    return type(name, (Expr,), {"__init__": __init__, "eval": eval})


def _make_unary_expr(name, alg_func_name):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return getattr(_alg, alg_func_name)(self.x.eval())

    return type(name, (Expr,), {"__init__": __init__, "eval": eval})


# Binary
Gp = _make_binary_expr("Gp", "gp")
Op = _make_binary_expr("Op", "op")
Lc = _make_binary_expr("Lc", "left_contraction")
Rc = _make_binary_expr("Rc", "right_contraction")
Hi = _make_binary_expr("Hi", "hestenes_inner")
Dli = _make_binary_expr("Dli", "doran_lasenby_inner")
Sp = _make_binary_expr("Sp", "scalar_product")
Commutator = _make_binary_expr("Commutator", "commutator")
Anticommutator = _make_binary_expr("Anticommutator", "anticommutator")
LieBracket = _make_binary_expr("LieBracket", "lie_bracket")
JordanProduct = _make_binary_expr("JordanProduct", "jordan_product")
Regressive = _make_binary_expr("Regressive", "regressive_product")

# Unary
Reverse = _make_unary_expr("Reverse", "reverse")
Involute = _make_unary_expr("Involute", "involute")
Conjugate = _make_unary_expr("Conjugate", "conjugate")
Dual = _make_unary_expr("Dual", "dual")
Undual = _make_unary_expr("Undual", "undual")
Complement = _make_unary_expr("Complement", "complement")
Uncomplement = _make_unary_expr("Uncomplement", "uncomplement")
Norm = _make_unary_expr("Norm", "norm")
Unit = _make_unary_expr("Unit", "unit")
Inverse = _make_unary_expr("Inverse", "inverse")
Exp = _make_unary_expr("Exp", "exp")
Log = _make_unary_expr("Log", "log")
Even = _make_unary_expr("Even", "even_grades")
Odd = _make_unary_expr("Odd", "odd_grades")


# ── Hand-written nodes (need custom eval or extra fields) ──


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


class Grade(Expr):
    def __init__(self, x, k: int):
        self.x, self.k = _coerce(x), k

    def eval(self):
        return _alg.grade(self.x.eval(), self.k)


class Squared(Expr):
    def __init__(self, x):
        self.x = _coerce(x)

    def eval(self):
        return _alg.gp(self.x.eval(), self.x.eval())


# ── Coercion helper (defined after all node classes) ──


def _ensure_expr(x) -> Expr:
    """Convert any value to an Expr node for use in expression trees."""
    if isinstance(x, Expr):
        return x
    if isinstance(x, _alg.Multivector):
        return _coerce(x)
    if isinstance(x, (int, float)):
        return Scalar(x)
    raise TypeError(f"Cannot convert {type(x)} to Expr")
