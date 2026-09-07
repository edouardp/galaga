---
status: accepted
date: 2026-09-07
deciders: edouard
---

# ADR-100: Explicit Bounded LaTeX Name Conversion

## Context and problem statement

The 108 symbol-conversion tests still imported the old `galaga.latex_symbols`
module, and one constructed a legacy multivector. Immutable `Name` retained
explicit spellings but offered no replacement for v1's LaTeX-driven naming.
Replacing these tests with spelling passthrough would lose a real capability.

Probes against commit `88aff5d1670fa91711cd2861628e30439de52d8b` also
exposed incorrect font arithmetic: `\mathbb{a}` produced “𝕘”,
`\mathcal{a}` produced an unassigned codepoint, and `\mathbb{ℍ}`
produced an emoji. Lowercase script/double-struck letters used uppercase
offsets; unrestricted Unicode `\w` admitted characters that cannot use
Latin-alphabet offsets. Digits also incorrectly followed letter arithmetic.

## Decision outcome

Make `galaga.names.LatexSymbols` the public lookup API, with one private
implementation in `galaga._latex_symbols`. The utility depends only on the
standard library, not core arithmetic, the facade, expression nodes, or a
renderer. Retain all existing explicit Greek, symbol, operator, relation,
arrow, and valid accent mappings, including `lambda_` and combining accents.

Keep conversion bounded and exact:

- Five math fonts accept one ASCII Latin letter. Uppercase and lowercase use
  their own blocks, with Letterlike Symbol exceptions for Unicode gaps.
- Bold and double-struck fonts accept ASCII digits using their digit blocks.
  Italic, script, and fraktur digit forms are unsupported.
- Hat, tilde, bar, vector, dot, and double-dot accents accept one ASCII letter
  or digit. Their derived ASCII spelling is the accent name plus underscore
  plus the input character; their Unicode form remains decomposed.
- Nested commands, multi-character bodies, arbitrary macros, and non-ASCII
  font/accent bodies are unsupported, not guessed.
- `lookup` returns `(unicode, ascii)` or `None` for unsupported strings.
  `unicode` and `ascii` share that lookup. Input must be a string; matching
  consumes the whole input and does not strip whitespace.

The mappings follow the Unicode Consortium's
[Mathematical Alphanumeric Symbols](https://www.unicode.org/charts/nameslist/n_1D400.html)
and [Letterlike Symbols](https://www.unicode.org/charts/nameslist/n_2100.html)
tables. Tests use Unicode names and compatibility decomposition independently
of production's offsets and exception tables.

Add `Name.from_latex(latex, *, ascii=None, unicode=None)` as an explicit
opt-in factory. It strips surrounding whitespace, rejects blank/non-string
input, derives supported spellings, and honors each explicit override.
Unsupported text requires `ascii=`; Unicode then defaults to that spelling
unless supplied separately. Empty or non-string overrides fail existing
`Name` validation rather than silently becoming defaults.

Ordinary `Name(...)` construction and `value.named(...)` do not infer
spellings or change signatures. Users migrate
`value.name(latex=r"\theta")` to `value.named(Name.from_latex(r"\theta"))`.
This replaces ADR-024's implicit derivation and raw-LaTeX fallback for v2,
while preserving ADR-076's immutable, presentation-only ownership.

The old `galaga.latex_symbols` path is a temporary same-object re-export,
not a second converter. It stays warning-free while legacy internal consumers
remain and is scheduled for Phase 9 removal before stable `2.0.0`. Its
manifest target is now `galaga.names`. It remains in the historical-path
retirement inventory, not the supported v2 entry-point set; a separate fresh
process checks the shim without allowing any legacy engine imports.

## Validation and consequences

Retain all 108 original test identifiers and valid literal mapping assertions.
Only their canonical import and the final multivector-naming integration
change. Exhaustive tests cover all 260 font letters, all 50 digit/font pairs,
every ASCII letter/digit under all six accents, malformed and Unicode input,
overrides, fallback errors, immutable names, and the original mapping bugs.

Independent Gram-derived product checks across Euclidean, degenerate,
oblique, and native-null metrics establish values before applying labels.
Naming preserves core identity, coefficients, equality, hashes, and explicit
expression replay. Fresh-process gates run both public suites with the old
converter path and all legacy engine imports blocked.

This work removes `test_latex_symbols.py` from the construction-exemption
ledger, reducing it from fourteen to thirteen files. It neither changes
numeric semantics nor adds automatic naming to renderers or the core.
Remaining notation/mixed tests, engine deletion, and final release gates are
separate work.
