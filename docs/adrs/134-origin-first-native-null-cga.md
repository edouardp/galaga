---
status: accepted
date: 2026-09-13
deciders: edouard
---

# ADR-134: Origin-First Native-Null CGA with an Explicit Compatibility Order

Naming follow-up: [ADR-135](135-cga-pseudoscalar-names-and-exact-orientations.md)
adds default `I` and optional `IE`/`IC`/`E` names (LaTeX $I_E$/$I_C$/$E$),
plus a native PSS name override. This does not change the coordinates or dual
definitions below.

## Context

The chosen conformal orientation is
$I_C=e_o\wedge I_E\wedge e_\infty$, with
$I_E=e_1\wedge\cdots\wedge e_n$. The former Euclidean-first native preset
gave $I_C=(-1)^n I_{\mathrm{native}}$. Printing the origin first would not
change that relationship, and could conceal it from users.

This decision changes the default native coordinates described by ADR-086
and extends the CGA recipes in ADR-129. It does not change ADR-133's
presentation-only display ordering.

## Decision

The complete recipe accepts the keyword
`basis_order: Literal["origin-first", "euclidean-first"] | None = None`.

- For the default null frame, omission resolves to origin-first:
  $(e_o,e_1,\ldots,e_n,e_\infty)$.
- `basis_order="euclidean-first"` selects the former native coordinates
  $(e_1,\ldots,e_n,e_o,e_\infty)$.
- The orthogonal frame remains $(e_1,\ldots,e_n,e_+,e_-)$.
  Its order must be omitted; explicit null-order options are errors.
- The frozen recipe retains the supplied parameter (`None` means use the
  frame default); omitted and explicit origin-first recipes build equal
  complete configurations.

Apply this contract to `presets.cga`, its `p_cga` spelling and `CGAPreset`.
The concrete `null_cga_blade_convention` also defaults to origin-first.
Generate its labels, aliases and roles in the actual chosen order.
Build Gram entries from those roles rather than maintaining a separate
hardcoded coordinate table.

`presets.blades.cga` accepts the matching order option. Resolution validates
the entire supplied Gram matrix, including the selected null-pair positions;
it never transforms coordinates. An opposite-order recipe is rejected.
An explicitly supplied concrete convention remains a presentation choice,
as before: it is not a substitute for a complete basis conversion.

### Identity and migration

Origin-first definitions have IDs such as `cga-3d-null-origin-first`.
The compatibility convention keeps `cga-3d-null`. Orthogonal and Lengyel IDs
are unchanged. Both null orders retain `model.id == "cga-null"`, because
the same role-validated model supports them.

IDs are descriptive, not a complete serialization format: save the Gram
matrix, native basis convention and null-pair normalization with coefficients.
Loading old arrays into the new default silently changes their meaning.
Use the explicit compatibility recipe for old arrays, or apply a real
vector basis map and its exterior extension to every grade. Permuting vector
coefficients alone is insufficient for a general multivector.

### Orientation and protected contracts

`algebra.I` remains the wedge of the native ordered basis, not a mutable
orientation setting. In the new default it equals the role-derived $I_C$.
In the compatibility order the factor $(-1)^n$ remains intentional.

No dual operation is redefined: `dual(A)` is still $AI^{-1}$,
`undual(A)` is $AI$, and `ConformalModel.dual` remains right Hodge duality.
Under an orientation-reversing basis identification, native complements and
duals acquire their corresponding orientation factor. Do not correct this
in rendering or hide it with projective equality.

Orthogonal CGA, Lengyel CGA, RGA and quaternion conventions and explicit
display orders are unchanged. In particular, coordinate-specific Lengyel
antiproduct formulas retain their original orientation.

Display remains independently overridable at `Algebra` construction or via
presentation views. The generic grade-then-lexicographic default follows
native basis indices. Gram and vector wedge tables follow native vector
order; full wedge tables follow the active display order.

No new model-pseudoscalar properties, general basis-conversion API or
orthogonal `ConformalModel` support is introduced here. Teaching code derives
$I_E$, $e_o\wedge e_\infty$, and $I_C$ from existing model roles using wedges.
Those separate API extensions can be considered without changing this choice.

## Validation

Algebra-first tests cover both orders in spatial dimensions 1–4 and positive
and negative nonzero null-pair scalings. They check Gram entries against
computed vector products, labels/roles, deterministic recipe expansion,
parameter rejection, and unchanged protected conventions.

An exterior map built by wedging mapped vectors tests every basis blade,
left/right generator products, mixed-grade products, and embedding. Dual,
undual, both Hodge duals, complements and model dual/antidual are checked
with the orientation factor derived from the mapped native pseudoscalar.
Exact 2D line and circle duals verify signed OPNS/IPNS results, not just loci.
The familiar orthogonal construction is computed independently in 2D and 3D.

Matrix tests check every 3D CGA blade's compact roundtrip and mixed-grade
product preservation under both orders and multiple pair scalings.
The native-null foundations lesson compares native, compatibility and
orthogonal orientations; existing Gram and complex/quaternion lessons use
the new native order. Notebook execution and rendering tests remain gates.
The focused basis-order lesson covers every combination of 2D/3D, native
order and display order, including explicit conversion and signed flats/rounds.
