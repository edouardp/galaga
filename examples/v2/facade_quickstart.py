"""Combine eager values with optional immutable expression provenance."""

from __future__ import annotations

from galaga.facade import Algebra, geometric_product, p_euclidean


def run() -> None:
    algebra = Algebra(config=p_euclidean(spatial_dim=3))
    e1, e2, _ = algebra.basis_vectors(expr=True)
    bivector = geometric_product(e1, e2).named("B", latex=r"\mathbf{B}")

    assert bivector.expr is not None
    assert bivector.name is not None
    assert bivector.name.ascii == "B"
    assert bivector.display(content="expr", target="ascii") == "e1e2"
    assert bivector.display(content="value", target="unicode") == "e₁₂"


if __name__ == "__main__":
    run()
