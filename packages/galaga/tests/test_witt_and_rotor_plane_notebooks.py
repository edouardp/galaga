"""Compute the new lessons across controls, exceptional cases and changed frames."""

import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from tools.migrate_v2_notebooks import migrated_notebook_paths

from galaga import complement, dual, exp, grade, metric_inner_product, outer_product, uncomplement
from galaga.display import emit

ROOT = Path(__file__).resolve().parents[3]
WITT = ROOT / "examples/algebra/witt_bases_and_null_geometry.py"
ROTORS = ROOT / "examples/algebra/four_dimensional_rotor_planes.py"
pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Teaching notebooks use Python 3.14 t-strings")


def assert_readable(outputs):
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "<pre>" not in markup
    equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
    assert equations
    assert all("$" not in equation for equation in equations)
    assert all("{generator." not in equation and "{witt_volume." not in equation for equation in equations)


def test_lessons_are_in_the_executable_gallery():
    assert {WITT, ROTORS} <= set(migrated_notebook_paths(ROOT))


@pytest.fixture(scope="module", params=[(count, rapidity) for count in (1, 2, 3) for rapidity in (-1.5, 0, 1.5)])
def witt_lesson(request):
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_matrix")
    count, rapidity = request.param
    outputs, values = runpy.run_path(str(WITT))["app"].run(
        defs={"pair_count": SimpleNamespace(value=count), "rapidity_control": SimpleNamespace(value=rapidity)}
    )
    return outputs, values, count, rapidity


def test_witt_null_reciprocal_and_orthogonal_bases_are_computed(witt_lesson):
    outputs, values, count, _ = witt_lesson
    algebra, vectors = values["witt"], values["null_vectors"]
    computed = [[float(metric_inner_product(a, b)) for b in vectors] for a in vectors]
    np.testing.assert_array_equal(computed, algebra.gram)
    np.testing.assert_array_equal(np.linalg.eigvalsh(algebra.gram), [-1] * count + [1] * count)
    assert not algebra.is_degenerate
    assert all(vector * vector == 0 for vector in vectors)
    for group in (values["ps"], values["qs"]):
        assert all(metric_inner_product(a, b) == 0 for a in group for b in group)
    for i, a in enumerate(vectors):
        for j, b in enumerate(values["reciprocal_vectors"]):
            assert metric_inner_product(a, b) == int(i == j)
    orthogonal = tuple(v for uv in zip(values["positive"], values["negative"]) for v in uv)
    matrix = np.column_stack([v.data[[1 << i for i in range(algebra.n)]] for v in orthogonal])
    np.testing.assert_allclose(matrix.T @ algebra.gram @ matrix, np.diag([1, -1] * count), atol=1e-12)
    np.testing.assert_allclose(outer_product(*orthogonal).data, (np.linalg.det(matrix) * algebra.I).data, atol=1e-12)
    # Every label denotes the actual native exterior word, not a GP in this oblique basis.
    table = algebra.bilinear_form_table(full=True)
    for mask in algebra.display_order:
        factors = [v for i, v in enumerate(vectors) if mask & (1 << i)]
        computed_blade = outer_product(*factors) if factors else algebra.identity
        assert algebra.blade(mask) == computed_blade
        assert emit(table.tree.headings[algebra.display_order.index(mask)], "latex") == computed_blade.latex(
            content="value"
        )
    assert_readable(outputs)


def test_witt_boost_scales_null_directions_and_preserves_pairing(witt_lesson):
    _, values, _, rapidity = witt_lesson
    algebra, p, q = values["witt"], values["ps"][0], values["qs"][0]
    K, R = values["boost_plane"], values["boost"]
    assert K == p ^ q and p * q == 1 + K
    assert K * K == 1
    np.testing.assert_allclose(R.data, (np.cosh(rapidity / 2) - np.sinh(rapidity / 2) * K).data, atol=1e-12)
    np.testing.assert_allclose(values["boosted_p"].data, (np.exp(-rapidity) * p).data, atol=1e-12)
    np.testing.assert_allclose(values["boosted_q"].data, (np.exp(rapidity) * q).data, atol=1e-12)
    assert float(metric_inner_product(values["boosted_p"], values["boosted_q"])) == pytest.approx(1)
    for v in values["null_vectors"][2:]:
        np.testing.assert_allclose((R * v * ~R).data, v.data, atol=1e-12)
    np.testing.assert_allclose((R * ~R).data, algebra.identity.data, atol=1e-12)
    fig = values["plot_null_boost"](values["boosted_sample"], p, q)
    np.testing.assert_allclose(fig.axes[0].collections[0].get_offsets()[-1], [np.exp(-rapidity), np.exp(rapidity)])


