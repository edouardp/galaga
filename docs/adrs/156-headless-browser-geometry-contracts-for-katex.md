---
status: accepted
date: 2026-09-20
deciders: edouard
---

# ADR-156: Headless Browser Geometry Contracts for KaTeX

## Context

LaTeX snapshots prove deterministic lowering, and importing Marimo's bundled
KaTeX through Node proves that the generated command vocabulary parses. Neither
test runs a browser layout engine. They therefore cannot detect a marker whose
phantom has the right source text but the wrong pixel extent, a label that
recentres its marker, or a zero-width overlay that changes TeX math-atom
spacing.

Desktop Safari is useful for manual notebook review but requires interactive
OS permissions, depends on user state, and is unsuitable as an automated test
contract. Full screenshot baselines are also sensitive to operating system,
font rasterization, browser version and device scale.

## Decision

Add Playwright to the root `browser-test` dependency group and pin its resolved
version in `uv.lock`. `make install-browser-tests` installs Playwright's pinned
Chromium headless shell and its CI system dependencies;
`make test-galaga-annotation-browser` installs that browser and runs the
required browser suite. The ordinary annotation suite may skip these tests
when the browser executable is absent, while the dedicated target sets
`GALAGA_REQUIRE_BROWSER_TESTS=1` so absence is a failure.

Serve Marimo's installed static asset directory from a loopback-only HTTP
server during the test. Headless Chromium imports the exact KaTeX JavaScript
module and stylesheet distributed with that Marimo installation. Tests render
the annotation package's emitted LaTeX with `trust=True`; test-only `\htmlId`
markers expose semantic target bounds without changing production output.

Treat browser geometry as the primary visual contract. Compare target, marker
and label centres and widths through `getBoundingClientRect()` with a subpixel
tolerance. Keep element screenshots available for diagnosis, but do not make
cross-platform pixel images the default gate. Curated screenshot baselines may
be added later for one fixed CI image if geometric assertions prove
insufficient.

## Consequences

- Annotation alignment failures are measured rather than corrected by eye or
  arbitrary `\mkern` guesses.
- Tests cover the browser layout phase that Node render-tree and string tests
  cannot observe.
- Local and future CI execution use a hermetic headless Chromium build and do
  not need Safari, Accessibility permission, or a desktop session.
- The optional test setup downloads a large browser artifact, so it remains a
  distinct dependency group and Make target rather than a runtime dependency.
- KaTeX or Marimo asset changes can surface as explicit geometry-contract
  failures even when emitted LaTeX remains unchanged.

## Validation

- A non-leading negative bivector callout must cover the visible minus,
  coefficient and blade with matching marker and label centres.
- A leading unary minus must retain its unary spacing while its callout matches
  the complete signed term.
- A label wider than its selected expression must remain centred without
  widening or shifting the marker.
- A decorated sign copied for callout measurement must not paint a phantom
  background over an earlier visible term.

## Related

- [ADR-147](147-katex-annotation-lowering-and-decoration-wrappers.md): KaTeX
  decoration lowering.
- [ADR-154](154-independent-external-span-overlays.md): independent external
  span overlays and sign-aware phantom measurement.
- [SPEC-015](../specs/SPEC-015-expression-and-matrix-annotations.md): annotation
  capability and rendering specification.
