"""Ground truth for the ideal/column lesson, plus its reactive teaching paths."""

from __future__ import annotations

import html
import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from galaga_matrix import MatrixRepr, from_matrix, from_spinor_column, to_matrix, to_spinor_column

from galaga import Algebra, even_grades, exp, odd_grades, reverse

ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples/matrix/spinors_ideals_and_chirality.py"


@pytest.mark.parametrize("amplitudes", [(1, 0, 0, 0), (0, 0, 1, 0), (1, 0.5, 0.5, -0.75), (0, 0, 0, 0)])
def test_actual_blade_products_agree_with_ideal_columns_and_even_pullback(amplitudes):
    algebra = Algebra(3)
    e1, _, e3 = algebra.basis_vectors()
    f = (1 + e3) / 2
    g = (1 - e3) / 2
    ar, ai, br, bi = amplitudes
    psi = (ar + ai * algebra.I) * f + (br + bi * algebra.I) * e1 * f
    representative = 2 * even_grades(psi)
    column = to_spinor_column(representative)
    np.testing.assert_allclose(column.mat[:, 0], [complex(ar, ai), complex(br, bi)], atol=1e-12)
    for mask in range(algebra.dim):
        operator = algebra.blade(mask)
        # Actual multiplication in the algebra, not an expected Pauli sign table.
        product = operator * psi
        expected = to_matrix(product, mode="compact").mat[:, :1]
        np.testing.assert_allclose((to_matrix(operator, mode="compact") @ column).mat, expected, atol=1e-12)
        pulled = even_grades(operator) * representative + odd_grades(operator) * representative * e3
        np.testing.assert_allclose((pulled * f).data, product.data, atol=1e-12)
        np.testing.assert_allclose(to_spinor_column(pulled).mat, expected, atol=1e-12)
        other = product * e1
        assert other * g == other
        assert other == operator * (psi * e1)
        np.testing.assert_allclose(to_matrix(other, mode="compact").mat[:, 1:2], expected, atol=1e-12)
    assert e1 * (2 * f + 3 * e1 * f) == 3 * f + 2 * e1 * f
    assert f * (e1 * f) == 0 and (e1 * f) * f == e1 * f


@pytest.mark.parametrize("turns", [0, 0.25, 0.5, 1, 2])
def test_rotation_double_cover_and_bloch_vector_are_the_same_physical_rotation(turns):
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    theta = 2 * np.pi * turns
    rotor = exp(-theta * (e1 ^ e2) / 2)
    # An even representative whose column is (1, 1)/sqrt(2).
    initial = (1 + algebra.blade(5)) / np.sqrt(2)
    column = to_spinor_column(rotor * initial)
    bloch = np.array(
        [
            np.vdot(column.mat[:, 0], to_matrix(v, mode="compact").mat @ column.mat[:, 0]).real
            for v in algebra.basis_vectors()
        ]
    )
    np.testing.assert_allclose(bloch, (rotor * e1 * reverse(rotor)).vector_part, atol=1e-12)
    np.testing.assert_allclose(bloch, [np.cos(theta), np.sin(theta), 0], atol=1e-12)
    if turns in (0, 1, 2):
        np.testing.assert_allclose(column.mat, (-1) ** int(turns) * to_spinor_column(initial).mat, atol=1e-12)


def test_chirality_commutes_with_every_even_blade_and_anticommutes_with_every_odd_blade():
    algebra = Algebra(1, 3)
    chirality = 1j * to_matrix(algebra.I, mode="compact").to_basis("weyl").mat
    left = (np.eye(4) - chirality) / 2
    right = (np.eye(4) + chirality) / 2
    np.testing.assert_allclose(left @ right, 0, atol=1e-12)
    assert np.linalg.matrix_rank(left) == np.linalg.matrix_rank(right) == 2
    for mask in range(algebra.dim):
        matrix = to_matrix(algebra.blade(mask), mode="compact").to_basis("weyl").mat
        sign = (-1) ** mask.bit_count()
        np.testing.assert_allclose(chirality @ matrix, sign * matrix @ chirality, atol=1e-12)
        if mask.bit_count() % 2:
            np.testing.assert_allclose(left @ matrix @ left, 0, atol=1e-12)
        else:
            np.testing.assert_allclose(right @ matrix @ left, 0, atol=1e-12)


