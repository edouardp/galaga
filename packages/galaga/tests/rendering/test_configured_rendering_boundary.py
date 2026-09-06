"""Exact rendering survives legacy deletion without losing historical evidence."""

from __future__ import annotations

import inspect
import json
import runpy
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS
from tools.latex_contract import latex_test, render_test, testcase
from tools.rendering_contract import (
    ALGEBRA_PROFILES,
    DISPLAY_PROFILES,
    NAMED_ALGEBRAS,
    ExpressionContext,
    context_for,
)

import galaga.facade as facade

CONTRACT_FILES = (
    "test_compound_latex_contract.py",
    "test_sta_latex_contract.py",
    "test_rga_latex_contract.py",
)
ARCHIVE_PATH = Path(__file__).parents[2] / "tools/baselines/configured-rendering-v1.json"
ARCHIVE = json.loads(ARCHIVE_PATH.read_text())


@lru_cache
def _suite(filename: str):
    # Load ordinary test definitions without collecting the parent conftest's
    # temporary v1 constructor guard. The suites themselves must not need v1.
    return runpy.run_path(str(Path(__file__).with_name(filename)))


def _rendering_cases(function):
    return next(mark.args[1] for mark in function.pytestmark if mark.args[0] == "_rendering_case")


def test_archive_has_capture_provenance_and_complete_live_counterparts() -> None:
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "af3c167c188f2174fad65948e17d9b2706ee755b"
    assert ARCHIVE["captured_on"] == "2026-09-06"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    historical_tests = {row["test"] for row in ARCHIVE["expressions"]}
    assert len(historical_tests) == len(ARCHIVE["expressions"]) == 32
    live_tests = set()
    case_count = 0
    for filename in CONTRACT_FILES:
        for name, function in _suite(filename).items():
            if not name.startswith("test_") or not callable(function):
                continue
            marks = getattr(function, "pytestmark", ())
            if not any(mark.name == "parametrize" and mark.args[0] == "_rendering_case" for mark in marks):
                continue
            live_tests.add(f"{filename}::{name}")
            cases = _rendering_cases(function)
            case_count += len(cases)
            assert all(case.algebra in NAMED_ALGEBRAS for case in cases)
    assert historical_tests <= live_tests  # New v2-only cases need no invented v1 history.
    assert case_count >= 34
    display_test = _suite("test_compound_latex_contract.py")["test_display_sensitive_expression"]
    assert {
        "core-facade-v2/cl3/full-default",
        "core-facade-v2/cl3/full-precision-3",
        "core-facade-v2/cl3/full-unfiltered-12",
    } <= {case.algebra for case in _rendering_cases(display_test)}
    notation = _suite("test_rga_latex_contract.py")["LENGYEL_NOTATION"]
    assert {row["operation"] for row in ARCHIVE["notation"]} <= {row.operation for row in notation}
    assert len(ARCHIVE["notation"]) == 26
    assert len(_suite("test_rga_latex_contract.py")["RGA_BLADE_TABLE"]) == 16
    for row in ARCHIVE["expressions"]:
        assert row["configuration"].startswith("legacy-v1/")
        assert row["target"] == "latex" and row["content"] == "full"
        assert isinstance(row["expected"], str) and row["expected"]
    for row in ARCHIVE["notation"]:
        assert set(row["renderings"]) == {"unicode", "latex"}
        assert all(row["renderings"].values())


@pytest.mark.parametrize("observation", ARCHIVE["expressions"], ids=lambda row: row["test"])
def test_compound_coefficients_match_history_after_algebraic_basis_transport(observation) -> None:
    filename, name = observation["test"].split("::")
    function = _suite(filename)[name]
    expression = inspect.getclosurevars(function).nonlocals["expression"]
    configuration = observation["configuration"].replace("legacy-v1/", "core-facade-v2/")
    context = context_for(configuration)

    # Derive the exterior basis transport from actual wedge products. PGA's
    # old e0-first storage cannot be compared directly to native v2 e0-last data.
    assert len(observation["basis_vectors"]) == context.algebra.n
    assert set(observation["basis_vectors"]) == set(context.vectors)
    columns = []
    for mask in range(context.algebra.dim):
        blade = context.algebra.scalar(1)
        for index, semantic_name in enumerate(observation["basis_vectors"]):
            if mask & (1 << index):
                blade = blade ^ context.vector(semantic_name)
        columns.append(blade.data)
    historical = np.asarray(observation["coefficients"])
    assert historical.shape == (context.algebra.dim,) and np.isfinite(historical).all()
    expected = np.column_stack(columns) @ historical

    value = expression(context)

    np.testing.assert_allclose(value.data, expected, atol=1e-12, rtol=0)
    # Execute the existing literal v2 rendering contract, not the archived v1
    # spelling: reviewed floor symbols, accents, and PGA order stay authoritative.
    case = next(case for case in _rendering_cases(function) if case.algebra == configuration)
    function(case)


