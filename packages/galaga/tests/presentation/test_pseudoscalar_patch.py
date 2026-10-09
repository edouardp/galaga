"""Sparse top-blade naming preserves the algebra and unrelated presentation."""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from galaga import (
    Algebra,
    BladeLabel,
    BladePatch,
    BladeRef,
    LocalNamePolicy,
    Name,
    PresentationRecipe,
    Presenter,
    indexed_blade_convention,
    presets,
)


def test_one_negative_vector_renders_as_i_throughout_values():
    algebra = Algebra(0, 1, blades=presets.blades.pss("i"), user_config_files=False)
    (i,) = algebra.basis_vectors()
    assert i * i == -algebra.identity
    assert algebra.I == i
    assert algebra.blade("i") == i
    assert i.latex(content="value") == "i"
    assert (2 + 3 * i).display("value/ascii") == "2 + 3i"
    assert (2 + 3 * i).latex(content="value") == "2 + 3 i"
    # Display vocabulary and Python bindings are independent components in v2.
    assert list(algebra.locals()) == ["e1"]
    renamed = algebra.with_local_names(LocalNamePolicy.from_convention(algebra.presentation.blades))
    assert list(renamed.locals()) == ["i"]
    assert renamed.locals()["i"] == i


@pytest.mark.parametrize(
    "preset",
    [
        presets.euclidean(3),
        presets.oblique_plane(degrees=60),
        presets.exterior(3),
        presets.sta(sigmas=True, pseudovectors=True),
        presets.cga(3),
        presets.cga(3, basis_order="euclidean-first", model_pseudoscalars=True),
    ],
)
def test_patch_preserves_metric_orientations_and_other_components(preset):
    original = Algebra(config=preset, user_config_files=False)
    native_top = original.identity
    for vector in original.basis_vectors():
        native_top = native_top ^ vector
    assert native_top == original.I
    top_square = native_top * native_top

    renamed = Algebra(config=preset | presets.blades.pss("J"), user_config_files=False)
    before, after = original.presentation, renamed.presentation
    mask = original.dim - 1
    np.testing.assert_array_equal(renamed.gram, original.gram)
    assert after.blades.labels[:-1] == before.blades.labels[:-1]
    assert after.blades.label(mask).ref == before.blades.label(mask).ref
    assert after.blades.label(mask).name == Name("J")
    assert after.blades.aliases == before.blades.aliases
    assert after.blades.roles == before.blades.roles
    assert after.local_names == before.local_names
    assert after.display_order == before.display_order
    assert after.notation == before.notation
    assert after.display == before.display
    assert renamed.model == original.model
    np.testing.assert_array_equal((renamed.I * renamed.I).data, top_square.data)
    assert renamed.blade("J") == after.blades.label(mask).ref.orientation * renamed.I


def test_patch_works_as_keyword_presentation_and_existing_algebra_view():
    base = Algebra(config=presets.sta(sigmas=True), user_config_files=False)
    patch = presets.blades.pss("J")
    expected = patch.apply(base.presentation.blades)
    via_keyword = Algebra(config=presets.sta(sigmas=True), blades=patch, user_config_files=False)
    via_presentation = Algebra(config=presets.sta(sigmas=True), presentation=patch, user_config_files=False)
    via_view = base.with_blades(patch)
    assert via_keyword.presentation.blades == via_presentation.presentation.blades == expected
    assert via_view.presentation.blades == expected
    assert via_view.numeric is base.numeric
    assert base.presentation.blades != expected


def test_complete_blade_preset_composes_with_patch_and_other_components():
    patch = presets.blades.pss("J")
    blades = presets.blades.indexed(3, prefix="v") | patch
    algebra = Algebra(3, blades=blades, user_config_files=False)
    assert algebra.basis_vectors()[0].display("value/ascii") == "v1"
    assert algebra.I.display("value/ascii") == "J"
    recipe = blades | presets.notation.override(reverse="dagger")
    composed = Algebra(config=presets.euclidean(3) | recipe, user_config_files=False)
    assert composed.presentation.blades == algebra.presentation.blades
    assert composed.presentation.notation != algebra.presentation.notation


def test_repeated_patches_use_right_precedence_and_full_vocabulary_replaces_patch():
    first, last = presets.blades.pss("J"), presets.blades.pss("K")
    full = presets.blades.indexed(3, prefix="v")
    selected = Algebra(3, blades=full | first | last, user_config_files=False)
    replaced = Algebra(3, blades=first | full, user_config_files=False)
    assert selected.I.display("value/ascii") == "K"
    assert replaced.I.display("value/ascii") == "v123"
    invalid_intermediate = presets.blades.pss("v1")
    valid = Algebra(3, blades=full | invalid_intermediate | last, user_config_files=False)
    assert valid.I.display("value/ascii") == "K"


