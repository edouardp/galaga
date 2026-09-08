"""Public LaTeX contracts extracted from the mixed coverage suite."""

import inspect
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
import galaga.core as core

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/coverage-latex-v1.json").read_text())
TARGETS = ("ascii", "unicode", "latex")
GRAMS = (((1, 0), (0, 1)), ((2, 0.5), (0.5, -1)), ((1, 1), (1, 1)))


def custom_blades():
    """Supply every native exterior blade label; no implicit name derivation."""
    letters = (ga.Name("a", "𝐚", "𝐚"), ga.Name("b", "𝐛", "𝐛"), ga.Name("c", "𝐜", "𝐜"))
    labels = []
    for mask in range(8):
        names = [name for index, name in enumerate(letters) if mask & (1 << index)]
        labels.append(
            ga.Name(
                "".join(name.ascii for name in names) or "1",
                "".join(name.unicode for name in names) or "1",
                " ".join(name.latex for name in names) or "1",
            )
        )
    return ga.BladeConvention(3, labels)


@pytest.fixture
def cl3():
    # Select expression content explicitly instead of the default auto policy.
    return ga.Algebra(3, display=ga.DisplayPolicy(content="expr"))


def assert_data(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.ndim == expected.ndim == 1 and actual.shape == expected.shape
    assert np.isfinite(actual).all() and np.isfinite(expected).all()
    np.testing.assert_allclose(actual, expected, rtol=0, atol=2e-12)


def accepted_body(text):
    """Only the already accepted v2 accent and contraction typography changes."""
    if text.startswith("$$\n") and text.endswith("\n$$"):
        text = text[3:-3]
    elif text.startswith("$") and text.endswith("$"):
        text = text[1:-1]
    for old, new in (
        (r"\tilde", r"\widetilde"),
        (r"\hat", r"\widehat"),
        (r"\bar", r"\overline"),
        (r"\;\lrcorner\;", r"\mathbin{\rfloor}"),
        (r"\;\llcorner\;", r"\mathbin{\lfloor}"),
    ):
        text = text.replace(old, new)
    return text


def check_archived_method(row, monkeypatch):
    """Every rendering call keeps both a literal string and a numeric owner."""
    cls, method = row["id"].split(".")
    method = getattr(globals()[cls](), method)
    seen = set()
    calls = 0
    original = ga.Multivector.latex

    def checked(value, *args, **kwargs):
        nonlocal calls
        calls += 1
        data, expression, value_hash = value.data.copy(), value.expr, hash(value)
        text = original(value, *args, **kwargs)
        wrap = inspect.signature(original).bind(value, *args, **kwargs).arguments.get("wrap")
        if ".test_repr_latex" in row["id"]:
            # V1's rich hook wrapped the result; v2 delegates wrapping to latex.
            wrap = None
        matches = [
            index
            for index, observation in enumerate(row["observations"])
            if accepted_body(text) == accepted_body(observation["latex"]) and observation["wrap"] == wrap
        ]
        assert matches, "unreviewed rendering change"
        for index in matches:
            observation = row["observations"][index]
            assert_data(value.algebra.gram.ravel(), np.diag(observation["signature"]).ravel())
            assert_data(data, observation["data"])
            if expression is not None:
                environment = {
                    key: value.algebra.multivector(coeffs) for key, coeffs in observation["bindings"].items()
                }
                assert_data(ga.evaluate(expression, algebra=value.algebra, environment=environment).data, data)
            seen.add(index)
        assert_data(value.data, data)
        assert value.expr is expression and hash(value) == value_hash
        return text

    monkeypatch.setattr(ga.Multivector, "latex", checked)
    kwargs = (
        {"cl3": ga.Algebra(3, display=ga.DisplayPolicy(content="expr"))}
        if "cl3" in inspect.signature(method).parameters
        else {}
    )
    method(**kwargs)
    assert seen == set(range(len(row["observations"]))), "archived output lost its live numeric owner"
    # Replacing the permissive vector assertion removes its second OR operand.
    expected_calls = len(row["observations"]) - (row["id"] == "TestLatex.test_multivector_latex_bare")
    assert calls == expected_calls, "historical rendering call removed or duplicated"


@pytest.mark.parametrize("row", ARCHIVE["tests"], ids=lambda row: row["id"])
def test_all_historical_renderings_keep_computed_values_and_explicit_replay(row, monkeypatch):
    check_archived_method(row, monkeypatch)


class TestLatex:
    def test_sym(self, cl3):
        "An explicit symbol leaf renders its LaTeX spelling."
        e1, _, _ = cl3.basis_vectors()
        assert e1.named("v").with_expr().latex() == "v"

    def test_gp(self, cl3):
        """Gp LaTeX renders with space."""
        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).named("R").with_expr()
        v = e1.named("v").with_expr()
        assert (R * v).latex() == "R v"

    def test_sandwich_grade(self, cl3):
        """Grade of sandwich renders correctly."""
        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).named("R").with_expr()
        v = e1.named("v").with_expr()
        assert ga.grade(R * v * ~R, 1).latex() == "\\langle R v \\widetilde{R} \\rangle_{1}"

    def test_wedge(self, cl3):
        """Op LaTeX renders with \\wedge."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = (e1.named("a").with_expr(), e2.named("b").with_expr())
        assert (a ^ b).latex() == "a \\wedge b"

    def test_left_contraction(self, cl3):
        "Left contraction uses the right-floor glyph."
        e1, e2, _ = cl3.basis_vectors()
        a, b = (e1.named("a").with_expr(), e2.named("b").with_expr())
        assert ga.left_contraction(a, b).latex() == "a \\mathbin{\\rfloor} b"

    def test_right_contraction(self, cl3):
        "Right contraction uses the left-floor glyph."
        e1, e2, _ = cl3.basis_vectors()
        a, b = (e1.named("a").with_expr(), e2.named("b").with_expr())
        assert ga.right_contraction(a, b).latex() == "a \\mathbin{\\lfloor} b"

    def test_hestenes_inner(self, cl3):
        """Hi LaTeX renders with \\cdot."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = (e1.named("A").with_expr(), e2.named("B").with_expr())
        assert ga.hestenes_inner(a, b).latex() == "A \\cdot B"

    def test_scalar_product(self, cl3):
        """Sp LaTeX renders with *."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = (e1.named("A").with_expr(), e2.named("B").with_expr())
        assert ga.scalar_product(a, b).latex() == "A * B"

    def test_reverse(self, cl3):
        "Reverse uses the wide tilde accent."
        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).named("R").with_expr()
        assert (~R).latex() == "\\widetilde{R}"

    def test_involute(self, cl3):
        """Involute LaTeX renders with \\widehat."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        assert ga.grade_involution(v).latex() == "\\widehat{v}"

    def test_conjugate(self, cl3):
        "Conjugation uses the overline accent."
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        assert ga.conjugate(v).latex() == "\\overline{v}"

    def test_dual(self, cl3):
        """Dual LaTeX renders with ^*."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        assert ga.dual(v).latex() == "v^*"

    def test_undual(self, cl3):
        """Undual LaTeX renders with ^{*^{-1}}."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        assert ga.undual(v).latex() == "v^{*^{-1}}"

    def test_norm(self, cl3):
        """Norm LaTeX renders with \\lVert."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        assert ga.norm(v).latex() == "\\lVert v \\rVert"

    def test_unit(self, cl3):
        """Unit LaTeX renders with \\widehat."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        assert ga.unit(v).latex() == "\\widehat{v}"

    def test_inverse(self, cl3):
        """Inverse LaTeX renders with ^{-1}."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        assert ga.inverse(v).latex() == "v^{-1}"

    def test_squared(self, cl3):
        """Squared LaTeX renders with ^2."""
        e1, e2, _ = cl3.basis_vectors()
        R = (e1 * e2).named("R").with_expr()
        assert ga.squared(R).latex() == "R^2"

    def test_even(self, cl3):
        "Even-grade selection has an explicit parity label."
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        assert ga.even_grades(v).latex() == "\\langle v \\rangle_{\\text{even}}"

    def test_odd(self, cl3):
        "Odd-grade selection has an explicit parity label."
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        assert ga.odd_grades(v).latex() == "\\langle v \\rangle_{\\text{odd}}"

    def test_add(self, cl3):
        """Add LaTeX renders with +."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = (e1.named("a").with_expr(), e2.named("b").with_expr())
        assert (a + b).latex() == "a + b"

    def test_sub(self, cl3):
        """Sub LaTeX renders with -."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = (e1.named("a").with_expr(), e2.named("b").with_expr())
        assert (a - b).latex() == "a - b"

    def test_neg(self, cl3):
        """Neg LaTeX renders with -."""
        e1, _, _ = cl3.basis_vectors()
        a = e1.named("a").with_expr()
        assert (-a).latex() == "-a"

    def test_scalar_mul(self, cl3):
        """ScalarMul LaTeX renders as coefficient."""
        e1, _, _ = cl3.basis_vectors()
        a = e1.named("a").with_expr()
        assert (3 * a).latex() == "3 a"
        assert (-1 * a).latex() == "-a"

    def test_parens(self, cl3):
        "A sum used as a product operand has scalable parentheses."
        e1, e2, _ = cl3.basis_vectors()
        a, b = (e1.named("a").with_expr(), e2.named("b").with_expr())
        R = (e1 * e2).named("R").with_expr()
        assert ((a + b) * R).latex() == "\\left(a + b\\right) R"

    def test_repr_latex(self, cl3):
        """MV._repr_latex_() wraps in $."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        assert v._repr_latex_() == "$v$"
        assert (~v)._repr_latex_() == "$\\widetilde{v}$"

    def test_multivector_latex_bare(self, cl3):
        """Bare value output is exact and contains no math delimiters."""
        e1, e2, _ = cl3.basis_vectors()
        v = 3 * e1 + 4 * e2
        assert v.latex() == "3 e_{1} + 4 e_{2}"
        assert "$" not in v.latex()

    def test_multivector_latex_wrap_inline(self, cl3):
        """MV.latex(wrap='$') wraps inline."""
        e1, _, _ = cl3.basis_vectors()
        v = 3 * e1
        raw = v.latex()
        assert v.latex(wrap="$") == f"${raw}$"

    def test_multivector_latex_wrap_display(self, cl3):
        """MV.latex(wrap='$$') wraps display."""
        e1, _, _ = cl3.basis_vectors()
        v = 3 * e1
        raw = v.latex()
        assert v.latex(wrap="$$") == f"$$\n{raw}\n$$"

    def test_multivector_latex_wrap_none(self, cl3):
        """MV.latex(wrap=None) returns raw."""
        e1, _, _ = cl3.basis_vectors()
        v = 3 * e1
        assert v.latex(wrap=None) == v.latex()


