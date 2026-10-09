"""Canonical alias identity and distinct operation provenance."""

from __future__ import annotations

import galaga
import galaga.facade as facade


def test_top_level_numeric_aliases_are_the_facade_objects() -> None:
    for alias, canonical in facade.OPERATION_ALIASES.items():
        assert getattr(galaga, alias) is getattr(facade, canonical)


def test_v2_antiwedge_has_a_distinct_operation_identity_but_the_same_value() -> None:
    algebra = facade.Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    left = e1 ^ e2
    right = e2 ^ e3

    assert facade.antiwedge is not facade.regressive_product
    assert facade.antiwedge(left, right) == facade.regressive_product(left, right)


def test_public_api_reexports_the_facade_objects_without_a_fork() -> None:
    import galaga.facade.catalog as facade_catalog

    assert galaga.Algebra is facade.Algebra
    assert galaga.Multivector is facade.Multivector
    assert galaga.OPERATIONS is facade.OPERATIONS
    assert galaga.geometric_product is facade.geometric_product
    assert galaga.OperationSpec is facade_catalog.OperationSpec
