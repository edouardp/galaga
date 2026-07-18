"""Blade lookup, local-name policy, and signed basis-factory contracts."""

from __future__ import annotations

import pytest

from galaga import Algebra, b_default, b_gamma, b_sta
from galaga.blade_convention import BladeConvention


@pytest.fixture
def cl3():
    return Algebra((1, 1, 1))


def test_default_locals_filtering_and_expression_mode(cl3):
    assert set(cl3.locals()) == {"e1", "e2", "e3", "e12", "e13", "e23", "e123"}
    assert set(cl3.locals(grades=[1])) == {"e1", "e2", "e3"}
    assert cl3.locals(lazy=True)["e1"]._is_symbolic


def test_gamma_convention_and_explicit_prefix_have_python_safe_keys():
    algebra = Algebra(1, 3, blades=b_gamma())
    default = algebra.locals(grades=[1])
    explicit = algebra.locals(grades=[1, 2], prefix="g")

    assert set(default) == {"g0", "g1", "g2", "g3"}
    assert {"g0", "g1", "g2", "g3", "g01"} <= set(explicit)
    assert "y0" not in explicit
    assert str(explicit["g0"]) == "γ₀"
    assert str(explicit["g01"]) == "γ₀γ₁"


def test_prefix_override_is_uniform_but_preserves_variable_hints():
    algebra = Algebra(1, 3, blades=b_sta(sigmas=True))
    values = algebra.locals(prefix="g")

    assert {"g0", "g1", "g2", "g3", "g01"} <= set(values)
    assert "s1" not in values
    assert "i" in values


def test_empty_prefix_uses_axis_suffixes():
    algebra = Algebra(3, blades=b_default(subscripts="xyz"))

    assert list(algebra.locals(prefix="")) == ["x", "y", "xy", "z", "xz", "yz", "xyz"]


def test_prefix_must_be_a_string():
    algebra = Algebra(1, 3, blades=b_sta(sigmas=True))

    with pytest.raises(TypeError, match="prefix must be a string or None"):
        algebra.locals(grades=[2], prefix=123)


@pytest.mark.parametrize(
    ("style", "rendered"),
    (("wedge", "v₁∧v₂"), ("juxtapose", "v₁v₂")),
)
def test_display_style_does_not_leak_into_python_keys(style, rendered):
    algebra = Algebra(3, blades=BladeConvention(prefix="v", style=style, overrides={"pss": "I"}))
    values = algebra.locals()

    assert "v12" in values
    assert "v1v2" not in values
    assert all(name.isidentifier() for name in values)
    assert str(values["v12"]) == rendered


def test_variable_hints_and_display_overrides_have_separate_local_policy():
    hinted = Algebra(
        3,
        blades=BladeConvention(
            overrides={"+1+2": "B", "pss": "I"},
            variable_hints={"+1+2": "B", "pss": "I"},
        ),
    )
    display_only = Algebra(3, blades=b_default(overrides={"+1+2": "class"}))

    assert {"B", "I"} <= set(hinted.locals())
    assert "class" not in display_only.locals()
    assert "_class" not in display_only.locals()
    assert "e12" in display_only.locals()


def test_signed_sta_factories_preserve_the_defining_order():
    algebra = Algebra(1, 3, blades=b_sta(sigmas=True))
    g0, g1, g2, g3 = algebra.basis_vectors()
    locals_by_name = algebra.locals(grades=[2])
    bivectors = algebra.basis_blades(2)

    assert locals_by_name["g01"] == g1 * g0
    assert locals_by_name["g02"] == g2 * g0
    assert locals_by_name["g03"] == g3 * g0
    assert bivectors[0] == g1 * g0


def test_blade_lookup_and_basis_blades_expression_mode(cl3):
    e12, _, _ = cl3.basis_blades(2, lazy=True)

    assert e12._is_symbolic
    assert cl3.blade("e12").data[3] == 1.0


def test_scalar_blade_lookup_accepts_empty_and_one(cl3):
    assert cl3.blade("") == cl3.scalar(1.0)
    assert cl3.blade("1") == cl3.scalar(1.0)


def test_blade_lookup_rejects_out_of_range_basis_name(cl3):
    with pytest.raises(ValueError, match="out of range"):
        cl3.blade("e5")
