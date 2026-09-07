---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-105: Public RGA Contracts and Under-Accent Fallback

## Context and problem statement

The remaining `test_rga_convention_layer.py` retains five historical test
functions and eleven collected cases. Numeric kernels already have direct
core owners, but the convention tests still import legacy values, expression
internals, mutable notation, and the old operation registry.

All eleven cases pass before migration. Computation shows that eleven of the
sixteen operation samples are zero: distinct orthogonal vectors are poor
probes for antiproducts, pairings, weight maps, and transwedge parameters.
Keep those historical samples, but do not mistake their agreement for
nonzero sign/grade coverage.

Migration also exposes a real LaTeX defect. A custom under-accent `\sim` is
emitted as `\sim{body}` rather than being placed below the body. Plain-text
marks use `\underaccent` instead of the existing underset layout. The source
suite explicitly owns the ordinary-symbol fallback.

## Decision outcome

### Preserve source ownership and historical evidence

Retain every original function identity and all eleven cases against the
public facade. Use `p_rga`, immutable `Notation`/`RenderRule`, `expr=True`,
generic `Call` nodes, explicit evaluation, and the public operation catalog.
No legacy adapters or numeric-engine changes are introduced.

The [archive](../../packages/galaga/tools/baselines/rga-convention-contracts-v1.json)
was captured at `48f5d0f` on 2026-09-08 with Python 3.14.4 and NumPy 2.5.2.
It stores the full source hash, all five test sources, the eleven-case count,
two basis-vector bindings, twenty-six actual operation/layout observations,
and all sixteen oriented basis values in historical display order.
Every observation retains native-mask coefficients and three requested
display channels. V1's symbolic `format(value, "a")` often returns Unicode;
the archive preserves that behavior, rather than misrepresenting it as ASCII.

Keep established v2 differences explicit:

- Signed names and locals represent actual ordered wedge products.
  Positive integer-mask lookup and `basis_blades` enumeration remain native;
  `DisplayOrder` controls presentation, not coefficient storage.
- Point, line, plane, projective, and antiscalar roles remain discoverable.
- Numeric zero has no unique homogeneous grade, so `homogeneous_grade()`
  returns `None` rather than an inferred grade from expression shape.
- Transwedge has evaluator arity three, expression arity two, and an explicit
  `order` parameter. Simplification and replay preserve that parameter.
- ASCII uses the existing functional fallbacks. Unicode antiwedge spacing
  and compound accents follow shared grouping. LaTeX removes the old phantom
  padding, keeps wide reverse accents, and uses mirrored floor contractions.
- Immutable target-specific overrides do not mutate the source algebra.
  Binary mismatch checks include both different dimensions and different
  metrics of the same dimension.

### Distinguish an under-accent command from an annotation

Change only the LaTeX `Accent` emitter's under-position handling.
The recognized one-argument commands remain `\underline`, `\utilde`,
`\underbrace`, `\underleftarrow`, `\underrightarrow`, and
`\underleftrightarrow`. Every other under-accent spelling is an annotation,
emitted as `\underset{annotation}{body}`, whether it starts with a backslash
or is plain text. The annotation must itself be valid TeX.

This is a bounded command distinction, not arbitrary macro discovery.
Custom accent macros are not inferred; callers can use an explicit wrapper
rule for a custom command with authored delimiters. Over-accent behavior,
ASCII/Unicode emission, semantic grouping, numeric values, and expression
identity remain unchanged. Default Lengyel under-tilde and underline output
is unchanged. Follow through ADR-078's emitter-owned target rewriting.

Regressions first reproduce fourteen failing fallback cases. Tests then cover
plain marks, command-like symbols, compound annotations, grouped bodies, all
six native commands, and existing over-accent forms. Facade tests independently
check eager values, replay, hashes, and target-specific override isolation.

### Add nonzero, coefficient-level checks

Compute all expected values before constructing names or expressions.
Use standard RGA, oblique-indefinite, and singular-oblique Gram matrices.
The latter two exercise generic algebraic operations with RGA vocabulary;
they are not claimed to satisfy the validated rigid geometric model.

Derive the exterior metric from Gram minors and complements from exterior
permutations. Obtain the antimetric by complementary conjugation. Derive
antireverse signs from antigrades and both pairings from the coefficient
matrices. Only the geometric product tensor uses the core's forced reference
backend; transwedge uses explicit grade selection on that tensor. No oracle
calls the corresponding facade operation or reads private product/sign tables.
This is independent composition evidence, not another GA library.

All sixteen original operations have nonzero mixed-grade probes on all three
metrics. Three-target rendering, eager coefficients, homogeneous grades,
replay, simplification, hashes, and scoped notation remain checked.
Orders zero through four retain parameters and reconstruct both products
through their signed sums. Explicitly check that bulk plus weight reconstructs
the standard PGA value but is not a universal projection identity for arbitrary
Gram matrices.

Corruption probes reject invalid coefficient shape/finiteness, wrong archived
output, swapped dual sides, a sign error hidden by the original zero
antiproduct, and a lost transwedge order. Fresh processes prohibit all legacy
imports.

## Verification and consequences

All 300 focused cases pass with 100% line and branch coverage in the four
test files. All new emitter paths are covered; its full-suite coverage rises
from 94% to 95%. The 288 public cases pass directly from the built wheel with
package origins verified and test/tool directories excluded.

The full package/release suites pass 5,910 cases on Python 3.11 and 6,027 on
Python 3.14, including maintained notebook exports. Core/facade coverage,
the existing matrix complex-to-real warning, and 295 type errors remain.

The RGA demo now teaches signed versus native lookup, numeric-zero grades,
and a computed mixed-grade antireverse shown with default and custom
under-accents. The construction-exemption ledger falls from nine files to
eight. Locals/naming, other mixed legacy contracts, engine deletion, and final
stable-release gates remain unfinished.
