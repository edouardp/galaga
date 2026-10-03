import math

import numpy as np
import pytest

from galaga import presets
from galaga.blades import default_blade_convention
from galaga.facade import Algebra
from galaga.presentation import Notation
from galaga.presets import (
    CGAPreset,
    ComplexPreset,
    EuclideanPreset,
    ExteriorPreset,
    LengyelCGAPreset,
    LengyelRGAPreset,
    ObliquePlanePreset,
    PGAPreset,
    QuaternionPreset,
    SpacetimePreset,
    oblique_plane,
)


def test_native_null_cga_preset_defines_all_five_basis_vectors_and_gram_entries():
    algebra = Algebra(config=presets.cga(spatial_dim=3))

    expected = np.zeros((5, 5))
    expected[1:4, 1:4] = np.eye(3)
    expected[0, 4] = expected[4, 0] = -1
    np.testing.assert_array_equal(algebra.gram, expected)
    assert algebra.n == 5
    assert algebra.model is not None
    assert algebra.model.id == "cga-null"
    assert algebra.presentation.blades.resolve("origin").mask == 1
    assert algebra.presentation.blades.resolve("infinity").mask == 16


def test_preset_expansion_matches_explicit_numeric_and_presentation_configuration():
    expanded = EuclideanPreset(2).build()
    preset_algebra = Algebra(config=EuclideanPreset(2))
    explicit = Algebra(
        gram=expanded.definition.gram,
        presentation=expanded.presentation,
        id=expanded.definition.id,
    )

    np.testing.assert_array_equal(preset_algebra.gram, explicit.gram)
    assert preset_algebra.default_presentation == explicit.default_presentation


@pytest.mark.parametrize(
    "preset",
    [
        EuclideanPreset(2),
        SpacetimePreset(),
        PGAPreset(2),
        CGAPreset(2),
        CGAPreset(2, frame="orthogonal"),
        LengyelCGAPreset(),
        LengyelRGAPreset(),
        ObliquePlanePreset(math.pi / 3),
        ComplexPreset(),
        QuaternionPreset(),
        ExteriorPreset(3),
    ],
)
def test_supported_presets_expand_to_dimensionally_complete_configs(preset):
    config = preset.build()

    assert config.definition.dimension == config.presentation.dimension
    assert len(config.presentation.blades.labels) == 1 << config.definition.dimension


def test_preset_parameters_are_validated():
    with pytest.raises(ValueError, match="positive integer"):
        CGAPreset(0)
    with pytest.raises(ValueError, match="CGA frame"):
        CGAPreset(frame="diagonal")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="nonzero"):
        CGAPreset(null_pair=0)
    with pytest.raises(ValueError, match="only applies"):
        CGAPreset(frame="orthogonal", null_pair=-0.5)
    with pytest.raises(ValueError, match="spatial_dim=3"):
        LengyelRGAPreset(2)
    with pytest.raises(ValueError, match="spatial_dim=3"):
        LengyelCGAPreset(2)
    with pytest.raises(ValueError, match="dimension must be a positive integer"):
        ExteriorPreset(0)


@pytest.mark.parametrize("angle", [0, math.pi, -0.1, math.nan, math.inf, -math.inf, True, "1.0", 1e-300])
def test_oblique_plane_rejects_invalid_or_numerically_collapsed_angles(angle):
    with pytest.raises(ValueError, match="angle"):
        ObliquePlanePreset(angle)


@pytest.mark.parametrize("degrees", [0, 180, -1, 181, math.nan, math.inf, -math.inf, True, "60", 1e-300])
def test_oblique_plane_rejects_invalid_or_numerically_collapsed_degrees(degrees):
    with pytest.raises(ValueError, match="degrees"):
        oblique_plane(degrees=degrees)


def test_oblique_plane_requires_exactly_one_angle_unit():
    with pytest.raises(ValueError, match="exactly one"):
        oblique_plane()
    with pytest.raises(ValueError, match="exactly one"):
        oblique_plane(angle=math.pi / 3, degrees=60)


def test_oblique_plane_degrees_preserves_input_and_matches_radian_metric():
    preset = oblique_plane(degrees=60)
    assert preset == ObliquePlanePreset(degrees=60)
    assert preset.degrees == 60
    assert preset.angle is None
    degrees_algebra = Algebra(config=preset)
    radians_algebra = Algebra(config=oblique_plane(angle=math.pi / 3))
    np.testing.assert_allclose(degrees_algebra.gram, radians_algebra.gram)
    e1, e2 = degrees_algebra.basis_vectors()
    assert e1 * e2 == (e1 ^ e2) + math.cos(math.radians(60))


