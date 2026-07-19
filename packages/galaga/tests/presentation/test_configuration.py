from dataclasses import FrozenInstanceError

import pytest

from galaga.blades import (
    BladeConvention,
    BladeRef,
    DisplayOrder,
    LocalNamePolicy,
    default_blade_convention,
)
from galaga.names import Name
from galaga.presentation import (
    AlgebraConfig,
    AlgebraDefinition,
    DisplayPolicy,
    ModelConfig,
    Notation,
    PresentationConfig,
    default_presentation,
)


def test_name_has_stable_target_spellings_and_fallbacks():
    fallback = Name("alpha")
    explicit = Name("g0", "γ₀", r"\gamma_{0}")

    assert fallback.variants == ("alpha", "alpha", "alpha")
    assert explicit.for_target("ascii") == "g0"
    assert explicit.for_target("unicode") == "γ₀"
    assert explicit.for_target("latex") == r"\gamma_{0}"
    assert str(explicit) == "γ₀"

    with pytest.raises(ValueError, match="target must be"):
        explicit.for_target("html")


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("",), "ASCII"),
        (("x", ""), "Unicode"),
        (("x", "x", ""), "LaTeX"),
    ],
)
def test_name_rejects_empty_target_spellings(args, message):
    with pytest.raises(ValueError, match=message):
        Name(*args)


def test_presentation_components_are_independently_replaceable_and_immutable():
    original = default_presentation(3)
    notation = Notation("teaching", {"geometric_product": "gp"})
    changed = original.with_notation(notation)

    assert changed.notation is notation
    assert changed.blades is original.blades
    assert changed.local_names is original.local_names
    assert changed.display_order is original.display_order
    assert changed.display is original.display
    assert original.notation == Notation()
    assert hash(changed) == hash(
        PresentationConfig(
            original.blades,
            notation,
            original.local_names,
            original.display_order,
            original.display,
        )
    )

    with pytest.raises(FrozenInstanceError):
        changed.notation = Notation()  # type: ignore[misc]


def test_replacing_blades_does_not_replace_notation():
    original = default_presentation(2).with_notation(Notation("functional"))
    blades = default_blade_convention(2)

    changed = original.with_blades(blades)

    assert changed.blades is blades
    assert changed.notation is original.notation


def test_each_presentation_component_has_an_independent_copy_operation():
    original = default_presentation(2)
    local_names = LocalNamePolicy(2, {"x": 1})
    order = DisplayOrder(2, (0, 2, 1, 3))
    display = DisplayPolicy(content="full", target="latex")

    with_locals = original.with_local_names(local_names)
    with_order = original.with_display_order(order)
    with_display = original.with_display(display)

    assert with_locals.local_names is local_names
    assert with_locals.blades is original.blades
    assert with_order.display_order is order
    assert with_order.notation is original.notation
    assert with_display.display is display
    assert with_display.display_order is original.display_order


def test_configuration_rejects_incomplete_or_dimensionally_inconsistent_components():
    with pytest.raises(ValueError, match="every mask"):
        BladeConvention(2, {0: "1", 1: "e1"})

    blades = default_blade_convention(2)
    with pytest.raises(ValueError, match="dimensions must match"):
        PresentationConfig(
            blades,
            Notation(),
            LocalNamePolicy.from_convention(blades),
            DisplayOrder(3),
            DisplayPolicy(),
        )

    with pytest.raises(ValueError, match="dimensions must match"):
        AlgebraConfig(AlgebraDefinition.from_signature((1,)), default_presentation(2))


def test_algebra_definition_validates_and_normalizes_a_gram_matrix():
    definition = AlgebraDefinition(((1, 0.25), (0.25, -1)), id="mixed")

    assert definition.gram == ((1.0, 0.25), (0.25, -1.0))
    assert definition.dimension == 2
    assert definition == AlgebraDefinition(((1, 0.25), (0.25, -1)), id="mixed")

    with pytest.raises(ValueError, match="square"):
        AlgebraDefinition(((1, 0),))
    with pytest.raises(ValueError, match="symmetric"):
        AlgebraDefinition(((1, 2), (3, 4)))
    with pytest.raises(ValueError, match="finite"):
        AlgebraDefinition(((float("inf"),),))
    with pytest.raises(ValueError, match="product_backend"):
        AlgebraDefinition(((1,),), product_backend="magic")


