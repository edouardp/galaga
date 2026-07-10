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

from galaga.symbolic_core import Add, Neg, Scalar, ScalarDiv, ScalarMul, Sub, Sym, SymbolicNamingMixin

from .expr import (
    Adjoint,
    ConjugateMatrix,
    KroneckerProduct,
    MatMul,
    MatrixBasisChange,
    MatrixElementwiseMul,
    MatrixInverse,
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


class MatrixRepr(SymbolicNamingMixin):
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
        self._init_symbolic_state()
        if isinstance(data, MatrixRepr):
            # Unwrap: copy the underlying matrix, inherit metadata if not overridden
            self.mat = data.mat.copy()
            self.algebra = algebra if algebra is not None else data.algebra
            self.mode = mode if mode != "left-regular" else data.mode
            self.basis = basis if basis is not None else data.basis
            self.kind = kind if kind != "operator" else data.kind
            self._name = data._name
            self._name_latex = data._name_latex
            self._name_unicode = data._name_unicode
            self._is_symbolic = data._is_symbolic
            self._expr = data._expr
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
        copy._name = overrides.get("_name", self._name)
        copy._name_latex = overrides.get("_name_latex", self._name_latex)
        copy._name_unicode = overrides.get("_name_unicode", self._name_unicode)
        copy._is_symbolic = overrides.get("_is_symbolic", self._is_symbolic)
        copy._expr = overrides.get("_expr", self._expr)
        return copy

    def _make_symbolic_leaf(self) -> Sym:
        return Sym(
            self.eval(),
            self._name_unicode or self._name,
            name_latex=self._name_latex,
            name_ascii=self._name,
        )

    def _to_expr(self):
        """Convert this matrix wrapper to a symbolic expression node."""
        if self._name is not None:
            inner = self._expr if self._expr is not None and not isinstance(self._expr, Sym) else None
            return Sym(
                self.eval(),
                self._name_unicode or self._name,
                name_latex=self._name_latex,
                name_ascii=self._name,
                inner_expr=inner,
            )
        if self._expr is not None:
            return self._expr
        return Sym(self.eval(), str(self), name_latex=self.latex())

    @property
    def expr(self):
        """The symbolic expression tree, if this matrix is symbolic."""
        return self._expr

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
        wrapped._is_symbolic = True
        wrapped._expr = expr
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
            return value._to_expr()
        if _is_scalar(value):
            return Scalar(value)
        return MatrixRepr(
            np.asarray(value),
            algebra=self.algebra,
            mode=self.mode,
            basis=self.basis,
            kind="operator",
        )._to_expr()

    def _is_symbolic_with(self, other=None) -> bool:
        return self._is_symbolic or (isinstance(other, MatrixRepr) and other._is_symbolic)

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
                MatMul(self._to_expr(), self._operand_expr(other)),
                kind=result_kind,
            )
        return MatrixRepr(result, algebra=self.algebra, mode=self.mode, basis=self.basis, kind=result_kind)

    def __rmatmul__(self, other) -> MatrixRepr:
        if self._is_symbolic:
            return self._symbolic_result(
                _unwrap(other) @ self._require_mat(), MatMul(self._operand_expr(other), self._to_expr())
            )
        return self._wrap(_unwrap(other) @ self._require_mat())

    def __add__(self, other) -> MatrixRepr:
        result = self._require_mat() + _unwrap(other)
        if self._is_symbolic_with(other):
            return self._symbolic_result(result, Add(self._to_expr(), self._operand_expr(other)))
        return self._wrap(result)

    def __radd__(self, other) -> MatrixRepr:
        result = _unwrap(other) + self._require_mat()
        if self._is_symbolic:
            return self._symbolic_result(result, Add(self._operand_expr(other), self._to_expr()))
        return self._wrap(result)

    def __sub__(self, other) -> MatrixRepr:
        result = self._require_mat() - _unwrap(other)
        if self._is_symbolic_with(other):
            return self._symbolic_result(result, Sub(self._to_expr(), self._operand_expr(other)))
        return self._wrap(result)

    def __rsub__(self, other) -> MatrixRepr:
        result = _unwrap(other) - self._require_mat()
        if self._is_symbolic:
            return self._symbolic_result(result, Sub(self._operand_expr(other), self._to_expr()))
        return self._wrap(result)

    def __mul__(self, other) -> MatrixRepr:
        result = self._require_mat() * _unwrap(other)
        if self._is_symbolic_with(other):
            if _is_scalar(other):
                expr = ScalarMul(other, self._to_expr())
            else:
                expr = MatrixElementwiseMul(self._to_expr(), self._operand_expr(other))
            return self._symbolic_result(result, expr)
        return self._wrap(result)

    def __rmul__(self, other) -> MatrixRepr:
        result = _unwrap(other) * self._require_mat()
        if self._is_symbolic:
            if _is_scalar(other):
                expr = ScalarMul(other, self._to_expr())
            else:
                expr = MatrixElementwiseMul(self._operand_expr(other), self._to_expr())
            return self._symbolic_result(result, expr)
        return self._wrap(result)

    def __truediv__(self, other) -> MatrixRepr:
        result = self._require_mat() / _unwrap(other)
        if self._is_symbolic:
            if _is_scalar(other):
                expr = ScalarDiv(self._to_expr(), other)
            else:
                expr = MatrixElementwiseMul(self._to_expr(), self._operand_expr(1 / _unwrap(other)))
            return self._symbolic_result(result, expr)
        return self._wrap(result)

    def __neg__(self) -> MatrixRepr:
        result = -self._require_mat()
        if self._is_symbolic:
            return self._symbolic_result(result, Neg(self._to_expr()))
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
        if self._is_symbolic:
            return self._symbolic_result(result, Transpose(self._to_expr()))
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
        if self._is_symbolic:
            return self._symbolic_result(result, Adjoint(self._to_expr()), kind=new_kind)
        return MatrixRepr(result, algebra=self.algebra, mode=self.mode, basis=self.basis, kind=new_kind)

    def conj(self) -> MatrixRepr:
        """Element-wise complex conjugate."""
        result = self._require_mat().conj()
        if self._is_symbolic:
            return self._symbolic_result(result, ConjugateMatrix(self._to_expr()))
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
        if self._is_symbolic:
            return self._symbolic_result(result, MatrixInverse(self._to_expr()))
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

        if self._is_symbolic:
            return self._symbolic_result(new_mat, MatrixBasisChange(self._to_expr(), target), basis=target)

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
            return self._symbolic_result(result, KroneckerProduct(self._to_expr(), self._operand_expr(other)))
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
        if wrap is None and getattr(self.algebra, "_display_mode", False):
            return self.display().latex()
        body = self._body_latex()
        raw = f"\\begin{{pmatrix}}\n{body}\n\\end{{pmatrix}}"
        if self._name_latex:
            raw = f"{self._name_latex} \\quad = \\quad {raw}"
        if wrap == "$":
            return f"${raw}$"
        if wrap == "$$":
            return f"$$\n{raw}\n$$"
        return raw

    def display(self, compact: bool = False) -> _MatrixDisplayResult:
        """Return a LaTeX-renderable object showing name = expression = value."""
        parts = []
        value_latex = self.eval()._matrix_latex_raw()
        if self._name_latex is not None:
            parts.append(self._name_latex)
        if self._is_symbolic and self._expr is not None:
            expr_latex = self._expr.latex()
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
