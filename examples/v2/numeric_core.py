"""Use the presentation-free numeric core directly."""

from __future__ import annotations

import numpy as np

from galaga.core import Algebra, geometric_product


def run() -> None:
    algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, -1.0]]))
    e1, e2 = algebra.basis_vectors()

    assert geometric_product(e1, e2) + geometric_product(e2, e1) == algebra.scalar(1.0)
    assert algebra.inertia == (1, 1, 0)


if __name__ == "__main__":
    run()