@pytest.mark.parametrize("observation", ARCHIVE["notation"], ids=lambda row: row["operation"])
def test_rga_notation_operations_preserve_the_captured_numeric_results(observation) -> None:
    configuration = observation["configuration"].replace("legacy-v1/", "core-facade-v2/")
    context = context_for(configuration)
    a = context.named(context.vector("e1"), "a")
    b = context.named(context.vector("e2"), "b")
    arguments = (a,) if observation["arity"] == 1 else (a, b)
    if observation["order"] is not None:
        arguments += (observation["order"],)

    value = context.call(observation["operation"], *arguments)

    # Both RGA implementations use native e1/e2/e3/e4 coefficient order.
    assert tuple(context.vectors) == ("e1", "e2", "e3", "e4")
    expected = np.asarray(observation["coefficients"])
    assert expected.shape == value.data.shape and np.isfinite(expected).all()
    np.testing.assert_allclose(value.data, expected, atol=1e-12, rtol=0)


@pytest.mark.parametrize("configuration", NAMED_ALGEBRAS)
def test_named_contexts_construct_only_tracked_facade_values_with_the_actual_metric(configuration: str) -> None:
    context = context_for(configuration)

    assert context.implementation == "core-facade-v2"
    assert context.api is facade
    assert isinstance(context.algebra, facade.Algebra)
    for i, left in enumerate(context.basis_vectors()):
        assert isinstance(left, facade.Multivector) and left.expr is not None
        for j, right in enumerate(context.basis_vectors()):
            anticommutator = context.call("geometric_product", left, right) + context.call(
                "geometric_product", right, left
            )
            expected = context.algebra.scalar(2 * context.algebra.gram[i, j])
            np.testing.assert_allclose(anticommutator.data, expected.data, atol=1e-12, rtol=0)


def test_named_contexts_and_profile_registries_are_immutable_and_fresh() -> None:
    context = context_for("core-facade-v2/cl3/full-default")
    other = context_for(context.configuration.id)

    assert context is not other and context.algebra is not other.algebra
    for registry in (ALGEBRA_PROFILES, DISPLAY_PROFILES, NAMED_ALGEBRAS, context.vectors):
        key = next(iter(registry))
        with pytest.raises(TypeError):
            registry[key] = registry[key]  # type: ignore[index] - deliberately test runtime immutability
    with pytest.raises(FrozenInstanceError):
        context.configuration.id = "changed"  # type: ignore[misc] - deliberately mutate a frozen record


@pytest.mark.parametrize("configuration", ("unknown", "legacy-v1/cl3/full-default"))
def test_unknown_or_retired_configuration_is_not_silently_mapped_to_v2(configuration: str) -> None:
    with pytest.raises(KeyError, match="unknown configured algebra"):
        context_for(configuration)


def test_direct_context_construction_also_rejects_a_retired_implementation() -> None:
    configuration = replace(
        NAMED_ALGEBRAS["core-facade-v2/cl3/full-default"],
        implementation="legacy-v1",  # type: ignore[arg-type] - exercise rejection of invalid runtime input
    )
    with pytest.raises(ValueError, match="only core-facade-v2"):
        ExpressionContext(configuration, ALGEBRA_PROFILES["cl3"], DISPLAY_PROFILES["full-default"])


@pytest.mark.parametrize("names, error", ((("e1",), "invalid vector-name map"), (("e1", "e1", "e3"), "duplicate")))
def test_invalid_semantic_vector_maps_are_rejected(names, error) -> None:
    profile = replace(ALGEBRA_PROFILES["cl3"], facade_vectors=names)
    with pytest.raises(ValueError, match=error):
        ExpressionContext(NAMED_ALGEBRAS["core-facade-v2/cl3/full-default"], profile, DISPLAY_PROFILES["full-default"])


def test_unknown_semantic_vector_has_explicit_guidance() -> None:
    with pytest.raises(KeyError, match="no semantic basis vector 'e0'"):
        context_for("core-facade-v2/cl3/full-default").vector("e0")


