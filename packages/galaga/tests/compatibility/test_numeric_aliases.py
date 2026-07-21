"""Compatibility aliases kept outside numeric mathematics tests."""

from __future__ import annotations

import importlib

import pytest

import galaga
import galaga.facade as facade
import galaga.legacy as legacy


def test_top_level_numeric_aliases_are_the_facade_objects() -> None:
    for alias, canonical in facade.OPERATION_ALIASES.items():
        assert getattr(galaga, alias) is getattr(facade, canonical)


def test_explicit_v1_numeric_aliases_remain_the_same_function_objects() -> None:
    assert legacy.geometric_product is legacy.gp
    assert legacy.wedge is legacy.op
    assert legacy.join is legacy.op
    assert legacy.meet is legacy.regressive_product
    assert legacy.rev is legacy.reverse
    assert legacy.antiwedge is legacy.regressive_product


def test_v2_antiwedge_has_a_distinct_operation_identity_but_the_same_value() -> None:
    algebra = facade.Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    left = e1 ^ e2
    right = e2 ^ e3

    assert facade.antiwedge is not facade.regressive_product
    assert facade.antiwedge(left, right) == facade.regressive_product(left, right)


def test_gram_bridge_reexports_the_facade_objects_without_a_fork() -> None:
    import galaga.facade.catalog as facade_catalog

    with pytest.warns(facade.GalagaDeprecationWarning, match="gram_bridge is deprecated"):
        bridge = importlib.reload(importlib.import_module("galaga.gram_bridge"))
    with pytest.warns(facade.GalagaDeprecationWarning, match="gram_bridge.catalog is deprecated"):
        bridge_catalog = importlib.reload(importlib.import_module("galaga.gram_bridge.catalog"))

    assert bridge.Algebra is facade.Algebra
    assert bridge.Multivector is facade.Multivector
    assert bridge.OPERATIONS is facade.OPERATIONS
    assert bridge.geometric_product is facade.geometric_product
    assert bridge_catalog.OperationSpec is facade_catalog.OperationSpec
