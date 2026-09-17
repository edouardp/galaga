"""Annotated views: transparency, formatting and presenter integration."""

from __future__ import annotations

import numpy as np
import pytest

import galaga_annotation as ga
from galaga import Algebra, PresentedMultivector, metric_inner_product, presets


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