@pytest.mark.parametrize(
    "operation, alias", (("geometric_product", "gp"), ("outer_product", "op"), ("grade_involution", "involute"))
)
def test_canonical_calls_do_not_remap_through_legacy_spellings(
    operation, alias, monkeypatch: pytest.MonkeyPatch
) -> None:
    context = context_for("core-facade-v2/cl3/full-default")
    value = context.vector("e1")
    observed = []

    def canonical(*args):
        observed.extend(args)
        return value

    def reject_alias(*args):
        raise AssertionError("legacy operation remapping")

    monkeypatch.setattr(facade, operation, canonical)
    monkeypatch.setattr(facade, alias, reject_alias)

    assert context.call(operation, value) is value
    assert len(observed) == 1 and observed[0] is value


def test_naming_is_immutable_and_preserves_all_public_name_channels() -> None:
    context = context_for("core-facade-v2/cl3/full-default")
    value = context.vector("e1")
    previous_name = value.name

    named = context.named(value, "theta", unicode="θ", latex=r"\theta")

    assert named is not value and named.numeric is value.numeric
    assert value.name is previous_name
    assert named.name is not None
    assert (named.name.ascii, named.name.unicode, named.name.latex) == ("theta", "θ", r"\theta")


@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
@pytest.mark.parametrize("content", ("value", "expr", "full"))
def test_context_rendering_delegates_explicit_content_and_target(target: str, content: str) -> None:
    context = context_for("core-facade-v2/cl3/full-default")
    value = context.named(context.vector("e1") ^ context.vector("e2"), "B")

    assert context.render(value, target=target, content=content) == value.display(target=target, content=content)
    assert context.latex(value) == value.display(target="latex", content="full")


def test_decorator_requires_an_expectation_and_keeps_latex_alias_strict() -> None:
    with pytest.raises(ValueError, match="at least one testcase"):
        render_test()
    for target, content in (("ascii", "full"), ("latex", "expr")):
        with pytest.raises(ValueError, match="target='latex' and content='full'"):
            latex_test(testcase("core-facade-v2/cl3/full-default", "bad", target=target, content=content))


@pytest.mark.parametrize(
    "target, content, expected",
    (("latex", "full", r"e_{1} \wedge e_{2} \quad = \quad e_{12}"), ("ascii", "expr", "e1 ^ e2")),
)
def test_decorator_renders_after_builder_return_and_never_weakens_literal_comparison(
    target: str, content: str, expected: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    finished = []
    original = ExpressionContext.render

    def after_return(context, value, **kwargs):
        assert finished.pop() is True
        return original(context, value, **kwargs)

    def build(context):
        """A value must outlive this builder's local scope."""
        e1, e2, _ = context.basis_vectors()
        result = e1 ^ e2
        finished.append(True)
        return result

    case = testcase("core-facade-v2/cl3/full-default", expected, target=target, content=content)
    execute = render_test(case)(build)
    monkeypatch.setattr(ExpressionContext, "render", after_return)

    assert execute.__name__ == build.__name__ and execute.__doc__ == build.__doc__
    expected_id = case.algebra if (target, content) == ("latex", "full") else f"{case.algebra}/{content}-{target}"
    assert execute.pytestmark[0].kwargs["ids"](case) == expected_id
    execute(case)
    with pytest.raises(AssertionError):
        execute(replace(case, expected=expected + " "))


def test_exact_suites_have_left_the_legacy_construction_allowlist() -> None:
    assert all(f"rendering/{filename}" not in LEGACY_ORACLE_TESTS for filename in CONTRACT_FILES)


def test_complete_exact_suites_execute_with_legacy_imports_blocked() -> None:
    program = """
import importlib.abc
import sys

class RejectLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {'galaga.algebra', 'galaga.expr', 'galaga.ops', 'galaga.blade_convention', 'galaga.notation', 'galaga.symbolic_core'} or fullname.startswith('galaga.legacy'):
            raise AssertionError('configured rendering imported legacy module: ' + fullname)

sys.meta_path.insert(0, RejectLegacy())
import pytest
# The parent conftest still imports v1 to poison its constructors. This fresh
# process instead forbids imports entirely; it runs all three suites unchanged.
result = pytest.main(['--noconftest', '-q', *sys.argv[1:]])
assert result == 0
assert 'galaga.algebra' not in sys.modules and 'galaga.legacy' not in sys.modules
"""
    paths = [str(Path(__file__).with_name(filename)) for filename in CONTRACT_FILES]
    completed = subprocess.run(
        [sys.executable, "-c", program, *paths], capture_output=True, text=True, check=False, timeout=60
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
