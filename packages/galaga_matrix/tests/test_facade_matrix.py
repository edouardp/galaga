"""Galaga 2 facade contracts for numeric matrix representations."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest
from galaga_matrix import from_matrix, to_matrix
from galaga_matrix.matrix import (
    _compact_metric_supported,
    _gram_matrix,
    _left_regular_matrix,
    _metric_inertia,
    _representation_plan,
    compact_basis,
)

from galaga.facade import Algebra, Multivector, geometric_product

GENERAL_GRAM_METRICS = (
    np.array([[2.0, 0.5], [0.5, -1.0]]),
    np.array([[0.0, -1.0], [-1.0, 0.0]]),
)


@pytest.mark.parametrize("gram", GENERAL_GRAM_METRICS)
def test_left_regular_facade_matrix_reproduces_geometric_product(gram: np.ndarray) -> None:
    algebra = Algebra(gram=gram)
    left = algebra.multivector(np.array([1.5, -2.0, 0.75, 3.0]))
    right = algebra.multivector(np.array([-1.0, 0.5, 2.0, -0.25]))

    matrix = to_matrix(left, mode="left-regular")

    np.testing.assert_allclose(
        np.asarray(matrix) @ right.data,
        geometric_product(left, right).data,
        rtol=0.0,
        atol=1e-12,
    )
    assert matrix.algebra is algebra
    assert matrix.mode == "left-regular"


@pytest.mark.parametrize("gram", GENERAL_GRAM_METRICS)
def test_general_gram_left_regular_roundtrip_preserves_facade_coefficients(gram: np.ndarray) -> None:
    algebra = Algebra(gram=gram)
    value = algebra.multivector(np.array([2.0, -1.0, 3.5, 0.25]))

    matrix = to_matrix(value)
    recovered = from_matrix(matrix)

    assert matrix.mode == "left-regular"
    assert isinstance(recovered, Multivector)
    assert recovered.algebra is algebra
    np.testing.assert_array_equal(recovered.data, value.data)


@pytest.mark.parametrize("gram", GENERAL_GRAM_METRICS)
def test_generator_anticommutators_reproduce_the_supplied_gram_matrix(gram: np.ndarray) -> None:
    algebra = Algebra(gram=gram)
    generators = [np.asarray(to_matrix(vector, mode="left-regular")) for vector in algebra.basis_vectors()]
    identity = np.eye(algebra.dim)

    for row, left in enumerate(generators):
        for column, right in enumerate(generators):
            np.testing.assert_allclose(
                left @ right + right @ left,
                2.0 * gram[row, column] * identity,
                rtol=0.0,
                atol=1e-12,
            )


def test_basis_left_actions_use_the_same_public_representation() -> None:
    algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, -1.0]]))

    actions = _left_regular_matrix(algebra)

    assert actions.shape == (algebra.dim, algebra.dim, algebra.dim)
    for bitmask in range(algebra.dim):
        np.testing.assert_array_equal(
            actions[bitmask],
            algebra.left_action(algebra.blade(bitmask)),
        )


@pytest.mark.parametrize(
    "gram",
    (*GENERAL_GRAM_METRICS, np.diag([2.0, -3.0])),
)
def test_explicit_compact_accepts_general_gram_while_automatic_mode_stays_regular(
    gram: np.ndarray,
) -> None:
    algebra = Algebra(gram=gram)

    generators = compact_basis(algebra)
    explicit = to_matrix(algebra.identity, mode="compact")
    automatic = to_matrix(algebra.identity)

    assert len(generators) == algebra.n
    assert explicit.mode == "compact"
    assert automatic.mode == "left-regular"


def test_quaternion_mode_rejects_a_general_gram_basis_of_cl13() -> None:
    gram = np.diag([1.0, -1.0, -1.0, -1.0])
    gram[1, 2] = gram[2, 1] = 0.25
    algebra = Algebra(gram=gram)

    assert algebra.inertia == (1, 3, 0)
    with pytest.raises(NotImplementedError, match="normalized orthogonal.*left-regular"):
        to_matrix(algebra.identity, mode="quaternion")


def test_normalized_diagonal_compact_behavior_remains_compatible() -> None:
    algebra = Algebra(signature=(1, 1, -1))
    e1, e2, e3 = algebra.basis_vectors()
    left = 1 + 2 * e1 - e2
    right = e1 + 0.5 * e3

    left_matrix = to_matrix(left, mode="compact")
    right_matrix = to_matrix(right, mode="compact")
    product_matrix = to_matrix(geometric_product(left, right), mode="compact")

    np.testing.assert_allclose(
        np.asarray(product_matrix),
        np.asarray(left_matrix) @ np.asarray(right_matrix),
        rtol=0.0,
        atol=1e-12,
    )


def test_named_facade_value_roundtrips_without_legacy_expression_internals() -> None:
    algebra = Algebra(2)
    value = algebra.vector([1.0, -2.0], name="v")

    matrix = to_matrix(value, mode="left-regular")
    recovered = from_matrix(matrix)

    assert matrix.symbolic_name is not None
    assert matrix.symbolic_name.latex == r"\rho(v)"
    assert recovered.name is not None
    assert recovered.name.latex == r"\rho^{-1}(\rho(v))"
    np.testing.assert_array_equal(recovered.data, value.data)


@pytest.mark.parametrize(
    "reader, metadata, missing",
    (
        (_metric_inertia, {"signature": (1, -1)}, "inertia"),
        (_gram_matrix, {"signature": (1, -1), "n": 2}, "gram"),
        (_compact_metric_supported, {"signature": (1, -1), "inertia": (1, 1, 0)}, "gram"),
    ),
)
def test_matrix_metadata_cannot_be_guessed_from_an_old_signature(reader, metadata, missing) -> None:
    signature_only: Any = SimpleNamespace(**metadata)

    with pytest.raises(AttributeError, match=missing):
        reader(signature_only)


@pytest.mark.parametrize("gram", (*GENERAL_GRAM_METRICS, np.diag([1.0, 0.0])))
def test_regular_conversion_uses_one_public_action_without_column_products(
    gram: np.ndarray, monkeypatch: pytest.MonkeyPatch
) -> None:
    algebra = Algebra(gram=gram)
    value = algebra.multivector(np.arange(algebra.dim, dtype=float))
    expected = algebra.left_action(value)
    original = Algebra.left_action
    observed = []

    def record_action(owner, operand):
        observed.append((owner, operand))
        return original(owner, operand)

    def reject_column_products(*args, **kwargs):
        raise AssertionError("regular conversion fell back to per-column products")

    monkeypatch.setattr(Algebra, "left_action", record_action)
    monkeypatch.setattr(Multivector, "__mul__", reject_column_products)

    result = to_matrix(value, mode="left-regular")

    assert len(observed) == 1
    assert observed[0][0] is algebra and observed[0][1] is value
    np.testing.assert_array_equal(result.mat, expected)


def test_missing_public_left_action_is_not_replaced_by_a_legacy_algorithm(monkeypatch: pytest.MonkeyPatch) -> None:
    value = Algebra(2).vector([1.0, 2.0])
    monkeypatch.delattr(Algebra, "left_action")

    with pytest.raises(AttributeError, match="left_action"):
        to_matrix(value, mode="left-regular")


@pytest.mark.parametrize("mode", ("left-regular", "compact", "quaternion"))
def test_matrix_inverse_uses_the_public_factory_and_immutable_naming(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    algebra = Algebra(0, 2)
    value = algebra.multivector(np.array([1.0, 2.0, -3.0, 0.5])).named("v")
    matrix = to_matrix(value, mode=mode)
    original = Algebra.multivector
    constructed = []

    def record_factory(owner, data, **kwargs):
        result = original(owner, data, **kwargs)
        constructed.append(result)
        return result

    monkeypatch.setattr(Algebra, "multivector", record_factory)

    recovered = from_matrix(matrix)

    assert len(constructed) == 1
    assert constructed[0].name is None
    assert recovered is not constructed[0]
    assert recovered.numeric is constructed[0].numeric
    assert recovered.algebra is algebra
    assert recovered.name is not None and matrix.symbolic_name is not None
    assert recovered.name.latex == rf"\rho^{{-1}}({matrix.symbolic_name.latex})"
    np.testing.assert_allclose(recovered.data, value.data, atol=1e-12, rtol=0)


@pytest.mark.parametrize("mode", ("left-regular", "compact"))
def test_core_plan_identity_and_actions_survive_legacy_fallback_removal(mode: str) -> None:
    algebra = Algebra(gram=GENERAL_GRAM_METRICS[1])
    core_algebra: Any = algebra.numeric

    plan = _representation_plan(algebra, mode)
    direct_plan = _representation_plan(core_algebra, mode)
    actions = _left_regular_matrix(core_algebra)

    assert direct_plan is plan
    assert plan.source_algebra is core_algebra
    for mask, action in enumerate(actions):
        np.testing.assert_array_equal(action, core_algebra.left_action(core_algebra.blade(mask)))


def test_matrix_conversion_runs_with_legacy_imports_blocked() -> None:
    program = """
