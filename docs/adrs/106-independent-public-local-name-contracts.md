---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-106: Independent Public Local-Name Contracts

## Context and problem statement

The remaining `test_locals.py` mixes Python-key generation, signed factories,
display labels, and legacy expression flags. All twelve original cases pass
before migration. Their eleven function identities must retain explicit
public ownership before the old engine can be removed.

The existing v2 model in [ADR-076](076-immutable-presentation-configuration.md)
deliberately separates these concerns. Reintroducing implicit prefix rewriting
or display-oriented basis enumeration merely to retain old test syntax would
undo that boundary. In particular, v1 local `g01` under the sigma convention
can mean $\gamma_1\gamma_0$; a native gamma product has the opposite sign.

## Decision outcome

Migrate the original tests to public facade values and immutable
`LocalNamePolicy` objects without changing production code. Retain every
function identity and all twelve cases. The
[archive](../../packages/galaga/tools/baselines/locals-contracts-v1.json)
captures the complete source and its SHA-256, eleven full local-binding
tables with ordered keys, coefficients and observed Unicode values, all six
legacy STA basis bivectors, scalar lookups, and exception messages.
It was captured at `2856245` on 2026-09-08 using Python 3.14.4 / NumPy 2.5.2.

### Make each existing v2 boundary explicit

- `locals()` returns read-only named values in policy insertion order.
  Policies snapshot their input; keys are validated Python identifiers, not
  inferred or sanitized labels. Explicit scalar and Unicode bindings are valid.
- Replace `locals(grades=...)` by filtering policy entries on
  `ref.mask.bit_count()` and applying `with_local_names`. Preserve the whole
  signed reference. Replace `prefix=` and `variable_hints` with explicitly
  authored policy entries or an independently generated compact vocabulary.
  These old factory keywords remain unsupported.
- `from_convention` filters canonical ASCII spellings literally, excluding
  the scalar, invalid identifiers and keywords. It does not include aliases
  or roles, invent sanitized names, or compact product spellings. Wedge
  `v1^v2` is omitted; juxtaposed `v1v2` remains that identifier.
  To keep `v12`, derive locals from a separate compact convention.
- Changing `blades=` or `with_blades` alone does not regenerate locals.
  Presets explicitly configure both. A local value's `name` is its Python
  key; request `display("value/unicode")` to see its blade vocabulary.
- `locals(expr=True)` attaches `Symbol(key)` leaves, not signed blade
  literals. Replay needs an explicit environment. `expr=False` omits those
  initial leaves, but names still opt subsequent operations into provenance.
  `blade(value, expr=True)` discards the name/provenance and produces a
  self-contained signed literal. Changing an environment can change a
  symbol's replayed value without changing the symbol itself.
- STA locals use actual signed products. Explicit policies can retain old
  `g01` bindings, but native `g0g1` lookup and `basis_blades(2)` retain
  positive native orientation. See
  [ADR-104](104-metric-derived-sta-names-and-public-blade-contracts.md).
- Use `blade(0)`, `blade("1")` under the default convention, or `scalar(1)`
  for the scalar. Empty-string scalar parsing stays retired. Unknown names
  raise `KeyError`; out-of-range integer masks raise `ValueError`.

### Prove value ownership, not only spelling

Replay all eleven archived binding tables in both expression modes,
checking order, coefficients, names, rendered values and evaluation.
Compute exterior products and geometric products before configuring local
names. Use Euclidean, oblique-indefinite, and singular-oblique Gram matrices,
both orientations, and all three display styles/targets. Mixed-grade
compositions check nonzero coefficients, replay, hashes, and numeric sharing.

Additional tests cover scoped rebinding versus literal replay, immutable
snapshots, invalid policies, scalar/Unicode keys, and keyword/alias filtering.
Corruption probes reject altered archived keys, shapes, nonfinite or wrong
coefficients, wrong output, and a local factory that discards orientation.
Fresh-process gates prohibit imports of the old engine and rendering stack.

The presentation-contexts notebook teaches signed references, independent
keys/labels, grade filtering and explicit symbol replay using computed
examples. The migration guide documents equivalent explicit recipes.

## Consequences

All 73 focused cases pass with 100% line and branch coverage in the three
test files. All 63 public cases also pass from the built wheel with package
origins checked and legacy imports prohibited. The construction-exemption
ledger falls from eight files to seven.

This retires a test dependency, not a production feature or the engine itself.
Legacy keyword conveniences are not restored; existing explicit v2 policies
preserve their useful binding behavior. Remaining mixed legacy suites,
namespace/construction guards, engine deletion, and final release gates remain.
