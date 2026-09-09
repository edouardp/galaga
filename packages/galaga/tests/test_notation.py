"""Public notation contracts with captured legacy ownership and observations."""

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
from galaga.expression import Call, Symbol, evaluate

ARCHIVE = json.loads((Path(__file__).parents[1] / "tools/baselines/notation-contracts-v1.json").read_text())
TARGETS = ("ascii", "unicode", "latex")

# V1 node class names are evidence keys only. Div is now gp(a, inverse(b)),
# not a new or aliased division operation in the v2 catalog.
OLD_NODE_OPERATIONS = {
    "Reverse": "reverse",
    "Involute": "grade_involution",
    "Conjugate": "conjugate",
    "Dual": "dual",
    "Undual": "undual",
    "Inverse": "inverse",
    "Squared": "squared",
    "Neg": "negate",
    "ScalarMul": "scalar_multiply",
    "ScalarDiv": "scalar_divide",
    "Gp": "geometric_product",
    "Op": "outer_product",
    "Lc": "left_contraction",
    "Rc": "right_contraction",
    "Hi": "hestenes_inner",
    "Dli": "doran_lasenby_inner",
    "Sp": "scalar_product",
    "MetricInnerProduct": "metric_inner_product",
    "AntidotProduct": "antidot_product",
    "GeometricAntiproduct": "geometric_antiproduct",
    "LeftInteriorProduct": "left_interior_product",
    "RightInteriorProduct": "right_interior_product",
    "Transwedge": "transwedge",
    "TranswedgeAntiproduct": "transwedge_antiproduct",
    "Div": "geometric_product",
    "Regressive": "regressive_product",
    "Add": "add",
    "Sub": "subtract",
    "Grade": "grade",
    "Norm": "norm",
    "Unit": "unit",
    "Exp": "exp",
    "Even": "even_grades",
    "Odd": "odd_grades",
    "Commutator": "commutator",
    "Anticommutator": "anticommutator",
    "LieBracket": "lie_bracket",
    "JordanProduct": "jordan_product",
    "MetricApply": "metric_apply",
    "AntimetricApply": "antimetric_apply",
    "BulkPart": "bulk_part",
    "WeightPart": "weight_part",
    "RightHodgeDual": "right_hodge_dual",
    "LeftHodgeDual": "left_hodge_dual",
    "RightWeightDual": "right_weight_dual",
    "LeftWeightDual": "left_weight_dual",
    "Antireverse": "antireverse",
}

