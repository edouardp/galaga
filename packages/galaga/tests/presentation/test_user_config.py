"""YAML preferences resolve into the existing immutable presentation types."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from galaga import Algebra, config, presets, right_hodge_dual
from galaga.composition import NotationPatch, PresentationRecipe
from galaga.presentation import AlgebraConfig, DisplayPolicy, RenderRule
from galaga.presenter import Presenter


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source)
    return path


def test_discovery_layers_global_and_ancestor_presentation_defaults(tmp_path, monkeypatch):
    global_file = _write(
        tmp_path / "xdg/galaga_python/config.yaml",
        "version: 1\ndefaults:\n  presentation:\n    display: {coefficient_precision: 4}\n",
    )
    project = tmp_path / "project"
    _write(project / ".galaga_python", "version: 1\ndefaults:\n  presentation:\n    display: {content: full}\n")
    leaf = project / "notebooks"
    local_file = _write(
        leaf / ".galaga_python", "version: 1\ndefaults:\n  presentation:\n    display: {coefficient_precision: 3}\n"
    )
    monkeypatch.delenv("GALAGA_CONFIG")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))

    settings = config.load(start=leaf)
    assert settings.sources == (global_file, project / ".galaga_python", local_file)
    monkeypatch.chdir(leaf)
    algebra = Algebra(2)
    assert algebra.presentation.display.content == "full"
    assert algebra.presentation.display.coefficient_precision == 3
    assert algebra.numeric.gram[0, 0] == 1


def test_named_notation_hodge_latex_preserves_other_rules_and_numeric_value(tmp_path, monkeypatch):
    path = _write(
        tmp_path / "config.yaml",
        """version: 1
defaults:
  presentation:
    notation: {ref: textbook}
notations:
  textbook:
    reverse: dagger
    rules:
      right_hodge_dual:
        latex: {kind: superscript, symbol: '\\star'}
      left_hodge_dual:
        latex: {kind: subscript, symbol: '\\star'}
""",
    )
    monkeypatch.setenv("GALAGA_CONFIG", str(path))
    ordinary = Algebra(2, expr=True, notation=presets.notation.default())
    algebra = Algebra(2, expr=True)
    e1 = algebra.basis_vectors()[0]
    ordinary_e1 = ordinary.basis_vectors()[0]
    dual = right_hodge_dual(e1)
    baseline = right_hodge_dual(ordinary_e1)

    np.testing.assert_array_equal(dual.data, baseline.data)
    assert r"\star" in dual.latex(content="expr")
    assert r"\star" not in baseline.latex(content="expr")
    assert algebra.presentation.notation.rule("geometric_product", "latex") == ordinary.presentation.notation.rule(
        "geometric_product", "latex"
    )
    assert algebra.presentation.notation.rule("reverse", "latex") == presets.notation.hestenes().rule(
        "reverse", "latex"
    )


def test_named_objects_resolve_to_existing_types_and_compose(tmp_path):
    path = _write(
        tmp_path / "config.yaml",
        """version: 1
defaults:
  presentation:
    display: {coefficient_precision: 5}
notations:
  textbook: {reverse: dagger}
presentations:
  article:
    notation: {ref: textbook}
    display: {target: latex}
presenters:
  values:
    presentation: {ref: article}
    content: value
algebras:
  spacetime:
    preset: sta
    args: {signature: mostly-minus, sigmas: true}
    presentation: {ref: article}
""",
    )
    settings = config.load(files=[path])
    assert isinstance(settings.notation("textbook"), NotationPatch)
    assert isinstance(settings.presentation("article"), PresentationRecipe)
    assert isinstance(settings.presenter("values"), Presenter)
    recipe = settings.algebra("spacetime")
    assert isinstance(recipe, AlgebraConfig)
    algebra = Algebra(config=recipe)
    np.testing.assert_array_equal(algebra.gram, Algebra(config=presets.sta()).gram)
    assert algebra.presentation.display.coefficient_precision == 5
    assert algebra.presentation.display.target == "latex"
    assert settings.presenter("values")(algebra.basis_vectors()[0]).presentation.display.content == "value"
    assert algebra.with_notation(settings.notation("textbook")).presentation.notation.rule("reverse", "latex") == (
        presets.notation.hestenes().rule("reverse", "latex")
    )


def test_explicit_snapshots_and_overrides_outrank_files(tmp_path, monkeypatch):
    path = _write(
        tmp_path / "config.yaml",
        "version: 1\ndefaults:\n  presentation:\n    display: {coefficient_precision: 3}\n",
    )
    monkeypatch.setenv("GALAGA_CONFIG", str(path))
    explicit = presets.euclidean(2).build()
    assert Algebra(config=explicit).presentation.display.coefficient_precision == 6
    assert Algebra(config=presets.euclidean(2)).presentation.display.coefficient_precision == 3
    assert Algebra(2, display=DisplayPolicy(coefficient_precision=9)).presentation.display.coefficient_precision == 9
    numeric = Algebra(2).numeric
    assert Algebra.from_numeric(numeric).presentation.display.coefficient_precision == 3
    assert (
        Algebra.from_numeric(numeric, presentation=explicit.presentation).presentation.display.coefficient_precision
        == 6
    )
    assert (
        Algebra(
            config=presets.euclidean(2) | presets.display.override(coefficient_precision=8)
        ).presentation.display.coefficient_precision
        == 8
    )


def test_file_changes_affect_new_algebras_not_existing_ones(tmp_path, monkeypatch):
    path = _write(
        tmp_path / "config.yaml", "version: 1\ndefaults:\n  presentation:\n    display: {coefficient_precision: 3}\n"
    )
    monkeypatch.setenv("GALAGA_CONFIG", str(path))
    first = Algebra(2)
    _write(path, "version: 1\ndefaults:\n  presentation:\n    display: {coefficient_precision: 8}\n")
    assert first.presentation.display.coefficient_precision == 3
    assert Algebra(2).presentation.display.coefficient_precision == 8
    assert config.reload().sources == (path,)


def test_notation_rule_patches_compose_in_order_and_keep_preset_rules():
    first = NotationPatch(rules=(("right_hodge_dual", "latex", RenderRule("superscript", symbol=r"\star")),))
    second = NotationPatch(rules=(("right_hodge_dual", "latex", RenderRule("superscript", symbol="*")),))
    base = presets.notation.hestenes()
    result = (first | second).apply(base)
    assert result.rule("right_hodge_dual", "latex") == second.rules[0][2]
    assert result.rule("hestenes_inner", "latex") == base.rule("hestenes_inner", "latex")


def test_later_reverse_choice_clears_an_earlier_reverse_specific_rule():
    earlier = NotationPatch(rules=(("reverse", "latex", RenderRule("superscript", symbol="old")),))
    selected = (earlier | NotationPatch(reverse="dagger")).apply(presets.notation.default())
    assert selected.rule("reverse", "latex") == presets.notation.hestenes().rule("reverse", "latex")


def test_local_profile_replaces_global_profile_while_defaults_merge(tmp_path, monkeypatch):
    _write(
        tmp_path / "xdg/galaga_python/config.yaml",
        """version: 1
