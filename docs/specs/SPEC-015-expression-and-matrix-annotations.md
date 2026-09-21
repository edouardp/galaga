# SPEC-015: Expression and Matrix Annotations

## Status

Partially implemented Galaga 2 extension specification. This document defines
the boundary and rendering model for the optional `galaga_annotation` package
in `packages/galaga_annotation`. The first milestone provides immutable rules,
callable annotators, whole-expression / expression-path / operator / variable /
grade / term / coefficient targets, and a KaTeX renderer with escaped plain
labels plus an explicit trusted raw-label mode for colours, fills, borders,
arrows, rules, braces, group accents, underlines and boxes.
See [ADR-142](../adrs/142-reusable-callable-annotators.md) and
[ADR-147](../adrs/147-katex-annotation-lowering-and-decoration-wrappers.md).

Sentence spans, semantic-role targets, expression-to-matrix
provenance and arithmetic propagation remain later milestones. Matrix cell and
region annotations are implemented for content colour, fill, border, emphasis,
cell labels and whole-matrix markers; region block callouts and separate
row/column header labels remain a later refinement. See
[ADR-149](../adrs/149-matrix-cell-and-region-annotations.md). Sign-only targets
are implemented for visible sum signs; a singleton negative term has no
separate sign slot and falls back to the term body. See
[ADR-150](../adrs/150-sign-only-annotation-targets.md). Content-part targets
select the displayed name, expression, or value side, following the active
content setting. See
[ADR-151](../adrs/151-content-part-annotation-targets.md). Subexpression targets
find a provenance subtree structurally by value. See
[ADR-152](../adrs/152-subexpression-annotation-targets.md).

Implemented prerequisite: core `galaga.rendering.value_document` now supplies
separate immutable anchors for visible concrete terms, coefficient magnitudes,
signs, and blades. See
[ADR-143](../adrs/143-concrete-render-documents-and-semantic-anchors.md).
Core `expression_document` also provides source occurrence mapping and
expression, symbol, and operator anchors, including implicit product extents.
See [ADR-144](../adrs/144-expression-render-occurrence-anchors.md).
`content_document` combines visible teaching parts and their anchors;
presenter views expose `render_document` with captured settings. See
[ADR-145](../adrs/145-teaching-render-documents-and-presenter-capture.md).
Expression-literal components are also anchored by original operand scope
using `select(..., scope="expr", path=...)`, which selects components at or
below the original occurrence path (`()` selects the whole expression
subtree). See [ADR-146](../adrs/146-expression-component-anchor-scopes.md).
Extension wrapper adapters and the annotation package are implemented in
`packages/galaga_annotation`; the package participates in the joint release
workflow and the teaching gallery. Matrix cell and region targets are
documented in [ADR-149](../adrs/149-matrix-cell-and-region-annotations.md).

Related implemented designs:

- [presentation configuration](../v2/presentation-configuration.md)
- [expression provenance](../v2/expression-provenance.md)
- [semantic rendering](../v2/rendering-implementation.md)
- [ADR-068: Recognize Known Multivectors](../adrs/068-recognize-known-mvs.md)
- [ADR-139: Reusable Presentation Views](../adrs/139-reusable-presentation-views.md)

## Intent

The extension provides semantic annotations for teaching, explanation, and
inspection of geometric-algebra calculations. It can highlight or label an
entire value, a subexpression, an operation, a blade, or a region of a matrix
representation.

Annotations are presentation metadata. They must not change numerical values,
expression evaluation, equality, hashing, or algebra semantics.

The primary initial renderer is KaTeX, as used by Marimo. Other renderers may
consume the same annotation plan.

## Part I — Annotation capabilities

This section defines what users should be able to show. The examples are
capability sketches, not yet a final Python API. They use the existing Galaga
operations and presentation vocabulary so that the intended result remains
clear while the target model is still being designed.

### 1. Label a complete value or expression

An annotation can explain the role of a complete result:

```python
annotate(rotor * vector * ~rotor, label="rotor sandwich")
```

The intended KaTeX shape is:

```latex
\overset{
  {\color{seagreen}\substack{\text{rotor sandwich} \\ \downarrow}}
}{R v \widetilde{R}}
```

This is useful for teaching a named construction without changing the
underlying expression or replacing the active notation.

### 2. Label an operand or subexpression

Annotations can explain the parts of a larger expression:

```python
expr = (e1 + e2) ^ e3

annotate(expr, target=(0,), label="vector sum", side="below")
annotate(expr, target=(1,), label="third basis vector", side="above")
```

The intended result is visually equivalent to:

```latex
\underset{\text{vector sum}}{(e_1 + e_2)}
\wedge
\overset{\text{third basis vector}}{e_3}
```

The target refers to the semantic expression tree. It must not depend on
counting characters in a rendered LaTeX string.

### 3. Explain an operation

An annotation can identify the mathematical operation represented by a
function name or notation symbol:

```python
annotate(
    metric_inner_product(e1, e2),
    operation="metric_inner_product",
    label="metric pairing",
)
```

With a functional presentation this may render as:

```latex
\overset{\text{metric pairing}}{\operatorname{metric\_inner\_product}}(e_1,e_2)
```

With a geometric presentation it may instead annotate the operator symbol:

```latex
e_1 \mathbin{\overset{\text{metric pairing}}{\bullet}} e_2
```

The annotation targets the canonical operation ID, while the active
`Notation` decides whether the operation is shown as `metric_inner_product`,
`\bullet`, `\cdot`, or another configured form.

### 4. Highlight a term or span

Text colour is a lightweight way to draw attention to a term:

```python
highlight(e1 ^ e2, color="royalblue")
```

A filled or bordered box is useful when the highlighted region must remain
visible in a dense equation:

