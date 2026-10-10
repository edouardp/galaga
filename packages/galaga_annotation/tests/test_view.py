"""Annotated views: transparency, formatting and presenter integration."""

from __future__ import annotations

import numpy as np
import pytest

import galaga_annotation as ga
from galaga import Algebra, DisplayOrder, PresentedMultivector, Presenter, metric_inner_product, presets


def _value():
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    return algebra, e1 + e2


def test_views_are_numerically_transparent() -> None:
    _, mv = _value()
    view = ga.annotate(mv, label="both")
    assert view.plain is mv
    assert view.value is mv
    assert view.plain == mv
    data = mv.data.copy()
    view.latex()
    np.testing.assert_array_equal(mv.data, data)


def test_views_have_no_arithmetic() -> None:
    _, mv = _value()
    view = ga.annotate(mv, label="both")
    for operation in (lambda: view + view, lambda: view * 2, lambda: -view):
        with pytest.raises(TypeError):
            operation()


def test_plain_text_targets_ignore_annotations() -> None:
    _, mv = _value()
    view = ga.annotate(mv, label="both")
    assert view.unicode() == mv.display(target="unicode")
    assert view.ascii() == mv.display(target="ascii")
    assert str(view) == mv.display(target="unicode")
    assert repr(view) == mv.display(target="ascii")


def test_format_specs_route_latex_through_the_renderer() -> None:
    _, mv = _value()
    view = ga.annotate(mv, label="both")
    assert format(view, "latex") == view.latex()
    assert format(view, "value/latex") == view.latex()
    assert view.display("unicode") == mv.display(target="unicode")
    assert view._repr_latex_() == "$" + view.latex() + "$"
    with pytest.raises(ValueError, match="conflicts"):
        view.display("value/latex", target="unicode")


def test_presented_values_keep_their_captured_presentation() -> None:
    algebra = Algebra(2, expr=True)
    e1, _ = algebra.basis_vectors(expr=True)
    presented = presets.presenters.lengyel()(metric_inner_product(e1, e1))
    view = ga.annotate(presented, label="pairing")
    rendered = view.latex()
    assert r"\bullet" in rendered
    assert r"\overset{\text{pairing}}" in rendered
    assert view.plain is presented.value


def test_ordinary_presenters_compose_through_the_adapter_protocol() -> None:
    _, mv = _value()
    view = ga.annotate(mv, label="both")
    composed = presets.presenters.functional()(view)
    assert isinstance(composed, ga.Annotated)
    assert composed.rules == view.rules
    assert composed.latex() == view.latex()


def test_composed_presenter_keeps_annotation_rules_and_blade_names() -> None:
    algebra = Algebra(3, expr=True)
    e1, e2, _ = algebra.basis_vectors()
    annotated = ga.annotate(e1 * e2, label="product")
    presenter = presets.presenters.short_functional() | presets.blades.indexed(3, prefix="v")

    for result in (presenter(annotated), ga.AnnotationPresenter(base=presenter)(annotated)):
        assert isinstance(result, ga.Annotated)
        assert result.rules == annotated.rules
        assert isinstance(result.value, PresentedMultivector)
        assert result.value.ascii() == "gp(v1, v2) = v12"


@pytest.mark.parametrize("representation", ["bivector", "vector"])
def test_complex_representations_preserve_annotation_rules_and_numeric_value(representation) -> None:
    algebra = Algebra(config=presets.complex(representation=representation), user_config_files=False)
    value = 2 + 3 * algebra.I
    annotated = ga.annotate(value, label="complex number")
    presenter = presets.presenters.values()

    for result in (presenter(annotated), ga.AnnotationPresenter(base=presenter)(annotated)):
        assert isinstance(result, ga.Annotated)
        assert result.rules == annotated.rules
        assert result.plain is value
        assert result.value.ascii() == "2 + 3i"
    assert algebra.locals()["i"] == algebra.I


