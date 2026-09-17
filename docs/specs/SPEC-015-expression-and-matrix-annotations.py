"""Static KaTeX gallery for SPEC-015 annotation capabilities."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Expression and matrix annotations

    This static gallery accompanies
    [SPEC-015](SPEC-015-expression-and-matrix-annotations.md).
    It deliberately contains no annotation implementation and no dynamic
    Galaga calculations. Each example is hand-authored KaTeX so that the
    notebook preserves the rendering fidelity that a MathJax-based Markdown
    editor cannot provide.

    Marimo renders mathematics with **KaTeX**. The examples therefore use
    `\overset`, `\underset`, `\substack`, `\textcolor`, `\colorbox`,
    `\fcolorbox`, braces, arrows, and `\cr` row separators.

    In this gallery, `\cr` is used inside `\substack` rather than `\\`, and
    each display equation stays on one physical source line. These details are
    important when the source passes through Marimo's Markdown renderer.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Label a complete expression

    A callout can explain the role of an entire expression without changing
    the expression or its active notation:

    $$\overset{\color{seagreen}\substack{\text{rotor sandwich} \cr \downarrow}}{R v \widetilde{R}}$$

    A result can carry a label below it instead:

    $$\underset{\color{royalblue}\substack{\uparrow \cr \text{evaluated vector}}}{v'}$$

    Above and below labels can coexist on one target:

    $$\overset{\color{seagreen}\substack{\text{expression} \cr \downarrow}}{\underset{\color{royalblue}\substack{\uparrow \cr \text{value}}}{R v \widetilde{R}}}$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Explain operands and subexpressions

    The labels belong to semantic spans, not to character offsets:

    $$\underset{\color{royalblue}\substack{\uparrow \cr \text{vector sum}}}{(e_1 + e_2)} \wedge \overset{\color{darkorange}\substack{\text{basis vector} \cr \downarrow}}{e_3}$$

    A longer expression can annotate several nested levels:

    $$\overset{\color{seagreen}\substack{\text{outer expression} \cr \downarrow}}{\underset{\color{royalblue}\substack{\uparrow \cr \text{left operand}}}{(e_1 + e_2)} \wedge \overset{\color{darkorange}\substack{\text{right operand} \cr \downarrow}}{e_3}}$$

    The same idea applies to a rotor sandwich:

    $$\overset{\color{seagreen}\substack{\text{rotated vector} \cr \downarrow}}{v'} = \overset{\color{royalblue}\substack{\uparrow \cr \text{rotor}}}{R}\,\overset{\color{darkorange}\substack{\text{input} \cr \text{vector} \cr \downarrow}}{v}\,\underset{\color{slateblue}\substack{\uparrow \cr \text{reverse rotor}}}{\widetilde{R}}$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Annotate an operation symbol

    The semantic target is the operation. The active Galaga notation decides
    whether that operation is shown as a function or as a geometric symbol.

    Functional presentation:

    $$\overset{\color{seagreen}\text{metric pairing}}{\operatorname{metric\_inner\_product}}(e_1, e_2)$$

    Geometric presentation:

    $$e_1 \mathbin{\overset{\color{seagreen}\text{metric pairing}}{\bullet}} e_2$$

    The annotation is attached to `metric_inner_product`, not to the literal
    characters `metric_inner_product` or `\bullet`. The same plan can therefore
    be rendered with a different `Notation` preset.

    Other useful operation callouts:

    $$e_1 \mathbin{\overset{\color{royalblue}\text{exterior product}}{\wedge}} e_2 \qquad R v \mathbin{\underset{\color{slateblue}\text{reverse on the right}}{\widetilde{R}}}$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Highlight terms and spans

    Text colour is the lightest emphasis:

    $$a + {\color{royalblue}(e_1 \wedge e_2)} + b$$

    A filled box gives a stronger highlight. KaTeX's `\colorbox` enters text
    mode, so the mathematical content re-enters math mode with `$...$`:

    $$a + \colorbox{#e8f5e9}{$\color{black}e_1 \wedge e_2$} + b$$

    A bordered box distinguishes a matrix or teaching focus:

    $$\fcolorbox{seagreen}{#e8f5e9}{$\color{black}e_1 \wedge e_2$}$$

    Highlighting can combine with a label:

    $$\overset{\color{seagreen}\substack{\text{simple bivector} \cr \downarrow}}{\fcolorbox{seagreen}{#e8f5e9}{$\color{black}e_{12}$}}$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Group terms with braces and spans

    Braces communicate that an annotation covers a complete range:

    $$\underbrace{(e_1 + e_2)}_{\text{vector sum}} \wedge e_3$$

    $$\overbrace{e_1 \wedge e_2}^{\text{simple bivector}} + e_3$$

    A multi-line label remains centred on the span:

    $$\underbrace{e_1 \wedge e_2}_{\substack{\text{grade two} \cr \text{simple blade}}}$$

    Nested spans are possible, although the layout solver should keep labels
    short in dense expressions:

    $$\underbrace{e_1 + \underbrace{e_2 + e_3}_{\text{inner sum}}}_{\text{outer vector expression}}$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Annotate multivector terms, coefficients, and grades

    A multivector term is a semantic display item even when it is not a
    separate expression node:

    $$0.5 + \color{darkorange}{2e_1} - \underbrace{3e_{12}}_{\text{bivector part}}$$

    A grade-wide annotation can cover all vector terms:

    $$\overset{\color{darkorange}\text{grade one}}{2e_1} + 3e_{12} + \overset{\color{darkorange}\text{grade one}}{e_3}$$

    The semantic blade identity must remain stable even when a presenter
    changes display order, blade names, compactness, or wedge style.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Explain cancellation and simplification

    An explicit cancellation annotation can teach why a result vanishes:

    $$\cancel{e_1 \wedge e_1}$$

    A labelled equality is often clearer for a lesson:

    $$e_1 \wedge e_1 \overset{\color{indianred}\text{alternating product}}{=} 0$$

    The annotation system should not infer a pedagogical explanation merely
    because a computed coefficient is zero. A helper may provide a reason, but
    the reason remains explicit metadata supplied by the user or a trusted
    higher-level derivation tool.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7a. Colour a multivector by grade

    A multivector can use one stable colour for each grade. The colour belongs
    to the semantic grade component, not to the term's position in the string:

    $$A = \textcolor{#111827}{0.5} + \textcolor{#0072B2}{(1.2e_1-0.4e_2)} + \textcolor{#D55E00}{(0.7e_{12}+0.2e_{23})} + \textcolor{#009E73}{0.9e_{123}} + \textcolor{purple}{0.3e_{1234}}$$

    The same palette can explain the grade projections:

    $$\langle A\rangle_0 = \textcolor{#111827}{0.5} \qquad \langle A\rangle_1 = \textcolor{#0072B2}{1.2e_1-0.4e_2} \qquad \langle A\rangle_2 = \textcolor{#D55E00}{0.7e_{12}+0.2e_{23}}$$

    A labelled decomposition makes the legend explicit for a lesson:

    $$A = \underbrace{\textcolor{#111827}{A_0}}_{\text{scalar}} + \underbrace{\textcolor{#0072B2}{A_1}}_{\text{vector}} + \underbrace{\textcolor{#D55E00}{A_2}}_{\text{bivector}} + \underbrace{\textcolor{#009E73}{A_3}}_{\text{trivector}} + \underbrace{\textcolor{purple}{A_4}}_{\text{4-vector}}$$

    Grade colouring remains meaningful when the presenter changes blade names,
    display order, compactness, or the algebra's basis convention.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7a.1. Colour semantic parts of a multivector

    Colour does not have to mean grade. In this example every term is a
    trivector, but the terms are grouped by geometric role: the green part is
    the cocarrier direction/carrier plane contribution, while the purple part
    is the cocarrier moment/flat-line contribution.

    $$c = \overset{\mathclap{\substack{\textcolor{#0099cc}{\text{Cocarrier Direction}} \cr \rule{5em}{0.4pt} \cr \rule{0.4pt}{0.7em}}}}{\colorbox{#b8e6bf}{$\displaystyle c_{gx}e_{423}+c_{gy}e_{431}+c_{gz}e_{412}+c_{gw}e_{321}$}} + \overset{\mathclap{\substack{\textcolor{#0099cc}{\text{Cocarrier Moment}} \cr \rule{5em}{0.4pt} \cr \rule{0.4pt}{0.7em}}}}{\colorbox{#d8c4ee}{$\displaystyle c_{vx}e_{415}+c_{vy}e_{425}+c_{vz}e_{435}+c_{mx}e_{235}+c_{my}e_{315}+c_{mz}e_{125}$}}$$

    The same two semantic spans can be labelled below, with the condition for
    the flat-line special case made explicit:

    $$c = \underset{\textcolor{seagreen}{\text{Carrier Plane}}}{\colorbox{#b8e6bf}{$\displaystyle c_{gx}e_{423}+c_{gy}e_{431}+c_{gz}e_{412}+c_{gw}e_{321}$}} + \underset{\substack{\textcolor{slateblue}{\text{Flat Line}} \cr \textcolor{slateblue}{\text{when }c_{gx}=c_{gy}=c_{gz}=c_{gw}=0}}}{\colorbox{#d8c4ee}{$\displaystyle c_{vx}e_{415}+c_{vy}e_{425}+c_{vz}e_{435}+c_{mx}e_{235}+c_{my}e_{315}+c_{mz}e_{125}$}}$$

    This is a useful distinction for the annotation API: a multivector term
    can have a `grade` colour, a domain-specific `role` colour, or both. The
    semantic span should remain stable if the presenter changes blade order or
    notation.

    The same role-based convention applies to a vector in a conformal-style
    basis. The first four components form the carrier point, while the final
    component is the infinity direction:

    $$a = \underset{\textcolor{seagreen}{\text{Carrier Point}}}{\colorbox{#b8e6bf}{$\displaystyle a_xe_1+a_ye_2+a_ze_3+a_we_4$}} + \underset{\substack{\textcolor{slateblue}{\text{Infinity}} \cr \textcolor{slateblue}{\text{when }a_x=a_y=a_z=a_w=0}}}{\colorbox{#d8c4ee}{$\displaystyle a_ue_5$}}$$

    Unlike grade colouring, this annotation remains meaningful even when the
    highlighted components are not a complete grade projection: it names the
    geometric interpretation of each semantic span.

    A two-part even multivector can use the same visual language. The purple
    span is the rotation quaternion, while the green span carries moment and
    displacement data:

    $$Q = \underset{\mathclap{\substack{\rule{0.4pt}{0.7em} \cr \textcolor{slateblue}{\text{Rotation}}}}}{\colorbox{#d8c4ee}{$\displaystyle Q_{xv}e_{41}+Q_{yv}e_{42}+Q_{zv}e_{43}+Q_{wv}$}} + \underset{\mathclap{\substack{\rule{0.4pt}{0.7em} \cr \textcolor{seagreen}{\text{Moment and Displacement}}}}}{\colorbox{#b8e6bf}{$\displaystyle Q_{mx}e_{23}+Q_{my}e_{31}+Q_{mz}e_{12}+Q_{mw}e_{1234}$}}$$

    The exact basis names depend on the algebra and presentation, but the
    annotation targets are stable semantic spans such as `rotation` and
    `moment_displacement`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7a.2. Nested spans: carrier highlights and cocarrier brackets

    The reference diagram combines two levels of annotation. The green
    highlight covers all six **Carrier Line** terms, but **Cocarrier Normal**
    brackets only the first three terms, with coefficients $d_{vx}$,
    $d_{vy}$, and $d_{vz}$. The purple highlight covers all four **Flat Point**
    terms, while **Cocarrier Position** brackets only $d_{pw}e_{45}$.

    These labels and ordered blade names reproduce the supplied diagram's
    convention; they do not define a new Galaga basis convention. All ten
    displayed terms are bivectors, so these colours distinguish geometric
    roles within one grade.

    $$\vphantom{\overbracket{\vphantom{\raisebox{5px}{$\displaystyle d_{vx}e_{41}$}}d_{vx}e_{41}}^{\text{Cocarrier Normal}}}\mathbf{d} = \underset{\substack{\textcolor{seagreen}{\rule{0.6pt}{0.8em}} \cr \textcolor{seagreen}{\text{Carrier Line}}}}{\colorbox{#b8e6bf}{$\displaystyle\vphantom{d_{vx}e_{41}}\smash[t]{\textcolor{#0099cc}{\overbracket{\vphantom{\raisebox{5px}{$\displaystyle d_{vx}e_{41}$}}\textcolor{black}{d_{vx}e_{41}+d_{vy}e_{42}+d_{vz}e_{43}}}^{\text{Cocarrier Normal}}}}+d_{mx}e_{23}+d_{my}e_{31}+d_{mz}e_{12}$}} + \underset{\substack{\textcolor{slateblue}{\rule{0.6pt}{0.8em}} \cr \textcolor{slateblue}{\text{Flat Point}} \cr \textcolor{slateblue}{\text{when }d_{vx}=d_{vy}=d_{vz}=d_{mx}=d_{my}=d_{mz}=0}}}{\colorbox{#d8c4ee}{$\displaystyle\vphantom{d_{vx}e_{41}}d_{px}e_{15}+d_{py}e_{25}+d_{pz}e_{35}+\smash[t]{\textcolor{#0099cc}{\overbracket{\vphantom{\raisebox{5px}{$\displaystyle d_{vx}e_{41}$}}\textcolor{black}{d_{pw}e_{45}}}^{\mathclap{\text{Cocarrier Position}}}}}$}}$$

    The highlights stay behind the equation; the cyan brackets and their
    labels sit above them. Here `\smash[t]` removes the bracket's extra height
    from the filled box, a `\vphantom` inside each box preserves the terms'
    height, and the outer `\vphantom` reserves room above the equation. The
    labels below use plain `\rule` leaders. Inside each overbracket,
    `\vphantom{\raisebox{5px}{$...$}}` adds about 5 px of clearance
    above the terms, lifting the bracket and its label without moving the
    visible coefficients, blades, or highlight.

    For a semantic API, the two highlights select complete term sets. The
    brackets select subsets of those same sets, so both annotations must be
    allowed to attach to a term at once:

    | Annotation | Selected terms | Rendering |
    |---|---|---|
    | Carrier Line | $e_{41},e_{42},e_{43},e_{23},e_{31},e_{12}$ terms | Green fill, label below |
    | Cocarrier Normal | $e_{41},e_{42},e_{43}$ terms | Cyan overbracket, label above |
    | Flat Point | $e_{15},e_{25},e_{35},e_{45}$ terms | Purple fill, label and condition below |
    | Cocarrier Position | $e_{45}$ term | Cyan overbracket, label above |

    The screenshot brackets the **coefficient-plus-blade terms**. If a lesson
    needs to mark only the coefficients, those are distinct targets. For
    example, the same final term can show a bracket over $d_{pw}$ alone:

    $$\vphantom{\overbracket{\vphantom{\raisebox{5px}{$\displaystyle d_{pw}$}}d_{pw}}^{\text{Cocarrier Position}}}\colorbox{#d8c4ee}{$\displaystyle\vphantom{d_{pw}e_{45}}\smash[t]{\textcolor{#0099cc}{\overbracket{\vphantom{\raisebox{5px}{$\displaystyle d_{pw}$}}\textcolor{black}{d_{pw}}}^{\mathclap{\text{Cocarrier Position}}}}}e_{45}$}$$

    That corresponds to `MultivectorCoefficient(blade=e45)` nested inside a
    `MultivectorTerm(blade=e45)` highlight. It differs from putting an
    overbracket on the whole term, as in the main diagram.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7b. Which grades flip under each involution?

    For a homogeneous grade-$r$ component, the three standard signs are:

    $$\widehat{A_r}=(-1)^rA_r \qquad \widetilde{A_r}=(-1)^{r(r-1)/2}A_r \qquad \overline{A_r}=(-1)^{r(r+1)/2}A_r$$

    Here `\widehat{\phantom{A}}` is the grade involution, `\widetilde{\phantom{A}}`
    is the reverse, and the overline denotes Clifford conjugation. The first
    few grades make the different patterns visible:

    $$\begin{array}{c|ccccc}r & 0 & 1 & 2 & 3 & 4 \\ \hline \text{grade involution }\widehat{\phantom{A}} & + & - & + & - & + \\ \text{reverse }\widetilde{\phantom{A}} & + & + & - & - & + \\ \text{Clifford conjugation }\overline{\phantom{A}} & + & - & - & + & +\end{array}$$

    Equivalently: grade involution flips odd grades; reverse flips grades
    congruent to 2 or 3 modulo 4; Clifford conjugation flips grades congruent
    to 1 or 2 modulo 4.

    Apply these involutions to the explicit multivector from the grade-colour
    example. Yellow (`#fff3cd`) highlights each grade component whose sign
    flips, including its new coefficient signs. Underbraces identify grades
    0 through 4 in every display:

    $$A = \textcolor{#888888}{\underbrace{\textcolor{black}{0.5}}_{\text{grade 0}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{1.2 e_{1} - 0.4 e_{2}}}_{\text{grade 1}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{0.7 e_{12} + 0.2 e_{23}}}_{\text{grade 2}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{0.9 e_{123}}}_{\text{grade 3}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{0.3 e_{1234}}}_{\text{grade 4}}}$$

    **Grade involution:** the vector and trivector components flip.

    $$\widehat{A} = \textcolor{#888888}{\underbrace{\textcolor{black}{0.5}}_{\text{grade 0}}} \;\textcolor{#888888}{\underbrace{\textcolor{black}{\colorbox{#fff3cd}{$-1.2 e_{1} + 0.4 e_{2}$}}}_{\text{grade 1}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{0.7 e_{12} + 0.2 e_{23}}}_{\text{grade 2}}} \;\textcolor{#888888}{\underbrace{\textcolor{black}{\colorbox{#fff3cd}{$-0.9 e_{123}$}}}_{\text{grade 3}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{0.3 e_{1234}}}_{\text{grade 4}}}$$

    **Reverse:** the bivector and trivector components flip.

    $$\widetilde{A} = \textcolor{#888888}{\underbrace{\textcolor{black}{0.5}}_{\text{grade 0}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{1.2 e_{1} - 0.4 e_{2}}}_{\text{grade 1}}} \;\textcolor{#888888}{\underbrace{\textcolor{black}{\colorbox{#fff3cd}{$-0.7 e_{12} - 0.2 e_{23}$}}}_{\text{grade 2}}} \;\textcolor{#888888}{\underbrace{\textcolor{black}{\colorbox{#fff3cd}{$-0.9 e_{123}$}}}_{\text{grade 3}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{0.3 e_{1234}}}_{\text{grade 4}}}$$

    **Clifford conjugation:** the vector and bivector components flip.

    $$\overline{A} = \textcolor{#888888}{\underbrace{\textcolor{black}{0.5}}_{\text{grade 0}}} \;\textcolor{#888888}{\underbrace{\textcolor{black}{\colorbox{#fff3cd}{$-1.2 e_{1} + 0.4 e_{2}$}}}_{\text{grade 1}}} \;\textcolor{#888888}{\underbrace{\textcolor{black}{\colorbox{#fff3cd}{$-0.7 e_{12} - 0.2 e_{23}$}}}_{\text{grade 2}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{0.9 e_{123}}}_{\text{grade 3}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{0.3 e_{1234}}}_{\text{grade 4}}}$$

    Flipping a grade negates every coefficient in that component. In
    particular, the original $-0.4 e_2$ becomes $+0.4 e_2$ under grade
    involution and Clifford conjugation. The scalar and grade-four terms
    remain unchanged in all three examples.

    **Grade involution, highlighting only the changed signs.** This second
    view uses the same result and grade underbraces, but puts yellow behind
    just the three signs that changed. Coefficient magnitudes and basis blades
    remain unhighlighted:

    $$\widehat{A} = \textcolor{#888888}{\underbrace{\textcolor{black}{0.5}}_{\text{grade 0}}} \;\textcolor{#888888}{\underbrace{\textcolor{black}{\colorbox{#fff3cd}{$-$}\,1.2 e_{1} \mathbin{\colorbox{#fff3cd}{$+$}} 0.4 e_{2}}}_{\text{grade 1}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{0.7 e_{12} + 0.2 e_{23}}}_{\text{grade 2}}} \;\textcolor{#888888}{\underbrace{\textcolor{black}{\colorbox{#fff3cd}{$-$}\,0.9 e_{123}}}_{\text{grade 3}}} + \textcolor{#888888}{\underbrace{\textcolor{black}{0.3 e_{1234}}}_{\text{grade 4}}}$$

    Relative to $A$, the $e_1$ and $e_{123}$ signs change from $+$ to $-$,
    while the $e_2$ sign changes from $-$ to $+$. This motivates selecting
    a displayed term's sign separately from its coefficient magnitude or
    its blade.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Derivation and transition layouts

    A derivation is a sequence of expressions rather than one expression tree:

    $$R v \widetilde{R} \xrightarrow{\text{rotor action}} v' \xrightarrow{\text{vector projection}} \langle v' \rangle_1$$

    A matrix conversion can be shown as a transition too:

    $$\text{GA expression} \xrightarrow{\text{Dirac basis conversion}} \text{matrix representation}$$

    A derivation renderer may use `aligned`, `cases`, or extensible arrows, but
    it should share annotation labels, colours, and semantic roles with the
    ordinary expression renderer.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Matrix rows, columns, entries, and blocks

    Matrix annotations can identify a complete block:

    $$\left(\begin{array}{cc|cc}\colorbox{#e8f5e9}{$1$} & \colorbox{#e8f5e9}{$0$} & 0 & 0 \\ 0 & 1 & 0 & 0 \\ \hline 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1\end{array}\right)\quad\overset{\color{seagreen}\text{left-chiral block}}{\longrightarrow}$$

    Individual rows and columns can carry labels:

    $$\overset{\color{royalblue}\text{image of }e_1}{\left(\begin{array}{cccc}1 & 0 & 0 & 0\end{array}\right)}$$

    An entry-level annotation can explain a mixing term:

    $$\left(\begin{array}{cc}1 & \overset{\color{indianred}\text{mixing}}{0.5i} \\ 0 & 1\end{array}\right)$$

    The matrix adapter must validate row, column, and block targets against the
    actual representation shape.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9a. Colour individual matrix cells and rectangular ranges

    A light text colour can mark one entry without changing the matrix's
    spacing. This is useful for pointing at a single coefficient or sign:

    $$M = \left(\begin{array}{cccc}1 & \textcolor{royalblue}{0} & 0 & 0 \cr 0 & 1 & 0 & \textcolor{indianred}{0} \cr 0 & 0 & 1 & 0 \cr 0 & 0 & 0 & 1\end{array}\right)$$

    A filled cell is stronger and remains visible when the selected value is
    zero. Individual cells can use the same semantic highlight style as
    expression terms:

    $$\left(\begin{array}{cccc}1 & \colorbox{#e8f5e9}{$0$} & 0 & 0 \cr 0 & 1 & 0 & 0 \cr 0 & 0 & \fcolorbox{seagreen}{#e8f5e9}{$1$} & 0 \cr 0 & 0 & 0 & 1\end{array}\right)$$

    A rectangular selection can be highlighted cell-by-cell. Here the
    displayed mathematical range is rows 2--4 and columns 2--4:

    $$\left(\begin{array}{cccc}a_{11} & a_{12} & a_{13} & a_{14} \cr a_{21} & \colorbox{#e8f5e9}{$a_{22}$} & \colorbox{#e8f5e9}{$a_{23}$} & \colorbox{#e8f5e9}{$a_{24}$} \cr a_{31} & \colorbox{#e8f5e9}{$a_{32}$} & \colorbox{#e8f5e9}{$a_{33}$} & \colorbox{#e8f5e9}{$a_{34}$} \cr a_{41} & \colorbox{#e8f5e9}{$a_{42}$} & \colorbox{#e8f5e9}{$a_{43}$} & \colorbox{#e8f5e9}{$a_{44}$}\end{array}\right)$$

    The same range may be rendered as one filled block when the renderer can
    preserve the cell grid inside the highlight:

    $$M[2\!:\!4,2\!:\!4] = \colorbox{#e8f5e9}{$\begin{matrix}a_{22} & a_{23} & a_{24} \cr a_{32} & a_{33} & a_{34} \cr a_{42} & a_{43} & a_{44}\end{matrix}$}$$

    Keep the entire 4-by-4 matrix visible, but give its bottom-right region
    one continuous background. Here four nested arrays represent the four
    partitions; only the lower-right array is boxed:

    $$\left(\begin{array}{cc}a_{11} & \begin{array}{ccc}a_{12} & a_{13} & a_{14}\end{array} \cr \begin{array}{c}a_{21} \cr a_{31} \cr a_{41}\end{array} & \colorbox{#e8f5e9}{$\displaystyle\begin{array}{ccc}a_{22} & a_{23} & a_{24} \cr a_{32} & a_{33} & a_{34} \cr a_{42} & a_{43} & a_{44}\end{array}$}\end{array}\right)$$

    This is a pure-KaTeX block-layout mockup, not a general cell-grid
    renderer. Nested arrays size their columns independently, and the box
    introduces padding. Similar-sized symbolic entries work well here;
    unequal-width entries need shared sizing to preserve alignment. A rich
    HTML/CSS matrix renderer should instead keep a single grid and paint
    one background region behind the selected cells and their gaps.

    A border gives the range a clear extent without tinting every value:

    $$M[2\!:\!4,2\!:\!4] = \fcolorbox{seagreen}{white}{$\begin{matrix}a_{22} & a_{23} & a_{24} \cr a_{32} & a_{33} & a_{34} \cr a_{42} & a_{43} & a_{44}\end{matrix}$}$$

    `\fcolorbox` can also sit inside a larger matrix when the selected region
    is represented as a block. The inner matrix is one outer-array entry, so
    this is best for block-partitioned matrices rather than arbitrary cell
    overlays:

    $$\left(\begin{array}{c|c}A_{11} & A_{12} \cr \hline A_{21} & \fcolorbox{seagreen}{#e8f5e9}{$\begin{matrix}a_{22} & a_{23} \cr a_{32} & a_{33}\end{matrix}$}\end{array}\right)$$

    For a true cell-preserving overlay, apply `\fcolorbox` to each selected
    cell instead. That keeps every entry in the original matrix grid:

    $$\left(\begin{array}{cccc}a_{11} & a_{12} & a_{13} & a_{14} \cr a_{21} & \fcolorbox{seagreen}{#e8f5e9}{$a_{22}$} & \fcolorbox{seagreen}{#e8f5e9}{$a_{23}$} & a_{24} \cr a_{31} & \fcolorbox{seagreen}{#e8f5e9}{$a_{32}$} & \fcolorbox{seagreen}{#e8f5e9}{$a_{33}$} & a_{34} \cr a_{41} & a_{42} & a_{43} & a_{44}\end{array}\right)$$

    In a Python-facing API, the displayed 1-based range 2--4 is commonly
    represented by the half-open 0-based slice `rows=slice(1, 4)` and
    `columns=slice(1, 4)`. The annotation should retain that semantic region;
    the renderer decides whether to use fills, borders, or per-cell colours.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9a.1. A shared grid with a continuous block background

    Unlike the nested-array fallback, this HTML/CSS mockup uses one grid
    for all sixteen entries. The background spans rows 2–4 and columns 2–4
    without affecting entry sizes or spacing. The parentheses are CSS curves
    outside the grid, not oversized text characters.

    <div role="group" aria-label="Four by four matrix, with rows two through four and columns two through four highlighted" style="display: inline-block; position: relative; padding: 0.3em 1em; margin: 1em 0;">
      <span aria-hidden="true" style="position: absolute; top: 0; bottom: 0; left: 0; width: 0.65em; border-left: 1px solid currentColor; border-radius: 50% 0 0 50%;"></span>
      <span aria-hidden="true" style="position: absolute; top: 0; bottom: 0; right: 0; width: 0.65em; border-right: 1px solid currentColor; border-radius: 0 50% 50% 0;"></span>
      <div style="display: grid; grid-template-columns: repeat(4, max-content); grid-template-rows: repeat(4, auto); gap: 0; isolation: isolate;">
        <div aria-hidden="true" style="grid-row: 2 / 5; grid-column: 2 / 5; background: #e8f5e9; z-index: -1;"></div>
      <span style="grid-row: 1; grid-column: 1; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>11</sub></span>
      <span style="grid-row: 1; grid-column: 2; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>12</sub></span>
      <span style="grid-row: 1; grid-column: 3; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>13</sub></span>
      <span style="grid-row: 1; grid-column: 4; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>14</sub></span>
      <span style="grid-row: 2; grid-column: 1; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>21</sub></span>
      <span style="grid-row: 2; grid-column: 2; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>22</sub></span>
      <span style="grid-row: 2; grid-column: 3; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>23</sub></span>
      <span style="grid-row: 2; grid-column: 4; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>24</sub></span>
      <span style="grid-row: 3; grid-column: 1; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>31</sub></span>
      <span style="grid-row: 3; grid-column: 2; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>32</sub></span>
      <span style="grid-row: 3; grid-column: 3; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>33</sub></span>
      <span style="grid-row: 3; grid-column: 4; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>34</sub></span>
      <span style="grid-row: 4; grid-column: 1; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>41</sub></span>
      <span style="grid-row: 4; grid-column: 2; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>42</sub></span>
      <span style="grid-row: 4; grid-column: 3; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>43</sub></span>
      <span style="grid-row: 4; grid-column: 4; position: relative; padding: 0.35em 0.65em; text-align: center;"><i>a</i><sub>44</sub></span>
      </div>
    </div>

    This is intended rich notebook output, not portable LaTeX. Entries still
    use HTML italics and subscripts in this static mockup, since Markdown
    math inside raw HTML is not processed by mo.md. A production renderer
    would supply rendered math entries within the same grid.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9b. Matrix rows, columns, blocks, and callouts

    A complete row or column can be emphasized with a consistent colour:

    $$\left(\begin{array}{c|cccc} & c_1 & c_2 & c_3 & c_4 \cr r_1 & 1 & 0 & 0 & 0 \cr r_2 & \textcolor{royalblue}{0} & \textcolor{royalblue}{1} & \textcolor{royalblue}{0} & \textcolor{royalblue}{0} \cr r_3 & 0 & 0 & 1 & 0 \cr r_4 & 0 & 0 & 0 & 1\end{array}\right)$$

    A filled row is more forceful, and a column may use a different colour so
    the two selections can be compared:

    $$\left(\begin{array}{cccc}\colorbox{#fff3cd}{$1$} & 0 & 0 & 0 \cr \colorbox{#fff3cd}{$0$} & \colorbox{#e7f0ff}{$1$} & \colorbox{#fff3cd}{$0$} & \colorbox{#fff3cd}{$0$} \cr \colorbox{#fff3cd}{$0$} & 0 & 1 & 0 \cr \colorbox{#fff3cd}{$0$} & 0 & 0 & 1\end{array}\right)$$

    A block can be labelled above the matrix while its extent is shown by a
    border. This is useful for chiral, grade, or domain decompositions:

    $$\overset{\color{seagreen}\text{left-chiral block}}{\fcolorbox{seagreen}{#e8f5e9}{$\begin{matrix}A_{11} & A_{12} \cr A_{21} & A_{22}\end{matrix}$}} \qquad \overset{\color{royalblue}\text{right-chiral block}}{\fcolorbox{royalblue}{#e7f0ff}{$\begin{matrix}B_{11} & B_{12} \cr B_{21} & B_{22}\end{matrix}$}}$$

    Entry callouts can explain a special coefficient without obscuring the
    rest of the representation:

    $$\left(\begin{array}{cc}1 & \overset{\color{indianred}\text{mixing}}{0.5i} \cr 0 & 1\end{array}\right)$$

    Matrix annotations can also describe a representation transition rather
    than a cell selection:

    $$A \xmapsto[\text{basis }\mathcal{B}]{\rho} \colorbox{#e7f0ff}{$[A]_{\rho,\mathcal{B}}$} \xrightarrow{\text{evaluate}} M_A$$

    These examples motivate separate semantic targets for `MatrixCell`,
    `MatrixRow`, `MatrixColumn`, `MatrixRegion`, and `MatrixBlock`; a renderer
    should not infer a rectangular region from a collection of character
    offsets.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9b.1. Highlighting a geometric-product table

    A product table can highlight a semantic subset of cells rather than
    colouring an entire row or column. In this excerpt, green cells mark
    products whose displayed value agrees with the corresponding outer-product
    result; the legend makes the selection rule explicit:

    $$\text{Geometric Product}\quad ab \qquad \colorbox{#b8e6bf}{$ab=a\wedge b$}$$

    $$\renewcommand{\arraystretch}{1.25}\begin{array}{c|ccccc}ab & 1 & e_1 & e_2 & e_3 & e_4 \\ \hline 1 & \colorbox{#b8e6bf}{$1$} & \colorbox{#b8e6bf}{$e_1$} & \colorbox{#b8e6bf}{$e_2$} & \colorbox{#b8e6bf}{$e_3$} & \colorbox{#b8e6bf}{$e_4$} \\ e_1 & \colorbox{#b8e6bf}{$e_1$} & 1 & \colorbox{#b8e6bf}{$e_{12}$} & \colorbox{#b8e6bf}{$-e_{31}$} & \colorbox{#b8e6bf}{$-e_{41}$} \\ e_2 & \colorbox{#b8e6bf}{$e_2$} & \colorbox{#b8e6bf}{$-e_{12}$} & 1 & \colorbox{#b8e6bf}{$e_{23}$} & \colorbox{#b8e6bf}{$-e_{42}$} \\ e_3 & \colorbox{#b8e6bf}{$e_3$} & \colorbox{#b8e6bf}{$e_{31}$} & \colorbox{#b8e6bf}{$-e_{23}$} & 1 & \colorbox{#b8e6bf}{$-e_{43}$} \\ e_4 & \colorbox{#b8e6bf}{$e_4$} & \colorbox{#b8e6bf}{$e_{41}$} & \colorbox{#b8e6bf}{$e_{42}$} & \colorbox{#b8e6bf}{$e_{43}$} & 0\end{array}$$

    In a complete table the same idea can highlight all qualifying cells,
    mark the diagonal separately, or show a rectangular subtable. The
    annotation target is a set of matrix coordinates plus a semantic rule;
    the renderer may choose per-cell fills, a border around a contiguous
    region, or both.

    A `\colorbox` can act as a cell-sized background when it wraps the cell's
    mathematical content. Small horizontal and vertical padding makes the
    result read more like a filled table cell:

    $$\renewcommand{\arraystretch}{1.4}\begin{array}{c|ccc} & e_1 & e_2 & e_3 \\ \hline e_1 & 1 & \colorbox{#b8e6bf}{$\displaystyle\mkern3mu e_{12}\mkern3mu$} & \colorbox{#b8e6bf}{$\displaystyle\mkern3mu e_{13}\mkern3mu$} \\ e_2 & \colorbox{#b8e6bf}{$\displaystyle\mkern3mu -e_{12}\mkern3mu$} & 1 & e_{23} \\ e_3 & \colorbox{#b8e6bf}{$\displaystyle\mkern3mu -e_{13}\mkern3mu$} & -e_{23} & 1\end{array}$$

    This is still a content-sized box: the surrounding `array` inter-column
    spacing is not painted. A true rectangular cell background requires a
    renderer with access to the matrix layout (for example HTML/CSS or SVG),
    or a future KaTeX feature such as `\cellcolor`; `\cellcolor` is not in
    KaTeX's current supported-command table. The semantic API should therefore
    distinguish `content_highlight` from `cell_fill`, allowing the KaTeX
    renderer to use the portable approximation and a richer renderer to fill
    the actual cell rectangle.

    A Markdown cell can also contain an HTML table. Here the background belongs
    to the actual HTML `<td>` elements, so the whole cell rectangle is filled:

    <table style="border-collapse: collapse; margin: 1em 0;">
      <thead>
        <tr>
          <th style="border: 1px solid #666; padding: 0.35em 0.7em;">$ab$</th>
          <th style="border: 1px solid #666; padding: 0.35em 0.7em;">$e_1$</th>
          <th style="border: 1px solid #666; padding: 0.35em 0.7em;">$e_2$</th>
          <th style="border: 1px solid #666; padding: 0.35em 0.7em;">$e_3$</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th style="border: 1px solid #666; padding: 0.35em 0.7em;">$e_1$</th>
          <td style="border: 1px solid #666; padding: 0.35em 0.7em;">$1$</td>
          <td style="background-color: #b8e6bf; border: 1px solid #666; padding: 0.35em 0.7em;">$e_{12}$</td>
          <td style="background-color: #b8e6bf; border: 1px solid #666; padding: 0.35em 0.7em;">$e_{13}$</td>
        </tr>
        <tr>
          <th style="border: 1px solid #666; padding: 0.35em 0.7em;">$e_2$</th>
          <td style="background-color: #b8e6bf; border: 1px solid #666; padding: 0.35em 0.7em;">$-e_{12}$</td>
          <td style="border: 1px solid #666; padding: 0.35em 0.7em;">$1$</td>
          <td style="background-color: #b8e6bf; border: 1px solid #666; padding: 0.35em 0.7em;">$e_{23}$</td>
        </tr>
        <tr>
          <th style="border: 1px solid #666; padding: 0.35em 0.7em;">$e_3$</th>
          <td style="background-color: #b8e6bf; border: 1px solid #666; padding: 0.35em 0.7em;">$-e_{13}$</td>
          <td style="background-color: #b8e6bf; border: 1px solid #666; padding: 0.35em 0.7em;">$-e_{23}$</td>
          <td style="border: 1px solid #666; padding: 0.35em 0.7em;">$1$</td>
        </tr>
      </tbody>
    </table>

    This HTML route is appropriate when a renderer can safely emit trusted
    presentation HTML. It is more visually precise than KaTeX alone, but less
    portable to Markdown editors that strip HTML or do not run math rendering
    inside table cells.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9c. Dense equation annotations from the rendering prototype

    A realistic teaching equation may need several annotation kinds at once:
    highlighted terms, labels above and below, and directional labels inside
    an argument list. The following uses only baseline KaTeX constructs:

    $$\overset{\mathclap{\color{seagreen}\begin{array}{c}\text{outgoing} \cr \text{radiance} \cr \downarrow\end{array}}}{\underset{\mathclap{\color{royalblue}\begin{array}{c}\uparrow \cr \text{surface point}\end{array}}}{\colorbox{#e8f5e9}{$L_o(\mathbf p,\omega_o)$}}} = \overset{\mathclap{\color{seagreen}\begin{array}{c}\text{emitted} \cr \text{radiance} \cr \downarrow\end{array}}}{\colorbox{#e8f5e9}{$L_e(\mathbf p,\omega_o)$}} + \int_{\mathcal H} \underset{\mathclap{\color{royalblue}\begin{array}{c}\uparrow \cr \text{BRDF}\end{array}}}{f_r}\bigl(\mathbf p,\omega_i,\omega_o\bigr) \overset{\mathclap{\color{seagreen}\begin{array}{c}\text{incoming} \cr \text{radiance} \cr \downarrow\end{array}}}{\colorbox{#e8f5e9}{$L_i(\mathbf p,\omega_i)$}}\,d\omega_i$$

    A reusable point-callout shape can be approximated with a local macro. A
    future annotation package may emit this pattern rather than exposing the
    raw TeX to callers:

    $${\def\annabove#1#2#3{\overset{\mathclap{\color{#1}\begin{array}{c}#2 \cr \downarrow\end{array}}}{#3}} \annabove{seagreen}{output}{y} = \annabove{royalblue}{model}{f(x)}}$$

    The prototype also explored rounded `\enclose` boxes and `\bbox` fills.
    Those require KaTeX extensions or trust configuration and are therefore
    recorded as optional renderer capabilities, not baseline SPEC-015 output:

    $$\underbrace{\colorbox{#fff3cd}{$x^2$} + y}_{\text{portable filled highlight}} \qquad \boxed{\textcolor{seagreen}{x^2+y}}$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9d. The wider prototype rendering vocabulary

    The prototype explored several ways to connect a label to a target. A
    short arrow, a plain leader, and a fixed-height delimiter all preserve the
    target's horizontal position:

    $$\overset{\substack{\textcolor{seagreen}{\text{slope}} \cr \downarrow}}{m}x + \underset{\substack{\uparrow \cr \textcolor{royalblue}{\text{intercept}}}}{b}$$

    $$\underset{\substack{\rule[0.2em]{0.4pt}{1.2em} \cr \textcolor{purple}{\text{constant}}}}{k} \qquad \underset{\substack{\biggm\vert \cr \textcolor{darkorange}{\text{selected}}}}{x_i}$$

    `\mathrlap` and `\mathllap` can hang a long label to one side. They are
    useful escape hatches, but should be renderer-owned because they can cause
    collisions when callers choose arbitrary offsets:

    $$\underset{\substack{\rule[0.2em]{0.4pt}{1em} \cr \mathrlap{\textcolor{royalblue}{\text{right-extending note}}}}}{x_1} + \underset{\substack{\rule[0.2em]{0.4pt}{1.5em} \cr \mathllap{\textcolor{seagreen}{\text{left-extending note}}}}}{x_2}$$

    A `\mathrlap` label can be shifted slightly left with a negative math kern
    while still contributing zero width to the surrounding layout:

    $$\underset{\substack{\rule[0.2em]{0.4pt}{1em} \cr \mathrlap{\mkern-3mu\textcolor{purple}{\text{slightly left}}}}}{x_3} \qquad \underset{\substack{\rule[0.2em]{0.4pt}{1em} \cr \mathrlap{\textcolor{darkorange}{\text{unshifted}}}}}{x_4}$$

    The offset should remain a renderer-level layout hint rather than part of
    the semantic annotation target. Small `\mkern` values are preferable to
    arbitrary `\hspace` offsets because they stay in math units.

    Annotation text can have an explicit visual hierarchy. KaTeX supports
    compact text sizes as well as script math styles:

    $$\overset{\substack{\Large\text{primary label} \cr \small\downarrow}}{A} \qquad \overset{\substack{\scriptsize\text{secondary label} \cr \scriptscriptstyle\downarrow}}{B} \qquad \underset{\substack{\uparrow \cr \tiny\text{tertiary note}}}{C}$$

    Size changes should be local to the label. The annotated expression keeps
    its normal presentation, and the annotation API can expose a small set of
    named sizes such as `normal`, `small`, `script`, and `tiny` rather than
    requiring callers to provide arbitrary TeX size commands.

    Extensible arrows describe transformations between complete forms:

    $$A B \xrightarrow[\text{collect grades}]{\text{expand geometric product}} \langle AB\rangle_0 + \langle AB\rangle_1 + \langle AB\rangle_2$$

    Brackets, underlines, and overlines provide span-level emphasis when a
    brace would imply the wrong relationship:

    $$\overbracket{a+b+c}^{\textcolor{seagreen}{\text{input block}}} \qquad \underbracket{d+e}_{\textcolor{royalblue}{\text{output block}}} \qquad \underline{\textcolor{purple}{A_1+A_2}}$$

    Derivations can carry colours through aligned rows, and cases can expose
    the condition behind a selected result:

    $$\begin{aligned}A &= \textcolor{royalblue}{A_0}+A_1+A_2 \cr \langle A\rangle_0 &= \left\langle\textcolor{royalblue}{A_0}+A_1+A_2\right\rangle_0 \cr &= \textcolor{royalblue}{A_0}\end{aligned} \qquad e_i^2 = \begin{cases}+1 & \text{if }g_{ii}>0 \cr -1 & \text{if }g_{ii}<0 \cr 0 & \text{if }g_{ii}=0\end{cases}$$

    Equation tags and operator annotations keep explanations attached to the
    relation or operation rather than to an operand:

    $$AB = A\mathbin{\cdot}B + A\mathbin{\wedge}B \tag{grade split}$$

    $$A\mathbin{\underset{\textcolor{royalblue}{\text{outer product}}}{\wedge}}B \qquad C \overset{\textcolor{purple}{\mathrm{def}}}{:=} AB$$

    A future implementation may use local macros for consistent styles, but
    should expand them or scope them to one expression:

    $${\def\markred#1{\textcolor{indianred}{#1}} \mathbf{x}=(x_1,x_2,\markred{x_3},x_4)}$$

    KaTeX's `CD` environment can align several callouts, although its spacing
    is usually too generous for an annotation embedded in a normal matrix:

    $$\begin{CD}A @>{f}>> B \cr @V{\textcolor{royalblue}{g}}V{\textcolor{seagreen}{g'}}V @V{\textcolor{purple}{h}}V{\textcolor{darkorange}{h'}}V \cr C @>{k}>> D\end{CD}$$

    The prototype also tested `\bbox`, `\enclose`, `\htmlStyle`, and related
    extensions. They are deliberately not baseline examples here: support
    depends on KaTeX trust settings and they weaken portability and safety.
    `\colorbox`, `\fcolorbox`, `\textcolor`, `\boxed`, braces, arrows, and
    semantic matrix regions cover the initial SPEC-015 scope.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9f. Size, alignment, and matrix-spacing tools

    Invisible material can align labels without changing what the reader sees.
    `\phantom` reserves both dimensions, while `\vphantom` reserves only
    vertical extent:

    $$\underbrace{A+B}_{\text{short}} \qquad \underbrace{C+\phantom{A+B}+D}_{\text{width aligned}} \qquad \overline{\vphantom{M}a}$$

    `\raisebox` makes a small vertical adjustment when two labels need to sit
    on a common baseline. It should be a renderer-level hint, not a semantic
    coordinate system:

    $$\overset{\raisebox{2pt}{\scriptsize\text{raised note}}}{A} \qquad \underset{\raisebox{-2pt}{\scriptsize\text{lowered note}}}{B}$$

    `\smash` suppresses an annotation's vertical contribution when the
    surrounding layout already reserves sufficient room:

    $$\overset{\smash{\scriptsize\text{compact}}}{x^2} + y \qquad \sqrt{\smash[b]{\text{long annotation}}}$$

    Labelled transition arrows are useful for derivations and representation
    changes:

    $$A \xrightarrow[\text{collect grades}]{\text{expand}} B \xlongequal{\text{evaluate}} C \xleftarrow{\text{inverse}} D$$

    KaTeX's `array` separators can express matrix block structure. A colon is
    lighter than a solid rule, while `\hdashline` gives a visibly dashed split:

    $$\def\arraystretch{1.4}\begin{array}{c:c:c}A_{11} & A_{12} & A_{13} \cr A_{21} & A_{22} & A_{23} \cr \hdashline A_{31} & A_{32} & A_{33}\end{array}$$

    These tools affect layout or grouping only. They should not alter the
    semantic target, algebraic value, matrix entry, or presentation meaning.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9e. Arrow-only callouts and complementary braces

    An annotation may use only an arrow and a label. No vertical leader line
    or delimiter is required:

    $$\overset{\substack{\textcolor{seagreen}{\text{output}} \cr \downarrow}}{v'} = \overset{\substack{\textcolor{royalblue}{\text{rotor}} \cr \downarrow}}{R}\,\overset{\substack{\textcolor{darkorange}{\text{input vector}} \cr \downarrow}}{v}\,\underset{\substack{\uparrow \cr \textcolor{slateblue}{\text{reverse}}}}{\widetilde{R}}$$

    The same arrow-only style can point to a coefficient or matrix entry:

    $$a x^2 + \underset{\substack{\uparrow \cr \textcolor{darkorange}{\text{linear coefficient}}}}{b}\,x + c = 0 \qquad \left(\begin{array}{cc}1 & \overset{\substack{\textcolor{indianred}{\text{mixing}} \cr \downarrow}}{0.5i} \cr 0 & 1\end{array}\right)$$

    A short label can sit directly above or below a target with no arrow at
    all when the spatial relationship is already obvious:

    $$\overset{\textcolor{seagreen}{\text{result}}}{v'} = \underset{\textcolor{royalblue}{\text{input}}}{v}$$

    `\underbrace` groups a span and labels it below. Its complementary form,
    `\overbrace`, labels the span above:

    $$\underbrace{e_1 \wedge e_2}_{\text{bivector part}} \qquad \overbrace{e_1 \wedge e_2}^{\text{bivector part}}$$

    KaTeX also supports the rounded group accents `\undergroup` and
    `\overgroup`:

    $$\undergroup{e_1 \wedge e_2}_{\text{bivector part}} \qquad \overgroup{e_1 \wedge e_2}^{\text{bivector part}}$$

    Both forms can use colour and multi-line labels:

    $$\overbrace{a+b+c}^{\substack{\textcolor{seagreen}{\text{three-term}} \cr \textcolor{seagreen}{\text{input block}}}} + \underbrace{d+e}_{\substack{\textcolor{royalblue}{\text{two-term}} \cr \textcolor{royalblue}{\text{output block}}} }$$

    Braces can nest to show both an inner subexpression and the larger span
    that contains it:

    $$\overbrace{e_1 + \underbrace{e_2 + e_3}_{\text{inner sum}}}^{\text{outer vector expression}}$$

    These are semantic span annotations: the target is the selected
    expression range, while the renderer chooses `\underbrace`, `\overbrace`,
    `\undergroup`, `\overgroup`, an arrow-only callout, or another presentation
    style.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9e.1. Rounded groups with centred, grey labels

    Rounded groups are a quieter alternative to braces. Use `\underset`
    or `\overset` to centre the label, and colour the group and label grey
    while keeping the mathematical content black:

    $$\textcolor{#888888}{\underset{\text{grade 1}}{\undergroup{\textcolor{black}{1.2e_1-0.4e_2}}}} \qquad \textcolor{#888888}{\overset{\text{grade 1}}{\overgroup{\textcolor{black}{1.2e_1-0.4e_2}}}}$$

    Add two pixels of clearance below or above the terms by extending an
    invisible vertical strut in the corresponding direction. The terms
    stay on their original baseline; the group and its label move outward:

    $$\textcolor{#888888}{\underset{\text{grade 1}}{\undergroup{\textcolor{black}{\vphantom{\raisebox{-2px}{$\displaystyle 1.2e_1-0.4e_2$}}1.2e_1-0.4e_2}}}} \qquad \textcolor{#888888}{\overset{\text{grade 1}}{\overgroup{\textcolor{black}{\vphantom{\raisebox{2px}{$\displaystyle 1.2e_1-0.4e_2$}}1.2e_1-0.4e_2}}}}$$

    Group each homogeneous component of a concrete multivector:

    $$A = \textcolor{#888888}{\underset{\text{grade 0}}{\undergroup{\textcolor{black}{0.5}}}} + \textcolor{#888888}{\underset{\text{grade 1}}{\undergroup{\textcolor{black}{1.2e_1-0.4e_2}}}} + \textcolor{#888888}{\underset{\text{grade 2}}{\undergroup{\textcolor{black}{0.7e_{12}+0.2e_{23}}}}} + \textcolor{#888888}{\underset{\text{grade 3}}{\undergroup{\textcolor{black}{0.9e_{123}}}}}$$

    The group annotation and a sign-only highlight can coexist. Grade
    involution negates the odd-grade components; yellow marks only the
    signs that changed:

    $$\widehat{A} = \textcolor{#888888}{\underset{\text{grade 0}}{\undergroup{\textcolor{black}{0.5}}}} \; \textcolor{#888888}{\underset{\text{grade 1}}{\undergroup{\textcolor{black}{\colorbox{#fff3cd}{$-$}\,1.2e_1\mathbin{\colorbox{#fff3cd}{$+$}}0.4e_2}}}} + \textcolor{#888888}{\underset{\text{grade 2}}{\undergroup{\textcolor{black}{0.7e_{12}+0.2e_{23}}}}} \; \textcolor{#888888}{\underset{\text{grade 3}}{\undergroup{\textcolor{black}{\colorbox{#fff3cd}{$-$}\,0.9e_{123}}}}}$$

    Groups can also identify operands rather than grades. Here the upper
    group selects the entire input sum, while the lower group identifies
    the resulting bivector component:

    $$\textcolor{#888888}{\overset{\text{input vector}}{\overgroup{\textcolor{black}{(e_1+e_2)}}}}\wedge e_3 = \textcolor{#888888}{\underset{\text{bivector result}}{\undergroup{\textcolor{black}{e_{13}+e_{23}}}}}$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Multiple annotations and layout pressure

    Several nearby annotations should remain readable and centred on their
        targets:

    $$\overset{\color{seagreen}\substack{\text{output} \cr \downarrow}}{v'} = \overset{\color{royalblue}\substack{\uparrow \cr \text{rotor}}}{R}\,\overset{\color{darkorange}\substack{\text{input} \cr \text{vector} \cr \downarrow}}{v}\,\underset{\color{slateblue}\substack{\uparrow \cr \text{reverse}}}{\widetilde{R}}$$

    When labels are adjacent, the renderer may stagger them into shallow tiers:

    $$\overset{\color{seagreen}\substack{\text{first label} \cr \downarrow}}{a} + \overset{\color{royalblue}\substack{\text{second label} \cr \downarrow}}{b} + \overset{\color{indianred}\substack{\text{third label} \cr \downarrow}}{c}$$

    The layout solver should prefer short labels, preserve anchor-centred output,
    and expose its decisions for debugging rather than applying invisible string
    offsets.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 11. Presentation independence

    An annotation follows the semantic target while the presenter controls the
    display vocabulary. The same operation can therefore appear in different
    notations:

    $$\overset{\color{seagreen}\text{metric pairing}}{\operatorname{metric\_inner\_product}}(e_1,e_2)$$

    $$e_1 \mathbin{\overset{\color{seagreen}\text{metric pairing}}{\bullet}} e_2$$

    $$e_1 \mathbin{\overset{\color{seagreen}\text{metric pairing}}{\cdot}} e_2$$

    The annotation does not choose the symbol, reorder blades, or change the
    algebra. Those remain responsibilities of Galaga's `PresentationConfig`,
    `Notation`, `BladeConvention`, `DisplayOrder`, and `Presenter` systems.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 12. API mockups: annotating semantic targets

    The proposed annotation method should accept one or more semantic targets.
    These are deliberately static examples: they show the intended call shape
    and the corresponding rendering, not a final implementation.

    A single target can be annotated with a compact convenience form:

    ```python
    annotated = annotate(
        value,
        target=VariableTarget(name="R"),
        label="unit rotor",
        style=AnnotationStyle(color="royalblue", marker="arrow"),
    )
    ```

    A possible KaTeX lowering is:

    $$\overset{\substack{\textcolor{royalblue}{\text{unit rotor}} \cr \downarrow}}{R}$$

    The same method can select an operation instead of an operand. The target
    remains `outer_product` if the presenter later changes `\wedge` to a
    functional name:

    ```python
    annotated = annotate(
        (e1 + e2) ^ e3,
        target=OperationTarget(operation_id="outer_product"),
        label="alternating product",
        style=AnnotationStyle(color="seagreen", marker="arrow"),
    )
    ```

    $$(e_1+e_2)\mathbin{\overset{\substack{\textcolor{seagreen}{\text{alternating product}} \cr \downarrow}}{\wedge}}e_3$$

    An `ExpressionSpan` selects a range of sibling nodes, rather than one
    operand or the whole expression:

    ```python
    expr = a + b + c + d
    annotated = annotate(
        expr,
        target=ExpressionSpan(parent=(), start=0, stop=2),
        label="input block",
        style=AnnotationStyle(background="#e7f0ff", marker="brace"),
    )
    ```

    $$\overbrace{\colorbox{#e7f0ff}{$a+b$}}^{\text{input block}} + c + d$$

    Several targets can be annotated in one call. Here one annotation selects
    only a coefficient, another selects the complete term, and a third selects
    a relation:

    ```python
    annotated = annotate(
        result,
        annotations=(
            Annotation(
                target=MultivectorCoefficient(blade=e1),
                label="coefficient",
                style=AnnotationStyle(color="darkorange"),
            ),
            Annotation(
                target=MultivectorTerm(blade=e12),
                label="bivector term",
                style=AnnotationStyle(background="#fff3cd", marker="box"),
            ),
            Annotation(
                target=RelationTarget(kind="equality"),
                label="evaluates to",
                style=AnnotationStyle(color="purple", marker="arrow"),
            ),
        ),
    )
    ```

    $$\overset{\textcolor{purple}{\text{evaluates to}}}{=} \qquad 1.\overset{\textcolor{darkorange}{\text{coefficient}}}{354}e_1 + \colorbox{#fff3cd}{$\displaystyle 2e_{12}$}$$

    A `MultivectorCoefficientSet` or `MultivectorTermSet` can select several
    terms that are not necessarily adjacent in the display order:

    ```python
    annotated = annotate(
        c,
        annotations=(
            Annotation(
                target=MultivectorTermSet(
                    blades=(e423, e431, e412, e321),
                ),
                label="carrier plane",
                style=AnnotationStyle(background="#b8e6bf", marker="box"),
            ),
            Annotation(
                target=MultivectorTermSet(
                    blades=(e415, e425, e435, e235, e315, e125),
                ),
                label="flat-line part",
                style=AnnotationStyle(background="#d8c4ee", marker="box"),
            ),
        ),
    )
    ```

    $$c = \underset{\text{carrier plane}}{\colorbox{#b8e6bf}{$c_{gx}e_{423}+c_{gy}e_{431}+c_{gz}e_{412}+c_{gw}e_{321}$}} + \underset{\text{flat-line part}}{\colorbox{#d8c4ee}{$c_{vx}e_{415}+c_{vy}e_{425}+c_{vz}e_{435}+c_{mx}e_{235}+c_{my}e_{315}+c_{mz}e_{125}$}}$$

    A grade target is a different selection: it follows every displayed term
    of a grade, even when those terms are separated by other components:

    ```python
    annotated = annotate(
        A,
        target=GradeTarget(grade=2),
        label="bivector grade",
        style=AnnotationStyle(color="#D55E00", marker="brace"),
    )
    ```

    $$A = A_0 + \underbrace{\textcolor{#D55E00}{A_2}}_{\text{bivector grade}} + A_1 + A_3$$

    A matrix annotation uses coordinates instead of an expression path:

    ```python
    annotated = annotate(
        matrix,
        annotations=(
            Annotation(
                target=MatrixCell(row=1, column=2),
                label="mixing term",
                style=AnnotationStyle(background="#fff3cd", marker="box"),
            ),
            Annotation(
                target=MatrixRegion(
                    rows=slice(1, 4),
                    columns=slice(1, 4),
                ),
                label="selected block",
                style=AnnotationStyle(border="seagreen", marker="box"),
            ),
        ),
    )
    ```

    $$M = \left(\begin{array}{cccc}a_{11} & a_{12} & a_{13} & a_{14} \cr a_{21} & \colorbox{#fff3cd}{$a_{22}$} & \colorbox{#e8f5e9}{$a_{23}$} & \colorbox{#e8f5e9}{$a_{24}$} \cr a_{31} & \colorbox{#e8f5e9}{$a_{32}$} & \colorbox{#e8f5e9}{$a_{33}$} & \colorbox{#e8f5e9}{$a_{34}$} \cr a_{41} & \colorbox{#e8f5e9}{$a_{42}$} & \colorbox{#e8f5e9}{$a_{43}$} & \colorbox{#e8f5e9}{$a_{44}$}\end{array}\right)$$

    The important contract is that `annotate(...)` stores semantic targets and
    styles first. The presenter or renderer then chooses whether each target
    becomes text colour, a background, a border, an arrow, a brace, an HTML
    cell fill, or another supported lowering.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 13. Teaching-notebook use cases

    The annotation API is most useful when it follows the questions students
    actually ask. The following examples are motivated by common GA lessons,
    rather than by isolated rendering features.

    **Metric product versus outer product.** A first lesson often contrasts
    the symmetric metric contribution with the antisymmetric oriented-area
    contribution of a geometric product:

    ```python
    annotated = annotate(
        a * b,
        annotations=(
            Annotation(
                target=ExpressionSpan(parent=(), start=0, stop=1),
                label="metric part",
                style=AnnotationStyle(color="royalblue", marker="brace"),
            ),
            Annotation(
                target=ExpressionSpan(parent=(), start=1, stop=2),
                label="outer part",
                style=AnnotationStyle(color="seagreen", marker="brace"),
            ),
        ),
    )
    ```

    $$ab = \underbrace{a\mathbin{\cdot}b}_{\textcolor{royalblue}{\text{metric part}}} + \overbrace{a\mathbin{\wedge}b}^{\textcolor{seagreen}{\text{outer part}}}$$

    **A rotor sandwich.** When teaching rotations, the important roles are
    the rotor, the input vector, the reverse rotor, and the transformed output:

    ```python
    annotated = annotate(
        R * v * ~R,
        annotations=(
            Annotation(target=VariableTarget(name="R"), label="rotor"),
            Annotation(target=VariableTarget(name="v"), label="input vector"),
            Annotation(target=VariableTarget(name="~R"), label="reverse"),
            Annotation(target=WholeExpression(), label="rotated vector"),
        ),
    )
    ```

    $$\overset{\substack{\textcolor{seagreen}{\text{rotated vector}} \cr \downarrow}}{v'} = \overset{\substack{\textcolor{royalblue}{\text{rotor}} \cr \downarrow}}{R}\,\overset{\substack{\textcolor{darkorange}{\text{input vector}} \cr \downarrow}}{v}\,\underset{\substack{\uparrow \cr \textcolor{slateblue}{\text{reverse}}}}{\widetilde{R}}$$

    **Grade projection.** A projection lesson benefits from showing which
    components are retained and which are discarded, rather than presenting
    only the final answer:

    ```python
    annotated = annotate(
        grade_projection(A, 1),
        annotations=(
            Annotation(target=GradeTarget(grade=1), label="retained vector"),
            Annotation(target=GradeTarget(grade=0), label="discarded scalar"),
            Annotation(target=GradeTarget(grade=2), label="discarded bivector"),
        ),
    )
    ```

    $$\langle A_0 + A_1 + A_2\rangle_1 = \cancel{\textcolor{#999999}{A_0}} + \textcolor{royalblue}{A_1} + \cancel{\textcolor{#999999}{A_2}} = \textcolor{royalblue}{A_1}$$

    **A conformal point construction.** In a CGA notebook, students need to
    see the Euclidean vector contribution separately from the null-basis
    correction:

    ```python
    point = e_o + x + (x * x / 2) * e_infinity
    annotated = annotate(
        point,
        annotations=(
            Annotation(target=SemanticRoleTarget(role="origin"), label="origin"),
            Annotation(target=SemanticRoleTarget(role="euclidean_vector"), label="Euclidean position"),
            Annotation(target=SemanticRoleTarget(role="infinity_correction"), label="null correction"),
        ),
    )
    ```

    $$P(x) = \colorbox{#d8c4ee}{$e_o$} + \colorbox{#b8e6bf}{$x$} + \colorbox{#e7f0ff}{$\displaystyle\frac{x^2}{2}e_\infty$}$$

    **Null-basis metric interpretation.** A Gram-matrix lesson can annotate
    the two non-zero pairings instead of colouring every zero entry:

    ```python
    annotated = annotate(
        gram_matrix,
        annotations=(
            Annotation(target=MatrixCell(row="e_o", column="e_infinity"), label="null pairing"),
            Annotation(target=MatrixCell(row="e_infinity", column="e_o"), label="symmetric pairing"),
            Annotation(target=MatrixRegion(rows=slice(0, 3), columns=slice(0, 3)), label="Euclidean block"),
        ),
    )
    ```

    $$\begin{array}{c|ccccc}g & e_1 & e_2 & e_3 & e_o & e_\infty \\ \hline e_1 & \colorbox{#e8f5e9}{$1$} & 0 & 0 & 0 & 0 \\ e_2 & 0 & \colorbox{#e8f5e9}{$1$} & 0 & 0 & 0 \\ e_3 & 0 & 0 & \colorbox{#e8f5e9}{$1$} & 0 & 0 \\ e_o & 0 & 0 & 0 & 0 & \colorbox{#fff3cd}{$-1$} \\ e_\infty & 0 & 0 & 0 & \colorbox{#fff3cd}{$-1$} & 0\end{array}$$

    **Meet, join, or contraction notation.** A notation lesson can keep the
    operation's semantic identity stable while showing several configured
    symbols:

    ```python
    annotated = annotate(
        left_contraction(A, B),
        target=OperationTarget(operation_id="left_contraction"),
        label="left contraction",
    )
    ```

    $$A\mathbin{\overset{\text{left contraction}}{\lfloor}}B \qquad A\mathbin{\overset{\text{outer product}}{\wedge}}B \qquad A\mathbin{\overset{\text{geometric product}}{}}B$$

    These examples reinforce the core design: annotations should explain the
    mathematics of a notebook, while the presenter controls notation and the
    renderer controls layout.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways for the future API

    The rendering gallery suggests three important boundaries:

    1. annotations describe semantic targets, not rendered character offsets;
    2. annotation plans remain format-neutral until a renderer lowers them;
    3. KaTeX layout is approximate and must be tested with real Marimo output.

    The first useful implementation slice is therefore whole-expression,
    expression-path, operation, multivector-term, and matrix-region targets,
    rendered through the existing Galaga presentation and semantic LaTeX
    systems.
    """)
    return


if __name__ == "__main__":
    app.run()
