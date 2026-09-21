"""Compile representative annotation output with Marimo's actual KaTeX.

String snapshots prove that lowering is deterministic, but cannot prove that
the resulting command vocabulary is accepted by the browser renderer. These
tests use the KaTeX JavaScript bundle shipped with Marimo, matching the runtime
that displays the teaching notebooks.
"""

from __future__ import annotations

import json
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import galaga_annotation as ga
from galaga import Algebra, outer_product, presets
from galaga.cga import ConformalModel

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def katex_module_url() -> str:
    if shutil.which("node") is None:
        pytest.skip("standalone KaTeX contract requires Node")
    marimo = pytest.importorskip("marimo")
    assets = Path(marimo.__file__).resolve().parent / "_static" / "assets"
    candidates = tuple(assets.glob("katex-*.js"))
    if not candidates:
        pytest.skip("Marimo installation does not expose its KaTeX bundle")

    # Vite emits a tiny default-export shim beside the large implementation.
    # Importing the shim also resolves its hashed sibling relative to itself.
    module = min(candidates, key=lambda path: path.stat().st_size)
    return module.as_uri()


def _compile_katex(module_url: str, expressions: list[str], *, strict: str = "error") -> None:
    script = r"""
const katex = (await import(process.argv[1])).default;
let input = "";
for await (const chunk of process.stdin) input += chunk;
const { expressions, strict } = JSON.parse(input);
for (const expression of expressions) {
  katex.renderToString(expression, {
    displayMode: true,
    output: "htmlAndMathml",
    strict,
    throwOnError: true,
    trust: true,
  });
}
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script, module_url],
        input=json.dumps({"expressions": expressions, "strict": strict}),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def _measure_katex(module_url: str, expressions: dict[str, str]) -> dict[str, tuple[float, float]]:
    script = r"""
const katex = (await import(process.argv[1])).default;
let input = "";
for await (const chunk of process.stdin) input += chunk;
const expressions = JSON.parse(input);
const dimensions = {};
for (const [name, expression] of Object.entries(expressions)) {
  const tree = katex.__renderToDomTree(expression, {
    displayMode: true,
    strict: "error",
    throwOnError: true,
    trust: true,
  });
  dimensions[name] = [tree.height, tree.depth];
}
process.stdout.write(JSON.stringify(dimensions));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script, module_url],
        input=json.dumps(expressions),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return {name: (float(values[0]), float(values[1])) for name, values in json.loads(result.stdout).items()}


