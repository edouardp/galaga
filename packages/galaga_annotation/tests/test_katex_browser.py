"""Measure annotation geometry in the same browser layout engine as notebooks.

String snapshots and standalone KaTeX compilation catch structural and syntax
regressions.  These tests add the missing contract: Chromium must place the
visible marker and label over the pixels occupied by their semantic target.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

import galaga_annotation as ga
from galaga import Algebra


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


@contextmanager
def _asset_server(directory: Path) -> Iterator[str]:
    handler = partial(_QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.fixture(scope="module")
def browser_page():
    marimo = pytest.importorskip("marimo")
    playwright = pytest.importorskip("playwright.sync_api")
    assets = Path(marimo.__file__).resolve().parent / "_static" / "assets"
    modules = tuple(assets.glob("katex-*.js"))
    if not modules:
        pytest.skip("Marimo installation does not expose its KaTeX bundle")
    module = min(modules, key=lambda path: path.stat().st_size)
    stylesheets = tuple(path for path in assets.glob("*.css") if ".katex" in path.read_text())
    if not stylesheets:
        pytest.skip("Marimo installation does not expose its KaTeX stylesheet")
    stylesheet = min(stylesheets, key=lambda path: path.stat().st_size)

    with _asset_server(assets) as origin, playwright.sync_playwright() as runtime:
        try:
            browser = runtime.chromium.launch(headless=True)
        except playwright.Error as error:
            message = "Chromium is unavailable; run `make install-browser-tests`"
            if os.environ.get("GALAGA_REQUIRE_BROWSER_TESTS") == "1":
                pytest.fail(f"{message}: {error}")
            pytest.skip(message)
        page = browser.new_page(viewport={"width": 1000, "height": 500}, device_scale_factor=1)
        page.goto(origin)
        page.add_style_tag(url=f"{origin}/{stylesheet.name}")
        page.evaluate(
            """
            async ({moduleUrl}) => {
              window.__galagaKatex = (await import(moduleUrl)).default;
            }
            """,
            {"moduleUrl": f"{origin}/{module.name}"},
        )
        try:
            yield page
        finally:
            browser.close()


def _tag_last(source: str, fragment: str, element_id: str) -> str:
    before, match, after = source.rpartition(fragment)
    assert match, f"cannot instrument missing fragment {fragment!r}"
    return before + rf"\htmlId{{{element_id}}}{{{match}}}" + after


def _render(page: Any, latex: str) -> None:
    page.evaluate(
        """
        async ({latex}) => {
          document.body.innerHTML = '<main id="fixture"></main>';
          window.__galagaKatex.render(latex, document.querySelector('#fixture'), {
            displayMode: true,
            output: 'htmlAndMathml',
            strict: (errorCode) => errorCode === 'htmlExtension' ? 'ignore' : 'error',
            throwOnError: true,
            trust: true,
          });
          await document.fonts.ready;
        }
        """,
        {"latex": latex},
    )


def _box(page: Any, selector: str, *, last: bool = False) -> dict[str, float]:
    locator = page.locator(selector)
    assert locator.count(), f"missing browser element for {selector}"
    box = (locator.last if last else locator).bounding_box()
    assert box is not None, f"missing browser geometry for {selector}"
    return box


def _leaf_text_box(page: Any, text: str, *, last: bool = False) -> dict[str, float]:
    boxes = page.locator(".katex-html span").evaluate_all(
        """
        (elements, expected) => elements
          .filter((element) => element.childElementCount === 0 && element.textContent === expected)
          .map((element) => {
            const rect = element.getBoundingClientRect();
            return {x: rect.x, y: rect.y, width: rect.width, height: rect.height};
          })
        """,
        text,
    )
    assert boxes, f"missing browser geometry for leaf text {text!r}"
    return boxes[-1] if last else boxes[0]


def _center_x(box: dict[str, float]) -> float:
    return box["x"] + box["width"] / 2


def _union_x(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    start = min(left["x"], right["x"])
    stop = max(left["x"] + left["width"], right["x"] + right["width"])
    return {"x": start, "width": stop - start}


def test_reversion_bivector_callout_is_centred_on_its_visible_term(browser_page) -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    value = algebra.scalar(0.573576) - 0.819152 * (e1 ^ e2)
    rendered = ga.annotator(
        ga.on(ga.grade(0), label="unchanged", marker="underbrace", color="#0072B2"),
        ga.on(ga.grade(2), label="negated", marker="underbrace", color="#D55E00"),
    )(value).latex()
    rendered = _tag_last(rendered, r"0.819152 e_{12}", "bivector-target")
    _render(browser_page, rendered)

    unsigned_body = _box(browser_page, ".katex-html #bivector-target")
    sign = _box(browser_page, ".katex-html .mbin", last=True)
    target = _union_x(sign, unsigned_body)
    brace = _box(browser_page, ".katex-html .stretchy", last=True)
    label = _box(browser_page, ".katex-html .clap .text", last=True)
    assert _center_x(brace) == pytest.approx(_center_x(target), abs=0.5)
    assert _center_x(label) == pytest.approx(_center_x(target), abs=0.5)
    assert brace["width"] == pytest.approx(target["width"], abs=0.5)


def test_leading_negative_callout_preserves_unary_sign_geometry(browser_page) -> None:
    algebra = Algebra(1)
    (e1,) = algebra.basis_vectors()
    value = algebra.scalar(-0.573576) + e1
    rendered = ga.annotate(
        value,
        ga.on(ga.grade(0), label="negated", marker="underbrace", color="#0072B2"),
    ).latex()
    rendered = _tag_last(rendered, "0.573576", "scalar-target")
    _render(browser_page, rendered)

    unsigned_body = _box(browser_page, ".katex-html #scalar-target")
    sign = _leaf_text_box(browser_page, "−", last=True)
    target = _union_x(sign, unsigned_body)
    brace = _box(browser_page, ".katex-html .stretchy", last=True)
    label = _box(browser_page, ".katex-html .clap .text", last=True)

    assert _center_x(brace) == pytest.approx(_center_x(target), abs=0.5)
    assert _center_x(label) == pytest.approx(_center_x(target), abs=0.5)
    assert brace["width"] == pytest.approx(target["width"], abs=0.5)


def test_wide_label_does_not_widen_or_shift_its_marker(browser_page) -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    rendered = ga.annotate(
        e1 + e2,
        ga.on(
            ga.terms(e1, e2),
            label="a much wider explanatory annotation",
            marker="overbrace",
            join=True,
        ),
    ).latex()
    rendered = _tag_last(rendered, r"e_{1} + e_{2}", "wide-label-target")
    _render(browser_page, rendered)

    target = _box(browser_page, ".katex-html #wide-label-target")
    brace = _box(browser_page, ".katex-html .stretchy", last=True)
    label = _box(browser_page, ".katex-html .clap .text", last=True)

    assert label["width"] > target["width"]
    assert _center_x(brace) == pytest.approx(_center_x(target), abs=0.5)
    assert _center_x(label) == pytest.approx(_center_x(target), abs=0.5)
    assert brace["width"] == pytest.approx(target["width"], abs=0.5)


def test_sign_fill_measurement_does_not_cover_an_earlier_scalar(browser_page) -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    value = algebra.scalar(7.125) + 2 * e1 - 3 * (e1 ^ e2)
    rendered = ga.annotator(
        ga.on(ga.grade(2), background="#FDE7D9", color="#D55E00", join=True),
        ga.on(ga.sign(e1 ^ e2), background="#FDE7D9"),
        ga.on(ga.grade(0), label="grade 0", marker="underbrace"),
        ga.on(ga.grade(1), label="grade 1", marker="underbrace"),
        ga.on(ga.grade(2), label="grade 2", marker="underbrace"),
    )(value).latex()
    rendered = _tag_last(rendered, "7.125", "scalar-target")
    _render(browser_page, rendered)

    scalar = _box(browser_page, ".katex-html #scalar-target")
    backgrounds = browser_page.locator(".katex-html span").evaluate_all(
        """
        (elements) => elements
          .filter((element) => getComputedStyle(element).backgroundColor === 'rgb(253, 231, 217)')
          .map((element) => {
            const rect = element.getBoundingClientRect();
            return {x: rect.x, width: rect.width};
          })
          .filter((rect) => rect.width > 0)
        """
    )
    scalar_start = scalar["x"]
    scalar_stop = scalar["x"] + scalar["width"]
    assert all(box["x"] >= scalar_stop or box["x"] + box["width"] <= scalar_start for box in backgrounds)
