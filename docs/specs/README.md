# Specifications Index

Formal specifications for galaga's rendering and formatting behaviour.
Each spec defines the authoritative rules for a subsystem, with decision
tables and examples that map directly to tests.

## Specs

| Spec | Status | Description |
|---|---|---|
| [SPEC-001](SPEC-001-latex-coefficient-rendering.md) | Draft | LaTeX coefficient formatting and scientific notation |
| SPEC-002 | Planned | Precedence and parenthesisation rules |
| SPEC-003 | Planned | Notation system: kinds, dispatch, and override semantics |
| SPEC-004 | Planned | Display method: name/reveal/eval deduplication |
| SPEC-005 | Planned | Accent width selection (narrow vs wide) |
| SPEC-006 | Planned | Postfix wrapping: compound names, superscripts, fractions |
| SPEC-007 | Planned | Unicode coefficient formatting |
| SPEC-008 | Planned | Lazy/eager propagation rules |
| SPEC-009 | Planned | Expression tree rendering (SlashFrac, Frac, Sup interactions) |

## Format

Each spec uses a hybrid format:
- **Intent**: why this behaviour exists
- **Rules**: decision tables defining input → output mappings
- **Examples**: concrete input/output pairs (verifiable against tests)
- **Edge cases**: explicitly documented boundary conditions
