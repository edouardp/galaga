"""Permanent source/artifact deletion gates and corruption controls."""

from __future__ import annotations

import io
import runpy
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

from scripts import check_galaga_artifact as gate

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def project(tmp_path):
    for name in gate.REQUIRED_RUNTIME:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "galaga"\nversion = "2.0.0a2"\nrequires-python = ">=3.11"\ndependencies = ["numpy>=1.24"]\n'
    )
    return tmp_path


METADATA = b"Name: galaga\nVersion: 2.0.0a2\nRequires-Python: >=3.11\nRequires-Dist: numpy>=1.24\n\n"


def artifact(project, kind, extra=None):
    members = gate.source_runtime(project)
    metadata_path = "galaga-2.0.0a2.dist-info/METADATA" if kind == "wheel" else "PKG-INFO"
    members[metadata_path] = METADATA
    members.update(extra or {})
    path = project / ("galaga.whl" if kind == "wheel" else "galaga.tar.gz")
    if kind == "wheel":
        with zipfile.ZipFile(path, "w") as archive:
            for name, data in members.items():
                archive.writestr(name, data)
    else:
        with tarfile.open(path, "w:gz") as archive:
            for name, data in members.items():
                info = tarfile.TarInfo("galaga-2.0.0a2/" + name)
                if name.endswith("/"):
                    info.type = tarfile.DIRTYPE
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
    return path


def test_retirement_list_matches_the_migration_manifest():
    manifest = runpy.run_path(str(ROOT / "packages/galaga/tests/compatibility/v1_surface_manifest.py"))
    roots = {"galaga." + name for name in gate.RETIRED_ROOTS}
    legacy = manifest["LEGACY_ONLY_SUBMODULES"]
    assert roots == {name for name in legacy if not any(name.startswith(other + ".") for other in legacy)}


def test_production_source_contains_no_retired_files_imports_or_product_tables():
    runtime = gate.source_runtime(ROOT / "packages/galaga")
    assert "galaga/_latex_symbols.py" in runtime and "galaga/names.py" in runtime


