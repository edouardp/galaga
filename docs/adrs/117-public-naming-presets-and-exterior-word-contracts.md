---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-117: Public Naming Presets and Exterior-Word Contracts

## Context and problem statement

Nine naming tests remain in the mixed `test_coverage.py`. All pass against
v1. They cover gamma, sigma, letter subscripts, custom labels, invalid
configuration and lookup. Their orthogonal examples also happen to equate
geometric vector words with exterior blades, hiding an important distinction
in a general Gram frame.

[ADR-104](104-metric-derived-sta-names-and-public-blade-contracts.md) already
defines complete immutable conventions, signed lookup and ASCII repr.
This subgroup preserves those decisions without restoring the `b_*` factories
or interpreting blade labels as executable products.

## Decision outcome

### Retain all nine identities and their full vocabulary evidence

Move `TestNamingPresets` to
`tests/presentation/test_naming_preset_contracts.py`. The other twenty
rotor/sandwich methods and unrelated mixed-file code remain unchanged.
No production behavior changes.

The [archive](../../packages/galaga/tools/baselines/naming-presets-v1.json)
retains complete source/SHA-256, all 29 source identities, selected ownership
and five complete tables: gamma, sigma, sigma-xyz, and two-/three-dimensional
custom names. The 44 native labels retain coefficients, squares, three
spellings, actual Unicode/repr/LaTeX and 132 evaluated lookups. Three actual
validation errors remain recorded. Capture provenance is `f75d795`,
2026-09-08, Python 3.14.4 and NumPy 2.5.2.

Public replay checks every label, target and lookup with and without explicit
expression literals. Native-mask coefficient oracles, exterior products and
signed Gram minors check values and squares independently of presentation.
Repr intentionally follows ASCII, not v1 Unicode. The existing LaTeX
script-bracing correction applies to sigma-xyz; its historical ASCII keys
`x/y/z` and actual Unicode `σz` remain explicit choices.

Use indexed conventions for regular gamma/sigma vocabulary. Complete `Name`
tables preserve custom word spellings and the sigma-xyz ASCII keys without
guessing a prefix. Unknown names raise `KeyError`; incomplete conventions,
dimension mismatches, invalid types and ambiguous target spellings remain
construction errors. Input containers are snapshotted and metadata is frozen.

### Blade words label exterior masks, not geometric products

A native mask denotes the ordered exterior basis. Thus a configured `ab`
label can mean $a\wedge b$ while $ab=G_{12}+a\wedge b$. Likewise,

$$
abc=G_{23}a-G_{13}b+G_{12}c+a\wedge b\wedge c.
$$

The extra metric terms must not be discarded or absorbed into a basis label.
Across Euclidean, oblique-indefinite and degenerate metrics, three indexed
styles and all three targets, compare every pair of named basis blades
against forced-reference core products and explicit replay. These are
independent of facade composition, not a second Clifford-algebra library.

Derive reversed-plane references from the actual exterior product before
assigning an oriented name. Canonical spellings and roles return that signed
value; an explicit positive-native alias remains distinct. All target
spellings, literal replay, equality/hashing and exceptional scope restoration
preserve the computed sign.

Changing `blades` alone preserves the metric and Python local-name policy.
Use `LocalNamePolicy.from_convention(...)` explicitly when those bindings
should follow the new canonical ASCII names.

### Teach the general-metric distinction

The [construction notebook](../../examples/galaga_v2/algebra_construction.py)
now displays its oblique Gram matrix through `MatrixRepr`, compares exterior
lookup with two-/three-vector geometric words and shows independent local
binding configuration. Its runtime regression checks actual coefficients,
lookup, replay, shared numeric ownership and generated teaching text.
An existing unused preset example is made cell-local with an underscore.

Mutation controls reject corrupted archives, old Unicode repr, geometric-word
parsing in blade lookup and unsigned oriented lookup. A fresh process blocks
legacy imports.

## Verification and consequences

All 109 focused cases pass on Python 3.14 with 100% line/branch coverage in
both test files. All 93 public cases pass from the wheel with module origins
verified and legacy imports blocked. Full suites pass 8,831 cases (73 skipped)
on Python 3.11 and 8,976 (20 skipped) on Python 3.14.

A separate full-suite production coverage checkpoint measures 100% for
`names.py`, 99% for `blades.py` and 96% for `presentation.py`, with branch
measurement enabled. These are measured totals, not claimed improvements.

Core, facade, expression and rendering coverage are unchanged. Ruff lint,
configured Python formatting and changed-file Markdown lint pass. The guide
recipe executes and all 246 local links in the seven changed Markdown files
resolve. The existing matrix warning, 295 type errors and Markdown code-block
formatting debt remain separate work.

The naming subgroup is complete. Twenty rotor/sandwich tests remain in the
mixed suite; it and `test_redesign.py` remain in the construction ledger.
Namespace guards, engine deletion and release gates are separate work.