def test_oblique_plane_metric_and_geometric_product_agree_with_explicit_gram():
    preset = ObliquePlanePreset(math.pi / 3)
    algebra = Algebra(config=preset)
    explicit = Algebra(gram=((1.0, 0.5), (0.5, 1.0)))
    e1, e2 = algebra.basis_vectors()
    x1, x2 = explicit.basis_vectors()

    np.testing.assert_allclose(algebra.gram, explicit.gram)
    assert e1 * e1 == 1
    assert e2 * e2 == 1
    assert e1 * e2 == (e1 ^ e2) + math.cos(preset.angle)
    assert x1 * x2 == (x1 ^ x2) + 0.5
    assert algebra.model is not None
    assert algebra.model.id == "euclidean"


def test_oblique_plane_right_angle_has_exactly_diagonal_metric():
    algebra = Algebra(config=ObliquePlanePreset(math.pi / 2))
    np.testing.assert_array_equal(algebra.gram, np.eye(2))
    degrees_algebra = Algebra(config=oblique_plane(degrees=90))
    np.testing.assert_array_equal(degrees_algebra.gram, np.eye(2))


def test_complex_quaternion_and_exterior_presets_define_their_numeric_models():
    complex_algebra = Algebra(config=ComplexPreset())
    imaginary = complex_algebra.blade("imaginary")
    assert float(imaginary * imaginary) == -1

    quaternion_algebra = Algebra(config=QuaternionPreset())
    i = quaternion_algebra.blade("quaternion_i")
    j = quaternion_algebra.blade("quaternion_j")
    k = quaternion_algebra.blade("quaternion_k")
    assert i * j == k
    assert j * k == i
    assert k * i == j

    exterior_algebra = Algebra(config=ExteriorPreset(2))
    e1, e2 = exterior_algebra.basis_vectors()
    assert e1 * e1 == 0
    assert e1 * e2 == e1 ^ e2


def test_explicit_presentation_component_overrides_only_that_preset_component():
    preset = CGAPreset(2)
    base = preset.build().presentation
    notation = Notation("teaching")
    blades = default_blade_convention(4)

    changed_notation = Algebra(config=preset, notation=notation)
    changed_blades = Algebra(config=preset, blades=blades)

    assert changed_notation.presentation.notation is notation
    assert changed_notation.presentation.blades == base.blades
    assert changed_notation.presentation.local_names == base.local_names
    assert changed_blades.presentation.blades is blades
    assert changed_blades.presentation.notation == base.notation
    np.testing.assert_array_equal(changed_notation.gram, changed_blades.gram)


def test_complete_config_rejects_a_second_numeric_definition():
    with pytest.raises(TypeError, match="defines the numeric algebra"):
        Algebra(3, config=EuclideanPreset(3))
    with pytest.raises(TypeError, match="defines the numeric algebra"):
        Algebra(config=EuclideanPreset(3), gram=np.eye(3))


def test_reusing_a_preset_creates_equal_but_independent_immutable_configs():
    preset = EuclideanPreset(3)
    left = Algebra(config=preset)
    right = Algebra(config=preset)

    assert left.default_presentation == right.default_presentation
    assert left.default_presentation is not right.default_presentation
    assert left.presentation.blades is not right.presentation.blades


def test_ergonomic_preset_constructors_return_inspectable_preset_objects():
    assert presets.euclidean(2) == EuclideanPreset(2)
    assert presets.sta("mostly-plus") == SpacetimePreset("mostly-plus")
    assert presets.pga(2) == PGAPreset(2)
    assert presets.cga(2, frame="orthogonal") == CGAPreset(2, "orthogonal")
    assert presets.rga() == LengyelRGAPreset()
    assert presets.lengyel_cga() == LengyelCGAPreset()
    assert presets.complex() == ComplexPreset()
    assert presets.quaternion() == QuaternionPreset()
    assert presets.exterior(2) == ExteriorPreset(2)


def test_lengyel_cga_preset_combines_native_null_roles_blades_order_and_notation() -> None:
    algebra = Algebra(config=presets.lengyel_cga())

    assert algebra.model is not None
    assert algebra.model.id == "cga-null"
    assert algebra.presentation.notation == Notation.lengyel()
    assert algebra.blade("origin").latex(content="value") == r"\mathbf{e}_{4}"
    assert algebra.blade("infinity").latex(content="value") == r"\mathbf{e}_{5}"
    assert algebra.blade("e31").latex(content="value") == r"\mathbf{e}_{31}"
    assert algebra.pseudoscalar().latex(content="value") == r"\text{𝟙}"
    assert algebra.blade("e12345") == algebra.pseudoscalar()
    assert algebra.display_order[-1] == 31


def test_spacetime_preset_and_custom_null_pair_change_the_numeric_definition():
    mostly_minus = Algebra(config=SpacetimePreset())
    mostly_plus = Algebra(config=SpacetimePreset("mostly-plus"))
    custom_null = Algebra(config=CGAPreset(1, null_pair=-0.5))

    assert mostly_minus.blade("i") == mostly_minus.I
    np.testing.assert_array_equal(mostly_plus.basis_squares, (-1, 1, 1, 1))
    assert custom_null.gram[0, 2] == custom_null.gram[2, 0] == -0.5

    with pytest.raises(ValueError, match="finite"):
        CGAPreset(null_pair=float("nan"))
