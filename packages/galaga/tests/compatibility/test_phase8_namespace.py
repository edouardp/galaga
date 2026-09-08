"""Permanent public namespace contracts after retiring the live v1 oracle."""

from __future__ import annotations

import importlib
import subprocess
import sys

import numpy as np
import pytest
from tools.legacy_import_boundary import LegacyImportError, assert_no_legacy_modules

import galaga
import galaga.core as core
import galaga.facade as facade


def test_top_level_manifest_and_objects_are_exact_facade_reexports() -> None:
    assert galaga.__all__ == facade.__all__
    assert galaga.__all__ is not facade.__all__
    for name in facade.__all__:
        assert getattr(galaga, name) is getattr(facade, name)


def test_plain_import_does_not_load_the_legacy_engine() -> None:
    program = """
from tools.legacy_import_boundary import install_import_guard, assert_no_legacy_modules
install_import_guard()
import galaga
assert galaga.Algebra.__module__ == 'galaga.facade._numeric'
algebra = galaga.Algebra(2)
assert galaga.geometric_product(algebra.blade(1), algebra.blade(2)) == algebra.blade(3)
assert_no_legacy_modules()
"""
    result = subprocess.run([sys.executable, "-c", program], check=False, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("gram", (((1, 0), (0, 1)), ((2, 0.5), (0.5, -1)), ((0, -1), (-1, 0))))
def test_public_values_use_only_the_owned_core_domain(gram) -> None:
    algebra = galaga.Algebra(gram=gram)
    a, b = algebra.basis_vectors()
    assert type(a) is galaga.Multivector is facade.Multivector
    assert type(a.numeric) is core.Multivector and a.numeric.algebra is algebra.numeric
    assert galaga.geometric_product(a, b) == a * b
    np.testing.assert_array_equal((a * b).data, [gram[0][1], 0, 0, 1])
    named = a.named("a") * b.named("b")
    assert galaga.evaluate(named.expr, algebra=algebra, environment={"a": a, "b": b}) == a * b
    assert_no_legacy_modules()


def test_retired_imports_fail_before_numeric_construction() -> None:
    with pytest.raises(LegacyImportError, match="retired Galaga import"):
        importlib.import_module("galaga.legacy")
    assert_no_legacy_modules()


@pytest.mark.parametrize("side", ("left", "right"))
def test_foreign_value_domains_do_not_mix_implicitly(side) -> None:
    class ForeignValue:
        """Having data/algebra attributes is not admission to the facade domain."""

        data = np.array([0, 1, 0, 0])
        algebra = object()

    value = galaga.Algebra(2).blade(1)
    operands = (value, ForeignValue()) if side == "right" else (ForeignValue(), value)
    with pytest.raises(TypeError, match="Multivectors"):
        galaga.geometric_product(*operands)


@pytest.mark.parametrize("name", ("inner_product", "ip"))
def test_ambiguous_v1_inner_product_names_have_top_level_migration_guidance(name: str) -> None:
    with pytest.raises(AttributeError, match="does not select an ambiguous inner product"):
        getattr(galaga, name)