# Reviewed v2 output in target order: ASCII, Unicode, LaTeX.
DEFAULT_RENDERINGS = {
    "Reverse": ("~a", "ã", "\\widetilde{a}"),
    "Involute": ("hat(a)", "â", "\\widehat{a}"),
    "Conjugate": ("bar(a)", "a̅", "\\overline{a}"),
    "Dual": ("a^*", "a^★", "a^*"),
    "Undual": ("a^*^-1", "a^(★⁻¹)", "a^{*^{-1}}"),
    "Inverse": ("a^-1", "a⁻¹", "a^{-1}"),
    "Squared": ("a^2", "a²", "a^2"),
    "Neg": ("-a", "-a", "-a"),
    "ScalarMul": ("2a", "2a", "2 a"),
    "ScalarDiv": ("a / 2", "a / 2", "\\frac{a}{2}"),
    "Gp": ("ab", "ab", "a b"),
    "Op": ("a ^ b", "a ∧ b", "a \\wedge b"),
    "Lc": ("a _| b", "a ⌋ b", "a \\mathbin{\\rfloor} b"),
    "Rc": ("a |_ b", "a ⌊ b", "a \\mathbin{\\lfloor} b"),
    "Hi": ("hestenes_inner(a, b)", "hestenes_inner(a, b)", "a \\cdot b"),
    "Dli": ("a | b", "a · b", "a \\cdot b"),
    "Sp": ("a * b", "a * b", "a * b"),
    "MetricInnerProduct": (
        "metric_inner_product(a, b)",
        "metric_inner_product(a, b)",
        "\\operatorname{metric\\_inner\\_product}(a,\\, b)",
    ),
    "AntidotProduct": ("antidot_product(a, b)", "antidot_product(a, b)", "\\operatorname{antidot\\_product}(a,\\, b)"),
    "GeometricAntiproduct": (
        "geometric_antiproduct(a, b)",
        "geometric_antiproduct(a, b)",
        "\\operatorname{geometric\\_antiproduct}(a,\\, b)",
    ),
    "LeftInteriorProduct": (
        "left_interior_product(a, b)",
        "left_interior_product(a, b)",
        "\\operatorname{left\\_interior\\_product}(a,\\, b)",
    ),
    "RightInteriorProduct": (
        "right_interior_product(a, b)",
        "right_interior_product(a, b)",
        "\\operatorname{right\\_interior\\_product}(a,\\, b)",
    ),
    "Transwedge": ("transwedge(a, b, 1)", "transwedge(a, b, 1)", "\\operatorname{transwedge}(a,\\, b,\\, 1)"),
    "TranswedgeAntiproduct": (
        "transwedge_antiproduct(a, b, 1)",
        "transwedge_antiproduct(a, b, 1)",
        "\\operatorname{transwedge\\_antiproduct}(a,\\, b,\\, 1)",
    ),
    "Div": ("ab^-1", "ab⁻¹", "a b^{-1}"),
    "Regressive": ("a vee b", "a ∨ b", "a \\vee b"),
    "Add": ("a + b", "a + b", "a + b"),
    "Sub": ("a - b", "a - b", "a - b"),
    "Grade": ("<a>[1]", "⟨a⟩₁", "\\langle a \\rangle_{1}"),
    "Norm": ("||a||", "‖a‖", "\\lVert a \\rVert"),
    "Unit": ("hat(a)", "â", "\\widehat{a}"),
    "Exp": ("exp(a)", "exp(a)", "e^{a}"),
    "Even": ("<a>even", "⟨a⟩₊", "\\langle a \\rangle_{\\text{even}}"),
    "Odd": ("<a>odd", "⟨a⟩₋", "\\langle a \\rangle_{\\text{odd}}"),
    "Commutator": ("[a, b]", "[a, b]", "[a,\\, b]"),
    "Anticommutator": ("{a, b}", "{a, b}", "\\{a,\\, b\\}"),
    "LieBracket": ("[a, b]", "[a, b]", "[a,\\, b]"),
    "JordanProduct": ("{a, b}", "{a, b}", "\\{a,\\, b\\}"),
    "MetricApply": ("metric_apply(a)", "metric_apply(a)", "\\operatorname{metric\\_apply}(a)"),
    "AntimetricApply": ("antimetric_apply(a)", "antimetric_apply(a)", "\\operatorname{antimetric\\_apply}(a)"),
    "BulkPart": ("bulk_part(a)", "bulk_part(a)", "\\operatorname{bulk\\_part}(a)"),
    "WeightPart": ("weight_part(a)", "weight_part(a)", "\\operatorname{weight\\_part}(a)"),
    "RightHodgeDual": ("right_hodge_dual(a)", "right_hodge_dual(a)", "\\operatorname{right\\_hodge\\_dual}(a)"),
    "LeftHodgeDual": ("left_hodge_dual(a)", "left_hodge_dual(a)", "\\operatorname{left\\_hodge\\_dual}(a)"),
    "RightWeightDual": ("right_weight_dual(a)", "right_weight_dual(a)", "\\operatorname{right\\_weight\\_dual}(a)"),
    "LeftWeightDual": ("left_weight_dual(a)", "left_weight_dual(a)", "\\operatorname{left\\_weight\\_dual}(a)"),
    "Antireverse": ("antireverse(a)", "antireverse(a)", "\\operatorname{antireverse}(a)"),
}

