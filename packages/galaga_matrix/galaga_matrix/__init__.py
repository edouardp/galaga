"""galaga_matrix — Matrix representations for galaga Clifford algebras."""

from .matrix import (
    Quat,
    from_matrix,
    from_spinor_column,
    from_spinor_matrix,
    from_spinor_quaternion,
    to_matrix,
    to_spinor_column,
    to_spinor_matrix,
    to_spinor_quaternion,
)
from .repr import MatrixRepr, QuatMatrixRepr

__all__ = [
    "from_matrix",
    "from_spinor_column",
    "from_spinor_matrix",
    "from_spinor_quaternion",
    "MatrixRepr",
    "Quat",
    "QuatMatrixRepr",
    "to_matrix",
    "to_spinor_column",
    "to_spinor_matrix",
    "to_spinor_quaternion",
]
