---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-110: Public Factory and Display Edge Contracts

## Context and problem statement

The thirty cases in `test_coverage_gaps.py` still import the legacy engine.
They cover blade lookup, pseudoscalar labels, display hooks and the old
`lazy`/`symbolic` factory flags. All thirty pass before migration, but many
assert only a private flag or a nonempty string. Existing public v2 contracts
deliberately differ in lookup orientation, content defaults and result types.

Compute before choosing expectations: in the time-first mostly-minus frame,
`gamma1*gamma0` is the negative native `gamma0^gamma1` blade. Legacy lookup of
`"σ₁"` returned the positive native slot and rendered `-σ₁`. The public
lookup already returns the signed product, following
[ADR-104](104-metric-derived-sta-names-and-public-blade-contracts.md).
That correction must not be undone while retiring another legacy import.

## Decision outcome

Retain every historical method identity on the public facade. Preserve old
observations as data and test existing v2 differences explicitly; do not
restore retired flags, constructors or the `_DisplayResult` object.
No production package behavior changes.

The [archive](../../packages/galaga/tools/baselines/factory-display-edges-v1.json)
was captured at `0105096` on 2026-09-08 with Python 3.14.4 and NumPy 2.5.2.
It retains the full source and SHA-256 digest, all thirty identities, six
lookup observations, four errors, three complete pseudoscalar-labelled basis
tables (32 blades), six display samples and ten factory/flag observations.
The display samples include original strings, repr, rich LaTeX, wrapped
output, result-object type and fixed-decimal formatting.

### Keep the public migration boundaries explicit

| Concern | Existing v2 contract |
|---|---|
| Factory provenance | `expr=True` or `expr=False`; `lazy` and `symbolic` are rejected even when false |
| Scalar blade | Native mask `0` or label `"1"`; empty text is not an implicit scalar |
| Lookup text | Declared labels, aliases and roles; unknown names raise `KeyError` rather than parsing metric-role strings |
| Blade literalization | Preserve a signed unit blade's coefficients; drop name and prior provenance, optionally attaching a fresh literal |
| Pseudoscalar labels | Override the derived top-grade mask using immutable indexed conventions; names do not change metric or invertibility |
| Default named display | Automatic teaching equality; request `content="name"` for the old name-only appearance |
| Render result | `.display()` and `.latex()` return ordinary string snapshots; later policy changes affect only new calls |
| Hooks and wrapping | Repr selects ASCII, rich output selects LaTeX; delimiters do not bypass the selected content |

Retire `display_repr` in favor of `DisplayPolicy`. Numeric `.2f` formatting
is not supported on a rendered string; Python `.2` would truncate its text,
not change numeric precision. Set significant-digit precision before
rendering, or format individual coefficients after checked conversion.
Indexed sigma letter subscripts use braced LaTeX, such as `\sigma_{x}`;
the archive retains the older equivalent unbraced spelling.

These refine the migration evidence in
[ADR-097](097-concrete-display-contracts-outlive-legacy-rendering.md) without
changing the immutable presentation design.

### Verify values independently of presentation

Recompute all archived values through public factories or exterior products.
Replay complete basis tables and match factory observations by coefficients,
not legacy presentation order. Exact hook/content assertions supplement the
original weak string checks.

General-Gram probes use the independent vector identity
`xy = x.T @ G @ y + x ^ y`: the two-dimensional exterior coefficient is the
determinant of the spanning columns. Scope changes, nested overrides and
exceptional exits preserve numeric coefficients, expression identity and hashes.
Saved strings remain fixed while new rendering calls observe the active policy.

Compute volume orientation from ordered wedges before assigning a signed label.
Verify its square against `(-1)**(n*(n-1)//2) * det(G)` under Euclidean,
oblique-indefinite and degenerate metrics. Native pseudoscalars and signed
label/alias/role lookup remain distinct; a named null volume has no inverse.
Both expression modes and all three display targets are exercised.

Corruption probes reject malformed/nonfinite or erased coefficients, unsigned
semantic lookup, Unicode substituted for ASCII repr, a non-string result
wrapper and altered pseudoscalar labels. Fresh-process tests prohibit legacy
imports. The existing presentation notebook now explicitly demonstrates string
snapshots and asserts scope restoration plus coefficient/provenance/hash
stability; a Python 3.14 runtime test checks its values and generated math.

## Consequences

All 211 focused cases pass on Python 3.14 with 100% line and branch coverage
in their three files. Both public suites pass all 199 cases directly from
the built wheel with package origins verified and legacy imports blocked.
Full package/release suites pass 6,875 cases (62 skipped) on Python 3.11 and
7,009 (20 skipped) on Python 3.14, including maintained notebook exports.
Core/facade coverage percentages remain unchanged, with one additional facade
path covered. Emitter coverage stays at 96%; the existing matrix warning and
295-error type-check baseline remain.

The construction-exemption ledger falls from three files to two:
`test_coverage.py` and `test_redesign.py`. Their mixed contracts,
namespace/construction guards, engine deletion and final release gates
remain pending. This completes one dependency-retirement unit, not a release.
