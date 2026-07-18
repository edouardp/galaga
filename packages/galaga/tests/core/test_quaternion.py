"""Quaternion and complex subalgebra identities in real Clifford algebras."""

from galaga.core import Algebra, geometric_product, outer_product, reverse


def test_cl3_even_subalgebra_satisfies_hamilton_identities() -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    i = outer_product(e2, e3)
    j = outer_product(e1, e3)
    k = outer_product(e1, e2)

    assert geometric_product(i, i) == -1
    assert geometric_product(j, j) == -1
    assert geometric_product(k, k) == -1
    assert geometric_product(geometric_product(i, j), k) == -1

    assert geometric_product(i, j) == k
    assert geometric_product(j, k) == i
    assert geometric_product(k, i) == j
    assert geometric_product(j, i) == -k
    assert geometric_product(k, j) == -i
    assert geometric_product(i, k) == -j


def test_cl2_even_subalgebra_has_complex_arithmetic_and_conjugation() -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    i = outer_product(e1, e2)
    z = algebra.scalar(3) + 4 * i

    assert geometric_product(i, i) == -1
    assert geometric_product(z, z) == algebra.scalar(-7) + 24 * i
    assert reverse(z) == algebra.scalar(3) - 4 * i
