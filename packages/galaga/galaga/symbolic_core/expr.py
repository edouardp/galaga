"""Domain-neutral symbolic expression nodes."""

from __future__ import annotations

from numbers import Number


class Expr:
    """Base class for domain-neutral symbolic expressions."""

    def eval(self):
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

    def __add__(self, other):
        return Add(self, _ensure_expr(other))

    def __radd__(self, other):
        return Add(_ensure_expr(other), self)

    def __sub__(self, other):
        return Sub(self, _ensure_expr(other))

    def __rsub__(self, other):
        return Sub(_ensure_expr(other), self)

    def __neg__(self):
        return Neg(self)

    def __mul__(self, other):
        if isinstance(other, Number):
            return ScalarMul(other, self)
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, Number):
            return ScalarMul(other, self)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Number):
            return ScalarDiv(self, other)
        return Div(self, _ensure_expr(other))


class Sym(Expr):
    """Named symbolic leaf wrapping a concrete value."""

    def __init__(
        self,
        value,
        name: str,
        grade: int | None = None,
        name_latex: str | None = None,
        name_ascii: str | None = None,
        inner_expr: Expr | None = None,
    ):
        self._value = value
        self._mv = value
        self._name = name
        self._name_latex = name_latex or name
        self._name_ascii = name_ascii or name
        self._grade = grade
        self._inner_expr = inner_expr

    @property
    def is_compound(self) -> bool:
        latex = self._name_latex or self._name
        if self._inner_expr is not None:
            if not (hasattr(self._inner_expr, "a") and hasattr(self._inner_expr, "b")):
                return False
            depth = 0
            for ch in latex:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                elif ch == " " and depth == 0:
                    return True
            return False
        return any(op in latex for op in (r"\wedge", r"\vee", r"\cdot", " + ", " - "))

    @property
    def has_superscript(self) -> bool:
        return "^" in (self._name_latex or self._name)

    def eval(self):
        return self._value

    def __repr__(self) -> str:
        return self._name_ascii


class Scalar(Expr):
    """Numeric scalar leaf."""

    def __init__(self, value: Number):
        self._value = value

    def eval(self):
        return self._value


class Add(Expr):
    def __init__(self, a, b):
        self.a, self.b = _ensure_expr(a), _ensure_expr(b)

    def eval(self):
        return self.a.eval() + self.b.eval()


class Sub(Expr):
    def __init__(self, a, b):
        self.a, self.b = _ensure_expr(a), _ensure_expr(b)

    def eval(self):
        return self.a.eval() - self.b.eval()


class Neg(Expr):
    def __init__(self, x):
        self.x = _ensure_expr(x)

    def eval(self):
        return -self.x.eval()


class ScalarMul(Expr):
    def __init__(self, k: Number, x):
        self.k, self.x = k, _ensure_expr(x)

    def eval(self):
        return self.k * self.x.eval()


class ScalarDiv(Expr):
    def __init__(self, x, k: Number):
        self.x, self.k = _ensure_expr(x), k

    def eval(self):
        return self.x.eval() / self.k


class Div(Expr):
    def __init__(self, a, b):
        self.a, self.b = _ensure_expr(a), _ensure_expr(b)

    def eval(self):
        return self.a.eval() / self.b.eval()


def _ensure_expr(value) -> Expr:
    if isinstance(value, Expr):
        return value
    if isinstance(value, Number):
        return Scalar(value)
    if hasattr(value, "_to_expr"):
        return value._to_expr()
    raise TypeError(f"Cannot convert {type(value)} to Expr")
