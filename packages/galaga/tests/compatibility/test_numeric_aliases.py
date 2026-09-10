"""Compatibility aliases kept outside numeric mathematics tests."""

from __future__ import annotations

import json
from pathlib import Path

import galaga
import galaga.facade as facade


def test_top_level_numeric_aliases_are_the_facade_objects() -> None:
    for alias, canonical in facade.OPERATION_ALIASES.items():
        assert getattr(galaga, alias) is getattr(facade, canonical)


def test_archived_v1_aliases_do_not_define_the_public_v2_catalog() -> None:
    archive = json.loads((Path(__file__).parents[2] / "tools/baselines/namespace-boundaries-v1.json").read_text())
    assert [(row["left"], row["right"]) for row in archive["aliases"]] == [
        ("geometric_product", "gp"),
        ("wedge", "op"),
        ("join", "op"),
        ("meet", "regressive_product"),
        ("rev", "reverse"),
        ("antiwedge", "regressive_product"),
    ]
    assert all(row["identical"] for row in archive["aliases"])
    assert facade.antiwedge is not facade.regressive_product
    assert "antiwedge" in facade.OPERATIONS and "antiwedge" not in facade.OPERATION_ALIASES
    assert facade.gp is facade.geometric_product and facade.op is facade.outer_product


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
