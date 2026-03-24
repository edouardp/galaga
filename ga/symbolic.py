"""Symbolic expression tree for pretty-printing GA expressions.

Usage:
    from ga import Algebra, grade, reverse
    from ga.symbolic import sym

    alg = Algebra((1,1,1))
    e1, e2, e3 = alg.basis_vectors()

    R = sym(e1 * e2, "R")
    v = sym(e1 + 2*e2, "v")

    expr = grade(R * v * ~R, 0)
    print(expr)          # ⟨Rv R̃⟩₀
    result = expr.eval() # concrete Multivector
"""

from __future__ import annotations

from typing import Union
import ga.algebra as _alg

_SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
_REVERSE = "\u0303"      # combining tilde: R̃
_HAT = "\u0302"          # combining circumflex: x̂
_INVOLUTE = "\u0302"     # same hat for involute
_CONJUGATE = "\u0304"    # combining macron: x̄
_DAGGER = "\u0020\u0334" # †


def _needs_parens(node: Expr, parent_op: str) -> bool:
    """Whether a node needs parentheses in the context of parent_op."""
    if isinstance(node, (Sym, Neg)):
        return False
    if isinstance(node, (Add, Sub)):
        return parent_op in ("gp", "op", "lc", "rc", "hi", "sp")
    return False


def _wrap(node: Expr, parent_op: str) -> str:
    s = str(node)
    if _needs_parens(node, parent_op):
        return f"({s})"
    return s


def _latex_wrap(node: Expr, parent_op: str) -> str:
    s = node._latex()
    if _needs_parens(node, parent_op):
        return rf"\left({s}\right)"
    return s


Numeric = Union[int, float]