@pytest.mark.parametrize("basis", ["dirac", "weyl"])
def test_real_chiral_projections_agree_with_matrices_and_roundtrip(basis):
    algebra = Algebra(1, 3)
    structure = from_spinor_column(1j * to_spinor_column(algebra.identity))
    # Derive the complex structure from the public reference-column convention.
    np.testing.assert_allclose((structure * structure).data, (-algebra.identity).data, atol=1e-12)
    np.testing.assert_allclose((algebra.I * algebra.I).data, (-algebra.identity).data, atol=1e-12)
    chirality = 1j * to_matrix(algebra.I, mode="compact")
    identity = to_matrix(algebra.identity, mode="compact")
    left, right = (identity - chirality) / 2, (identity + chirality) / 2
    blades = [algebra.blade(mask) for mask in range(algebra.dim) if mask.bit_count() % 2 == 0]
    rng = np.random.default_rng(20260912)
    states = blades + [0 * algebra.identity]
    states.extend(
        sum(c * blade for c, blade in zip(rng.normal(size=len(blades)), blades, strict=True)) for _ in range(3)
    )
    for psi in states:
        chi = to_spinor_column(psi)
        real_chirality = algebra.I * psi * structure
        np.testing.assert_allclose(to_spinor_column(psi * structure).mat, 1j * chi.mat, atol=1e-12)
        np.testing.assert_allclose(to_spinor_column(real_chirality).mat, (chirality @ chi).mat, atol=1e-12)
        np.testing.assert_allclose((algebra.I * real_chirality * structure).data, psi.data, atol=1e-12)
        projections = []
        for sign, projector in ((-1, left), (1, right)):
            projected = (psi + sign * real_chirality) / 2
            projected_chirality = algebra.I * projected * structure
            np.testing.assert_allclose(((projected + sign * projected_chirality) / 2).data, projected.data, atol=1e-12)
            np.testing.assert_allclose(((projected - sign * projected_chirality) / 2).data, 0, atol=1e-12)
            column = (projector @ chi).to_basis(basis)
            np.testing.assert_allclose(to_spinor_column(projected).to_basis(basis).mat, column.mat, atol=1e-12)
            recovered = from_spinor_column(column)
            assert np.isrealobj(recovered.data)
            np.testing.assert_allclose(recovered.data, projected.data, atol=1e-12)
            projections.append(projected)
        np.testing.assert_allclose(sum(projections).data, psi.data, atol=1e-12)


def test_every_sta_blade_action_on_every_even_spinor_has_real_even_representative():
    algebra = Algebra(1, 3)
    gamma0 = algebra.basis_vectors()[0]
    for operator_mask in range(algebra.dim):
        operator = algebra.blade(operator_mask)
        matrix = to_matrix(operator, mode="compact")
        for spinor_mask in range(algebra.dim):
            if spinor_mask.bit_count() % 2:
                continue
            psi = algebra.blade(spinor_mask)
            acted = even_grades(operator) * psi + odd_grades(operator) * psi * gamma0
            np.testing.assert_allclose(odd_grades(acted).data, 0, atol=1e-12)
            np.testing.assert_allclose(to_spinor_column(acted).mat, (matrix @ to_spinor_column(psi)).mat, atol=1e-12)


@pytest.mark.parametrize("diagonal", [[1, 1, 0, 0], [0, 0, 1, 1]])
def test_chiral_projector_is_not_a_single_real_mv_even_after_basis_change(diagonal):
    algebra = Algebra(1, 3)
    projector = MatrixRepr(np.diag(diagonal), algebra=algebra, mode="compact", basis="weyl")
    dirac = projector.to_basis("dirac")
    np.testing.assert_allclose(dirac.mat.imag, 0, atol=1e-12)
    for matrix in (projector, dirac):
        with pytest.raises(ValueError, match="not in the image"):
            from_matrix(matrix)
    # By contrast, genuine real Clifford elements still roundtrip in both bases.
    for mask in range(algebra.dim):
        blade = algebra.blade(mask)
        matrix = to_matrix(blade, mode="compact")
        for basis in ("dirac", "weyl"):
            np.testing.assert_allclose(from_matrix(matrix.to_basis(basis)).data, blade.data, atol=1e-12)


