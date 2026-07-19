"""LaTeX rendering and transparent numpy proxy for matrix representations.

Provides ``MatrixRepr``, a wrapper around matrix data that:
- Supports ``.latex()`` and ``._repr_latex_()`` for notebooks
- Forwards all arithmetic operations (matmul, add, sub, etc.)
- Preserves metadata (algebra, mode, basis, kind) through operations
- Supports Galaga-style ``.name()`` symbolic naming and expression trees
- Acts as a transparent numpy proxy via ``__array_ufunc__``

Handles complex matrices (from left-regular and compact modes) and
quaternion matrices (from ``to_matrix(mv, mode="quaternion")``).
"""

from __future__ import annotations

from numbers import Number
from typing import Any

import numpy as np

from galaga.names import Name

from .expr import (
    Add,
    Adjoint,
    ConjugateMatrix,
    KroneckerProduct,
    MatMul,
    MatrixBasisChange,
    MatrixElementwiseMul,
    MatrixInverse,
    Neg,
    Scalar,
    ScalarDiv,
    ScalarMul,
    Sub,
    Symbol,
    Transpose,
)


def _fmt(z: complex, tol: float = 1e-12) -> str:
    """Format a complex number for LaTeX."""
    re, im = z.real, z.imag
    if abs(im) < tol:
        return _fmt_real(re)
    if abs(re) < tol:
        return _fmt_imag(im)
    sign = "+" if im >= 0 else "-"
    return f"{_fmt_real(re)} {sign} {_fmt_imag(abs(im))}"


def _fmt_real(x: float, tol: float = 1e-12) -> str:
    if abs(x - round(x)) < tol:
        return str(int(round(x)))
    return f"{x:.4g}"


def _fmt_imag(x: float, tol: float = 1e-12) -> str:
    if abs(x) < tol:
        return "0"
    if abs(x - 1) < tol:
        return "i"
    if abs(x + 1) < tol:
        return "-i"
    if abs(x - round(x)) < tol:
        return f"{int(round(x))}i"
    return f"{x:.4g}i"


def _unwrap(x) -> np.ndarray | Any:
    """Extract numpy array from MatrixRepr or return as-is."""
    if isinstance(x, MatrixRepr):
        return x.mat
    return x


def _is_scalar(x) -> bool:
    return isinstance(x, (Number, np.number))


def _quat_grid_to_complex(qmat: list[list]) -> np.ndarray:
    """Convert a list-of-lists of Quat to a complex numpy matrix.

    Each Quat is embedded as a 2×2 complex block:
        q = a + bi + cj + dk → [[a+bi, c+di], [-c+di, a-bi]]
    """
    rows = len(qmat)
    cols = len(qmat[0]) if rows else 0
    result = np.zeros((2 * rows, 2 * cols), dtype=complex)
    for i in range(rows):
        for j in range(cols):
            q = qmat[i][j]
            result[2 * i, 2 * j] = q.a + q.b * 1j
            result[2 * i, 2 * j + 1] = q.c + q.d * 1j
            result[2 * i + 1, 2 * j] = -q.c + q.d * 1j
            result[2 * i + 1, 2 * j + 1] = q.a - q.b * 1j
    return result


class _MatrixDisplayResult:
    """LaTeX-renderable MatrixRepr display result."""

    def __init__(self, parts: list[str], sep: str, value: MatrixRepr):
        self.parts = parts
        self.sep = sep
        self.value = value

    def latex(self, wrap: str | None = None) -> str:
        raw = self.sep.join(self.parts)
        if wrap == "$":
            return f"${raw}$"
        if wrap == "$$":
            return f"$$\n{raw}\n$$"
        return raw

    def _repr_latex_(self) -> str:
        return f"${self.latex()}$"

    def __str__(self) -> str:
        return self.latex()


