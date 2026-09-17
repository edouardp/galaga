"""Presenter contracts: compute first, then compare independent display views."""

import sys
from dataclasses import FrozenInstanceError, replace

import numpy as np
import pytest

import galaga as ga
from galaga import (
    Algebra,
    DisplayOrder,
    DisplayPolicy,
    LocalNamePolicy,
    PresentedMultivector,
    Presenter,
    metric_inner_product,
    presets,
)


def test_metric_pairing_view_uses_actual_product_without_mutating_provenance():
    algebra = Algebra(config=presets.euclidean(3), expr=True)
    e1, _, _ = algebra.basis_vectors()
    value = metric_inner_product(e1, e1)
    numeric, expression, presentation = value.numeric, value.expr, algebra.presentation
    view = presets.presenters.lengyel()(value)
    assert view.value is value and value.numeric is numeric and value.expr is expression
    assert value == algebra.scalar(algebra.gram[0, 0])
    assert view.latex() == r"e_{1} \mathbin{\bullet} e_{1} \quad = \quad 1"
    assert algebra.presentation is presentation
    assert r"\operatorname{metric\_inner\_product}" in value.latex()
    assert hash(view.value) == hash(value)
    assert ga.Presenter is ga.facade.Presenter
    assert ga.PresentedMultivector is ga.facade.PresentedMultivector


def test_views_and_presenters_are_immutable_and_not_arithmetic():
    value = Algebra(2).identity
    presenter = Presenter()
    view = presenter(value)
    with pytest.raises(FrozenInstanceError):
        presenter.content = "value"
    with pytest.raises(FrozenInstanceError):
        view.presentation = value.algebra.presentation
    with pytest.raises(TypeError):
        _ = view + view
    assert view.value + view.value == 2
    assert replace(presenter, content="full").content == "full"
    assert presenter.content is None


def test_presenter_binds_on_application_view_ignores_later_scopes():
    algebra = Algebra(2, expr=True)
    e1, e2 = algebra.basis_vectors()
    value = e1 ^ e2
    presenter = Presenter()
    baseline = value.latex()
    with algebra.use_notation(presets.notation.functional()):
        view = presenter(value)
        captured = value.latex()
    assert view.latex() == captured != baseline
    with algebra.use_notation(presets.notation.lengyel()):
        assert view.latex() == captured
    assert presenter(value).latex() == baseline
    assert view.display(target="latex", presentation=algebra.presentation) == baseline
    assert ga.render(view, target="latex", presentation=algebra.presentation) == baseline


@pytest.mark.parametrize("preset", [presets.euclidean(3), presets.cga(2), presets.rga(), presets.sta()])
def test_portable_recipe_inherits_each_algebras_blades_and_order(preset):
    algebra = Algebra(config=preset, expr=True)
    a, b, *_ = algebra.basis_vectors()
    value = a ^ b
    view = presets.presenters.functional()(value)
    assert view.presentation.blades is algebra.presentation.blades
    assert view.presentation.display_order is algebra.presentation.display_order
    assert view.presentation.local_names is algebra.presentation.local_names
    assert view.latex() == value.latex(notation=presets.notation.functional())


@pytest.mark.parametrize("n", [0, 1, 3, 4])
@pytest.mark.parametrize("order", ["grade-lexicographic", "bitmap"])
def test_order_recipes_resolve_per_dimension_without_changing_native_data(n, order):
    algebra = Algebra(n)
    value = algebra.multivector(range(1, (1 << n) + 1))
    original = value.data.copy()
    view = Presenter(display_order=order)(value)
    expected = DisplayOrder(n, range(1 << n)) if order == "bitmap" else DisplayOrder(n)
    assert view.presentation.display_order == expected
    assert view.latex() == value.latex(presentation=algebra.presentation.with_display_order(expected))
    np.testing.assert_array_equal(value.data, original)
    assert view.value.numeric is value.numeric