class Expr:
    """Base class for symbolic GA expressions."""

    def eval(self) -> _alg.Multivector:
        raise NotImplementedError

    def latex(self, wrap: str | None = None) -> str:
        """Return LaTeX representation.

        Args:
            wrap: Optional delimiter — '$' for inline, '$$' for display block.
        """
        raw = self._latex()
        if wrap == "$":
            return f"${raw}$"
        if wrap == "$$":
            return f"$$\n{raw}\n$$"
        return raw

    def _latex(self) -> str:
        """Override in subclasses to provide LaTeX output."""
        raise NotImplementedError

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
        return Lc(self, _ensure_expr(other))

    def __invert__(self):
        return Reverse(self)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return ScalarMul(1.0 / other, self)
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
    """A named multivector — leaf node."""

    def __init__(self, mv: _alg.Multivector, name: str):
        self._mv = mv
        self._name = name

    def eval(self) -> _alg.Multivector:
        return self._mv

    def __str__(self) -> str:
        return self._name

    def _latex(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"Sym({self._name})"


class Scalar(Expr):
    """A numeric scalar leaf."""

    def __init__(self, value: Numeric):
        self._value = value

    def eval(self) -> _alg.Multivector:
        raise TypeError("Scalar has no algebra context; use in combination with Sym nodes")

    def __str__(self) -> str:
        return f"{self._value:g}"

    def _latex(self) -> str:
        return f"{self._value:g}"


# --- Binary ops ---

class Gp(Expr):
    def __init__(self, a: Expr, b: Expr):
        self.a, self.b = a, b

    def eval(self):
        return _alg.gp(self.a.eval(), self.b.eval())

    def __str__(self):
        return _wrap(self.a, "gp") + _wrap(self.b, "gp")

    def _latex(self):
        return _latex_wrap(self.a, "gp") + " " + _latex_wrap(self.b, "gp")


class Op(Expr):
    def __init__(self, a: Expr, b: Expr):
        self.a, self.b = a, b

    def eval(self):
        return _alg.op(self.a.eval(), self.b.eval())

    def __str__(self):
        return f"{_wrap(self.a, 'op')}∧{_wrap(self.b, 'op')}"

    def _latex(self):
        return rf"{_latex_wrap(self.a, 'op')} \wedge {_latex_wrap(self.b, 'op')}"


class Lc(Expr):
    def __init__(self, a: Expr, b: Expr):
        self.a, self.b = a, b

    def eval(self):
        return _alg.left_contraction(self.a.eval(), self.b.eval())

    def __str__(self):
        return f"{_wrap(self.a, 'lc')}⌋{_wrap(self.b, 'lc')}"

    def _latex(self):
        return rf"{_latex_wrap(self.a, 'lc')} \;\lrcorner\; {_latex_wrap(self.b, 'lc')}"


class Rc(Expr):
    def __init__(self, a: Expr, b: Expr):
        self.a, self.b = a, b

    def eval(self):
        return _alg.right_contraction(self.a.eval(), self.b.eval())

    def __str__(self):
        return f"{_wrap(self.a, 'rc')}⌊{_wrap(self.b, 'rc')}"

    def _latex(self):
        return rf"{_latex_wrap(self.a, 'rc')} \;\llcorner\; {_latex_wrap(self.b, 'rc')}"


class Hi(Expr):
    def __init__(self, a: Expr, b: Expr):
        self.a, self.b = a, b

    def eval(self):
        return _alg.hestenes_inner(self.a.eval(), self.b.eval())

    def __str__(self):
        return f"{_wrap(self.a, 'hi')}·{_wrap(self.b, 'hi')}"

    def _latex(self):
        return rf"{_latex_wrap(self.a, 'hi')} \cdot {_latex_wrap(self.b, 'hi')}"


class Sp(Expr):
    def __init__(self, a: Expr, b: Expr):
        self.a, self.b = a, b

    def eval(self):
        return _alg.scalar_product(self.a.eval(), self.b.eval())

    def __str__(self):
        return f"{_wrap(self.a, 'sp')}∗{_wrap(self.b, 'sp')}"

    def _latex(self):
        return rf"{_latex_wrap(self.a, 'sp')} * {_latex_wrap(self.b, 'sp')}"


class Add(Expr):
    def __init__(self, a: Expr, b: Expr):
        self.a, self.b = a, b

    def eval(self):
        return self.a.eval() + self.b.eval()

    def __str__(self):
        return f"{self.a} + {self.b}"

    def _latex(self):
        return f"{self.a._latex()} + {self.b._latex()}"


class Sub(Expr):
    def __init__(self, a: Expr, b: Expr):
        self.a, self.b = a, b

    def eval(self):
        return self.a.eval() - self.b.eval()

    def __str__(self):
        return f"{self.a} - {self.b}"

    def _latex(self):
        return f"{self.a._latex()} - {self.b._latex()}"


class ScalarMul(Expr):
    def __init__(self, k: Numeric, x: Expr):
        self.k, self.x = k, x

    def eval(self):
        return self.x.eval() * self.k

    def __str__(self):
        if self.k == -1:
            return f"-{self.x}"
        return f"{self.k:g}{_wrap(self.x, 'gp')}"

    def _latex(self):
        if self.k == -1:
            return f"-{self.x._latex()}"
        return f"{self.k:g} {_latex_wrap(self.x, 'gp')}"


class Neg(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return -self.x.eval()

    def __str__(self):
        return f"-{self.x}"

    def _latex(self):
        return f"-{self.x._latex()}"


# --- Unary ops ---

class Reverse(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.reverse(self.x.eval())

    def __str__(self):
        return f"{self.x}{_REVERSE}"

    def _latex(self):
        return rf"\tilde{{{self.x._latex()}}}"


class Involute(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.involute(self.x.eval())

    def __str__(self):
        return f"{self.x}{_INVOLUTE}"

    def _latex(self):
        return rf"{self.x._latex()}^\dagger"


class Conjugate(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.conjugate(self.x.eval())

    def __str__(self):
        return f"{self.x}{_CONJUGATE}"

    def _latex(self):
        return rf"\bar{{{self.x._latex()}}}"


class Grade(Expr):
    def __init__(self, x: Expr, k: int):
        self.x, self.k = x, k

    def eval(self):
        return _alg.grade(self.x.eval(), self.k)

    def __str__(self):
        sub = str(self.k).translate(_SUBSCRIPTS)
        return f"⟨{self.x}⟩{sub}"

    def _latex(self):
        return rf"\langle {self.x._latex()} \rangle_{{{self.k}}}"


class Dual(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.dual(self.x.eval())

    def __str__(self):
        return f"{self.x}⋆"

    def _latex(self):
        return rf"{self.x._latex()}^*"


class Undual(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.undual(self.x.eval())

    def __str__(self):
        return f"{self.x}⋆⁻¹"

    def _latex(self):
        return rf"{self.x._latex()}^{{*^{{-1}}}}"


class Norm(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.norm(self.x.eval())

    def __str__(self):
        return f"‖{self.x}‖"

    def _latex(self):
        return rf"\lVert {self.x._latex()} \rVert"


class Unit(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.unit(self.x.eval())

    def __str__(self):
        s = str(self.x)
        if len(s) == 1:
            return f"{s}{_HAT}"
        return f"{self.x}/‖{self.x}‖"

    def _latex(self):
        return rf"\hat{{{self.x._latex()}}}"


class Inverse(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.inverse(self.x.eval())

    def __str__(self):
        return f"{self.x}⁻¹"

    def _latex(self):
        return rf"{self.x._latex()}^{{-1}}"


class Squared(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.gp(self.x.eval(), self.x.eval())

    def __str__(self):
        return f"{self.x}²"

    def _latex(self):
        return rf"{self.x._latex()}^2"


class Even(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.even_grades(self.x.eval())

    def __str__(self):
        return f"⟨{self.x}⟩₊"

    def _latex(self):
        return rf"\langle {self.x._latex()} \rangle_{{\text{{even}}}}"


class Odd(Expr):
    def __init__(self, x: Expr):
        self.x = x

    def eval(self):
        return _alg.odd_grades(self.x.eval())

    def __str__(self):
        return f"⟨{self.x}⟩₋"

    def _latex(self):
        return rf"\langle {self.x._latex()} \rangle_{{\text{{odd}}}}"


# --- Helper ---

def _ensure_expr(x) -> Expr:
    if isinstance(x, Expr):
        return x
    if isinstance(x, (int, float)):
        return Scalar(x)
    if isinstance(x, _alg.Multivector):
        return Sym(x, str(x))
    raise TypeError(f"Cannot convert {type(x)} to symbolic expression")


# --- Public API: drop-in replacements for ga.algebra functions ---
# These detect Expr arguments and return Expr trees; otherwise delegate to numeric.

def sym(mv: _alg.Multivector, name: str) -> Sym:
    """Wrap a concrete multivector with a display name."""
    return Sym(mv, name)


def gp(a, b):
    if isinstance(a, Expr) or isinstance(b, Expr):
        return Gp(_ensure_expr(a), _ensure_expr(b))
    return _alg.gp(a, b)


def op(a, b):
    if isinstance(a, Expr) or isinstance(b, Expr):
        return Op(_ensure_expr(a), _ensure_expr(b))
    return _alg.op(a, b)


def left_contraction(a, b):
    if isinstance(a, Expr) or isinstance(b, Expr):
        return Lc(_ensure_expr(a), _ensure_expr(b))
    return _alg.left_contraction(a, b)


def right_contraction(a, b):
    if isinstance(a, Expr) or isinstance(b, Expr):
        return Rc(_ensure_expr(a), _ensure_expr(b))
    return _alg.right_contraction(a, b)


def hestenes_inner(a, b):
    if isinstance(a, Expr) or isinstance(b, Expr):
        return Hi(_ensure_expr(a), _ensure_expr(b))
    return _alg.hestenes_inner(a, b)


def scalar_product(a, b):
    if isinstance(a, Expr) or isinstance(b, Expr):
        return Sp(_ensure_expr(a), _ensure_expr(b))
    return _alg.scalar_product(a, b)


def reverse(x):
    if isinstance(x, Expr):
        return Reverse(x)
    return _alg.reverse(x)


def involute(x):
    if isinstance(x, Expr):
        return Involute(x)
    return _alg.involute(x)


def conjugate(x):
    if isinstance(x, Expr):
        return Conjugate(x)
    return _alg.conjugate(x)


def grade(x, k):
    if isinstance(x, Expr):
        if k == "even":
            return Even(x)
        if k == "odd":
            return Odd(x)
        return Grade(x, k)
    return _alg.grade(x, k)


def dual(x):
    if isinstance(x, Expr):
        return Dual(x)
    return _alg.dual(x)


def undual(x):
    if isinstance(x, Expr):
        return Undual(x)
    return _alg.undual(x)


def norm(x):
    if isinstance(x, Expr):
        return Norm(x)
    return _alg.norm(x)


def unit(x):
    if isinstance(x, Expr):
        return Unit(x)
    return _alg.unit(x)


def inverse(x):
    if isinstance(x, Expr):
        return Inverse(x)
    return _alg.inverse(x)


normalize = unit
normalise = unit


def ip(a, b, mode: str = "hestenes"):
    if isinstance(a, Expr) or isinstance(b, Expr):
        a, b = _ensure_expr(a), _ensure_expr(b)
        match mode:
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
    if isinstance(x, Expr):
        return Squared(x)
    return _alg.squared(x)


def sandwich(r, x):
    if isinstance(r, Expr) or isinstance(x, Expr):
        r = r if isinstance(r, Expr) else sym(r, str(r))
        x = x if isinstance(x, Expr) else sym(x, str(x))
        return Gp(Gp(r, x), Reverse(r))
    return _alg.sandwich(r, x)


sw = sandwich


def even_grades(x):
    if isinstance(x, Expr):
        return Even(x)
    return _alg.even_grades(x)


def odd_grades(x):
    if isinstance(x, Expr):
        return Odd(x)
    return _alg.odd_grades(x)


even = even_grades
odd = odd_grades