@pytest.mark.parametrize(
    "components",
    [
        (presets.blades.indexed(3, prefix="v"), presets.blades.pss("J"), presets.blades.pss("K")),
        (presets.blades.pss("J"), presets.notation.override(reverse="dagger"), presets.blades.euclidean(3)),
        (presets.blades.euclidean(3), presets.blades.pss("J"), presets.notation.override(reverse="dagger")),
    ],
)
def test_patch_composition_is_associative(components):
    a, b, c = components
    left = Algebra(3, presentation=(a | b) | c, user_config_files=False)
    right = Algebra(3, presentation=a | (b | c), user_config_files=False)
    assert left.presentation == right.presentation


def test_target_specific_name_and_signed_top_label_are_preserved():
    convention = indexed_blade_convention(2, overrides={3: BladeLabel(Name("old"), BladeRef(3, -1))})
    name = Name("J", "𝒥", r"\mathcal{J}")
    algebra = Algebra(2, blades=convention | presets.blades.pss(name), user_config_files=False)
    e1, e2 = algebra.basis_vectors()
    assert algebra.blade("J") == -(e1 ^ e2)
    assert algebra.I.display("value/ascii") == "-J"
    assert algebra.I.display("value/unicode") == "-𝒥"
    assert algebra.I.latex(content="value") == r"-\mathcal{J}"


@pytest.mark.parametrize("style", ["keyword", "composition", "reverse-composition", "config"])
def test_presenter_uses_patch_without_mutating_algebra(style):
    algebra = Algebra(config=presets.sta(sigmas=True), user_config_files=False)
    value = algebra.I
    patch = presets.blades.pss("J")
    presenters = {
        "keyword": Presenter(blades=patch),
        "composition": presets.presenters.values() | patch,
        "reverse-composition": patch | presets.presenters.values(),
        "config": Presenter(config=PresentationRecipe(blade_patch=patch)),
    }
    original = algebra.presentation
    view = presenters[style](value)
    assert view.value is value
    assert view.latex(content="value") == "J"
    assert view.presentation.blades.labels[:-1] == original.blades.labels[:-1]
    assert algebra.presentation is original


def test_presenter_accepts_composed_blade_keyword():
    algebra = Algebra(3, user_config_files=False)
    recipe = presets.blades.indexed(3, prefix="v") | presets.blades.pss("J")
    view = Presenter(blades=recipe)(algebra.I)
    assert view.ascii(content="value") == "J"
    assert view.presentation.blades.label(1).name.ascii == "v1"


def test_patch_is_immutable_reusable_and_validated():
    patch = presets.blades.pss("J")
    assert isinstance(patch, BladePatch)
    with pytest.raises(FrozenInstanceError):
        patch.pss = Name("K")
    for dimension in (0, 1, 2, 3):
        algebra = Algebra(dimension, blades=patch, user_config_files=False)
        assert algebra.blade_label(algebra.dim - 1).name == Name("J")
    with pytest.raises(TypeError, match="BladeConvention"):
        patch.apply("not a convention")
    with pytest.raises(TypeError, match="Name"):
        BladePatch("J")
    with pytest.raises(TypeError, match="unsupported component"):
        PresentationRecipe(blade_patch="J")
    with pytest.raises(ValueError, match="ambiguous"):
        Algebra(3, blades=presets.blades.pss("e1"), user_config_files=False)


@pytest.mark.parametrize("invalid", [None, 3, ("i", "i", "i")])
def test_factory_rejects_invalid_name_types(invalid):
    with pytest.raises(TypeError, match="Name or string"):
        presets.blades.pss(invalid)


def test_factory_rejects_empty_name():
    with pytest.raises(ValueError, match="non-empty"):
        presets.blades.pss("")


def test_blade_keyword_rejects_recipes_with_unrelated_components():
    recipe = presets.blades.pss("J") | presets.notation.override(reverse="dagger")
    with pytest.raises(TypeError, match="only blade components"):
        Algebra(3, blades=recipe, user_config_files=False)
    value = Algebra(3, user_config_files=False).I
    with pytest.raises(TypeError, match="only blade components"):
        Presenter(blades=recipe)(value)
