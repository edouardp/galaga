"""Execute the reversion teaching notebook headlessly."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "reversion_explained.py"


@pytest.fixture(scope="module")
def lesson():
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    return outputs, definitions


def test_reversion_swaps_the_factors_without_a_sign(lesson) -> None:
    _, definitions = lesson
    assert (~definitions["R"]).almost_equal(definitions["v2"] * definitions["v1"])
    assert definitions["factor_R_view"].latex().count(r"\underbrace") == 1
    assert r"v_2 v_1" in definitions["factor_reverse_view"].latex()


def test_simple_vector_bivector_and_trivector_reverse_signs(lesson) -> None:
    _, definitions = lesson
    assert definitions["simple_reverse_checks"] == (True, True, True)
    assert definitions["simple_vector_reverse"].almost_equal(definitions["simple_vector"])
    assert definitions["simple_bivector_reverse"].almost_equal(-definitions["simple_bivector"])
    assert definitions["simple_trivector_reverse"].almost_equal(-definitions["simple_trivector"])


def test_reversion_labels_the_scalar_and_bivector_parts(lesson) -> None:
    _, definitions = lesson
    assert definitions["product_split"].almost_equal(definitions["R"])
    assert definitions["swapped_split"].almost_equal(~definitions["R"])
    product = definitions["product_split_view"].latex()
    assert "unchanged by reverse" in product and "changes sign" in product
    assert "reversed" in definitions["swapped_split_view"].latex()


def test_reverse_is_not_negation_in_general(lesson) -> None:
    _, definitions = lesson
    assert definitions["reverse_is_negation"] is False
    assert "negated" in definitions["negated_view"].latex()
    assert "unchanged" in definitions["reverse_value_view"].latex()


def test_orthogonal_vectors_make_reverse_equal_negation() -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(defs={"angle": SimpleNamespace(value=90)})
    assert definitions["reverse_is_negation"] is True
    assert abs(float(definitions["inner_product"])) < 1e-9


def test_two_reflection_formula_brackets_the_rotor_and_its_reverse(lesson) -> None:
    _, definitions = lesson
    assert definitions["unit_rotor_reverse_product"] is True
    rendered = definitions["two_reflections_view"].latex()
    assert r"\underbrace" in rendered
    assert r"\widetilde R" in rendered
    assert r"R^{-1}" not in rendered


def test_inverse_is_a_distinct_partial_involution_that_survives_degeneracy(lesson) -> None:
    _, definitions = lesson
    assert definitions["scaled_reverse_differs_from_inverse"] is True
    assert definitions["inverse_round_trip"] is True
    assert definitions["pga_unit_inverse_is_expected"] is True
    assert definitions["pga_unit_product_is_one"] is True
    assert definitions["pga_inverse_round_trip"] is True
    assert definitions["pga_null_inverse_error"] == "multivector is not invertible"

    assert not definitions["scaled_rotor_reverse"].almost_equal(definitions["scaled_rotor_inverse"])
    assert definitions["factor_reverse_view"].latex().find(r"R^{-1}") == -1


def test_high_grade_reverse_sign_pattern(lesson) -> None:
    _, definitions = lesson
    assert definitions["kept_grades"] == (0, 1, 4, 5)
    assert definitions["flipped_grades"] == (2, 3, 6)
    assert definitions["grade_signs_match"] is True
    assert definitions["pseudoscalar_flips"] is True

    assert definitions["M"].latex(content="full").startswith("M \\quad = \\quad")
    assert definitions["reverse_M"].latex(content="full").startswith("\\widetilde{M} \\quad = \\quad")

    highlighted = definitions["highlighted_reverse"].latex()
    for grade in range(7):
        assert f"grade {grade}" in highlighted
    assert r"\rule[0.2em]{0.4pt}{1em}" in highlighted
    assert r"\colorbox{#FDE7D9}{$" in highlighted
    assert highlighted.count(r"\colorbox{#FDE7D9}") == 2
    assert r"\colorbox{#FDE7D9}{$-$}" not in highlighted
    reservation, visible = highlighted.split(r"\mathrlap", maxsplit=1)
    assert r"\colorbox" not in reservation
    final_fill = visible.rsplit(r"\colorbox{#FDE7D9}", maxsplit=1)[1]
    assert r"\textcolor{#D55E00}{-" in final_fill
    assert r"2.8 e_{123456}" in final_fill


def test_general_reversion_law_reverses_and_transforms_both_factors(lesson) -> None:
    _, definitions = lesson
    assert definitions["reverse_product_law"] is True
    assert definitions["reverse_is_not_plain_factor_swap"] is True


def test_grade_involution_is_an_automorphism_with_odd_grades_flipped(lesson) -> None:
    _, definitions = lesson
    assert definitions["grade_involution_grade_signs"] == (1, -1, 1, -1, 1, -1, 1)
    assert definitions["grade_involution_flipped_grades"] == (1, 3, 5)
    assert definitions["grade_involution_product_law"] is True

    rendered = definitions["highlighted_grade_involution"].latex()
    assert r"\colorbox{#FFF3CD}" in rendered
    for grade in range(7):
        assert f"grade {grade}" in rendered


def test_clifford_conjugation_combines_parity_and_order_reversal(lesson) -> None:
    _, definitions = lesson
    assert definitions["clifford_conjugate_grade_signs"] == (1, -1, -1, 1, 1, -1, -1)
    assert definitions["clifford_conjugate_flipped_grades"] == (1, 2, 5, 6)
    assert definitions["conjugation_is_composition"] is True
    assert definitions["clifford_conjugate_product_law"] is True

    rendered = definitions["highlighted_clifford_conjugate"].latex()
    assert r"\colorbox{#E8DDF5}" in rendered
    for grade in range(7):
        assert f"grade {grade}" in rendered


def test_all_three_operations_are_involutions_and_match_the_grade_formulas(lesson) -> None:
    _, definitions = lesson
    assert definitions["sign_formulas_match"] is True
    assert definitions["involution_round_trips"] == {
        "grade involution": True,
        "reversion": True,
        "Clifford conjugation": True,
    }
    assert definitions["all_round_trips"] is True
