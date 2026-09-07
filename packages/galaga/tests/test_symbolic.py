"""Named symbolic contracts owned by eager facade values and generic provenance."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
from galaga.expression import Call, Expr, Symbol, evaluate, simplify

ARCHIVE = json.loads((Path(__file__).parents[1] / "tools/baselines/symbolic-contracts-v1.json").read_text())
HISTORY = {row["id"]: row for row in ARCHIVE["values"]}


def _context():
    algebra = ga.Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    # Derive values from the algebra before attaching their semantic names.
    values = {
        "a": e1,
        "b": e2,
        "c": e1 + e2,
        "A": e1,
        "B": e2,
        "R": e1 * e2,
        "v": e1,
        "w": 2 * e1,
        "u": algebra.vector([3, 4, 0]),
    }
    named = {key: value.named(key).with_expr() for key, value in values.items()}
    named["contraction_B"] = (e1 * e2).named("B").with_expr()
    return algebra, named


RECIPES = {
    "name": lambda x: x["R"],
    "product": lambda x: x["R"] * x["v"],
    "sandwich": lambda x: x["R"] * x["v"] * ~x["R"],
    "grade-0": lambda x: ga.grade(x["R"] * x["v"] * ~x["R"], 0),
    "grade-1": lambda x: ga.grade(x["R"] * x["v"] * ~x["R"], 1),
    "grade-2": lambda x: ga.grade(x["R"] * x["v"] * ~x["R"], 2),
    "wedge": lambda x: x["a"] ^ x["b"],
    "left-contraction": lambda x: ga.left_contraction(x["a"], x["b"]),
    "right-contraction": lambda x: ga.right_contraction(x["a"], x["b"]),
    "hestenes-inner": lambda x: ga.hestenes_inner(x["A"], x["B"]),
    "scalar-product": lambda x: ga.scalar_product(x["A"], x["B"]),
    "reverse": lambda x: ga.reverse(x["R"]),
    "involution": lambda x: ga.grade_involution(x["v"]),
    "conjugate": lambda x: ga.conjugate(x["v"]),
    "dual": lambda x: ga.dual(x["v"]),
    "undual": lambda x: ga.undual(x["v"]),
    "norm": lambda x: ga.norm(x["v"]),
    "unit": lambda x: ga.unit(x["v"]),
    "inverse": lambda x: ga.inverse(x["v"]),
    "dag": lambda x: x["R"].dag,
    "sq": lambda x: x["R"].sq,
    "add": lambda x: x["a"] + x["b"],
    "subtract": lambda x: x["a"] - x["b"],
    "negate": lambda x: -x["a"],
    "scale": lambda x: 2 * x["a"],
    "minus-unit-scale": lambda x: -1 * x["a"],
    "grouped-product": lambda x: (x["a"] + x["b"]) * x["c"],
    "grade-product": lambda x: ga.grade(x["A"] * x["B"], 2),
    "vector-bivector-contraction": lambda x: ga.left_contraction(x["a"], x["contraction_B"]),
    "inverse-identity": lambda x: x["w"] * x["w"].inv,
    "triple-scale": lambda x: 3 * x["a"],
    "norm-345": lambda x: ga.norm(x["u"]),
    "commutator": lambda x: ga.commutator(x["a"], x["b"]),
    "anticommutator": lambda x: ga.anticommutator(x["a"], x["b"]),
    "lie-bracket": lambda x: ga.lie_bracket(x["a"], x["b"]),
    "jordan-product": lambda x: ga.jordan_product(x["a"], x["b"]),
}

# Independently reviewed literal v2 outputs; never populated by a live renderer.
# Each row contains (root operation ID, ASCII, Unicode, LaTeX).
REVIEWED = {
    "name": ("Symbol", "R", "R", "R"),
    "product": ("geometric_product", "Rv", "Rv", "R v"),
    "sandwich": ("geometric_product", "Rv~R", "RvR̃", "R v \\widetilde{R}"),
    "grade-0": ("grade", "<Rv~R>[0]", "⟨RvR̃⟩₀", "\\langle R v \\widetilde{R} \\rangle_{0}"),
    "grade-1": ("grade", "<Rv~R>[1]", "⟨RvR̃⟩₁", "\\langle R v \\widetilde{R} \\rangle_{1}"),
    "grade-2": ("grade", "<Rv~R>[2]", "⟨RvR̃⟩₂", "\\langle R v \\widetilde{R} \\rangle_{2}"),
    "wedge": ("outer_product", "a ^ b", "a ∧ b", "a \\wedge b"),
    "left-contraction": ("left_contraction", "a _| b", "a ⌋ b", "a \\mathbin{\\rfloor} b"),
    "right-contraction": ("right_contraction", "a |_ b", "a ⌊ b", "a \\mathbin{\\lfloor} b"),
    "hestenes-inner": ("hestenes_inner", "hestenes_inner(A, B)", "hestenes_inner(A, B)", "A \\cdot B"),
    "scalar-product": ("scalar_product", "A * B", "A * B", "A * B"),
    "reverse": ("reverse", "~R", "R̃", "\\widetilde{R}"),
    "involution": ("grade_involution", "hat(v)", "v̂", "\\widehat{v}"),
    "conjugate": ("conjugate", "bar(v)", "v̅", "\\overline{v}"),
    "dual": ("dual", "v^*", "v^★", "v^*"),
    "undual": ("undual", "v^*^-1", "v^(★⁻¹)", "v^{*^{-1}}"),
    "norm": ("norm", "||v||", "‖v‖", "\\lVert v \\rVert"),
    "unit": ("unit", "hat(v)", "v̂", "\\widehat{v}"),
    "inverse": ("inverse", "v^-1", "v⁻¹", "v^{-1}"),
    "dag": ("reverse", "~R", "R̃", "\\widetilde{R}"),
    "sq": ("squared", "R^2", "R²", "R^2"),
    "add": ("add", "a + b", "a + b", "a + b"),
    "subtract": ("subtract", "a - b", "a - b", "a - b"),
    "negate": ("negate", "-a", "-a", "-a"),
    "scale": ("scalar_multiply", "2a", "2a", "2 a"),
    "minus-unit-scale": ("scalar_multiply", "-a", "-a", "-a"),
    "grouped-product": ("geometric_product", "(a + b)c", "(a + b)c", "\\left(a + b\\right) c"),
    "grade-product": ("grade", "<AB>[2]", "⟨AB⟩₂", "\\langle A B \\rangle_{2}"),
    "vector-bivector-contraction": ("left_contraction", "a _| B", "a ⌋ B", "a \\mathbin{\\rfloor} B"),
    "inverse-identity": ("geometric_product", "ww^-1", "ww⁻¹", "w w^{-1}"),
    "triple-scale": ("scalar_multiply", "3a", "3a", "3 a"),
    "norm-345": ("norm", "||u||", "‖u‖", "\\lVert u \\rVert"),
    "commutator": ("commutator", "[a, b]", "[a, b]", "[a,\\, b]"),
    "anticommutator": ("anticommutator", "{a, b}", "{a, b}", "\\{a,\\, b\\}"),
    "lie-bracket": ("lie_bracket", "[a, b]", "[a, b]", "[a,\\, b]"),
    "jordan-product": ("jordan_product", "{a, b}", "{a, b}", "\\{a,\\, b\\}"),
}

BRACKETS = {
    "commutator": (-1, 1),
    "anticommutator": (1, 1),
    "lie_bracket": (-1, 1),
    "jordan_product": (1, 1),
    "half_commutator": (-1, 0.5),
    "half_anticommutator": (1, 0.5),
}


def _assert_coefficients(actual, expected) -> None:
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape, "coefficient shape changed"
    assert np.isfinite(actual).all() and np.isfinite(expected).all(), "nonfinite coefficient"
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)


@pytest.mark.parametrize("case_id", tuple(RECIPES))
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_named_recipes_preserve_values_replay_and_reviewed_renderings(case_id: str, target: str) -> None:
    algebra, values = _context()
    result = RECIPES[case_id](values)
    expression, coefficients, value_hash = result.expr, result.data.copy(), hash(result)
    assert isinstance(result, ga.Multivector) and not isinstance(result, Expr)
    # V2's explicit unscaled Lie/Jordan definitions are not v1 numeric parity.
    factor = 2 if case_id in {"lie-bracket", "jordan-product"} else 1
    expected = factor * np.asarray(HISTORY[case_id]["coefficients"])
    _assert_coefficients(result.data, expected)
    if case_id == "name":
        assert expression == Symbol("R")
    else:
        assert isinstance(expression, Call) and expression.operation_id == REVIEWED[case_id][0]
    environment = dict(values)
    if case_id == "vector-bivector-contraction":
        environment["B"] = values["contraction_B"]
    _assert_coefficients(evaluate(expression, algebra=algebra, environment=environment).data, expected)
    assert result.display(f"expr/{target}") == REVIEWED[case_id][1 + ("ascii", "unicode", "latex").index(target)]
    assert result.expr is expression and hash(result) == value_hash
    np.testing.assert_array_equal(result.data, coefficients)


def test_sandwich_provenance_keeps_order_and_symbols() -> None:
    algebra, values = _context()
    result = values["R"] * values["v"] * values["R"].dag
    expected = Call(
        "geometric_product",
        (Call("geometric_product", (Symbol("R"), Symbol("v"))), Call("reverse", (Symbol("R"),))),
    )
    assert result.expr == expected
    assert result == -values["v"]
    # The same saved tree can use a new rotor; no hidden v1-style binding.
    assert evaluate(expected, algebra=algebra, environment={"R": 1, "v": values["v"]}) == values["v"]
    assert result == -values["v"]


@pytest.mark.parametrize(
    "operation", ("geometric_product", "grade", "reverse", "commutator", "lie_bracket", "jordan_product")
)
def test_anonymous_numeric_calls_do_not_create_expressions(operation: str) -> None:
    algebra = ga.Algebra(3)
    a, b, _ = algebra.basis_vectors()
    arguments = (a, 1) if operation == "grade" else (a,) if operation == "reverse" else (a, b)
    result = getattr(ga, operation)(*arguments)
    assert isinstance(result, ga.Multivector) and not isinstance(result, Expr)
    assert result.expr is None and result.name is None


@pytest.mark.parametrize("row", ARCHIVE["brackets"], ids=lambda row: f"{row['operation']}-tracked={row['tracked']}")
def test_nonzero_bracket_archive_distinguishes_unscaled_and_half_scaled_conventions(row) -> None:
    algebra = ga.Algebra(3)
    # The recorded explicit inputs, not recorded results, initialize the probe.
    left, right = algebra.multivector(row["left"]), algebra.multivector(row["right"])
    if row["tracked"]:
        left, right = left.named("a").with_expr(), right.named("b").with_expr()
    operation = row["operation"]
    result = getattr(ga, operation)(left, right)
    scale = 2 if operation in {"lie_bracket", "jordan_product"} else 1
    assert np.any(row["coefficients"]), "a zero sample cannot detect half-scaling"
    _assert_coefficients(result.data, scale * np.asarray(row["coefficients"]))
    sign, _ = BRACKETS[operation]
    ab = algebra.numeric.left_action(left.numeric) @ right.data
    ba = algebra.numeric.left_action(right.numeric) @ left.data
    _assert_coefficients(result.data, ab + sign * ba)
    half_operation = "half_commutator" if sign == -1 else "half_anticommutator"
    _assert_coefficients(getattr(ga, half_operation)(left, right).data, 0.5 * (ab + sign * ba))
    if row["tracked"]:
        assert result.expr == Call(operation, (Symbol("a"), Symbol("b")))
        _assert_coefficients(
            evaluate(result.expr, algebra=algebra, environment={"a": left, "b": right}).data, result.data
        )
    else:
        assert result.expr is None


@pytest.mark.parametrize("operation", tuple(BRACKETS))
@pytest.mark.parametrize(
    "gram",
    (((1, 0), (0, 1)), ((1, 0), (0, 0)), ((2, 0.5), (0.5, -1)), ((0, -1), (-1, 0))),
    ids=("euclidean", "degenerate", "oblique", "native-null"),
)
@pytest.mark.parametrize("named, tracked", ((False, False), (True, False), (False, True), (True, True)))
def test_bracket_scaling_is_independent_of_metric_and_provenance(operation, gram, named, tracked) -> None:
    algebra = ga.Algebra(gram=gram)
    left = algebra.multivector([1, 1, 0.5, 0.2], name="a" if named else None, expr=tracked)
    right = algebra.multivector([-0.25, 0.75, 1, -0.1], name="b" if named else None, expr=tracked)
    ab = algebra.numeric.left_action(left.numeric) @ right.data
    ba = algebra.numeric.left_action(right.numeric) @ left.data
    sign, scale = BRACKETS[operation]
    expected = scale * (ab + sign * ba)
    assert np.any(expected), "the scale check needs a nonzero result"
    result = getattr(ga, operation)(left, right)
    _assert_coefficients(result.data, expected)
    if named or tracked:
        assert result.expr.operation_id == operation
        _assert_coefficients(evaluate(result.expr, algebra=algebra, environment={"a": left, "b": right}).data, expected)
    else:
        assert result.expr is None


@pytest.mark.parametrize("operation", ("jordan_product", "half_anticommutator"))
@pytest.mark.parametrize("kind", ("vectors", "bivectors", "mixed"))
def test_simplification_does_not_assume_symbol_grades_or_replace_jordan_with_inner(operation: str, kind: str) -> None:
    algebra = ga.Algebra(4)
    e1, e2, e3, e4 = algebra.basis_vectors()
    bindings = {
        "vectors": (e1, e1 + e2),
        "bivectors": (e1 ^ e2, (e1 ^ e2) + (e3 ^ e4)),
        "mixed": (1 + e1 + (e1 ^ e2), 2 + e2 + (e3 ^ e4)),
    }
    left, right = bindings[kind]
    expression = Call(operation, (Symbol("a"), Symbol("b")))
    simplified = simplify(expression)
    assert simplified == expression
    assert simplify(simplified) == simplified
    ab = algebra.numeric.left_action(left.numeric) @ right.data
    ba = algebra.numeric.left_action(right.numeric) @ left.data
    expected = BRACKETS[operation][1] * (ab + ba)
    _assert_coefficients(evaluate(simplified, algebra=algebra, environment={"a": left, "b": right}).data, expected)
    if kind == "vectors":
        pairing = left.vector_part @ algebra.gram @ right.vector_part
        assert float(ga.half_anticommutator(left, right)) == pairing
        assert float(ga.jordan_product(left, right)) == 2 * pairing
    else:
        # Mixed grades (including grade 4 here) refute a universal inner-product rewrite.
        assert not ga.half_anticommutator(left, right).almost_equal(ga.hestenes_inner(left, right))


@pytest.mark.parametrize(
    "operation, ascii_text, unicode_text, latex",
    (
        ("half_commutator", "1/2[a, b]", "½[a, b]", r"\tfrac{1}{2}[a,\, b]"),
        ("half_anticommutator", "1/2{a, b}", "½{a, b}", r"\tfrac{1}{2}\{a,\, b\}"),
    ),
)
def test_half_product_notation_keeps_its_explicit_scale(operation, ascii_text, unicode_text, latex) -> None:
    algebra, values = _context()
    result = getattr(ga, operation)(values["a"], values["a"] + values["b"])
    assert result.expr.operation_id == operation
    # Use simple named operands for the exact notation contract.
    expression = Call(operation, (Symbol("a"), Symbol("b")))
    assert ga.render(expression, target="ascii", presentation=algebra.presentation) == ascii_text
    assert ga.render(expression, target="unicode", presentation=algebra.presentation) == unicode_text
    assert ga.render(expression, target="latex", presentation=algebra.presentation) == latex