class TestMultivectorLatex:
    def test_scalar(self, cl3):
        """Scalar MV LaTeX renders as number."""
        assert cl3.scalar(5).latex() == "5"

    def test_zero(self, cl3):
        "A zero multivector renders as the number zero."
        assert cl3.scalar(0).latex() == "0"

    def test_vector(self, cl3):
        """Vector MV LaTeX renders with basis names."""
        e1, e2, e3 = cl3.basis_vectors()
        assert (3 * e1 + 4 * e2).latex() == "3 e_{1} + 4 e_{2}"

    def test_coeff_one_suppressed(self, cl3):
        """Coefficient ±1 is suppressed in LaTeX."""
        e1, e2, _ = cl3.basis_vectors()
        assert e1.latex() == "e_{1}"
        assert (-e2).latex() == "-e_{2}"

    def test_bivector(self, cl3):
        """Bivector MV LaTeX renders correctly."""
        e1, e2, _ = cl3.basis_vectors()
        assert (e1 ^ e2).latex() == "e_{12}"

    def test_pseudoscalar(self, cl3):
        """Pseudoscalar MV LaTeX renders correctly."""
        assert cl3.pseudoscalar().latex() == "e_{123}"

    def test_mixed(self, cl3):
        """Mixed-grade MV LaTeX renders all terms."""
        e1, e2, _ = cl3.basis_vectors()
        mv = cl3.scalar(1) + 2 * e1 + 3 * (e1 ^ e2)
        assert mv.latex() == "1 + 2 e_{1} + 3 e_{12}"

    def test_negative_terms(self, cl3):
        """Negative terms use - not + -."""
        e1, e2, _ = cl3.basis_vectors()
        assert (e1 - e2).latex() == "e_{1} - e_{2}"

    def test_gamma_names(self):
        """Gamma-named algebra uses γ in LaTeX."""
        sta = ga.Algebra(
            (1, -1, -1, -1),
            blades=ga.indexed_blade_convention(4, prefix=ga.Name("g", "γ", "\\gamma"), start=0, style="juxtapose"),
        )
        g0, g1, _, _ = sta.basis_vectors()
        assert g0.latex() == "\\gamma_{0}"
        assert (g0 * g1).latex() == "\\gamma_{0} \\gamma_{1}"

    def test_sigma_names(self):
        """Sigma-named algebra uses σ in LaTeX."""
        pauli = ga.Algebra(
            (1, 1, 1), blades=ga.indexed_blade_convention(3, prefix=ga.Name("s", "σ", "\\sigma"), style="juxtapose")
        )
        s1, s2, _ = pauli.basis_vectors()
        assert s1.latex() == "\\sigma_{1}"
        assert (s1 * s2).latex() == "\\sigma_{1} \\sigma_{2}"

    def test_repr_latex(self, cl3):
        """MV._repr_latex_() wraps in $."""
        e1, _, _ = cl3.basis_vectors()
        assert e1._repr_latex_() == "$e_{1}$"

    def test_repr_latex_mixed(self, cl3):
        """Mixed MV _repr_latex_() wraps correctly."""
        e1, e2, _ = cl3.basis_vectors()
        mv = cl3.scalar(1) + e1
        assert mv._repr_latex_() == "$1 + e_{1}$"


