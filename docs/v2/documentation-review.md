# Post-a4 Documentation Review

Date: 2026-09-11. Base commit: `17118f2` on `galaga_v2`.
This records a documentation and regression-test update, not a release or a
replacement for the [clean-candidate release gate](legacy-engine-deletion-gate.md#remaining-release-actions).

## Scope and findings

The review inventoried all 269 tracked Markdown files, including package
guides, specifications, ADRs, release instructions, notebook design notes and
root-level transcripts. Current guidance was checked against the implemented
API and existing validation evidence. Historical plans and external-library
surveys were distinguished from current contracts rather than rewritten as if
their proposals had all shipped. `AGENTS.md` and `CHANGELOG.md` were left unchanged.

The substantive corrections are:

- Retired legacy engines, bridge imports, expression constructors and temporary
  aliases are no longer described as supported or awaiting implementation.
- Release and typing guidance reflects blocking local validation, no required
  CI, and the distinction between preparation evidence and final publication.
- Matrix documents distinguish implemented general-Gram compact and named-basis
  conversion from proposed native-CGA quaternion/Vahlen APIs. Executable examples
  use current naming, explicit compact modes where required, and complex scalars
  in the matrix layer rather than real multivectors.
- Product guidance uses the current unscaled bracket names, explicit half
  variants, scalar pairing and contraction notation.
- The [duality guide](../what_is_dual.md) now includes the metric extension in
  general-Gram formulas, limits the simpler formula to the orthonormal Euclidean
  case, and explains mixed grades and degenerate metrics. Related ADRs correct
  the old geometric-product definition of complement and the supposed
  mixed-grade difference between contraction and multiplication by inverse $I$.

No runtime algorithm, public API, package version, dependency or release policy
changed. Existing historical counts remain attached to their original checkpoints.

## Validation

- Full source package and release-workflow suite, Python 3.11.15:
  **9,620 passed, 170 skipped**.
- Full source package and release-workflow suite, Python 3.14.4:
  **9,862 passed, 20 skipped**, including all 88 maintained notebook exports.
- Nineteen new parametrized regression cases execute the corrected guide
  examples and check the duality formulas against actual basis products in
  both core and facade, across Euclidean, mixed-signature, oblique, null-pair,
  degenerate and native-null CGA metrics.
- The relative Markdown file-target audit checks 923 targets with none missing. It does
  not claim to validate every heading fragment or remote HTTP destination.
- Configured release Markdown lint and Ruff checks pass. The broader tracked
  Markdown scan reports 1,227 findings versus 1,230 at the base commit, with
  no new or increased findings by file, rule and diagnostic. Existing formatting
  debt in historical material is not a globally clean lint result.

The full suites use the repository's current runtime source with dependencies
from the isolated Python environments prepared for the preceding release-gate
review. These are source tests, not fresh installed-artifact validation.
Third-party comparison recipes were not rerun, and no package was published.
