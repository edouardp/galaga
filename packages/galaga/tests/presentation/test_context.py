import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from galaga.facade import Algebra, geometric_product
from galaga.presentation import Notation
from galaga.presets import EuclideanPreset


def _named_presentation(algebra, name):
    return algebra.default_presentation.with_notation(Notation(name))


def test_scoped_presentation_restores_normally_after_nested_scopes():
    algebra = Algebra(config=EuclideanPreset(2))
    outer = _named_presentation(algebra, "outer")
    inner = _named_presentation(algebra, "inner")

    assert algebra.presentation.notation.id == "euclidean"
    with algebra.use_presentation(outer):
        assert algebra.presentation.notation.id == "outer"
        with algebra.use_presentation(inner):
            assert algebra.presentation.notation.id == "inner"
        assert algebra.presentation.notation.id == "outer"
    assert algebra.presentation.notation.id == "euclidean"


def test_scoped_presentation_restores_after_an_exception():
    algebra = Algebra(config=EuclideanPreset(2))

    with pytest.raises(RuntimeError, match="stop"):
        with algebra.use_presentation(_named_presentation(algebra, "temporary")):
            raise RuntimeError("stop")

    assert algebra.presentation.notation.id == "euclidean"


def test_explicit_presentation_has_priority_over_a_scoped_override():
    algebra = Algebra(config=EuclideanPreset(2))
    scoped = _named_presentation(algebra, "scoped")
    explicit = _named_presentation(algebra, "explicit")

    with algebra.use_presentation(scoped):
        assert algebra.resolve_presentation().notation.id == "scoped"
        assert algebra.resolve_presentation(explicit).notation.id == "explicit"


def test_same_algebra_has_isolated_presentations_in_two_threads():
    algebra = Algebra(config=EuclideanPreset(2))
    barrier = Barrier(2)

    def worker(name):
        with algebra.use_presentation(_named_presentation(algebra, name)):
            barrier.wait()
            selected = algebra.presentation.notation.id
        return selected, algebra.presentation.notation.id

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = set(executor.map(worker, ("thread-a", "thread-b")))

    assert results == {("thread-a", "euclidean"), ("thread-b", "euclidean")}
    assert algebra.presentation.notation.id == "euclidean"


def test_same_algebra_has_isolated_presentations_in_interleaved_async_tasks():
    algebra = Algebra(config=EuclideanPreset(2))

    async def worker(name):
        with algebra.use_presentation(_named_presentation(algebra, name)):
            await asyncio.sleep(0)
            selected = algebra.presentation.notation.id
            await asyncio.sleep(0)
            assert algebra.presentation.notation.id == name
        return selected

    async def run_workers():
        return await asyncio.gather(worker("task-a"), worker("task-b"))

    assert asyncio.run(run_workers()) == ["task-a", "task-b"]
    assert algebra.presentation.notation.id == "euclidean"


def test_scoped_presentation_does_not_change_numeric_results_equality_or_hashing():
    algebra = Algebra(config=EuclideanPreset(2))
    e1, e2 = algebra.basis_vectors()
    expected = geometric_product(e1, e2)

    with algebra.use_presentation(_named_presentation(algebra, "teaching")):
        actual = geometric_product(e1, e2)

    assert actual == expected
    assert hash(actual) == hash(expected)
    assert actual.numeric == expected.numeric
