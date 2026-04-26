"""LaTeX rendering for matrix representations.

Provides ``MatrixRepr``, a single wrapper around matrix data that
supports ``.latex()`` and ``._repr_latex_()`` so it works in
galaga_marimo t-strings and Jupyter notebooks.

Handles complex matrices (from left-regular and compact modes) and
quaternion matrices (from ``to_quaternion_matrix``).
"""

from __future__ import annotations

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


class MatrixRepr:
    """A matrix with LaTeX rendering support.

    Works in galaga_marimo t-strings via the ``.latex()`` protocol,
    and in Jupyter via ``_repr_latex_()``.

    Handles two data formats:

    - **numpy array** (real or complex): from ``to_matrix``
    - **list-of-lists of Quat**: from ``to_quaternion_matrix``

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
        if isinstance(data, np.ndarray):
            self.mat = data
            self._qmat = None
        elif isinstance(data, list):
            self.mat = None
            self._qmat = data
            mode = "quaternion"
        else:
            self.mat = np.asarray(data)
            self._qmat = None
        self.label = label
        self.algebra = algebra
        self.mode = mode

    @property
    def mv(self):
        """Convert back to a galaga Multivector."""
        if self.algebra is None:
            raise ValueError("No algebra reference; pass algebra= when creating MatrixRepr")
        from galaga_matrix.matrix import from_matrix

        if self.mat is not None:
            return from_matrix(self.algebra, self.mat, mode=self.mode)
        raise ValueError("Cannot convert quaternion matrix back to MV; use compact or left-regular mode")

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

    def __array__(self, dtype=None, copy=None):
        if self.mat is None:
            raise TypeError("Quaternion matrix cannot be converted to numpy array")
        if dtype is not None:
            return np.array(self.mat, dtype=dtype)
        return self.mat


# Backward compatibility alias
QuatMatrixRepr = MatrixRepr
