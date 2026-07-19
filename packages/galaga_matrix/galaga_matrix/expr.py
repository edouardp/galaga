"""Immutable, package-owned expression provenance for :class:`MatrixRepr`.

Matrix operations are not geometric-algebra catalog operations, so their
provenance does not belong in :mod:`galaga.expression`.  This module owns the
small matrix expression vocabulary and adapts public Galaga expression nodes
at the representation-map boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Number
from typing import Any

import numpy as np

from galaga.expression import Expr as GalagaExpr
from galaga.names import Name
from galaga.presentation import PresentationConfig


class Expr:
    """Base class for immutable matrix expression provenance."""

    __slots__ = ()

    def eval(self):
        """Evaluate the expression using the eager values captured by leaves."""
        raise NotImplementedError

    def render(self, target: str = "unicode") -> str:
        """Render as ASCII, Unicode, or LaTeX."""
        if target not in {"ascii", "unicode", "latex"}:
            raise ValueError("target must be 'ascii', 'unicode', or 'latex'")
        return _render(self, target)

    def latex(self, wrap: str | None = None) -> str:
        raw = self.render("latex")
        if wrap == "$":
            return f"${raw}$"
        if wrap == "$$":
            return f"$$\n{raw}\n$$"
        if wrap is not None:
            raise ValueError("LaTeX wrap must be None, '$', or '$$'")
        return raw

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        return self.render("ascii")

    def _repr_latex_(self) -> str:
        return self.latex(wrap="$")


def _readonly_array(value: Any) -> np.ndarray:
    source = value.mat if hasattr(value, "mat") else value
    array = np.array(source, copy=True)
    array.setflags(write=False)
    return array


@dataclass(frozen=True, slots=True, eq=False, init=False)
class Symbol(Expr):
    """A named matrix leaf with an immutable eager-value snapshot."""

    name: Name
    value: np.ndarray
    inner_expr: Expr | None

    def __init__(self, name: Name, value: Any, inner_expr: Expr | None = None) -> None:
        if not isinstance(name, Name):
            raise TypeError("matrix symbol name must be a Name")
        if inner_expr is not None and not isinstance(inner_expr, Expr):
            raise TypeError("inner_expr must be a matrix Expr or None")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "value", _readonly_array(value))
        object.__setattr__(self, "inner_expr", inner_expr)

    def eval(self) -> np.ndarray:
        return self.value.copy()


@dataclass(frozen=True, slots=True, eq=False, init=False)
class MatrixLiteral(Expr):
    """An unnamed immutable matrix-value leaf."""

    value: np.ndarray

    def __init__(self, value: Any) -> None:
        object.__setattr__(self, "value", _readonly_array(value))

    def eval(self) -> np.ndarray:
        return self.value.copy()


@dataclass(frozen=True, slots=True)
class Scalar(Expr):
    value: Number

    def eval(self) -> Number:
        return self.value


@dataclass(frozen=True, slots=True, eq=False)
class GalagaExpression(Expr):
    """Public adapter from Galaga provenance into the matrix expression tree."""

    expression: GalagaExpr
    presentation: PresentationConfig
    value: Any

    def __post_init__(self) -> None:
        if not isinstance(self.expression, GalagaExpr):
            raise TypeError("expression must be a galaga.expression.Expr")
        if not isinstance(self.presentation, PresentationConfig):
            raise TypeError("presentation must be a PresentationConfig")

    def eval(self) -> Any:
        return self.value


@dataclass(frozen=True, slots=True)
class Add(Expr):
    a: Expr
    b: Expr

    def __init__(self, a: Any, b: Any) -> None:
        object.__setattr__(self, "a", _ensure_expr(a))
        object.__setattr__(self, "b", _ensure_expr(b))

    def eval(self):
        return self.a.eval() + self.b.eval()


@dataclass(frozen=True, slots=True)
class Sub(Expr):
    a: Expr
    b: Expr

    def __init__(self, a: Any, b: Any) -> None:
        object.__setattr__(self, "a", _ensure_expr(a))
        object.__setattr__(self, "b", _ensure_expr(b))

    def eval(self):
        return self.a.eval() - self.b.eval()


@dataclass(frozen=True, slots=True)
class Neg(Expr):
    x: Expr

    def __init__(self, x: Any) -> None:
        object.__setattr__(self, "x", _ensure_expr(x))

    def eval(self):
        return -self.x.eval()


@dataclass(frozen=True, slots=True)
class ScalarMul(Expr):
    k: Number
    x: Expr

    def __init__(self, k: Number, x: Any) -> None:
        object.__setattr__(self, "k", k)
        object.__setattr__(self, "x", _ensure_expr(x))

    def eval(self):
        return self.k * self.x.eval()


@dataclass(frozen=True, slots=True)
class ScalarDiv(Expr):
    x: Expr
    k: Number

    def __init__(self, x: Any, k: Number) -> None:
        object.__setattr__(self, "x", _ensure_expr(x))
        object.__setattr__(self, "k", k)

    def eval(self):
        return self.x.eval() / self.k


@dataclass(frozen=True, slots=True)
class MatMul(Expr):
    a: Expr
    b: Expr

    def __init__(self, a: Any, b: Any) -> None:
        object.__setattr__(self, "a", _ensure_expr(a))
        object.__setattr__(self, "b", _ensure_expr(b))

    def eval(self):
        return self.a.eval() @ self.b.eval()


@dataclass(frozen=True, slots=True)
class MatrixElementwiseMul(Expr):
    a: Expr
    b: Expr

    def __init__(self, a: Any, b: Any) -> None:
        object.__setattr__(self, "a", _ensure_expr(a))
        object.__setattr__(self, "b", _ensure_expr(b))

    def eval(self):
        return self.a.eval() * self.b.eval()


@dataclass(frozen=True, slots=True)
class Transpose(Expr):
    x: Expr

    def __init__(self, x: Any) -> None:
        object.__setattr__(self, "x", _ensure_expr(x))

    def eval(self):
        return self.x.eval().T


@dataclass(frozen=True, slots=True)
class Adjoint(Expr):
    x: Expr

    def __init__(self, x: Any) -> None:
        object.__setattr__(self, "x", _ensure_expr(x))

    def eval(self):
        return self.x.eval().conj().T


@dataclass(frozen=True, slots=True)
class ConjugateMatrix(Expr):
    x: Expr

    def __init__(self, x: Any) -> None:
        object.__setattr__(self, "x", _ensure_expr(x))

    def eval(self):
        return self.x.eval().conj()


@dataclass(frozen=True, slots=True)
class MatrixInverse(Expr):
    x: Expr

    def __init__(self, x: Any) -> None:
        object.__setattr__(self, "x", _ensure_expr(x))

    def eval(self):
        return np.linalg.inv(self.x.eval())


@dataclass(frozen=True, slots=True)
class KroneckerProduct(Expr):
    a: Expr
    b: Expr

    def __init__(self, a: Any, b: Any) -> None:
        object.__setattr__(self, "a", _ensure_expr(a))
        object.__setattr__(self, "b", _ensure_expr(b))

    def eval(self):
        return np.kron(self.a.eval(), self.b.eval())


@dataclass(frozen=True, slots=True, eq=False, init=False)
class MatrixBasisChange(Expr):
    x: Expr
    target: str
    value: np.ndarray | None

    def __init__(self, x: Any, target: str, *, value: Any | None = None) -> None:
        object.__setattr__(self, "x", _ensure_expr(x))
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "value", None if value is None else _readonly_array(value))

    def eval(self):
        if self.value is not None:
            return self.value.copy()
        source = self.x.eval()
        if hasattr(source, "to_basis"):
            return source.to_basis(self.target)
        raise ValueError("matrix basis-change evaluation requires a captured eager result")


@dataclass(frozen=True, slots=True, eq=False, init=False)
class MatrixRepresentation(Expr):
    x: Expr
    mode: str
    basis: str | None
    value: np.ndarray | None

    def __init__(self, x: Any, *, mode: str, basis: str | None = None, value: Any | None = None) -> None:
        object.__setattr__(self, "x", _ensure_expr(x))
        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "basis", basis)
        object.__setattr__(self, "value", None if value is None else _readonly_array(value))

    def eval(self):
        if self.value is not None:
            return self.value.copy()
        from .matrix import to_matrix

        return np.asarray(to_matrix(self.x.eval(), mode=self.mode))


@dataclass(frozen=True, slots=True, eq=False, init=False)
class SpinorColumnRepresentation(Expr):
    x: Expr
    basis: str | None
    value: np.ndarray | None

    def __init__(self, x: Any, *, basis: str | None = None, value: Any | None = None) -> None:
        object.__setattr__(self, "x", _ensure_expr(x))
        object.__setattr__(self, "basis", basis)
        object.__setattr__(self, "value", None if value is None else _readonly_array(value))

    def eval(self):
        if self.value is not None:
            return self.value.copy()
        from .matrix import to_spinor_column

        return np.asarray(to_spinor_column(self.x.eval()))


def multivector_operand(value: Any) -> Expr | None:
    """Adapt only the public Galaga 2 name/provenance protocol."""
    name = getattr(value, "name", None)
    expression = getattr(value, "expr", None)
    algebra = getattr(value, "algebra", None)
    presentation = getattr(algebra, "presentation", None)

    inner = None
    if isinstance(expression, GalagaExpr) and isinstance(presentation, PresentationConfig):
        inner = GalagaExpression(expression, presentation, value)
    if isinstance(name, Name):
        return Symbol(name, value.data, inner_expr=inner)
    return inner


def _ensure_expr(value: Any) -> Expr:
    if isinstance(value, Expr):
        return value
    if isinstance(value, Number):
        return Scalar(value)
    as_expression = getattr(value, "as_expression", None)
    if callable(as_expression):
        result = as_expression()
        if isinstance(result, Expr):
            return result
    if isinstance(value, (np.ndarray, list, tuple)):
        return MatrixLiteral(value)
    raise TypeError(f"Cannot convert {type(value).__name__} to a matrix expression")


def _prec(node: Expr) -> int:
    return {
        Symbol: 100,
        MatrixLiteral: 100,
        Scalar: 100,
        GalagaExpression: 100,
        MatrixRepresentation: 100,
        SpinorColumnRepresentation: 100,
        Transpose: 95,
        Adjoint: 95,
        ConjugateMatrix: 95,
        MatrixInverse: 95,
        MatrixBasisChange: 95,
        MatMul: 80,
        MatrixElementwiseMul: 80,
        ScalarMul: 80,
        ScalarDiv: 80,
        KroneckerProduct: 75,
        Neg: 70,
        Add: 60,
        Sub: 60,
    }.get(type(node), 50)


def _wrap(rendered: str, node: Expr, min_prec: int) -> str:
    return f"({rendered})" if _prec(node) < min_prec else rendered


def _fmt_scalar(value: Any) -> str:
    try:
        return f"{value:g}"
    except (TypeError, ValueError):
        return str(value)


def _basis_rho_latex(basis: str | None, mode: str | None = None) -> str:
    if mode == "quaternion":
        return r"\rho_{\mathbb{H}}"
    if basis in (None, "pauli", "dirac"):
        return r"\rho"
    if basis == "weyl":
        return r"\rho^{\mathrm{Weyl}}"
    if basis == "majorana":
        return r"\rho^{\mathrm{Majorana}}"
    return r"\rho"


def _basis_label(basis: str, target: str) -> str:
    text = {"weyl": "Weyl", "majorana": "Majorana", "dirac": "Dirac"}.get(basis, basis)
    return rf"\mathrm{{{text}}}" if target == "latex" else text


def _render(node: Expr, target: str) -> str:  # noqa: PLR0911, PLR0912
    if isinstance(node, Symbol):
        return node.name.for_target(target)
    if isinstance(node, MatrixLiteral):
        return np.array2string(node.value)
    if isinstance(node, Scalar):
        return _fmt_scalar(node.value)
    if isinstance(node, GalagaExpression):
        from galaga.display import render

        algebra = getattr(node.value, "algebra", None)
        presentation = getattr(algebra, "presentation", node.presentation)
        return render(node.expression, presentation=presentation, target=target)
    if isinstance(node, Neg):
        return f"-{_wrap(_render(node.x, target), node.x, 61)}"
    if isinstance(node, ScalarMul):
        child = _wrap(_render(node.x, target), node.x, 61)
        if node.k == 1:
            return child
        if node.k == -1:
            return f"-{child}"
        return f"{_fmt_scalar(node.k)}{child}"
    if isinstance(node, ScalarDiv):
        child = _wrap(_render(node.x, target), node.x, 70)
        if target == "latex":
            return rf"\frac{{{child}}}{{{_fmt_scalar(node.k)}}}"
        return f"{child}/{_fmt_scalar(node.k)}"
    if isinstance(node, Add):
        lhs = _wrap(_render(node.a, target), node.a, 60)
        rhs = _render(node.b, target)
        return f"{lhs} - {rhs[1:]}" if rhs.startswith("-") else f"{lhs} + {rhs}"
    if isinstance(node, Sub):
        return f"{_render(node.a, target)} - {_wrap(_render(node.b, target), node.b, 61)}"
    if isinstance(node, (MatMul, MatrixElementwiseMul, KroneckerProduct)):
        precedence = _prec(node)
        symbol = " "
        if isinstance(node, MatrixElementwiseMul):
            symbol = r" \odot " if target == "latex" else " ⊙ "
        elif isinstance(node, KroneckerProduct):
            symbol = r" \otimes " if target == "latex" else " ⊗ "
        lhs = _wrap(_render(node.a, target), node.a, precedence)
        rhs = _wrap(_render(node.b, target), node.b, precedence)
        return f"{lhs}{symbol}{rhs}"
    if isinstance(node, Transpose):
        child = _wrap(_render(node.x, target), node.x, 95)
        return rf"{child}^T" if target == "latex" else f"{child}ᵀ"
    if isinstance(node, Adjoint):
        child = _wrap(_render(node.x, target), node.x, 95)
        if target == "latex":
            if child.startswith(r"\left|") and child.endswith(r"\right\rangle"):
                inner = child[len(r"\left|") : -len(r"\right\rangle")]
                return rf"\left\langle {inner}\right|"
            return rf"{child}^\dagger"
        return f"{child}†"
    if isinstance(node, ConjugateMatrix):
        child = _wrap(_render(node.x, target), node.x, 95)
        return rf"\overline{{{child}}}" if target == "latex" else f"conj({child})"
    if isinstance(node, MatrixInverse):
        child = _wrap(_render(node.x, target), node.x, 95)
        return rf"{child}^{{-1}}" if target == "latex" else f"{child}⁻¹"
    if isinstance(node, MatrixRepresentation):
        source = _render(node.x, target)
        if target == "latex":
            return rf"{_basis_rho_latex(node.basis, node.mode)}({source})"
        if node.basis not in (None, "pauli", "dirac"):
            return f"ρ^{_basis_label(node.basis, target)}({source})"
        return f"ρ({source})"
    if isinstance(node, SpinorColumnRepresentation):
        source = _render(node.x, target)
        return rf"\left|\rho({source})\right\rangle" if target == "latex" else f"|ρ({source})⟩"
    if isinstance(node, MatrixBasisChange):
        child = _wrap(_render(node.x, target), node.x, 95)
        inner = node.x.inner_expr if isinstance(node.x, Symbol) else None
        if isinstance(inner, MatrixRepresentation) and child == _render(inner, target):
            source = _render(inner.x, target)
            if target == "latex":
                return rf"{_basis_rho_latex(node.target)}({source})"
            return f"ρ^{_basis_label(node.target, target)}({source})"
        label = _basis_label(node.target, target)
        return rf"{child}^{{({label})}}" if target == "latex" else f"{child}^({label})"
    raise TypeError(f"unsupported matrix expression node {type(node).__name__}")


__all__ = [
    "Add",
    "Adjoint",
    "ConjugateMatrix",
    "Expr",
    "GalagaExpression",
    "KroneckerProduct",
    "MatMul",
    "MatrixBasisChange",
    "MatrixElementwiseMul",
    "MatrixInverse",
    "MatrixLiteral",
    "MatrixRepresentation",
    "Neg",
    "Scalar",
    "ScalarDiv",
    "ScalarMul",
    "SpinorColumnRepresentation",
    "Sub",
    "Symbol",
    "Transpose",
    "multivector_operand",
]
