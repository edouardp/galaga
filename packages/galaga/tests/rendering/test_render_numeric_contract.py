"""Numeric ownership of historical rendering cases and non-vacuous compositions."""

import inspect
import json
import runpy
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
from galaga import core
from galaga.expression import Symbol, evaluate

TEST_ROOT = Path(__file__).parents[1]
ARCHIVE = json.loads((TEST_ROOT.parent / "tools/baselines/render-contracts-v1.json").read_text())
CONTRACT = runpy.run_path(str(TEST_ROOT / "test_render.py"))
GRAMS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    ((2, 0.5, 0), (0.5, 1, 0.25), (0, 0.25, -1)),
    ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),
)
TARGETS = ("ascii", "unicode", "latex")


def assert_coefficients(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape, "coefficient shape mismatch"
    assert np.isfinite(actual).all() and np.isfinite(expected).all(), "nonfinite coefficients"
    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize("row", ARCHIVE["tests"], ids=lambda row: row["id"])
def test_every_original_rendering_case_keeps_its_archived_numeric_contract(row, monkeypatch):
    class_name, method_name = row["id"].split(".")
    method = getattr(CONTRACT[class_name](), method_name)
    algebra = ga.Algebra(3)
    observation = row["observations"][0]
    environment = {name: algebra.multivector(data) for name, data in observation["bindings"].items()}
    expected = np.asarray(observation["coefficients"])
    if row["id"] in {"TestCommutators.test_lie_bracket", "TestCommutators.test_jordan_product"}:
        # The explicitly reviewed v2 operations are unscaled. Mixed-grade
        # probes below prevent the original zero Jordan sample hiding a bug.
        expected = 2 * expected
    calls = []

    def checked(renderer):
        def render(expression, notation=None):
            before = hash(expression)
            value = evaluate(expression, algebra=algebra, environment=environment)
            assert_coefficients(value.data, expected)
            text = renderer(expression, notation)
            assert hash(expression) == before
            calls.append(expression)
            return text

        return render

    globals_ = method.__func__.__globals__
    for name in ("_unicode", "_latex"):
        monkeypatch.setitem(globals_, name, checked(globals_[name]))
    fixtures = {"alg": algebra, "syms": tuple(Symbol(name) for name in ("a", "b", "c"))}
    method(**{name: fixtures[name] for name in inspect.signature(method).parameters})
    assert calls, "historical test no longer renders an expression"


# Literal three-target output, reviewed independently of the renderer.
COMPOSITIONS = {
    "lie": ("[a, b]", "[a, b]", r"[a,\, b]"),
    "jordan": ("{a, b}", "{a, b}", r"\{a,\, b\}"),
    # ADR-119 preserves division as a two-operand call, including its scope.
    "division": ("a / (b + c)", "a / (b + c)", r"\frac{a}{b + c}"),
    "negative_product": ("-(ab)", "-(ab)", r"-\left(a b\right)"),
    "reverse_product": ("~(ab)", "(ab)̃", r"\widetilde{a b}"),
    "reverse_sum_left": ("~(a + b)c", "(a + b)̃c", r"\widetilde{a + b} c"),
    "sandwich": ("ab~a", "abã", r"a b \widetilde{a}"),
    "grade_sandwich": ("<ab~a>[1]", "⟨abã⟩₁", r"\langle a b \widetilde{a} \rangle_{1}"),
    "square_sum": ("(a + b)^2", "(a + b)²", r"\left(a + b\right)^2"),
    "negative_rhs": ("a - 3b", "a - 3b", "a - 3 b"),
}


def composition_case(gram, case):
    algebra = ga.Algebra(gram=gram)
    a = algebra.scalar(2) + algebra.blade(1)
    b = algebra.scalar(0.5) + algebra.blade(2)
    c = algebra.scalar(-0.25) + algebra.blade(4)
    # Force an independent product backend and work in raw coefficient arrays
    # before naming values or constructing the facade expression.
    reference = core.Algebra(gram=gram, product_backend="reference")

    def left(data):
        return reference.left_action(reference.multivector(data))

    grades = np.array([mask.bit_count() for mask in range(algebra.dim)])
    reverse_signs = (-1.0) ** (grades * (grades - 1) // 2)
    ab, ba = left(a.data) @ b.data, left(b.data) @ a.data
    sandwich = left(ab) @ (reverse_signs * a.data)
    inverse_denominator = np.linalg.solve(left(b.data + c.data), algebra.identity.data)
    expected = {
        "lie": ab - ba,
        "jordan": ab + ba,
        "division": left(a.data) @ inverse_denominator,
        "negative_product": -ab,
        "reverse_product": reverse_signs * ab,
        "reverse_sum_left": left(reverse_signs * (a.data + b.data)) @ c.data,
        "sandwich": sandwich,
        "grade_sandwich": np.where(grades == 1, sandwich, 0),
        "square_sum": left(a.data + b.data) @ (a.data + b.data),
        "negative_rhs": a.data - 3 * b.data,
    }[case]
    assert np.any(abs(expected) > 1e-8), "vacuous numeric composition"
    environment = {"a": a, "b": b, "c": c}
    a, b, c = a.named("a"), b.named("b"), c.named("c")
    recipes = {
        "lie": lambda: ga.lie_bracket(a, b),
        "jordan": lambda: ga.jordan_product(a, b),
        "division": lambda: a / (b + c),
        "negative_product": lambda: -(a * b),
        "reverse_product": lambda: ga.reverse(a * b),
        "reverse_sum_left": lambda: ga.reverse(a + b) * c,
        "sandwich": lambda: a * b * ga.reverse(a),
        "grade_sandwich": lambda: (a * b * ga.reverse(a))[1],
        "square_sum": lambda: ga.squared(a + b),
        "negative_rhs": lambda: a + (-3) * b,
    }
    return algebra, environment, recipes[case](), expected


@pytest.mark.parametrize("gram", GRAMS, ids=("euclidean", "oblique-indefinite", "native-null"))
@pytest.mark.parametrize("case", COMPOSITIONS)
@pytest.mark.parametrize("index, target", tuple(enumerate(TARGETS)))
def test_mixed_grade_compositions_preserve_numeric_scope_and_all_targets(gram, case, index, target):
    algebra, environment, value, expected = composition_case(gram, case)
    expression, before_hash, data = value.expr, hash(value), value.data.copy()
    assert_coefficients(data, expected)
    assert value.display(f"expr/{target}") == COMPOSITIONS[case][index]
    assert_coefficients(evaluate(expression, algebra=algebra, environment=environment).data, expected)
    assert value.expr is expression and hash(value) == before_hash
    np.testing.assert_array_equal(value.data, data)


@pytest.mark.parametrize("gram", GRAMS)
def test_division_oracle_distinguishes_the_side_of_the_inverse(gram):
    algebra, environment, value, expected = composition_case(gram, "division")
    a, b, c = (environment[name] for name in ("a", "b", "c"))
    inverse = np.linalg.solve(algebra.left_action(b + c), algebra.identity.data)
    wrong_side = algebra.left_action(algebra.multivector(inverse)) @ a.data
    assert not np.allclose(expected, wrong_side)
    np.testing.assert_allclose((value * (b + c)).data, a.data, rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize("target", TARGETS)
def test_immutable_notation_views_do_not_change_sandwich_values_or_provenance(target):
    algebra, environment, value, expected = composition_case(GRAMS[1], "sandwich")
    before = value.display(f"expr/{target}")
    notation = ga.Notation.functional()
    view = algebra.with_notation(notation)
    assert view.numeric is algebra.numeric and algebra.presentation.notation != notation
    a, b = environment["a"].named("a"), environment["b"].named("b")
    # Explicit display policy and a scoped view are both presentation-only.
    custom = value.display(f"expr/{target}", notation=notation)
    assert custom != before
    with algebra.use_presentation(view.presentation):
        assert value.display(f"expr/{target}") == custom
        assert (a * b * ga.reverse(a)).display(f"expr/{target}") == custom
        assert algebra.default_presentation.notation != notation
        assert view.presentation is view.default_presentation
    assert_coefficients(value.data, expected)
    assert value.display(f"expr/{target}") == before
