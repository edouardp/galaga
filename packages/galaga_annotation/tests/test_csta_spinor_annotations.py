"""CSTA teaching views preserve values and target the intended factors/regions."""

import numpy as np
import pytest

import galaga_annotation as ga
from galaga import Algebra, exp, presets
from galaga.models import ConformalSpacetimeModel

pytest.importorskip("galaga_matrix")
from galaga_matrix import MatrixRepr  # noqa: E402


def test_twistor_column_regions_distinguish_upper_and_lower_pairs_without_mutation():
    column = MatrixRepr(np.array([[1 + 0.5j], [-0.25j], [0.3], [1 - 0.2j]]), kind="ket")
    original = column.mat.copy()
    rules = (
        ga.on(ga.block(rows=slice(0, 2)), background="#e8f0ff", color="#1d4ed8"),
        ga.on(ga.block(rows=slice(2, 4)), background="#fff3df", color="#9a4d00"),
    )
    plan = ga.resolve_matrix(column, rules)
    assert [p.cells for p in plan.placements] == [((0, 0), (1, 0)), ((2, 0), (3, 0))]
    view = ga.annotator(*rules)(column)
    rendered = view.latex()
    assert rendered.count(r"\textcolor{#1d4ed8}") == 2
    assert rendered.count(r"\textcolor{#9a4d00}") == 2
    assert view.value is column
    np.testing.assert_array_equal(column.mat, original)
    assert column.kind == "ket" and column.algebra is None


def test_translator_coupling_highlight_selects_only_the_upper_right_block():
    # This is the explicit spinor frame's translator matrix, not a default
    # Clifford compact representation.
    q = np.array([[0.9, 0.3 + 0.4j], [0.3 - 0.4j, 0.5]])
    column_action = MatrixRepr(np.block([[np.eye(2), -1j * q], [np.zeros((2, 2)), np.eye(2)]]))
    original = column_action.mat.copy()
    rule = ga.on(ga.block(rows=slice(0, 2), columns=slice(2, 4)), background="#e8f5e9", color="#166534")
    plan = ga.resolve_matrix(column_action, (rule,))
    assert plan.placements[0].cells == ((0, 2), (0, 3), (1, 2), (1, 3))
    view = ga.annotate(column_action, rule)
    assert view.latex().count(r"\textcolor{#166534}") == 4
    np.testing.assert_array_equal(column_action.mat, original)


def test_csta_spinor_and_event_action_labels_preserve_the_computed_products():
    model = ConformalSpacetimeModel(Algebra(config=presets.csta(), user_config_files=False))
    g0, g1, _, _ = model.spacetime_basis_vectors()
    P = (1 + g1 * g0) * (1 + (model.origin ^ model.infinity)) / 4
    R = exp(0.3 * g1 * g0).with_expr().named("R")
    psi = P.with_expr().named("psi", latex=r"\psi")
    X = model.event(0.7, 0.2, -0.3, 0.4).with_expr().named("X")
    left_action = R * psi
    sandwich = R * X * ~R
    spinor_view = ga.annotate(
        left_action,
        ga.on(ga.variable("R"), background="#e8f0ff", label="rotor", side="below", missing="error"),
        ga.on(ga.variable("psi"), label="spinor", side="below", missing="error"),
    )
    event_view = ga.annotate(
        sandwich,
        ga.on(ga.variable("R"), background="#e8f0ff", missing="error"),
        ga.on(ga.variable("X"), label="event", side="below", missing="error"),
        ga.on(ga.subexpression(~R), background="#e8f0ff", label="reverse rotor", side="below", missing="error"),
    )
    spinor_latex = spinor_view.latex(content="expr")
    event_latex = event_view.latex(content="expr")
    assert r"\underset{\text{rotor}}" in spinor_latex
    assert r"\underset{\text{spinor}}" in spinor_latex
    assert r"\widetilde{R}" not in spinor_latex
    assert r"\underset{\text{event}}" in event_latex
    assert r"\underset{\text{reverse rotor}}" in event_latex
    assert r"\widetilde{R}" in event_latex
    assert spinor_view.plain is left_action and event_view.plain is sandwich
    assert spinor_view.plain.expr == left_action.expr and event_view.plain.expr == sandwich.expr
    np.testing.assert_array_equal(spinor_view.plain.data, left_action.data)
    np.testing.assert_array_equal(event_view.plain.data, sandwich.data)
