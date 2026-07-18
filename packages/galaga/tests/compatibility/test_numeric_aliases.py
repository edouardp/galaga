"""Compatibility aliases kept outside numeric mathematics tests."""

from __future__ import annotations

import galaga
import galaga.gram_bridge as facade


def test_v1_numeric_aliases_remain_the_same_function_objects() -> None:
    assert galaga.geometric_product is galaga.gp
    assert galaga.wedge is galaga.op
    assert galaga.join is galaga.op
    assert galaga.meet is galaga.regressive_product
    assert galaga.rev is galaga.reverse
    assert galaga.antiwedge is galaga.regressive_product


def test_v2_antiwedge_has_a_distinct_operation_identity_but_the_same_value() -> None:
    algebra = facade.Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    left = e1 ^ e2
    right = e2 ^ e3

    assert facade.antiwedge is not facade.regressive_product
    assert facade.antiwedge(left, right) == facade.regressive_product(left, right)