RECIPES = {
    "geometric_product": lambda a, b, s: a * b,
    "outer_product": lambda a, b, s: a ^ b,
    "doran_lasenby_inner": lambda a, b, s: a | b,
    "left_contraction": lambda a, b, s: ga.left_contraction(a, b),
    "right_contraction": lambda a, b, s: ga.right_contraction(a, b),
    "hestenes_inner": lambda a, b, s: ga.hestenes_inner(a, b),
    "scalar_product": lambda a, b, s: ga.scalar_product(a, b),
    "commutator": lambda a, b, s: ga.commutator(a, b),
    "anticommutator": lambda a, b, s: ga.anticommutator(a, b),
    "lie_bracket": lambda a, b, s: ga.lie_bracket(a, b),
    "jordan_product": lambda a, b, s: ga.jordan_product(a, b),
    "reverse": lambda a, b, s: ga.reverse(a),
    "grade_involution": lambda a, b, s: ga.grade_involution(a),
    "conjugate": lambda a, b, s: ga.conjugate(a),
    "dual": lambda a, b, s: ga.dual(a),
    "undual": lambda a, b, s: ga.undual(a),
    "complement": lambda a, b, s: ga.complement(a),
    "inverse": lambda a, b, s: ga.inverse(a),
    "squared": lambda a, b, s: ga.squared(a),
    "norm": lambda a, b, s: ga.norm(a),
    "unit": lambda a, b, s: ga.unit(a),
    "exp": lambda a, b, s: ga.exp(a ^ b),
    "scalar_sqrt": lambda a, b, s: ga.scalar_sqrt(s),
    "grade": lambda a, b, s: ga.grade(a * b, 1),
    "even_grades": lambda a, b, s: ga.even_grades(a),
    "odd_grades": lambda a, b, s: ga.odd_grades(a),
    "nested": lambda a, b, s: ga.grade(a * ga.reverse(b), 1),
}

FUNCTIONAL_LATEX = {
    "geometric_product": "\\operatorname{geometric\\_product}\\left(a, b\\right)",
    "outer_product": "\\operatorname{outer\\_product}\\left(a, b\\right)",
    "doran_lasenby_inner": "\\operatorname{doran\\_lasenby\\_inner}\\left(a, b\\right)",
    "left_contraction": "\\operatorname{left\\_contraction}\\left(a, b\\right)",
    "right_contraction": "\\operatorname{right\\_contraction}\\left(a, b\\right)",
    "hestenes_inner": "\\operatorname{hestenes\\_inner}\\left(a, b\\right)",
    "scalar_product": "\\operatorname{scalar\\_product}\\left(a, b\\right)",
    "commutator": "\\operatorname{commutator}\\left(a, b\\right)",
    "anticommutator": "\\operatorname{anticommutator}\\left(a, b\\right)",
    "lie_bracket": "\\operatorname{lie\\_bracket}\\left(a, b\\right)",
    "jordan_product": "\\operatorname{jordan\\_product}\\left(a, b\\right)",
    "reverse": "\\operatorname{reverse}\\left(a\\right)",
    "grade_involution": "\\operatorname{grade\\_involution}\\left(a\\right)",
    "conjugate": "\\operatorname{conjugate}\\left(a\\right)",
    "dual": "\\operatorname{dual}\\left(a\\right)",
    "undual": "\\operatorname{undual}\\left(a\\right)",
    "complement": "\\operatorname{complement}\\left(a\\right)",
    "inverse": "\\operatorname{inverse}\\left(a\\right)",
    "squared": "\\operatorname{squared}\\left(a\\right)",
    "norm": "\\operatorname{norm}\\left(a\\right)",
    "unit": "\\operatorname{unit}\\left(a\\right)",
    "exp": "\\operatorname{exp}\\left(\\operatorname{outer\\_product}\\left(a, b\\right)\\right)",
    "scalar_sqrt": "\\operatorname{scalar\\_sqrt}\\left(s\\right)",
    "grade": "\\operatorname{grade}\\left(\\operatorname{geometric\\_product}\\left(a, b\\right), 1\\right)",
    "even_grades": "\\operatorname{even\\_grades}\\left(a\\right)",
    "odd_grades": "\\operatorname{odd\\_grades}\\left(a\\right)",
    "nested": "\\operatorname{grade}\\left(\\operatorname{geometric\\_product}\\left(a, \\operatorname{reverse}\\left(b\\right)\\right), 1\\right)",
}


