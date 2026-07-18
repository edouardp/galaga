import pytest

from galaga.blades import (
    BladeConvention,
    BladeLabel,
    BladeRef,
    DisplayOrder,
    LocalNamePolicy,
    complex_blade_convention,
    euclidean_blade_convention,
    indexed_blade_convention,
    null_cga_blade_convention,
    orthogonal_cga_blade_convention,
    quaternion_blade_convention,
    rga_blade_convention,
    rga_display_order,
    spacetime_blade_convention,
)
from galaga.names import Name


@pytest.mark.parametrize(
    ("convention", "dimension", "role"),
    [
        (euclidean_blade_convention(3), 3, "euclidean_1"),
        (spacetime_blade_convention(), 4, "time"),
        (orthogonal_cga_blade_convention(3), 5, "plus"),
        (null_cga_blade_convention(3), 5, "origin"),
        (rga_blade_convention(), 4, "projective"),
        (complex_blade_convention(), 2, "imaginary"),
        (quaternion_blade_convention(), 3, "quaternion_i"),
    ],
)
def test_conventions_are_complete_and_resolve_canonical_names(convention, dimension, role):
    assert convention.dimension == dimension
    assert len(convention.labels) == 1 << dimension
    assert convention.resolve(role).mask < 1 << dimension
    for label in convention.labels:
        assert convention.resolve(label.name.ascii) == label.ref


def test_rga_distinguishes_a_negative_signed_name_from_the_native_blade():
    convention = rga_blade_convention()

    assert convention.resolve("e31") == BladeRef(0b0101, -1)
    assert convention.resolve("e13") == BladeRef(0b0101, 1)
    assert convention.label(0b0101) == BladeLabel(
        Name("e31", "e₃₁", r"\mathbf{e}_{31}"),
        BladeRef(0b0101, -1),
    )


def test_rga_display_order_is_a_complete_grade_grouped_permutation():
    order = rga_display_order()

    assert order.masks[:5] == (0, 1, 2, 4, 8)
    assert order.masks[-1] == 15
    assert set(order.masks) == set(range(16))


def test_convention_validation_rejects_collisions_bad_masks_and_bad_orders():
    labels = ("1", "e1")
    assert BladeConvention(1, {0: "1", 1: "e1"}).label(1).name.ascii == "e1"
    with pytest.raises(ValueError, match="requires 2 labels"):
        BladeConvention(1, ("1",))
    with pytest.raises(ValueError, match="ambiguous canonical"):
        BladeConvention(1, ("same", "same"))
    with pytest.raises(ValueError, match="collides"):
        BladeConvention(1, labels, aliases={"e1": BladeRef(1)})
    with pytest.raises(ValueError, match="duplicate alias"):
        BladeConvention(1, labels, aliases=(("x", 0), ("x", 1)))
    with pytest.raises(ValueError, match="outside dimension"):
        BladeConvention(1, labels, aliases={"x": 2})
    with pytest.raises(ValueError, match="every mask"):
        DisplayOrder(2, (0, 1, 2, 2))


def test_local_name_policy_rejects_duplicates_invalid_identifiers_and_masks():
    with pytest.raises(ValueError, match="duplicate local name"):
        LocalNamePolicy(1, (("e1", 1), ("e1", 0)))
    with pytest.raises(ValueError, match="valid Python identifier"):
        LocalNamePolicy(1, {"not-a-name": 1})
    with pytest.raises(ValueError, match="outside dimension"):
        LocalNamePolicy(1, {"e2": 2})


def test_unknown_blade_error_lists_available_forms():
    convention = rga_blade_convention()

    with pytest.raises(KeyError) as caught:
        convention.resolve("missing")

    assert "e31" in str(caught.value)
    assert "projective" in str(caught.value)
    assert "e31" in convention.available_names


def test_blade_reference_and_label_mask_validation_is_eager():
    with pytest.raises(ValueError, match="non-negative integer"):
        BladeRef(-1)
    with pytest.raises(ValueError, match="orientation"):
        BladeRef(0, 0)
    with pytest.raises(TypeError, match="name must be a Name"):
        BladeLabel("e1", BladeRef(1))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="reference must be a BladeRef"):
        BladeLabel(Name("e1"), 1)  # type: ignore[arg-type]

    convention = euclidean_blade_convention(1)
    with pytest.raises(ValueError, match="integer from 0 to 1"):
        convention.label(2)
    with pytest.raises(ValueError, match="every mask"):
        DisplayOrder(1, (0, True))


def test_indexed_convention_styles_and_custom_subscripts_are_semantic_configuration():
    wedge = indexed_blade_convention(2, subscripts=("x", "y"), style="wedge")
    juxtaposed = indexed_blade_convention(2, prefix=Name("g", "γ", r"\gamma"), start=0, style="juxtapose")

    assert wedge.label(3).name.variants == ("ex^ey", "ex∧ey", r"e_{x} \wedge e_{y}")
    assert juxtaposed.label(3).name.ascii == "g0g1"

    with pytest.raises(ValueError, match="blade style"):
        indexed_blade_convention(2, style="words")
    with pytest.raises(ValueError, match="expected 2 vector subscripts"):
        indexed_blade_convention(2, subscripts=("x",))
    with pytest.raises(ValueError, match="outside the convention dimension"):
        indexed_blade_convention(1, overrides={2: "e2"})


def test_local_policy_mapping_is_read_only_and_skips_nonidentifiers():
    convention = BladeConvention(1, ("1", "not-a-python-name"))
    policy = LocalNamePolicy.from_convention(convention)

    assert policy.mapping == {}
    with pytest.raises(TypeError):
        policy.mapping["x"] = BladeRef(1)  # type: ignore[index]