def _render_katex_markup(module_url: str, expression: str) -> str:
    script = r"""
const katex = (await import(process.argv[1])).default;
let expression = "";
for await (const chunk of process.stdin) expression += chunk;
process.stdout.write(katex.renderToString(expression, {
  displayMode: true,
  output: "htmlAndMathml",
  strict: "error",
  throwOnError: true,
  trust: true,
}));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script, module_url],
        input=expression,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_every_marker_compiles_with_standalone_katex(katex_module_url: str) -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    value = e1 + e2
    markers = (
        "none",
        "arrow",
        "rule",
        "brace",
        "underline",
        "box",
        "underbrace",
        "underbracket",
        "overbrace",
        "undergroup",
        "overgroup",
        "overline",
        "overbracket",
    )
    expressions = [ga.annotate(value, label="concept", marker=marker).latex() for marker in markers]
    _compile_katex(katex_module_url, expressions)


def test_composed_spans_and_clearance_compile_with_standalone_katex(katex_module_url: str) -> None:
    algebra = Algebra(4)
    e1, e2, e3, e4 = algebra.basis_vectors()
    value = e1 + e2 - e3 + e4
    expressions = [
        ga.annotator(
            ga.on(ga.terms(e1, e2, e3), background="#b8e6bf", join=True),
            ga.on(
                ga.terms(e2, e3, e4),
                label="inner",
                marker="overgroup",
                color="#0099cc",
                clearance="4px",
                overlay=True,
                join=True,
            ),
            ga.on(ga.terms(e1, e2), label="lower", marker="undergroup", join=True),
            ga.on(ga.sign(e3), background="#fff3cd"),
        )(value).latex(),
        ga.annotator(
            ga.on(ga.terms(e1, e2, e3), label="first", join=True),
            ga.on(ga.terms(e1, e2, e3), label="second", join=True),
        )(value).latex(),
    ]
    _compile_katex(katex_module_url, expressions)


def test_overlay_reserves_outer_katex_bounds(katex_module_url: str) -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    value = e1 + e2 + e3
    highlighted = ga.annotator(
        ga.on(ga.terms(e1, e2), background="#b8e6bf", join=True),
    )(value).latex()
    above = ga.annotator(
        ga.on(ga.terms(e1, e2), background="#b8e6bf", join=True),
        ga.on(ga.terms(e1, e2), label="above", marker="overgroup", join=True),
    )(value).latex()
    below = ga.annotator(
        ga.on(ga.terms(e1, e2), background="#b8e6bf", join=True),
        ga.on(ga.terms(e1, e2), label="below", marker="undergroup", join=True),
    )(value).latex()
    direct_above = ga.annotate(
        value,
        label="direct above",
        marker="overgroup",
        overlay=True,
    ).latex()
    direct_below = ga.annotate(
        value,
        label="direct below",
        marker="undergroup",
        overlay=True,
    ).latex()

    # The reservation precedes the base fill; it is not part of the colorbox.
    assert above.startswith(r"\vphantom{") and r"}\colorbox{#b8e6bf}" in above
    assert below.startswith(r"\vphantom{") and r"}\colorbox{#b8e6bf}" in below

    dimensions = _measure_katex(
        katex_module_url,
        {
            "highlighted": highlighted,
            "above": above,
            "below": below,
            "plain": value.latex(content="value"),
            "direct_above": direct_above,
            "direct_below": direct_below,
        },
    )
    highlighted_height, highlighted_depth = dimensions["highlighted"]
    above_height, _ = dimensions["above"]
    _, below_depth = dimensions["below"]
    assert above_height > highlighted_height
    assert below_depth > highlighted_depth
    plain_height, plain_depth = dimensions["plain"]
    direct_above_height, _ = dimensions["direct_above"]
    _, direct_below_depth = dimensions["direct_below"]
    assert direct_above_height > plain_height
    assert direct_below_depth > plain_depth


def test_wide_external_label_has_zero_horizontal_layout_width(katex_module_url: str) -> None:
    algebra = Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    rendered = ga.annotator(
        ga.on(ga.terms(e1, e2), background="#b8e6bf", join=True),
        ga.on(
            ga.terms(e1, e2),
            label="a much wider explanatory annotation",
            marker="overbrace",
            join=True,
        ),
    )(e1 + e2 + e3).latex()

    assert r"^{\mathclap{\text{a much wider explanatory annotation}}}" in rendered
    markup = _render_katex_markup(katex_module_url, rendered)
    # KaTeX lowers mathclap to a centred zero-width mpadded node. The label
    # remains visible, but cannot widen and recenter the brace's phantom body.
    assert markup.count('<mpadded lspace="-0.5width" width="0px">') >= 2


def test_cga_cocarrier_callouts_reserve_their_height(katex_module_url: str) -> None:
    cga = ConformalModel(Algebra(config=presets.lengyel_cga(), expr=True), expr=True)
    dipole = outer_product(cga.up((0.75, 1.0, 2.0)), cga.up((-0.25, 0.1, 0.2)))
    incidence = ga.highlight_cga(cga, decomposition="incidence")(dipole).latex()
    components = ga.highlight_cga(cga, decomposition="components")(dipole).latex()

    assert r"\vphantom{\textcolor{#0099cc}{\overbrace{" in incidence
    assert r"^{\mathclap{\text{cocarrier normal}}}" in incidence
    dimensions = _measure_katex(
        katex_module_url,
        {"incidence": incidence, "components": components},
    )
    incidence_height, _ = dimensions["incidence"]
    components_height, _ = dimensions["components"]
    assert incidence_height > components_height


def test_annotation_notebooks_emit_parseable_katex(katex_module_url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    if sys.version_info < (3, 14):
        pytest.skip("annotation notebooks use native t-strings")
    pytest.importorskip("galaga_marimo")

    expressions: list[str] = []
    expression_latex = ga.Annotated.latex
    matrix_latex = ga.AnnotatedMatrix.latex

    def capture_expression(self, *args, **kwargs) -> str:
        rendered = expression_latex(self, *args, **kwargs)
        expressions.append(rendered)
        return rendered

    def capture_matrix(self, *args, **kwargs) -> str:
        rendered = matrix_latex(self, *args, **kwargs)
        expressions.append(rendered)
        return rendered

    monkeypatch.setattr(ga.Annotated, "latex", capture_expression)
    monkeypatch.setattr(ga.AnnotatedMatrix, "latex", capture_matrix)

    for notebook in sorted((ROOT / "examples" / "annotation").glob("*.py")):
        runpy.run_path(str(notebook))["app"].run()

    assert expressions
    # The notebooks intentionally include Unicode labels and RGA operator
    # glyphs. Marimo renders those in KaTeX's normal non-strict mode; this
    # contract is concerned with fatal parser errors and unsupported commands.
    _compile_katex(katex_module_url, list(dict.fromkeys(expressions)), strict="ignore")