@pytest.fixture(scope="module")
def app():
    if sys.version_info < (3, 14):
        pytest.skip("Notebook t-strings require Python 3.14")
    pytest.importorskip("marimo")
    return runpy.run_path(str(NOTEBOOK))["app"]


@pytest.fixture(scope="module")
def notebook(app):
    return app.run()


def test_notebook_renders_values_and_derives_reflection_matrices(notebook):
    outputs, definitions = notebook
    assert definitions["action_residual"] < 1e-12
    assert definitions["basis_action_residual"] < 1e-12
    for name, frame in (("plane_reflection", "reflected_frame"), ("axis_halfturn", "halfturned_frame")):
        np.testing.assert_allclose(definitions[name].mat, np.column_stack([v.vector_part for v in definitions[frame]]))
    assert np.linalg.det(definitions["plane_reflection"].mat) == pytest.approx(-1)
    assert np.linalg.det(definitions["axis_halfturn"].mat) == pytest.approx(1)
    rendered = html.unescape("\n".join(output.text for output in outputs if hasattr(output, "text")))
    equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", rendered, flags=re.S)
    assert equations
    assert all("$" not in equation for equation in equations), "Do not nest inline math in display math"
    assert "<pre>" not in rendered, "Indented interpolations must not turn prose into code blocks"
    assert "One spinor, three representations" in rendered
    assert "Left weight:" in rendered and "Right weight:" in rendered
    assert "Direct real-GA projections" in rendered
    assert "Recovered from the projected columns" in rendered
    assert "Coefficient residuals:" in rendered
    assert r"\begin{pmatrix}" in rendered
    assert not re.search(r"\{(?:ideal_spinor|spinor_ket|chiral_result|displayed_operator)(?::[^}]*)?\}", rendered)


@pytest.mark.parametrize(
    "controls,result_marker",
    [
        (("a_real", "a_imag", "b_real", "b_imag"), "<strong>Algebra element</strong>"),
        (("operator_choice",), "<strong>Algebra result</strong>"),
        (("turns",), "<strong>Transformed column</strong>"),
        (("chiral_action", "chiral_basis", "odd_strength"), "<strong>Result from a left-chiral input</strong>"),
    ],
)
def test_controls_render_once_alongside_the_results_they_affect(notebook, controls, result_marker):
    outputs, definitions = notebook
    rendered = [output.text for output in outputs if hasattr(output, "text")]
    result_outputs = [output for output in rendered if result_marker in output]
    assert len(result_outputs) == 1
    for name in controls:
        control_html = definitions[name].text
        assert control_html in result_outputs[0], f"{name} must be displayed in its result cell"
        assert sum(output.count(control_html) for output in rendered) == 1, f"{name} must not have a standalone display"
        assert result_outputs[0].index(control_html) < result_outputs[0].index(result_marker)


def test_matrix_panel_stacks_heading_math_and_caption_separately(notebook, monkeypatch):
    _, definitions = notebook
    mo = definitions["mo"]
    stacks = []
    original = mo.vstack

    def record_stack(items, **kwargs):
        stacks.append((items, kwargs))
        return original(items, **kwargs)

    monkeypatch.setattr(mo, "vstack", record_stack)
    caption = mo.md("Panel caption")
    panel = definitions["matrix_panel"]("Panel heading", definitions["displayed_operator"], caption)
    items, options = stacks[-1]
    assert len(items) == 3
    assert "<strong>Panel heading</strong>" in items[0].text
    assert "marimo-tex" not in items[0].text
    assert "<marimo-tex" in items[1].text and "Panel heading" not in items[1].text
    assert items[2] is caption
    assert options["align"] == "start"
    assert "flex-direction: column" in panel.text


