"""Definition-shaped unit notation preserves eager values and provenance."""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

import galaga as ga
from galaga.expression import Call, Symbol, evaluate
from galaga.rendering import Fraction, Identifier, Wrapper, _build, expression_tree


def _notation(target=None):
    return ga.Notation.default().with_rule("unit", ga.RenderRule("unit_fraction"), target=target)


@pytest.mark.parametrize(
    "operand, expected",
    (
        (Symbol("B"), ("B / ||B||", "B / ‖B‖", r"\frac{B}{\lVert B \rVert}")),
        (
            Call("add", (Symbol("a"), Symbol("b"))),
            ("(a + b) / ||a + b||", "(a + b) / ‖a + b‖", r"\frac{a + b}{\lVert a + b \rVert}"),
        ),
        (
            Call("geometric_product", (Symbol("a"), Symbol("b"))),
            ("ab / ||ab||", "ab / ‖ab‖", r"\frac{a b}{\lVert a b \rVert}"),
        ),
    ),
)
@pytest.mark.parametrize("index, target", tuple(enumerate(("ascii", "unicode", "latex"))))
def test_unit_fraction_renders_atoms_sums_and_products(operand, expected, index, target):
    presentation = ga.Algebra(2).presentation.with_notation(_notation())
    assert ga.render(Call("unit", (operand,)), target=target, presentation=presentation) == expected[index]


def test_unit_fraction_builds_existing_semantic_nodes_without_evaluating(monkeypatch):
    def reject(*args, **kwargs):
        raise AssertionError("rendering evaluated numeric algebra")

    monkeypatch.setattr(ga, "unit", reject)
    monkeypatch.setattr(ga, "norm", reject)
    monkeypatch.setattr(ga, "evaluate", reject)
    # Prove the sentinels are active before asking the renderer to avoid them.
    for operation in (ga.unit, ga.norm, ga.evaluate):
        with pytest.raises(AssertionError, match="rendering evaluated"):
            operation(None)
    presentation = ga.Algebra(1).presentation.with_notation(_notation())
    operand = Identifier("x")
    expected = Fraction(
        operand,
        Wrapper(operand, ga.Name("||", "‖", r"\lVert "), ga.Name("||", "‖", r" \rVert"), scalable=False),
    )
    assert expression_tree(Call("unit", (Symbol("x"),)), presentation) == expected