def test_witt_projector_matrix_and_cga_pga_duality_are_exact(witt_lesson):
    from galaga_matrix import from_matrix

    _, values, _, _ = witt_lesson
    p, q, f = values["p"], values["q"], values["projector"]
    assert p * p == q * q == 0
    assert f * f == f and p * f == 0 and q * f == q and p * (q * f) == 2 * f
    P, Q, F = (values[key].mat for key in ("p_matrix", "q_matrix", "projector_matrix"))
    np.testing.assert_allclose(P @ Q / 2, F, atol=1e-12)
    np.testing.assert_allclose(F @ F, F, atol=1e-12)
    np.testing.assert_allclose(from_matrix(values["projector_matrix"]).data, f.data, atol=1e-12)
    cga, pga = values["cga"], values["pga"]
    assert not cga.is_degenerate and pga.is_degenerate
    assert cga.I == outer_product(*cga.basis_vectors())
    assert cga.I * cga.I != 0 and pga.I * pga.I == 0
    with pytest.raises(ValueError, match="invertible pseudoscalar"):
        dual(pga.identity)
    for algebra in (cga, pga):
        for blade in algebra.blades(*algebra.display_order):
            assert blade ^ complement(blade) == algebra.I
            assert uncomplement(complement(blade)) == blade


def test_receiver_frequencies_follow_the_observer_not_an_active_signal_boost(witt_lesson):
    _, v, _, eta = witt_lesson
    U, u, s = v["receiver_time"], v["positive"][0], v["negative"][0]
    np.testing.assert_allclose(U.data, (np.cosh(eta) * u + np.sinh(eta) * s).data, atol=1e-12)
    for wave, frequency, scale in (
        (v["right_signal"], v["right_frequency"], np.exp(-eta)),
        (v["left_signal"], v["left_frequency"], np.exp(eta)),
    ):
        np.testing.assert_allclose((wave * wave).data, 0, atol=1e-12)
        assert float(metric_inner_product(wave, u)) == pytest.approx(1)
        assert float(metric_inner_product(wave, U)) == pytest.approx(scale)
        assert frequency == pytest.approx(scale)
        observer_components = v["boost"] * wave * ~v["boost"]
        assert float(metric_inner_product(observer_components, u)) == pytest.approx(frequency)
    assert v["right_frequency"] * v["left_frequency"] == pytest.approx(1)
    if eta > 0:
        assert v["right_frequency"] < 1 < v["left_frequency"]
    elif eta < 0:
        assert v["left_frequency"] < 1 < v["right_frequency"]


def test_occupation_actions_derive_fermion_signs_counting_and_energies(witt_lesson):
    _, v, count, _ = witt_lesson
    vacuum, states = v["vacuum"], v["occupation_states"]
    matrix = v["occupation_action_matrix"]
    basis = np.column_stack([state.data for state in states])
    assert np.linalg.matrix_rank(basis) == 2**count
    np.testing.assert_allclose((vacuum * vacuum).data, vacuum.data, atol=1e-12)
    for i, (a, c, number) in enumerate(zip(v["annihilators"], v["creators"], v["number_operators"])):
        A, C, N = (matrix(operator, states) for operator in (a, c, number))
        np.testing.assert_allclose(A.T, C, atol=1e-12)
        np.testing.assert_allclose((a * vacuum).data, 0, atol=1e-12)
        for j, (other_a, other_c) in enumerate(zip(v["annihilators"], v["creators"])):
            np.testing.assert_allclose((a * other_c + other_c * a).data, v["witt"].scalar(int(i == j)).data, atol=1e-12)
            np.testing.assert_allclose((c * other_c + other_c * c).data, 0, atol=1e-12)
            np.testing.assert_allclose((a * other_a + other_a * a).data, 0, atol=1e-12)
        for mask, state in enumerate(states):
            occupied = (mask >> i) & 1
            sign = (-1) ** ((mask & ((1 << i) - 1)).bit_count())
            expected_create = np.zeros(2**count)
            expected_annihilate = np.zeros(2**count)
            if not occupied:
                expected_create[mask | (1 << i)] = sign
            else:
                expected_annihilate[mask ^ (1 << i)] = sign
            np.testing.assert_allclose(C[:, mask], expected_create, atol=1e-12)
            np.testing.assert_allclose(A[:, mask], expected_annihilate, atol=1e-12)
            np.testing.assert_allclose((number * state).data, (occupied * state).data, atol=1e-12)
            assert N[mask, mask] == pytest.approx(occupied)
    energies = [sum(e * ((mask >> i) & 1) for i, e in enumerate(v["mode_energies"])) for mask in range(2**count)]
    np.testing.assert_allclose(v["energy_matrix"], np.diag(energies), atol=1e-12)
    # The ideal basis is not assigned a Hilbert norm by the indefinite GA metric.
    assert all(np.isfinite(v["energy_matrix"].flat))