def test_notebook_rows_have_at_most_two_panels_and_wide_matrices_stand_alone(app, monkeypatch):
    import marimo as mo

    rows = []
    original = mo.hstack

    def record_row(items, **kwargs):
        rows.append(items)
        return original(items, **kwargs)

    monkeypatch.setattr(mo, "hstack", record_row)
    _, definitions = app.run()
    assert rows
    assert all(len(items) <= 2 for items in rows)
    # The exact rendered wide operator must never be squeezed into a row.
    wide_panel = definitions["matrix_panel"]("Wide operator", definitions["displayed_operator"])
    wide_math = re.search(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", html.unescape(wide_panel.text), flags=re.S)
    assert wide_math is not None
    for items in rows:
        rendered = html.unescape("".join(getattr(item, "text", "") for item in items))
        assert wide_math.group(1) not in rendered
        assert "Computed basis change" not in rendered
        assert "Result from a left-chiral input" not in rendered


@pytest.mark.parametrize("selection", ["1", "e1", "e3", "f"])
def test_operator_control_agrees_with_the_actual_algebra(app, selection):
    _, definitions = app.run(defs={"operator_choice": SimpleNamespace(value=selection)})
    expected = definitions["selected_operator"] * definitions["ideal_spinor"]
    np.testing.assert_allclose(definitions["acted_ket"].mat, definitions["ideal_column"](expected).mat, atol=1e-12)


@pytest.mark.parametrize("turns,overlap", [(0, 1), (1, 0), (2, 1)])
def test_rotation_control_reaches_both_signs_and_closes_after_four_pi(app, turns, overlap):
    _, definitions = app.run(defs={"turns": SimpleNamespace(value=turns)})
    np.testing.assert_allclose(
        definitions["rotation_column"].mat, (-1) ** turns * definitions["rotation_reference"].mat, atol=1e-12
    )
    assert definitions["interference"] == pytest.approx(overlap, abs=1e-12)


@pytest.mark.parametrize("basis", ["dirac", "weyl"])
@pytest.mark.parametrize("action", ["even rotor", "odd vector", "mixed"])
def test_chiral_controls_and_basis_change_preserve_the_same_action(app, basis, action):
    _, definitions = app.run(
        defs={
            "chiral_basis": SimpleNamespace(value=basis),
            "chiral_action": SimpleNamespace(value=action),
            "odd_strength": SimpleNamespace(value=0.6),
        }
    )
    left, right = definitions["left_weight"], definitions["right_weight"]
    if action == "even rotor":
        assert left > 0 and right < 1e-24
    elif action == "odd vector":
        assert left < 1e-24 and right > 0
    else:
        assert left > 0 and right > 0
    change = definitions["dirac_to_weyl"]
    for side in ("left", "right"):
        direct = definitions[f"{side}_ga"]
        recovered = definitions[f"recovered_{side}_ga"]
        assert np.isrealobj(recovered.data)
        assert definitions[f"{side}_roundtrip_residual"] < 1e-12
        np.testing.assert_allclose(recovered.data, direct.data, atol=1e-12)
        np.testing.assert_allclose(
            to_spinor_column(direct).to_basis(basis).mat,
            definitions[f"projected_{side}_column"].mat,
            atol=1e-12,
        )
    np.testing.assert_allclose(
        (definitions["left_ga"] + definitions["right_ga"]).data,
        definitions["acted_sta_spinor"].data,
        atol=1e-12,
    )
    np.testing.assert_allclose(definitions["weyl_action"].mat, change @ definitions["dirac_result"].mat, atol=1e-12)
    algebra = definitions["sta"]
    for mask in range(algebra.dim):
        matrix = to_matrix(algebra.blade(mask), mode="compact")
        np.testing.assert_allclose(matrix.to_basis("weyl").mat, change @ matrix.mat @ change.conj().T, atol=1e-12)


def test_zero_amplitudes_are_allowed_without_division_by_zero(app):
    _, definitions = app.run(defs={name: SimpleNamespace(value=0) for name in ("a_real", "a_imag", "b_real", "b_imag")})
    assert definitions["ideal_spinor"] == 0
    np.testing.assert_array_equal(definitions["spinor_ket"].mat, np.zeros((2, 1)))
    np.testing.assert_array_equal(definitions["pulled_column_action"].mat, np.zeros((2, 1)))
