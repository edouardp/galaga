"""Right-biased presentation composition without numeric-algebra changes."""

import math

import numpy as np
import pytest

from galaga import Algebra, ConfiguredPreset, DisplayPolicy, Notation, PresentationRecipe, RenderRule, presets
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
    assert recipe.display is last_display
    assert recipe.local_names is local_names
    assert recipe.display_order is order
    assert first.display is first_display


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
    assert updated.presentation.display == DisplayPolicy(coefficient_precision=2)
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