class MatrixRepr:
    """A matrix with LaTeX rendering and transparent numpy proxy behavior.

    Works in galaga_marimo t-strings via the ``.latex()`` protocol,
    and in Jupyter via ``_repr_latex_()``. All arithmetic operations
    return new MatrixRepr instances, preserving metadata.

    Handles two data formats:

    - **numpy array** (real or complex): from ``to_matrix``
    - **list-of-lists of Quat**: from ``to_matrix(mv, mode="quaternion")``

    The format is auto-detected from the data type.

    Args:
        data: A numpy array or list-of-lists of Quat objects.
        algebra: Optional reference to the source Algebra (enables ``.mv``).
        mode: The representation mode (``"left-regular"``, ``"compact"``,
              or ``"quaternion"``).
    """

    def __init__(
        self,
        data,
        *,
        algebra=None,
        mode: str = "left-regular",
        basis: str | None = None,
        kind: str = "operator",
    ):
        self._symbolic_name: Name | None = None
        self._tracking = False
        self._expression = None
        if isinstance(data, MatrixRepr):
            # Unwrap: copy the underlying matrix, inherit metadata if not overridden
            self.mat = data.mat.copy()
            self.algebra = algebra if algebra is not None else data.algebra
            self.mode = mode if mode != "left-regular" else data.mode
            self.basis = basis if basis is not None else data.basis
            self.kind = kind if kind != "operator" else data.kind
            self._symbolic_name = data._symbolic_name
            self._tracking = data._tracking
            self._expression = data._expression
        elif isinstance(data, np.ndarray):
            self.mat = data
        elif isinstance(data, list) and data and isinstance(data[0], list):
            # list-of-lists of Quat → convert to complex matrix
            self.mat = _quat_grid_to_complex(data)
            mode = "quaternion"
        else:
            self.mat = np.asarray(data)
        if not isinstance(data, MatrixRepr):
            self.algebra = algebra
            self.mode = mode
            self.basis = basis
            self.kind = kind

    def _copy_with_symbolic(self, **overrides) -> MatrixRepr:
        copy = MatrixRepr(self.mat.copy(), algebra=self.algebra, mode=self.mode, basis=self.basis, kind=self.kind)
        copy._symbolic_name = overrides.get("name", self._symbolic_name)
        copy._tracking = overrides.get("tracking", self._tracking)
        copy._expression = overrides.get("expression", self._expression)
        return copy

    @property
    def symbolic_name(self) -> Name | None:
        """The immutable, target-aware matrix name, if one was assigned."""
        return self._symbolic_name

    @property
    def is_symbolic(self) -> bool:
        """Whether subsequent operations record matrix expression provenance."""
        return self._tracking

    def name(
        self,
        label: str | None = None,
        *,
        latex: str | None = None,
        unicode: str | None = None,
        ascii: str | None = None,
    ) -> MatrixRepr:
        """Assign a target-aware name and enable expression tracking in place."""
        if label is None and latex is None:
            raise ValueError("at least one of label or latex must be provided")
        ascii_name = (ascii or label or latex).strip()
        unicode_name = (unicode or label or ascii_name).strip()
        latex_name = (latex or label or unicode_name).strip()
        self._symbolic_name = Name(ascii_name, unicode=unicode_name, latex=latex_name)
        self._tracking = True
        if self._expression is None or isinstance(self._expression, Symbol):
            self._expression = Symbol(self._symbolic_name, self.mat)
        return self

    def anon(self) -> MatrixRepr:
        """Remove the name while preserving compound provenance."""
        if isinstance(self._expression, Symbol):
            self._expression = None
        self._symbolic_name = None
        return self

    def symbolic(self) -> MatrixRepr:
        self._tracking = True
        return self

    def lazy(self) -> MatrixRepr:
        return self.symbolic()

    def numeric(self, name: str | None = None) -> MatrixRepr:
        self._tracking = False
        self._expression = None
        self._symbolic_name = Name(name) if name is not None else None
        return self

    def eager(self, name: str | None = None) -> MatrixRepr:
        return self.numeric(name)

    def eval(self) -> MatrixRepr:
        """Return an eager copy without symbolic name or provenance."""
        return self._copy_with_symbolic(name=None, tracking=False, expression=None)

    def reveal(self) -> MatrixRepr:
        """Return a copy with provenance but without its display name."""
        return self._copy_with_symbolic(name=None)

    def copy_as(
        self,
        label: str | None = None,
        *,
        latex: str | None = None,
        unicode: str | None = None,
        ascii: str | None = None,
    ) -> MatrixRepr:
        return self._copy_with_symbolic().name(label, latex=latex, unicode=unicode, ascii=ascii)

    def as_expression(self):
        """Return this matrix as a package-owned immutable expression node."""
        if self._symbolic_name is not None:
            inner = (
                self._expression if self._expression is not None and not isinstance(self._expression, Symbol) else None
            )
            return Symbol(self._symbolic_name, self.mat, inner_expr=inner)
        if self._expression is not None:
            return self._expression
        return Symbol(Name(str(self), latex=self._matrix_latex_raw()), self.mat)

    @property
    def expr(self):
        """The symbolic expression tree, if this matrix is symbolic."""
        return self._expression

    def _attach_expression(self, expression) -> None:
        """Attach package-owned provenance to an eager conversion result."""
        from .expr import Expr

        if not isinstance(expression, Expr):
            raise TypeError("expression must be a galaga_matrix Expr")
        self._tracking = True
        self._expression = expression

    def _symbolic_result(
        self,
        result: np.ndarray,
        expr,
        *,
        algebra=None,
        mode: str | None = None,
        basis: str | None = None,
        kind: str | None = None,
    ) -> MatrixRepr:
        wrapped = MatrixRepr(
            result,
            algebra=self.algebra if algebra is None else algebra,
            mode=self.mode if mode is None else mode,
            basis=self.basis if basis is None else basis,
            kind=self.kind if kind is None else kind,
        )
        wrapped._tracking = True
        wrapped._expression = expr
        return wrapped

    def _wrap(self, result: np.ndarray) -> MatrixRepr:
        """Wrap a numpy result in a new MatrixRepr, inheriting algebra/mode/basis/kind."""
        return MatrixRepr(result, algebra=self.algebra, mode=self.mode, basis=self.basis, kind=self.kind)

    def _require_mat(self) -> np.ndarray:
        """Get the numpy array."""
        return self.mat

    @property
    def quat(self) -> list[list]:
        """Read the matrix as a quaternion grid (k×k Quat entries).

        Each 2×2 complex block is interpreted as one quaternion.
        Only meaningful when mode='quaternion'.

        Raises:
            TypeError: If mode is not 'quaternion' or dimensions are odd.
        """
        from .matrix import Quat

        if self.mode != "quaternion":
            raise TypeError("`.quat` is only available for mode='quaternion' matrices.")
        rows, cols = self.mat.shape
        if rows % 2 != 0 or cols % 2 != 0:
            raise TypeError(f"Cannot read {rows}×{cols} matrix as quaternion blocks (need even dimensions).")
        qrows = rows // 2
        qcols = cols // 2
        result = []
        for i in range(qrows):
            row = []
            for j in range(qcols):
                block = self.mat[2 * i : 2 * i + 2, 2 * j : 2 * j + 2]
                a = block[0, 0].real
                b = block[0, 0].imag
                c = block[0, 1].real
                d = block[0, 1].imag
                row.append(Quat(a, b, c, d))
            result.append(row)
        return result

    # ── Conversion ──

    @property
    def mv(self):
        """Convert back to a galaga Multivector."""
        if self.algebra is None:
            raise ValueError("No algebra reference; pass algebra= when creating MatrixRepr")
        from galaga_matrix.matrix import from_matrix

        if self.mat is not None:
            return from_matrix(self)
        raise ValueError("Cannot convert quaternion matrix back to MV; use compact or left-regular mode")

    # ── Shape / indexing ──

    @property
    def shape(self) -> tuple[int, ...]:
        """Matrix shape."""
        return self._require_mat().shape

    @property
    def dtype(self) -> np.dtype:
        """Matrix dtype."""
        return self._require_mat().dtype

    def __len__(self) -> int:
        return len(self._require_mat())

    def __getitem__(self, key):
        result = self._require_mat()[key]
        if isinstance(result, np.ndarray) and result.ndim == 2:
            return self._wrap(result)
        return result  # scalar or 1D slice — return raw

    def _operand_expr(self, value):
        if isinstance(value, MatrixRepr):
            return value.as_expression()
        if _is_scalar(value):
            return Scalar(value)
        return MatrixRepr(
            np.asarray(value),
            algebra=self.algebra,
            mode=self.mode,
            basis=self.basis,
            kind="operator",
        ).as_expression()

    def _is_symbolic_with(self, other=None) -> bool:
        return self._tracking or (isinstance(other, MatrixRepr) and other._tracking)

    # ── Arithmetic operators ──

    def __matmul__(self, other) -> MatrixRepr:
        other_mat = _unwrap(other)
        result = self._require_mat() @ other_mat
        # Type propagation: operator @ ket → ket, bra @ ket → scalar
        other_kind = other.kind if isinstance(other, MatrixRepr) else "operator"
        if self.kind == "bra" and other_kind == "ket":
            return result[0, 0]  # inner product → complex scalar
        result_kind = self.kind
        if self.kind == "operator" and other_kind == "ket":
            result_kind = "ket"
        elif self.kind == "ket" and other_kind == "bra":
            result_kind = "operator"
        if self._is_symbolic_with(other):
            return self._symbolic_result(
                result,
                MatMul(self.as_expression(), self._operand_expr(other)),
                kind=result_kind,
            )
        return MatrixRepr(result, algebra=self.algebra, mode=self.mode, basis=self.basis, kind=result_kind)

    def __rmatmul__(self, other) -> MatrixRepr:
        if self._tracking:
            return self._symbolic_result(
                _unwrap(other) @ self._require_mat(), MatMul(self._operand_expr(other), self.as_expression())
            )
        return self._wrap(_unwrap(other) @ self._require_mat())

    def __add__(self, other) -> MatrixRepr:
        result = self._require_mat() + _unwrap(other)
        if self._is_symbolic_with(other):
            return self._symbolic_result(result, Add(self.as_expression(), self._operand_expr(other)))
        return self._wrap(result)

    def __radd__(self, other) -> MatrixRepr:
        result = _unwrap(other) + self._require_mat()
        if self._tracking:
            return self._symbolic_result(result, Add(self._operand_expr(other), self.as_expression()))
        return self._wrap(result)

    def __sub__(self, other) -> MatrixRepr:
        result = self._require_mat() - _unwrap(other)
        if self._is_symbolic_with(other):
            return self._symbolic_result(result, Sub(self.as_expression(), self._operand_expr(other)))
        return self._wrap(result)

    def __rsub__(self, other) -> MatrixRepr:
        result = _unwrap(other) - self._require_mat()
        if self._tracking:
            return self._symbolic_result(result, Sub(self._operand_expr(other), self.as_expression()))
        return self._wrap(result)

    def __mul__(self, other) -> MatrixRepr:
        result = self._require_mat() * _unwrap(other)
        if self._is_symbolic_with(other):
            if _is_scalar(other):
                expr = ScalarMul(other, self.as_expression())
            else:
                expr = MatrixElementwiseMul(self.as_expression(), self._operand_expr(other))
            return self._symbolic_result(result, expr)
        return self._wrap(result)

    def __rmul__(self, other) -> MatrixRepr:
        result = _unwrap(other) * self._require_mat()
        if self._tracking:
            if _is_scalar(other):
                expr = ScalarMul(other, self.as_expression())
            else:
                expr = MatrixElementwiseMul(self._operand_expr(other), self.as_expression())
            return self._symbolic_result(result, expr)
        return self._wrap(result)

    def __truediv__(self, other) -> MatrixRepr:
        result = self._require_mat() / _unwrap(other)
        if self._tracking:
            if _is_scalar(other):
                expr = ScalarDiv(self.as_expression(), other)
            else:
                expr = MatrixElementwiseMul(self.as_expression(), self._operand_expr(1 / _unwrap(other)))
            return self._symbolic_result(result, expr)
        return self._wrap(result)

    def __neg__(self) -> MatrixRepr:
        result = -self._require_mat()
        if self._tracking:
            return self._symbolic_result(result, Neg(self.as_expression()))
        return self._wrap(result)

    def __pos__(self) -> MatrixRepr:
        return self._wrap(+self._require_mat())

    def __pow__(self, n: int) -> MatrixRepr:
        """Integer matrix power."""
        return self._wrap(np.linalg.matrix_power(self._require_mat(), n))

    # ── Comparison ──

    def __eq__(self, other) -> np.ndarray:
        return self._require_mat() == _unwrap(other)

    # ── Unary operations / properties ──

    @property
    def T(self) -> MatrixRepr:
        """Transpose."""
        result = self._require_mat().T
        if self._tracking:
            return self._symbolic_result(result, Transpose(self.as_expression()))
        return self._wrap(result)

    @property
    def H(self) -> MatrixRepr:
        """Conjugate transpose (Hermitian adjoint). Ket becomes bra and vice versa."""
        result = self._require_mat().conj().T
        new_kind = self.kind
        if self.kind == "ket":
            new_kind = "bra"
        elif self.kind == "bra":
            new_kind = "ket"
        if self._tracking:
            return self._symbolic_result(result, Adjoint(self.as_expression()), kind=new_kind)
        return MatrixRepr(result, algebra=self.algebra, mode=self.mode, basis=self.basis, kind=new_kind)

    def conj(self) -> MatrixRepr:
        """Element-wise complex conjugate."""
        result = self._require_mat().conj()
        if self._tracking:
            return self._symbolic_result(result, ConjugateMatrix(self.as_expression()))
        return self._wrap(result)

    def trace(self) -> complex:
        """Matrix trace."""
        return np.trace(self._require_mat())

    def det(self) -> complex:
        """Matrix determinant."""
        return np.linalg.det(self._require_mat())

    def inv(self) -> MatrixRepr:
        """Matrix inverse."""
        result = np.linalg.inv(self._require_mat())
        if self._tracking:
            return self._symbolic_result(result, MatrixInverse(self.as_expression()))
        return self._wrap(result)

    # ── Basis change ──

    def to_basis(self, target: str) -> MatrixRepr:
        """Transform to a named basis via similarity: M' = S M S†.

        Supported bases for Cl(1,3) / Cl(3,1) 4×4 matrices:
            ``"dirac"``, ``"weyl"``, ``"majorana"``

        Args:
            target: The target basis name.

        Returns:
            A new MatrixRepr in the target basis with .basis set.

        Raises:
            TypeError: If the matrix is not 4×4 from Cl(1,3) or Cl(3,1).
            ValueError: If target is not a recognized basis name.
        """
        from .bases import DIRAC_BASES, TRANSFORMS

        mat = self._require_mat()

        if self.mode == "quaternion":
            raise TypeError(
                "to_basis() is not supported for quaternion-mode matrices. "
                "The quaternion-block basis is a separate representation, not a Dirac basis variant."
            )

        if target not in DIRAC_BASES:
            raise ValueError(f"Unknown basis {target!r}; use 'dirac', 'weyl', or 'majorana'.")

        if mat.shape not in ((4, 4), (4, 1), (1, 4)):
            raise TypeError(f"to_basis({target!r}) requires a 4-dim Dirac representation, got {mat.shape}.")

        # Determine source basis
        source = self.basis or "dirac"

        # No-op if already in target basis
        if source == target:
            return self

        if source not in DIRAC_BASES:
            raise TypeError(f"Cannot change basis from {source!r}; not a recognized Dirac basis.")

        S = TRANSFORMS[(source, target)]
        if self.kind == "ket":
            new_mat = S @ mat
        elif self.kind == "bra":
            new_mat = mat @ S.conj().T
        else:
            new_mat = S @ mat @ S.conj().T

        if self._tracking:
            expression = MatrixBasisChange(self.as_expression(), target, value=new_mat)
            return self._symbolic_result(new_mat, expression, basis=target)

        return MatrixRepr(new_mat, algebra=self.algebra, mode=self.mode, basis=target, kind=self.kind)

    # ── Factory methods ──

    @classmethod
    def identity(cls, k: int, *, dtype=complex, algebra=None, mode: str = "compact") -> MatrixRepr:
        """k×k identity matrix."""
        return cls(np.eye(k, dtype=dtype), algebra=algebra, mode=mode)

    @classmethod
    def zeros(cls, shape: tuple[int, int], *, dtype=complex, algebra=None, mode: str = "compact") -> MatrixRepr:
        """Zero matrix of given shape."""
        return cls(np.zeros(shape, dtype=dtype), algebra=algebra, mode=mode)

    def kron(self, other: MatrixRepr) -> MatrixRepr:
        """Kronecker (tensor) product."""
        result = np.kron(self._require_mat(), _unwrap(other))
        if self._is_symbolic_with(other):
            return self._symbolic_result(result, KroneckerProduct(self.as_expression(), self._operand_expr(other)))
        return self._wrap(result)

    # ── Numpy interop ──

    def __array__(self, dtype=None, copy=None):
        if dtype is not None:
            return np.array(self.mat, dtype=dtype)
        return self.mat

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """Intercept numpy ufuncs to keep results wrapped in MatrixRepr.

        This ensures operations like np.add(M1, M2), np.matmul(M1, M2),
        and np.conj(M) return MatrixRepr instances rather than bare arrays.
        """
        if method != "__call__":
            return NotImplemented

        # Unwrap all MatrixRepr inputs
        unwrapped = [_unwrap(x) for x in inputs]

        # Find the first MatrixRepr for metadata inheritance
        source = None
        for x in inputs:
            if isinstance(x, MatrixRepr):
                source = x
                break

        # Handle 'out' keyword
        out = kwargs.get("out")
        if out is not None:
            kwargs["out"] = tuple(_unwrap(o) if isinstance(o, MatrixRepr) else o for o in out)

        result = ufunc(*unwrapped, **kwargs)

        # Wrap result if it's a matrix-shaped array
        if isinstance(result, np.ndarray) and result.ndim == 2 and source is not None:
            return source._wrap(result)
        return result

    # ── Rendering ──

    def _body_latex(self) -> str:
        if self.mode == "quaternion":
            qm = self.quat
            lines = []
            for row in qm:
                cells = [q.latex() for q in row]
                lines.append(" & ".join(cells))
            return " \\\\\n".join(lines)
        rows, cols = self.mat.shape
        lines = []
        for i in range(rows):
            cells = [_fmt(self.mat[i, j]) for j in range(cols)]
            lines.append(" & ".join(cells))
        return " \\\\\n".join(lines)

    def latex(self, wrap: str | None = None) -> str:
        """Return raw LaTeX for the matrix.

        Args:
            wrap: ``"$"`` for inline, ``"$$"`` for display, or ``None`` for raw.
        """
        display_policy = getattr(getattr(self.algebra, "presentation", None), "display", None)
        if wrap is None and getattr(display_policy, "content", None) in {"expr", "full"}:
            return self.display().latex()
        body = self._body_latex()
        raw = f"\\begin{{pmatrix}}\n{body}\n\\end{{pmatrix}}"
        if self._symbolic_name is not None:
            raw = f"{self._symbolic_name.latex} \\quad = \\quad {raw}"
        if wrap == "$":
            return f"${raw}$"
        if wrap == "$$":
            return f"$$\n{raw}\n$$"
        return raw

    def display(self, compact: bool = False) -> _MatrixDisplayResult:
        """Return a LaTeX-renderable object showing name = expression = value."""
        parts = []
        value_latex = self.eval()._matrix_latex_raw()
        if self._symbolic_name is not None:
            parts.append(self._symbolic_name.latex)
        if self._tracking and self._expression is not None:
            expr_latex = self._expression.latex()
            if expr_latex not in parts and expr_latex != value_latex:
                parts.append(expr_latex)
        if value_latex not in parts:
            parts.append(value_latex)

        sep = " = " if compact else " \\quad = \\quad "
        return _MatrixDisplayResult(parts, sep, self.eval())

    def _matrix_latex_raw(self) -> str:
        body = self._body_latex()
        return f"\\begin{{pmatrix}}\n{body}\n\\end{{pmatrix}}"

    def _repr_latex_(self) -> str:
        return f"${self.latex()}$"

    def __repr__(self) -> str:
        if self.mode == "quaternion":
            rows, cols = self.mat.shape
            return f"MatrixRepr({rows // 2}×{cols // 2}, quaternion)"
        return repr(self.mat)

    def __str__(self) -> str:
        if self.mode == "quaternion":
            return repr(self)
        return str(self.mat)


# Backward compatibility alias
QuatMatrixRepr = MatrixRepr
