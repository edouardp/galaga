# Legacy/Facade LaTeX Rendering Parity

The rendering parity audit runs the core-backed Galaga 2 facade and compares
its output with frozen Galaga v1 observations. It also checks the reviewed v2
outputs independently, so an accepted v1/v2 difference cannot conceal a new
regression. The audit no longer imports or executes the legacy engine.

The 73 historical observations were captured from commit
`d98c9f463ecd532e7d9c5b3bdc82aa471ecad1bc` before removing the live adapter and
reproduced against that commit's original audit. The fixture records the
capture's Python and NumPy versions, shared operation inventory, exact LaTeX,
coefficients, and legacy rendering errors. See the
[baseline maintenance notes](../../packages/galaga/tools/baselines/README.md)
and [ADR-092](../adrs/092-frozen-historical-rendering-oracles.md).

This is a migration oracle, not a requirement that Galaga 2 reproduce every
legacy token forever. An exact match is useful evidence. A difference is a
review item that must be classified as an intended correction, an accepted
presentation change, a missing v2 notation rule, or a defect.

The independent [exact configured rendering contract](exact-rendering-contracts.md)
stores reviewed literal LaTeX for representative implementation, algebra,
display, and compound-expression combinations. It catches shared mistakes and
facade-only policy regressions that a differential comparison cannot detect.

## Run the audit

From the repository root:

```shell
PYTHONPATH=packages/galaga python -m tools.audit_rendering_parity \
  --repository . --check
```

For a valid case inventory, the command writes a timestamped report under
`docs/v2/rendering-parity-reports/`. The `--check` option fails if the case or
operation inventory is incomplete, the difference IDs no longer match the
reviewed ledger, or any facade output differs from its reviewed v2 baseline.
Use an explicit output path for a disposable CI or local run:

```shell
PYTHONPATH=packages/galaga python -m tools.audit_rendering_parity \
  --repository . --output /tmp/galaga-latex-parity.md --check
```

The historical checked audit with visual rendering is
[LaTeX parity report, 2026-07-19 18:46](rendering-parity-reports/latex-parity-20260719-184624+1200.md).

## What one case compares

Each retained recipe is evaluated only against the facade:

| Reference or implementation | Algebra and display contract |
|---|---|
| Frozen legacy v1 | Captured `galaga.legacy.Algebra` and `Multivector.display()` outputs |
| Reviewed v2 reference | Captured and reviewed facade outputs, including accepted corrections |
| Live core facade v2 | `galaga.Algebra` and `DisplayPolicy("full")` |

The audit compares these channels independently:

| Channel | Purpose |
|---|---|
| Expression | Operation notation, precedence, and grouping |
| Value | Concrete coefficient and blade rendering |
| Full | Teaching form: distinct name, expression, and value |
| Rich | Notebook `_repr_latex_` wrapper and full-display behavior |
| Coefficients | Whether a visual difference conceals a numeric difference |

LaTeX channels compare exactly. Coefficients use the existing
`rtol=1e-12, atol=1e-12` tolerance with equal lengths required; NumPy shape
broadcasting is not allowed. This is a regression-test tolerance, not a change
to multivector equality or hashing.

The default profile uses the three-dimensional Euclidean algebra. A separate
Lengyel RGA profile exercises its signature, blade convention, notation, and
value typography. Cases also cover nested precedence, deduplication, near-zero
elision, six-significant-digit formatting, and anonymous values.

## One inventory, three consumers

`tools.rendering_parity.CASES` is the canonical case registry. Both the command
and the permanent Pytest gate consume it. This avoids a prose checklist, a test
inventory, and a reporting inventory drifting apart.

The test suite enforces that:

- case keys are unique and match the frozen inventory;
- captured shared operation IDs remain in the facade catalog and are exercised;
- exact successes remain exact;
- every difference is present in `DIFFERENCE_LEDGER`;
- every ledger entry is still observed;
- all live facade results match the reviewed v2 outputs, including cases where
  the legacy renderer failed; and
- a fresh process runs the complete audit with legacy imports blocked.

