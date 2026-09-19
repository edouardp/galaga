"""Execute the annotation gallery notebook headlessly."""

from __future__ import annotations

import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook uses native t-strings")
ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK = ROOT / "examples" / "annotation" / "annotated_lessons.py"


def test_annotation_notebook_renders_every_labelled_feature() -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    outputs, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={"presenter_choice": SimpleNamespace(value="Lengyel")}
    )

    assert definitions["view_whole"].plain is definitions["area"]
    assert definitions["presented_area"].plain is definitions["area"]
    assert [label.side for label in definitions["adjacent_result"].labels] == ["above", "below"]
    assert definitions["absent_view"].katex().missing[0].label == "no grade three"

    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    for fragment in (
        "overset",
        "underset",
        "underbrace",
        "overbrace",
        "undergroup",
        "overgroup",
        "colorbox",
        "fcolorbox",
        "boxed",
        "textcolor",
    ):
        assert fragment in markup, fragment
    assert r"\wedge" in markup
    assert definitions["solved_summary"].startswith("labels=")
    equation_label = definitions["view_equation_label"].latex()
    assert r"\substack{\text{carrier line} \\ e_{1} \wedge e_{2}}" in equation_label

    # Color fills re-enter math with `$...$`, so wrapping them in inline math
    # would split the segment; decorated equations must be display math.
    segments = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
    decorated = [
        segment
        for segment in segments
        if any(command in segment for command in ("colorbox", "fcolorbox", "undergroup", "overgroup"))
    ]
    assert decorated
    assert all(segment.startswith("||[") and segment.endswith("||]") for segment in decorated)


def test_annotation_notebook_colours_grades() -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={"presenter_choice": SimpleNamespace(value="Lengyel")}
    )
    rendered = definitions["view_grades"].latex()
    assert r"\textcolor{#111827}{0.5}" in rendered
    assert r"\textcolor{#0072B2}{2 e_{1}}" in rendered
    assert r"\textcolor{#D55E00}{3 e_{12}}" in rendered
    assert r"\textcolor{#009E73}{0.4 e_{123}}" in rendered


def test_annotation_notebook_brackets_a_lengyel_cga_dipole() -> None:
    pytest.importorskip("marimo")
    pytest.importorskip("galaga_marimo")
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run(
        defs={"presenter_choice": SimpleNamespace(value="Lengyel")}
    )

    dipole = definitions["dipole"]
    nonzero = {int(index) for index in np.flatnonzero(dipole.data)}
    # e12,e23,e31 moment; e41,e42,e43 direction; e15,e25,e35,e45 flat point.
    assert nonzero == {3, 5, 6, 9, 10, 12, 17, 18, 20, 24}

    assert [label.side for label in definitions["view_grouped"].katex().labels] == ["below", "above"]

    nested = definitions["view_nested"]
    assert nested.plain is dipole
    rendered = nested.latex()
    assert r"\overgroup" in rendered
    assert r"\undergroup" in rendered
    assert r"\overset{\mathclap{\text{cocarrier normal}}}{\overgroup{" in rendered
    assert r"\underset{\mathclap{\text{cocarrier position}}}{\undergroup{" in rendered
    assert "cocarrier normal" in rendered
    assert "cocarrier position" in rendered

    assert definitions["classified"].kind == "dipole"
    classified_view = definitions["view_object"]
    assert classified_view.plain is dipole
    classified_text = classified_view.latex()
    assert classified_text.count(r"\colorbox{#b8e6bf}") == 1
    assert classified_text.count(r"\colorbox{#d8c4ee}") == 1
    assert (
        r"\colorbox{#b8e6bf}{$\mathord{\mathrlap{\smash[b]{\underset{\mathclap{\textcolor{#2f7d4f}{"
        r"\text{carrier line}}}}{\phantom{" in classified_text
    )
    assert (
        r"\mathrlap{\smash[t]{\textcolor{#0099cc}{\overset{\mathclap{\text{cocarrier normal}}}{"
        r"\overgroup{" in classified_text
    )
    assert (
        r"\mathrlap{\smash[t]{\textcolor{#0099cc}{\overset{\mathclap{\text{cocarrier position}}}{"
        r"\overgroup{"
        r"\textcolor{black}{\vphantom{\raisebox{4px}{" in classified_text
    )
    assert (
        r"\colorbox{#d8c4ee}{$\mathrlap{\smash[b]{\underset{\mathclap{\textcolor{#6b4a9e}{"
        r"\text{flat point}}}}{\phantom{" in classified_text
    )
    assert r"\overgroup{\textcolor{#0099cc}{" not in classified_text
    assert "- -" not in classified_text and "+ -" not in classified_text

    examples = (
        ("round_point_kind", "highlighted_round_point", "round point", ("origin", "position", "infinity")),
        (
            "circle_kind",
            "highlighted_circle",
            "circle",
            ("carrier plane", "flat line", "cocarrier direction", "cocarrier moment"),
        ),
        ("sphere_kind", "highlighted_sphere", "sphere", ("origin part", "flat part")),
    )
    for kind_name, view_name, expected_kind, labels in examples:
        assert definitions[kind_name].kind == expected_kind
        example_text = definitions[view_name].latex()
        assert all(label in example_text for label in labels)
        assert r"\colorbox" in example_text

    component_text = definitions["highlighted_circle_components"].latex()
    assert all(label in component_text for label in ("plane part", "center part", "flat part", "flat weight"))
    assert "carrier plane" not in component_text
