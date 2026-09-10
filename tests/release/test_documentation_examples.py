"""Keep corrected, copyable documentation examples executable."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GUIDES = (
    ("README.md", None),
    ("docs/what_is_dual.md", None),
    ("docs/core/inner-products-contractions-and-interior-products.md", None),
    ("packages/galaga_matrix/docs/specs/basis-change.md", "Examples"),
    ("packages/galaga_matrix/docs/specs/spinor-ket-bra.md", "Examples"),
    ("packages/galaga_matrix/docs/specs/quaternion-unified-storage.md", "Examples"),
)


@pytest.mark.parametrize("relative,section", GUIDES, ids=[entry[0] for entry in GUIDES])
def test_documentation_python_examples(relative: str, section: str | None) -> None:
    if relative.startswith("packages/galaga_matrix/"):
        pytest.importorskip("galaga_matrix")
    path = ROOT / relative
    source = path.read_text()
    selected = source
    if section is not None:
        selected = source.split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
    blocks = list(re.finditer(r"^```python\n(.*?)^```$", selected, re.M | re.S))
    assert blocks, "The documented executable section must not disappear"
    for block in blocks:
        code = block.group(1)
        ast.parse(code, feature_version=(3, 11))
        namespace = {"__name__": "__documentation_example__"}
        line_offset = source.count("\n", 0, source.index(code))
        exec(compile("\n" * line_offset + code, str(path), "exec"), namespace)
        if "ket" in namespace:
            import numpy as np

            assert namespace["ket"].kind == "ket"
            assert namespace["bra"].kind == "bra"
            assert namespace["result"].kind == "ket"
            np.testing.assert_allclose(
                namespace["from_spinor_column"](namespace["ket_weyl"]).data,
                namespace["R"].data,
                atol=1e-12,
            )
