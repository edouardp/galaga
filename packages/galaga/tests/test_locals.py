"""Historical locals contracts expressed through independent public v2 policies.

V1 observations are retained in tools/baselines/locals-contracts-v1.json.
ADR-106 documents explicit replacements, not compatibility keyword adapters.
"""

from __future__ import annotations

import pytest

import galaga as ga
from galaga.expression import BladeLiteral, Symbol, evaluate


@pytest.fixture
def cl3():
    return ga.Algebra((1, 1, 1))


def test_default_locals_filtering_and_expression_mode(cl3):
    assert set(cl3.locals()) == {"e1", "e2", "e3", "e12", "e13", "e23", "e123"}
    vectors = ga.LocalNamePolicy(
        cl3.n, ((name, ref) for name, ref in cl3.presentation.local_names.entries if ref.mask.bit_count() == 1)
    )
    assert set(cl3.with_local_names(vectors).locals()) == {"e1", "e2", "e3"}
    value = cl3.locals(expr=True)["e1"]
    assert value.expr == Symbol(ga.Name("e1"))
    assert evaluate(value.expr, algebra=cl3, environment=cl3.locals()) == cl3.blade(1)
    with pytest.raises(TypeError, match="grades"):
        cl3.locals(grades=[1])
    with pytest.raises(TypeError, match="lazy"):
        cl3.locals(lazy=True)


def test_gamma_convention_and_explicit_prefix_have_python_safe_keys():
    algebra = ga.Algebra(config=ga.p_sta())
    compact = ga.indexed_blade_convention(4, prefix="g", start=0)
    policy = ga.LocalNamePolicy(
        4, ((label.name.ascii, label.ref) for label in compact.labels if label.ref.mask.bit_count() in (1, 2))
    )
    values = algebra.with_local_names(policy).locals()
    assert {key for key, value in values.items() if value.homogeneous_grade() == 1} == {"g0", "g1", "g2", "g3"}
    assert {"g0", "g1", "g2", "g3", "g01"} <= set(values)
    assert "y0" not in values
    assert all(key.isidentifier() for key in values)
    assert values["g0"].display("value/unicode") == "γ₀"
    assert values["g01"].display("value/unicode") == "γ₀γ₁"
    assert values["g01"].display("name/ascii") == "g01"


def test_prefix_override_is_uniform_but_preserves_variable_hints():
    algebra = ga.Algebra(config=ga.p_sta(sigmas=True))
    compact = ga.indexed_blade_convention(4, prefix="g", start=0, overrides={15: "i"})
    policy = ga.LocalNamePolicy(
        4, ((label.name.ascii, algebra.blade_label(mask).ref) for mask, label in enumerate(compact.labels) if mask)
    )
    values = algebra.with_local_names(policy).locals()
    assert {"g0", "g1", "g2", "g3", "g01", "i"} <= set(values)
    assert "s1" not in values
    g0, g1, _, _ = algebra.basis_vectors()
    assert values["g01"] == g1 * g0
    assert algebra.locals()["s1"] == values["g01"]
    assert values["i"] == algebra.I
    with pytest.raises(TypeError, match="prefix"):
        algebra.locals(prefix="g")


def test_empty_prefix_uses_axis_suffixes():
    labels = ga.indexed_blade_convention(3, subscripts=tuple("xyz"))
    policy = ga.LocalNamePolicy(
        3, (("".join(axis for bit, axis in enumerate("xyz") if mask & (1 << bit)), mask) for mask in range(1, 8))
    )
    algebra = ga.Algebra(3, blades=labels, local_names=policy)
    assert list(algebra.locals()) == ["x", "y", "xy", "z", "xz", "yz", "xyz"]
    e1, e2, _ = algebra.basis_vectors()
    assert algebra.locals()["xy"] == e1 ^ e2
    assert algebra.locals()["xy"].display("value/unicode") == "exy"


def test_prefix_must_be_a_string():
    # Prefix rewriting is retired; reject it even when well typed. Policies
    # validate actual identifiers instead of coercing arbitrary objects.
    with pytest.raises(TypeError, match="prefix"):
        ga.Algebra(config=ga.p_sta(sigmas=True)).locals(prefix=123)
    with pytest.raises(ValueError, match="non-empty strings"):
        ga.LocalNamePolicy(4, [(123, 3)])


@pytest.mark.parametrize(
    ("style", "rendered"),
    (("wedge", "v₁∧v₂"), ("juxtapose", "v₁v₂")),
)
def test_display_style_does_not_leak_into_python_keys(style, rendered):
    labels = ga.indexed_blade_convention(3, prefix="v", style=style, overrides={7: "I"})
    compact = ga.indexed_blade_convention(3, prefix="v")
    algebra = ga.Algebra(3, blades=labels, local_names=ga.LocalNamePolicy.from_convention(compact))
    values = algebra.locals()
    assert "v12" in values
    assert "v1v2" not in values
    assert all(name.isidentifier() for name in values)
    assert values["v12"].display("value/unicode") == rendered
    assert values["v12"].display("name/ascii") == "v12"
    assert values["v12"] == algebra.blade(1) ^ algebra.blade(2)


def test_variable_hints_and_display_overrides_have_separate_local_policy():
    labels = ga.indexed_blade_convention(3, overrides={3: "B", 7: "I"})
    hinted = ga.Algebra(3, blades=labels, local_names=ga.LocalNamePolicy.from_convention(labels))
    display_only = ga.Algebra(3, blades=ga.indexed_blade_convention(3, overrides={3: "class"}))
    assert {"B", "I"} <= set(hinted.locals())
    assert "class" not in display_only.locals()
    assert "_class" not in display_only.locals()
    assert "e12" in display_only.locals()
    assert display_only.locals()["e12"].display("value/unicode") == "class"
    derived = ga.LocalNamePolicy.from_convention(display_only.presentation.blades)
    assert "class" not in derived.mapping
    assert "e12" not in derived.mapping  # No invented replacement for a keyword.


def test_signed_sta_factories_preserve_the_defining_order():
    algebra = ga.Algebra(config=ga.p_sta(sigmas=True))
    g0, g1, g2, g3 = algebra.basis_vectors()
    expected = (g1 * g0, g2 * g0, g3 * g0)
    values = algebra.locals()
    assert tuple(values[key] for key in ("s1", "s2", "s3")) == expected
    assert tuple(algebra.blade(key) for key in ("g0g1", "g0g2", "g0g3")) == tuple(-v for v in expected)
    # V1's first basis_blades(2) value had the displayed sigma sign.
    # Native enumeration is deliberately independent in v2.
    assert algebra.basis_blades(2)[0] == g0 ^ g1 == -expected[0]


def test_blade_lookup_and_basis_blades_expression_mode(cl3):
    e12, _, _ = cl3.basis_blades(2, expr=True)
    assert e12.expr == BladeLiteral(3)
    assert evaluate(e12.expr, algebra=cl3) == cl3.blade("e12")
    assert cl3.blade("e12").data[3] == 1.0


def test_scalar_blade_lookup_accepts_empty_and_one(cl3):
    assert cl3.blade(0) == cl3.blade("1") == cl3.scalar(1.0)
    # Empty-string implicit scalar parsing is retired; names are configured.
    with pytest.raises(KeyError, match="unknown blade"):
        cl3.blade("")


def test_blade_lookup_rejects_out_of_range_basis_name(cl3):
    with pytest.raises(KeyError, match="unknown blade"):
        cl3.blade("e5")
    with pytest.raises(ValueError, match="blade mask"):
        cl3.blade(1 << cl3.n)