def _default_expression(old_node):
    operation_id = OLD_NODE_OPERATIONS[old_node]
    if old_node == "Div":
        return Call("geometric_product", (Symbol("a"), Call("inverse", (Symbol("b"),))))
    spec = ga.get_operation(operation_id)
    operands = tuple(Symbol(name) for name in "ab"[: spec.expression_arity])
    parameters = {
        parameter.name: {"scalar": 2, "target": 1, "order": 1}[parameter.name]
        for parameter in spec.parameters
        if parameter.required
    }
    return Call(operation_id, operands, parameters)


def _context(notation):
    algebra = ga.Algebra(3, notation=notation)
    a, b, _ = (value.named(name) for value, name in zip(algebra.basis_vectors(), "abc", strict=True))
    return algebra, a, b, algebra.scalar(2).named("s")


def _assert_coefficients(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape, "coefficient shape changed"
    assert np.isfinite(actual).all() and np.isfinite(expected).all(), "nonfinite coefficients"
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)


@pytest.mark.parametrize("old_node", OLD_NODE_OPERATIONS)
@pytest.mark.parametrize("index, target", tuple(enumerate(TARGETS)))
def test_default_notation_retains_reviewed_output_for_every_historical_node(old_node, index, target):
    expression = _default_expression(old_node)
    assert (
        ga.render(expression, target=target, presentation=ga.Algebra(3).presentation)
        == DEFAULT_RENDERINGS[old_node][index]
    )
    assert expression == _default_expression(old_node)


@pytest.mark.parametrize("case_id", RECIPES)
@pytest.mark.parametrize("target", TARGETS)
def test_functional_notation_preserves_history_replay_and_canonical_operation_names(case_id, target):
    algebra, a, b, s = _context(ga.Notation.functional())
    result = RECIPES[case_id](a, b, s)
    expression, data, before_hash = result.expr, result.data.copy(), hash(result)
    history = ARCHIVE["functional_values"][case_id]
    # V2 deliberately uses unscaled Lie/Jordan products (ADR-099).
    scale = 2 if case_id in {"lie_bracket", "jordan_product"} else 1
    expected = scale * np.asarray(history["coefficients"])
    _assert_coefficients(data, expected)
    _assert_coefficients(evaluate(expression, algebra=algebra, environment={"a": a, "b": b, "s": s}).data, expected)
    text = "grade_involution(a)" if case_id == "grade_involution" else history["unicode"]
    expected_text = FUNCTIONAL_LATEX[case_id] if target == "latex" else text
    assert result.display(f"expr/{target}") == expected_text
    assert result.expr is expression and hash(result) == before_hash
    np.testing.assert_array_equal(result.data, data)


def test_log_symbol_can_render_without_accepting_the_legacy_vector_logarithm():
    algebra, a, _, _ = _context(ga.Notation.functional())
    expression = Call("log", (Symbol("a"),))
    assert (
        ga.render(expression, target="unicode", presentation=algebra.presentation)
        == ARCHIVE["functional_values"]["log"]["unicode"]
    )
    assert (
        ga.render(expression, target="latex", presentation=algebra.presentation) == r"\operatorname{log}\left(a\right)"
    )
    with pytest.raises(ValueError, match="principal real"):
        ga.log(a)
    with pytest.raises(ValueError, match="principal real"):
        evaluate(expression, algebra=algebra, environment={"a": a})
    # The old pi/2 times a result is not a logarithm of this positive-square
    # vector: exponentiating it fails the defining round-trip identity.
    legacy_log = algebra.multivector(ARCHIVE["functional_values"]["log"]["coefficients"])
    assert not ga.exp(legacy_log).almost_equal(a)


