"""Archived factory/display edges with coefficient-first public owners."""

import json
import runpy
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
from galaga.expression import BladeLiteral, ScalarLiteral, evaluate

TEST_ROOT = Path(__file__).parents[1]
ARCHIVE = json.loads((TEST_ROOT.parent / "tools/baselines/factory-display-edges-v1.json").read_text())
SOURCE = runpy.run_path(str(TEST_ROOT / "test_coverage_gaps.py"))
TARGETS = ("ascii", "unicode", "latex")


def assert_data(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape
    assert np.isfinite(actual).all() and np.isfinite(expected).all()
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)


def check_value(value, expected, target, environment=None):
    assert_data(value.data, expected)
    expression, value_hash = value.expr, hash(value)
    assert value.display("full/" + target)
    assert_data(value.data, expected)
    assert value.expr is expression and hash(value) == value_hash
    if expression is not None:
        assert_data(evaluate(expression, algebra=value.algebra, environment=environment).data, expected)


def exterior_basis(algebra, mask, expr=False):
    value = algebra.scalar(1, expr=expr)
    for index, vector in enumerate(algebra.basis_vectors(expr=expr)):
        if mask & (1 << index):
            value = value ^ vector
    return value


@pytest.mark.parametrize("row", ARCHIVE["lookups"], ids=lambda row: row["id"])
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("target", TARGETS)
def test_archived_lookup_values_have_explicit_public_replacements(row, expr, target):
    if row["id"] == "display_name":
        algebra = ga.Algebra(config=ga.p_sta(sigmas=True))
        g0, g1, _, _ = algebra.basis_vectors()
        value = algebra.blade("σ₁", expr=expr)
        expected = (g1 * g0).data
        assert_data(algebra.blade("g0g1").data, row["data"])  # Old lookup ignored label orientation.
        assert_data(expected, -np.asarray(row["data"]))
        assert value.display("value/unicode") == "σ₁"
    else:
        algebra = ga.Algebra(row["signature"])
        mask = 0 if row["id"] in {"empty", "scalar"} else 3
        value = algebra.blade(exterior_basis(algebra, mask), expr=expr)
        expected = row["data"]
        if row["id"] in {"metric_role", "empty"}:
            with pytest.raises(KeyError, match="unknown blade"):
                algebra.blade("+1+2" if row["id"] == "metric_role" else "")
    check_value(value, expected, target)
    assert (value.expr is not None) == expr


