"""Symbolic expression nodes for MatrixRepr."""

from __future__ import annotations

from galaga.symbolic_core.expr import Add, Expr, Sub, _ensure_expr


def _prec(node) -> int:
    return getattr(node, "_render_prec", {Add: 60, Sub: 60}.get(type(node), 100))


def _wrap(rendered: str, node, min_prec: int) -> str:
    return f"({rendered})" if _prec(node) < min_prec else rendered


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


def _basis_label_latex(basis: str) -> str:
    if basis == "weyl":
        return r"\mathrm{Weyl}"
    if basis == "majorana":
        return r"\mathrm{Majorana}"
    if basis == "dirac":
        return r"\mathrm{Dirac}"
    return rf"\mathrm{{{basis}}}"


def _basis_label_text(basis: str) -> str:
    if basis == "weyl":
        return "Weyl"
    if basis == "majorana":
        return "Majorana"
    if basis == "dirac":
        return "Dirac"
    return basis


class MatMul(Expr):
    _render_prec = 80

    def __init__(self, a, b):
        self.a, self.b = _ensure_expr(a), _ensure_expr(b)

    def eval(self):
        return self.a.eval() @ self.b.eval()

    def _render(self, render, fmt: str) -> str:
        lhs = _wrap(render(self.a), self.a, 80)
        rhs = _wrap(render(self.b), self.b, 80)
        return f"{lhs} {rhs}"


class MatrixElementwiseMul(Expr):
    _render_prec = 80

    def __init__(self, a, b):
        self.a, self.b = _ensure_expr(a), _ensure_expr(b)

    def eval(self):
        return self.a.eval() * self.b.eval()

    def _render(self, render, fmt: str) -> str:
        symbol = r"\odot" if fmt == "latex" else "⊙"
        return f"{_wrap(render(self.a), self.a, 80)} {symbol} {_wrap(render(self.b), self.b, 80)}"


class Transpose(Expr):
    _render_prec = 95

    def __init__(self, x):
        self.x = _ensure_expr(x)

    def eval(self):
        return self.x.eval().T

    def _render(self, render, fmt: str) -> str:
        suffix = "T" if fmt == "latex" else "ᵀ"
        return f"{_wrap(render(self.x), self.x, 95)}^{suffix}" if fmt == "latex" else f"{render(self.x)}{suffix}"


class Adjoint(Expr):
    _render_prec = 95

    def __init__(self, x):
        self.x = _ensure_expr(x)

    def eval(self):
        return self.x.eval().H

    def _render(self, render, fmt: str) -> str:
        child = _wrap(render(self.x), self.x, 95)
        if fmt == "latex":
            if child.startswith(r"\left|") and child.endswith(r"\right\rangle"):
                inner = child[len(r"\left|") : -len(r"\right\rangle")]
                return rf"\left\langle {inner}\right|"
            return rf"{child}^\dagger"
        return f"{child}†"


class ConjugateMatrix(Expr):
    _render_prec = 95

    def __init__(self, x):
        self.x = _ensure_expr(x)

    def eval(self):
        return self.x.eval().conj()

    def _render(self, render, fmt: str) -> str:
        child = _wrap(render(self.x), self.x, 95)
        return rf"\overline{{{child}}}" if fmt == "latex" else f"conj({child})"


class MatrixInverse(Expr):
    _render_prec = 95

    def __init__(self, x):
        self.x = _ensure_expr(x)

    def eval(self):
        return self.x.eval().inv()

    def _render(self, render, fmt: str) -> str:
        child = _wrap(render(self.x), self.x, 95)
        return rf"{child}^{{-1}}" if fmt == "latex" else f"{child}⁻¹"


class KroneckerProduct(Expr):
    _render_prec = 75

    def __init__(self, a, b):
        self.a, self.b = _ensure_expr(a), _ensure_expr(b)

    def eval(self):
        return self.a.eval().kron(self.b.eval())

    def _render(self, render, fmt: str) -> str:
        symbol = r"\otimes" if fmt == "latex" else "⊗"
        return f"{_wrap(render(self.a), self.a, 75)} {symbol} {_wrap(render(self.b), self.b, 75)}"


class MatrixBasisChange(Expr):
    _render_prec = 95

    def __init__(self, x, target: str):
        self.x = _ensure_expr(x)
        self.target = target

    def eval(self):
        return self.x.eval().to_basis(self.target)

    def _render(self, render, fmt: str) -> str:
        child = _wrap(render(self.x), self.x, 95)
        rep = None
        if isinstance(self.x, MatrixRepresentation):
            rep = self.x
        else:
            inner = getattr(self.x, "_inner_expr", None)
            if isinstance(inner, MatrixRepresentation) and child == render(inner):
                rep = inner
        if rep is not None:
            if isinstance(rep.x, Expr):
                source = render(rep.x)
            elif fmt == "latex" and hasattr(rep.x, "latex"):
                source = rep.x.latex()
            else:
                source = str(rep.x)
            if fmt == "latex":
                return rf"{_basis_rho_latex(self.target)}({source})"
            return f"ρ^{_basis_label_text(self.target)}({source})"
        if fmt == "latex":
            return rf"{child}^{{({_basis_label_latex(self.target)})}}"
        return f"{child}^({_basis_label_text(self.target)})"


class MatrixRepresentation(Expr):
    _render_prec = 100

    def __init__(self, x, *, mode: str, basis: str | None = None, value=None):
        self.x = x
        self.mode = mode
        self.basis = basis
        self._value = value

    def eval(self):
        if self._value is not None:
            return self._value.eval()
        from .matrix import to_matrix

        return to_matrix(self.x.eval(), mode=self.mode).eval()

    def _render(self, render, fmt: str) -> str:
        if isinstance(self.x, Expr):
            source = render(self.x)
        elif fmt == "latex" and hasattr(self.x, "latex"):
            source = self.x.latex()
        else:
            source = str(self.x)
        if fmt == "latex":
            return rf"{_basis_rho_latex(self.basis, self.mode)}({source})"
        return f"ρ({source})"


class SpinorColumnRepresentation(Expr):
    _render_prec = 100

    def __init__(self, x, *, basis: str | None = None, value=None):
        self.x = x
        self.basis = basis
        self._value = value

    def eval(self):
        if self._value is not None:
            return self._value.eval()
        from .matrix import to_spinor_column

        return to_spinor_column(self.x.eval()).eval()

    def _render(self, render, fmt: str) -> str:
        if isinstance(self.x, Expr):
            source = render(self.x)
        elif fmt == "latex" and hasattr(self.x, "latex"):
            source = self.x.latex()
        else:
            source = str(self.x)
        if fmt == "latex":
            return rf"\left|\rho({source})\right\rangle"
        return f"|ρ({source})⟩"
