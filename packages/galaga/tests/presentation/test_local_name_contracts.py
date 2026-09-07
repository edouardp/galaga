"""Archived bindings and coefficient-first ownership for independent locals."""

import json
from pathlib import Path
from types import MappingProxyType

import numpy as np
import pytest

import galaga as ga
from galaga.expression import BladeLiteral, Symbol, evaluate

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/locals-contracts-v1.json").read_text())
GRAMS = (
    ((1, 0), (0, 1)),
    ((2, 0.5), (0.5, -1)),
    ((1, 1), (1, 1)),
)


def historical_binding_views():
    """Explicit v2 policies retaining the archived Python keys and values."""
    euclidean = ga.Algebra(3)
    gamma = ga.Algebra(config=ga.p_sta())
    sta = ga.Algebra(config=ga.p_sta(sigmas=True))
    compact = ga.indexed_blade_convention(4, prefix="g", start=0, overrides={15: "i"})
    sta_policy = ga.LocalNamePolicy(
        4, ((label.name.ascii, sta.blade_label(mask).ref) for mask, label in enumerate(compact.labels) if mask)
    )
    axes = ga.LocalNamePolicy(
        3, (("".join(axis for bit, axis in enumerate("xyz") if mask & (1 << bit)), mask) for mask in range(1, 8))
    )
    hinted = ga.indexed_blade_convention(3, overrides={3: "B", 7: "I"})
    views = {
        "default": euclidean,
        "vectors": euclidean.with_local_names(
            ga.LocalNamePolicy(
                3,
                ((name, ref) for name, ref in euclidean.presentation.local_names.entries if ref.mask.bit_count() == 1),
            )
        ),
        "gamma_vectors": gamma.with_local_names(
            ga.LocalNamePolicy(
                4, ((label.name.ascii, label.ref) for label in compact.labels if label.ref.mask.bit_count() == 1)
            )
        ),
        "gamma_vectors_bivectors": gamma.with_local_names(
            ga.LocalNamePolicy(
                4, ((label.name.ascii, label.ref) for label in compact.labels if label.ref.mask.bit_count() in (1, 2))
            )
        ),
        "sta_prefixed": sta.with_local_names(sta_policy),
        "axes": ga.Algebra(3, blades=ga.indexed_blade_convention(3, subscripts=tuple("xyz")), local_names=axes),
        "hinted": ga.Algebra(3, blades=hinted, local_names=ga.LocalNamePolicy.from_convention(hinted)),
        "display_only": ga.Algebra(3, blades=ga.indexed_blade_convention(3, overrides={3: "class"})),
        "sta_bivectors": sta.with_local_names(
            ga.LocalNamePolicy(4, ((name, ref) for name, ref in sta_policy.entries if ref.mask.bit_count() == 2))
        ),
    }
    for style in ("wedge", "juxtapose"):
        views[style] = ga.Algebra(
            3,
            blades=ga.indexed_blade_convention(3, prefix="v", style=style, overrides={7: "I"}),
            local_names=ga.LocalNamePolicy.from_convention(ga.indexed_blade_convention(3, prefix="v")),
        )
    return views


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda table: table["id"])
@pytest.mark.parametrize("expr", (False, True))
def test_archived_keys_coefficients_order_and_value_rendering(table, expr):
    algebra = historical_binding_views()[table["id"]]
    values = algebra.locals(expr=expr)
    assert list(values) == [row["key"] for row in table["bindings"]]
    for row in table["bindings"]:
        expected = np.asarray(row["coefficients"])
        assert expected.shape == (algebra.dim,)
        assert np.isfinite(expected).all()
        value = values[row["key"]]
        np.testing.assert_array_equal(value.data, expected)
        assert value.display("value/unicode") == row["unicode"]
        assert value.name == ga.Name(row["key"])
        assert value.expr == (Symbol(row["key"]) if expr else None)
        if expr:
            replay = evaluate(value.expr, algebra=algebra, environment=values)
            np.testing.assert_array_equal(replay.data, expected)


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("orientation", (-1, 1))
@pytest.mark.parametrize("style", ("compact", "wedge", "juxtapose"))
def test_signed_local_values_and_nonzero_replay_are_independent_of_display(gram, orientation, style):
    algebra = ga.Algebra(gram=gram, product_backend="reference")
    e1, e2 = algebra.basis_vectors()
    expected_plane = orientation * (e1 ^ e2)
    expected_product = e1 * e2
    np.testing.assert_array_equal(expected_plane.data, [0, 0, 0, orientation])
    np.testing.assert_array_equal(expected_product.data, [gram[0][1], 0, 0, 1])
    labels = ga.indexed_blade_convention(2, prefix="v", style=style)
    policy = ga.LocalNamePolicy(2, {"x": 1, "y": 2, "plane": ga.BladeRef(3, orientation)})
    view = algebra.with_blades(labels).with_local_names(policy)
    before = algebra.presentation
    for expr in (False, True):
        values = view.locals(expr=expr)
        x, y, plane = (values[key] for key in ("x", "y", "plane"))
        assert plane.expr == (Symbol("plane") if expr else None)
        assert plane == expected_plane
        assert x * y == expected_product
        mixed = 2 * x + 3 * y + 5 * plane
        np.testing.assert_array_equal(mixed.data, [0, 2, 3, 5 * orientation])
        assert hash(plane) == hash(expected_plane)
        expression = mixed.expr
        for target in ("ascii", "unicode", "latex"):
            assert plane.display(f"value/{target}") == view.blade(ga.BladeRef(3, orientation)).display(
                f"value/{target}"
            )
            assert plane.display(f"name/{target}") == "plane"
            assert mixed.display(f"full/{target}")
            np.testing.assert_array_equal(mixed.data, [0, 2, 3, 5 * orientation])
            assert mixed.expr is expression
        # Names opt subsequent operations into provenance even when the
        # factory did not attach an initial leaf expression.
        replay = evaluate(mixed.expr, algebra=view, environment=values)
        np.testing.assert_array_equal(replay.data, mixed.data)
    assert view.numeric is algebra.numeric
    assert algebra.presentation is before
    assert list(algebra.locals()) == ["e1", "e2", "e12"]


