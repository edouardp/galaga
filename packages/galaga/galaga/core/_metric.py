"""Exterior metric and antimetric matrices derived from a vector Gram matrix."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ._metadata import DimensionMetadata, set_bit_indices


def exterior_metric_matrix(
    gram: NDArray[np.float64],
    metadata: DimensionMetadata,
) -> NDArray[np.float64]:
    """Return the compound-matrix extension ``ΛG`` in bitmask order."""
    if np.array_equal(gram, np.diag(np.diag(gram))):
        diagonal = np.ones(metadata.dim, dtype=np.float64)
        basis_squares = np.diag(gram)
        for bitmask in range(1, metadata.dim):
            factor = 1.0
            for index in set_bit_indices(bitmask):
                factor *= basis_squares[index]
            diagonal[bitmask] = factor
        result = np.diag(diagonal)
    else:
        result = np.zeros((metadata.dim, metadata.dim), dtype=np.float64)
        for masks in _grade_bitmasks(metadata):
            for row_position, row_mask in enumerate(masks):
                rows = set_bit_indices(row_mask)
                for column_mask in masks[row_position:]:
                    columns = set_bit_indices(column_mask)
                    value = _minor_determinant(gram, rows, columns)
                    result[row_mask, column_mask] = value
                    result[column_mask, row_mask] = value
    result.setflags(write=False)
    return result


def exterior_antimetric_matrix(
    gram: NDArray[np.float64],
    metadata: DimensionMetadata,
) -> NDArray[np.float64]:
    """Return the signed complementary-compound extension of ``G``.

    For invertible ``G`` this equals ``det(G) * inverse(ΛG)``. Constructing it
    from complementary minors keeps it defined for degenerate metrics.
    """
    if np.array_equal(gram, np.diag(np.diag(gram))):
        diagonal = np.ones(metadata.dim, dtype=np.float64)
        basis_squares = np.diag(gram)
        full_mask = metadata.dim - 1
        for bitmask in range(metadata.dim):
            factor = 1.0
            for index in set_bit_indices(full_mask ^ bitmask):
                factor *= basis_squares[index]
            diagonal[bitmask] = factor
        result = np.diag(diagonal)
    else:
        result = np.zeros((metadata.dim, metadata.dim), dtype=np.float64)
        full_mask = metadata.dim - 1
        signs = metadata.right_complement_sign
        for masks in _grade_bitmasks(metadata):
            for row_position, row_mask in enumerate(masks):
                rows = set_bit_indices(full_mask ^ row_mask)
                for column_mask in masks[row_position:]:
                    columns = set_bit_indices(full_mask ^ column_mask)
                    value = int(signs[row_mask]) * int(signs[column_mask]) * _minor_determinant(gram, rows, columns)
                    result[row_mask, column_mask] = value
                    result[column_mask, row_mask] = value
    result.setflags(write=False)
    return result


def _grade_bitmasks(metadata: DimensionMetadata) -> tuple[list[int], ...]:
    return tuple([int(bitmask) for bitmask in np.flatnonzero(mask)] for mask in metadata.grade_masks)


def _minor_determinant(
    matrix: NDArray[np.float64],
    rows: list[int],
    columns: list[int],
) -> float:
    size = len(rows)
    if size == 0:
        return 1.0
    if size == 1:
        return float(matrix[rows[0], columns[0]])
    if size == 2:
        return float(
            matrix[rows[0], columns[0]] * matrix[rows[1], columns[1]]
            - matrix[rows[0], columns[1]] * matrix[rows[1], columns[0]]
        )
    return float(np.linalg.det(matrix[np.ix_(rows, columns)]))