@pytest.mark.parametrize("target", TARGETS)
def test_log_of_a_valid_rotor_retains_functional_notation_and_numeric_meaning(target):
    algebra, a, b, _ = _context(ga.Notation.functional())
    bivector = a.unnamed() ^ b.unnamed()
    assert float(bivector * bivector) == -np.linalg.det(algebra.gram[:2, :2])
    rotor = (np.cos(0.4) + np.sin(0.4) * bivector).named("R")
    result = ga.log(rotor)
    _assert_coefficients(result.data, 0.4 * bivector.data)
    _assert_coefficients(evaluate(result.expr, algebra=algebra, environment={"R": rotor}).data, result.data)
    expected = r"\operatorname{log}\left(R\right)" if target == "latex" else "log(R)"
    assert result.display(f"expr/{target}") == expected


@pytest.mark.parametrize(
    "preset, expected",
    (
        (ga.Notation.default, ("~a", "ã", r"\widetilde{a}")),
        (ga.Notation.doran_lasenby, ("~a", "ã", r"\widetilde{a}")),
        (ga.Notation.hestenes, ("adag", "a†", r"a^{\dagger}")),
    ),
)
@pytest.mark.parametrize("index, target", tuple(enumerate(TARGETS)))
def test_reverse_presets_apply_to_actual_algebra_rendering_in_every_target(preset, expected, index, target):
    algebra, a, _, _ = _context(preset())
    result = ga.reverse(a)
    assert result.display(f"expr/{target}") == expected[index]
    assert result.expr == Call("reverse", (Symbol("a"),))
    _assert_coefficients(result.data, a.data)
    assert algebra.numeric is a.numeric.algebra


@pytest.mark.parametrize(
    "kind, symbol, expected",
    (
        ("postfix", "†", "a†"),
        ("prefix", "*", "*a"),
        ("function", "rev", "rev(a)"),
    ),
)
def test_target_local_reverse_overrides_take_priority_without_mutation(kind, symbol, expected):
    base = ga.Notation.default()
    rule = ga.RenderRule(kind, symbol=symbol)
    custom = base.with_rule("reverse", rule, target="unicode")
    _, a, _, _ = _context(base)
    value = ga.reverse(a)
    assert value.display("expr/unicode", notation=custom) == expected
    assert value.display("expr/latex", notation=custom) == r"\widetilde{a}"
    assert custom.rule("reverse", "unicode") is rule
    assert base == ga.Notation.default() and custom is not base
    with pytest.raises(FrozenInstanceError):
        rule.kind = "function"
    with pytest.raises(FrozenInstanceError):
        custom.rules = ()


def test_generic_rule_replacement_preserves_target_specific_override_precedence():
    base = ga.Notation.default()
    generic = ga.RenderRule("function", symbol="rev")
    custom = base.with_rule("reverse", generic)
    assert custom.rule("reverse", "unicode") is generic
    assert custom.rule("reverse", "latex") == base.rule("reverse", "latex")
    overridden = custom.with_rule("reverse", generic, target="latex")
    assert overridden.rule("reverse", "latex") is generic
    assert base == ga.Notation.default()


def test_chained_overrides_and_input_containers_are_independently_immutable():
    rules = {"reverse": ga.RenderRule("function", symbol="rev")}
    base = ga.Notation("custom", rules=rules)
    custom = base.with_rule("dual", ga.RenderRule("prefix", symbol="*")).with_rule(
        "geometric_product", ga.RenderRule("infix", symbol="@", associativity="left")
    )
    rules.clear()
    assert base.rule("reverse").symbol == ga.Name("rev")
    assert base.rule("dual") is None
    assert custom.rule("dual").symbol == ga.Name("*")
    assert custom.rule("geometric_product").symbol == ga.Name("@")
    assert hash(base) == hash(ga.Notation("custom", rules={"reverse": ga.RenderRule("function", symbol="rev")}))


