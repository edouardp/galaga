"""Immutable callable annotator contracts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

import galaga_annotation as ga
from galaga import Algebra


def test_annotator_recipes_are_immutable_and_reusable() -> None:
    algebra = Algebra(2)
    value = algebra.basis_vectors()[0]
    base = ga.annotator(ga.on(ga.whole(), label="a"))
    extended = base.label("b", target=ga.grade(1))
    assert len(base) == 1
    assert len(extended) == 2
    assert base.rules[0].label == "a"
    assert extended.rules[1].label == "b"
    with pytest.raises(FrozenInstanceError):
        base.rules = ()
    first = base(value)
    second = base(value)
    assert isinstance(first, ga.Annotated)
    assert isinstance(second, ga.Annotated)
    assert first.rules == second.rules


def test_fluent_and_functional_construction_produce_the_same_rules() -> None:
    fluent = ga.annotator().mark(ga.grade(1), background="#fff3cd", label="vector part")
    functional = ga.annotator(ga.on(ga.grade(1), background="#fff3cd", label="vector part"))
    assert fluent.rules == functional.rules


def test_highlight_rejects_labels_and_label_requires_text() -> None:
    with pytest.raises(TypeError, match="label"):
        ga.annotator().highlight(ga.whole(), label="nope")
    with pytest.raises(TypeError, match="label text"):
        ga.annotator().label(3)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="positional"):
        ga.annotator().label("x", label="y")


def test_add_appends_rules_without_mutating_the_recipe() -> None:
    first = ga.on(ga.whole(), label="first")
    second = ga.on(ga.grade(1), color="red")
    recipe = ga.annotator(first)
    extended = recipe.add(second)
    assert recipe.rules == (first,)
    assert extended.rules == (first, second)
    with pytest.raises(TypeError, match="Annotation"):
        recipe.add("not a rule")  # type: ignore[arg-type]


def test_one_off_annotate_matches_the_recipe_spelling() -> None:
    algebra = Algebra(2)
    value = algebra.basis_vectors()[0]
    shorthand = ga.annotate(value, label="whole", side="below")
    explicit = ga.annotator(ga.on(ga.whole(), label="whole", side="below"))(value)
    assert shorthand.rules == explicit.rules
    assert shorthand.plain is value
    empty = ga.annotate(value)
    assert empty.rules == ()