@pytest.mark.parametrize("signature", ["mostly-minus", "mostly-plus"])
def test_metric_derived_sta_labels_match_the_actual_products(signature):
    algebra = Algebra(config=presets.sta(signature))
    time, *space = algebra.basis_vectors()
    presenter = Presenter(blades=presets.blades.sta(sigmas=True))
    for i, vector in enumerate(space, 1):
        product = vector * time
        view = presenter(product)
        ref = view.presentation.blades.resolve(f"s{i}")
        assert algebra.blade(ref) == product
        assert view.latex() == rf"\sigma_{{{i}}}"
        assert view.value is product
        assert product == -time * vector


def test_reversed_rga_blade_keeps_its_computed_sign():
    algebra = Algebra(config=presets.rga())
    convention = algebra.presentation.blades
    ref = convention.resolve("e31")
    # Identify the factors through the original convention, not mask guesses.
    reversed_product = algebra.blade("e3") ^ algebra.blade("e1")
    assert reversed_product == algebra.blade(ref)
    ordinary = Presenter(blades=presets.blades.indexed(4))
    view = ordinary(reversed_product)
    assert view.value == reversed_product
    assert view.latex() == reversed_product.latex(
        presentation=algebra.with_blades(presets.blades.indexed(4)).presentation
    )
    native = algebra.blade(ref.mask)
    assert native == ref.orientation * reversed_product
    assert Presenter()(native).latex().startswith("-")


def test_blade_style_is_exterior_not_geometric_product_in_an_oblique_basis():
    algebra = Algebra(gram=((1, 0.5), (0.5, 1)), expr=True)
    a, b = algebra.basis_vectors()
    assert a * b == 0.5 + (a ^ b)
    presenter = Presenter(blades=presets.blades.indexed(2, style="wedge"), content="value")
    assert presenter(a ^ b).latex() == r"e_{1} \wedge e_{2}"
    assert presenter(a * b).latex() == r"0.5 + e_{1} \wedge e_{2}"


def test_complete_presentation_components_and_content_precedence():
    algebra = Algebra(3, expr=True)
    a, b, _ = algebra.basis_vectors()
    value = a ^ b
    explicit = algebra.presentation.with_notation(presets.notation.functional())
    order = DisplayOrder(3, reversed(range(8)))
    locals_policy = LocalNamePolicy(3, {"u": 1})
    display = DisplayPolicy(content="expr", coefficient_precision=3, target="ascii")
    view = Presenter(
        presentation=explicit,
        blades=presets.blades.euclidean(3).resolve(algebra.gram),
        local_names=locals_policy,
        display_order=order,
        display=display,
        content="value",
    )(value)
    assert view.presentation.notation is explicit.notation
    assert view.presentation.local_names is locals_policy
    assert view.presentation.display_order is order
    assert view.presentation.display == replace(display, content="value")
    assert str(view) == value.ascii(content="value")
    assert "u" not in algebra.locals()
    assert value.expr is not None


def test_representing_a_view_inherits_its_snapshot_not_the_algebra_default():
    algebra = Algebra(2, expr=True)
    a, b = algebra.basis_vectors()
    value = a ^ b
    original = Presenter(notation=presets.notation.functional())(value)
    derived = Presenter(content="expr")(original)
    assert derived.value is value
    assert derived.presentation.notation is original.presentation.notation
    assert derived.latex() == value.latex(content="expr", notation=presets.notation.functional())
    assert original.presentation.display.content == "auto"


def test_render_protocols_and_explicit_value_content():
    algebra = Algebra(3, expr=True)
    a, b, c = algebra.basis_vectors()
    value = (a + b) ^ c
    view = Presenter()(value)
    for target in ("ascii", "unicode", "latex"):
        assert ga.render(view, target=target) == view.display(target=target)
        assert format(view, f"value/{target}") == value.display(content="value", target=target)
        assert ga.build_render_tree(view, target=target) == ga.build_render_tree(
            value, presentation=view.presentation, target=target
        )
    assert str(view) == format(view, "") == view.unicode()
    assert repr(view) == view.ascii()
    assert view._repr_latex_() == "$" + view.latex() + "$"
    assert view.latex(content="value") == r"e_{13} + e_{23}"
    with pytest.raises(ValueError, match="conflicts"):
        view.display("expr", content="value")


