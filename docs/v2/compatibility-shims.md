# Galaga 2 Compatibility and Removed Migration Shims

Galaga 2 keeps a deliberately small compatibility surface. Long operation
names are the mathematical contract. A concise spelling is either a permanent
same-object alias or a local import choice made by the user. The migration-only
operation adapters and bridge paths are removed in the final-API cleanup after
`2.0.0a4`; earlier published alphas still contain them.

This policy is now active at both `galaga` and `galaga.facade`: the top-level
objects are exact facade re-exports.

## Permanent concise aliases

These names are exact references to the canonical function. They have no
catalog entry, wrapper, warning, or independent semantics.

| Alias | Canonical operation |
|---|---|
| `dorst_inner` | `doran_lasenby_inner` |
| `gp` | `geometric_product` |
| `join` | `outer_product` |
| `meet` | `regressive_product` |
| `op` | `outer_product` |
| `rev` | `reverse` |
| `sw` | `sandwich` |
| `wedge` | `outer_product` |

`galaga.facade.OPERATION_ALIASES` is the immutable executable manifest for
this group.

## Removed function spellings

These six v1 names are no longer attributes, imports or wildcard exports of
`galaga` or `galaga.facade`. The old `galaga.core.involute` alias is also
removed. Use the canonical operations, which retain the same numerical and
expression-provenance contracts.

| Removed spelling | Replacement |
|---|---|
| `involute` | `grade_involution` |
| `mag2` | `norm2` |
| `magnitude_squared` | `norm2` |
| `norm_squared` | `norm2` |
| `normalise` | `unit` |
| `normalize` | `unit` |

The unused `GalagaDeprecationWarning` and `DEPRECATED_OPERATION_ALIASES`
exports and private adapter module are removed too. The development-only
`REMOVED_OPERATION_ALIASES` ledger preserves replacement guidance; it is not
a new runtime API. Attribute lookup fails and explicit imports raise
`ImportError` instead of warning and forwarding.

The `p_*` complete preset factories and concrete preset classes remain
available through explicit imports under their separate
[preset policy](../adrs/129-concise-complete-and-resolvable-blade-presets.md).
Prefer `from galaga import presets` in new code. No additional removals are
implied for permanent aliases or model-specific methods.

## No ambiguous inner-product adapter

Galaga 2 does not expose `ip` or `inner_product` in the facade. Access fails
with guidance toward:

- `doran_lasenby_inner`;
- `hestenes_inner`;
- `metric_inner_product`;
- `scalar_product`;
- `left_contraction`; or
- `right_contraction`.

This is a correctness boundary, not merely a naming preference. These
operations disagree for mixed grades and scalar inputs. Code that wants a
project-local short name can use ordinary Python:

```python
from galaga import doran_lasenby_inner as ip
```

## Migration-only import paths

The Gram proof repository has already been folded into Galaga. Its three
migration-only bridge import paths are now absent, including from artifacts:

| Removed module | Replacement | Status |
|---|---|---|
| `galaga.gram_bridge` | `galaga.facade` | Removed after `2.0.0a4` |
| `galaga.gram_bridge.facade` | `galaga.facade` | Removed after `2.0.0a4` |
| `galaga.gram_bridge.catalog` | `galaga.facade.catalog` | Removed after `2.0.0a4` |

Ordinary application code can import directly from `galaga`. There is no
warning shim or empty bridge namespace left behind. See
[ADR-130](../adrs/130-retire-migration-only-api-adapters.md).

The temporary `galaga.latex_symbols` shim is removed. Use
`galaga.names.LatexSymbols` or `Name.from_latex(...)`; the converter remains
unchanged. Legacy `galaga.lazy`, `galaga.symbolic`, `galaga.expr`,
`galaga.notation`, `galaga.symbolic_core` and the old LaTeX pipeline are also
removed, together with `galaga.legacy` and its renderer/simplifier.
The historical retirement inventory remains as evidence, not an importability
promise. See [ADR-122](../adrs/122-remove-the-legacy-engine-and-verify-artifacts.md)
and the replacement table in the [migration guide](migration-guide.md#use-the-top-level-api).

## Helpers are not aliases

Projection, rejection, reflection, and model constructors are separate policy
decisions. Per the Galaga 2 design constraint, a helper is not added merely
because it can wrap a short composition of existing operations. It must make a
domain contract materially clearer or validate model metadata. Until that case
is established, users compose the explicit primitives directly.

The [transformation migration recipes](migration-guide.md#migrate-transformation-helpers)
spell out invertibility, normal orientation, and metric-dependent exponentials.
The legacy `Algebra.rotor` constructor and its aliases remain absent; generic
`exp` does not inherit their plane-angle validation. Historical observations
and public composition tests are retained in
[ADR-108](../adrs/108-public-transformation-compositions-and-geometric-notebook-plots.md).

Fraction and constant members likewise remain retired. Use explicit scalar
construction, division and names; neither a fraction layout nor a symbolic
label changes the floating-point numeric domain. See the
[scalar migration recipes](migration-guide.md#migrate-scalar-helpers) and
[ADR-109](../adrs/109-public-scalar-compositions-and-small-value-contracts.md).

## Enforcement

The executable public-surface ledger owns every alias, target, milestone, and
warning message. Historical API completeness is checked against captured v1
observations; current supported v2 imports and behavior are tested with legacy
imports forbidden. Historical submodule dispositions are not themselves a
promise of supported v2 entry points. See
[ADR-096](../adrs/096-compatibility-manifests-use-historical-api-evidence.md).
Compatibility tests prove:

- permanent aliases are exact function objects;
- removed aliases cannot return through attribute lookup, explicit imports,
  wildcard exports, core aliases or catalog entries;
- canonical replacements retain their numeric values and expression IDs;
- ambiguous inner products remain absent and provide explicit choices;
- bridge imports fail in fresh processes without relying on a test guard;
- top-level exports are identical to their facade owners;
- plain `import galaga` leaves legacy engine modules unloaded;
- unledgered tests cannot construct legacy numeric values; and
- source and artifact checks reject bridge files and empty directories; and
- this guide names every removed function and bridge replacement.
