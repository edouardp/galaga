"""TOML preferences resolve into the existing immutable presentation types."""

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


def _local_config(tmp_path, monkeypatch, source: str) -> Path:
    monkeypatch.chdir(tmp_path)
    return _write(tmp_path / ".galaga_python.toml", source)


def test_discovery_layers_global_and_ancestor_presentation_defaults(tmp_path, monkeypatch):
    global_file = _write(
        tmp_path / "xdg/galaga_python/config.toml",
        "version = 1\n[defaults.presentation.display]\ncoefficient_precision = 4\n",
    )
    project = tmp_path / "project"
    _write(project / ".galaga_python.toml", 'version = 1\n[defaults.presentation.display]\ncontent = "full"\n')
    leaf = project / "notebooks"
    local_file = _write(
        leaf / ".galaga_python.toml", "version = 1\n[defaults.presentation.display]\ncoefficient_precision = 3\n"
    )
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))

    settings = config.load(start=leaf)
    assert settings.sources == (global_file, project / ".galaga_python.toml", local_file)
    monkeypatch.chdir(leaf)
    algebra = Algebra(2)
    assert algebra.presentation.display.content == "full"
    assert algebra.presentation.display.coefficient_precision == 3
    assert algebra.numeric.gram[0, 0] == 1


def test_named_notation_hodge_latex_preserves_other_rules_and_numeric_value(tmp_path, monkeypatch):
    _local_config(
        tmp_path,
        monkeypatch,
        """version = 1
[defaults.presentation]
notation = "@textbook"
[notations.textbook]
reverse = "dagger"
[notations.textbook.rules.right_hodge_dual.latex]
kind = "superscript"
symbol = '\\star'
[notations.textbook.rules.left_hodge_dual.latex]
kind = "subscript"
symbol = '\\star'
""",
    )
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
    python_patch = presets.notation.override(
        reverse="dagger",
        latex={
            "right_hodge_dual": RenderRule("superscript", symbol=r"\star"),
            "left_hodge_dual": RenderRule("subscript", symbol=r"\star"),
        },
    )
    assert python_patch.apply(presets.notation.default()) == config.load().notation("textbook").apply(
        presets.notation.default()
    )