def test_removed_modules_really_fail_to_import_without_the_test_guard():
    program = """
import importlib
import importlib.util
import sys
import galaga
for name in sys.argv[1:]:
    assert importlib.util.find_spec(name) is None, name
    try:
        importlib.import_module(name)
    except ModuleNotFoundError as error:
        assert error.name == name, (name, error.name)
    else:
        raise AssertionError('retired module remains importable: ' + name)
assert not hasattr(galaga, 'legacy')
"""
    result = subprocess.run(
        [sys.executable, "-c", program, *("galaga." + name for name in sorted(gate.RETIRED_ROOTS))],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("kind", ("wheel", "sdist"))
def test_clean_artifact_matches_runtime_and_metadata(project, kind, capsys):
    path = artifact(project, kind)
    assert "source-identical" in gate.check_artifact(path, project)
    assert gate.main(["--project", str(project), str(path)]) == 0
    assert "no legacy engine" in capsys.readouterr().out


@pytest.mark.parametrize("root", sorted(gate.RETIRED_ROOTS))
@pytest.mark.parametrize("kind", ("wheel", "sdist"))
@pytest.mark.parametrize("suffix", ("hidden.py", ""))
def test_artifact_gate_rejects_every_retired_root_including_empty_directories(project, root, kind, suffix):
    path = artifact(project, kind, {f"galaga/{root}/{suffix}": b""})
    with pytest.raises(ValueError, match="retired runtime"):
        gate.check_artifact(path, project)


@pytest.mark.parametrize(
    "name, data, message",
    (
        ("galaga/algebra.py", b"", "retired runtime file"),
        ("galaga/legacy.pyc", b"", "retired runtime file"),
        ("galaga/core/__pycache__/core.pyc", b"", "cached runtime file"),
        ("galaga/core/core.pyc", b"", "cached runtime file"),
        ("galaga/core/extra.py", b"from .. import algebra", "retired runtime dependency"),
        ("galaga/core/extra.py", b"def f(x): return x . _mul_sign", "retired runtime dependency"),
        ("galaga/names.py", b"# altered", "runtime differs from source"),
        ("galaga/new.py", b"", "runtime differs from source"),
        ("tools/oracle.py", b"", "outside galaga"),
        ("../galaga/hidden.py", b"", "unsafe artifact member"),
        ("/galaga/hidden.py", b"", "unsafe artifact member"),
        ("galaga\\hidden.py", b"", "unsafe artifact member"),
        ("galaga/./hidden.py", b"", "unsafe artifact member"),
        ("galaga//hidden.py", b"", "unsafe artifact member"),
    ),
)
def test_wheel_corruption_cannot_pass(project, name, data, message):
    with pytest.raises(ValueError, match=message):
        gate.check_artifact(artifact(project, "wheel", {name: data}), project)


@pytest.mark.parametrize(
    "before, after, message",
    (
        (b"Name: galaga", b"Name: other", "Name"),
        (b"Version: 2.0.0a2", b"Version: 1.0.0", "Version"),
        (b">=3.11", b">=3.14", "Requires-Python"),
        (b"numpy>=1.24", b"gram>=1", "Requires-Dist"),
    ),
)
@pytest.mark.parametrize("kind", ("wheel", "sdist"))
def test_metadata_cannot_silently_change(project, before, after, message, kind):
    name = "galaga-2.0.0a2.dist-info/METADATA" if kind == "wheel" else "PKG-INFO"
    path = artifact(project, kind, {name: METADATA.replace(before, after)})
    with pytest.raises(ValueError, match=message):
        gate.check_artifact(path, project)


@pytest.mark.parametrize("path", ("legacy", "symbolic_core", "algebra.py", "gram_bridge"))
def test_source_gate_rejects_empty_namespace_directories_and_retired_modules(project, path):
    (project / "galaga" / path).mkdir()
    with pytest.raises(ValueError, match="retired source path"):
        gate.source_runtime(project)


def test_source_gate_allows_local_caches_but_not_missing_runtime(project):
    cache = project / "galaga/__pycache__"
    cache.mkdir()
    (cache / "live.pyc").write_bytes(b"cached")
    assert not any("__pycache__" in name for name in gate.source_runtime(project))
    (project / "galaga/py.typed").unlink()
    with pytest.raises(ValueError, match="missing runtime"):
        gate.source_runtime(project)


@pytest.mark.parametrize(
    "source",
    (
        "import galaga.algebra",
        "import galaga.gram_bridge.catalog",
        "from galaga import gram_bridge",
        "importlib.import_module('galaga.gram_bridge')",
        "def later():\n    from .. import legacy",
        "if TYPE_CHECKING:\n    from ..symbolic_core import Expr",
        "value . _mul_index",
        "getattr(value, '_mul_sign')",
        "importlib.import_module('galaga.legacy')",
        "__import__('galaga.latex_symbols')",
        "import_module('..ops')",
    ),
)
def test_source_scan_detects_nested_relative_and_literal_dynamic_dependencies(source):
    assert gate.source_violations(source, "galaga.facade")


@pytest.mark.parametrize(
    "source",
    (
        "from ..core import Algebra",
        "from galaga import Algebra",
        "from galaga._latex_symbols import LatexSymbols",
        "import galaga.symbolic_core_extra",
        "import_module(variable)",
        "# import galaga.legacy\ntext = 'value._mul_sign'",
    ),
)
def test_source_scan_distinguishes_live_imports_and_historical_text(source):
    assert not gate.source_violations(source, "galaga.facade")


def test_cli_reports_missing_invalid_and_unknown_artifacts(project, capsys):
    for name, content in (("absent.whl", None), ("bad.whl", b"bad zip"), ("bad.tar.gz", b"bad tar"), ("bad.txt", b"")):
        path = project / name
        if content is not None:
            path.write_bytes(content)
        assert gate.main(["--project", str(project), str(path)]) == 1
        assert "artifact check failed" in capsys.readouterr().err


def test_duplicate_wheel_members_are_rejected(project):
    path = artifact(project, "wheel")
    with zipfile.ZipFile(path, "a") as archive, pytest.warns(UserWarning, match="Duplicate"):
        archive.writestr("galaga/names.py", b"other")
    with pytest.raises(ValueError, match="duplicate artifact"):
        gate.check_artifact(path, project)


@pytest.mark.parametrize("kind", ("wheel", "sdist"))
def test_directory_entries_do_not_become_runtime_files(project, kind):
    path = project / ("directories.whl" if kind == "wheel" else "directories.tar.gz")
    if kind == "wheel":
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("galaga/", b"")
            archive.writestr("galaga/file.py", b"")
    else:
        with tarfile.open(path, "w:gz") as archive:
            directory = tarfile.TarInfo("project/galaga")
            directory.type = tarfile.DIRTYPE
            archive.addfile(directory)
            archive.addfile(tarfile.TarInfo("project/galaga/file.py"), io.BytesIO())
    assert gate.read_artifact(path) == ({"galaga/file.py": b""}, kind)


def test_script_entry_point_runs_the_same_cli(project, monkeypatch):
    path = artifact(project, "wheel")
    monkeypatch.setattr(sys, "argv", ["check_galaga_artifact", "--project", str(project), str(path)])
    with pytest.raises(SystemExit) as exit_:
        runpy.run_path(str(ROOT / "scripts/check_galaga_artifact.py"), run_name="__main__")
    assert exit_.value.code == 0


def test_unreadable_sdist_member_is_an_explicit_error(project, monkeypatch):
    path = artifact(project, "sdist")
    monkeypatch.setattr(tarfile.TarFile, "extractfile", lambda *args: None)
    with pytest.raises(ValueError, match="unreadable sdist member"):
        gate.read_artifact(path)


@pytest.mark.parametrize("kind", ("symlink", "multiple_roots", "root_file", "no_metadata", "duplicate_metadata"))
def test_malformed_sdist_or_metadata_is_rejected(project, kind):
    if kind in {"no_metadata", "duplicate_metadata"}:
        path = artifact(project, "wheel", {"other.dist-info/METADATA": METADATA})
        if kind == "no_metadata":
            path = project / "empty.whl"
            with zipfile.ZipFile(path, "w") as archive:
                for name, data in gate.source_runtime(project).items():
                    archive.writestr(name, data)
        with pytest.raises(ValueError, match="exactly one"):
            gate.check_artifact(path, project)
        return
    path = project / "bad.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        if kind == "symlink":
            info = tarfile.TarInfo("galaga/link")
            info.type = tarfile.SYMTYPE
            info.linkname = "../outside"
            archive.addfile(info)
        else:
            for name in ("one/a", "two/b") if kind == "multiple_roots" else ("a",):
                archive.addfile(tarfile.TarInfo(name), io.BytesIO())
    with pytest.raises(ValueError, match="nonregular|one enclosing"):
        gate.read_artifact(path)
