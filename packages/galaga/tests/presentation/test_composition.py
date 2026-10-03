"""Right-biased presentation composition without numeric-algebra changes."""

import math

import numpy as np
import pytest

from galaga import (
    Algebra,
    ConfiguredPreset,
    DisplayPolicy,
    Notation,
    NotationPatch,
    PresentationRecipe,
    Presenter,
    RenderRule,
    presets,
)
from galaga._composition_base import PresentationComposable
from galaga.blades import DisplayOrder, LocalNamePolicy


def test_notation_union_merges_tokens_and_target_specific_rules_with_right_precedence():
    left_rule = RenderRule("function", symbol="left")
    right_rule = RenderRule("function", symbol="right")
    latex_rule = RenderRule("function", symbol="latex_right")
    left = Notation("left", {"shared": "left", "retained": "old"}, rules={"reverse": left_rule})
    right = Notation(
        "right",
        {"shared": "right", "added": "new"},
        rules={"reverse": right_rule, ("reverse", "latex"): latex_rule},
    )

    merged = left | right

    assert merged.id == "right"
    assert dict(merged.tokens) == {"shared": "right", "retained": "old", "added": "new"}
    assert merged.rule("reverse", "ascii") is right_rule
    assert merged.rule("reverse", "latex") is latex_rule
    assert left.rule("reverse", "latex") is left_rule
    assert right.token("retained") is None


def test_notation_union_preserves_absent_rules_and_respects_named_preset_overlap():
    default = presets.notation.default()
    functional = presets.notation.functional()
    assert (default | functional).rules == default.rules

    hestenes = presets.notation.hestenes()
    doran = presets.notation.doran_lasenby()
    combined = hestenes | doran
    assert combined.rule("hestenes_inner", "ascii") == doran.rule("hestenes_inner", "ascii")
    assert combined.rule("hestenes_inner", "latex") == hestenes.rule("hestenes_inner", "latex")
    assert combined.rule("reverse", "latex") == doran.rule("reverse", "latex")
    assert hestenes.rule("reverse", "latex") != combined.rule("reverse", "latex")


def test_sparse_reverse_patch_preserves_base_notation_and_replaces_latex_override():
    base = presets.notation.default()
    patch = presets.notation.override(reverse="dagger")
    patched = base | patch

    assert isinstance(patch, NotationPatch)
    assert patched.id == base.id
    assert patched.rule("geometric_product", "latex") == base.rule("geometric_product", "latex")
    assert patched.rule("reverse", "ascii") == presets.notation.hestenes().rule("reverse", "ascii")
    assert patched.rule("reverse", "latex") == presets.notation.hestenes().rule("reverse", "latex")
    assert patched.rule("reverse", "latex") != base.rule("reverse", "latex")
    assert base.rule("reverse", "latex") == presets.notation.default().rule("reverse", "latex")


def test_reverse_patch_resolves_against_complete_preset_and_composes_right_biased():
    dagger = presets.notation.override(reverse="dagger")
    tilde = presets.notation.override(reverse="tilde")
    base = presets.sta()
    configured = base | dagger
    patched = Algebra(config=configured)
    reverted = Algebra(config=base | dagger | tilde)

    assert configured.presentation.notation == dagger
    assert patched.presentation.notation.id == Algebra(config=base).presentation.notation.id
    assert patched.presentation.notation.rule("reverse", "latex") == presets.notation.hestenes().rule(
        "reverse", "latex"
    )
    assert reverted.presentation.notation.rule("reverse", "latex") == presets.notation.default().rule(
        "reverse", "latex"
    )
    assert dagger | tilde == tilde
    np.testing.assert_array_equal(patched.gram, Algebra(config=base).gram)


def test_sparse_reverse_patch_validates_style_and_type():
    with pytest.raises(ValueError, match="reverse"):
        presets.notation.override(reverse="star")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="Notation"):
        NotationPatch(reverse="dagger").apply("not notation")  # type: ignore[arg-type]


def test_different_component_classes_promote_to_an_immutable_right_biased_recipe():
    notation = presets.notation.hestenes()
    first_display = DisplayPolicy(coefficient_precision=4)
    last_display = DisplayPolicy(coefficient_precision=3)
    local_names = LocalNamePolicy(2, {"x": 1})
    order = DisplayOrder(2)

    first = notation | first_display
    recipe = first | local_names | order | last_display

    assert isinstance(recipe, PresentationRecipe)
    assert recipe.notation is notation
    assert recipe.display == last_display
    assert recipe.local_names is local_names
    assert recipe.display_order is order
    assert first.display is first_display


