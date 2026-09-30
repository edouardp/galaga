"""Concrete v2 display policies, with v1-only formatting recorded in the archive."""

from __future__ import annotations

import numpy as np
import pytest

from galaga import Algebra, DisplayPolicy, exp, p_cga, p_sta, presets


@pytest.mark.parametrize(
    ("algebra", "expected"),
    (
        (Algebra(3, 0, 1), "Algebra(p=3, q=0, r=1) [n=4, is_degenerate=True]"),
        (Algebra(2, 1), "Algebra(p=2, q=1, r=0) [n=3]"),
        (Algebra(sig=[1, 1, 1, 0]), "Algebra(sig=[1, 1, 1, 0]) [n=4, is_degenerate=True]"),
        (Algebra(sig=[1, 0, -1]), "Algebra(sig=[1, 0, -1]) [n=3, is_degenerate=True]"),
        (Algebra(sig=[0, 1, -1]), "Algebra(p=1, q=1, r=1) [n=3, is_degenerate=True]"),
        (Algebra(gram=[[0, 0], [0, 1]]), "Algebra(p=1, q=0, r=1) [n=2, is_degenerate=True]"),
        (Algebra(gram=[[1, 0], [0, 0]]), "Algebra(sig=[1, 0]) [n=2, is_degenerate=True]"),
        (
            Algebra(gram=[[1, 0, -1], [0, 1, 0], [-1, 0, 1]]),
            "Algebra(gram=[[1, 0, -1], [0, 1, 0], [-1, 0, 1]]) [n=3, is_degenerate=True, non_diagonal=True]",
        ),
        (Algebra(gram=[[2, 0], [0, -1]]), "Algebra(gram=[[2, 0], [0, -1]]) [n=2]"),
        (Algebra(0), "Algebra(p=0, q=0, r=0) [n=0]"),
    ),
)
def test_algebra_repr_uses_the_stored_metric_and_derived_annotations(algebra, expected) -> None:
    assert repr(algebra) == expected
    assert ("is_degenerate=True" in repr(algebra)) == algebra.is_degenerate
    assert ("non_diagonal=True" in repr(algebra)) == (not algebra.is_orthogonal_basis)
    assert "object at" not in repr(algebra)


def test_algebra_rich_repr_displays_gram_as_an_inline_matrix() -> None:
    algebra = Algebra(gram=[[1, 0.125], [0.125, -2]])

    assert repr(algebra) == "Algebra(gram=[[1, 0.125], [0.125, -2]]) [n=2, non_diagonal=True]"
    assert algebra._repr_latex_() == (
        r"$\operatorname{Algebra}\!\left(\mathrm{gram}=\left["
        r"\begin{smallmatrix}1 & 0.125 \\ 0.125 & -2\end{smallmatrix}"
        r"\right]\right)\;\left[\mathrm{n}=2,\;\mathrm{non\_diagonal}=\mathrm{True}\right]$"
    )


def test_gram_latex_colours_only_exact_zeros_like_the_product_tables() -> None:
    algebra = Algebra(gram=[[2, 0], [0, -1]])
    grey_zero = r"{\color{#bbbbbb}0}"

    assert grey_zero in algebra.wedge_product_table().latex()
    assert algebra._repr_latex_().count(grey_zero) == int(np.count_nonzero(algebra.gram == 0))
    assert repr(algebra) == "Algebra(gram=[[2, 0], [0, -1]]) [n=2]"

    tiny_nonzero = Algebra(gram=[[2, 1e-12], [1e-12, -1]])
    assert grey_zero not in tiny_nonzero._repr_latex_()
    assert r"10^{-12}" in tiny_nonzero._repr_latex_()


def test_oblique_algebra_and_bilinear_table_share_display_precision() -> None:
    default = Algebra(config=presets.oblique_plane(degrees=30))
    concise = Algebra(config=presets.oblique_plane(degrees=30), display=DisplayPolicy(coefficient_precision=3))

    assert "0.866025" in default._repr_latex_()
    assert "0.866025" in default.bilinear_form_table().latex()
    assert "0.8660254037844387" not in default._repr_latex_()
    assert "0.866" in concise._repr_latex_()
    assert "0.866" in concise.bilinear_form_table().latex()
    assert "0.866025" not in concise._repr_latex_()
    assert "0.866025" not in concise.bilinear_form_table().latex()
    assert "0.866" in repr(concise)


@pytest.mark.parametrize("counts", ((2, 0, 1), (0, 1, 0), (0, 0, 0)))
def test_pqr_latex_colours_zero_counts_without_changing_the_plain_repr(counts) -> None:
    algebra = Algebra(*counts)
    grey_prefix = r"{\color{#bbbbbb}"
    labels = dict(zip(("p", "q", "r"), counts, strict=True))

    assert algebra._repr_latex_().count(grey_prefix) == counts.count(0)
    for label, count in labels.items():
        shown = f"{grey_prefix}{label}=0}}" if count == 0 else f"{label}={count}"
        assert shown in algebra._repr_latex_()
        assert f"{label}={count}" in repr(algebra)
    assert grey_prefix not in repr(algebra)


def test_algebra_rich_repr_preserves_signature_order_and_view_metric() -> None:
    algebra = Algebra(sig=[1, 1, 1, 0])
    view = Algebra.from_numeric(algebra.numeric)

    assert view._repr_latex_() == (
        r"$\operatorname{Algebra}\!\left(\mathrm{sig}=\left[1, 1, 1, 0\right]\right)"
        r"\;\left[\mathrm{n}=4,\;\mathrm{is\_degenerate}=\mathrm{True}\right]$"
    )
    assert repr(view) == repr(algebra)


