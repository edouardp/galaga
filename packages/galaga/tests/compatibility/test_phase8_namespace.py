"""Public, facade, and legacy namespace contracts for the Phase 8 cutover."""

from __future__ import annotations

import subprocess
import sys

import pytest

import galaga
import galaga.facade as facade
import galaga.legacy as legacy


def test_top_level_manifest_and_objects_are_exact_facade_reexports() -> None:
    assert galaga.__all__ == facade.__all__
    for name in facade.__all__:
        assert getattr(galaga, name) is getattr(facade, name)


def test_plain_import_does_not_load_the_legacy_engine() -> None:
    program = """
import sys
import galaga
assert galaga.Algebra.__module__ == 'galaga.facade._numeric'
assert 'galaga.legacy' not in sys.modules
assert 'galaga.algebra' not in sys.modules
assert 'galaga.expr' not in sys.modules
"""
    result = subprocess.run([sys.executable, "-c", program], check=False, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr


@pytest.mark.legacy_oracle
def test_explicit_legacy_namespace_preserves_a_coherent_v1_domain() -> None:
    algebra = legacy.Algebra(2)
    e1, e2 = algebra.basis_vectors()

    assert legacy.Algebra.__module__ == "galaga.algebra"
    assert legacy.Multivector.__module__ == "galaga.algebra"
    assert legacy.geometric_product(e1, e2) == e1 * e2
    assert galaga.Algebra is not legacy.Algebra
    assert galaga.Multivector is not legacy.Multivector


def test_unledgered_tests_poison_legacy_construction() -> None:
    with pytest.raises(AssertionError, match="unledgered test"):
        legacy.Algebra(2)


@pytest.mark.legacy_oracle
def test_v1_and_v2_values_do_not_mix_implicitly() -> None:
    v2_e1, _ = galaga.Algebra(2).basis_vectors()
    v1_e1, _ = legacy.Algebra(2).basis_vectors()

    with pytest.raises(TypeError):
        galaga.geometric_product(v2_e1, v1_e1)


@pytest.mark.parametrize("name", ("inner_product", "ip"))
def test_ambiguous_v1_inner_product_names_have_top_level_migration_guidance(name: str) -> None:
    with pytest.raises(AttributeError, match="does not select an ambiguous inner product"):
        getattr(galaga, name)
