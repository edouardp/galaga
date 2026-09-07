---
status: accepted
date: 2026-09-07
deciders: edouard
---

# ADR-102: LaTeX Contracts and Script-Safe Spelling

## Context and problem statement

The legacy `test_latex_build.py` exercises 112 cases through separate
expression, layout, rewrite, and emission modules. Its pure display symbols
have arbitrary numeric backing; they are not independent numeric oracles.
Retiring that dependency exposed three reproducible gaps in v2:

- a command prefix could merge with the operand, producing `\tildea`;
- an exponential or already-scripted name could acquire an illegal second
  superscript, such as `e^{a}^*` or `x^2^{-1}`; and
- a compound name's script could appear to apply to only its final term,
  as in `a \wedge b^*` instead of `\left(a \wedge b\right)^*`.

Scientific literal powers had the same problem: the outer power must cover
the mantissa as well as the existing decimal exponent.

## Decision outcome

### Retain source evidence and public contracts

The [historical archive](../../packages/galaga/tools/baselines/latex-build-contracts-v1.json)
records the full source commit `813eb60`, Python/NumPy versions, all 112
test identifiers and method sources, and actual results observed through
the original `_latex` helper. Cases that bypassed that helper retain their
source assertions, not invented observations. Every historical test class
has a checked live owner.

The replacement suite constructs public `Call`, `Symbol`, and literal
expressions, or semantic nodes when testing layout separately from expression
simplification. Facade integration checks derive a rotor from the Gram
determinant before naming it, including an oblique metric. They verify eager
coefficients, logarithm, explicit replay, and unchanged expression identity
and hashes. Complement is checked against the exterior-product law.
Named values keep provenance without hidden symbol bindings.

Existing v2 choices remain explicit:

- Wide accents, floor contractions, and immutable target-specific rules
  replace the corresponding v1 policies and mutable setters.
- Builder-selected fraction parentheses are retained in all targets.
  A literal half can simplify to `0.5`; semantic `Fraction` tests retain
  the independent fraction-bar layout contract.
- Multivector division is a product with inverse, not a `Div` node.
- Prefix/product grouping need not reproduce v1's negative-sign hoisting.
- Single-character superscripts may omit braces.
- Private `Sym.is_compound`, `has_superscript`, `_inner_expr`, and
  lazy flags do not return. Their observable naming/provenance contracts do.
- Scientific notation retains `\times`; the unavailable `cdot`/`raw`
  configuration remains a documented limitation, not an implemented feature.

### Keep spelling safety in the LaTeX emitter

Semantic precedence remains builder-owned. The emitter adds a bounded
lexical guard when attaching a semantic superscript or subscript:

1. Preserve an existing semantic `Group`.
2. Scan the emitted base into control words, escaped characters, braces,
   and ordinary characters. Ignore brace contents and single-token script
   arguments when detecting outer operators.
3. Parenthesize an identifier or numeric literal whose outer spelling
   contains `+`, `-`, `/`, `=`, `\wedge`, `\vee`, `\cdot`,
   `\times`, or `\mathbin`.
4. Otherwise brace a base that already has the same outer script marker.
   This covers powers, names, and script-style exponential wrappers without
   treating a nested script inside `\widehat{x^2}` as an outer script.

The shared guard replaces the previous subscript-only regex. Escaped braces
and underscores are distinguished from grouping and script syntax. A trailing
LaTeX control word in a prefix gets a separating space; punctuation and
already-terminated commands keep their existing spelling.

This is not a TeX parser or validator, macro expansion, algebraic name
inference, or a general precedence policy for opaque labels. Callers still
supply valid LaTeX. For structured mathematical expressions, use `Call`
or semantic nodes; for opaque complex labels outside the bounded vocabulary,
supply explicitly grouped spellings. ASCII/Unicode names, `Name.from_latex`,
numeric operations, and stored expressions are unchanged. This follows
ADR-078's emitter ownership and replaces the relevant v1 heuristic from
ADR-067 without restoring private expression flags.

## Verification and consequences

The new safety tests first reproduced 22 failures against the unchanged v2
emitter. All 161 migrated, safety, and boundary cases now pass, with 100%
line/branch coverage in the three test files. All new emitter paths are
covered; full-suite emitter coverage increases from 92% to 94%.
Fresh-process gates prohibit every legacy import, and all 154 public cases
also pass directly from the built wheel with package origins verified.

The full package/release suites pass 5,241 cases on Python 3.11 and 5,358 on
Python 3.14, including maintained notebook exports. The existing matrix
complex-to-real warning remains. Type checking reports 295 existing errors;
this is not the final release gate.

Removing `test_latex_build.py` from the construction ledger reduces it
from twelve files to eleven. The remaining rendering/mixed suites, engine
deletion, and final artifact gates remain separate work. No changelog,
release version, or notebook content is changed.
