"""Configured rendering, metric-derived coefficients, and decorator contracts."""

from __future__ import annotations

import inspect
import json
import runpy
from dataclasses import FrozenInstanceError, replace
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest
from tools.latex_contract import latex_test, render_test, testcase
from tools.rendering_contract import (
    ALGEBRA_PROFILES,
    DISPLAY_PROFILES,
    NAMED_ALGEBRAS,
    ExpressionContext,
    context_for,
)

import galaga.facade as facade

ARCHIVE_PATH = Path(__file__).parents[2] / "tools/baselines/configured-rendering-v1.json"
ARCHIVE = json.loads(ARCHIVE_PATH.read_text())


@lru_cache
def _suite(filename: str):
    # Load expression builders and their literal expectations together.
    return runpy.run_path(str(Path(__file__).with_name(filename)))


def _rendering_cases(function):
    return next(mark.args[1] for mark in function.pytestmark if mark.args[0] == "_rendering_case")


def test_unknown_configuration_has_explicit_guidance():
    with pytest.raises(KeyError, match="unknown configured algebra"):
        context_for("unknown")


@pytest.mark.parametrize("observation", ARCHIVE["expressions"], ids=lambda row: row["test"])
def test_compound_coefficients_match_history_after_algebraic_basis_transport(observation) -> None:
    filename, name = observation["test"].split("::")
    function = _suite(filename)[name]
    expression = inspect.getclosurevars(function).nonlocals["expression"]
    configuration = observation["configuration"].replace("legacy-v1/", "")
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
    configuration = observation["configuration"].replace("legacy-v1/", "")
    context = context_for(configuration)
    a = context.named(context.vector("e1"), "a")
    b = context.named(context.vector("e2"), "b")
    arguments = (a,) if observation["arity"] == 1 else (a, b)
    if observation["order"] is not None:
        arguments += (observation["order"],)

    operation = {"bulk_part": "metric_apply", "weight_part": "antimetric_apply"}.get(
        observation["operation"], observation["operation"]
    )
    value = context.call(operation, *arguments)

    # Both RGA implementations use native e1/e2/e3/e4 coefficient order.
    assert tuple(context.vectors) == ("e1", "e2", "e3", "e4")
    expected = np.asarray(observation["coefficients"])
    assert expected.shape == value.data.shape and np.isfinite(expected).all()
    np.testing.assert_allclose(value.data, expected, atol=1e-12, rtol=0)


@pytest.mark.parametrize("configuration", NAMED_ALGEBRAS)
def test_named_contexts_construct_only_tracked_facade_values_with_the_actual_metric(configuration: str) -> None:
    context = context_for(configuration)

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
    context = context_for("cl3/full-default")
    other = context_for(context.configuration.id)

    assert context is not other and context.algebra is not other.algebra
    for registry in (ALGEBRA_PROFILES, DISPLAY_PROFILES, NAMED_ALGEBRAS, context.vectors):
        key = next(iter(registry))
        with pytest.raises(TypeError):
            registry[key] = registry[key]  # type: ignore[index] - deliberately test runtime immutability
    with pytest.raises(FrozenInstanceError):
        context.configuration.id = "changed"  # type: ignore[misc] - deliberately mutate a frozen record


@pytest.mark.parametrize("names, error", ((("e1",), "invalid vector-name map"), (("e1", "e1", "e3"), "duplicate")))
def test_invalid_semantic_vector_maps_are_rejected(names, error) -> None:
    profile = replace(ALGEBRA_PROFILES["cl3"], facade_vectors=names)
    with pytest.raises(ValueError, match=error):
        ExpressionContext(NAMED_ALGEBRAS["cl3/full-default"], profile, DISPLAY_PROFILES["full-default"])


def test_unknown_semantic_vector_has_explicit_guidance() -> None:
    with pytest.raises(KeyError, match="no semantic basis vector 'e0'"):
        context_for("cl3/full-default").vector("e0")


def test_naming_is_immutable_and_preserves_all_public_name_channels() -> None:
    context = context_for("cl3/full-default")
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
    context = context_for("cl3/full-default")
    value = context.named(context.vector("e1") ^ context.vector("e2"), "B")

    assert context.render(value, target=target, content=content) == value.display(target=target, content=content)
    assert context.latex(value) == value.display(target="latex", content="full")


def test_decorator_requires_an_expectation_and_keeps_latex_alias_strict() -> None:
    with pytest.raises(ValueError, match="at least one testcase"):
        render_test()
    for target, content in (("ascii", "full"), ("latex", "expr")):
        with pytest.raises(ValueError, match="target='latex' and content='full'"):
            latex_test(testcase("cl3/full-default", "bad", target=target, content=content))


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

    case = testcase("cl3/full-default", expected, target=target, content=content)
    execute = render_test(case)(build)
    monkeypatch.setattr(ExpressionContext, "render", after_return)

    assert execute.__name__ == build.__name__ and execute.__doc__ == build.__doc__
    expected_id = case.algebra if (target, content) == ("latex", "full") else f"{case.algebra}/{content}-{target}"
    assert execute.pytestmark[0].kwargs["ids"](case) == expected_id
    execute(case)
    with pytest.raises(AssertionError):
        execute(replace(case, expected=expected + " "))