@pytest.mark.parametrize(
    "target, expected",
    (
        ("ascii", "wedge(a, b)"),
        ("unicode", "wedge(a, b)"),
        ("latex", r"\operatorname{wedge}\left(a, b\right)"),
    ),
)
def test_binary_function_override_uses_the_public_operation_id(target, expected):
    notation = ga.Notation.default().with_rule(
        "outer_product", ga.RenderRule("function", symbol="wedge"), target=target
    )
    _, a, b, _ = _context(notation)
    result = a ^ b
    assert result.display(f"expr/{target}") == expected
    assert result.expr == Call("outer_product", (Symbol("a"), Symbol("b")))


@pytest.mark.parametrize("target", TARGETS)
def test_infix_product_override_preserves_values_and_explicit_replay(target):
    notation = ga.Notation.default().with_rule("geometric_product", ga.RenderRule("infix", symbol="@"), target=target)
    algebra, a, b, _ = _context(notation)
    result = a * b
    expected = algebra.numeric.left_action(a.numeric) @ b.data
    _assert_coefficients(result.data, expected)
    assert result.display(f"expr/{target}") == "a @ b"
    _assert_coefficients(evaluate(result.expr, algebra=algebra, environment={"a": a, "b": b}).data, expected)


@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize(
    "operation, short, arity",
    (
        ("geometric_product", "gp", 2),
        ("outer_product", "op", 2),
        ("left_contraction", "lc", 2),
        ("reverse", "rev", 1),
        ("grade_involution", "invol", 1),
        ("doran_lasenby_inner", "dl_inner", 2),
        ("hestenes_inner", "h_inner", 2),
    ),
)
def test_short_functional_preset_has_explicit_unambiguous_spelling(operation, short, arity, target):
    expression = Call(operation, tuple(Symbol(name) for name in "ab"[:arity]))
    arguments = "a, b" if arity == 2 else "a"
    expected = f"{short}({arguments})"
    if target == "latex":
        escaped = short.replace("_", r"\_")
        expected = rf"\operatorname{{{escaped}}}\left({arguments}\right)"
    for notation in (ga.Notation.functional(short=True), ga.Notation.functional_short()):
        assert (
            ga.render(expression, target=target, presentation=ga.Algebra(3).presentation.with_notation(notation))
            == expected
        )


def test_unknown_rule_metadata_does_not_register_an_operation_or_silently_render_it():
    notation = ga.Notation("extension", rules={"custom": ga.RenderRule("function", symbol="custom")})
    assert notation.rule("custom").symbol == ga.Name("custom")
    assert notation.rule("missing") is None
    with pytest.raises(ValueError, match="unknown expression operation"):
        ga.render(
            Call("custom", (Symbol("a"),)),
            target="unicode",
            presentation=ga.Algebra(1).presentation.with_notation(notation),
        )


@pytest.mark.parametrize(
    "factory, error, message",
    (
        (
            lambda: ga.Notation.default().with_rule(
                "reverse", ga.RenderRule("function", symbol="rev"), target="klingon"
            ),
            ValueError,
            "target",
        ),
        (lambda: ga.Notation.default().rule("reverse", "klingon"), ValueError, "target"),
        (lambda: ga.RenderRule("banana", symbol="!"), ValueError, "kind"),
        (lambda: ga.Notation("bad", rules={"reverse": "not a rule"}), TypeError, "RenderRule"),
    ),
)
def test_invalid_notation_configuration_fails_at_construction(factory, error, message):
    with pytest.raises(error, match=message):
        factory()


def test_scientific_number_formatting_has_an_explicit_current_boundary():
    notation = ga.Notation.default()
    algebra = ga.Algebra(1, notation=notation)
    assert algebra.scalar(ARCHIVE["scientific_input"]).latex() == ARCHIVE["scientific_styles"]["times"]
    assert len(set(ARCHIVE["scientific_styles"].values())) == 3
    # Scientific styling belongs to the numeric emitter, not operation rules.
    # V2 currently has no cdot/raw style switch; do not claim parity with v1.
    assert not hasattr(notation, "with_scientific") and not hasattr(notation, "scientific")
    with pytest.raises(TypeError):
        ga.Notation(scientific="cdot")
