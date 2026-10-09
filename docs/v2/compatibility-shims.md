# Operation Aliases and Removed APIs

Long operation names define the mathematical API. The concise aliases below
are exact references to those operations. The replacement tables help update
code written against earlier Galaga APIs.

This policy is now active at both `galaga` and `galaga.facade`: the top-level
objects are exact facade re-exports.

## Permanent concise aliases

These names are exact references to the canonical function. They have no
catalog entry, wrapper, warning, or independent semantics.

| Alias | Canonical operation |
|---|---|
| `conjugate` | `clifford_conjugate` |
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

These retired names are no longer attributes, imports or wildcard exports of
`galaga` or `galaga.facade`. The old `galaga.core.involute` alias is also
removed. Use the canonical operations, which retain the same numerical and
expression-provenance contracts.

| Removed spelling | Replacement |
|---|---|
| `bulk_part` | `metric_apply` for the former metric map |
| `weight_part` | `antimetric_apply` for the former antimetric map |
| `involute` | `grade_involution` |
| `mag2` | `norm2` |
| `magnitude_squared` | `norm2` |
| `norm_squared` | `norm2` |
| `normalise` | `unit` |
| `normalize` | `unit` |

The generic `bulk_part` and `weight_part` names are also absent from
`galaga.core`, the operation catalog, and built-in notation recipes. Metric
and antimetric maps are defined for every algebra, but do not generally form
a complementary decomposition. Model methods such as `cga.bulk_part(value)`
and `cga.weight_part(value)` retain their validated component semantics. See
[ADR-174](../adrs/174-runtime-geometry-model-hierarchy-and-classifiers.md).

Attribute lookup for a removed spelling fails. Explicit imports raise
`ImportError`. Use the replacement operation directly.

The prefixed `p_*` complete preset factories have been retired. Import
`presets` from `galaga` and call the concise factory names. Concrete preset
classes remain available under the
[preset policy](../adrs/129-concise-complete-and-resolvable-blade-presets.md).
No additional removals are implied for permanent aliases or model-specific
methods.

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

## Current contracts

Tests in `packages/galaga/tests/facade/` cover alias identity, canonical
numeric results, expression operation IDs, rejected spellings, and explicit
inner-product guidance. The public namespace tests verify that `galaga`
reexports the facade objects. Release artifact checks validate the shipped
runtime and reject retired modules and dependencies.

The completed migration manifests and import guards were retired under
[ADR-170](../adrs/170-retire-migration-scaffolding-before-stable-2.md).
