"""Public expression grouping contracts with independently captured v1 values."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
from galaga.expression import evaluate

ARCHIVE = json.loads((Path(__file__).parents[1] / "tools/baselines/expression-contracts-v1.json").read_text())
HISTORY = {row["id"]: row for row in ARCHIVE["observations"]}

# Every recipe corresponds to one original test. Expected v2 strings are literal,
# reviewed contracts, not outputs obtained by rendering the current expression.
RECIPES = {
    "reverse-sum": lambda a, b, c: ga.reverse(a + b),
    "involute-sum": lambda a, b, c: ga.grade_involution(a + b),
    "conjugate-sum": lambda a, b, c: ga.conjugate(a + b),
    "dual-sum": lambda a, b, c: ga.dual(a + b),
    "inverse-sum": lambda a, b, c: ga.inverse(a + b),
    "reverse-product": lambda a, b, c: ga.reverse(a * b),
    "inverse-product": lambda a, b, c: ga.inverse(a * b),
    "dual-product": lambda a, b, c: ga.dual(a * b),
    "squared-product": lambda a, b, c: ga.squared(a * b),
    "reverse-name": lambda a, b, c: ga.reverse(a),
    "inverse-name": lambda a, b, c: ga.inverse(a),
    "dual-name": lambda a, b, c: ga.dual(a),
    "squared-name": lambda a, b, c: ga.squared(a),
    "negate-sum": lambda a, b, c: -(a + b),
    "negate-product": lambda a, b, c: -(a * b),
    "negate-name": lambda a, b, c: -a,
    "reverse-left": lambda a, b, c: ~(a + b) * c,
    "reverse-right": lambda a, b, c: c * ~(a + b),
    "sum-sandwich": lambda a, b, c: (a + b) * c * ~(a + b),
    "double-reverse": lambda a, b, c: ~~a,
    "divide-sum": lambda a, b, c: (a + b) / 2,
    "scale-inside-wedge": lambda a, b, c: (2 * a) ^ b,
    "scale-outside-wedge": lambda a, b, c: 2 * (a ^ b),
    "unit-sum": lambda a, b, c: ga.unit(a + b),
    "exp-sum": lambda a, b, c: ga.exp(a + b),
}

# Target order: ASCII, Unicode, LaTeX. See ADR-098 for retained differences.
RENDERINGS = {
    "reverse-sum": ("~(a + b)", "(a + b)̃", "\\widetilde{a + b}"),
    "involute-sum": ("hat((a + b))", "(a + b)̂", "\\widehat{\\left(a + b\\right)}"),
    "conjugate-sum": ("bar((a + b))", "(a + b)̅", "\\overline{a + b}"),
    "dual-sum": ("(a + b)^*", "(a + b)^★", "\\left(a + b\\right)^*"),
    "inverse-sum": ("(a + b)^-1", "(a + b)⁻¹", "\\left(a + b\\right)^{-1}"),
    "reverse-product": ("~(ab)", "(ab)̃", "\\widetilde{a b}"),
    "inverse-product": ("(ab)^-1", "(ab)⁻¹", "\\left(a b\\right)^{-1}"),
    "dual-product": ("(ab)^*", "(ab)^★", "\\left(a b\\right)^*"),
    "squared-product": ("(ab)^2", "(ab)²", "\\left(a b\\right)^2"),
    "reverse-name": ("~a", "ã", "\\widetilde{a}"),
    "inverse-name": ("a^-1", "a⁻¹", "a^{-1}"),
    "dual-name": ("a^*", "a^★", "a^*"),
    "squared-name": ("a^2", "a²", "a^2"),
    "negate-sum": ("-(a + b)", "-(a + b)", "-\\left(a + b\\right)"),
    "negate-product": ("-(ab)", "-(ab)", "-\\left(a b\\right)"),
    "negate-name": ("-a", "-a", "-a"),
    "reverse-left": ("~(a + b)c", "(a + b)̃c", "\\widetilde{a + b} c"),
    "reverse-right": ("c~(a + b)", "c(a + b)̃", "c \\widetilde{a + b}"),
    "sum-sandwich": ("(a + b)c~(a + b)", "(a + b)c(a + b)̃", "\\left(a + b\\right) c \\widetilde{a + b}"),
    "double-reverse": ("~(~a)", "(ã)̃", "\\widetilde{\\widetilde{a}}"),
    "divide-sum": ("(a + b) / 2", "(a + b) / 2", "\\frac{a + b}{2}"),
    "scale-inside-wedge": ("(2a) ^ b", "(2a) ∧ b", "\\left(2 a\\right) \\wedge b"),
    "scale-outside-wedge": ("2a ^ b", "2a ∧ b", "2 a \\wedge b"),
    "unit-sum": ("hat((a + b))", "(a + b)̂", "\\widehat{\\left(a + b\\right)}"),
    "exp-sum": ("exp(a + b)", "exp(a + b)", "e^{a + b}"),
}


def _assert_coefficients(actual, expected) -> None:
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape, "coefficient shape changed"
    assert np.isfinite(actual).all() and np.isfinite(expected).all(), "nonfinite coefficient"
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)


@pytest.mark.parametrize("case_id", tuple(RECIPES))
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_grouping_preserves_historical_value_replay_and_reviewed_rendering(case_id: str, target: str) -> None:
    algebra = ga.Algebra(3)
    a, b, c = [value.named(name) for value, name in zip(algebra.basis_vectors(), "abc", strict=True)]
    # Names start provenance when an operation is applied; naming alone is not
    # lazy evaluation, nor does it need a redundant with_expr() call.
    assert all(value.expr is None for value in (a, b, c))
    result = RECIPES[case_id](a, b, c)
    expression, coefficients = result.expr, result.data.copy()
    assert expression is not None
    _assert_coefficients(result.data, HISTORY[case_id]["coefficients"])
    replayed = evaluate(expression, algebra=algebra, environment={"a": a, "b": b, "c": c})
    _assert_coefficients(replayed.data, HISTORY[case_id]["coefficients"])
    assert result.display(f"expr/{target}") == RENDERINGS[case_id][("ascii", "unicode", "latex").index(target)]
    assert result.expr is expression
    np.testing.assert_array_equal(result.data, coefficients)


def test_squaring_a_product_must_not_look_like_squaring_its_last_factor() -> None:
    algebra = ga.Algebra(3)
    a, b, _ = [value.named(name) for value, name in zip(algebra.basis_vectors(), "abc", strict=True)]
    whole_product = ga.squared(a * b)
    last_factor = a * ga.squared(b)
    # Compute the values first: these are different algebraic expressions.
    assert whole_product == -1
    assert last_factor == a
    assert whole_product.expr != last_factor.expr
    assert whole_product.display("expr/latex") == r"\left(a b\right)^2"
    assert last_factor.display("expr/latex") == r"a b^2"


def test_unit_and_involution_keep_distinct_ids_even_when_conventional_hats_match() -> None:
    algebra = ga.Algebra(3)
    a, b, _ = [value.named(name) for value, name in zip(algebra.basis_vectors(), "abc", strict=True)]
    normalized, involuted = ga.unit(a + b), ga.grade_involution(a + b)
    assert ga.squared(normalized).almost_equal(algebra.identity)
    assert ga.squared(involuted) == 2
    assert normalized.expr.operation_id == "unit"
    assert involuted.expr.operation_id == "grade_involution"
    assert normalized.display("expr/latex") == involuted.display("expr/latex") == r"\widehat{\left(a + b\right)}"
    assert normalized.display("expr/ascii", notation=ga.Notation.functional()) == "unit(add(a, b))"
    assert involuted.display("expr/ascii", notation=ga.Notation.functional()) == "grade_involution(add(a, b))"
