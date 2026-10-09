"""Public namespace identity and value-domain contracts."""

from __future__ import annotations

import numpy as np
import pytest

import galaga
import galaga.core as core
import galaga.facade as facade


def test_top_level_manifest_and_objects_are_exact_facade_reexports() -> None:
    assert galaga.__all__ == facade.__all__
    assert galaga.__all__ is not facade.__all__
    for name in facade.__all__:
        assert getattr(galaga, name) is getattr(facade, name)


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
def test_ambiguous_inner_product_names_have_top_level_guidance(name: str) -> None:
    with pytest.raises(AttributeError, match="does not select an ambiguous inner product"):
        getattr(galaga, name)
