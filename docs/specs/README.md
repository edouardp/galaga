# Presentation and Annotation Specifications

SPEC-001 through SPEC-013 record the Galaga 1 rendering, naming, and
expression design. SPEC-015 describes the current optional annotation package
and identifies its remaining proposed capabilities.

For current behavior, start with:

- [Galaga 2 presentation configuration](../v2/presentation-configuration.md);
- [expression provenance](../v2/expression-provenance.md);
- [semantic rendering](../v2/rendering-implementation.md);
- [exact rendering contracts](../v2/exact-rendering-contracts.md); and
- the implemented [numeric core specifications](../core/specs/README.md).

Statuses below describe completion against the Galaga 1 design at the time.
Examples using `.name()`, `.symbolic()`, `.numeric()`, or `symbolic=True` are
historical; Galaga 2 uses immutable `.named()` and `expr=True`.

For implemented annotations, see
[the package guide](../../packages/galaga_annotation/README.md) and
[SPEC-015](SPEC-015-expression-and-matrix-annotations.md). The specification
distinguishes supported targets and effects from future refinements.

## Specification index

| Spec | Status | Description |
|---|---|---|
| [SPEC-001](SPEC-001-latex-coefficient-rendering.md) | Draft | LaTeX coefficient formatting and scientific notation |
| [SPEC-002](SPEC-002-precedence-parenthesisation.md) | Draft | Precedence and parenthesisation rules |
| [SPEC-003](SPEC-003-notation-system.md) | Draft | Notation system: kinds, dispatch, and override semantics |
| [SPEC-004](SPEC-004-display-method.md) | Draft | Display method: name/reveal/eval deduplication |
| [SPEC-005](SPEC-005-accent-width.md) | Draft | Accent width selection (narrow vs wide) |
| [SPEC-006](SPEC-006-postfix-wrapping.md) | Draft | Postfix wrapping: compound names, superscripts, fractions |
| [SPEC-007](SPEC-007-unicode-coefficient-formatting.md) | Draft | Unicode coefficient formatting |
| [SPEC-008](SPEC-008-lazy-eager-propagation.md) | Draft | Lazy/eager propagation rules |
| [SPEC-009](SPEC-009-expression-tree-rendering.md) | Draft | Expression tree rendering (SlashFrac, Frac, Sup interactions) |
| [SPEC-010](SPEC-010-blade-naming-display.md) | Accepted | Blade naming and display system |
| [SPEC-011](SPEC-011-display-ordering.md) | Accepted | Custom basis blade display ordering |
| [SPEC-012](SPEC-012-algebra-symbolic-split.md) | Complete | Algebraic/symbolic split via operation registry |
| [SPEC-013](SPEC-013-decoupled-symbolic-naming.md) | Accepted | Decoupled symbolic naming and expression trees |
| [SPEC-015](SPEC-015-expression-and-matrix-annotations.md) | Partial | Optional semantic annotations for expressions and matrix representations |

## Format

Each historical spec uses a hybrid format:

- **Intent**: why this behaviour exists
- **Rules**: decision tables defining input → output mappings
- **Examples**: concrete input/output pairs (verifiable against tests)
- **Edge cases**: explicitly documented boundary conditions
