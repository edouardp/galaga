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

import sys as _sys

from . import algebra as _alg

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
        from .render import render

        return render(self)

    def latex(self, wrap: str | None = None) -> str:
        from .render import render_latex

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
        return Gp(self, _ensure_expr(other))  # noqa: F821

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return ScalarMul(other, self)
        return _ensure_expr(other).__mul__(self)

    def __xor__(self, other):
        return Op(self, _ensure_expr(other))  # noqa: F821

    def __or__(self, other):
        return Hi(self, _ensure_expr(other))  # noqa: F821

    def __invert__(self):
        return Reverse(self)  # noqa: F821

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return ScalarDiv(self, other)
        return NotImplemented

    @property
    def inv(self) -> Expr:
        return Inverse(self)  # noqa: F821

    @property
    def dag(self) -> Expr:
        return Reverse(self)  # noqa: F821

    @property
    def sq(self) -> Expr:
        return Squared(self)


# ── Leaf nodes ──


class Sym(Expr):
    """Named multivector — leaf node wrapping a concrete MV with a display name.

    Grade auto-detection: if the wrapped MV is homogeneous, that grade is
    recorded for use by simplify() (e.g. grade(v,1) → v when v is grade-1).

    _inner_expr: if this Sym was created from a named symbolic MV that had an
    expression tree, the original tree is preserved here. This lets the
    renderer detect compound expressions (e.g. a ∧ b) and wrap them in
    parens when applying postfix operations.
    """

    def __init__(
        self,
        mv: _alg.Multivector,
        name: str,
        grade: int | None = None,
        name_latex: str | None = None,
        name_ascii: str | None = None,
        inner_expr: Expr | None = None,
    ):
        self._mv = mv
        self._name = name
        self._name_latex = name_latex or name
        self._name_ascii = name_ascii or name
        self._grade = grade if grade is not None else mv.homogeneous_grade()
        self._inner_expr = inner_expr

    @property
    def is_compound(self) -> bool:
        """True if this Sym's name represents a compound expression that needs
        wrapping when a postfix is applied.

        Uses inner_expr when available: compound if the inner expression is
        binary AND the name contains spaces (wasn't abbreviated to a simple name).
        Falls back to checking the name string for infix operators.
        """
        latex = self._name_latex or self._name
        if self._inner_expr is not None:
            if not (hasattr(self._inner_expr, "a") and hasattr(self._inner_expr, "b")):
                return False
            return " " in latex
        # Fallback: check name string for operator patterns
        return any(op in latex for op in (r"\wedge", r"\vee", r"\cdot", " + ", " - "))

    @property
    def has_superscript(self) -> bool:
        """True if this Sym's latex name contains a superscript ^."""
        return "^" in (self._name_latex or self._name)

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
# Node classes are auto-generated from tables. The _NODE_NAMES table is the
# single mapping from GA operation names to Expr class names. Adding a new
# @ga_op in algebra.py requires only adding an entry here and a handler
# registration below. The invariant tests enforce that these stay in sync
# with GA_OPS.


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


# op_name → (class_name, arity)
_NODE_NAMES = {
    # Binary
    "gp": ("Gp", 2),
    "op": ("Op", 2),
    "left_contraction": ("Lc", 2),
    "right_contraction": ("Rc", 2),
    "hestenes_inner": ("Hi", 2),
    "doran_lasenby_inner": ("Dli", 2),
    "scalar_product": ("Sp", 2),
    "commutator": ("Commutator", 2),
    "anticommutator": ("Anticommutator", 2),
    "lie_bracket": ("LieBracket", 2),
    "jordan_product": ("JordanProduct", 2),
    "regressive_product": ("Regressive", 2),
    # Unary
    "reverse": ("Reverse", 1),
    "involute": ("Involute", 1),
    "conjugate": ("Conjugate", 1),
    "dual": ("Dual", 1),
    "undual": ("Undual", 1),
    "complement": ("Complement", 1),
    "uncomplement": ("Uncomplement", 1),
    "unit": ("Unit", 1),
    "inverse": ("Inverse", 1),
    "even_grades": ("Even", 1),
    "odd_grades": ("Odd", 1),
    "exp": ("Exp", 1),
    "log": ("Log", 1),
    "outerexp": ("OuterExp", 1),
    "outersin": ("OuterSin", 1),
    "outercos": ("OuterCos", 1),
    "outertan": ("OuterTan", 1),
}

# Additional unary nodes for functions not in GA_OPS
_EXTRA_UNARY = {
    "Norm": "norm",
    "Norm2": "norm2",
    "Sqrt": "scalar_sqrt",
}

_this = _sys.modules[__name__]