```python
box(
    e1 ^ e2,
    fill="#e8f5e9",
    border="seagreen",
)
```

The KaTeX backend may lower these to `\textcolor`, `\colorbox`, or
`\fcolorbox`. The semantic annotation must remain independent of that visual
choice.

### 5. Mark a multivector term, coefficient, or grade

The displayed terms of a multivector are semantic display items, even when
they are not separate expression nodes:

```python
A = 0.5 + 2 * e1 - 3 * (e1 ^ e2)

annotate_term(A, mask=e1 ^ e2, label="bivector part")
highlight_grade(A, grade=1, color="darkorange")
```

Possible output:

```latex
0.5 + \color{darkorange}{2e_1}
  - \underbrace{3e_{12}}_{\text{bivector part}}
```

Term selection must use the active Galaga display order and blade convention.
It must never assume bitmap order or reconstruct blade names independently.

### 6. Show a relationship between expression and value

Annotations can explain both sides of an eager calculation:

```python
result = (e1 + e2) ^ e3
annotate(result, target="expression", label="computed as")
annotate(result, target="value", label="evaluated bivector")
```

For a full display, the intended shape is:

```latex
x
\quad = \quad
\overset{\text{expression}}{(e_1 + e_2) \wedge e_3}
\quad = \quad
\underset{\text{evaluated bivector}}{e_{13} + e_{23}}
```

This capability must respect the existing `content="name"`, `"expr"`,
`"value"`, and `"full"` presentation choices.

### 7. Group terms with braces, brackets, or underlines

Structural annotations can communicate a span without changing its contents:

```python
underbrace(e1 + e2, label="vector sum")
overbrace(e1 ^ e2, label="simple bivector")
```

Candidate lowerings include:

```latex
\underbrace{(e_1 + e_2)}_{\text{vector sum}}
```

and:

```latex
\overbrace{e_1 \wedge e_2}^{\text{simple bivector}}
```

These are span annotations, not merely labels attached to the first token of
the target.

### 8. Show cancellation or simplification

An annotation may explain why a term vanishes or changes form:

```python
cancel(e1 ^ e1, reason="alternating product")
```

Possible renderings include:

```latex
\cancel{e_1 \wedge e_1}
```

or an equality annotation:

```latex
e_1 \wedge e_1
\overset{\text{alternating product}}{=}
0
```

Cancellation should be an explicit teaching annotation. The annotation system
must not infer that a numerical zero is mathematically interesting without a
user or higher-level helper requesting it.

### 9. Show a derivation or transition

A derivation is a sequence of complete expressions rather than one annotated
expression tree:

```python
derive(
    (R * v * ~R, "rotor action"),
    ((R * v * ~R).grade(1), "vector projection"),
)
```

The intended rendering is conceptually:

```latex
R v \widetilde{R}
\xrightarrow{\text{rotor action}}
v'
\xrightarrow{\text{vector projection}}
\langle v' \rangle_1
```

Derivations need their own ordered-step model. They should not be forced into
ordinary expression paths merely because both eventually render as KaTeX.

### 10. Annotate matrix rows, columns, entries, and blocks

Matrix annotations should support the same explanatory vocabulary:

```python
annotate_region(
    matrix,
    rows=slice(0, 2),
    columns=slice(0, 2),
    label="left-chiral block",
)
```

Other examples include:

```python
annotate_row(matrix, 0, label="image of e₁")
annotate_column(matrix, 3, label="right projector")
annotate_entry(matrix, row=1, column=2, label="mixing term")
```

The matrix renderer may use coloured cells, borders, row/column labels, or
callouts. A matrix adapter must validate the selected shape and must not infer
semantic meaning from arbitrary numeric entries.

#### 10.1. Colour individual cells and ranges

Matrix annotations should distinguish content colouring from cell-background
colouring. A KaTeX backend can colour the content of selected cells:

```latex
\left(\begin{array}{cccc}
a_{11} & a_{12} & a_{13} & a_{14} \\
a_{21} & \colorbox{#e8f5e9}{$a_{22}$} & \colorbox{#e8f5e9}{$a_{23}$} & \colorbox{#e8f5e9}{$a_{24}$} \\
a_{31} & \colorbox{#e8f5e9}{$a_{32}$} & \colorbox{#e8f5e9}{$a_{33}$} & \colorbox{#e8f5e9}{$a_{34}$} \\
a_{41} & \colorbox{#e8f5e9}{$a_{42}$} & \colorbox{#e8f5e9}{$a_{43}$} & \colorbox{#e8f5e9}{$a_{44}$}
\end{array}\right)
```

This represents the displayed mathematical range rows 2--4, columns 2--4.
In a Python-facing API that range is conventionally represented by:

```python
MatrixRegion(rows=slice(1, 4), columns=slice(1, 4))
```

The same region may be rendered as one block:

```latex
\fcolorbox{seagreen}{#e8f5e9}{$
  \begin{matrix}
    a_{22} & a_{23} & a_{24} \\
    a_{32} & a_{33} & a_{34} \\
    a_{42} & a_{43} & a_{44}
  \end{matrix}
$}
```

`\fcolorbox` around an inner matrix is useful for a block-partitioned
representation, but it is not a true background for the outer `array` cells.
KaTeX does not provide `\cellcolor` in its baseline command set. A renderer
with access to the actual matrix layout may instead emit trusted HTML/CSS:

```html
<td style="background-color: #b8e6bf; border: 1px solid #666;">
  \(e_{12}\)
</td>
```

The semantic target is the same in both cases; only the lowering differs.

#### 10.2. Colour semantic multivector parts

Colour may represent grade, but it may also represent a domain-specific role.
For example, a grade-coloured multivector can use one stable colour per grade:

