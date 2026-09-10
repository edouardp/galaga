"""Execute the actual companion README fences in their documented order."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPANIONS = ("galaga_anywidget", "galaga_marimo", "galaga_matrix", "galaga_mermaid")


@pytest.mark.parametrize("package", COMPANIONS)
def test_companion_readme_examples(package: str) -> None:
    if package == "galaga_marimo" and sys.version_info < (3, 14):
        pytest.skip("Galaga Marimo requires Python 3.14")
    pytest.importorskip(package)
    path = ROOT / "packages" / package / "README.md"
    source = path.read_text()
    blocks = list(re.finditer(r"^```python\n(.*?)^```$", source, re.MULTILINE | re.DOTALL))
    assert blocks, "README must retain executable examples"
    namespace = {"__name__": "__readme_example__"}
    executed = 0
    for block in blocks:
        code = block.group(1)
        if "import galaga_marimo" in code:
            if sys.version_info < (3, 14):
                continue  # Matrix's optional t-string example; still run its numeric quick start.
            pytest.importorskip("galaga_marimo")
        elif package != "galaga_marimo":
            ast.parse(code, feature_version=(3, 11))
        offset = source.count("\n", 0, block.start(1))
        exec(compile("\n" * offset + code, str(path), "exec"), namespace)
        executed += 1
    assert executed


@pytest.mark.parametrize("package", COMPANIONS)
def test_companion_readme_repository_links_exist(package: str) -> None:
    source = (ROOT / "packages" / package / "README.md").read_text()
    targets = re.findall(r"https://github.com/edouardp/galaga/(?:blob|tree)/galaga_v2/([^\s)]+)", source)
    assert targets
    assert "github.com/edouardp/galaga/blob/main/" not in source
    assert "github.com/edouardp/galaga/tree/main/" not in source
    for target in targets:
        assert (ROOT / target.split("#", 1)[0]).exists(), target