@pytest.mark.parametrize("table", ARCHIVE["pseudoscalar_tables"], ids=lambda row: row["id"])
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("target", TARGETS)
def test_complete_named_pseudoscalar_basis_tables_preserve_exterior_coefficients(table, expr, target):
    convention = SOURCE["pss_convention"](table["id"])
    algebra = ga.Algebra(table["signature"], blades=convention)
    assert [row["mask"] for row in table["basis"]] == list(range(algebra.dim))
    for row in table["basis"]:
        value = algebra.blade(row["mask"], expr=expr)
        assert_data(value.data, exterior_basis(algebra, row["mask"]).data)
        check_value(value, row["data"], target)
        assert value.unicode() == row["unicode"]
        expected_latex = row["latex"]
        if table["id"] == "sigma_xyz":
            for subscript in "xyz":
                expected_latex = expected_latex.replace(r"\sigma_" + subscript, rf"\sigma_{{{subscript}}}")
        assert value.latex(content="value") == expected_latex
    volume = algebra.pseudoscalar(expr=expr)
    expected_square = (-1) ** (algebra.n * (algebra.n - 1) // 2) * np.linalg.det(algebra.gram)
    assert float(volume * volume) == pytest.approx(expected_square, rel=0, abs=1e-12)
    assert algebra.blade("I") == volume


def factory_values(algebra, factory, expr):
    if factory == "basis_vectors":
        return algebra.basis_vectors(expr=expr)
    if factory == "basis_blades":
        return algebra.basis_blades(2, expr=expr)
    if factory == "locals":
        return tuple(algebra.locals(expr=expr).values())
    if factory == "pseudoscalar":
        return (algebra.pseudoscalar(expr=expr),)
    assert factory == "blade"
    return (algebra.blade("e1", expr=expr),)


@pytest.mark.parametrize("row", ARCHIVE["factories"], ids=lambda row: f"{row['id']}-{row['symbolic']}")
@pytest.mark.parametrize("target", TARGETS)
def test_archived_symbolic_factories_migrate_to_explicit_expr_flags(row, target):
    algebra = ga.Algebra(3)
    values = factory_values(algebra, row["id"], row["symbolic"])
    # V1 iterated in presentation order; v2 uses native masks. Match by value.
    archived = {tuple(value["data"]): value for value in row["values"]}
    assert len(values) == len(archived)
    for value in values:
        expected = archived[tuple(value.data)]
        check_value(value, expected["data"], target, algebra.locals(expr=True))
        assert (value.expr is not None) == row["symbolic"]
    if row["id"] == "locals":
        assert set(algebra.locals()) == set(row["keys"])


def expected_vector(coordinates, target):
    """The archived display examples use positive vector coefficients only."""
    labels = {"ascii": ("e1", "e2", "e3"), "unicode": ("e₁", "e₂", "e₃"), "latex": ("e_{1}", "e_{2}", "e_{3}")}
    terms = []
    for coefficient, label in zip(coordinates, labels[target], strict=True):
        if coefficient == 0:
            continue
        assert coefficient > 0
        prefix = "" if coefficient == 1 else format(coefficient, ".6g") + (" " if target == "latex" else "")
        terms.append(prefix + label)
    return " + ".join(terms)


@pytest.mark.parametrize("row", ARCHIVE["displays"], ids=lambda row: row["id"])
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("target", TARGETS)
def test_archived_display_values_keep_explicit_content_targets_and_wrapping(row, expr, target):
    algebra = ga.Algebra(3, display=ga.DisplayPolicy(content="full", target=target))
    value = algebra.vector(row["coordinates"], expr=expr)
    if row["named"]:
        value = value.named("v")
    body = expected_vector(row["coordinates"], target)
    expected = (("v" + (r" \quad = \quad " if target == "latex" else " = ")) if row["named"] else "") + body
    check_value(value, row["data"], target)
    snapshot = value.display()
    assert type(snapshot) is str and snapshot == expected
    assert str(value) == expected
    assert repr(value) == (("v = " if row["named"] else "") + expected_vector(row["coordinates"], "ascii"))
    assert value.latex(content="full") == row["display_str"]
    assert value._repr_latex_() == "$" + row["display_str"] + "$"
    assert value.latex(wrap="$") == value._repr_latex_()
    assert value.latex(wrap="$$") == "$$\n" + row["display_str"] + "\n$$"
    # Request the old name-only default explicitly; wrapping never bypasses content.
    if row["named"]:
        assert value.latex(content="name", wrap="$") == "$v$"
    assert row["display_type"] == "_DisplayResult"
    assert row["display_repr_text"] == row["display_str"]  # Old object repr was unquoted LaTeX.
    with pytest.raises(ValueError, match="format code"):
        format(snapshot, ".2f")


@pytest.mark.parametrize("gram", (((1, 0), (0, 1)), ((2, 0.5), (0.5, -1)), ((1, 0), (0, 0))))
@pytest.mark.parametrize("target", TARGETS)
def test_rendered_strings_are_snapshots_while_new_calls_observe_scoped_policy(gram, target):
    algebra = ga.Algebra(gram=gram)
    x_coordinates, y_coordinates = np.array([2, 1]), np.array([-1, 3])
    x, y = (
        algebra.vector(coordinates, expr=True).named(name)
        for coordinates, name in ((x_coordinates, "x"), (y_coordinates, "y"))
    )
    value = (x * y).named("M")
    pairing = float(x_coordinates @ np.asarray(gram) @ y_coordinates)
    area = float(np.linalg.det(np.column_stack((x_coordinates, y_coordinates))))
    expected = [pairing, 0, 0, area]
    check_value(value, expected, target, {"x": x, "y": y})
    before = value.display("full/" + target)
    assert type(before) is str
    function_spelling = r"geometric\_product" if target == "latex" else "geometric_product"
    functional = algebra.presentation.with_notation(ga.Notation.functional())
    with pytest.raises(RuntimeError, match="leave scope"):
        with algebra.use_presentation(functional):
            during = value.display("full/" + target)
            assert type(during) is str and function_spelling in during
            assert before != during
            name_only = functional.with_display(ga.DisplayPolicy(content="name"))
            with algebra.use_presentation(name_only):
                assert value.display(target=target) == "M"
                assert value.display("full/" + target) == during
            assert value.display("full/" + target) == during
            raise RuntimeError("leave scope")
    assert value.display("full/" + target) == before
    assert function_spelling in during and function_spelling not in before
    check_value(value, expected, target, {"x": x, "y": y})


@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("mask", (0, 1, 3))
@pytest.mark.parametrize("sign", (-1, 1))
def test_signed_blade_literalization_drops_names_and_preserves_values(mask, sign, expr):
    algebra = ga.Algebra(2)
    value = (sign * exterior_basis(algebra, mask, True)).named("B")
    literal = algebra.blade(value, expr=expr)
    np.testing.assert_array_equal(literal.data, value.data)
    assert literal.name is None
    if expr:
        assert literal.expr == (ScalarLiteral(sign) if mask == 0 else BladeLiteral(mask, sign))
        assert evaluate(literal.expr, algebra=algebra) == value
    else:
        assert literal.expr is None
    np.testing.assert_array_equal(value.data, sign * np.eye(algebra.dim)[mask])


@pytest.mark.parametrize("factory", ("basis_vectors", "basis_blades", "locals", "pseudoscalar", "blade"))
@pytest.mark.parametrize("flag", ("lazy", "symbolic"))
def test_retired_factory_flags_are_rejected_even_when_false(factory, flag):
    algebra = ga.Algebra(3)
    args = (2,) if factory == "basis_blades" else ("e1",) if factory == "blade" else ()
    with pytest.raises(TypeError, match=flag):
        getattr(algebra, factory)(*args, **{flag: False})


@pytest.mark.parametrize("gram", (np.eye(3), ((2, 0.5, 0), (0.5, -1, 0), (0, 0, 3)), np.diag((1, 1, 0))))
@pytest.mark.parametrize("swap", (False, True))
@pytest.mark.parametrize("target", TARGETS)
def test_pseudoscalar_labels_preserve_computed_orientation_and_gram_determinants(gram, swap, target):
    algebra = ga.Algebra(gram=gram)
    vectors = list(algebra.basis_vectors())
    if swap:
        vectors[0], vectors[1] = vectors[1], vectors[0]
    volume = algebra.scalar(1)
    for vector in vectors:
        volume = volume ^ vector
    (mask,) = np.flatnonzero(volume.data)
    ref = ga.BladeRef(int(mask), int(volume.data[mask]))
    convention = ga.indexed_blade_convention(
        algebra.n,
        overrides={int(mask): ga.BladeLabel(ga.Name("I"), ref)},
        aliases={"volume": ref},
        roles={"oriented_volume": ref},
    )
    view = algebra.with_blades(convention)
    assert view.numeric is algebra.numeric
    named = view.blade("I", expr=True)
    check_value(named, volume.data, target)
    assert named.display("value/" + target) == "I"
    assert view.blade("volume") == view.blade("oriented_volume") == named
    assert view.blade(int(mask)) == ref.orientation * named
    assert algebra.blade(int(mask)) == view.pseudoscalar()
    expected_square = (-1) ** (algebra.n * (algebra.n - 1) // 2) * np.linalg.det(gram)
    assert float(named * named) == pytest.approx(expected_square, rel=0, abs=1e-12)
    if expected_square == 0:
        with pytest.raises(ValueError, match="not invertible"):
            ga.inverse(named)