@pytest.mark.parametrize(
    "kwargs,exception",
    [
        ({"notation": "lengyel"}, TypeError),
        ({"presentation": 1}, TypeError),
        ({"blades": "sta"}, TypeError),
        ({"local_names": {}}, TypeError),
        ({"display": {}}, TypeError),
        ({"display_order": []}, TypeError),
        ({"display_order": "typo"}, ValueError),
        ({"content": "typo"}, ValueError),
    ],
)
def test_invalid_options_fail_at_construction(kwargs, exception):
    with pytest.raises(exception):
        Presenter(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"blades": presets.blades.sta()},
        {"display_order": DisplayOrder(4)},
        {"local_names": LocalNamePolicy(4, {})},
        {"presentation": Algebra(4).presentation},
        {"blades": presets.blades.cga(1)},  # Same dimension, wrong null Gram frame.
    ],
)
def test_incompatible_dimension_or_metric_fails_on_application(kwargs):
    with pytest.raises(ValueError):
        Presenter(**kwargs)(Algebra(3).identity)


@pytest.mark.parametrize("value", [None, 3, "x", object()])
def test_unsupported_values_fail_explicitly(value):
    with pytest.raises(TypeError, match="Multivector"):
        Presenter()(value)


def test_view_constructor_validates_value_and_presentation():
    algebra = Algebra(2)
    with pytest.raises(TypeError, match="Multivector"):
        PresentedMultivector(3, algebra.presentation)
    with pytest.raises(TypeError, match="PresentationConfig"):
        PresentedMultivector(algebra.identity, None)
    with pytest.raises(ValueError, match="dimension"):
        PresentedMultivector(algebra.identity, Algebra(3).presentation)


def test_presenter_presets_are_clean_and_match_their_documented_recipes():
    expected = {
        "default": Presenter(),
        "values": Presenter(content="value"),
        "full": Presenter(content="full"),
        "functional": Presenter(notation=presets.notation.functional()),
        "lengyel": Presenter(notation=presets.notation.lengyel()),
        "short_functional": Presenter(notation=presets.notation.functional_short()),
        "grade_order": Presenter(display_order="grade-lexicographic"),
        "bitmap_order": Presenter(display_order="bitmap"),
    }
    assert dir(presets.presenters) == sorted(expected) == presets.presenters.__all__
    for name, recipe in expected.items():
        assert getattr(presets.presenters, name)() == recipe
    assert presets.presenters.functional(short=True).notation == presets.notation.functional(short=True)
    assert presets.presenters.short_functional() == presets.presenters.functional(short=True)
    assert not any(name in vars(presets.presenters) for name in ("Presenter", "Notation", "Any", "dataclass"))


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Native t-strings require Python 3.14")
def test_marimo_templates_and_direct_rich_display_use_the_view_snapshot():
    mo = pytest.importorskip("marimo")
    gm = pytest.importorskip("galaga_marimo")
    algebra = Algebra(2, expr=True)
    e1, _ = algebra.basis_vectors()
    view = presets.presenters.lengyel()(metric_inner_product(e1, e1))
    with algebra.use_notation(presets.notation.functional()):
        for output in (mo.as_html(view), gm.md(eval('t"{view}"'))):
            assert r"\bullet" in output.text
        value_only = gm.md(eval('t"{view:value}"'))
        assert r"\bullet" not in value_only.text
        assert "<pre>" not in value_only.text


def test_presenter_delegates_to_annotation_style_adapter_hooks():
    class Adapted:
        def __init__(self, value):
            self.value = value
            self.seen = None

        def __galaga_present__(self, presenter):
            self.seen = presenter
            return ("adapted", presenter)

    presenter = Presenter(content="value")
    adapted = Adapted(Algebra(2).identity)
    assert presenter(adapted) == ("adapted", presenter)
    assert adapted.seen is presenter
