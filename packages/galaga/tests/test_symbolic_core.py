"""Public owners of the shared symbolic helpers; no live symbolic_core dependency.

The eleven historical identities remain, but private values, automatic name
normalization and the mutable toy registry are explicitly retired (ADR-121).
"""

import json
from pathlib import Path

import numpy as np
import pytest

import galaga as ga

ARCHIVE = json.loads((Path(__file__).parents[1] / "tools/baselines/namespace-boundaries-v1.json").read_text())


def assert_name(name, index):
    assert name.variants == tuple(ARCHIVE["names"][index]["variants"])
    value = ga.Algebra(1).scalar(3).named(name)
    for target, spelling in zip(("ascii", "unicode", "latex"), name.variants, strict=True):
        assert value.display("name/" + target) == spelling
    assert value == 3


def test_normalize_name_matches_multivector_label_style():
    # V1 stripped plain labels implicitly. V2 makes that input choice explicit.
    raw = ARCHIVE["names"][0]["inputs"]["label"]
    assert ga.Name(raw).variants == (raw, raw, raw)
    assert_name(ga.Name(raw.strip()), 0)


def test_normalize_name_latex_derives_greek_unicode_ascii():
    assert_name(ga.Name.from_latex(r"\theta"), 1)


def test_normalize_name_latex_derives_mathbf_unicode_ascii():
    assert_name(ga.Name.from_latex(r"\mathbf{v}"), 2)


def test_normalize_name_unknown_latex_falls_back():
    with pytest.raises(ValueError, match="unsupported"):
        ga.Name.from_latex(r"\weirdthing")
    assert_name(ga.Name.from_latex(r"\weirdthing", ascii=r"\weirdthing"), 3)


def test_normalize_name_requires_label_or_latex():
    assert ARCHIVE["missing_name"]["type"] == "ValueError"
    with pytest.raises(TypeError):
        ga.Name()
    with pytest.raises(ValueError, match="non-empty"):
        ga.Name("")
    with pytest.raises(ValueError, match="non-empty"):
        ga.Name.from_latex(" ")


def test_explicit_unicode_ascii_override_derived_values():
    assert_name(ga.Name.from_latex(r"\theta", unicode="theta-u", ascii="theta-a"), 4)


def test_sym_keeps_compatibility_attributes():
    """The historical private attributes are replaced, not compatibility promises."""
    name = ga.Name(*ARCHIVE["symbol"]["name"])
    symbol = ga.Symbol(name)
    assert symbol.identifier == "alpha" and symbol.name == name
    for attribute in ("_value", "_mv", "_name", "_name_latex", "_name_ascii", "eval"):
        assert not hasattr(symbol, attribute)
    algebra = ga.Algebra(1)
    before = hash(symbol)
    first = ga.evaluate(symbol, algebra=algebra, environment={"alpha": ARCHIVE["symbol"]["value"]})
    rebound = ga.evaluate(symbol, algebra=algebra, environment={name: 5})
    assert first == 3 and rebound == 5 and hash(symbol) == before
    with pytest.raises(KeyError, match="alpha"):
        ga.evaluate(symbol, algebra=algebra)


def test_scalar_keeps_value_attribute():
    """ScalarLiteral exposes immutable .value and requires an evaluation context."""
    scalar = ga.ScalarLiteral(ARCHIVE["scalar"])
    assert scalar.value == 2 and not hasattr(scalar, "_value")
    assert ga.evaluate(scalar, algebra=ga.Algebra(1)) == 2
    with pytest.raises(AttributeError):
        scalar.value = 4
    with pytest.raises(TypeError, match="algebra"):
        ga.evaluate(scalar)


def test_structural_add_scalar_mul_and_scalar_div_eval():
    algebra = ga.Algebra(2)
    x = algebra.scalar(4).named("x")
    cases = (
        (x + 2, ga.Call("add", (ga.Symbol("x"), ga.ScalarLiteral(2))), "add", 10),
        (3 * x, ga.Call("scalar_multiply", (ga.Symbol("x"),), {"scalar": 3}), "scalar_multiply", 24),
        (x / 2, ga.Call("scalar_divide", (ga.Symbol("x"),), {"scalar": 2}), "scalar_divide", 4),
    )
    for value, expression, operation, rebound in cases:
        assert value.expr == expression
        assert value == ARCHIVE["arithmetic"][operation]
        assert ga.evaluate(expression, algebra=algebra, environment={"x": 4}) == value
        assert ga.evaluate(expression, algebra=algebra, environment={"x": 8}) == rebound
        assert value == ARCHIVE["arithmetic"][operation]
    with pytest.raises(TypeError):
        ga.Symbol("x") + 2


def test_domain_operator_maps_to_registered_node():
    """Use a declared catalog operation, not a mutable per-domain node registry."""
    operation = ga.get_operation("geometric_product")
    expression = ga.Call(operation.id, (ga.Symbol("a"), ga.Symbol("b")))
    assert expression.operation_id == operation.id and operation.expression_arity == 2
    algebra = ga.Algebra(gram=((2, 0.5), (0.5, -1)))
    assert (
        ga.evaluate(expression, algebra=algebra, environment={"a": 2, "b": 5})
        == ARCHIVE["domain"]["registered_product"]
    )
    a, b = algebra.basis_vectors()
    result = ga.evaluate(expression, algebra=algebra, environment={"a": 2 * a, "b": 5 * b})
    np.testing.assert_array_equal(result.data, [10 * algebra.gram[0, 1], 0, 0, 10])
    with pytest.raises(TypeError):
        ga.OPERATIONS["toy_mul"] = operation


def test_missing_domain_operator_raises_type_error():
    """V1's registry TypeError becomes an explicit unknown-operation ValueError."""
    assert ARCHIVE["domain"]["missing_error"]["type"] == "TypeError"
    with pytest.raises(ValueError, match="unknown expression operation"):
        ga.Call("toy_mul", (ga.Symbol("a"), ga.Symbol("b")))

    class ToyMul(ga.Expr):
        pass

    with pytest.raises(TypeError, match="unsupported expression node"):
        ga.evaluate(ToyMul(), algebra=ga.Algebra(1))