def test_cga_reports_its_non_diagonal_stored_gram_without_claiming_degeneracy() -> None:
    algebra = Algebra(config=p_cga())

    assert not algebra.is_degenerate
    assert not algebra.is_orthogonal_basis
    assert repr(algebra).startswith("Algebra(gram=[[0, 0, 0, 0, -1],")
    assert repr(algebra).endswith("[n=5, non_diagonal=True]")
    assert "is_degenerate" not in repr(algebra)


def test_multivector_repr_is_ascii_while_str_uses_unicode() -> None:
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    value = 3 + 2 * e1 - e2
    assert repr(value) == value.ascii() == "3 + 2e1 - e2"
    assert str(value) == value.unicode() == "3 + 2e₁ - e₂"
    assert repr(algebra.scalar(0)) == str(algebra.scalar(0)) == "0"
    g0, g1, _, _ = Algebra(config=p_sta()).basis_vectors()
    assert repr(g0 * g1) == "g0g1"
    assert str(g0 * g1) == "γ₀γ₁"


@pytest.mark.parametrize("target, expected", (("unicode", "2e₁ + e₂"), ("ascii", "2e1 + e2")))
def test_ipython_plain_text_uses_the_selected_multivector_target(target, expected) -> None:
    formatters = pytest.importorskip("IPython.core.formatters")
    algebra = Algebra(2, display=DisplayPolicy(target=target))
    e1, e2 = algebra.basis_vectors()
    value = 2 * e1 + e2

    formatted, _ = formatters.DisplayFormatter().format(value)

    assert formatted["text/plain"] == expected
    assert repr(value) == "2e1 + e2"
    assert formatted["text/latex"] == value._repr_latex_()


@pytest.mark.parametrize("precision, expected", ((4, "3.142e₁ + 2.718e₂"), (2, "3.1e₁ + 2.7e₂")))
def test_display_policy_controls_significant_digits_without_changing_coefficients(
    precision: int, expected: str
) -> None:
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    value = 3.14159 * e1 + 2.71828 * e2
    data = value.data.copy()
    presentation = algebra.presentation.with_display(DisplayPolicy(coefficient_precision=precision))
    assert value.display("value/unicode", presentation=presentation) == expected
    assert str(value) == "3.14159e₁ + 2.71828e₂"
    np.testing.assert_array_equal(value.data, data)


def test_scalar_and_zero_use_significant_digits_without_fixed_decimal_padding() -> None:
    algebra = Algebra(3, display=DisplayPolicy(coefficient_precision=3))
    assert str(algebra.scalar(3.14159)) == "3.14"
    assert str(algebra.scalar(0)) == "0"
    # Significant digits are not a replacement spelling for decimal places.
    assert str(algebra.scalar(0.00123456)) == "0.00123"
    assert str(algebra.scalar(12345.6)) == "1.23e+04"


@pytest.mark.parametrize("spec", (".0f", ".1f", ".2f", ".3f"))
def test_legacy_numeric_multivector_format_specs_are_not_v2_semantic_specs(spec: str) -> None:
    for value in (Algebra(1).scalar(3.14159), Algebra(1).scalar(0), Algebra(1).blade(1)):
        with pytest.raises(ValueError, match="format specification must be"):
            format(value, spec)


def test_semantic_format_targets_delegate_to_their_renderers() -> None:
    e1, _, _ = Algebra(3).basis_vectors()
    assert f"{e1}" == f"{e1:unicode}" == str(e1)
    assert f"{e1:latex}" == e1.latex() == r"e_{1}"
    assert f"{e1:ascii}" == "e1"


def test_mixed_value_formatting_keeps_signs_and_all_components() -> None:
    algebra = Algebra(3, display=DisplayPolicy(coefficient_precision=1))
    e1, e2, _ = algebra.basis_vectors()
    value = 1 + 2 * e1 - 3 * (e1 ^ e2)
    assert str(value) == "1 + 2e₁ - 3e₁₂"
    assert value.latex() == r"1 + 2 e_{1} - 3 e_{12}"


def test_near_minus_one_coefficients_are_suppressed_without_rounding_the_value() -> None:
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors(expr=True)
    generator = e1 ^ e2
    rotor = exp(-generator * np.pi / 2)
    transformed = rotor * (e1 + e2) * ~rotor
    assert transformed.expr is not None
    np.testing.assert_allclose(transformed.data, (-e1 - e2).data, atol=1e-12, rtol=0)
    original = transformed.data.copy()
    assert transformed.unicode(content="value") == "-e₁ - e₂"
    assert transformed.latex(content="value") == r"-e_{1} - e_{2}"
    # Also pin the floating-point boundary independently of platform libm.
    neighbor = algebra.multivector([0, -1.0, np.nextafter(-1.0, 0.0), 0, 0, 0, 0, 0])
    assert neighbor != -e1 - e2
    assert str(neighbor) == "-e₁ - e₂"
    precise = algebra.presentation.with_display(DisplayPolicy(coefficient_precision=17, zero_tolerance=0))
    assert neighbor.display("value/ascii", presentation=precise) == "-e1 - 0.99999999999999989e2"
    np.testing.assert_array_equal(transformed.data, original)
