"""LaTeX rendering and transparent numpy proxy for matrix representations.

Provides ``MatrixRepr``, a wrapper around matrix data that:
- Supports ``.latex()`` and ``._repr_latex_()`` for notebooks
- Forwards all arithmetic operations (matmul, add, sub, etc.)
- Preserves metadata (label, algebra, mode) through operations
- Acts as a transparent numpy proxy via ``__array_ufunc__``

Handles complex matrices (from left-regular and compact modes) and
quaternion matrices (from ``to_matrix(mv, mode="quaternion")``).
"""

from __future__ import annotations

from typing import Any

import numpy as np


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
        label: Optional label shown as ``label = \\begin{pmatrix}...``.
        algebra: Optional reference to the source Algebra (enables ``.mv``).
        mode: The representation mode (``"left-regular"``, ``"compact"``,
              or ``"quaternion"``).
    """

    def __init__(
        self,
        data,
        label: str | None = None,
        algebra=None,
        mode: str = "left-regular",
    ):
        if isinstance(data, MatrixRepr):
            # Unwrap: copy the underlying matrix, inherit metadata if not overridden
            self.mat = data.mat.copy() if data.mat is not None else None
            self._qmat = [row[:] for row in data._qmat] if data._qmat is not None else None
            if self._qmat is not None:
                mode = "quaternion"
            self.label = label if label is not None else data.label
            self.algebra = algebra if algebra is not None else data.algebra
            self.mode = mode if mode != "left-regular" else data.mode
        elif isinstance(data, np.ndarray):
            self.mat = data
            self._qmat = None
        elif isinstance(data, list):
            self.mat = None
            self._qmat = data
            mode = "quaternion"
        else:
            self.mat = np.asarray(data)
            self._qmat = None
        if not isinstance(data, MatrixRepr):
            self.label = label
            self.algebra = algebra
            self.mode = mode

    def _wrap(self, result: np.ndarray, label: str | None = None) -> MatrixRepr:
        """Wrap a numpy result in a new MatrixRepr, inheriting algebra/mode."""
        return MatrixRepr(result, label=label, algebra=self.algebra, mode=self.mode)

    def _require_mat(self) -> np.ndarray:
        """Get the numpy array or raise if quaternion."""
        if self.mat is None:
            raise TypeError("Operation not supported on quaternion matrix representations")
        return self.mat

    # ── Conversion ──

    @property
    def mv(self):
        """Convert back to a galaga Multivector."""
        if self.algebra is None:
            raise ValueError("No algebra reference; pass algebra= when creating MatrixRepr")
        from galaga_matrix.matrix import from_matrix

        if self.mat is not None:
            return from_matrix(self.algebra, self.mat, mode=self.mode)
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

    # ── Arithmetic operators ──

    def __matmul__(self, other) -> MatrixRepr:
        return self._wrap(self._require_mat() @ _unwrap(other))

    def __rmatmul__(self, other) -> MatrixRepr:
        return self._wrap(_unwrap(other) @ self._require_mat())

    def __add__(self, other) -> MatrixRepr:
        return self._wrap(self._require_mat() + _unwrap(other))

    def __radd__(self, other) -> MatrixRepr:
        return self._wrap(_unwrap(other) + self._require_mat())

    def __sub__(self, other) -> MatrixRepr:
        return self._wrap(self._require_mat() - _unwrap(other))

    def __rsub__(self, other) -> MatrixRepr:
        return self._wrap(_unwrap(other) - self._require_mat())

    def __mul__(self, other) -> MatrixRepr:
        return self._wrap(self._require_mat() * _unwrap(other))

    def __rmul__(self, other) -> MatrixRepr:
        return self._wrap(_unwrap(other) * self._require_mat())

    def __truediv__(self, other) -> MatrixRepr:
        return self._wrap(self._require_mat() / _unwrap(other))

    def __neg__(self) -> MatrixRepr:
        return self._wrap(-self._require_mat())

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
        return self._wrap(self._require_mat().T)

    @property
    def H(self) -> MatrixRepr:
        """Conjugate transpose (Hermitian adjoint)."""
        return self._wrap(self._require_mat().conj().T)

    def conj(self) -> MatrixRepr:
        """Element-wise complex conjugate."""
        return self._wrap(self._require_mat().conj())

    def trace(self) -> complex:
        """Matrix trace."""
        return np.trace(self._require_mat())

    def det(self) -> complex:
        """Matrix determinant."""
        return np.linalg.det(self._require_mat())

    def inv(self) -> MatrixRepr:
        """Matrix inverse."""
        return self._wrap(np.linalg.inv(self._require_mat()))

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
        return self._wrap(np.kron(self._require_mat(), _unwrap(other)))

    # ── Numpy interop ──

    def __array__(self, dtype=None, copy=None):
        if self.mat is None:
            raise TypeError("Quaternion matrix cannot be converted to numpy array")
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
        if self._qmat is not None:
            lines = []
            for row in self._qmat:
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
        body = self._body_latex()
        raw = f"\\begin{{pmatrix}}\n{body}\n\\end{{pmatrix}}"
        if self.label:
            raw = f"{self.label} = {raw}"
        if wrap == "$":
            return f"${raw}$"
        if wrap == "$$":
            return f"$$\n{raw}\n$$"
        return raw

    def _repr_latex_(self) -> str:
        return f"${self.latex()}$"

    def __repr__(self) -> str:
        if self._qmat is not None:
            r = len(self._qmat)
            c = len(self._qmat[0]) if r else 0
            return f"MatrixRepr({r}×{c}, quaternion)"
        return repr(self.mat)

    def __str__(self) -> str:
        if self._qmat is not None:
            return repr(self)
        return str(self.mat)


# Backward compatibility alias
QuatMatrixRepr = MatrixRepr
