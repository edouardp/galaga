"""RGA presentation is checked against archived data and coefficient oracles."""

import json
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
from galaga import core
from galaga.expression import Call, evaluate, simplify

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/rga-convention-contracts-v1.json").read_text())
UNARY = (
    "metric_apply",
    "antimetric_apply",
    "bulk_part",
    "weight_part",
    "right_hodge_dual",
    "left_hodge_dual",
    "right_weight_dual",
    "left_weight_dual",
    "antireverse",
)
BINARY = (
    "metric_inner_product",
    "antidot_product",
    "geometric_antiproduct",
    "left_interior_product",
    "right_interior_product",
    "transwedge",
    "transwedge_antiproduct",
)
GRAMS = (
    np.diag([1.0, 1.0, 1.0, 0.0]),
    np.array([[2.0, 0.5, 0, 0], [0.5, -1.0, 0.25, 0], [0, 0.25, 1.0, 0.5], [0, 0, 0.5, 0]]),
    np.array([[1.0, 0, 0, 1.0], [0, 1.0, 0, 1.0], [0, 0, 1.0, 0], [1.0, 1.0, 0, 2.0]]),
)
LEFT = np.array([-2, 1, 4, 4, 2, -4, 1, 0, 0, -1, -2, -3, 2, 3, -3, 0], dtype=float)
RIGHT = np.array([1, 1, -2, -2, -1, 1, 3, 2, -3, -3, -2, -2, 3, -2, -2, 0], dtype=float)


def assert_coefficients(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape == (16,), "coefficient shape"
    assert np.isfinite(actual).all() and np.isfinite(expected).all(), "nonfinite coefficients"
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-11)


def archived_case(row):
    algebra = ga.Algebra(config=ga.p_rga(), display=ga.DisplayPolicy(content="expr"))
    x, y, _, _ = algebra.basis_vectors(expr=True)
    if row["kind"] == "operation":
        arguments = (x,) if row["arity"] == 1 else ((x, y, row["order"]) if row["arity"] == 3 else (x, y))
        result = getattr(ga, row["operation"])(*arguments)
    elif row["kind"] == "nested":
        result = ga.antireverse(ga.antiwedge(ga.complement(x), ga.complement(y)))
    elif row["kind"] == "pseudoscalar":
        result = algebra.I
    elif row["kind"] == "fallback":
        notation = ga.Notation.lengyel().with_rule(
            "antireverse", ga.RenderRule("underaccent", symbol=ga.Name("sim", "\u0330", r"\sim")), target="latex"
        )
        algebra = algebra.with_notation(notation)
        result = ga.antireverse(algebra.blade(1, expr=True))
    else:
        assert row["kind"] == "default"
        algebra = algebra.with_notation(ga.Notation.default())
        result = ga.metric_inner_product(*algebra.basis_vectors(expr=True)[:2])
    return algebra, result


@pytest.mark.parametrize("row", ARCHIVE["observations"])
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_original_rga_observations_keep_numeric_values_and_reviewed_spelling(row, target):
    algebra, result = archived_case(row)
    assert_coefficients(result.data, row["coefficients"])
    if result.expr is not None:
        assert_coefficients(evaluate(result.expr, algebra=algebra).data, row["coefficients"])
    # Accepted v2 typography is bounded and explicit, never whitespace-normalized.
    expected = row[target]
    if target == "ascii":
        # V1's format(value, "a") silently kept Unicode for symbolic values.
        if row["kind"] == "operation":
            operation = row["operation"]
            arguments = "e1" if row["arity"] == 1 else ("e1, e2, 1" if row["arity"] == 3 else "e1, e2")
            expected = (
                "~e1"
                if operation == "reverse"
                else (f"{'gp' if operation == 'geometric_product' else operation}({arguments})")
            )
        else:
            expected = {
                "nested": "antireverse(antiwedge(complement(e1), complement(e2)))",
                "pseudoscalar": "I",
                "fallback": "antireverse(e1)",
                "default": "metric_inner_product(e1, e2)",
            }[row["kind"]]
    if target == "unicode":
        if row.get("operation") == "antiwedge":
            expected = "e₁ ∨ e₂"
        if row["kind"] == "nested":
            expected = "(e₁̅ ∨ e₂̅)̰"
    if target == "latex":
        expected = expected.replace(r"\vphantom{Aft^6}", "").replace(r"\vphantom{gy_7}", "")
        if row.get("operation") == "reverse":
            expected = r"\widetilde{\mathbf{e}_{1}}"
        if row.get("operation") == "left_interior_product":
            expected = r"\mathbf{e}_{1} \mathbin{\rfloor} \mathbf{e}_{2}"
        if row.get("operation") == "right_interior_product":
            expected = r"\mathbf{e}_{1} \mathbin{\lfloor} \mathbf{e}_{2}"
    assert result.display(f"expr/{target}") == expected


