"""Curated unary properties share canonical dispatch, values, and provenance."""

from __future__ import annotations

import numpy as np
import pytest

import galaga as ga
from galaga.expression import Call, Symbol, evaluate
from galaga.facade import _numeric

CONVENIENCES = {"bar": "grade_involution", "dag": "reverse", "inv": "inverse", "sq": "squared"}


@pytest.mark.parametrize("member, operation", tuple(CONVENIENCES.items()))
@pytest.mark.parametrize(
    "gram",
    (((1, 0), (0, 1)), ((1, 0), (0, 0)), ((2, 0.5), (0.5, -1)), ((0, -1), (-1, 0))),
    ids=("euclidean", "degenerate", "oblique", "native-null"),
)
@pytest.mark.parametrize("named, tracked", ((False, False), (True, False), (False, True), (True, True)))
def test_unary_properties_match_independent_algebra_and_preserve_metadata(
    member, operation, gram, named, tracked
) -> None:
    algebra = ga.Algebra(gram=gram)
    value = algebra.multivector([2, 0.1, -0.2, 0.05], name="X" if named else None, expr=tracked)
    data_before, expression_before, name_before, hash_before = value.data.copy(), value.expr, value.name, hash(value)
    grades = np.array([mask.bit_count() for mask in range(algebra.dim)])
    action = algebra.numeric.left_action(value.numeric)
    expected = {
        "bar": data_before * (-1.0) ** grades,
        "dag": data_before * (-1.0) ** (grades * (grades - 1) // 2),
        "sq": action @ data_before,
        "inv": np.linalg.solve(action, algebra.identity.data),
    }[member]

    result = getattr(value, member)

    assert isinstance(result, ga.Multivector) and result.algebra is algebra
    assert result.data.shape == expected.shape and np.isfinite(result.data).all()
    np.testing.assert_allclose(result.data, expected, rtol=0, atol=1e-12)
    assert result.name is None
    if named or tracked:
        operand = Symbol("X") if named else value.expr
        assert result.expr == Call(operation, (operand,))
        replayed = evaluate(result.expr, algebra=algebra, environment={"X": value})
        np.testing.assert_allclose(replayed.data, expected, rtol=0, atol=1e-12)
    else:
        assert result.expr is None
    assert value.expr is expression_before and value.name is name_before
    assert hash(value) == hash_before
    np.testing.assert_array_equal(value.data, data_before)
    assert not result.data.flags.writeable


@pytest.mark.parametrize("member, operation", tuple(CONVENIENCES.items()))
def test_unary_properties_delegate_once_to_the_canonical_function(member, operation, monkeypatch) -> None:
    value = ga.Algebra(3).blade(3).named("B")
    expected = getattr(ga, operation)(value)
    calls = []

    def record(operand):
        calls.append(operand)
        return expected

    monkeypatch.setattr(_numeric, operation, record)
    assert getattr(value, member) is expected
    assert len(calls) == 1 and calls[0] is value


@pytest.mark.parametrize("member", tuple(CONVENIENCES))
def test_unary_properties_are_read_only(member) -> None:
    descriptor = getattr(ga.Multivector, member)
    assert isinstance(descriptor, property) and descriptor.fset is None
    value = ga.Algebra(1).blade(1)
    with pytest.raises(AttributeError):
        setattr(value, member, value)
    with pytest.raises(AttributeError):
        delattr(value, member)


@pytest.mark.parametrize("kind", ("zero", "null-vector"))
@pytest.mark.parametrize("tracked", (False, True))
def test_inverse_property_preserves_the_canonical_singular_domain_error(kind, tracked) -> None:
    algebra = ga.Algebra(gram=((0, 0), (0, 1)))
    value = (algebra.scalar(0) if kind == "zero" else algebra.blade(1)).named("x")
    if tracked:
        value = value.with_expr()
    expression_before = value.expr
    with pytest.raises(ValueError) as canonical:
        ga.inverse(value)
    with pytest.raises(ValueError) as shorthand:
        _ = value.inv
    assert str(shorthand.value) == str(canonical.value)
    assert value.expr is expression_before


def test_bar_means_grade_involution_not_clifford_conjugation() -> None:
    algebra = ga.Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    value = (1 + e1 + (e1 ^ e2)).named("X")
    # Odd grades change under involution; grade 2 changes under reverse.
    assert value.bar == 1 - e1 + (e1 ^ e2)
    assert value.dag == 1 + e1 - (e1 ^ e2)
    assert ga.conjugate(value) == 1 - e1 - (e1 ^ e2)
    assert value.bar != ga.conjugate(value)
    assert value.bar.expr.operation_id == "grade_involution"


def test_unary_properties_render_canonical_operation_ids() -> None:
    value = ga.Algebra(3).blade(3).named("B")
    assert value.dag.display("expr/latex") == r"\widetilde{B}"
    assert value.inv.display("expr/latex") == r"B^{-1}"
    assert value.sq.display("expr/latex") == r"B^2"
    assert value.bar.display("expr/ascii", notation=ga.Notation.functional()) == "grade_involution(B)"