class TestCoverageGaps:
    def test_blade_latex_custom_names_no_latex(self):
        """Custom names with explicit latex use the latex variant."""
        alg = ga.Algebra((1, 1, 1), blades=custom_blades())
        e1, e2, _ = alg.basis_vectors()
        mv = e1 ^ e2
        latex = mv.latex()
        assert latex == "𝐚 𝐛"

    def test_expr_latex_wrap(self, cl3):
        """Expr.latex(wrap='$') wraps in $."""
        e1, _, _ = cl3.basis_vectors()
        v = e1.named("v").with_expr()
        raw = v.latex()
        assert v.latex(wrap="$") == f"${raw}$"
        assert v.latex(wrap="$$") == f"$$\n{raw}\n$$"


# Exact output is specified separately from reference-product numeric oracles.
SPELLINGS = {
    "gp": ("(a + b)B", "(a + b)B", r"\left(a + b\right) B"),
    "wedge": ("a ^ b", "a ∧ b", r"a \wedge b"),
    "left": ("a _| B", "a ⌋ B", r"a \mathbin{\rfloor} B"),
    "right": ("B |_ a", "B ⌊ a", r"B \mathbin{\lfloor} a"),
    "inner": ("hestenes_inner(a, b)", "hestenes_inner(a, b)", r"a \cdot b"),
    "scalar": ("B * B", "B * B", "B * B"),
    "reverse": ("~(ab)", "(ab)̃", r"\widetilde{a b}"),
    "involution": ("hat(a)", "â", r"\widehat{a}"),
    "conjugate": ("bar((ab))", "(ab)̅", r"\overline{a b}"),
    "dual": ("a^*", "a^★", "a^*"),
    "undual": ("a^*^-1", "a^(★⁻¹)", "a^{*^{-1}}"),
    "norm": ("||B||", "‖B‖", r"\lVert B \rVert"),
    "unit": ("hat(a)", "â", r"\widehat{a}"),
    "inverse": ("a^-1", "a⁻¹", "a^{-1}"),
    "square": ("(a + b)^2", "(a + b)²", r"\left(a + b\right)^2"),
    "even": ("<2 + a + B>even", "⟨2 + a + B⟩₊", r"\langle 2 + a + B \rangle_{\text{even}}"),
    "odd": ("<2 + a + B>odd", "⟨2 + a + B⟩₋", r"\langle 2 + a + B \rangle_{\text{odd}}"),
    "grade": ("<Ba~B>[1]", "⟨BaB̃⟩₁", r"\langle B a \widetilde{B} \rangle_{1}"),
    "negative": ("-(a + b)", "-(a + b)", r"-\left(a + b\right)"),
    "scale": ("-3(a + b)", "-3(a + b)", r"-3 \left(a + b\right)"),
}


