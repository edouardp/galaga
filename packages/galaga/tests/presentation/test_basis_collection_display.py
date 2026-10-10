"""Basis factory sequences keep native values and show their selected blades."""

import re
from collections.abc import Sequence

import numpy as np
import pytest

from galaga import Algebra, BasisMultivectors, DisplayOrder, DisplayPolicy, presets


@pytest.mark.parametrize("grade", range(4))
@pytest.mark.parametrize("expr", (False, True))
def test_basis_blades_grade_keyword_preserves_values_expressions_and_table(grade, expr):
    algebra = Algebra(3)
    values = algebra.basis_blades(grade=grade, expr=expr)
    positional = algebra.basis_blades(grade, expr=expr)
    expected = tuple(algebra.blade(mask) for mask in range(algebra.dim) if mask.bit_count() == grade)

    assert isinstance(values, BasisMultivectors)
    assert values == expected
    assert values == positional
    assert values.latex() == positional.latex()
    assert all((value.expr is not None) == expr for value in values)


@pytest.mark.parametrize("preset", (presets.sta(), presets.sta(sigmas=True, pseudovectors=True), presets.cga()))
@pytest.mark.parametrize("grade", (1, 2))
def test_basis_factory_table_follows_display_order_without_changing_sequence(preset, grade):
    algebra = Algebra(config=preset)
    values = algebra.basis_vectors() if grade == 1 else algebra.basis_blades(grade)
    masks = [int(np.flatnonzero(value.data).item()) for value in values]

    assert isinstance(values, BasisMultivectors)
    assert isinstance(values, Sequence)
    assert tuple(values) == tuple(algebra.blade(mask) for mask in masks)
    assert masks == sorted(masks)
    assert all(mask.bit_count() == grade for mask in masks)

    row_indices = [int(index) for index in re.findall(r"\\texttt\{\[(\d+)\]\} &", values.latex())]
    expected_masks = [mask for mask in algebra.display_order if mask.bit_count() == grade]
    assert [masks[index] for index in row_indices] == expected_masks
    assert len(row_indices) == len(values)
    assert values._repr_latex_() == f"${values.latex()}$"


def test_basis_collection_uses_requested_grade_and_captured_custom_presentation():
    algebra = Algebra(3)
    default_vectors = algebra.basis_vectors()
    custom = DisplayOrder(3, (0, 4, 2, 1, 6, 5, 3, 7))
    with algebra.use_presentation(algebra.presentation.with_display_order(custom)):
        vectors = algebra.basis_vectors()
        assert algebra.basis_vectors() is vectors
        bivectors = algebra.basis_blades(2, expr=True)

    assert algebra.basis_vectors() is default_vectors
    first, second, third = vectors
    assert (first, second, third) == tuple(algebra.basis_vectors())
    assert re.findall(r"\\texttt\{\[(\d+)\]\} &", vectors.latex()) == ["2", "1", "0"]
    assert re.findall(r"\\texttt\{\[(\d+)\]\} &", bivectors.latex()) == ["2", "1", "0"]
    assert all(value.expr is not None for value in bivectors)
    assert r"\text{Index} & \text{basis blade}" in bivectors.latex()


def test_empty_basis_vector_collection_is_unpackable_and_renderable():
    values = Algebra(0).basis_vectors()
    assert values == ()
    assert len(values) == 0
    assert values.latex() == r"\begin{array}{c|l}\text{Index} & \text{basis blade}\end{array}"


@pytest.mark.parametrize("target, blade", (("unicode", "e₁₂"), ("ascii", "e12")))
def test_ipython_plain_text_uses_captured_targets_for_basis_and_local_tables(target, blade):
    formatters = pytest.importorskip("IPython.core.formatters")
    algebra = Algebra(3, display=DisplayPolicy(target=target))
    formatter = formatters.DisplayFormatter()

    for values, heading in ((algebra.basis_blades(2), "Index"), (algebra.locals(), "Python name")):
        formatted, _ = formatter.format(values)
        assert heading in formatted["text/plain"]
        assert blade in formatted["text/plain"]
        assert formatted["text/latex"] == values._repr_latex_()
