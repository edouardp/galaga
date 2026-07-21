from types import MappingProxyType

import numpy as np
import pytest

from galaga import core
from galaga.blades import BladeRef, DisplayOrder, LocalNamePolicy, default_blade_convention
from galaga.expression import BladeLiteral, Call
from galaga.facade import Algebra
from galaga.presentation import (
    AlgebraConfig,
    AlgebraDefinition,
    DisplayPolicy,
    ModelConfig,
    Notation,
    default_presentation,
)
from galaga.presets import EuclideanPreset, LengyelRGAPreset


def test_named_and_signed_blade_factories_have_independently_verifiable_coefficients():
    algebra = Algebra(config=LengyelRGAPreset())

    assert algebra.blade(0b0101).coefficient(0b0101) == 1
    assert algebra.blade(BladeRef(0b0101, -1)).coefficient(0b0101) == -1
    assert algebra.blade("e31").coefficient(0b0101) == -1
    assert algebra.blade("e13").coefficient(0b0101) == 1
    assert np.count_nonzero(algebra.blade("e31").data) == 1


def test_multivector_blade_factory_preserves_rga_orientation_and_replaces_provenance():
    algebra = Algebra(config=LengyelRGAPreset())
    e1, _, e3, _ = algebra.basis_vectors(expr=True)
    displayed_positive = (e3 ^ e1).named("constructed")
    displayed_negative = e1 ^ e3

    positive_literal = algebra.blade(displayed_positive, expr=True)
    negative_literal = algebra.blade(displayed_negative, expr=True)
    untracked = algebra.blade(displayed_positive)

    assert isinstance(displayed_positive.expr, Call)
    assert positive_literal.name is None
    assert positive_literal.coefficient(0b0101) == -1
    assert positive_literal.expr == BladeLiteral(0b0101, -1)
    assert positive_literal.latex(content="expr") == r"\mathbf{e}_{31}"
    assert negative_literal.coefficient(0b0101) == 1
    assert negative_literal.expr == BladeLiteral(0b0101, 1)
    assert negative_literal.latex(content="expr") == r"-\mathbf{e}_{31}"
    assert untracked.name is None
    assert untracked.expr is None
    assert untracked == displayed_positive


def test_multivector_blade_factory_rejects_nonunit_and_foreign_values():
    algebra = Algebra(config=LengyelRGAPreset())
    e1, e2, _, _ = algebra.basis_vectors(expr=True)

    for invalid in (algebra.scalar(0), e1 + e2, 2 * (e1 ^ e2)):
        with pytest.raises(ValueError, match="signed unit basis blade"):
            algebra.blade(invalid, expr=True)

    foreign = Algebra(config=LengyelRGAPreset()).basis_vectors()[0]
    with pytest.raises(ValueError, match="different numeric algebra"):
        algebra.blade(foreign, expr=True)


def test_blades_factory_literalizes_computed_rga_blades_in_argument_order():
    algebra = Algebra(config=LengyelRGAPreset())
    e1, e2, e3, e4 = algebra.basis_vectors(expr=True)

    values = algebra.blades(e2 ^ e3, e3 ^ e1, e4 ^ e1, e4 ^ e2, expr=True)

    assert isinstance(values, tuple)
    assert tuple(value.expr for value in values) == (
        BladeLiteral(0b0110, 1),
        BladeLiteral(0b0101, -1),
        BladeLiteral(0b1001, -1),
        BladeLiteral(0b1010, -1),
    )
    assert tuple(value.latex(content="expr") for value in values) == (
        r"\mathbf{e}_{23}",
        r"\mathbf{e}_{31}",
        r"\mathbf{e}_{41}",
        r"\mathbf{e}_{42}",
    )


def test_blades_factory_accepts_mixed_singular_inputs_and_validates_shared_expr_flag():
    algebra = Algebra(config=LengyelRGAPreset())
    e1, e2, _, _ = algebra.basis_vectors(expr=True)

    values = algebra.blades("e23", BladeRef(0b0101, -1), e1 ^ e2)

    assert tuple(value.expr for value in values) == (None, None, None)
    assert tuple(np.flatnonzero(value.data).item() for value in values) == (0b0110, 0b0101, 0b0011)
    assert algebra.blades() == ()
    with pytest.raises(TypeError, match="expr must be a boolean"):
        algebra.blades(expr=None)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="signed unit basis blade"):
        algebra.blades(e1 + e2, expr=True)