```latex
A = \textcolor{#111827}{A_0}
  + \textcolor{#0072B2}{A_1}
  + \textcolor{#D55E00}{A_2}
  + \textcolor{#009E73}{A_3}
  + \textcolor{purple}{A_4}
```

The same rendering machinery can colour non-contiguous terms that share a
geometric role, even when they have the same grade:

```latex
c =
\colorbox{#b8e6bf}{$c_{gx}e_{423}+c_{gy}e_{431}+c_{gz}e_{412}+c_{gw}e_{321}$}
+
\colorbox{#d8c4ee}{$c_{vx}e_{415}+c_{vy}e_{425}+c_{vz}e_{435}+c_{mx}e_{235}+c_{my}e_{315}+c_{mz}e_{125}$}
```

Here the first span may be labelled “carrier plane” and the second “flat
line”; the colour is a semantic role colour, not a grade colour. The same
principle applies to a conformal-style vector split into carrier-point and
infinity components, or to an even multivector split into rotation and
moment/displacement quaternion-like parts.

#### 10.3. Involution sign annotations

Grade colouring can be combined with an explanation of involutions. For a
homogeneous grade-\( r \) component:

```latex
\widehat{A_r}=(-1)^rA_r \qquad
\widetilde{A_r}=(-1)^{r(r-1)/2}A_r \qquad
\overline{A_r}=(-1)^{r(r+1)/2}A_r
```

The first few sign patterns are:

| grade | 0 | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|
| grade involution `\widehat{A}` | + | − | + | − | + |
| reverse `\widetilde{A}` | + | + | − | − | + |
| Clifford conjugation `\overline{A}` | + | − | − | + | + |

Thus grade involution flips odd grades, reverse flips grades congruent to 2 or
3 modulo 4, and Clifford conjugation flips grades congruent to 1 or 2 modulo
4. The annotation should colour the grade component and render the sign
change explicitly; it must not suggest that the involution changed the
component's grade.

#### 10.4. Arrow, leader, and group styles

The same semantic target may support several callout styles:

```latex
% arrow-only callout
\overset{\substack{\text{input vector} \\ \downarrow}}{v}

% plain leader line
\underset{\substack{\rule[0.2em]{0.4pt}{1em} \\ \text{constant}}}{k}

% brace and group accents
\underbrace{a+b}_{\text{input block}}
\qquad
\overbrace{c+d}^{\text{output block}}
\qquad
\undergroup{e_1\wedge e_2}_{\text{bivector}}
\qquad
\overgroup{e_3\wedge e_4}^{\text{bivector}}
```

Arrow-only callouts must not require a vertical leader. A `\rule` leader is a
separate available style. `\mathrlap`, `\mathllap`, `\mathclap`, and small
`\mkern` adjustments may provide renderer-owned layout hints, but arbitrary
character offsets must not become part of target identity.

Annotation labels may also use local size hierarchy:

```latex
\overset{\substack{\Large\text{primary label} \\ \small\downarrow}}{A}
\qquad
\overset{\substack{\scriptsize\text{secondary label} \\ \scriptscriptstyle\downarrow}}{B}
```

Sizes, colours, fills, borders, arrows, braces, and leaders are presentation
styles. They do not change the semantic target.

### 11. Combine multiple annotations and avoid collisions

The renderer must support nearby annotations such as:

```python
annotate(expr, target=(0,), label="input vector", side="above")
annotate(expr, target=(0,), label="grade one", side="below")
annotate(expr, target=(1,), label="rotor", side="above")
annotate(expr, target=(2,), label="reverse", side="below")
```

The KaTeX proof of concept shows that adjacent labels need layout treatment.
The backend should:

1. keep labels centred on their semantic anchors;
2. estimate label widths;
3. detect neighbouring collisions;
4. assign shallow above/below tiers;
5. let KaTeX reserve the final horizontal width;
6. expose the solved layout for debugging and tests.

### 12. Recognize known values

The existing Marimo recognition feature remains useful:

```python
gm.md(t"Result: {result}", recognize=[up_state, down_state])
```

It answers “which known value does this equal?” and may render an annotation
such as `$(\equiv \uparrow)$`.

This is distinct from expression annotation, which answers “what role does
this expression or subexpression play?” The two mechanisms should compose but
must not duplicate one another's numeric matching logic.

### 13. Format and presentation independence

The same semantic annotation should work with different Galaga presenters:

```python
functional = annotate(value, label="computed value")
lengyel = annotate(value, label="computed value")

presets.presenters.functional()(functional)
presets.presenters.lengyel()(lengyel)
```

The annotation follows the expression or matrix target. The active
`PresentationConfig` controls blade names, display order, notation, content,
and output target. An annotation must not smuggle in a second blade convention
or silently reorder the value.

## Part II — Targets, APIs, and architecture

### Architectural boundary

`galaga_annotation` is optional. The dependency direction is:

```text
galaga_annotation -> galaga
galaga_annotation -> galaga_matrix   (optional integration)
galaga -> galaga_annotation          (forbidden)
```

Galaga provides expression and rendering protocols. The extension owns
annotation metadata, selection, layout, and renderer adapters. Importing
Galaga must not import or require `galaga_annotation`.

The extension may depend on `galaga_matrix` for matrix-specific adapters, but
ordinary expression annotations must not require the matrix package.

### Semantic model

An annotation plan is format-neutral:

```python
AnnotationPlan(
    annotations=(
        Annotation(
            target=ExpressionPath((0,)),
            label="vector part",
            role="operand",
            style=AnnotationStyle(color="royalblue"),
            side="below",
        ),
    ),
)
```

The plan is lowered later by a renderer-specific backend:

```text
Galaga value or matrix representation
        ↓
semantic render tree + annotation plan
        ↓
renderer layout solution
        ↓
KaTeX, HTML, matrix display, or another output
```

The plan must not contain renderer-specific TeX as its normal representation.
Raw renderer markup may be supported as an explicit advanced escape hatch.

### Annotation attachment targets

The central design question is not “which characters should be coloured?” but
“which semantic object should receive the annotation?” A target must survive
changes to presentation, blade ordering, notation, compactness, and output
backend. Rendered character offsets are therefore never the primary identity
of a target.

The initial target taxonomy is:

| Target kind | What it selects | Typical teaching question |
|---|---|---|
| `WholeExpression` | The complete expression or value | “What is this result?” |
| `ContentTarget` | One displayed content part: the name, expression, or value side | “Which side is the definition?” |
| `ExpressionPath` | One expression-tree node or nested operand | “What role does this operand play?” |
| `ExpressionSpan` | A contiguous semantic range of sibling nodes | “Which part of this sum/product is the input block?” |
| `VariableTarget` | A named variable or symbolic value | “Which symbol is the rotor?” |
| `SubexpressionTarget` | A provenance subtree occurrence, matched structurally | “Which factor is the reverse?” |
| `OperationTarget` | A canonical operation node or operator occurrence | “What does this `\bullet` mean?” |
| `RelationTarget` | An equality, assignment, implication, or transition relation | “Is this equality definitional or evaluated?” |
| `MultivectorTerm` | One coefficient-plus-blade display term | “What is the bivector term?” |
| `MultivectorCoefficient` | Only the scalar coefficient of one term | “Where did `1.354` come from?” |
| `MultivectorTermSet` | Several selected coefficient-plus-blade terms | “Which terms form the carrier plane?” |
| `MultivectorCoefficientSet` | Several scalar coefficients, possibly non-contiguous | “Which parameters control displacement?” |
| `GradeTarget` | All terms of one grade | “Which part is the bivector grade?” |
| `SemanticRoleTarget` | A domain-defined span such as `rotation` or `infinity` | “Which terms represent the flat-line part?” |
| `MatrixCell` | One matrix coordinate | “What is this mixing coefficient?” |
| `MatrixRegion` | A row, column, rectangle, or block | “Which entries form the chiral block?” |

The distinction between a term and its coefficient is important. Given a
displayed multivector containing:

```text
1.354 e₁
```

these are different targets:

```python
MultivectorCoefficient(blade=e1)  # selects only 1.354
MultivectorTerm(blade=e1)         # selects 1.354 e₁
```

The coefficient target must remain valid whether the presenter renders the
term as `1.354 e₁`, `1.354e₁`, or as a named component. The term target must
remain valid whether the coefficient is displayed before or after the blade,
for example:

```text
1.354 e₁       # coefficient-first presentation
e₁ 1.354       # blade-first presentation, if a presenter permits it
```

An annotation may select one or many components without requiring callers to
construct a character range:

```python
annotate(A, target=MultivectorCoefficient(blade=e1), label="weight")
annotate(A, target=MultivectorTerm(blade=e1), label="vector contribution")
annotate(
    A,
    target=MultivectorCoefficientSet(blades=(e1, e2, e3)),
    label="carrier-point coordinates",
)
annotate(
    A,
    target=MultivectorTermSet(blades=(e423, e431, e412, e321)),
    label="carrier plane",
)
```

The renderer may lower a selected coefficient, term, or set of terms to text
colour, a filled box, a border, a brace, or an arrow callout. The selection
must be preserved even if the selected terms are separated by other terms in
the active display order.

#### Expression spans

An `ExpressionPath` identifies a node. An `ExpressionSpan` identifies a
contiguous range of semantic children within a parent node. This is useful for
annotations that are neither a single operand nor the whole expression:

```python
expr = a + b + c + d

annotate(expr, target=ExpressionSpan(parent=(), start=0, stop=2),
         label="input block")       # a + b
annotate(expr, target=ExpressionSpan(parent=(), start=2, stop=4),
         label="output block")      # c + d
```

The span is defined before rendering and may be lowered as:

```latex
\overbrace{a+b}^{\text{input block}}
\qquad
\underbrace{c+d}_{\text{output block}}
```

The API should reject spans that cross unrelated expression-tree parents. A
caller who wants to annotate a mathematically meaningful but non-contiguous
set should use a set target, such as `MultivectorTermSet`, rather than a
synthetic character range.

#### Variables and named values

Variables need a first-class target because a variable may occur more than
once and because a displayed name is not necessarily the same as its Python
identifier:

```python
annotate(expr, target=VariableTarget(name="rotor"), label="unit rotor")
```

The target may select all occurrences or one occurrence:

```python
VariableTarget(name="R", occurrence="all")
VariableTarget(name="R", occurrence=0)
```

Occurrence selection is semantic and follows the expression tree. It must not
be implemented by searching for repeated rendered text.

#### Operators and relations

An operator target selects an operation occurrence. Its visual anchor is the
operator glyph or function name when present; an implicit operator uses the
displayed extent of that operation, as specified under Operation targets:

```python
annotate(expr, target=OperationTarget(operation_id="outer_product"),
         label="alternating product")
```

The same target can annotate either of these presentations:

```latex
\operatorname{outer_product}(a,b)
\qquad\text{or}\qquad
a \mathbin{\overset{\text{alternating product}}{\wedge}} b
```

Relations deserve a separate target because an equality sign can carry
meaning independently of the expressions on either side:

```python
annotate(result, target=RelationTarget(kind="equality"),
         label="evaluates to")
annotate(result, target=RelationTarget(kind="definition"),
         label="definition")
```

This allows a derivation to distinguish, for example, a definition (`:=`), an
algebraic identity (`=`), an approximation (`\approx`), and a representation
map (`\xmapsto{\rho}`).