The ledger maps a stable `profile/case` key to its accepted review decision. A
new difference therefore fails the check as unclassified. When a v2 change
resolves a difference, the stale ledger entry also fails the check. The author
must inspect the newly generated report and deliberately update the ledger.
The ledger alone is not permission for arbitrary further changes to that case:
the separate reviewed-v2 gate pins every compared channel and its coefficients.

Generated reports pre-check **Accept v2** and include the ledger rationale for
reviewed differences only when the v2 output still matches its reference.
Unclassified differences retain blank checkboxes; changed reviewed outputs are
listed as facade regressions and are not pre-approved.

## Report structure

Reports are designed for direct review in Typora or another Markdown editor:

1. metadata, historical source commit, and a count summary;
2. a compact success list, where each entry says **expression succeeded**;
3. a reviewed-facade regression summary and one detailed section per difference;
4. the expression's mathematical intent;
5. one display-math block containing the complete v1 and v2 teaching forms;
6. one source block containing those same complete emitted LaTeX strings;
7. case-level decision checkboxes and a reviewer notes field; and
8. operation and profile coverage.

Exact LaTeX is intentionally compared rather than rendered pixels. It exposes
grouping, command, wrapper, whitespace, and typography decisions and produces
small, reviewable version-control diffs. The human report shows only the full
teaching form, first typeset and then as emitted source. The audit and Pytest
gate retain their deeper expression, value, rich-wrapper, and coefficient
comparisons without repeating those channels in the report.

## Review outcome

The audit exercises 73 expressions, all 45 captured shared operation IDs, and
60 operation IDs in total. The initial run
had 16 exact matches and 57 differences. After review and remediation, 65
expressions match exactly and eight differences are explicit Galaga 2
decisions.

The remediation:

- ported the reviewed conventional operation notation, grouping, compact
  function calls, powers, duals, projections, transcendental forms, sandwich,
  and metric-regressive definition layout into semantic `RenderRule` data;
- fixed reflected addition provenance so `1 + a` is not recorded as `a + 1`;
- stopped default `unit`, `inverse`, `log`, and `sqrt` tolerances leaking into
  expression display while retaining non-default values for reevaluation;
- made Lengyel RGA vector blades use the same bold LaTeX typography as its
  higher-grade blades; and
- retained exactly eight accepted differences:
  - four legacy outer-transcendental renders raise `RecursionError`, while the
    facade renders successfully;
  - `lie_bracket` and `jordan_product` use the corrected unscaled definitions
    and the corresponding unscaled bracket/brace notation;
  - Galaga 2 consistently uses `\widetilde` for reverse; and
  - multi-grade projection retains provenance as
    `\langle x \rangle_{[0,2]}`, where v1 discarded the expression.

The subsequent conventional contraction-symbol change added two reviewed
differences: left and right contraction now use the floor-symbol pair. The
Phase 9 capture therefore has **63 exact matches and ten accepted differences**.
All 73 live facade outputs must match their reviewed v2 references.

The generated report, executable ledger, and pinned v2 outputs are authoritative
for the current tree.

## Review and retirement workflow

For each difference:

1. inspect its expression intent, coefficients, and differing channels;
2. check exactly one of **Accept v2**, **Match legacy v1**, **Prefer another
   rendering**, or **Investigate as defect**;
3. use the notes field for a preferred third form or a decision that applies
   only to one channel;
4. save the annotated report so its stable case IDs and decisions can be
   promoted into the executable ledger and implementation backlog;
5. implement a notation or renderer change only when that decision calls for
   one;
6. rerun the audit and focused parity tests; and
7. remove or revise the ledger entry and the affected reviewed v2 observation
   only after reviewing the new report. Do not rewrite the historical v1
   observation to match a new implementation.

The audit's legacy adapter has been retired. Its case registry remains a
semantic rendering regression suite backed by historical data. Other legacy
tests, the configured dual-implementation contracts, and the benchmark still
need retirement before deleting the engine; this checkpoint does not complete
Phase 9 or change the shipped public API.