def test_basis_factories_remain_native_numeric_factories():
    algebra = Algebra(config=EuclideanPreset(3))

    assert [value.coefficient(1 << index) for index, value in enumerate(algebra.basis_vectors())] == [1, 1, 1]
    assert [np.flatnonzero(value.data).item() for value in algebra.basis_blades(2)] == [3, 5, 6]
    assert np.flatnonzero(algebra.pseudoscalar().data).item() == 7
    assert algebra.blade_label(5).name.ascii == "e13"


def test_locals_are_read_only_and_follow_signed_local_name_policy():
    algebra = Algebra(config=LengyelRGAPreset())

    values = algebra.locals()

    assert isinstance(values, MappingProxyType)
    assert values["e31"].coefficient(5) == -1
    with pytest.raises(TypeError):
        values["replacement"] = algebra.identity  # type: ignore[index]


def test_presentation_views_share_numeric_algebra_but_not_presentation_state():
    original = Algebra(config=EuclideanPreset(2))
    teaching = original.with_notation(Notation("teaching"))

    assert teaching.numeric is original.numeric
    assert teaching.presentation.notation.id == "teaching"
    assert original.presentation.notation.id == "euclidean"
    assert teaching.blade(1) == original.blade(1)
    assert hash(teaching.blade(1)) == hash(original.blade(1))


def test_invalid_named_lookup_reports_the_available_convention_names():
    algebra = Algebra(config=LengyelRGAPreset())

    with pytest.raises(KeyError) as caught:
        algebra.blade("e99")

    assert "e31" in str(caught.value)
    assert "projective" in str(caught.value)


def test_all_fine_grained_facade_views_share_the_same_numeric_algebra():
    original = Algebra(config=EuclideanPreset(2))
    locals_policy = LocalNamePolicy(2, {"x": 1})
    order = DisplayOrder(2, (0, 2, 1, 3))
    display = DisplayPolicy(content="full", target="ascii")
    blades = default_blade_convention(2)

    views = (
        original.with_blades(blades),
        original.with_local_names(locals_policy),
        original.with_display_order(order),
        original.with_display(display),
    )

    assert all(view.numeric is original.numeric for view in views)
    assert views[0].presentation.blades is blades
    assert views[1].locals()["x"] == original.blade(1)
    assert views[2].display_order == order.masks
    assert views[3].presentation.display is display


def test_direct_complete_config_and_scalar_algebra_paths_are_supported():
    config = AlgebraConfig(
        AlgebraDefinition.from_signature((1,), id="direct"),
        default_presentation(1),
    )
    direct = Algebra(config=config)
    scalar = Algebra(
        config=AlgebraConfig(
            AlgebraDefinition.from_signature((), id="scalar"),
            default_presentation(0),
        )
    )

    assert direct.id == "direct"
    assert scalar.n == 0
    assert scalar.identity == 1


def test_from_numeric_validates_presentation_and_model_without_copying_core():
    numeric = core.Algebra(2)
    facade = Algebra.from_numeric(numeric)

    assert facade.numeric is numeric
    with pytest.raises(TypeError, match="core.Algebra"):
        Algebra.from_numeric(object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="does not match numeric dimension"):
        Algebra.from_numeric(numeric, presentation=default_presentation(1))
    with pytest.raises(ValueError, match="outside the algebra dimension"):
        Algebra.from_numeric(
            numeric,
            model=ModelConfig("bad", {"outside": BladeRef(4)}),
        )


def test_invalid_config_protocol_and_presentation_override_types_fail_clearly():
    class MissingBuild:
        pass

    class BadBuild:
        def build(self):
            return "not a config"

    with pytest.raises(TypeError, match="object with build"):
        Algebra(config=MissingBuild())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"build\(\) must return"):
        Algebra(config=BadBuild())  # type: ignore[arg-type]
    invalid_overrides = (
        ({"presentation": "bad"}, "presentation must be"),
        ({"blades": "bad"}, "blades must be"),
        ({"notation": "short"}, "notation must be"),
        ({"local_names": "bad"}, "local_names must be"),
        ({"display_order": "bad"}, "display_order must be"),
        ({"display": "bad"}, "display must be"),
    )
    for keywords, message in invalid_overrides:
        with pytest.raises(TypeError, match=message):
            Algebra(2, **keywords)


def test_presentation_and_blade_dimension_errors_are_reported_at_the_boundary():
    with pytest.raises(ValueError, match="does not match numeric dimension"):
        Algebra(2, presentation=default_presentation(1))

    algebra = Algebra(2)
    with pytest.raises(ValueError, match="does not match numeric dimension"):
        algebra.resolve_presentation(default_presentation(1))
    with pytest.raises(TypeError, match="integer bitmask"):
        algebra.blade(object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match=r"\[0, 4\)"):
        algebra.blade(4)
