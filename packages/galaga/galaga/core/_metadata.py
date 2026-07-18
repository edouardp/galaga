"""Metric-independent metadata for exterior bitmask bases."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class DimensionMetadata:
    """Immutable exterior-basis data shared by algebras of one dimension."""

    n: int
    dim: int
    blade_grades: NDArray[np.uint8]
    grade_masks: tuple[NDArray[np.bool_], ...]
    reverse_sign: NDArray[np.int8]
    involute_sign: NDArray[np.int8]
    conjugate_sign: NDArray[np.int8]
    antireverse_sign: NDArray[np.int8]
    wedge_factor: NDArray[np.int8]
    complement_index: NDArray[np.unsignedinteger[Any]]
    left_complement_sign: NDArray[np.int8]
    right_complement_sign: NDArray[np.int8]


@cache
def dimension_metadata(n: int) -> DimensionMetadata:
    """Return the one cached metadata object for vector dimension ``n``."""
    if n < 0:
        raise ValueError("vector dimension must be non-negative")

    dim = 1 << n
    blade_grades = np.fromiter(
        (bitmask.bit_count() for bitmask in range(dim)),
        dtype=np.uint8,
        count=dim,
    )
    grade_masks = tuple(blade_grades == grade for grade in range(n + 1))
    reverse_sign = np.fromiter(
        ((-1) ** (grade * (grade - 1) // 2) for grade in map(int, blade_grades)),
        dtype=np.int8,
        count=dim,
    )
    involute_sign = np.where(blade_grades % 2 == 0, 1, -1).astype(np.int8)
    conjugate_sign = reverse_sign * involute_sign
    antireverse_sign = np.fromiter(
        ((-1) ** ((n - grade) * (n - grade - 1) // 2) for grade in map(int, blade_grades)),
        dtype=np.int8,
        count=dim,
    )

    wedge_factor = np.zeros((dim, dim), dtype=np.int8)
    for left in range(dim):
        for right in range(dim):
            if left & right == 0:
                wedge_factor[left, right] = sign_of_reorder(left, right)

    mask_dtype = bitmask_dtype(dim)
    full_mask = dim - 1
    complement_index = np.fromiter(
        (full_mask ^ bitmask for bitmask in range(dim)),
        dtype=mask_dtype,
        count=dim,
    )
    right_complement_sign = np.fromiter(
        (wedge_factor[bitmask, full_mask ^ bitmask] for bitmask in range(dim)),
        dtype=np.int8,
        count=dim,
    )
    left_complement_sign = np.fromiter(
        (wedge_factor[full_mask ^ bitmask, bitmask] for bitmask in range(dim)),
        dtype=np.int8,
        count=dim,
    )

    arrays = (
        blade_grades,
        *grade_masks,
        reverse_sign,
        involute_sign,
        conjugate_sign,
        antireverse_sign,
        wedge_factor,
        complement_index,
        left_complement_sign,
        right_complement_sign,
    )
    for array in arrays:
        array.setflags(write=False)

    return DimensionMetadata(
        n=n,
        dim=dim,
        blade_grades=blade_grades,
        grade_masks=grade_masks,
        reverse_sign=reverse_sign,
        involute_sign=involute_sign,
        conjugate_sign=conjugate_sign,
        antireverse_sign=antireverse_sign,
        wedge_factor=wedge_factor,
        complement_index=complement_index,
        left_complement_sign=left_complement_sign,
        right_complement_sign=right_complement_sign,
    )


def bitmask_dtype(dim: int) -> np.dtype[np.unsignedinteger[Any]]:
    """Return the smallest unsigned dtype able to store ``dim - 1``."""
    if dim <= 1 << 8:
        return np.dtype(np.uint8)
    if dim <= 1 << 16:
        return np.dtype(np.uint16)
    if dim <= 1 << 32:
        return np.dtype(np.uint32)
    return np.dtype(np.uint64)


def set_bit_indices(bitmask: int) -> list[int]:
    """Return ascending indices of the set bits in ``bitmask``."""
    result: list[int] = []
    while bitmask:
        lowest = bitmask & -bitmask
        result.append(lowest.bit_length() - 1)
        bitmask ^= lowest
    return result


def sign_of_reorder(left: int, right: int) -> int:
    """Return the sign needed to merge two ascending blade index lists."""
    swaps = 0
    shifted = left >> 1
    while shifted:
        swaps += (shifted & right).bit_count()
        shifted >>= 1
    return 1 if swaps % 2 == 0 else -1