import importlib.abc
import sys

class RejectLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {'galaga.algebra', 'galaga.expr', 'galaga.ops', 'galaga.symbolic_core'} or fullname.startswith('galaga.legacy'):
            raise AssertionError('matrix package imported legacy module: ' + fullname)

sys.meta_path.insert(0, RejectLegacy())
import numpy as np
from galaga import Algebra
from galaga_matrix import to_matrix, from_matrix

for gram, modes in (
    (((0.0, -1.0), (-1.0, 0.0)), ('left-regular', 'compact')),
    (((-1.0, 0.0), (0.0, -1.0)), ('left-regular', 'compact', 'quaternion')),
):
    algebra = Algebra(gram=gram)
    value = algebra.multivector(np.arange(algebra.dim, dtype=float)).named('v')
    for mode in modes:
        matrix = to_matrix(value, mode=mode)
        recovered = from_matrix(matrix)
        assert recovered.algebra is algebra
        assert recovered.name is not None
        np.testing.assert_allclose(recovered.data, value.data, atol=1e-12, rtol=0)
        np.testing.assert_allclose(matrix.mat @ matrix.mat, to_matrix(value * value, mode=mode).mat, atol=1e-12, rtol=0)
assert 'galaga.algebra' not in sys.modules
assert 'galaga.legacy' not in sys.modules
"""
    completed = subprocess.run([sys.executable, "-c", program], check=False, capture_output=True, text=True, timeout=60)

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_matrix_implementation_does_not_read_legacy_multiplication_tables() -> None:
    source = (Path(__file__).parents[1] / "galaga_matrix/matrix.py").read_text()

    assert "_mul_index" not in source
    assert "_mul_sign" not in source
    assert "from galaga import Algebra" not in source
    assert "from galaga.algebra import Multivector" not in source
    assert 'getattr(mv, "_expr"' not in source
    assert 'getattr(mv, "_is_symbolic"' not in source
    assert 'getattr(mv, "_to_expr"' not in source
    assert 'getattr(mv, "_name' not in source
