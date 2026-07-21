# Legacy/Facade LaTeX Rendering Parity

The rendering parity audit runs the retained Galaga v1 algebra and the
core-backed Galaga 2 facade side by side. It builds equivalent expressions in
both implementations, compares their observable LaTeX, and writes a structured
Markdown report for human review.

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

The command always writes a timestamped report under
`docs/v2/rendering-parity-reports/`. The `--check` option additionally fails
when the observed difference IDs do not exactly match the reviewed executable
ledger. Use an explicit output path for a disposable CI or local run:

```shell
PYTHONPATH=packages/galaga python -m tools.audit_rendering_parity \
  --repository . --output /tmp/galaga-latex-parity.md --check
```

The latest checked audit with visual rendering is
[LaTeX parity report, 2026-07-19 18:46](rendering-parity-reports/latex-parity-20260719-184624+1200.md).

## What one case compares

Each implementation-neutral recipe is evaluated against two adapters:

| Adapter | Algebra and display contract |
|---|---|
| Legacy v1 | `galaga.legacy.Algebra` and public `Multivector.display()` |
| Core facade v2 | `galaga.Algebra` and `DisplayPolicy("full")` |

The audit compares these channels independently:

| Channel | Purpose |
|---|---|
| Expression | Operation notation, precedence, and grouping |
| Value | Concrete coefficient and blade rendering |
| Full | Teaching form: distinct name, expression, and value |
| Rich | Notebook `_repr_latex_` wrapper and full-display behavior |
| Coefficients | Whether a visual difference conceals a numeric difference |

The default profile uses the three-dimensional Euclidean algebra. A separate
Lengyel RGA profile exercises its signature, blade convention, notation, and
value typography. Cases also cover nested precedence, deduplication, near-zero
elision, six-significant-digit formatting, and anonymous values.

## One inventory, three consumers

`tools.rendering_parity.CASES` is the canonical case registry. Both the command
and the permanent Pytest gate consume it. This avoids a prose checklist, a test
inventory, and a reporting inventory drifting apart.

The test suite enforces that:

- case keys are unique;
- all operation IDs shared by the legacy and facade registries are exercised;
- exact successes remain exact;
- every difference is present in `DIFFERENCE_LEDGER`; and
- every ledger entry is still observed.

The ledger maps a stable `profile/case` key to its accepted review decision. A
new difference therefore fails the check as unclassified. When a v2 change
resolves a difference, the stale ledger entry also fails the check. The author
must inspect the newly generated report and deliberately update the ledger;
regressions and improvements cannot silently change the baseline.

Generated reports pre-check **Accept v2** and include the ledger rationale for
reviewed differences. Unclassified differences retain blank checkboxes and an
empty notes prompt, so a new regression cannot look reviewed merely because a
previous report was annotated.

## Report structure

Reports are designed for direct review in Typora or another Markdown editor:

1. metadata and a count summary;
2. a compact success list, where each entry says **expression succeeded**;
3. one detailed section per difference;
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

The audit exercises 73 expressions, all 45 operation IDs shared by the two
registered operation catalogs, and 60 operation IDs in total. The initial run
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

The latest generated report and executable ledger are authoritative for the
current tree.

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
7. remove or revise the ledger entry only after reviewing the new report.

The legacy adapter is temporary. Phase 9 can retire it with the old engine when
every retained behavior has either converged or received an explicit Galaga 2
decision. The implementation-neutral case registry should remain as a semantic
rendering regression suite after its legacy half is removed.
