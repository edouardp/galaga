"""Basis factory sequences and tables share the captured presentation order."""

import re
from collections.abc import Sequence

import numpy as np
import pytest

from galaga import Algebra, BasisMultivectors, DisplayOrder, DisplayPolicy, presets


@pytest.mark.parametrize("grade", range(5))
@pytest.mark.parametrize("expr", (False, True))
def test_basis_blades_grade_keyword_preserves_values_expressions_and_table(grade, expr):
    algebra = Algebra(4)
    values = algebra.basis_blades(grade=grade, expr=expr)
    positional = algebra.basis_blades(grade, expr=expr)
    expected = tuple(algebra.blade(mask) for mask in algebra.display_order if mask.bit_count() == grade)

    assert isinstance(values, BasisMultivectors)
    assert values == expected
    assert values == positional
    assert values.latex() == positional.latex()
    assert all((value.expr is not None) == expr for value in values)


@pytest.mark.parametrize("preset", (presets.sta(), presets.sta(sigmas=True, pseudovectors=True), presets.cga()))
@pytest.mark.parametrize("grade", (1, 2))
def test_basis_factory_sequence_and_table_follow_display_order(preset, grade):
    algebra = Algebra(config=preset)
    values = algebra.basis_vectors() if grade == 1 else algebra.basis_blades(grade)
    masks = [int(np.flatnonzero(value.data).item()) for value in values]

    assert isinstance(values, BasisMultivectors)
    assert isinstance(values, Sequence)
    assert tuple(values) == tuple(algebra.blade(mask) for mask in masks)
    expected_masks = [mask for mask in algebra.display_order if mask.bit_count() == grade]
    assert masks == expected_masks
    assert all(mask.bit_count() == grade for mask in masks)

    row_indices = [int(index) for index in re.findall(r"\\texttt\{\[(\d+)\]\} &", values.latex())]
    assert row_indices == list(range(len(values)))
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
    assert (first, second, third) == tuple(reversed(algebra.basis_vectors()))
    assert bivectors == tuple(reversed(algebra.basis_blades(2)))
    assert re.findall(r"\\texttt\{\[(\d+)\]\} &", vectors.latex()) == ["0", "1", "2"]
    assert re.findall(r"\\texttt\{\[(\d+)\]\} &", bivectors.latex()) == ["0", "1", "2"]
    assert all(value.expr is not None for value in bivectors)
    assert r"\text{Index} & \text{basis blade}" in bivectors.latex()


@pytest.mark.parametrize("expr", (False, True))
def test_quaternion_basis_blades_unpack_as_hamilton_units(expr):
    algebra = Algebra(config=presets.quaternion())
    values = algebra.basis_blades(grade=2, expr=expr)
    i, j, k = values
    e1, e2, e3 = algebra.basis_vectors()

    assert (i, j, k) == (e2 ^ e3, e1 ^ e3, e1 ^ e2)
    assert i * j == k and j * k == i and k * i == j
    assert i * i == j * j == k * k == -1
    assert values[0] == i and values[1] == j and values[2] == k
    assert values[:2] == (i, j)
    assert algebra.numeric.basis_blades(2) == (k.numeric, j.numeric, i.numeric)
    assert all((value.expr is not None) == expr for value in values)
    assert values.latex() == (
        r"\begin{array}{c|l}\text{Index} & \text{basis blade}"
        r" \\ \texttt{[0]} & i \\ \texttt{[1]} & j \\ \texttt{[2]} & k\end{array}"
    )


@pytest.mark.parametrize("target", ("ascii", "unicode"))
def test_quaternion_plain_text_table_matches_iteration(target):
    formatters = pytest.importorskip("IPython.core.formatters")
    algebra = Algebra(config=presets.quaternion(), display=DisplayPolicy(target=target))
    values = algebra.basis_blades(2)
    formatted, _ = formatters.DisplayFormatter().format(values)

    assert formatted["text/plain"].splitlines() == [
        "Index | basis blade",
        "[0]   | i",
        "[1]   | j",
        "[2]   | k",
    ]


@pytest.mark.parametrize("preset", (presets.quaternion(), presets.sta(), presets.cga()))
def test_explicit_native_display_order_matches_core_factory_enumeration(preset):
    algebra = Algebra(config=preset)
    native = algebra.with_display_order(DisplayOrder(algebra.n, range(algebra.dim)))

    assert native.numeric is algebra.numeric
    assert tuple(value.numeric for value in native.basis_vectors()) == native.numeric.basis_vectors()
    for grade in range(native.n + 1):
        assert tuple(value.numeric for value in native.basis_blades(grade)) == native.numeric.basis_blades(grade)


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