class CoefficientOracle:
    """Minors and exterior permutations; only GP uses core's reference backend."""

    def __init__(self, gram):
        self.gram = np.asarray(gram)
        self.grades = np.array([mask.bit_count() for mask in range(16)])
        axes = [tuple(index for index in range(4) if mask & (1 << index)) for mask in range(16)]
        metric = np.zeros((16, 16))
        right = np.zeros((16, 16))
        wedge = np.zeros((16, 16, 16))
        for i in range(16):
            missing = 15 ^ i
            word = (*axes[i], *axes[missing])
            sign = (-1) ** sum(a > b for index, a in enumerate(word) for b in word[index + 1 :])
            right[missing, i] = sign
            for j in range(16):
                if self.grades[i] == self.grades[j]:
                    metric[i, j] = np.linalg.det(self.gram[np.ix_(axes[i], axes[j])])
                if not i & j:
                    word = (*axes[i], *axes[j])
                    sign = (-1) ** sum(a > b for index, a in enumerate(word) for b in word[index + 1 :])
                    wedge[i, i | j, j] = sign
        self.metric, self.right, self.left, self.wedge = metric, right, right.T, wedge
        self.antimetric = right @ metric @ right.T
        reference = core.Algebra(gram=gram, product_backend="reference")
        self.product = np.stack([reference.left_action(reference.blade(mask)) for mask in range(16)])

    def gp(self, left, right):
        return np.einsum("i,ikj,j->k", left, self.product, right)

    def meet(self, left, right):
        return self.left @ np.einsum("i,ikj,j->k", self.right @ left, self.wedge, self.right @ right)

    def transwedge(self, left, right, order):
        r, s, t = self.grades[:, None, None], self.grades[None, None, :], self.grades[None, :, None]
        selected = (order <= np.minimum(r, s)) & (t == r + s - 2 * order)
        sign = (-1) ** (order * (order - 1) // 2)
        return sign * np.einsum("i,ikj,j->k", left, self.product * selected, right)

    def operations(self, left, right, order=1):
        metric_left = self.metric @ left
        antimetric_left = self.antimetric @ left
        antigrades = 4 - self.grades
        scalar, pseudoscalar = np.eye(16)[0], np.eye(16)[15]
        return {
            "metric_apply": metric_left,
            "antimetric_apply": antimetric_left,
            "bulk_part": metric_left,
            "weight_part": antimetric_left,
            "right_hodge_dual": self.right @ metric_left,
            "left_hodge_dual": self.left @ metric_left,
            "right_weight_dual": self.right @ antimetric_left,
            "left_weight_dual": self.left @ antimetric_left,
            "antireverse": (-1.0) ** (antigrades * (antigrades - 1) // 2) * left,
            "metric_inner_product": (left @ self.metric @ right) * scalar,
            "antidot_product": (left @ self.antimetric @ right) * pseudoscalar,
            "geometric_antiproduct": self.right @ self.gp(self.left @ left, self.left @ right),
            "left_interior_product": self.meet(self.left @ metric_left, right),
            "right_interior_product": self.meet(left, self.right @ (self.metric @ right)),
            "transwedge": self.transwedge(left, right, order),
            "transwedge_antiproduct": self.right @ self.transwedge(self.left @ left, self.left @ right, order),
        }


@pytest.fixture(scope="module", params=GRAMS, ids=("rga", "oblique-indefinite", "singular-oblique"))
def oracle(request):
    return CoefficientOracle(request.param)


@pytest.mark.parametrize("operation", (*UNARY, *BINARY))
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_nonzero_rga_operations_keep_coefficients_grades_and_provenance(oracle, operation, target):
    expected = oracle.operations(LEFT, RIGHT)[operation]
    assert np.linalg.norm(expected) > 1, "fixture must expose nonzero behavior"
    algebra = ga.Algebra(gram=oracle.gram, blades=ga.rga_blade_convention(), notation=ga.Notation.lengyel())
    a, b = algebra.multivector(LEFT).named("A"), algebra.multivector(RIGHT).named("B")
    args = (a,) if operation in UNARY else ((a, b, 1) if operation.startswith("transwedge") else (a, b))
    result = getattr(ga, operation)(*args)
    assert_coefficients(result.data, expected)
    assert result.expr.operation_id == operation
    expression, before_hash = result.expr, hash(result)
    environment = {"A": a, "B": b}
    assert_coefficients(evaluate(expression, algebra=algebra, environment=environment).data, expected)
    assert_coefficients(evaluate(simplify(expression), algebra=algebra, environment=environment).data, expected)
    expected_grades = {mask.bit_count() for mask, coefficient in enumerate(expected) if abs(coefficient) > 1e-11}
    assert result.homogeneous_grade() == (next(iter(expected_grades)) if len(expected_grades) == 1 else None)
    rendered = result.display(f"expr/{target}")
    assert "A" in rendered and (operation in UNARY or "B" in rendered)
    view = algebra.with_notation(ga.Notation.default())
    with algebra.use_presentation(view.presentation):
        assert_coefficients(result.data, expected)
        assert result.display(f"expr/{target}") == result.display(f"expr/{target}", notation=ga.Notation.default())
    assert result.display(f"expr/{target}") == rendered
    assert result.expr is expression and hash(result) == before_hash
    assert view.numeric is algebra.numeric


@pytest.mark.parametrize("operation", ("transwedge", "transwedge_antiproduct"))
@pytest.mark.parametrize("order", range(5))
def test_transwedge_order_survives_simplification_and_controls_actual_grade_selection(oracle, operation, order):
    expected = oracle.operations(LEFT, RIGHT, order)[operation]
    algebra = ga.Algebra(gram=oracle.gram)
    a, b = algebra.multivector(LEFT).named("A"), algebra.multivector(RIGHT).named("B")
    result = getattr(ga, operation)(a, b, order)
    assert_coefficients(result.data, expected)
    simplified = simplify(result.expr)
    assert isinstance(simplified, Call) and simplified.parameters == (("order", order),)
    assert_coefficients(evaluate(simplified, algebra=algebra, environment={"A": a, "B": b}).data, expected)


def test_ordered_transwedge_sums_reconstruct_both_products_and_pga_projection_boundary(oracle):
    algebra = ga.Algebra(gram=oracle.gram)
    a, b = algebra.multivector(LEFT), algebra.multivector(RIGHT)
    for operation, product in (
        ("transwedge", "geometric_product"),
        ("transwedge_antiproduct", "geometric_antiproduct"),
    ):
        total = algebra.scalar(0)
        for order in range(5):
            total += (-1) ** (order * (order - 1) // 2) * getattr(ga, operation)(a, b, order)
        expected = oracle.gp(LEFT, RIGHT) if product == "geometric_product" else oracle.operations(LEFT, RIGHT)[product]
        assert_coefficients(total.data, expected)
        assert_coefficients(getattr(ga, product)(a, b).data, expected)
    combined = ga.bulk_part(a) + ga.weight_part(a)
    if np.array_equal(oracle.gram, GRAMS[0]):
        assert combined == a
    else:
        assert not combined.almost_equal(a)  # These are not universal complementary projections.