@pytest.mark.parametrize(
    "gram, coefficients",
    (
        (((1, 0), (0, 1)), [0, 1, 2, 0]),
        (((1, 0), (0, 1)), [1, 1, 0, 1]),
        (((1, 0), (0, 0)), [1, 1, 0, 1]),
        (((2, 0.5), (0.5, -1)), [0, 0, 0, 1]),
        (((0, -1), (-1, 0)), [0, 1, 2, 0]),
        (((0, -1), (-1, 0)), [0, 0, 0, 1]),
    ),
    ids=("euclidean-vector", "euclidean-mixed", "degenerate-mixed", "oblique-bivector", "null-vector", "null-bivector"),
)
@pytest.mark.parametrize("tracked", (False, True))
@pytest.mark.parametrize("atol", (1e-15, 1e-10))
def test_unit_fraction_agrees_with_metric_norm_without_rewriting_provenance(gram, coefficients, tracked, atol):
    algebra = ga.Algebra(gram=gram)
    original = algebra.multivector(coefficients)
    # Ground truth comes from the actual left action and independently derived
    # reverse signs, not from the unit/norm aliases agreeing with each other.
    grades = np.array([mask.bit_count() for mask in range(algebra.dim)])
    reversed_data = original.data * (-1.0) ** (grades * (grades - 1) // 2)
    squared_norm = (algebra.numeric.left_action(original.numeric) @ reversed_data)[0]
    magnitude = np.sqrt(abs(squared_norm))
    assert magnitude > atol
    expected = original.data / magnitude
    value = original.named("X")
    if tracked:
        value = value.with_expr()
    result = ga.unit(value, atol=atol)
    expression, data, before_hash = result.expr, result.data.copy(), hash(result)
    assert expression == Call("unit", (Symbol("X"),), {} if atol == 1e-15 else {"atol": atol})
    np.testing.assert_allclose(data, expected, rtol=0, atol=1e-12)
    np.testing.assert_allclose(evaluate(expression, algebra=algebra, environment={"X": original}).data, expected)
    np.testing.assert_allclose((original / ga.norm(original)).data, expected)
    # Non-default numeric controls remain visible via the established
    # functional fallback; a compact fraction must not hide the tolerance.
    expected_latex = r"\frac{X}{\lVert X \rVert}" if atol == 1e-15 else r"\operatorname{unit}\left(X, 10^{-10}\right)"
    assert result.display("expr/latex", notation=_notation()) == expected_latex
    assert result.expr is expression and hash(result) == before_hash
    np.testing.assert_array_equal(result.data, data)
    assert value.numeric is original.numeric and not result.data.flags.writeable


def test_unit_fraction_makes_named_teaching_equalities_distinct():
    algebra = ga.Algebra(2)
    bivector = algebra.blade(3).named("B")
    normalized = ga.unit(bivector).named(ga.Name.from_latex(r"\hat{B}"))
    assert normalized.display("full/latex", notation=_notation()) == (
        r"\hat{B} \quad = \quad \frac{B}{\lVert B \rVert} \quad = \quad e_{12}"
    )
    assert normalized.expr == Call("unit", (Symbol("B"),))
    assert normalized.numeric == bivector.numeric


@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_unit_fraction_is_target_local_and_does_not_change_default_hats(target):
    algebra = ga.Algebra(2)
    value = ga.unit(algebra.blade(1).named("x"))
    base = ga.Notation.default()
    before = {name: value.display(f"expr/{name}", notation=base) for name in ("ascii", "unicode", "latex")}
    custom = _notation(target)
    assert value.display(f"expr/{target}", notation=custom) != before[target]
    for other in set(before) - {target}:
        assert value.display(f"expr/{other}", notation=custom) == before[other]
    assert base == ga.Notation.default()
    with pytest.raises(FrozenInstanceError):
        custom.id = "changed"


def test_unit_fraction_uses_fixed_norm_delimiters_not_a_recursive_notation_rewrite():
    custom = _notation().with_rule("norm", ga.RenderRule("function", symbol="length"))
    presentation = ga.Algebra(1).presentation.with_notation(custom)
    assert ga.render(Call("unit", (Symbol("x"),)), target="ascii", presentation=presentation) == "x / ||x||"
    assert ga.render(Call("norm", (Symbol("x"),)), target="ascii", presentation=presentation) == r"length(x)"


@pytest.mark.parametrize("operation", ("reverse", "grade_involution", "norm", "geometric_product", "custom"))
def test_definition_shaped_unit_rule_cannot_mislabel_another_operation(operation):
    with pytest.raises(ValueError, match="unit_fraction.*unit"):
        ga.Notation.default().with_rule(operation, ga.RenderRule("unit_fraction"))


@pytest.mark.parametrize(
    "arguments, parameters, parameter",
    (
        ((), (), None),
        ((Identifier("x"), Identifier("y")), (), None),
        ((Identifier("x"),), (("k", Identifier("k")),), "k"),
    ),
)
def test_unit_fraction_keeps_functional_fallback_for_incompatible_layout_arguments(arguments, parameters, parameter):
    rule = ga.RenderRule("unit_fraction", parameter=parameter)
    tree = _build._operation_tree("unit", arguments, parameters, rule)
    assert tree.function == ga.Name("unit")
    assert tree.arguments == (*arguments, *(value for _, value in parameters))


@pytest.mark.parametrize("kind", ("zero", "null-vector", "null-bivector", "near-zero"))
def test_notation_does_not_turn_singular_normalization_into_a_formal_fraction(kind):
    algebra = ga.Algebra(gram=((1, 0), (0, 0)), notation=_notation())
    value = {
        "zero": algebra.scalar(0),
        "null-vector": algebra.blade(2),
        "null-bivector": algebra.blade(3),
        "near-zero": 1e-16 * algebra.blade(1),
    }[kind].named("x")
    with pytest.raises(ValueError, match="near-zero"):
        ga.unit(value)