#### Target composition

Some teaching annotations intentionally combine targets:

```python
Annotation(
    target=MultivectorTerm(blade=e1),
    label="carrier coordinate",
    style=AnnotationStyle(color="royalblue", background="#e7f0ff"),
)
```

The target remains singular and semantic; the annotation style may contain
several visual effects. A future `TargetGroup` may combine several different
target kinds, but the first implementation should prefer explicit target
sets, such as `MultivectorTermSet`, over an untyped list of arbitrary anchors.

### Annotation

The conceptual fields are:

```python
@dataclass(frozen=True)
class Annotation:
    target: Target
    label: str | None = None
    label_latex: str | None = None
    role: str | None = None
    style: AnnotationStyle | None = None
    side: Literal["above", "below", "auto"] = "auto"
    description: str | None = None
    missing: Literal["ignore", "error"] = "ignore"
    join: bool = False
```

Labels may contain multiple logical lines. A renderer decides how those lines
are laid out. Labels intended for ordinary users should be plain text; an
explicit trusted/raw mode may accept renderer-specific math markup. A plain
`label` renders upright with its spaces preserved (for example
`\text{carrier line}`) and newlines stack the lines; `label_latex` supplies
trusted raw LaTeX for equation labels and is mutually exclusive with `label`.

### Styles

Styles are semantic and renderer-neutral:

```python
@dataclass(frozen=True)
class AnnotationStyle:
    color: str | None = None
    background: str | None = None
    border: str | None = None
    label_color: str | None = None
    emphasis: Literal["normal", "bold", "italic"] = "normal"
    marker: Literal[
        "none",
        "arrow",
        "rule",
        "brace",
        "underline",
        "box",
        "underbrace",
        "underbracket",
        "overbrace",
        "undergroup",
        "overgroup",
        "overline",
        "overbracket",
    ] = "none"
    clearance: str | None = None
    overlay: bool = False
```

Semantic roles and visual styles remain separate. A notebook may render the
role `metric` in green in one context and purple in another without changing
the annotation's meaning.

A rule with a `marker` colours its **chrome** -- the bracket glyph and label
-- rather than the highlighted content, so a cyan overgroup does not recolour
the blades it spans. Labels and markers over sum-term spans are always lowered
as independent zero-width overlays, so their interval may be equal to, nested
in, disjoint from, or cross a joined highlight interval without splitting the
fill. `clearance` is the outward lift (for example `"4px"`), applied through a
raised zero-width `\rule{0pt}{1em}` inside `\vphantom`, so the bracket rises
while the visible terms stay on the baseline. A separate outer `\vphantom`
reserves the callout's height or depth without enlarging a joined background
fill. `overlay=True` retains the same behavior for direct-node annotations
that do not have a term interval.
External labels use `\mathclap`, so a label wider than its target remains
centred and visible but cannot widen the marker atom and shift its measured
expression away from the visible annotated terms.
For callouts, a visible negative sign is part of the selected term even when
it also separates that term from a preceding sum term. The zero-width overlay
and sign are emitted inside an explicit ordinary or binary math class, and the
phantom reproduces the visible sign advance. Content-only fills continue to
leave separators between disjoint spans outside both backgrounds.
When a sign-only rule and the joined span beginning at that sign request the
same background, they compose as one continuous fill rather than two adjacent
boxes. Other sign styles remain independent.
`label_color` colours only the label text, so a span label can match its fill
in a darker shade.

### Target selection

Targets must be stable under rendering and must not depend on Python object
identity. The initial target vocabulary is:

```python
Target = (
    ExpressionPath(...)
    | WholeExpression()
    | ContentTarget(kind="expr")
    | ExpressionSpan(parent=..., start=..., stop=...)
    | VariableTarget(name=..., occurrence=...)
    | SubexpressionTarget(expression=..., occurrence=...)
    | OperationTarget(operation_id="metric_inner_product")
    | RelationTarget(kind="equality")
    | MultivectorTerm(blade=...)
    | MultivectorCoefficient(blade=...)
    | MultivectorTermSet(blades=...)
    | MultivectorCoefficientSet(blades=...)
    | GradeTarget(grade=...)
    | SemanticRoleTarget(role=...)
    | MatrixCell(row=..., column=...)
    | MatrixRegion(...)
)
```

### Expression paths

An expression path is a tuple of child indices. The root path is `()`.

For:

```python
metric_inner_product(e1 + e2, e3)
```

the paths are:

```text
()       complete operation
(0,)     left operand: e1 + e2
(1,)     right operand: e3
(0, 0)   first operand of the addition: e1
(0, 1)   second operand of the addition: e2
```

Paths refer to the semantic expression tree, not to positions in a rendered
string. A renderer must obtain anchors from the semantic tree and must not
parse already-rendered LaTeX to rediscover them.

### Operation targets

An operation target selects nodes by canonical operation ID, such as
`metric_inner_product`, `outer_product`, or `reverse`. If multiple nodes
match, the plan must define whether all matches are annotated or whether an
occurrence selector is required. The initial default is all matching nodes.

Compatibility aliases must resolve to canonical operation IDs before matching.

#### Implicit operator fallback

Geometric-product juxtaposition is a required first-version case. A reusable
operator annotator must work with this common notation as well as functional
and explicit-symbol presentations. This is a deliberate notation-aware
anchor rule, not a general fallback for missing targets.

When the active notation deliberately omits an operator glyph, an operator
annotation attaches to the complete displayed expression for that operation
occurrence. For example, a geometric product rendered by juxtaposition has
no separate glyph between its operands, so the label spans `ab`:

```python
explain_product = ga.annotator().label(
    "geometric product",
    target=ga.operator("geometric_product"),
    marker="underbrace",
)

explain_product(a * b)
```

$$\underbrace{ab}_{\text{geometric product}}$$

The same rule targets the function name under functional notation, or the
explicit operator glyph under a notation that supplies one. The semantic
target is unchanged; only its visual anchor differs. Highlighting, arrows,
and other decorations use the same resolved anchor policy.

The renderer must distinguish an operator that is implicit by notation from
an operation with no visible representation. Its anchor metadata records
both the operation's displayed extent and whether its operator is explicit
or implicit. Do not infer this distinction by inspecting emitted LaTeX or
by treating every missing glyph as an implicit operator.

The fallback stays local to the selected operation occurrence. In `ab + c`,
it covers `ab`; in `(a + b)c`, it covers the entire product `(a + b)c`,
including the parentheses needed to represent its operand. It does not
expand to an enclosing sum, teaching equality, or computed result. Nested
product occurrences retain distinct anchors even when notation flattens
their display; their annotations may consequently overlap.

If simplification removes the operation, or the selected content mode hides
its expression, the normal empty-selection policy applies. The fallback
does not recreate an eliminated operation or attach its label to a result.

### Matrix regions

Matrix annotations use explicit regions rather than expression paths:

```python
MatrixRegion(rows=slice(0, 2), columns=slice(2, 4))
```

Regions may identify rows, columns, rectangular blocks, individual entries,
or named basis blocks. A matrix adapter must validate that a region belongs to
the represented matrix shape. A region is a target only; its label, style and
side belong to the surrounding `Annotation` (the `annotate_region(...)`
convenience above binds the two).

### Integration with Galaga values

#### Reusable annotators: the primary API

An annotation recipe is independent of the value it will annotate. The public
factory `annotator(*rules)` returns an immutable, callable `Annotator`.
Calling it with a multivector or supported matrix returns an annotated view,
not rendered markup. All APIs below are proposed, not currently implemented.

Three distinct objects make up this model:

1. `on(target, ...)` constructs an immutable annotation rule.
2. `annotator(*rules)` constructs a reusable recipe containing those rules.
3. `recipe(value)` binds the recipe to a value and returns an annotated view.

```python
import galaga_annotation as ga

highlight_bivectors = ga.annotator(
    ga.on(ga.grade(2), background="#fff3cd"),
)

highlight_bivectors(A)
highlight_bivectors(B)
```

A parameterized factory requires no special callback or predicate mechanism:

```python
def highlight_grade(grade, background="#fff3cd"):
    return ga.annotator(
        ga.on(ga.grade(grade), background=background),
    )

highlight_vectors = highlight_grade(1)
highlight_vectors(A)
```

Grade recipes need no algebra at construction. Blade-specific recipes may
carry an algebra-bound blade identity and must reject incompatible target
algebras rather than reinterpret the blade by its displayed name.

#### Functional and fluent construction

Functional construction exposes explicit, reusable rules:

```python
vector_lesson = ga.annotator(
    ga.on(ga.grade(1), background="#fff3cd"),
    ga.on(
        ga.grade(1),
        label="vector part",
        marker="underbrace",
        color="#888888",
        clearance="4px",
    ),
)
```

Fluent construction produces the same ordered annotation plan:

```python
vector_lesson = (
    ga.annotator()
    .highlight(ga.grade(1), background="#fff3cd")
    .label(
        "vector part",
        target=ga.grade(1),
        marker="underbrace",
        color="#888888",
        clearance="4px",
    )
)

vector_lesson(A)
```

Every builder method returns a new annotator and leaves the original
unchanged. Methods append rules; they never modify a previously selected
target. There is no mutable `.select(...)` state.

- `.highlight(target=whole(), ...)` appends a text/fill/border annotation.
- `.label(text, target=whole(), ...)` appends a label and optional marker.
- `.mark(target=whole(), ...)` appends a combined highlight and label rule.

`on(...)` and `.mark(...)` accept the same annotation fields. Directional
markers determine their side: `underbrace`, `underbracket`, `undergroup` and
`underline` are below, while `overbrace`, `overgroup`, `overline` and `overbracket`
are above; a contradictory
explicit `side` is an error. Neutral markers (`none`, `arrow`, `rule`,
`brace`, `box`) accept an explicit side, defaulting to `side="auto"`, which
resolves above unless the approximate layout solver moves the label to avoid
a collision; `brace` is a generic span marker lowered to `\overbrace` or
`\underbrace` according to that side. `clearance` is the outward distance between the
target and its marker, not a shift of the mathematical content. `marker` and
`clearance` are `AnnotationStyle` fields, so functional and fluent
construction produce identical plans.

Reusable annotators and teaching notebooks should prefer `underbrace`,
`underbracket`, `overbrace`, and `overbracket`. Group accents remain supported
for explicit stylistic use, but are not defaults because KaTeX gives them less
predictable spacing when labels are wide or spans are composed with
highlights.

```python
carrier_lesson = (
    ga.annotator()
    .mark(
        ga.terms(e41, e42, e43, e23, e31, e12),
        background="#b8e6bf",
        label="Carrier line",
        marker="rule",
        side="below",
    )
    .label(
        "Cocarrier normal",
        target=ga.terms(e41, e42, e43),
        marker="overbracket",
        color="#888888",
        clearance="4px",
    )
)
```

#### Selector conveniences and resolution

Public selector factories construct the semantic targets described above:

| Factory | Semantic selection |
|---|---|
| `whole()` | Complete displayed expression or value |
| `content(kind)` | Displayed `name`, `expr`, or `value` part |
| `operand(index)` / `path(*indices)` | Root operand / nested expression node |
| `operator(operation_id)` | Operator occurrences by canonical ID |
| `variable(name)` | Recorded named-symbol occurrences, not Python variable discovery |
| `subexpression(value, occurrence=...)` | Provenance subtree occurrences that match `value` structurally |
| `term(blade)` / `terms(*blades)` | Complete coefficient-plus-blade terms |
| `coefficient(blade)` / `coefficients(*blades)` | Coefficients only |
| `grade(r)` / `grades(*r)` | Complete terms of selected grades |
| `sign(blade)` | Displayed sign belonging to a term |
| `cell(row, column)` | Matrix entry |
| `row(index)` / `column(index)` | Matrix row / column |
| `block(rows=..., columns=...)` | Rectangular matrix region |

These are conveniences over target objects, not string searches in LaTeX.
Matrix indices are zero-based and slices are half-open. Expression selectors
require retained provenance; the extension must not reconstruct an operation
from a numerical result.

A rule with `join=True` renders adjacent selected terms as one continuous
span: internal separators stay inside the fill, a label appears once for the
run, and a sign leading the complete sum stays inside the highlight. A sign at
a later span boundary remains the surrounding sum's separator unless a
matching sign fill explicitly fuses it into the span. Rules without `join`
render each placement separately. Content styles form the visible base layer
and must currently nest or stay disjoint. Labels and markers occupy independent
above/below overlay channels and may cross the base highlight. One overlapping
callout is supported per side; overlapping callouts competing for the same
side raise `SpanLayoutError` until multi-lane stacking is added.

Value-component selectors default to the result side of an expression/value
display. Selecting components within an expression operand needs an explicit
expression-path scope; its exact convenience syntax remains open.
Whole-expression and operator selectors retain their semantic meanings.

Rules are validated structurally at construction, then against the bound
value and final presentation during rendering. A valid selector may match
zero visible targets: this is normal and silently produces no decoration by
default (`missing="ignore"`). No empty label, bracket, background, or reserved
annotation space is emitted. A rule may opt into `missing="error"` when a
lesson specifically requires a visible match.

For example, `highlight_grade(2)(A)` is valid when `A` has no bivector terms,
including in an algebra whose dimension is less than two. The same applies
when selected terms are zero, suppressed by display tolerance, or absent
from the selected content mode. A set selector annotates its visible matches;
absent members do not prevent the others from rendering. Strict missing-target
checking requires at least one visible match, not every member of a set.

Simplification may also remove selected content. The source-to-render mapping
must record its disappearance rather than redirect the annotation to a
surviving or replacement term. An empty mapping simply follows the same
missing-target policy. Annotations do not force eliminated content to appear.

Empty selections are distinct from invalid requests: malformed selectors
(such as a negative grade), incompatible blade algebras, invalid matrix
regions, and expression selectors without required provenance still raise
useful errors. Unsupported rendering of a nonempty selection is also not an
empty match and must follow the renderer's explicit fallback/error policy.

An implicit coefficient or sign is not silently inserted by annotation.
Presentation must explicitly expose it to receive a decoration; otherwise
the default is to skip it under the same missing-target policy.
Non-contiguous selections do not include intervening unselected terms; the
renderer must use separate anchors or report an unsupported grouping.

Highlighting odd-grade terms of an involution result is a static grade rule.
Highlighting only signs that changed requires explicit reference/result
comparison. A comparison-rule API is deferred; no numeric inference is
implied by `sign(...)`.

#### One-off shorthand and view lifetime

`annotate(value, *rules)` is exactly the one-off spelling of
`annotator(*rules)(value)`. Whole-value keyword conveniences create one rule:

```python
ga.annotate(A, label="rotor generator", marker="underbrace")
# Equivalent to:
ga.annotator(
    ga.on(ga.whole(), label="rotor generator", marker="underbrace"),
)(A)
```

The first implementation should use an immutable annotation wrapper or view:

```python
annotated = annotate(
    metric_inner_product(e1, e2),
    label="metric pairing",
    role="metric",
)
```

The wrapper delegates read-only value access and rendering metadata. It must
not become a new arithmetic type in the Galaga core.

Arithmetic on an annotated value requires an explicit propagation policy:

- annotations that can be mapped unambiguously to the new expression may be
  propagated;
- annotations whose target cannot be mapped must be dropped rather than
  silently attached to an incorrect node;
- an explicit `map_annotations(...)` operation may be provided for advanced
  propagation.

The first release provides rendering-only views, with no arithmetic methods.
Their `value` property exposes the original object for explicit computation.
Applying the same annotator to another result is explicit, not propagation.
Automatic arithmetic propagation is a separate, deferred feature.

### Integration with `Presenter`

Annotators parallel presenters but do not replace them: annotators attach
semantic rules; presenters choose notation, blade names, ordering, and
formatting. The intended composition is:

```python
lengyel = presets.presenters.lengyel()
highlight_bivectors = highlight_grade(2)

lengyel(highlight_bivectors(A))
```

This is a proposed integration contract, not a claim that the existing
`Presenter` already accepts annotation views. The adapter must retain both
the annotation plan and the presenter's captured settings. Semantic anchors
are resolved using those final settings, rather than attaching annotations
to previously rendered strings. Presenting an annotated view must not drop
its rules. An annotator may also wrap an already presented supported value,
preserving its captured settings.

No dedicated callable-composition operator is required initially. A Python
function can reuse both recipes. Matrix views use a matrix-specific adapter;
this does not broaden the existing multivector presenter contract implicitly.

The extension should integrate through the existing presenter abstraction:

```python
from galaga_annotation import AnnotationPresenter

presenter = AnnotationPresenter(
    base=presets.presenters.functional(),
)

presenter(annotated_value)
```

The ordinary Galaga `Presenter` must remain usable without installing the
extension. The adapter may consume a lightweight optional annotation protocol
or an annotation-aware view.

