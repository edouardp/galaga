"""Eager operation/provenance contracts extracted from the mixed v1 suite."""

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
import galaga.core as core

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/eager-operation-edges-v1.json").read_text())
GRAMS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    ((2, 0.5, -0.25), (0.5, -1, 0.75), (-0.25, 0.75, 3)),
    ((1, 1, 0), (1, 1, 0), (0, 0, 0)),
)
LEFT = np.array([2, 1, -2, 0.5, 1, 0.25, -0.5, 0.125])
RIGHT = np.array([-0.5, 2, 0.5, -1, -1, 0.75, 0.5, -0.25])
BINARY = {
    "add",
    "subtract",
    "geometric_product",
    "outer_product",
    "right_contraction",
    "hestenes_inner",
    "scalar_product",
}
RECIPES = (
    "radd",
    "rsub",
    "rmul",
    "divide",
    "negate",
    "add",
    "subtract",
    "geometric_product",
    "outer_product",
    "right_contraction",
    "hestenes_inner",
    "scalar_product",
    "grade_involution",
    "conjugate",
    "reverse",
    "dual",
    "undual",
    "unit",
    "inverse",
    "even_grades",
    "odd_grades",
    "squared",
    "norm",
)
SPELLINGS = {
    "radd": ("3 + a", "3 + a", "3 + a"),
    "rsub": ("3 - a", "3 - a", "3 - a"),
    "rmul": ("3a", "3a", "3 a"),
    "divide": ("a / 2", "a / 2", r"\frac{a}{2}"),
    "negate": ("-a", "-a", "-a"),
    "add": ("a + b", "a + b", "a + b"),
    "subtract": ("a - b", "a - b", "a - b"),
    "geometric_product": ("ab", "ab", "a b"),
    "outer_product": ("a ^ b", "a ∧ b", r"a \wedge b"),
    "right_contraction": ("a |_ b", "a ⌊ b", r"a \mathbin{\lfloor} b"),
    "hestenes_inner": ("hestenes_inner(a, b)", "hestenes_inner(a, b)", r"a \cdot b"),
    "scalar_product": ("a * b", "a * b", "a * b"),
    "grade_involution": ("hat(a)", "â", r"\widehat{a}"),
    "conjugate": ("bar(a)", "a̅", r"\overline{a}"),
    "reverse": ("~a", "ã", r"\widetilde{a}"),
    "dual": ("a^*", "a^★", "a^*"),
    "undual": ("a^*^-1", "a^(★⁻¹)", "a^{*^{-1}}"),
    "unit": ("hat(a)", "â", r"\widehat{a}"),
    "inverse": ("a^-1", "a⁻¹", "a^{-1}"),
    "even_grades": ("<a>even", "⟨a⟩₊", r"\langle a \rangle_{\text{even}}"),
    "odd_grades": ("<a>odd", "⟨a⟩₋", r"\langle a \rangle_{\text{odd}}"),
    "squared": ("a^2", "a²", "a^2"),
    "norm": ("||a||", "‖a‖", r"\lVert a \rVert"),
}


def invoke(recipe, a, b):
    if recipe == "radd":
        return 3 + a
    if recipe == "rsub":
        return 3 - a
    if recipe == "rmul":
        return 3 * a
    if recipe == "divide":
        return a / 2
    if recipe == "negate":
        return -a
    if recipe == "add":
        return a + b
    if recipe == "subtract":
        return a - b
    return getattr(ga, recipe)(a, b) if recipe in BINARY else getattr(ga, recipe)(a)


@lru_cache
def oracle_metadata(gram):
    reference = core.Algebra(gram=gram, product_backend="reference")
    indices = [tuple(k for k in range(reference.n) if mask & (1 << k)) for mask in range(reference.dim)]
    grades = np.array([len(index) for index in indices])
    product = np.stack([reference.left_action(reference.blade(mask)) for mask in range(reference.dim)], axis=1)
    exterior = np.zeros_like(product)
    metric = np.zeros((reference.dim, reference.dim))
    for i, rows in enumerate(indices):
        for j, cols in enumerate(indices):
            if not i & j:
                swaps = sum(row > col for row in rows for col in cols)
                exterior[i | j, i, j] = (-1) ** swaps
            if len(rows) == len(cols):
                metric[i, j] = np.linalg.det(np.array(gram)[np.ix_(rows, cols)])
    return product, exterior, metric, grades


