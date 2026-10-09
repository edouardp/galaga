"""Public structural capabilities shared by runtime geometry models."""

from collections.abc import Iterable
from numbers import Real
from typing import Protocol, runtime_checkable

import numpy as np

from ..facade import Multivector


@runtime_checkable
class PointModel(Protocol):
    def point(self, coordinates: Iterable[Real], /, *, expr: bool | None = None) -> Multivector: ...
    def coordinates(self, point: Multivector, /, *, atol: float = 1e-12) -> np.ndarray: ...


@runtime_checkable
class BulkWeightModel(Protocol):
    def bulk_part(self, value: Multivector, /) -> Multivector: ...
    def weight_part(self, value: Multivector, /) -> Multivector: ...


@runtime_checkable
class ConformalEmbeddingModel(PointModel, Protocol):
    def up(self, value: Iterable[Real] | Multivector, /, *, expr: bool | None = None) -> Multivector: ...
    def down(self, point: Multivector, /, *, atol: float = 1e-12) -> Multivector: ...
