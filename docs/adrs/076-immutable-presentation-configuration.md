---
status: accepted
date: 2026-07-19
deciders: edouard
---

# ADR-076: Immutable Presentation Configuration and Context-Local Overrides

## Context and problem statement

The Galaga 2 numeric facade must support conventional algebra setups without
reintroducing presentation state into `galaga.core`. A single conventional
model can determine a Gram matrix, semantic basis roles, blade vocabulary,
local Python names, display order, and notation. At the same time, teaching,
book comparison, and notebook use require any presentation choice to be
replaceable independently and sometimes only for one dynamic scope.

The legacy implementation combined several of these concerns in mutable
`BladeConvention`, `Algebra`, and multivector state. That made it difficult to
tell whether a rename changed numeric meaning, caused shared-state hazards,
and made a process-wide temporary notation unsafe for threads and interleaved
async tasks.

## Decision drivers

- Keep the core's Gram matrix and exterior bitmask basis as numeric truth.
- Make complete conventional setups convenient without making presets magic.
- Permit blade vocabulary, notation, locals, ordering, and display policy to
  change independently.
- Represent reversed display blades such as Lengyel's `e31` without changing
  native coefficient order.
- Make temporary teaching presentations safe in threads and async tasks.
- Preserve equality, hashing, and numeric results across presentation views.
- Leave expression provenance and rendering as later consumers of the same
  immutable configuration.

## Decision outcome

Presentation is decomposed into immutable value objects:

- `Name` stores ASCII, Unicode, and LaTeX spellings;
- `BladeRef(mask, orientation)` identifies a signed native exterior blade;
- `BladeConvention` owns complete labels, lookup aliases, and semantic roles;
- `LocalNamePolicy` independently maps Python identifiers to signed blades;
- `DisplayOrder` owns a complete permutation of native bitmasks;
- `Notation` owns stable operation-token choices; and
- `DisplayPolicy` owns default content and output-target choices.

`PresentationConfig` groups those components and validates their common vector
dimension. Its `with_*` operations return new configs and replace exactly one
component.

`AlgebraDefinition` contains an immutable validated Gram matrix and numeric
backend options. `ModelConfig` contains optional semantic roles.
`AlgebraConfig` combines definition, model, and presentation. Complete preset
objects deterministically build an `AlgebraConfig`; they are ordinary frozen
classes with inspectable parameters, not strings dispatched through a central
conditional.

The facade constructor accepts complete setup through `config=`:

```python
from galaga.facade import Algebra, Notation, p_cga

algebra = Algebra(
    config=p_cga(spatial_dim=3),
    notation=Notation("teaching"),
)
```

An explicit presentation component overrides only the component supplied by
the preset. A complete config cannot be combined with a second numeric metric
definition. Users may instead construct every component directly.

Signed blade references are lookup and presentation metadata, not basis
changes. Native integer-mask lookup always returns the positive stored
exterior blade. For example, in Lengyel's RGA convention:

```python
rga.blade(0b0101)   # native +e13 coefficient
rga.blade("e13")    # the same native blade
rga.blade("e31")    # -1 times that native blade
```

The core never sees the label. Facade factories apply only the declared sign
to an otherwise ordinary core value.

Persistent presentation changes create a cheap facade view sharing the same
`core.Algebra`. Temporary changes use a per-algebra `ContextVar`:

```python
with algebra.use_presentation(teaching):
    ...
```

The resolution order is explicit per-render presentation, current scoped
presentation, then the facade view's persistent presentation. The explicit
hook is implemented now through `resolve_presentation`; renderers will consume
it in Phase 6.

## Consequences

- Good, because presets and fine-grained control use the same public objects.
- Good, because changing appearance cannot mutate the metric, coefficients,
  equality, hashing, or numeric results.
- Good, because signed conventional names do not masquerade as a basis
  transformation.
- Good, because local Python identifiers are not coupled to display labels.
- Good, because nested, threaded, and asynchronous presentation scopes are
  isolated and restore reliably.
- Good, because complex, quaternion, exterior, Euclidean, STA, PGA, CGA, and
  Lengyel RGA configurations are inspectable and independently testable.
- Cost, because a complete algebra setup has more small configuration types.
- Cost, because a facade algebra now owns a context-local override handle in
  addition to its core algebra and persistent presentation.
- Risk, because changing blade labels while deliberately retaining a separate
  local-name policy can produce different display and local vocabularies. This
  is intentional fine-grained control and must remain visible in documentation.
- Deferred, because this decision provides presentation metadata and
  precedence, not expression nodes or final ASCII, Unicode, and LaTeX
  rendering. Those remain Phases 5 and 6.

## Superseded legacy behavior

This decision supersedes ADR-028's mutating configuration direction for the
Galaga 2 facade. It retains the useful separation intended by ADR-057,
ADR-058, ADR-059, and ADR-070 while replacing their legacy mutable storage and
process-local assumptions with immutable components and context-local scope.