def test_symbols_require_explicit_bindings_while_literals_keep_their_signed_value():
    algebra = ga.Algebra(2, local_names=ga.LocalNamePolicy(2, {"B": ga.BladeRef(3, -1)}))
    old = algebra.locals(expr=True)
    symbol = old["B"]
    literal = algebra.blade(symbol, expr=True)
    assert symbol.expr == Symbol("B")
    assert literal.expr == BladeLiteral(3, -1)
    with pytest.raises(KeyError, match="no value supplied"):
        evaluate(symbol.expr, algebra=algebra)
    changed = algebra.presentation.with_local_names(ga.LocalNamePolicy(2, {"B": 3}))
    with algebra.use_presentation(changed):
        new = algebra.locals(expr=True)
        assert old["B"] == -new["B"]
        assert old["B"].same_expression(new["B"])
        assert evaluate(symbol.expr, algebra=algebra, environment=old) == old["B"]
        assert evaluate(symbol.expr, algebra=algebra, environment=new) == new["B"]
        assert evaluate(literal.expr, algebra=algebra) == old["B"]
    assert algebra.locals()["B"] == old["B"]
    with pytest.raises(ValueError, match="different algebra"):
        evaluate(symbol.expr, algebra=algebra, environment={"B": ga.Algebra(2).blade(3)})


def test_policy_mapping_and_returned_values_are_read_only_snapshots():
    entries = {"plane": ga.BladeRef(3, -1), "x": ga.BladeRef(1)}
    policy = ga.LocalNamePolicy(2, entries)
    algebra = ga.Algebra(2, local_names=policy)
    old = algebra.locals()
    entries["plane"] = ga.BladeRef(3)
    assert list(old) == ["plane", "x"]
    assert old["plane"] == -algebra.blade(3)
    assert isinstance(old, MappingProxyType)
    with pytest.raises(TypeError):
        old["plane"] = algebra.blade(3)
    with pytest.raises(TypeError):
        policy.mapping["plane"] = ga.BladeRef(3)
    assert algebra.locals()["plane"] is not old["plane"]
    assert algebra.locals()["plane"] == old["plane"]


@pytest.mark.parametrize(
    "style, names", (("compact", ["v1", "v2", "v12"]), ("wedge", ["v1", "v2"]), ("juxtapose", ["v1", "v2", "v1v2"]))
)
def test_from_convention_is_literal_ascii_filtering_not_compact_key_generation(style, names):
    labels = ga.indexed_blade_convention(2, prefix="v", style=style, aliases={"plane": 3}, roles={"axis": 1})
    policy = ga.LocalNamePolicy.from_convention(labels)
    assert list(policy.mapping) == names
    assert "plane" not in policy.mapping and "axis" not in policy.mapping
    assert all(ref.mask for _, ref in policy.entries)
    algebra = ga.Algebra(2).with_blades(labels)
    assert list(algebra.locals()) == ["e1", "e2", "e12"]
    assert list(algebra.with_local_names(policy).locals()) == names


@pytest.mark.parametrize("name", ("", 123, "class", "2x", "x-y"))
def test_invalid_identifiers_are_rejected_without_sanitization(name):
    with pytest.raises(ValueError):
        ga.LocalNamePolicy(2, [(name, 1)])


def test_policy_validation_does_not_forbid_explicit_scalar_or_unicode_bindings():
    algebra = ga.Algebra(
        2, local_names=ga.LocalNamePolicy(2, {"one": 0, "σ": ga.BladeRef(3, -1), "B": ga.BladeRef(3, -1)})
    )
    assert algebra.locals()["one"] == algebra.scalar(1)
    assert algebra.locals()["σ"] == algebra.locals()["B"] == -algebra.blade(3)
    with pytest.raises(ValueError, match="duplicate"):
        ga.LocalNamePolicy(2, [("x", 1), ("x", 2)])
    with pytest.raises(ValueError, match="outside dimension"):
        ga.LocalNamePolicy(2, {"x": 4})
    with pytest.raises(ValueError, match="dimension"):
        algebra.with_local_names(ga.LocalNamePolicy(3, {"x": 1}))
