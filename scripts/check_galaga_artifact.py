"""Verify a Galaga wheel or sdist against the local, legacy-free runtime tree.

This read-only check never extracts or imports an artifact. It is also usable
from a source distribution: pass its extracted project directory as --project.
"""

from __future__ import annotations

import argparse
import ast
import sys
import tarfile
import tomllib
import zipfile
from email.parser import BytesParser
from importlib.util import resolve_name
from pathlib import Path, PurePosixPath

RETIRED_ROOTS = frozenset(
    {
        "algebra",
        "basis_blade",
        "blade_convention",
        "expr",
        "latex_build",
        "latex_emit",
        "latex_nodes",
        "latex_rewrite",
        "latex_symbols",
        "lazy",
        "legacy",
        "notation",
        "ops",
        "symbolic",
        "symbolic_core",
    }
)
PRIVATE_TABLES = frozenset({"_mul_index", "_mul_sign"})
REQUIRED_RUNTIME = frozenset(
    {
        "galaga/__init__.py",
        "galaga/core/__init__.py",
        "galaga/core/_backends.py",
        "galaga/facade/__init__.py",
        "galaga/facade/catalog.py",
        "galaga/expression/__init__.py",
        "galaga/rendering/__init__.py",
        "galaga/names.py",
        "galaga/_latex_symbols.py",
        "galaga/py.typed",
    }
)


def retired_module(name: str) -> bool:
    parts = name.split(".")
    return len(parts) > 1 and parts[0] == "galaga" and parts[1] in RETIRED_ROOTS


def source_violations(source: str, package: str) -> list[tuple[int, str]]:
    """Inspect all lexical scopes, including literal dynamic imports/lookups."""
    violations = []
    for node in ast.walk(ast.parse(source)):
        names = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = resolve_name("." * node.level + (node.module or ""), package)
            names = [module + "." + alias.name for alias in node.names]
        elif isinstance(node, ast.Attribute) and node.attr in PRIVATE_TABLES:
            violations.append((node.lineno, node.attr))
        elif isinstance(node, ast.Call):
            function = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
            if function in {"__import__", "import_module"} and node.args:
                argument = node.args[0]
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    names = [resolve_name(argument.value, package)]
            if function == "getattr" and len(node.args) >= 2:
                attribute = node.args[1]
                if isinstance(attribute, ast.Constant) and attribute.value in PRIVATE_TABLES:
                    violations.append((node.lineno, attribute.value))
        violations.extend((node.lineno, name) for name in names if retired_module(name))
    return violations


def check_runtime(members: dict[str, bytes]) -> dict[str, bytes]:
    runtime = {name: data for name, data in members.items() if name.startswith("galaga/")}
    missing = REQUIRED_RUNTIME - runtime.keys()
    if missing:
        raise ValueError(f"missing runtime files: {sorted(missing)}")
    for name, data in runtime.items():
        path = PurePosixPath(name)
        root = path.parts[1].split(".", 1)[0]
        if root in RETIRED_ROOTS:
            raise ValueError(f"retired runtime file: {name}")
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            raise ValueError(f"cached runtime file: {name}")
        if path.suffix == ".py":
            package = ".".join(path.parts[:-1])
            violations = source_violations(data.decode("utf-8"), package)
            if violations:
                raise ValueError(f"retired runtime dependency in {name}: {violations}")
    return runtime


def source_runtime(project: Path) -> dict[str, bytes]:
    members = {}
    for path in (project / "galaga").rglob("*"):
        relative = path.relative_to(project).as_posix()
        # An empty retired directory can still be an importable namespace package.
        root = PurePosixPath(relative).parts[1].split(".", 1)[0]
        if root in RETIRED_ROOTS:
            raise ValueError(f"retired source path: {relative}")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            members[relative] = path.read_bytes()
    return check_runtime(members)


def _member_name(name: str) -> str:
    path = PurePosixPath(name)
    if "\\" in name or path.is_absolute() or any(part in {"", ".", ".."} for part in name.split("/")):
        raise ValueError(f"unsafe artifact member: {name}")
    return name


def read_artifact(path: Path) -> tuple[dict[str, bytes], str]:
    members: dict[str, bytes] = {}

    def directory(name: str, *, sdist: bool = False) -> None:
        parts = PurePosixPath(_member_name(name.rstrip("/"))).parts
        parts = parts[1:] if sdist else parts
        if len(parts) > 1 and parts[0] == "galaga" and parts[1].split(".", 1)[0] in RETIRED_ROOTS:
            raise ValueError(f"retired runtime directory: {name}")

    def add(name: str, data: bytes) -> None:
        name = _member_name(name)
        if name in members:
            raise ValueError(f"duplicate artifact member: {name}")
        members[name] = data

    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            for entry in archive.infolist():
                if entry.is_dir():
                    directory(entry.filename)
                else:
                    add(entry.filename, archive.read(entry))
        kind = "wheel"
    elif path.name.endswith(".tar.gz"):
        with tarfile.open(path, "r:gz") as archive:
            for entry in archive:
                if entry.isdir():
                    directory(entry.name, sdist=True)
                    continue
                if not entry.isfile():
                    raise ValueError(f"nonregular sdist member: {entry.name}")
                stream = archive.extractfile(entry)
                if stream is None:
                    raise ValueError(f"unreadable sdist member: {entry.name}")
                with stream:
                    add(entry.name, stream.read())
        roots = {name.split("/", 1)[0] for name in members}
        if len(roots) != 1 or any("/" not in name for name in members):
            raise ValueError("sdist must have one enclosing project directory")
        members = {name.split("/", 1)[1]: data for name, data in members.items()}
        kind = "sdist"
    else:
        raise ValueError("expected a .whl or .tar.gz artifact")
    return members, kind


def check_artifact(path: Path, project: Path) -> str:
    expected = source_runtime(project)
    metadata = tomllib.loads((project / "pyproject.toml").read_text())["project"]
    members, kind = read_artifact(path)
    actual = check_runtime(members)
    if actual != expected:
        changed = sorted(name for name in actual.keys() | expected.keys() if actual.get(name) != expected.get(name))
        raise ValueError(f"runtime differs from source: {changed}")
    if kind == "wheel":
        metadata_paths = [name for name in members if name.endswith(".dist-info/METADATA")]
        if any(not name.startswith("galaga/") and ".dist-info/" not in name for name in members):
            raise ValueError("wheel contains files outside galaga and its distribution metadata")
    else:
        metadata_paths = [name for name in members if name == "PKG-INFO"]
    if len(metadata_paths) != 1:
        raise ValueError("expected exactly one distribution metadata file")
    message = BytesParser().parsebytes(members[metadata_paths[0]])
    for field, key in (("Name", "name"), ("Version", "version"), ("Requires-Python", "requires-python")):
        if message[field] != metadata[key]:
            raise ValueError(f"{field} does not match project metadata")
    requirements = {value.replace(" ", "") for value in message.get_all("Requires-Dist", [])}
    expected_requirements = {value.replace(" ", "") for value in metadata["dependencies"]}
    if requirements != expected_requirements:
        raise ValueError("Requires-Dist does not match declared dependencies")
    return f"{path.name}: {kind}, {len(actual)} source-identical runtime files, no legacy engine"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("artifacts", type=Path, nargs="+")
    args = parser.parse_args(argv)
    try:
        for artifact in args.artifacts:
            print(check_artifact(artifact, args.project))
    except (OSError, ValueError, tarfile.TarError, zipfile.BadZipFile) as error:
        print(f"artifact check failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