def expected_coefficients(recipe, gram, a, b):
    product, exterior, metric, grades = oracle_metadata(gram)
    scalar = np.zeros(len(a))
    scalar[0] = 3
    if recipe == "radd":
        return scalar + a
    if recipe == "rsub":
        return scalar - a
    if recipe == "rmul":
        return 3 * a
    if recipe == "divide":
        return a / 2
    if recipe == "negate":
        return -a
    if recipe == "add":
        return a + b
    if recipe == "subtract":
        return a - b
    if recipe == "grade_involution":
        return (-1.0) ** grades * a
    if recipe == "reverse":
        return (-1.0) ** (grades * (grades - 1) // 2) * a
    if recipe == "conjugate":
        return (-1.0) ** (grades * (grades + 1) // 2) * a
    if recipe == "even_grades":
        return np.where(grades % 2 == 0, a, 0)
    if recipe == "odd_grades":
        return np.where(grades % 2 == 1, a, 0)
    if recipe == "scalar_product":
        scalar[0] = (a * (-1.0) ** (grades * (grades - 1) // 2)) @ metric @ b
        return scalar
    if recipe in {"norm", "unit"}:
        magnitude = np.sqrt(abs(float(a @ metric @ a)))
        if recipe == "unit":
            return a / magnitude
        scalar[0] = magnitude
        return scalar
    if recipe == "inverse":
        identity = np.zeros(len(a))
        identity[0] = 1
        return np.linalg.solve(np.einsum("i,kij->kj", a, product), identity)
    if recipe in {"dual", "undual"}:
        determinant = np.linalg.det(gram)
        if determinant == 0:
            raise ValueError("metric duality needs an invertible pseudoscalar")
        volume = np.zeros(len(a))
        volume[-1] = 1
        if recipe == "dual":
            n = len(gram)
            volume /= (-1) ** (n * (n - 1) // 2) * determinant
        return np.einsum("i,kij,j->k", a, product, volume)
    if recipe == "squared":
        return np.einsum("i,kij,j->k", a, product, a)
    if recipe == "geometric_product":
        return np.einsum("i,kij,j->k", a, product, b)
    if recipe == "outer_product":
        return np.einsum("i,kij,j->k", a, exterior, b)
    if recipe == "right_contraction":
        selected = grades[:, None, None] == (grades[:, None] - grades[None, :])[None, :, :]
    else:
        assert recipe == "hestenes_inner"
        selected = grades[:, None, None] == abs(grades[:, None] - grades[None, :])[None, :, :]
        selected &= (grades[:, None] > 0) & (grades[None, :] > 0)
    return np.einsum("i,kij,j->k", a, product * selected, b)


def expression_for(recipe, a, b):
    inputs = (a, b) if recipe in BINARY else (a,)
    if all(value.name is None and value.expr is None for value in inputs):
        return None
    leaves = tuple(
        ga.Symbol(value.name)
        if value.name is not None
        else value.expr
        if value.expr is not None
        else ga.MultivectorLiteral(value.data)
        for value in inputs
    )
    if recipe in {"radd", "rsub"}:
        return ga.Call("add" if recipe == "radd" else "subtract", (ga.ScalarLiteral(3), leaves[0]))
    if recipe in {"rmul", "divide"}:
        return ga.Call(
            "scalar_multiply" if recipe == "rmul" else "scalar_divide", leaves, {"scalar": 3 if recipe == "rmul" else 2}
        )
    return ga.Call(recipe, leaves)


def assert_coefficients(value, expected):
    expected = np.asarray(expected)
    assert expected.ndim == 1 and np.isfinite(expected).all()
    if isinstance(value, ga.Multivector):
        assert value.data.shape == expected.shape
        actual = value.data
    else:
        assert type(value) is float
        actual = np.zeros(len(expected))
        actual[0] = value
    np.testing.assert_allclose(actual, expected, rtol=0, atol=2e-12)


def check_recipe(recipe, a=None, b=None):
    if a is None:
        algebra = ga.Algebra(3)
        a, b = algebra.multivector(LEFT).named("a"), algebra.multivector(RIGHT).named("b")
    algebra = a.algebra
    gram = tuple(map(tuple, algebra.gram))
    value = invoke(recipe, a, b)
    expected = expected_coefficients(recipe, gram, a.data, b.data)
    assert_coefficients(value, expected)
    expression = expression_for(recipe, a, b)
    if expression is None:
        assert type(value) is (float if recipe == "norm" else ga.Multivector)
        if isinstance(value, ga.Multivector):
            assert value.expr is None
    else:
        assert type(value) is ga.Multivector
        assert value.expr == expression
        replay = ga.evaluate(expression, algebra=algebra, environment={"a": a, "b": b})
        assert_coefficients(replay, expected)
    return value


class TestSymbolicOperators:
    def test_radd_scalar(self):
        assert check_recipe("radd").display("expr/unicode") == "3 + a"

    def test_rsub_scalar(self):
        assert check_recipe("rsub").display("expr/unicode") == "3 - a"

    def test_rmul_scalar(self):
        assert check_recipe("rmul").display("expr/unicode") == "3a"

    def test_truediv(self):
        assert check_recipe("divide").display("expr/latex") == r"\frac{a}{2}"

    def test_truediv_notimplemented(self):
        assert ga.Algebra(2).blade(1).__truediv__("bad") is NotImplemented

    def test_neg_eval(self):
        check_recipe("negate")

    def test_scalar_mul_eval(self):
        check_recipe("rmul")


class TestSymbolicBinaryEval:
    def test_rc_eval(self):
        check_recipe("right_contraction")

    def test_hi_eval(self):
        check_recipe("hestenes_inner")

    def test_sp_eval(self):
        check_recipe("scalar_product")

    def test_op_eval(self):
        check_recipe("outer_product")

    def test_sub_eval(self):
        check_recipe("subtract")

    def test_add_eval(self):
        check_recipe("add")


class TestSymbolicUnaryEval:
    def test_involute_eval(self):
        check_recipe("grade_involution")

    def test_conjugate_eval(self):
        check_recipe("conjugate")

    def test_undual_eval(self):
        check_recipe("undual")

    def test_unit_eval(self):
        check_recipe("unit")

    def test_inverse_eval(self):
        check_recipe("inverse")


class TestSymbolicNormalize:
    def test_normalize_alias(self):
        a = ga.Algebra(3).multivector(LEFT).named("a")
        for name in ("normalize", "normalise"):
            assert not hasattr(ga, name)
        value = ga.unit(a)
        assert value.expr == ga.Call("unit", (ga.Symbol("a"),))
        assert value.same_expression(ga.unit(a))

    def test_normalize_numeric_fallback(self):
        a = ga.Algebra(3).vector([3, 4, 0])
        value = ga.unit(a)
        assert_coefficients(value, [0, 0.6, 0.8, 0, 0, 0, 0, 0])
        assert value.expr is None


class TestSymbolicConvenienceProps:
    def test_inv_property(self):
        a = ga.Algebra(3).multivector(LEFT).named("a")
        assert a.inv == check_recipe("inverse", a, a) and a.inv.expr.operation_id == "inverse"

    def test_dag_property(self):
        a = ga.Algebra(3).multivector(LEFT).named("a")
        assert a.dag == check_recipe("reverse", a, a) and a.dag.expr.operation_id == "reverse"

    def test_sq_property(self):
        a = ga.Algebra(3).multivector(LEFT).named("a")
        assert a.sq == check_recipe("squared", a, a) and a.sq.expr.operation_id == "squared"


class TestSymbolicMixedInputs:
    def test_gp_mv_and_expr(self):
        algebra = ga.Algebra(3)
        check_recipe("geometric_product", algebra.multivector(LEFT), algebra.multivector(RIGHT).named("b"))

    def test_op_mv_and_expr(self):
        algebra = ga.Algebra(3)
        check_recipe("outer_product", algebra.multivector(LEFT).named("a"), algebra.multivector(RIGHT))


class TestScalarExpr:
    def test_scalar_str(self):
        leaf = ga.ScalarLiteral(3)
        assert ga.render(leaf, presentation=ga.Algebra(1).presentation) == "3"
        assert str(leaf) == repr(leaf) == "ScalarLiteral(value=3.0)"

    def test_scalar_eval_raises(self):
        leaf = ga.ScalarLiteral(3)
        with pytest.raises(TypeError, match="algebra"):
            ga.evaluate(leaf)
        with pytest.raises(AttributeError):
            leaf.eval()
        assert ga.evaluate(leaf, algebra=ga.Algebra(1)) == 3


class TestUnitLongName:
    def test_unit_long_name(self):
        a = ga.Algebra(3).vector([3, 4, 0]).named("velocity")
        value = ga.unit(a)
        assert_coefficients(value, [0, 0.6, 0.8, 0, 0, 0, 0, 0])
        assert value.expr == ga.Call("unit", (ga.Symbol("velocity"),))
        assert value.display("expr/unicode") == "velocitŷ"
        assert value.display("expr/latex") == r"\widehat{velocity}"


class TestRemainingSymbolicGaps:
    def test_sym_repr(self):
        algebra = ga.Algebra(1)
        a = algebra.blade(1).named("alpha", unicode="α", latex=r"\alpha")
        assert a.display("name/ascii") == "alpha" and a.display("name/unicode") == "α"
        assert repr(a) == a.ascii() and str(a) == a.unicode()

    def test_expr_repr_delegates_to_str(self):
        # In v2 the expression repr is structural, while the value repr is ASCII.
        for recipe in ("geometric_product", "outer_product", "reverse", "add", "subtract", "rmul", "negate"):
            value = check_recipe(recipe)
            assert repr(value) == value.ascii()
            assert repr(value.expr).startswith("Call(operation_id=")
            assert repr(value.expr) != value.display("expr/ascii")

    def test_expr_or_operator(self):
        algebra = ga.Algebra(3)
        a, B = algebra.blade(1).named("a"), algebra.blade(3).named("B")
        value = a | B
        assert value == algebra.blade(2)
        assert value.expr == ga.Call("doran_lasenby_inner", (ga.Symbol("a"), ga.Symbol("B")))

    def test_expr_mul_with_expr(self):
        check_recipe("geometric_product")

    def test_symbolic_numeric_fallbacks(self):
        algebra = ga.Algebra(3)
        for recipe in RECIPES:
            check_recipe(recipe, algebra.multivector(LEFT), algebra.multivector(RIGHT))


class TestSymbolicEvenOddSquared:
    def test_squared_str(self):
        assert check_recipe("squared").display("expr/unicode") == "a²"

    def test_squared_eval(self):
        check_recipe("squared")

    def test_squared_numeric_fallback(self):
        algebra = ga.Algebra(3)
        check_recipe("squared", algebra.multivector(LEFT), algebra.identity)

    def test_even_str(self):
        assert check_recipe("even_grades").display("expr/unicode") == "⟨a⟩₊"

    def test_even_eval(self):
        check_recipe("even_grades")

    def test_even_numeric_fallback(self):
        algebra = ga.Algebra(3)
        check_recipe("even_grades", algebra.multivector(LEFT), algebra.identity)

    def test_odd_str(self):
        assert check_recipe("odd_grades").display("expr/unicode") == "⟨a⟩₋"

    def test_odd_eval(self):
        check_recipe("odd_grades")

    def test_odd_numeric_fallback(self):
        algebra = ga.Algebra(3)
        check_recipe("odd_grades", algebra.multivector(LEFT), algebra.identity)


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda table: str(table["signature"]))
@pytest.mark.parametrize("row_index", range(23))
def test_archived_eager_and_replayed_values_have_live_public_owners(table, row_index):
    algebra = ga.Algebra(signature=table["signature"])
    a, b = algebra.multivector(table["left"]).named("a"), algebra.multivector(table["right"]).named("b")
    row = table["operations"][row_index]
    value = check_recipe(row["id"], a, b)
    assert_coefficients(value, row["data"])
    assert_coefficients(value, row["replay"])


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda table: str(table["signature"]))
@pytest.mark.parametrize("row_index", range(4))
def test_archived_mixed_inputs_preserve_numeric_results_and_literal_leaves(table, row_index):
    algebra = ga.Algebra(signature=table["signature"])
    a, b = algebra.multivector(table["left"]), algebra.multivector(table["right"])
    row = table["mixed_inputs"][row_index]
    recipe, state = row["id"].split(":")
    if state == "left_plain":
        b = b.named("b")
    else:
        assert state == "right_plain"
        a = a.named("a")
    value = check_recipe(recipe, a, b)
    assert_coefficients(value, row["data"])


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("recipe", RECIPES)
@pytest.mark.parametrize("state", ("plain", "literal", "named", "left_plain", "right_plain"))
def test_eager_results_and_replay_respect_provenance_and_metric_domains(gram, recipe, state):
    algebra = ga.Algebra(gram=gram)
    a, b = algebra.multivector(LEFT), algebra.multivector(RIGHT)
    if state == "literal":
        a, b = a.with_expr(), b.with_expr()
    elif state == "named":
        a, b = a.named("a"), b.named("b")
    elif state == "left_plain":
        b = b.named("b")
    elif state == "right_plain":
        a = a.named("a")
    if recipe in {"dual", "undual"} and np.linalg.det(gram) == 0:
        with pytest.raises(ValueError, match="invertible pseudoscalar"):
            invoke(recipe, a, b)
        with pytest.raises(ValueError, match="invertible pseudoscalar"):
            expected_coefficients(recipe, gram, LEFT, RIGHT)
        return

    result = check_recipe(recipe, a, b)
    if isinstance(result, ga.Multivector) and result.expr is not None:
        expression, before_hash = result.expr, hash(result)
        for target in ("ascii", "unicode", "latex"):
            with algebra.use_presentation(algebra.presentation.with_notation(ga.Notation.functional())):
                assert result.display(content="expr", target=target)
                replay = ga.evaluate(expression, algebra=algebra, environment={"a": a, "b": b})
                assert_coefficients(replay, result.data)
        # Bind only symbol leaves to new numbers; literals remain snapshots.
        new_a, new_b = algebra.multivector(1.5 * LEFT), algebra.multivector(0.75 * RIGHT)
        replay = ga.evaluate(expression, algebra=algebra, environment={"a": new_a, "b": new_b})
        effective_a = new_a.data if a.name is not None else a.data
        effective_b = new_b.data if b.name is not None else b.data
        assert_coefficients(replay, expected_coefficients(recipe, gram, effective_a, effective_b))
        assert result.expr is expression and hash(result) == before_hash
        assert_coefficients(result, expected_coefficients(recipe, gram, LEFT, RIGHT))


@pytest.mark.parametrize("recipe", ("geometric_product", "outer_product"))
def test_bare_nodes_require_explicit_calls_not_numeric_operator_coercion(recipe):
    algebra = ga.Algebra(3)
    a = algebra.multivector(LEFT)
    node = ga.Symbol("b")
    with pytest.raises(TypeError):
        getattr(ga, recipe)(a, node)
    explicit = ga.Call(recipe, (ga.MultivectorLiteral(a.data), node))
    with pytest.raises(KeyError, match="b"):
        ga.evaluate(explicit, algebra=algebra)
    value = ga.evaluate(explicit, algebra=algebra, environment={"b": algebra.multivector(RIGHT)})
    assert_coefficients(value, expected_coefficients(recipe, GRAMS[0], LEFT, RIGHT))


@pytest.mark.parametrize("gram", GRAMS)
def test_unit_and_inverse_are_distinct_and_fail_eagerly_on_invalid_inputs(gram):
    algebra = ga.Algebra(gram=gram)
    a = algebra.multivector(LEFT).named("a")
    normalized, inverted = ga.unit(a), ga.inverse(a)
    assert normalized != inverted
    assert_coefficients(a * inverted, algebra.identity.data)
    assert_coefficients(inverted * a, algebra.identity.data)
    _, _, metric, _ = oracle_metadata(gram)
    magnitude2 = LEFT @ metric @ LEFT
    assert np.isclose(float(ga.norm2(normalized)), np.sign(magnitude2), rtol=0, atol=1e-12)
    for value in (algebra.scalar(0), algebra.scalar(0).with_expr(), algebra.scalar(0).named("zero")):
        with pytest.raises(ValueError, match="normalize"):
            ga.unit(value)
        with pytest.raises(ValueError, match="not invertible"):
            ga.inverse(value)
    with pytest.raises(ZeroDivisionError):
        a / 0


@pytest.mark.parametrize("recipe", RECIPES)
def test_reviewed_expression_spellings_do_not_replace_numeric_or_structural_checks(recipe):
    value = check_recipe(recipe)
    for target, expected in zip(("ascii", "unicode", "latex"), SPELLINGS[recipe], strict=True):
        assert value.display(content="expr", target=target) == expected
    assert tuple(SPELLINGS) == RECIPES


def test_nonzero_null_values_are_not_normalizable_or_invertible():
    algebra = ga.Algebra(gram=GRAMS[2])
    null = algebra.vector((1, -1, 0))
    assert null != 0
    assert_coefficients(null * null, np.zeros(algebra.dim))
    for value in (null, null.with_expr(), null.named("n")):
        with pytest.raises(ValueError, match="normalize"):
            ga.unit(value)
        with pytest.raises(ValueError, match="not invertible"):
            ga.inverse(value)
