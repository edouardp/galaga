# SPEC-005: Accent Width Selection

## Intent

LaTeX accents (`\tilde`, `\hat`, `\bar`) have narrow and wide variants
(`\widetilde`, `\widehat`, `\overline`). Narrow accents look correct on
single glyphs; wide accents are needed for multi-character expressions.

## Rules

### Rule 1: Single-Glyph Detection

A Sym's LaTeX name is a single glyph if:
- It is 1 character long (e.g. `a`, `R`), OR
- It starts with `\` (a LaTeX command rendering as one glyph: `\theta`, `\mathbf{F}`)

### Rule 2: Accent Selection

| Child | Accent | Example |
|---|---|---|
| Single-glyph Sym | Narrow (`\tilde`, `\hat`, `\bar`) | `\tilde{R}` |
| Multi-char Sym (e.g. `SR`) | Wide (`\widetilde`, `\widehat`, `\overline`) | `\widetilde{SR}` |
| LaTeX command Sym (e.g. `\theta`) | Narrow | `\tilde{\theta}` |
| Compound expression | Wide | `\widetilde{a + b}` |

### Rule 3: Unit Accent Special Case

For `Unit` with accent kind:
- Single-glyph Sym → narrow hat: `\hat{a}`
- Multi-char Sym or compound → fraction form: `\frac{x}{\lVert x \rVert}`

This is because `\widehat{SR}` looks odd for unit vectors; the fraction
form is clearer.