def test_named_objects_resolve_to_existing_types_and_compose(tmp_path):
    path = _write(
        tmp_path / "config.toml",
        """version = 1
[defaults.presentation.display]
coefficient_precision = 5
[notations.textbook]
reverse = "dagger"
[presentations.article]
notation = "@textbook"
display = { target = "latex" }
[presenters.values]
presentation = "@article"
content = "value"
[algebras.spacetime]
preset = "sta"
args = { signature = "mostly-minus", sigmas = true }
presentation = "@article"
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


def test_named_references_resolve_through_notation_and_presentation_inheritance(tmp_path):
    path = _write(
        tmp_path / "config.toml",
        """version = 1
[notations.foundation]
base = { preset = "hestenes" }
[notations.derived]
base = "@foundation"
[presentations.foundation]
notation = "@derived"
[presentations.article]
extends = "@foundation"
display = { target = "latex" }
[presenters.article_value]
presentation = "@article"
content = "value"
[algebras.plane]
pqr = { p = 2, q = 0, r = 0 }
presentation = "@article"
""",
    )
    settings = config.load(files=[path])
    algebra = Algebra(config=settings.algebra("plane"))
    assert algebra.presentation.notation.rule("reverse", "latex") == presets.notation.hestenes().rule(
        "reverse", "latex"
    )
    assert algebra.presentation.display.target == "latex"
    assert settings.presenter("article_value")(algebra.basis_vectors()[0]).presentation.display.content == "value"


def test_inline_settings_remain_tables_next_to_named_references(tmp_path):
    path = _write(
        tmp_path / "config.toml",
        """version = 1
[defaults.presentation.notation]
reverse = "dagger"
[algebras.plane]
pqr = { p = 2, q = 0, r = 0 }
presentation = { display = { target = "ascii" } }
""",
    )
    algebra = Algebra(config=config.load(files=[path]).algebra("plane"))
    assert algebra.presentation.notation.rule("reverse", "latex") == presets.notation.hestenes().rule(
        "reverse", "latex"
    )
    assert algebra.presentation.display.target == "ascii"


def test_algebra_constructor_resolves_named_config_from_discovered_files(tmp_path, monkeypatch):
    _local_config(
        tmp_path,
        monkeypatch,
        """version = 1
[defaults.presentation.display]
coefficient_precision = 4
[algebras.plane]
pqr = { p = 2, q = 0, r = 0 }
presentation = { display = { target = "ascii" } }
""",
    )
    algebra = Algebra(config="@plane")
    np.testing.assert_array_equal(algebra.gram, Algebra(2, user_config_files=False).gram)
    assert algebra.presentation.display.coefficient_precision == 4
    assert algebra.presentation.display.target == "ascii"
    assert (
        Algebra(
            config="@plane", display=DisplayPolicy(coefficient_precision=9)
        ).presentation.display.coefficient_precision
        == 9
    )


def test_named_algebra_constructor_rejects_opt_out_before_reading_files(tmp_path, monkeypatch):
    _local_config(tmp_path, monkeypatch, "[malformed\n")
    with pytest.raises(ValueError, match="requires user_config_files=True"):
        Algebra(config="@plane", user_config_files=False)


@pytest.mark.parametrize("reference", ["plane", "@", "@@plane"])
def test_algebra_constructor_rejects_invalid_named_config_reference(reference):
    with pytest.raises(ValueError, match="named algebra reference"):
        Algebra(config=reference)


def test_algebra_constructor_reports_missing_named_config(tmp_path, monkeypatch):
    _local_config(tmp_path, monkeypatch, "version = 1\n")
    with pytest.raises(config.ConfigError, match="unknown algebras name 'missing'"):
        Algebra(config="@missing")


def test_explicit_snapshots_and_overrides_outrank_files(tmp_path, monkeypatch):
    _local_config(
        tmp_path,
        monkeypatch,
        "version = 1\n[defaults.presentation.display]\ncoefficient_precision = 3\n",
    )
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


def test_user_config_files_false_skips_defaults_for_every_facade_construction_path(tmp_path, monkeypatch):
    _local_config(
        tmp_path,
        monkeypatch,
        "version = 1\n[defaults.presentation.display]\ncoefficient_precision = 3\n",
    )
    numeric = Algebra(2).numeric
    configured = presets.euclidean(2) | presets.display.override(content="full")

    assert Algebra(2).presentation.display.coefficient_precision == 3
    assert Algebra(2, user_config_files=False).presentation.display.coefficient_precision == 6
    assert Algebra(config=presets.euclidean(2), user_config_files=False).presentation.display.coefficient_precision == 6
    assert Algebra(config=configured, user_config_files=False).presentation.display.coefficient_precision == 6
    assert Algebra(config=configured, user_config_files=False).presentation.display.content == "full"
    assert Algebra.from_numeric(numeric, user_config_files=False).presentation.display.coefficient_precision == 6


def test_user_config_files_false_does_not_read_a_malformed_local_file(tmp_path, monkeypatch):
    _local_config(tmp_path, monkeypatch, "[malformed\n")
    assert Algebra(2, user_config_files=False).n == 2
    assert Algebra.from_numeric(Algebra(2, user_config_files=False).numeric, user_config_files=False).n == 2
    with pytest.raises(config.ConfigError, match=".galaga_python.toml"):
        Algebra(2)


@pytest.mark.parametrize("value", [None, 0, "false"])
def test_user_config_files_requires_boolean(value):
    with pytest.raises(TypeError, match="user_config_files must be a boolean"):
        Algebra(2, user_config_files=value)


def test_file_changes_affect_new_algebras_not_existing_ones(tmp_path, monkeypatch):
    path = _local_config(
        tmp_path, monkeypatch, "version = 1\n[defaults.presentation.display]\ncoefficient_precision = 3\n"
    )
    first = Algebra(2)
    _write(path, "version = 1\n[defaults.presentation.display]\ncoefficient_precision = 8\n")
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
        tmp_path / "xdg/galaga_python/config.toml",
        """version = 1
[defaults.presentation.display]
coefficient_precision = 3
[presentations.report.display]
target = "latex"
""",
    )
    project = tmp_path / "project"
    _write(
        project / ".galaga_python.toml",
        """version = 1
[defaults.presentation.display]
content = "full"
[presentations.report.display]
target = "ascii"
""",
    )
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    settings = config.load(start=project)
    monkeypatch.chdir(project)
    algebra = Algebra(2).with_presentation(settings.presentation("report"))
    assert algebra.presentation.display.target == "ascii"
    assert algebra.presentation.display.content == "full"
    assert algebra.presentation.display.coefficient_precision == 3


def test_blades_names_and_order_resolve_against_target_dimension(tmp_path):
    path = _write(
        tmp_path / "config.toml",
        """version = 1
[defaults.presentation]
blades = { preset = "indexed", args = { prefix = "v" } }
local_names = "from_blades"
display_order = "bitmap"
[algebras.plane]
gram = [[1, 0.5], [0.5, 1]]
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
        ("version = 1\nversion = 1\n", "config.toml"),
        ("version = 1\n[unexpected]\nvalue = 1\n", "unknown field"),
        ("version = 2\n", "version"),
        ('version = 1\n[algebras.a]\npreset = "nope"\n', "unknown algebra preset"),
        ('version = 1\n[notations.a]\nbase = "@b"\n[notations.b]\nbase = "@a"\n', "cycle"),
        (
            'version = 1\n[notations.a.rules.not_an_operation.latex]\nkind = "function"\nsymbol = "x"\n',
            "operation ID",
        ),
        ("version = 1\n[defaults\n", "config.toml"),
        ('version = 1\n[defaults.presentation]\nnotation = "textbook"\n', "@name"),
        ('version = 1\n[defaults.presentation]\nnotation = "@"\n', "non-empty string"),
        ('version = 1\n[defaults.presentation]\nnotation = "@@textbook"\n', "reserved"),
        ('version = 1\n[notations."@bad"]\nreverse = "dagger"\n', "reserved"),
        ('version = 1\n[notations.a]\nbase = { ref = "b" }\n', "unknown field"),
        ('version = 1\n[presentations.a]\nextends = "base"\n', "@name"),
        ('version = 1\n[presenters.a]\npresentation = { ref = "b" }\n', "@name"),
        ("version = 1\n[algebras.a]\npqr = { p = 2 }\ngram = [[1]]\n", "exactly one"),
        (
            'version = 1\n[presentations.a]\nextends = "@b"\n[presentations.b]\nextends = "@a"\n',
            "cycle",
        ),
    ],
)
def test_bad_configuration_fails_at_load_time(tmp_path, source, fragment):
    path = _write(tmp_path / "config.toml", source)
    with pytest.raises(config.ConfigError, match=fragment):
        config.load(files=[path])


def test_explicit_file_selection_and_retired_environment_variable(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = _write(tmp_path / "example.toml", "version = 1\n")
    monkeypatch.setenv("GALAGA_CONFIG", str(path))
    assert config.load().sources == ()
    assert config.load(files=[path]).sources == (path,)

    local = _write(tmp_path / ".galaga_python.toml", "version = 1\n")
    monkeypatch.setenv("GALAGA_CONFIG", "none")
    assert config.load().sources == (local,)
    with pytest.raises(config.ConfigError, match="existing file"):
        config.load(files=[tmp_path / "missing.toml"])