def test_signature_and_pqr_definitions_have_explicit_basis_order():
    assert AlgebraDefinition.from_signature((1, 0, -1)).gram == (
        (1.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (0.0, 0.0, -1.0),
    )
    assert AlgebraDefinition.from_pqr(1, 1, 1).gram == (
        (0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, -1.0),
    )
    with pytest.raises(ValueError, match="signature values"):
        AlgebraDefinition.from_signature((2,))
    with pytest.raises(ValueError, match="non-negative integers"):
        AlgebraDefinition.from_pqr(-1)


def test_model_roles_are_validated_against_complete_algebra_dimension():
    model = ModelConfig("line", {"direction": BladeRef(1)})
    config = AlgebraConfig(AlgebraDefinition.from_signature((1,)), default_presentation(1), model)

    assert config.model is model
    assert config.with_presentation(config.presentation) == config

    with pytest.raises(ValueError, match="outside the algebra dimension"):
        AlgebraConfig(
            AlgebraDefinition.from_signature((1,)),
            default_presentation(1),
            ModelConfig("bad", {"outside": BladeRef(2)}),
        )
    with pytest.raises(TypeError, match="BladeRef"):
        ModelConfig("bad", {"direction": 1})  # type: ignore[dict-item]


def test_notation_and_display_policy_validate_their_own_concerns():
    notation = Notation("functional", {"geometric_product": "gp"})
    assert notation.token("geometric_product") == "gp"
    assert notation.token("missing", "?") == "?"
    assert DisplayPolicy().zero_tolerance == 1e-12
    assert DisplayPolicy().coefficient_precision == 6

    with pytest.raises(ValueError, match="duplicate notation"):
        Notation("bad", (("gp", "*"), ("gp", "×")))
    with pytest.raises(ValueError, match="non-empty string"):
        Notation("")
    with pytest.raises(ValueError, match="ids and tokens"):
        Notation("bad", (("gp", ""),))
    with pytest.raises(ValueError, match="display content"):
        DisplayPolicy(content="everything")
    with pytest.raises(ValueError, match="display target"):
        DisplayPolicy(target="html")
    with pytest.raises(TypeError, match="zero_tolerance must be a real number"):
        DisplayPolicy(zero_tolerance=True)
    with pytest.raises(ValueError, match="finite and non-negative"):
        DisplayPolicy(zero_tolerance=-1)
    with pytest.raises(ValueError, match="finite and non-negative"):
        DisplayPolicy(zero_tolerance=float("inf"))
    with pytest.raises(TypeError, match="coefficient_precision must be an integer"):
        DisplayPolicy(coefficient_precision=6.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="between 1 and 17"):
        DisplayPolicy(coefficient_precision=0)
    with pytest.raises(ValueError, match="between 1 and 17"):
        DisplayPolicy(coefficient_precision=18)


def test_configuration_type_boundaries_fail_before_partial_objects_escape():
    presentation = default_presentation(1)

    with pytest.raises(TypeError, match="notation must be"):
        PresentationConfig(
            presentation.blades,
            "bad",  # type: ignore[arg-type]
            presentation.local_names,
            presentation.display_order,
            presentation.display,
        )
    with pytest.raises(ValueError, match="id must be"):
        AlgebraDefinition(((1,),), id="")
    with pytest.raises(ValueError, match="model id"):
        ModelConfig("")
    with pytest.raises(ValueError, match="unique"):
        ModelConfig("bad", (("x", BladeRef(1)), ("x", BladeRef(1))))
    with pytest.raises(ValueError, match="non-empty strings"):
        ModelConfig("bad", (("", BladeRef(1)),))
    with pytest.raises(TypeError, match="definition must be"):
        AlgebraConfig("bad", presentation)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="presentation must be"):
        AlgebraConfig(AlgebraDefinition(((1,),)), "bad")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="model must be"):
        AlgebraConfig(AlgebraDefinition(((1,),)), presentation, "bad")  # type: ignore[arg-type]