@pytest.mark.parametrize(
    "count,bits,mode,action",
    (
        (1, "0", 1, "Create"),
        (1, "1", 1, "Create"),
        (2, "10", 2, "Create"),
        (2, "01", 1, "Create"),
        (3, "110", 3, "Create"),
        (3, "100", 3, "Create"),
        (2, "00", 1, "Annihilate"),
        (2, "11", 2, "Annihilate"),
        (3, "101", 2, "Count"),
        (3, "101", 3, "Count"),
    ),
)
def test_occupation_controls_show_computed_states_including_forbidden_actions(count, bits, mode, action):
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_matrix")
    outputs, v = runpy.run_path(str(WITT))["app"].run(
        defs={
            "pair_count": SimpleNamespace(value=count),
            "rapidity_control": SimpleNamespace(value=0.7),
            "occupation_control": SimpleNamespace(value=bits),
            "mode_control": SimpleNamespace(value=mode),
            "action_control": SimpleNamespace(value=action),
        }
    )
    index = sum(int(bit) << i for i, bit in enumerate(bits))
    assert v["input_index"] == index
    assert v["selected_mode"] == mode - 1
    basis = np.column_stack([state.data for state in v["occupation_states"]])
    np.testing.assert_allclose((basis @ v["action_column"])[:, 0], v["action_state"].data, atol=1e-12)
    occupied = int(bits[mode - 1])
    forbidden = (action == "Create" and occupied) or (action != "Create" and not occupied)
    if forbidden:
        np.testing.assert_allclose(v["action_column"], 0, atol=1e-12)
        assert "not the vacuum" in v["transition_description"]
    else:
        target_bits = list(bits)
        if action != "Count":
            target_bits[mode - 1] = "1" if action == "Create" else "0"
        sign = "-" if action != "Count" and sum(map(int, bits[: mode - 1])) % 2 else "+"
        assert v["transition_description"] == sign + "|" + "".join(target_bits) + ">"
    assert v["input_energy"] == pytest.approx(sum((i + 1) * int(bit) for i, bit in enumerate(bits)))
    assert_readable(outputs)


@pytest.fixture(
    scope="module",
    params=[(70, 30), (30, 70), (0, 60), (60, 0), (0, 0), (60, 60), (60, -60), (-100, 100), (100, 95)],
)
def rotor_lesson(request):
    pytest.importorskip("marimo")
    a, b = request.param
    outputs, values = runpy.run_path(str(ROTORS))["app"].run(
        defs={
            "angle12": SimpleNamespace(value=a),
            "angle34": SimpleNamespace(value=b),
            "ambiguity_angle": SimpleNamespace(value=35),
        }
    )
    return outputs, values, a, b


