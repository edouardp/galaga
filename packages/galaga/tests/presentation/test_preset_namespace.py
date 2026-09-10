"""Tests for the concise complete- and blade-preset namespaces."""

import numpy as np
import pytest

from galaga import Algebra, presets
from galaga.blades import spacetime_blade_convention


def test_concise_complete_presets_match_the_existing_factories():
    assert presets.euclidean(2) == presets.p_euclidean(2)
    assert presets.sta("mostly-plus") == presets.p_sta("mostly-plus")
    assert presets.pga(2) == presets.p_pga(2)
    assert presets.cga(2, frame="orthogonal") == presets.p_cga(2, frame="orthogonal")
    assert presets.rga() == presets.p_rga()
    assert presets.complex() == presets.p_complex()
    assert presets.quaternion() == presets.p_quaternion()
    assert presets.exterior(2) == presets.p_exterior(2)
    assert presets.lengyel_cga() == presets.p_lengyel_cga()


@pytest.mark.parametrize(
    ("new", "old"),
    (
        (presets.euclidean(3), presets.p_euclidean(3)),
        (presets.sta(), presets.p_sta()),
        (presets.cga(), presets.p_cga()),
        (presets.pga(), presets.p_pga()),
    ),
)
def test_concise_complete_presets_build_identical_algebras(new, old):
    left = Algebra(config=new)
    right = Algebra(config=old)
    np.testing.assert_array_equal(left.gram, right.gram)
    assert left.default_presentation == right.default_presentation
    assert left.model == right.model


def test_blade_namespace_can_name_an_explicit_algebra_without_changing_its_metric():
    algebra = Algebra(1, 3, blades=presets.blades.sta())
    expected = Algebra(1, 3, blades=spacetime_blade_convention())
    np.testing.assert_array_equal(algebra.gram, expected.gram)
    assert algebra.default_presentation.blades == expected.default_presentation.blades
    assert [value.latex() for value in algebra.basis_vectors()] == [
        r"\gamma_{0}",
        r"\gamma_{1}",
        r"\gamma_{2}",
        r"\gamma_{3}",
    ]


def test_metric_aware_sta_blade_names_resolve_against_the_actual_ordered_metric():
    mostly_minus = Algebra(1, 3, blades=presets.blades.sta(sigmas=True, pseudovectors=True))
    mostly_plus = Algebra(3, 1, blades=presets.blades.sta(sigmas=True, pseudovectors=True))

    assert mostly_minus.blade("s1") == -mostly_minus.blade(0b0011)
    assert mostly_minus.blade("s1").data[0b0011] == -1
    assert mostly_plus.blade("s1") == -mostly_plus.blade(0b0011)
    assert mostly_plus.blade("s1").data[0b0011] == -1
    assert mostly_minus.blade("ig0") == mostly_minus.I * mostly_minus.blade(1)
    assert mostly_plus.blade("ig0") == mostly_plus.I * mostly_plus.blade(1)


def test_blade_recipe_resolution_is_reusable_and_with_blades_preserves_numeric_identity():
    recipe = presets.blades.sta(sigmas=True)
    first = Algebra(1, 3, blades=recipe)
    second = Algebra(3, 1).with_blades(recipe)
    assert first.numeric is not second.numeric
    assert second.with_blades(recipe).numeric is second.numeric
    assert second.blade("s1") == -second.blade(0b0011)


@pytest.mark.parametrize(
    "algebra",
    (
        Algebra(gram=[[1, 0.2, 0, 0], [0.2, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]]),
        Algebra(gram=[[2, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]]),
    ),
)
def test_metric_aware_sta_recipe_rejects_unsupported_metrics(algebra):
    with pytest.raises(ValueError, match="metric-aware STA blade names"):
        algebra.with_blades(presets.blades.sta(sigmas=True))


@pytest.mark.parametrize("flag", (None, 0, 1, "yes"))
def test_metric_aware_blade_recipe_flags_require_booleans(flag):
    with pytest.raises(TypeError, match="sigmas must be a boolean"):
        presets.blades.sta(sigmas=flag)


def test_blade_recipe_dimension_and_invalid_recipe_errors_are_actionable():
    with pytest.raises(ValueError, match="requires dimension 4"):
        Algebra(3, blades=presets.blades.sta())
    with pytest.raises(TypeError, match="BladeConvention or a resolvable blade preset"):
        Algebra(3, blades="sta")
    with pytest.raises(ValueError, match="unknown blade preset kind"):
        Algebra(1, blades=type(presets.blades.euclidean())("unknown"))


@pytest.mark.parametrize(
    ("recipe", "algebra"),
    (
        (presets.blades.euclidean(2), Algebra(2)),
        (presets.blades.indexed(2), Algebra(2)),
        (presets.blades.exterior(2), Algebra(gram=[[0, 0], [0, 0]])),
        (presets.blades.pga(2), Algebra(gram=[[1, 0, 0], [0, 1, 0], [0, 0, 0]])),
        (presets.blades.cga(1), Algebra(config=presets.cga(1))),
        (presets.blades.cga(1, frame="orthogonal"), Algebra(config=presets.cga(1, frame="orthogonal"))),
        (presets.blades.rga(), Algebra(gram=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]])),
        (presets.blades.complex(), Algebra(2)),
        (presets.blades.quaternion(), Algebra(3)),
    ),
)
def test_every_blade_recipe_resolves_to_the_expected_convention(recipe, algebra):
    resolved = recipe.resolve(algebra.gram)
    assert resolved.dimension == algebra.n
    assert algebra.with_blades(recipe).default_presentation.blades == resolved


def test_cga_blade_recipe_rejects_a_frame_that_does_not_match_the_metric():
    with pytest.raises(ValueError, match="orthogonal frame"):
        Algebra(config=presets.cga(1), blades=presets.blades.cga(1, frame="orthogonal"))
    with pytest.raises(ValueError, match="null frame"):
        Algebra(config=presets.cga(1, frame="orthogonal"), blades=presets.blades.cga(1))