for _op_name, (_class_name, _arity) in _NODE_NAMES.items():
    if _arity == 2:
        _cls = _make_binary_expr(_class_name, _op_name)
    else:
        _cls = _make_unary_expr(_class_name, _op_name)
    setattr(_this, _class_name, _cls)

for _class_name, _func_name in _EXTRA_UNARY.items():
    _cls = _make_unary_expr(_class_name, _func_name)
    setattr(_this, _class_name, _cls)

# The setattr loop above populates these names at runtime.
# Re-export them as module-level locals for static imports.
# (The Expr class methods reference Gp/Op/Hi/Reverse/Inverse/ScalarDiv
# before this point, but they execute after module load completes.)
Gp = Gp  # noqa: F821, PLW0127
Op = Op  # noqa: F821, PLW0127
Lc = Lc  # noqa: F821, PLW0127
Rc = Rc  # noqa: F821, PLW0127
Hi = Hi  # noqa: F821, PLW0127
Dli = Dli  # noqa: F821, PLW0127
Sp = Sp  # noqa: F821, PLW0127
Commutator = Commutator  # noqa: F821, PLW0127
Anticommutator = Anticommutator  # noqa: F821, PLW0127
LieBracket = LieBracket  # noqa: F821, PLW0127
JordanProduct = JordanProduct  # noqa: F821, PLW0127
Regressive = Regressive  # noqa: F821, PLW0127
Reverse = Reverse  # noqa: F821, PLW0127
Involute = Involute  # noqa: F821, PLW0127
Conjugate = Conjugate  # noqa: F821, PLW0127
Dual = Dual  # noqa: F821, PLW0127
Undual = Undual  # noqa: F821, PLW0127
Complement = Complement  # noqa: F821, PLW0127
Uncomplement = Uncomplement  # noqa: F821, PLW0127
Norm = Norm  # noqa: F821, PLW0127
Norm2 = Norm2  # noqa: F821, PLW0127
Unit = Unit  # noqa: F821, PLW0127
Inverse = Inverse  # noqa: F821, PLW0127
Even = Even  # noqa: F821, PLW0127
Odd = Odd  # noqa: F821, PLW0127
Exp = Exp  # noqa: F821, PLW0127
Log = Log  # noqa: F821, PLW0127
OuterExp = OuterExp  # noqa: F821, PLW0127
OuterSin = OuterSin  # noqa: F821, PLW0127
OuterCos = OuterCos  # noqa: F821, PLW0127
OuterTan = OuterTan  # noqa: F821, PLW0127
Sqrt = Sqrt  # noqa: F821, PLW0127


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


# ── Helpers ──


def _is_symbolic(x) -> bool:
    """True if x is a symbolic Multivector (has an expression tree)."""
    return isinstance(x, _alg.Multivector) and x._is_symbolic


def sym(mv: _alg.Multivector, name: str | None = None, grade: int | None = None) -> _alg.Multivector:
    """Create a named symbolic copy of a multivector.

    Returns a new Multivector that is a copy of mv, with .name(name) applied.
    If no name is given, the copy is made symbolic but anonymous.
    Non-mutating: the original mv is not modified.
    """
    copy = _alg.Multivector(mv.algebra, mv.data)
    if name is not None:
        copy.name(name)
    else:
        copy.symbolic()
    return copy


# ── Register symbolic handlers for @ga_op operations ──

from .ops import register_sym_factory, register_symbolic_handler

register_sym_factory(Sym, Sym)

_HANDLER_MAP = {
    # GA operations
    "gp": Gp,
    "op": Op,
    "left_contraction": Lc,
    "right_contraction": Rc,
    "hestenes_inner": Hi,
    "doran_lasenby_inner": Dli,
    "scalar_product": Sp,
    "commutator": Commutator,
    "anticommutator": Anticommutator,
    "lie_bracket": LieBracket,
    "jordan_product": JordanProduct,
    "reverse": Reverse,
    "involute": Involute,
    "conjugate": Conjugate,
    "dual": Dual,
    "undual": Undual,
    "complement": Complement,
    "uncomplement": Uncomplement,
    "regressive_product": Regressive,
    "unit": Unit,
    "inverse": Inverse,
    "even_grades": Even,
    "odd_grades": Odd,
    "exp": Exp,
    "log": Log,
    "outerexp": OuterExp,
    "outersin": OuterSin,
    "outercos": OuterCos,
    "outertan": OuterTan,
    # Arithmetic / structural nodes
    "add": Add,
    "sub": Sub,
    "neg": Neg,
    "scalar": Scalar,
    "scalar_mul": ScalarMul,
    "scalar_div": ScalarDiv,
    "div": Div,
    "squared": Squared,
    "grade": Grade,
    "norm": Norm,
    "norm2": Norm2,
    "sqrt": Sqrt,
}

for _name, _handler in _HANDLER_MAP.items():
    register_symbolic_handler(_name, _handler)