def test_rotor_log_sandwich_and_plane_extraction_follow_angles(rotor_lesson):
    outputs, v, a, b = rotor_lesson
    algebra, R, B = v["algebra"], v["rotor"], v["recovered"]
    np.testing.assert_allclose(exp(v["principal_log"]).data, R.data, rtol=0, atol=1e-12)
    np.testing.assert_allclose(v["principal_log"].data, v["generator"].data, rtol=0, atol=1e-12)
    expected_wedge = np.deg2rad(a) * np.deg2rad(b) / 2 * algebra.I
    np.testing.assert_allclose((B ^ B).data, expected_wedge.data, atol=1e-12)
    assert bool(v["simple"]) == (a == 0 or b == 0)
    if abs(a) == abs(b):
        assert v["pieces"] is None
        assert ("Zero" if a == 0 else "Isoclinic") in v["decomposition_status"]
    else:
        first, second = v["pieces"]
        np.testing.assert_allclose((first + second).data, B.data, atol=1e-12)
        for part in (first, second):
            np.testing.assert_allclose((part ^ part).data, 0, atol=1e-10)
        np.testing.assert_allclose((first * second - second * first).data, 0, atol=1e-10)
        assert float(metric_inner_product(first, second)) == pytest.approx(0, abs=1e-10)
        np.testing.assert_allclose((exp(first) * exp(second)).data, R.data, atol=1e-10)
    fig = v["plot_two_planes"](B, v["input_vector"])
    for ax, indices in zip(fig.axes, ([1, 2], [4, 8])):
        x, y = ax.lines[0].get_data()
        np.testing.assert_allclose([x[-1], y[-1]], v["output_vector"].data[indices], atol=1e-12)
    assert_readable(outputs)


def test_self_dual_correction_and_metric_independent_simplicity(rotor_lesson):
    _, v, a, b = rotor_lesson
    B, plus, minus = v["recovered"], v["self_dual"], v["anti_self_dual"]
    np.testing.assert_allclose((-dual(plus)).data, plus.data, atol=1e-12)
    np.testing.assert_allclose((-dual(minus)).data, -minus.data, atol=1e-12)
    assert v["plus_norm"] - v["minus_norm"] == pytest.approx(float((B ^ B) / v["algebra"].I), abs=1e-12)
    if (a == 0) != (b == 0):
        assert v["plus_norm"] > 0 and v["minus_norm"] > 0
        assert v["plus_norm"] == pytest.approx(v["minus_norm"])
    if a == b != 0:
        assert v["minus_norm"] == pytest.approx(0, abs=1e-12)
        assert not v["simple"]
    assert v["simple_six"] ^ v["simple_six"] == 0
    assert v["nonsimple_six"] ^ v["nonsimple_six"] != 0
    N = v["null_nonsimple"]
    assert N ^ N != 0
    assert metric_inner_product(N ^ N, N ^ N) == 0


def test_decomposition_is_not_hardcoded_to_coordinate_planes(rotor_lesson):
    _, v, _, _ = rotor_lesson
    algebra, split = v["algebra"], v["decompose_4d"]
    change = exp(0.31 * algebra.blade(5) - 0.19 * algebra.blade(10) + 0.11 * algebra.blade(9))
    B = change * (0.73 * v["plane12"] - 0.29 * v["plane34"]) * ~change
    B = grade(B, 2)
    pieces, _, _ = split(B)
    assert pieces is not None
    np.testing.assert_allclose(pieces[0].data, (change * (0.73 * v["plane12"]) * ~change).data, atol=1e-10)
    np.testing.assert_allclose(pieces[1].data, (change * (-0.29 * v["plane34"]) * ~change).data, atol=1e-10)
    close = 0.5 * v["plane12"] + (0.5 + 1e-9) * v["plane34"]
    assert split(close)[0] is None


@pytest.mark.parametrize("phi", (0, 30, 45, 90))
def test_isoclinic_planes_change_while_the_rotor_stays_the_same(phi):
    pytest.importorskip("marimo")
    _, v = runpy.run_path(str(ROTORS))["app"].run(
        defs={
            "angle12": SimpleNamespace(value=60),
            "angle34": SimpleNamespace(value=60),
            "ambiguity_angle": SimpleNamespace(value=phi),
        }
    )
    first, second = v["alternative_plane1"], v["alternative_plane2"]
    np.testing.assert_allclose((first ^ first).data, 0, atol=1e-12)
    np.testing.assert_allclose((second ^ second).data, 0, atol=1e-12)
    np.testing.assert_allclose((first + second).data, (v["plane12"] + v["plane34"]).data, atol=1e-12)
    np.testing.assert_allclose(v["alternative_rotor"].data, v["iso_rotor"].data, atol=1e-12)
    if 0 < phi < 90:
        assert not np.allclose(first.data, v["plane12"].data)
