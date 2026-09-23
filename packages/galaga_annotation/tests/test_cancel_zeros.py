"""Automatic cancellation of zero-valued expression subtrees."""

from __future__ import annotations

import pytest

import galaga_annotation as ga
from galaga import Algebra


@pytest.fixture()
def symbols():
    algebra = Algebra(3, expr=True)
    return (algebra, *algebra.basis_vectors())


def test_cancel_zeros_finds_the_zero_subexpression_without_changing_the_value(symbols) -> None:
    _, e1, e2, _ = symbols
    value = ((e1 | e2) + (e1 ^ e2)).named("v")

    view = ga.cancel_zeros(color="#aaaf")(value)

    assert view.plain is value
    assert view.plain.almost_equal(e1 ^ e2)
    assert view.latex() == (
        r"v \quad = \quad \cancel{\textcolor{#aaaf}{e_{1} \cdot e_{2}}}"
        r" + e_{1} \wedge e_{2} \quad = \quad e_{12}"
    )


def test_cancel_zeros_selects_innermost_zero_calls_without_nested_cancellation(symbols) -> None:
    _, e1, e2, e3 = symbols
    value = ((e1 | e2) + (e1 | e3) + (e1 ^ e2)).named("w")

    rendered = ga.cancel_zeros()(value).latex()

    assert rendered.count(r"\cancel{") == 2
    assert r"\cancel{\textcolor{#aaaf}{e_{1} \cdot e_{2}}}" in rendered
    assert r"\cancel{\textcolor{#aaaf}{e_{1} \cdot e_{3}}}" in rendered
    assert r"\cancel{\textcolor{#aaaf}{\cancel{" not in rendered


def test_cancel_zeros_can_select_a_zero_composite_with_no_zero_descendant(symbols) -> None:
    _, e1, _, _ = symbols
    value = (e1 - e1).named("q")
    assert r"\cancel{\textcolor{#aaaf}{e_{1} - e_{1}}}" in ga.cancel_zeros()(value).latex()


def test_cancel_zeros_preserves_a_flattened_sum_subtree_interval(symbols) -> None:
    _, e1, e2, _ = symbols
    value = ((e1 * e2 + e2 * e1) + e1 * e1).named("a")

    rendered = ga.cancel_zeros()(value).latex()

    assert r"\cancel{\textcolor{#aaaf}{e_{1} e_{2} + e_{2} e_{1}}} + e_{1} e_{1}" in rendered
    assert r"\cancel{\textcolor{#aaaf}{e_{1} e_{2} + e_{2} e_{1} + e_{1} e_{1}}}" not in rendered


def test_cancel_zeros_preserves_flattened_product_and_infix_intervals(symbols) -> None:
    _, e1, e2, _ = symbols
    wedge = ((e1 ^ e1) ^ e2).named("B")
    assert r"\cancel{\textcolor{#aaaf}{e_{1} \wedge e_{1}}} \wedge e_{2}" in (ga.cancel_zeros()(wedge).latex())

    witt = Algebra(gram=[[0, 1], [1, 0]], expr=True)
    p, q = witt.basis_vectors()
    product = ((p * p) * q).named("P")
    assert r"\cancel{\textcolor{#aaaf}{e_{1} e_{1}}} e_{2}" in ga.cancel_zeros()(product).latex()


def test_cancel_zeros_leaves_nonzero_calls_undecorated(symbols) -> None:
    _, e1, e2, _ = symbols
    value = ((e1 | e1) + (e1 ^ e2)).named("c")
    assert r"\cancel" not in ga.cancel_zeros()(value).latex()


def test_cancel_zeros_skips_unresolved_named_subtrees_but_keeps_independent_matches(symbols) -> None:
    _, e1, e2, e3 = symbols
    x = e1.named("x")
    value = ((x | e2) + (e1 | e3) + (e1 ^ e2)).named("s")

    rendered = ga.cancel_zeros()(value).latex()

    assert r"\cancel{\textcolor{#aaaf}{e_{1} \cdot e_{3}}}" in rendered
    assert r"\cancel{\textcolor{#aaaf}{x \cdot e_{2}}}" not in rendered


def test_cancel_zeros_uses_an_explicit_absolute_tolerance(symbols) -> None:
    _, e1, e2, _ = symbols
    value = (1e-13 * (e1 | e1) + (e1 ^ e2)).named("n")

    assert r"\cancel" not in ga.cancel_zeros()(value).latex()
    assert r"\cancel{\textcolor{#aaaf}{10^{-13} e_{1} \cdot e_{1}}}" in (ga.cancel_zeros(atol=1e-12)(value).latex())


def test_cancel_zeros_requires_provenance_and_a_cancellation_marker(symbols) -> None:
    algebra, e1, _, _ = symbols
    with pytest.raises(ValueError, match="tracked value"):
        ga.cancel_zeros()(algebra.multivector(e1.data, expr=False)).latex()
    with pytest.raises(ValueError, match="cancel_zeros marker"):
        ga.cancel_zeros(marker="underbrace")


@pytest.mark.parametrize("marker", ["cancel", "bcancel", "xcancel"])
def test_cancel_zeros_supports_the_katex_cancellation_family(marker, symbols) -> None:
    _, e1, e2, _ = symbols
    value = ((e1 | e2) + (e1 ^ e2)).named("v")
    assert rf"\{marker}{{\textcolor{{#aaaf}}{{e_{{1}} \cdot e_{{2}}}}}}" in (
        ga.cancel_zeros(marker=marker)(value).latex()
    )