def test_sparse_display_overrides_preserve_unmentioned_choices() -> None:
    base = Algebra(2, display=DisplayPolicy(content="full", target="latex", zero_tolerance=0))
    precision = presets.display.override(coefficient_precision=4)
    selected = base.with_display(precision).presentation.display

    assert selected.content == "full"
    assert selected.target == "latex"
    assert selected.zero_tolerance == 0
    assert selected.coefficient_precision == 4
    assert base.presentation.display.coefficient_precision == 6

    configured = Algebra(
        config=presets.euclidean(2).build().with_presentation(base.presentation),
        display=precision,
    ).presentation.display
    assert configured.content == "full"
    assert configured.target == "latex"
    assert configured.zero_tolerance == 0
    assert configured.coefficient_precision == 4

    recipe = presets.display.override(target="ascii") | precision
    composed = base.with_display(recipe).presentation.display
    assert composed.content == "full"
    assert composed.target == "ascii"
    assert composed.zero_tolerance == 0
    assert composed.coefficient_precision == 4

    reset = base.with_display(presets.display.override(content="auto"))
    assert reset.presentation.display.content == "auto"


def test_display_preset_is_sparse_for_presenter_factories() -> None:
    algebra = Algebra(2)
    value = algebra.basis_vectors()[0]
    presenter = presets.presenters.values() | presets.display.override(coefficient_precision=4)
    policy = presenter(value).presentation.display
    assert policy.content == "value"
    assert policy.coefficient_precision == 4
    assert policy.target == algebra.presentation.display.target
    assert dir(presets.display) == ["override"]


def test_direct_presenter_display_override_keeps_captured_policy() -> None:
    algebra = Algebra(2, display=DisplayPolicy(content="full", target="latex", zero_tolerance=0))
    value = algebra.basis_vectors()[0]
    view = Presenter(display=presets.display.override(coefficient_precision=4))(value)
    assert view.presentation.display.content == "full"
    assert view.presentation.display.target == "latex"
    assert view.presentation.display.zero_tolerance == 0
    assert view.presentation.display.coefficient_precision == 4


def test_recipe_applied_to_preset_preserves_metric_model_and_products():
    base = presets.oblique_plane(degrees=60)
    notation = presets.notation.hestenes() | presets.notation.doran_lasenby()
    recipe = presets.blades.euclidean(2) | notation | DisplayPolicy(coefficient_precision=3)
    configured = base | recipe

    assert isinstance(configured, ConfiguredPreset)
    assert configured.base is base
    assert configured.presentation is recipe
    algebra = Algebra(config=configured)
    original = Algebra(config=base)
    np.testing.assert_array_equal(algebra.gram, original.gram)
    assert algebra.model == original.model
    assert algebra.presentation.notation == notation
    assert algebra.presentation.display.coefficient_precision == 3
    e1, e2 = algebra.basis_vectors()
    assert e1 * e2 == (e1 ^ e2) + math.cos(math.pi / 3)


def test_direct_preset_composition_replaces_repeated_presentation_slots():
    base = presets.euclidean(2)
    first = base | presets.notation.hestenes()
    updated = first | presets.notation.doran_lasenby() | DisplayPolicy(coefficient_precision=2)

    assert isinstance(updated, ConfiguredPreset)
    assert updated.base is base
    assert updated.presentation.notation == presets.notation.doran_lasenby()
    assert updated.presentation.display.coefficient_precision == 2
    assert first.presentation.notation == presets.notation.hestenes()
    assert Algebra(config=updated).presentation.notation == presets.notation.doran_lasenby()


def test_config_and_recipe_can_compose_and_validate_blade_metric_on_build():
    base = presets.euclidean(2).build()
    recipe = DisplayPolicy(coefficient_precision=2) | presets.blades.euclidean(2)
    changed = (base | recipe).build()
    assert changed.definition is base.definition
    assert changed.model is base.model
    assert changed.presentation.display.coefficient_precision == 2

    incompatible = presets.euclidean(3) | presets.blades.cga()
    with pytest.raises(ValueError, match="requires dimension"):
        incompatible.build()


def test_complete_presets_cannot_be_implicitly_merged():
    with pytest.raises(TypeError):
        _ = presets.euclidean(2) | presets.oblique_plane(degrees=60)


def test_public_recipe_rejects_unknown_component_types():
    with pytest.raises(TypeError, match="blades"):
        PresentationRecipe(blades="sta")  # type: ignore[arg-type]


def test_leaf_composition_hook_dispatches_across_component_modules():
    blade_preset = presets.blades.indexed(2, prefix="v")
    notation = presets.notation.hestenes()
    display = DisplayPolicy(coefficient_precision=3)

    assert PresentationComposable.__module__ == "galaga._composition_base"
    assert isinstance(blade_preset, PresentationComposable)
    assert isinstance(notation, PresentationComposable)
    assert isinstance(display, PresentationComposable)

    recipe = blade_preset | notation | display
    algebra = Algebra(config=presets.euclidean(2) | recipe)
    assert algebra.presentation.blades.label(1).name.ascii == "v1"
    assert algebra.presentation.notation == notation
    assert algebra.presentation.display.coefficient_precision == 3

    with pytest.raises(TypeError):
        _ = blade_preset | object()
