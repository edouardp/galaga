"""Keep the package's copyable README examples tied to the public v2 API."""

import ast
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
README = ROOT / "packages/galaga/README.md"
SOURCE = README.read_text(encoding="utf-8")
PYTHON_BLOCKS = list(re.finditer(r"^```python\n(.*?)^```$", SOURCE, re.MULTILINE | re.DOTALL))
REFERENCES = dict(re.findall(r"^\[([^\]]+)\]: (\S+)$", SOURCE, re.MULTILINE))


@pytest.mark.parametrize(
    "block",
    PYTHON_BLOCKS,
    ids=[f"line-{SOURCE.count(chr(10), 0, match.start()) + 2}" for match in PYTHON_BLOCKS],
)
def test_readme_python_examples_are_self_contained(block, monkeypatch):
    """Run each actual fence in isolation, including its mathematical assertions."""
    code = block.group(1)
    if "import galaga_marimo" in code:
        if sys.version_info < (3, 14):
            pytest.skip("The explicitly labelled Marimo example uses Python 3.14 t-strings")
        pytest.importorskip("marimo")
        monkeypatch.syspath_prepend(str(ROOT / "packages/galaga_marimo"))
    else:
        # A newer test interpreter must not hide syntax incompatible with our floor.
        ast.parse(code, feature_version=(3, 11))

    # Preserve README line numbers in tracebacks without pre-seeding other examples.
    line_offset = SOURCE.count("\n", 0, block.start(1))
    namespace = {"__name__": "__readme_example__"}
    exec(compile("\n" * line_offset + code, str(README), "exec"), namespace)

    if "import galaga_marimo" in code:
        markup = namespace["document"].text
        assert "marimo-tex" in markup
        assert r"\begin{array}" in markup
        assert "<pre>" not in markup
        equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.DOTALL)
        assert equations
        assert all("$" not in equation for equation in equations)


def test_readme_examples_and_references_are_discovered():
    """Guard against vacuous passes if Markdown fence/link syntax changes."""
    assert PYTHON_BLOCKS
    assert REFERENCES
    used = set(re.findall(r"(?<!!)\[[^\]\n]+\]\[([^\]\n]+)\]", SOURCE))
    assert used == REFERENCES.keys()


@pytest.mark.parametrize("label,url", REFERENCES.items(), ids=list(REFERENCES))
def test_readme_links_target_existing_v2_repository_files(label, url):
    """Package-index links must be absolute and point to v2 rather than old main."""
    prefix = "https://github.com/edouardp/galaga/blob/galaga_v2/"
    assert url.startswith(prefix), f"{label}: expected an absolute v2 documentation link"
    path = ROOT / url.removeprefix(prefix)
    assert path.is_file(), f"{label}: missing link target {path}"
