# Specifications Index

Formal specifications for galaga's rendering and formatting behaviour.
Each spec defines the authoritative rules for a subsystem, with decision
tables and examples that map directly to tests.

## Specs

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
| [SPEC-011](SPEC-011-display-ordering.md) | Pending | Custom basis blade display ordering |

## Format

Each spec uses a hybrid format:
- **Intent**: why this behaviour exists
- **Rules**: decision tables defining input → output mappings
- **Examples**: concrete input/output pairs (verifiable against tests)
- **Edge cases**: explicitly documented boundary conditions
