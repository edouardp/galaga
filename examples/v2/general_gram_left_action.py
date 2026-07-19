"""Materialize a left-regular action in a native-null basis."""

from __future__ import annotations

import numpy as np

from galaga.facade import Algebra, geometric_product


def run() -> None:
    algebra = Algebra(gram=np.array([[0.0, -1.0], [-1.0, 0.0]]))
    left = algebra.multivector([1.0, 2.0, -1.0, 0.5])
    right = algebra.multivector([-2.0, 0.25, 3.0, 1.0])

    np.testing.assert_allclose(
        algebra.left_action(left) @ right.data,
        geometric_product(left, right).data,
        rtol=0.0,
        atol=1e-12,
    )
    assert algebra.inertia == (1, 1, 0)
    assert not algebra.is_orthogonal_basis


if __name__ == "__main__":
    run()