@pytest.mark.parametrize("representation", ["bivector", "direct"])
def test_quaternion_representations_preserve_annotation_rules_and_numeric_value(representation) -> None:
    algebra = Algebra(config=presets.quaternion(representation=representation), user_config_files=False)
    i, j, k = algebra.blades("quaternion_i", "quaternion_j", "quaternion_k")
    value = 1 + 2 * i + 3 * j + 4 * k
    annotated = ga.annotate(value, label="quaternion")
    presenter = presets.presenters.values() | presets.blades.quaternion(representation=representation)

    for result in (presenter(annotated), ga.AnnotationPresenter(base=presenter)(annotated)):
        assert isinstance(result, ga.Annotated)
        assert result.rules == annotated.rules
        assert result.plain is value
        expected = "1 + 4k + 3j + 2i" if representation == "bivector" else "1 + 2i + 3j + 4k"
        assert result.value.ascii() == expected


def test_presenter_default_order_preserves_annotations_when_relabeling_quaternion_terms():
    algebra = Algebra(config=presets.quaternion(), user_config_files=False)
    i, j, _ = algebra.basis_blades(2)
    value = (1 + 3 * i + 2 * j) ** 2
    annotated = ga.annotator(
        ga.on(ga.term(i), label="i component"),
        ga.on(ga.term(j), label="j component"),
    )(value)
    presenter = Presenter(blades=presets.blades.indexed(3), content="value")

    for result in (presenter(annotated), ga.AnnotationPresenter(base=presenter)(annotated)):
        assert result.plain is value
        assert result.rules == annotated.rules
        assert result.value.presentation.display_order == DisplayOrder(3)
        assert result.value.latex() == r"-12 + 4 e_{13} + 6 e_{23}"
        assert "i component" in result.latex() and "j component" in result.latex()


def test_pseudoscalar_patch_preserves_annotation_rules_and_numeric_value() -> None:
    algebra = Algebra(0, 1, user_config_files=False)
    value = 2 + 3 * algebra.I
    annotated = ga.annotate(value, label="complex number")
    presenter = presets.presenters.values() | presets.blades.pss("i")

    for result in (presenter(annotated), ga.AnnotationPresenter(base=presenter)(annotated)):
        assert isinstance(result, ga.Annotated)
        assert result.rules == annotated.rules
        assert result.plain is value
        assert result.value.ascii() == "2 + 3i"
    assert value.display("value/ascii") == "2 + 3e1"


def test_repr_paths_render_one_marimo_math_block() -> None:
    mo = pytest.importorskip("marimo")
    _, mv = _value()
    view = ga.annotate(mv, background="#e8f5e9", label="highlight")
    assert r"\colorbox{#e8f5e9}{$" in view.latex()
    # Inline LaTeX stays the default representation for other consumers ...
    assert view._repr_latex_().startswith("$") and view._repr_latex_().endswith("$")
    # ... while rich display hands Marimo one intact inline math block.
    html = mo.as_html(view).text
    assert html.count("<marimo-tex") == 1
    assert html.count("</marimo-tex>") == 1
    assert "||(" in html


def test_repr_html_escapes_trusted_latex_at_the_markup_boundary() -> None:
    pytest.importorskip("marimo")
    _, mv = _value()
    payload = r"</marimo-tex><img src=x onerror=alert(1)>"
    html = ga.annotate(mv, label_latex=payload)._repr_html_()
    assert html is not None
    assert payload not in html
    assert "&lt;/marimo-tex&gt;&lt;img" in html
    assert html.count("</marimo-tex>") == 1


def test_annotation_presenter_applies_the_base_and_keeps_rules() -> None:
    _, mv = _value()
    view = ga.annotate(mv, label="both")
    presenter = ga.AnnotationPresenter(base=presets.presenters.functional())
    presented = presenter(view)
    assert isinstance(presented, ga.Annotated)
    assert presented.rules == view.rules
    assert isinstance(presented.value, PresentedMultivector)


def test_annotation_presenter_passes_plain_values_to_its_base() -> None:
    _, mv = _value()
    presenter = ga.AnnotationPresenter(base=presets.presenters.default())
    assert not isinstance(presenter(mv), ga.Annotated)