@lru_cache
def reference_metadata(gram):
    reference = core.Algebra(gram=gram, product_backend="reference")
    product = np.stack([reference.left_action(reference.blade(mask)) for mask in range(reference.dim)], axis=1)
    indices = [tuple(i for i in range(reference.n) if mask & (1 << i)) for mask in range(reference.dim)]
    degrees = np.array([len(index) for index in indices])
    pairing = np.zeros((reference.dim, reference.dim))
    for i, rows in enumerate(indices):
        for j, columns in enumerate(indices):
            if len(rows) == len(columns):
                pairing[i, j] = np.linalg.det(np.asarray(gram)[np.ix_(rows, columns)])
    return product, pairing, degrees


def reference_value(node, gram, environment):
    """Native-mask signs/minors and the forced reference product, not facade ops."""
    product, pairing, degrees = reference_metadata(gram)
    identity = np.zeros(2 ** len(gram))
    identity[0] = 1
    if isinstance(node, ga.Symbol):
        return np.asarray(environment[node.identifier])
    if isinstance(node, ga.ScalarLiteral):
        return node.value * identity
    assert isinstance(node, ga.Call)
    values = [reference_value(operand, gram, environment) for operand in node.operands]
    a = values[0]
    operation = node.operation_id
    parameters = dict(node.parameters)

    def gp(left, right):
        return np.einsum("i,kij,j->k", left, product, right)

    if operation == "add":
        return a + values[1]
    if operation == "negate":
        return -a
    if operation == "scalar_multiply":
        return parameters["scalar"] * a
    if operation == "geometric_product":
        return gp(a, values[1])
    if operation in {"outer_product", "left_contraction", "right_contraction", "hestenes_inner", "scalar_product"}:
        result = np.zeros_like(a)
        for i, r in enumerate(degrees):
            for j, s in enumerate(degrees):
                target = {
                    "outer_product": r + s,
                    "left_contraction": s - r,
                    "right_contraction": r - s,
                    "hestenes_inner": abs(r - s) if r and s else -1,
                    "scalar_product": 0,
                }[operation]
                result += a[i] * values[1][j] * np.where(degrees == target, product[:, i, j], 0)
        return result
    if operation in {"reverse", "grade_involution", "conjugate"}:
        power = {
            "reverse": degrees * (degrees - 1) // 2,
            "grade_involution": degrees,
            "conjugate": degrees * (degrees + 1) // 2,
        }[operation]
        return (-1.0) ** power * a
    if operation in {"dual", "undual"}:
        determinant = np.linalg.det(gram)
        if determinant == 0:
            raise ValueError("invertible pseudoscalar required")
        volume = np.zeros_like(a)
        n = len(gram)
        volume[-1] = 1 if operation == "undual" else 1 / ((-1) ** (n * (n - 1) // 2) * determinant)
        return gp(a, volume)
    if operation in {"norm", "unit"}:
        magnitude = np.sqrt(abs(float(a @ pairing @ a)))
        return magnitude * identity if operation == "norm" else a / magnitude
    if operation == "inverse":
        return np.linalg.solve(np.einsum("i,kij->kj", a, product), identity)
    if operation == "squared":
        return gp(a, a)
    if operation == "grade":
        return np.where(degrees == parameters["target"], a, 0)
    assert operation in {"even_grades", "odd_grades"}
    return np.where(degrees % 2 == (operation == "odd_grades"), a, 0)


def mixed_case(gram, case):
    algebra = ga.Algebra(gram=gram)
    a = algebra.vector((2, 1)).named("a")
    b = algebra.vector((-1, 3)).named("b")
    B = algebra.blade(3).named("B")
    environment = {"a": a, "b": b, "B": B}
    recipes = {
        "gp": lambda: (a + b) * B,
        "wedge": lambda: a ^ b,
        "left": lambda: ga.left_contraction(a, B),
        "right": lambda: ga.right_contraction(B, a),
        "inner": lambda: ga.hestenes_inner(a, b),
        "scalar": lambda: ga.scalar_product(B, B),
        "reverse": lambda: ~(a * b),
        "involution": lambda: ga.grade_involution(a),
        "conjugate": lambda: ga.conjugate(a * b),
        "dual": lambda: ga.dual(a),
        "undual": lambda: ga.undual(a),
        "norm": lambda: ga.norm(B),
        "unit": lambda: ga.unit(a),
        "inverse": lambda: ga.inverse(a),
        "square": lambda: ga.squared(a + b),
        "even": lambda: ga.even_grades(2 + a + B),
        "odd": lambda: ga.odd_grades(2 + a + B),
        "grade": lambda: ga.grade(B * a * ~B, 1),
        "negative": lambda: -(a + b),
        "scale": lambda: -3 * (a + b),
    }
    return algebra, environment, recipes[case]


@pytest.mark.parametrize("gram", GRAMS, ids=("euclidean", "oblique-indefinite", "degenerate"))
@pytest.mark.parametrize("case", SPELLINGS)
@pytest.mark.parametrize("target", TARGETS)
def test_nonvacuous_compositions_preserve_values_replay_and_exact_scope(gram, case, target):
    algebra, environment, recipe = mixed_case(gram, case)
    expected_text = SPELLINGS[case][TARGETS.index(target)]
    arrays = {key: value.data for key, value in environment.items()}
    if case in {"dual", "undual"} and np.linalg.det(gram) == 0:
        node = ga.Call(case, (ga.Symbol("a"),))
        with pytest.raises(ValueError, match="invertible pseudoscalar"):
            recipe()
        with pytest.raises(ValueError, match="invertible pseudoscalar"):
            reference_value(node, gram, arrays)
        with pytest.raises(ValueError, match="invertible pseudoscalar"):
            ga.evaluate(node, algebra=algebra, environment=environment)
        # Unbound symbolic rendering alone cannot certify an evaluation domain.
        assert ga.render(node, presentation=algebra.presentation, target=target) == expected_text
        return
    value = recipe()
    node, value_hash, data = value.expr, hash(value), value.data.copy()
    expected = reference_value(node, gram, arrays)
    if np.linalg.det(gram) != 0:
        assert np.any(abs(expected) > 1e-8), "a zero example cannot pin this operation's semantics"
    assert_data(data, expected)
    assert value.display("expr/" + target) == expected_text
    assert_data(ga.evaluate(node, algebra=algebra, environment=environment).data, expected)
    assert_data(value.data, data)
    assert value.expr is node and hash(value) == value_hash


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("content", ("name", "expr", "value", "full"))
@pytest.mark.parametrize("target", TARGETS)
def test_wrapping_and_rich_hooks_preserve_selected_content_and_scoped_notation(gram, content, target):
    algebra, environment, recipe = mixed_case(gram, "gp")
    value = recipe().named("M")
    coefficients, node, value_hash = value.data.copy(), value.expr, hash(value)
    original_presentation = algebra.presentation
    selected = algebra.presentation.with_display(ga.DisplayPolicy(content=content, target=target))
    with algebra.use_presentation(selected):
        body = value.latex()
        assert body == value.display(content=content, target="latex")
        assert value.latex(wrap=None) == body
        assert value.latex(wrap="$") == value._repr_latex_() == f"${body}$"
        assert value.latex(wrap="$$") == f"$$\n{body}\n$$"
        assert repr(value) == value.display(content=content, target="ascii")
        functional = selected.with_notation(ga.Notation.functional())
        with pytest.raises(RuntimeError, match="restore"):
            with algebra.use_presentation(functional):
                assert (
                    value.latex(content="expr")
                    == r"\operatorname{geometric\_product}\left(\operatorname{add}\left(a, b\right), B\right)"
                )
                assert value.latex(content=content, wrap="$") == "$" + value.latex(content=content) + "$"
                raise RuntimeError("restore")
        assert value.latex() == body
    assert algebra.presentation is original_presentation
    assert_data(value.data, coefficients)
    assert value.expr is node and hash(value) == value_hash
    assert_data(ga.evaluate(node, algebra=algebra, environment=environment).data, coefficients)


@pytest.mark.parametrize("wrap", ("", "$$$", r"\(", 0, True))
def test_invalid_wrappers_are_rejected_instead_of_silently_ignored(wrap):
    with pytest.raises(ValueError, match="LaTeX wrap"):
        ga.Algebra(1).blade(1).latex(wrap=wrap)


@pytest.mark.parametrize("gram", GRAMS)
def test_a_name_and_a_provenance_leaf_are_distinct_content_choices(gram):
    algebra = ga.Algebra(gram=gram)
    named = algebra.vector((2, 1)).named("a")
    assert named.expr is None
    body = named.latex(content="value")
    assert named.latex(content="expr") == body
    assert named.latex() == "a" + r" \quad = \quad " + body
    assert named.latex(content="name") == "a"
    explicit = named.with_expr()
    assert explicit.expr == ga.Symbol("a")
    assert explicit == named and hash(explicit) == hash(named)
    assert explicit.latex(content="expr") == "a"
    assert explicit.latex() == named.latex()


@pytest.mark.parametrize("gram", GRAMS)
def test_identical_hat_accents_do_not_equate_unit_normalization_and_grade_involution(gram):
    algebra, environment, unit_recipe = mixed_case(gram, "unit")
    unit = unit_recipe()
    involution = ga.grade_involution(environment["a"])
    assert unit.latex(content="expr") == involution.latex(content="expr") == r"\widehat{a}"
    assert unit.expr != involution.expr and unit != involution
    functional = ga.Notation.functional()
    assert unit.latex(content="expr", notation=functional) == r"\operatorname{unit}\left(a\right)"
    assert involution.latex(content="expr", notation=functional) == r"\operatorname{grade\_involution}\left(a\right)"
    arrays = {key: value.data for key, value in environment.items()}
    for value in (unit, involution):
        assert_data(value.data, reference_value(value.expr, gram, arrays))
