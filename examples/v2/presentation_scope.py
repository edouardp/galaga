"""Change notation temporarily without changing blades or numeric identity."""

from __future__ import annotations

from galaga.facade import Algebra, Notation, geometric_product


def run() -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors(expr=True)
    value = geometric_product(e1, e2)
    default = value.display(content="expr", target="ascii")
    teaching = algebra.presentation.with_notation(Notation.functional(short=True))

    with algebra.use_presentation(teaching):
        assert value.display(content="expr", target="ascii") == "gp(e1, e2)"

    assert value.display(content="expr", target="ascii") == default
    assert value.numeric.algebra is algebra.numeric


if __name__ == "__main__":
    run()
