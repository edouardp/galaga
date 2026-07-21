# Galaga 2 Compatibility Shims

Galaga 2 keeps a deliberately small compatibility surface. Long operation
names are the mathematical contract. A concise spelling is either a permanent
same-object alias, a temporary warning adapter with a removal milestone, or a
local import choice made by the user.

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

## Temporary function spellings

These v1 names remain callable through Phase 9. Each emits
`GalagaDeprecationWarning` at the user's callsite and delegates to the canonical
facade function. A tracked value therefore records only the canonical
operation ID.

| Temporary spelling | Replacement |
|---|---|
| `involute` | `grade_involution` |
| `mag2` | `norm2` |
| `magnitude_squared` | `norm2` |
| `norm_squared` | `norm2` |
| `normalise` | `unit` |
| `normalize` | `unit` |

`galaga.facade.DEPRECATED_OPERATION_ALIASES` is the immutable executable
manifest. These adapters are deliberately not same-object aliases because a
wrapper is required to issue migration guidance.

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

The Gram proof repository has already been folded into Galaga. Its bridge
namespace re-exports the current implementation but now warns on import:

| Deprecated module | Replacement | Removal |
|---|---|---|
| `galaga.gram_bridge` | `galaga.facade` | Phase 9 |
| `galaga.gram_bridge.facade` | `galaga.facade` | Phase 9 |
| `galaga.gram_bridge.catalog` | `galaga.facade.catalog` | Phase 9 |

The bridge contains no implementation and must not become a second public
architecture.

Legacy `galaga.lazy`, `galaga.symbolic`, `galaga.expr`, `galaga.notation`, and
related v1 internals remain temporary implementation paths. The supported
Phase 8 oracle entry point is `galaga.legacy`; its renderer and simplifier are
`galaga.legacy.render` and `galaga.legacy.simplify`. This relocation is
required because `render` and `simplify` are top-level facade functions, and a
same-named Python submodule would overwrite those attributes based on import
order. The entire legacy namespace is removed in Phase 9.

## Helpers are not aliases

Projection, rejection, reflection, and model constructors are separate policy
decisions. Per the Galaga 2 design constraint, a helper is not added merely
because it can wrap a short composition of existing operations. It must make a
domain contract materially clearer or validate model metadata. Until that case
is established, users compose the explicit primitives directly.

## Enforcement

The executable public-surface ledger owns every alias, target, milestone, and
warning message. Compatibility tests prove:

- permanent aliases are exact function objects;
- temporary aliases warn with the ledgered category, text, and caller-facing
  stack level;
- tracked adapter calls retain the canonical expression operation ID;
- ambiguous inner products remain absent and provide explicit choices;
- bridge import paths warn and still import; and
- top-level exports are identical to their facade owners;
- plain `import galaga` leaves legacy engine modules unloaded;
- unledgered tests cannot construct legacy numeric values; and
- this guide names every temporary function and bridge replacement.
