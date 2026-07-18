"""Geometric-product backends for diagonal and general Gram matrices."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from threading import RLock
from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray

from ._metadata import (
    DimensionMetadata,
    bitmask_dtype,
    set_bit_indices,
    sign_of_reorder,
)

GradeSelector = Callable[[int, int], int | None]

_DEFAULT_PACKED_BYTE_BUDGET = 64 * 1024 * 1024
_DEFAULT_LAZY_CACHE_BYTE_BUDGET = 64 * 1024 * 1024


class ProductBackend(Protocol):
    """Private backend contract used by the public numeric algebra."""

    name: str

    def multiply(
        self,
        left: NDArray[np.float64],
        right: NDArray[np.float64],
    ) -> NDArray[np.float64]: ...

    def grade_selected_product(
        self,
        left: NDArray[np.float64],
        right: NDArray[np.float64],
        selector: GradeSelector,
    ) -> NDArray[np.float64]: ...

    def left_action(self, bitmask: int) -> NDArray[np.float64]: ...


class DiagonalProductBackend:
    """Compact monomial products for an exactly diagonal Gram matrix."""

    name = "diagonal"

    def __init__(
        self,
        basis_squares: NDArray[np.float64],
        metadata: DimensionMetadata,
    ) -> None:
        dim = metadata.dim
        outputs = np.empty((dim, dim), dtype=bitmask_dtype(dim))
        factors = np.empty((dim, dim), dtype=np.float64)
        for left in range(dim):
            for right in range(dim):
                outputs[left, right] = left ^ right
                factor = float(sign_of_reorder(left, right))
                repeated = left & right
                while repeated:
                    lowest = repeated & -repeated
                    factor *= basis_squares[lowest.bit_length() - 1]
                    repeated ^= lowest
                factors[left, right] = factor
        outputs.setflags(write=False)
        factors.setflags(write=False)

        self._dim = dim
        self._grades = metadata.blade_grades
        self._outputs = outputs
        self._factors = factors

    def multiply(
        self,
        left: NDArray[np.float64],
        right: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        output = np.zeros(self._dim, dtype=np.float64)
        for left_mask in np.flatnonzero(left):
            outputs = self._outputs[left_mask]
            output[outputs] += left[left_mask] * right * self._factors[left_mask]
        return output

    def grade_selected_product(
        self,
        left: NDArray[np.float64],
        right: NDArray[np.float64],
        selector: GradeSelector,
    ) -> NDArray[np.float64]:
        output = np.zeros(self._dim, dtype=np.float64)
        right_nonzero = np.flatnonzero(right)
        for left_mask in np.flatnonzero(left):
            left_grade = int(self._grades[left_mask])
            for right_mask in right_nonzero:
                target = selector(left_grade, int(self._grades[right_mask]))
                if target is None:
                    continue
                output_mask = int(self._outputs[left_mask, right_mask])
                if self._grades[output_mask] == target:
                    output[output_mask] += left[left_mask] * right[right_mask] * self._factors[left_mask, right_mask]
        return output

    def left_action(self, bitmask: int) -> NDArray[np.float64]:
        action = np.zeros((self._dim, self._dim), dtype=np.float64)
        action[self._outputs[bitmask], np.arange(self._dim)] = self._factors[bitmask]
        action.setflags(write=False)
        return action


@dataclass(frozen=True, slots=True)
class _SparseLeftAction:
    """One sparse left-action matrix stored by columns."""

    offsets: NDArray[np.intp]
    outputs: NDArray[np.unsignedinteger[Any]]
    factors: NDArray[np.float64]

    def terms(
        self,
        input_mask: int,
    ) -> tuple[NDArray[np.unsignedinteger[Any]], NDArray[np.float64]]:
        start = int(self.offsets[input_mask])
        stop = int(self.offsets[input_mask + 1])
        return self.outputs[start:stop], self.factors[start:stop]


class PackedProductBackend:
    """CSR-like sparse expansions for products in a general Gram basis."""

    name = "packed"

    def __init__(
        self,
        gram: NDArray[np.float64],
        metadata: DimensionMetadata,
    ) -> None:
        actions = _build_sparse_left_actions(gram, metadata)
        offsets, outputs, factors = _pack_left_actions(actions, metadata.dim)
        self._dim = metadata.dim
        self._grades = metadata.blade_grades
        self._offsets = offsets
        self._outputs = outputs
        self._factors = factors

    def _terms(
        self,
        left_mask: int,
        right_mask: int,
    ) -> tuple[NDArray[np.unsignedinteger[Any]], NDArray[np.float64]]:
        row = left_mask * self._dim + right_mask
        start = int(self._offsets[row])
        stop = int(self._offsets[row + 1])
        return self._outputs[start:stop], self._factors[start:stop]

    def multiply(
        self,
        left: NDArray[np.float64],
        right: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        output = np.zeros(self._dim, dtype=np.float64)
        right_nonzero = np.flatnonzero(right)
        for left_mask in np.flatnonzero(left):
            for right_mask in right_nonzero:
                outputs, factors = self._terms(int(left_mask), int(right_mask))
                output[outputs] += left[left_mask] * right[right_mask] * factors
        return output

    def grade_selected_product(
        self,
        left: NDArray[np.float64],
        right: NDArray[np.float64],
        selector: GradeSelector,
    ) -> NDArray[np.float64]:
        output = np.zeros(self._dim, dtype=np.float64)
        right_nonzero = np.flatnonzero(right)
        for left_mask in np.flatnonzero(left):
            left_grade = int(self._grades[left_mask])
            for right_mask in right_nonzero:
                target = selector(left_grade, int(self._grades[right_mask]))
                if target is None:
                    continue
                outputs, factors = self._terms(int(left_mask), int(right_mask))
                selected = self._grades[outputs] == target
                selected_outputs = outputs[selected]
                output[selected_outputs] += left[left_mask] * right[right_mask] * factors[selected]
        return output

    def left_action(self, bitmask: int) -> NDArray[np.float64]:
        action = np.zeros((self._dim, self._dim), dtype=np.float64)
        for input_mask in range(self._dim):
            outputs, factors = self._terms(bitmask, input_mask)
            action[outputs, input_mask] = factors
        action.setflags(write=False)
        return action


class LazyProductBackend:
    """Build and cache general-Gram blade actions only when requested."""

    name = "lazy"

    def __init__(
        self,
        gram: NDArray[np.float64],
        metadata: DimensionMetadata,
        *,
        cache_byte_budget: int = _DEFAULT_LAZY_CACHE_BYTE_BUDGET,
    ) -> None:
        if not isinstance(cache_byte_budget, int) or cache_byte_budget < 0:
            raise ValueError("cache_byte_budget must be a non-negative integer")
        self._dim = metadata.dim
        self._grades = metadata.blade_grades
        self._gram = gram
        self._metadata = metadata
        self._mask_dtype = bitmask_dtype(metadata.dim)
        self._vector_terms = _build_vector_terms(gram, metadata)
        self._base_actions = _build_base_left_actions(
            self._vector_terms,
            metadata,
            self._mask_dtype,
        )
        self._cache: OrderedDict[int, _SparseLeftAction] = OrderedDict()
        self._cache_bytes = 0
        self._cache_byte_budget = cache_byte_budget
        self._cache_lock = RLock()

    @property
    def cache_info(self) -> tuple[int, int, int]:
        """Return ``(entries, bytes, byte_budget)`` for diagnostics."""
        with self._cache_lock:
            return (
                len(self._cache),
                self._cache_bytes,
                self._cache_byte_budget,
            )

    def _action(self, bitmask: int) -> _SparseLeftAction:
        base_action = self._base_actions.get(bitmask)
        if base_action is not None:
            return base_action

        with self._cache_lock:
            cached = self._cache.get(bitmask)
            if cached is not None:
                self._cache.move_to_end(bitmask)
                return cached

            action = _build_higher_left_action(
                bitmask,
                self._gram,
                self._metadata,
                self._vector_terms,
                self._action,
                self._mask_dtype,
            )
            action_bytes = _sparse_action_bytes(action)
            if action_bytes <= self._cache_byte_budget:
                while self._cache and self._cache_bytes + action_bytes > self._cache_byte_budget:
                    _, evicted = self._cache.popitem(last=False)
                    self._cache_bytes -= _sparse_action_bytes(evicted)
                self._cache[bitmask] = action
                self._cache_bytes += action_bytes
            return action

    def multiply(
        self,
        left: NDArray[np.float64],
        right: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        output = np.zeros(self._dim, dtype=np.float64)
        right_nonzero = np.flatnonzero(right)
        for left_mask in np.flatnonzero(left):
            action = self._action(int(left_mask))
            for right_mask in right_nonzero:
                outputs, factors = action.terms(int(right_mask))
                output[outputs] += left[left_mask] * right[right_mask] * factors
        return output

    def grade_selected_product(
        self,
        left: NDArray[np.float64],
        right: NDArray[np.float64],
        selector: GradeSelector,
    ) -> NDArray[np.float64]:
        output = np.zeros(self._dim, dtype=np.float64)
        right_nonzero = np.flatnonzero(right)
        for left_mask in np.flatnonzero(left):
            left_grade = int(self._grades[left_mask])
            action = self._action(int(left_mask))
            for right_mask in right_nonzero:
                target = selector(left_grade, int(self._grades[right_mask]))
                if target is None:
                    continue
                outputs, factors = action.terms(int(right_mask))
                selected = self._grades[outputs] == target
                selected_outputs = outputs[selected]
                output[selected_outputs] += left[left_mask] * right[right_mask] * factors[selected]
        return output

    def left_action(self, bitmask: int) -> NDArray[np.float64]:
        sparse_action = self._action(bitmask)
        action = np.zeros((self._dim, self._dim), dtype=np.float64)
        for input_mask in range(self._dim):
            outputs, factors = sparse_action.terms(input_mask)
            action[outputs, input_mask] = factors
        action.setflags(write=False)
        return action


class ReferenceProductBackend:
    """Dense Chevalley-action oracle retained for backend verification."""

    name = "reference"

    def __init__(
        self,
        gram: NDArray[np.float64],
        metadata: DimensionMetadata,
    ) -> None:
        self._dim = metadata.dim
        self._grades = metadata.blade_grades
        self._left_actions = _build_dense_left_actions(gram, metadata)

    def multiply(
        self,
        left: NDArray[np.float64],
        right: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        output = np.zeros(self._dim, dtype=np.float64)
        for bitmask in np.flatnonzero(left):
            output += left[bitmask] * (self._left_actions[bitmask] @ right)
        return output

    def grade_selected_product(
        self,
        left: NDArray[np.float64],
        right: NDArray[np.float64],
        selector: GradeSelector,
    ) -> NDArray[np.float64]:
        output = np.zeros(self._dim, dtype=np.float64)
        right_nonzero = np.flatnonzero(right)
        for left_mask in np.flatnonzero(left):
            left_grade = int(self._grades[left_mask])
            for right_mask in right_nonzero:
                target = selector(left_grade, int(self._grades[right_mask]))
                if target is None:
                    continue
                column = self._left_actions[left_mask, :, right_mask]
                selected = self._grades == target
                output[selected] += left[left_mask] * right[right_mask] * column[selected]
        return output

    def left_action(self, bitmask: int) -> NDArray[np.float64]:
        return self._left_actions[bitmask]


def make_product_backend(
    requested: str,
    gram: NDArray[np.float64],
    metadata: DimensionMetadata,
    *,
    is_diagonal: bool,
) -> ProductBackend:
    """Construct the requested backend, resolving ``auto`` by metric shape."""
    if requested not in {"auto", "diagonal", "packed", "lazy", "reference"}:
        raise ValueError("product_backend must be 'auto', 'diagonal', 'packed', 'lazy', or 'reference'")
    selected = "diagonal" if requested == "auto" and is_diagonal else requested
    if selected == "auto":
        selected = "packed" if packed_backend_byte_estimate(metadata) <= _DEFAULT_PACKED_BYTE_BUDGET else "lazy"
    if selected == "diagonal":
        if not is_diagonal:
            raise ValueError("the diagonal product backend requires a diagonal Gram matrix")
        return DiagonalProductBackend(np.diag(gram), metadata)
    if selected == "packed":
        return PackedProductBackend(gram, metadata)
    if selected == "lazy":
        return LazyProductBackend(gram, metadata)
    return ReferenceProductBackend(gram, metadata)


def packed_backend_byte_estimate(metadata: DimensionMetadata) -> int:
    """Return a conservative final-storage estimate for a packed backend."""
    dim = metadata.dim
    offset_bytes = (dim * dim + 1) * np.dtype(np.intp).itemsize
    term_bytes = bitmask_dtype(dim).itemsize + np.dtype(np.float64).itemsize
    return offset_bytes + dim**3 * term_bytes


def _build_sparse_left_actions(
    gram: NDArray[np.float64],
    metadata: DimensionMetadata,
) -> tuple[_SparseLeftAction, ...]:
    """Build general-Gram left actions without allocating a dense cube."""
    dim = metadata.dim
    mask_dtype = bitmask_dtype(dim)
    vector_terms = _build_vector_terms(gram, metadata)
    actions: list[_SparseLeftAction | None] = [None] * dim

    for bitmask, action in _build_base_left_actions(
        vector_terms,
        metadata,
        mask_dtype,
    ).items():
        actions[bitmask] = action

    for blade_grade in range(2, metadata.n + 1):
        for blade_mask in range(dim):
            if int(metadata.blade_grades[blade_mask]) != blade_grade:
                continue
            actions[blade_mask] = _build_higher_left_action(
                blade_mask,
                gram,
                metadata,
                vector_terms,
                lambda bitmask: _require_action(actions, bitmask),
                mask_dtype,
            )

    return tuple(_require_action(actions, bitmask) for bitmask in range(dim))


def _build_base_left_actions(
    vector_terms: tuple[tuple[tuple[tuple[int, float], ...], ...], ...],
    metadata: DimensionMetadata,
    mask_dtype: np.dtype[np.unsignedinteger[Any]],
) -> dict[int, _SparseLeftAction]:
    actions = {
        0: _pack_columns(
            [((input_mask, 1.0),) for input_mask in range(metadata.dim)],
            mask_dtype,
        )
    }
    for vector_index in range(metadata.n):
        actions[1 << vector_index] = _pack_columns(
            list(vector_terms[vector_index]),
            mask_dtype,
        )
    return actions


def _build_higher_left_action(
    blade_mask: int,
    gram: NDArray[np.float64],
    metadata: DimensionMetadata,
    vector_terms: tuple[tuple[tuple[tuple[int, float], ...], ...], ...],
    action_for: Callable[[int], _SparseLeftAction],
    mask_dtype: np.dtype[np.unsignedinteger[Any]],
) -> _SparseLeftAction:
    """Build one grade-two-or-higher blade action by Chevalley recurrence."""
    first_mask = blade_mask & -blade_mask
    first_index = first_mask.bit_length() - 1
    remainder = blade_mask ^ first_mask
    remainder_action = action_for(remainder)
    contractions = tuple(
        (
            remainder ^ (1 << contracted_index),
            (-1.0) ** position * gram[first_index, contracted_index],
        )
        for position, contracted_index in enumerate(set_bit_indices(remainder))
        if gram[first_index, contracted_index] != 0.0
    )

    columns: list[tuple[tuple[int, float], ...]] = []
    for input_mask in range(metadata.dim):
        combined: dict[int, float] = {}
        intermediate_outputs, intermediate_factors = remainder_action.terms(input_mask)
        for intermediate, intermediate_factor in zip(
            intermediate_outputs,
            intermediate_factors,
            strict=True,
        ):
            for output_mask, vector_factor in vector_terms[first_index][int(intermediate)]:
                output_mask = int(output_mask)
                combined[output_mask] = combined.get(output_mask, 0.0) + (intermediate_factor * vector_factor)

        for contracted_mask, contraction in contractions:
            contracted_action = action_for(contracted_mask)
            contracted_outputs, contracted_factors = contracted_action.terms(input_mask)
            for output_mask, factor in zip(
                contracted_outputs,
                contracted_factors,
                strict=True,
            ):
                output_mask = int(output_mask)
                combined[output_mask] = combined.get(output_mask, 0.0) - (contraction * factor)

        columns.append(
            tuple((output_mask, factor) for output_mask, factor in sorted(combined.items()) if factor != 0.0)
        )
    return _pack_columns(columns, mask_dtype)


def _sparse_action_bytes(action: _SparseLeftAction) -> int:
    return action.offsets.nbytes + action.outputs.nbytes + action.factors.nbytes


def _build_vector_terms(
    gram: NDArray[np.float64],
    metadata: DimensionMetadata,
) -> tuple[tuple[tuple[tuple[int, float], ...], ...], ...]:
    all_vectors: list[tuple[tuple[tuple[int, float], ...], ...]] = []
    for vector_index in range(metadata.n):
        vector_mask = 1 << vector_index
        columns: list[tuple[tuple[int, float], ...]] = []
        for input_mask in range(metadata.dim):
            combined: dict[int, float] = {}
            wedge_sign = metadata.wedge_factor[vector_mask, input_mask]
            if wedge_sign:
                combined[vector_mask ^ input_mask] = float(wedge_sign)
            for position, contracted_index in enumerate(set_bit_indices(input_mask)):
                factor = (-1.0) ** position * gram[vector_index, contracted_index]
                if factor != 0.0:
                    output_mask = input_mask ^ (1 << contracted_index)
                    combined[output_mask] = combined.get(output_mask, 0.0) + factor
            columns.append(
                tuple((output_mask, factor) for output_mask, factor in sorted(combined.items()) if factor != 0.0)
            )
        all_vectors.append(tuple(columns))
    return tuple(all_vectors)


def _pack_columns(
    columns: list[tuple[tuple[int, float], ...]],
    mask_dtype: np.dtype[np.unsignedinteger[Any]],
) -> _SparseLeftAction:
    offsets = np.empty(len(columns) + 1, dtype=np.intp)
    offsets[0] = 0
    for index, column in enumerate(columns):
        offsets[index + 1] = offsets[index] + len(column)
    outputs = np.empty(int(offsets[-1]), dtype=mask_dtype)
    factors = np.empty(int(offsets[-1]), dtype=np.float64)
    cursor = 0
    for column in columns:
        for output_mask, factor in column:
            outputs[cursor] = output_mask
            factors[cursor] = factor
            cursor += 1
    offsets.setflags(write=False)
    outputs.setflags(write=False)
    factors.setflags(write=False)
    return _SparseLeftAction(offsets, outputs, factors)


def _pack_left_actions(
    actions: tuple[_SparseLeftAction, ...],
    dim: int,
) -> tuple[
    NDArray[np.intp],
    NDArray[np.unsignedinteger[Any]],
    NDArray[np.float64],
]:
    offsets = np.empty(dim * dim + 1, dtype=np.intp)
    offsets[0] = 0
    row = 0
    for action in actions:
        for input_mask in range(dim):
            start = int(action.offsets[input_mask])
            stop = int(action.offsets[input_mask + 1])
            offsets[row + 1] = offsets[row] + stop - start
            row += 1

    outputs = np.empty(int(offsets[-1]), dtype=bitmask_dtype(dim))
    factors = np.empty(int(offsets[-1]), dtype=np.float64)
    cursor = 0
    for action in actions:
        count = len(action.outputs)
        outputs[cursor : cursor + count] = action.outputs
        factors[cursor : cursor + count] = action.factors
        cursor += count
    offsets.setflags(write=False)
    outputs.setflags(write=False)
    factors.setflags(write=False)
    return offsets, outputs, factors


def _require_action(
    actions: list[_SparseLeftAction | None],
    bitmask: int,
) -> _SparseLeftAction:
    action = actions[bitmask]
    if action is None:  # pragma: no cover - guards the recurrence invariant
        raise RuntimeError(f"left action {bitmask} has not been constructed")
    return action


def _build_dense_left_actions(
    gram: NDArray[np.float64],
    metadata: DimensionMetadata,
) -> NDArray[np.float64]:
    """Build the original dense Chevalley reference tensor."""
    n = metadata.n
    dim = metadata.dim
    vector_action = np.zeros((n, dim, dim), dtype=np.float64)
    for vector_index in range(n):
        vector_mask = 1 << vector_index
        for input_mask in range(dim):
            wedge_sign = metadata.wedge_factor[vector_mask, input_mask]
            if wedge_sign:
                vector_action[
                    vector_index,
                    vector_mask ^ input_mask,
                    input_mask,
                ] += wedge_sign
            for position, contracted_index in enumerate(set_bit_indices(input_mask)):
                output_mask = input_mask ^ (1 << contracted_index)
                vector_action[vector_index, output_mask, input_mask] += (-1.0) ** position * gram[
                    vector_index, contracted_index
                ]

    left_action = np.zeros((dim, dim, dim), dtype=np.float64)
    left_action[0] = np.eye(dim)
    for vector_index in range(n):
        left_action[1 << vector_index] = vector_action[vector_index]
    for blade_grade in range(2, n + 1):
        for blade_mask in range(dim):
            if int(metadata.blade_grades[blade_mask]) != blade_grade:
                continue
            first_mask = blade_mask & -blade_mask
            first_index = first_mask.bit_length() - 1
            remainder = blade_mask ^ first_mask
            action = vector_action[first_index] @ left_action[remainder]
            for position, contracted_index in enumerate(set_bit_indices(remainder)):
                contraction = (-1.0) ** position * gram[first_index, contracted_index]
                if contraction:
                    action -= contraction * left_action[remainder ^ (1 << contracted_index)]
            left_action[blade_mask] = action
    left_action.setflags(write=False)
    return left_action