### Integration with `MatrixRepresentation`

Matrix annotations consume the provenance that `galaga_matrix` already owns
(ADR-082) rather than defining a parallel annotation-owned type:

- `MatrixRepr` carries the source algebra, representation mode, basis,
  coefficient domain and kind;
- `MatrixRepresentation` (in `galaga_matrix.expr`) records the immutable
  expression tree for tracked conversions;
- `MatrixRepresentationPlan` records the algebra-derived conversion data
  (descriptor, matrix shape, generators, coefficient indices and tolerances).

The annotation adapter reads these public objects to relate a matrix to its
source value and basis. It must not reimplement conversion or introduce a
competing provenance class.

There are two separate annotation classes:

1. **Expression annotations**, such as labelling the geometric product that
   produced the represented matrix.
2. **Matrix-region annotations**, such as labelling a chiral block, projector,
   basis row, basis column, or selected entry.

The matrix package must not infer mathematical meaning from arbitrary matrix
entries. It should render explicit annotations and use explicit conversion
provenance supplied by the representation plan.

### KaTeX rendering

The KaTeX backend performs four stages:

1. build semantic anchors from the Galaga render tree or matrix layout;
2. associate annotations with anchors;
3. solve approximate label placement;
4. lower the solution to supported KaTeX primitives.

The baseline lowering vocabulary is:

| Semantic primitive | KaTeX lowering |
|---|---|
| Text highlight | `\textcolor` |
| Filled highlight | `\colorbox` |
| Bordered highlight | `\fcolorbox` |
| Label above | `\overset` |
| Label below | `\underset` |
| Multi-line label | `\substack` |
| Directional relationship | `\uparrow`, `\downarrow` |
| Span grouping | `\underbrace`, `\underbracket`, `\overbrace`, `\overbracket`, `\overline`, `\overgroup`, underline |
| Cancellation | `\cancel`, `\bcancel`, `\xcancel` |
| Derivation transition | `aligned`, `cases`, extensible arrows |

For example:

```latex
\overset{
  {\color{seagreen}\substack{\text{metric pairing} \cr \downarrow}}
}{e_1 \bullet e_2}
```

`\colorbox` enters text mode in KaTeX. The backend re-enters math mode with
`$ ... $` inside the box, and annotated views hand the resulting math to
rich-display frontends as one inline block so Markdown `$` tokenizers cannot
split it.

### Layout solving

KaTeX reserves width for `\overset` and `\underset`, so annotations should
remain centred on their semantic anchors. The solver must not apply arbitrary
horizontal offsets that fight KaTeX's own spacing.

Browser geometry is the final alignment contract. Playwright loads Marimo's
actual KaTeX JavaScript and CSS in pinned headless Chromium and compares target,
marker and label bounding boxes. String snapshots and standalone KaTeX parsing
remain earlier, faster layers; screenshots are diagnostic unless generated in
one fixed browser/OS/font environment. See
[ADR-156](../adrs/156-headless-browser-geometry-contracts-for-katex.md).

The initial solver should:

1. estimate label width and height in em units;
2. detect collisions between neighbouring annotations on the same side;
3. assign shallow annotation tiers greedily;
4. alternate adjacent labels when possible;
5. cap depth and allow KaTeX to provide final spacing;
6. expose the placement result for debugging and tests.

Approximate metrics are layout hints, not a promise of pixel-perfect geometry.
The backend should provide a readable fallback when labels are too wide or the
renderer cannot place a target precisely.

### Safety and trust

The default plain-label path must emit trusted-free KaTeX. `label_latex` is an
explicit advanced mode whose contents are trusted as KaTeX source, never as
HTML; the complete equation must be HTML-escaped at any rich-display markup
boundary.

The following are not baseline requirements because they are unsupported or
trust-sensitive in Marimo's KaTeX environment:

- `\bbox`;
- `\cancelto`;
- `\mathtip`;
- `\cssId`;
- `\htmlClass`, `\htmlData`, `\htmlId`, and `\htmlStyle`.

Raw TeX, persistent macros, and HTML/CSS injection require an explicit advanced
mode and must not be accepted from ordinary annotation labels without escaping.

### Existing recognition annotations

`galaga_marimo` already supports `recognize=`. Recognition answers:

> Does this computed value numerically equal one of these known values?

This specification answers a different question:

> Which mathematical role or subexpression should be highlighted?

The two mechanisms remain separate. They may compose in a notebook, but
`galaga_annotation` must not duplicate recognition's numeric matching logic.

### Serialization

Annotation plans should be serializable when they use:

- expression paths;
- canonical operation IDs;
- plain labels and roles;
- simple styles;
- matrix slices or explicit index lists.

Arbitrary Python callbacks are not part of the portable annotation format.

### Initial scope

The first implementation milestone includes:

1. immutable `Annotation`, `AnnotationStyle`, target objects, and callable
   `Annotator` recipes with equivalent functional/fluent builders;
2. whole-expression and expression-path targets;
3. text, box, above-label, and below-label renderings;
4. KaTeX/Marimo output;
5. approximate collision avoidance;
6. presenter integration;
7. numerical transparency tests;
8. a pedagogical notebook annotating metric products, wedge products, and rotor
   sandwiches.

Matrix-region annotations, expression-to-matrix provenance, interactive
selection, and annotation propagation through arithmetic are later milestones.

### Non-goals

The first version does not provide:

- symbolic coefficients or symbolic metrics;
- automatic mathematical interpretation of arbitrary expressions;
- coefficient-by-coefficient annotation inference;
- arbitrary predicate selectors;
- an interactive equation editor;
- a general SVG geometry API;
- a dependency from Galaga core or facade to the extension.
