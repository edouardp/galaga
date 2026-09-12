---
status: accepted
date: 2026-09-13
deciders: edouard
---

# ADR-135: CGA Pseudoscalar Names and Exact Orientations

## Context

After selecting origin-first native CGA in ADR-134, the user requested a short
native pseudoscalar name, paired model volume names, an override, and a name
for the null-plane bivector. Names must not hide a sign or change a value.
Full wedge tables already consume the shared display order and signed blade
convention; they need no CGA-specific naming logic.

## Decision

Both `presets.cga` and `presets.blades.cga` accept:

- `model_pseudoscalars=False`: display native `I` by default. True selects
  the paired Python/ASCII names `IE` and `IC`, rendered as $I_E$ and $I_C$.
- `pseudoscalar_null=False`: True names `E = origin ^ infinity`.
- `pss=None`: automatic naming. A string or `Name` explicitly overrides
  the **native** top blade's preferred name, including `pss="I"` when model
  naming is enabled. None does not mean “remove the name.”

`CGAPreset` and the `p_cga` compatibility spelling accept the same options.
Require real booleans. Reject invalid names and conflicting spellings rather
than reinterpreting a name as another signed blade.

For example, `pss="IC"` is rejected for Euclidean-first 3D CGA even if paired
model naming is disabled: native `I` and semantic `IC` are opposite values.
`pss="J"` is valid; with model naming enabled `blade("IC")` then renders `-J`.
Target-specific spellings of `Name` are also checked for collisions.

The exact definitions, independent of display order, are

$$
I=\bigwedge(\text{native ordered basis}),\qquad
I_E=e_1\wedge\cdots\wedge e_n,\qquad
E=e_o\wedge e_\infty,\qquad
I_C=e_o\wedge I_E\wedge e_\infty.
$$

Therefore $I_E\wedge E=(-1)^n I_C$ and $I_C\wedge I_E=0$ for $n\geq1$.
Origin-first gives $I_C=I$; Euclidean-first gives $I_C=(-1)^n I$.
For the orthogonal preset use $e_o=(e_--e_+)/2$, $e_\infty=e_-+e_+$,
so $E=-e_+\wedge e_-$ and $I_C=(-1)^{n+1}I$.

Derive signed masks from the ordered semantic vectors. In the orthogonal
case expand the two null-vector combinations with wedges; do not substitute
an unexplained sign constant. This names derived blades but does not add
orthogonal support to `ConformalModel`.

### Canonical names, aliases and locals

Preserve original indexed ASCII, Unicode and LaTeX spellings as aliases to
the original positive native blades. `blade("I")` always returns native `I`.
When model names are enabled, `blade("IC")` and `blade("IE")` retain their
semantic values even if another name is preferred for display.

Use `Name("IE", latex="I_E")` and `Name("IC", latex="I_C")`: Python names
follow the compact `e1` convention, while mathematical subscripts belong to
LaTeX. The LaTeX spellings `blade("I_E")` and `blade("I_C")` remain accepted
lookup aliases, not additional canonical locals. Collision validation protects
both ASCII and LaTeX spellings, including when naming is disabled.

In 1D, the Euclidean volume is the vector `e1`. Keep `e1` canonical and
available in `locals()`; `IE` is a lookup alias only. Do not rename the axis.

Complete presets derive their local policy from canonical Python-safe ASCII
names, not all aliases. Consequently:

| Naming selection | Canonical volume locals |
|---|---|
| Default | `I` |
| Model names, dimension at least 2 | `IE`, `IC` |
| Model names, dimension 1 | `IC`; the axis remains `e1` |
| Model names plus `pss="I"` | `IE` (except 1D), `I` |
| Model names plus `pss="J"` | `IE` (except 1D), `J` |
| Null-plane naming | additionally `E` |

`locals()["IC"]` is the signed semantic volume, not necessarily native `I`.
A full wedge table instead enumerates native blades and can have a $-I_C$
heading (`-IC` in ASCII). Both behaviors express the same exact signed convention.

Explicit `local_names=` overrides retain precedence. A blade-only override
of an already configured algebra preserves its existing local-name policy.
Display order and expression tracking retain their independent contracts.

### Boundaries

This extends ADR-134's presentation choices without changing its coordinates,
model roles, metric, numeric IDs, or dual definitions. Ordinary orthogonal CGA
also receives the new names; its native coordinates do not change.
Lengyel CGA/RGA and quaternion conventions are untouched.

Low-level `null_cga_blade_convention` and `orthogonal_cga_blade_convention`
remain explicit indexed conventions. They can be supplied as overrides for
expanded teaching displays. The naming helper is private and shared by both
complete and blade-only presets. No public model-pseudoscalar properties or
new table rendering paths are introduced.

## Validation

Tests compute the named blades using actual algebra operations in spatial
dimensions 1–4, both null orders, the orthogonal frame, and scaled null pairs.
They assert exact coefficients and signed factorizations, not projective
equivalence. Coverage includes all naming combinations, preserved expanded
aliases, invalid/colliding names, canonical locals, explicit policy overrides,
1D axis preservation, and table headings/cells in all rendering targets.

The basis-order lesson adds adjacent naming controls, expanded equalities,
local-binding explanations and a small full wedge table. Runtime tests vary
the model-name flag, null-plane flag, PSS override, dimension and native order,
and check signed values plus rendered equations.
