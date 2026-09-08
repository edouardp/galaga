"""Immutable public replacements for the v1 naming and state redesign."""

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import pytest

import galaga as ga

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/redesign-v1.json").read_text())
GRAMS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    ((2, 0.5, -0.25), (0.5, -1, 0.75), (-0.25, 0.75, 3)),
    ((1, 1, 0), (1, 1, 0), (0, 0, 0)),
)


def observation(identifier, local):
    row = next(row for row in ARCHIVE["observations"] if row["id"] == identifier)
    return ARCHIVE["snapshots"][row["locals"][local]["snapshot"]]


def sparse_data(snapshot):
    data = np.zeros(1 << len(snapshot["signature"]))
    indices = [pair[0] for pair in snapshot["coefficients"]]
    assert len(indices) == len(set(indices))
    for mask, coefficient in snapshot["coefficients"]:
        assert type(mask) is int and 0 <= mask < len(data)
        assert np.isfinite(coefficient) and coefficient != 0
        data[mask] = coefficient
    return data


def assert_data(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape and actual.ndim == expected.ndim == 1
    assert np.isfinite(actual).all() and np.isfinite(expected).all()
    np.testing.assert_array_equal(actual, expected)


NAME_CASES = (
    ("TestNameMethod.test_name_sets_all_variants", "v", ga.Name("v")),
    ("TestNameMethod.test_name_with_overrides", "v", ga.Name("v", "𝐯", r"\mathbf{v}")),
    ("TestNameMethod.test_name_ascii_kwarg", "v", ga.Name("v_ascii", "v", "v")),
    ("TestNameAutoDerive.test_greek_auto_derive", "v", ga.Name.from_latex(r"\theta")),
    ("TestNameAutoDerive.test_mathbf_auto_derive", "v", ga.Name.from_latex(r"\mathbf{F}")),
    ("TestNameAutoDerive.test_hbar_auto_derive", "v", ga.Name.from_latex(r"\hbar")),
    ("TestNameAutoDerive.test_user_unicode_overrides", "v", ga.Name.from_latex(r"\theta", unicode="MINE")),
    ("TestNameAutoDerive.test_user_ascii_overrides", "v", ga.Name.from_latex(r"\theta", ascii="MINE")),
    ("TestNameAutoDerive.test_both_overrides", "v", ga.Name.from_latex(r"\theta", ascii="A", unicode="U")),
    ("TestNameAutoDerive.test_unknown_latex_uses_label", "v", ga.Name.from_latex(r"\weirdthing", ascii="v")),
    ("TestNameAutoDerive.test_no_latex_uses_label", "v", ga.Name("myvar")),
    ("TestNameLatexOnly.test_latex_only_greek", "v", ga.Name.from_latex(r"\theta")),
    ("TestNameLatexOnly.test_latex_only_mathbf", "v", ga.Name.from_latex(r"\mathbf{F}")),
    (
        "TestNameLatexOnly.test_latex_only_unknown_uses_latex_as_fallback",
        "v",
        ga.Name.from_latex(r"\weirdthing", ascii=r"\weirdthing"),
    ),
)


@pytest.mark.parametrize("identifier, local, name", NAME_CASES, ids=[row[0] for row in NAME_CASES])
def test_archived_names_use_explicit_variants_or_opt_in_latex_conversion(identifier, local, name):
    old = observation(identifier, local)
    assert tuple(old["name"]) == name.variants
    algebra = ga.Algebra(old["signature"])
    original = algebra.scalar(1) if identifier.endswith("hbar_auto_derive") else algebra.blade(1)
    value = original.named(name)
    assert_data(value.data, sparse_data(old))
    assert value.name == name and value.expr is None
    assert original.name is None and value.numeric is original.numeric and value is not original
    for target, spelling in zip(("ascii", "unicode", "latex"), name.variants, strict=True):
        assert value.display("name/" + target) == spelling


@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_plain_names_preserve_whitespace_and_latex_does_not_implicitly_derive_spellings(target):
    vector = ga.Algebra(1).blade(1)
    raw = {"ascii": "  v  ", "unicode": " θ ", "latex": r" \theta "}
    name = ga.Name(**raw)
    value = vector.named(name)
    assert value.name.for_target(target) == raw[target]
    explicit = vector.named(ga.Name(**{key: text.strip() for key, text in raw.items()}))
    assert explicit.name.for_target(target) == raw[target].strip()
    assert ga.Name.from_latex(raw["latex"]) == ga.Name("theta", "θ", r"\theta")
    assert vector.named("v", latex=r"\theta").name == ga.Name("v", "v", r"\theta")
    assert_data(vector.data, explicit.data)
    with pytest.raises(ValueError, match="unsupported"):
        ga.Name.from_latex(r"\weirdthing")
    with pytest.raises(TypeError):
        vector.named()
    with pytest.raises(TypeError):
        vector.named(latex=r"\theta")


@pytest.mark.parametrize("factory", ("vector", "arithmetic", "basis", "plane", "locals", "pseudoscalar", "lookup"))
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("gram", GRAMS)
def test_all_factories_and_arithmetic_values_have_the_same_immutable_naming_contract(factory, expr, gram):
    algebra = ga.Algebra(gram=gram)
    a, b, _ = algebra.basis_vectors(expr=expr)
    values = {
        "vector": algebra.vector((3, 4, 0), expr=expr),
        "arithmetic": a + b,
        "basis": a,
        "plane": algebra.basis_blades(2, expr=expr)[0],
        "locals": algebra.locals(expr=expr)["e1"],
        "pseudoscalar": algebra.pseudoscalar(expr=expr),
        "lookup": algebra.blade("e1", expr=expr),
    }
    original = values[factory]
    data, name, expression, value_hash = original.data.copy(), original.name, original.expr, hash(original)
    renamed = original.named("v")
    again = renamed.named("w")
    assert original.name == name and original.expr is expression
    assert renamed is not original and again is not renamed
    assert renamed.name == ga.Name("v") and again.name == ga.Name("w")
    assert renamed.numeric is again.numeric is original.numeric
    assert renamed.expr is again.expr is expression
    assert hash(original) == hash(renamed) == hash(again) == value_hash
    for value in (original, renamed, again):
        assert_data(value.data, data)
        for attribute in ("name", "expr", "numeric", "algebra"):
            with pytest.raises(AttributeError):
                setattr(value, attribute, None)
        with pytest.raises(ValueError):
            value.data[0] = 42


ACTIONS = {
    "unnamed": lambda value: value.unnamed(),
    "without_expr": lambda value: value.without_expr(),
    "with_expr": lambda value: value.with_expr(),
    "numeric_snapshot": lambda value: value.unnamed().without_expr(),
    "numeric_snapshot_other_order": lambda value: value.without_expr().unnamed(),
    "rename": lambda value: value.named("w"),
}


@pytest.mark.parametrize("action", ACTIONS)
@pytest.mark.parametrize("named", (False, True))
@pytest.mark.parametrize("expr", (False, True))
def test_explicit_state_transitions_preserve_values_and_change_only_the_selected_outer_state(action, named, expr):
    algebra = ga.Algebra(3)
    a, b, _ = algebra.basis_vectors(expr=expr)
    original = 3 * a + 4 * b
    if named:
        original = original.named("v")
    before = (original.name, original.expr, hash(original))
    result = ACTIONS[action](original)
    expected_name = ga.Name("w") if action == "rename" else original.name
    if action in {"unnamed", "numeric_snapshot", "numeric_snapshot_other_order"}:
        expected_name = None
    expected_expr = original.expr
    if action in {"without_expr", "numeric_snapshot", "numeric_snapshot_other_order"}:
        expected_expr = None
    elif action == "with_expr":
        expected_expr = ga.Symbol("v") if named else original.expr or ga.MultivectorLiteral(original.data)
    assert result.name == expected_name and result.expr == expected_expr
    assert result is not original and result.numeric is original.numeric
    assert (original.name, original.expr, hash(original)) == before
    assert_data(result.data, [0, 3, 4, 0, 0, 0, 0, 0])
    assert hash(result) == hash(original)
    repeated = ACTIONS[action](result)
    assert repeated.name == result.name and repeated.expr == result.expr
    assert repeated.numeric is original.numeric
    if result.expr is not None:
        assert_data(ga.evaluate(result.expr, algebra=algebra, environment={"v": original}).data, result.data)


def test_named_operands_can_track_again_after_without_expr_but_full_snapshots_do_not():
    algebra = ga.Algebra(3)
    source = (algebra.blade(1, expr=True) + algebra.blade(2, expr=True)).named("v")
    stripped = source.without_expr()
    assert stripped.name == source.name and stripped.expr is None
    tracked = 2 * stripped
    assert tracked.expr == ga.Call("scalar_multiply", (ga.Symbol("v"),), {"scalar": 2})
    untracked = 2 * stripped.unnamed()
    assert untracked.name is None and untracked.expr is None
    assert tracked == untracked and hash(tracked) == hash(untracked)
    rebound = ga.evaluate(tracked.expr, algebra=algebra, environment={"v": algebra.blade(4)})
    assert rebound == 2 * algebra.blade(4) and tracked != rebound
    assert source.expr is not None and stripped.expr is None


@pytest.mark.parametrize("mask", (1, 3, 7))
@pytest.mark.parametrize("gram", GRAMS)
def test_blade_renaming_uses_immutable_views_or_explicit_scopes_and_preserves_exterior_values(mask, gram):
    algebra = ga.Algebra(gram=gram)
    original = algebra.blade(mask, expr=True)
    label = algebra.blade_label(mask)
    renamed = ga.Name("x", "χ", r"\chi")
    labels = list(algebra.presentation.blades.labels)
    labels[mask] = ga.BladeLabel(renamed, label.ref)
    convention = ga.BladeConvention(algebra.n, labels)
    view = algebra.with_blades(convention)
    assert view.numeric is algebra.numeric
    assert view.blade("x") == original
    assert view.blade_label(mask).name == renamed and algebra.blade_label(mask) == label
    for target in ("ascii", "unicode", "latex"):
        before = original.display("value/" + target)
        assert before == label.name.for_target(target)
        assert original.display("value/" + target, presentation=view.presentation) == renamed.for_target(target)
        with algebra.use_presentation(view.presentation):
            assert original.display("value/" + target) == renamed.for_target(target)
        assert original.display("value/" + target) == before
    with pytest.raises(FrozenInstanceError):
        label.name = renamed
    with pytest.raises(FrozenInstanceError):
        label.name.ascii = "changed"
    # Chains create new immutable tables, not live BasisBlade mutation.
    newer = list(convention.labels)
    newer[mask] = ga.BladeLabel(ga.Name("plane", latex=r"\beta_{12}"), label.ref)
    second = view.with_blades(ga.BladeConvention(algebra.n, newer))
    assert second.blade_label(mask).name.ascii == "plane"
    assert view.blade_label(mask).name == renamed
    assert_data(original.data, ga.evaluate(original.expr, algebra=algebra).data)
    with pytest.raises(ValueError, match="signed unit"):
        algebra.blade(algebra.blade(1) + algebra.blade(2))
    with pytest.raises(ValueError, match="signed unit"):
        algebra.blade(2 * algebra.blade(mask))
    with pytest.raises((TypeError, ValueError)):
        algebra.blade_label(3.14)
    assert not hasattr(algebra, "get_basis_blade")


@pytest.mark.parametrize("dimension", (9, 10))
def test_high_dimension_lookup_resolves_complete_labels_without_digit_parsing(dimension):
    algebra = ga.Algebra(dimension)
    mask = 1 | (1 << (dimension - 1))
    label = algebra.blade_label(mask)
    expected = np.zeros(algebra.dim)
    expected[mask] = 1
    for target in ("ascii", "unicode", "latex"):
        spelling = label.name.for_target(target)
        assert_data(algebra.blade(spelling).data, expected)
    if dimension == 10:
        # V1 rejected this name at lookup; v2's complete table resolves it.
        assert label.name.ascii == "e110" and algebra.blade("e110") == algebra.blade(mask)
    names = [ga.Name("1" if i == 0 else f"blade_{i}") for i in range(algebra.dim)]
    custom = algebra.with_blades(ga.BladeConvention(dimension, names, aliases={"v01": 3}))
    assert custom.blade("v01") == custom.blade(3)
    assert_data(custom.blade(f"blade_{mask}").data, expected)
    names[mask] = ga.Name("collision")
    assert custom.blade_label(mask).name.ascii == f"blade_{mask}"
    labels = list(custom.presentation.blades.labels)
    labels[mask] = ga.BladeLabel(labels[1].name, ga.BladeRef(mask))
    with pytest.raises(ValueError, match="ambiguous"):
        ga.BladeConvention(dimension, labels)


def test_v1_state_mutators_and_lazy_flags_are_not_reintroduced():
    algebra = ga.Algebra(3)
    value = algebra.blade(1)
    for name in ("lazy", "eager", "anon", "eval", "reveal", "copy_as", "symbolic"):
        assert not hasattr(value, name)
    assert not callable(value.name)
    with pytest.raises(TypeError, match="lazy"):
        algebra.basis_vectors(lazy=True)
    with pytest.raises(TypeError, match="grade"):
        ga.Symbol("v", grade=1)
    with pytest.raises(TypeError):
        value.named("v", ascii="v_ascii")