defaults: {presentation: {display: {coefficient_precision: 3}}}
presentations:
  report: {display: {target: latex}}
""",
    )
    project = tmp_path / "project"
    _write(
        project / ".galaga_python",
        """version: 1
defaults: {presentation: {display: {content: full}}}
presentations:
  report: {display: {target: ascii}}
""",
    )
    monkeypatch.delenv("GALAGA_CONFIG")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    settings = config.load(start=project)
    monkeypatch.chdir(project)
    algebra = Algebra(2).with_presentation(settings.presentation("report"))
    assert algebra.presentation.display.target == "ascii"
    assert algebra.presentation.display.content == "full"
    assert algebra.presentation.display.coefficient_precision == 3


def test_blades_names_and_order_resolve_against_target_dimension(tmp_path):
    path = _write(
        tmp_path / "config.yaml",
        """version: 1
defaults:
  presentation:
    blades: {preset: indexed, args: {prefix: v}}
    local_names: from_blades
    display_order: bitmap
algebras:
  plane:
    gram: [[1, 0.5], [0.5, 1]]
""",
    )
    settings = config.load(files=[path])
    algebra = Algebra(config=settings.algebra("plane"))
    assert tuple(algebra.locals())[:2] == ("v1", "v2")
    assert algebra.presentation.display_order.masks == (0, 1, 2, 3)
    assert algebra.gram[0, 1] == 0.5


@pytest.mark.parametrize(
    "source, fragment",
    [
        ("version: 1\nversion: 1\n", "duplicate key"),
        ("version: 1\nfoo: bar\n", "unknown field"),
        ("version: 2\n", "version"),
        ("version: 1\nalgebras:\n  a: {preset: nope}\n", "unknown algebra preset"),
        ("version: 1\nnotations:\n  a: {base: {ref: b}}\n  b: {base: {ref: a}}\n", "cycle"),
        (
            "version: 1\nnotations:\n  a: {rules: {not_an_operation: {latex: {kind: function, symbol: x}}}}\n",
            "operation ID",
        ),
        ("version: 1\nx: &x {a: 1}\ndefaults: *x\n", "aliases"),
        ("version: 1\ndefaults: !!python/object/apply:os.system ['echo bad']\n", "constructor"),
        ("version: 1\nalgebras:\n  a: {pqr: {p: 2}, gram: [[1]]}\n", "exactly one"),
        ("version: 1\npresentations:\n  a: {extends: {ref: b}}\n  b: {extends: {ref: a}}\n", "cycle"),
    ],
)
def test_bad_configuration_fails_at_load_time(tmp_path, source, fragment):
    path = _write(tmp_path / "config.yaml", source)
    with pytest.raises(config.ConfigError, match=fragment):
        config.load(files=[path])


def test_environment_switches_discovery_off_or_to_one_file(tmp_path, monkeypatch):
    path = _write(tmp_path / "config.yaml", "version: 1\n")
    monkeypatch.setenv("GALAGA_CONFIG", "none")
    assert config.load().sources == ()
    monkeypatch.setenv("GALAGA_CONFIG", str(path))
    assert config.load().sources == (path,)
    monkeypatch.setenv("GALAGA_CONFIG", "relative.yaml")
    with pytest.raises(config.ConfigError, match="absolute"):
        config.load()
    with pytest.raises(config.ConfigError, match="existing file"):
        config.load(files=[tmp_path / "missing.yaml"])
