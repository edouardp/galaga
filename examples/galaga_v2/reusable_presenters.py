"""One calculation, several teaching presentations, with honest blade signs."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():

    import marimo as mo

    import galaga_marimo as gm
    from galaga import (
        Algebra,
        DisplayPolicy,
        Presenter,
        complement,
        dual,
        left_hodge_dual,
        metric_inner_product,
        presets,
    )
    from galaga import metric_inner_product as metric_ip
    from galaga.names import Name

    return (
        Algebra,
        DisplayPolicy,
        Name,
        Presenter,
        complement,
        dual,
        gm,
        left_hodge_dual,
        metric_inner_product,
        metric_ip,
        mo,
        presets,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # One calculation, several teaching presentations

    A calculation answers **what is the value?** A presenter answers **how
    should this lesson show it?** Prepare presenters in one line, then select
    one at the point of display. No context manager is required.

    We will compare operation notation, expression versus value, blade ordering,
    exterior-product spelling and signed spacetime names. Throughout, the
    multivector, its metric and its expression provenance remain unchanged.
    """)
    return


@app.cell
def _(Algebra, presets):
    alg = Algebra(config=presets.euclidean(3), expr=True)
    e1, e2, e3 = alg.basis_vectors()
    lengyel = presets.presenters.lengyel()
    functional = presets.presenters.functional()
    values = presets.presenters.values()
    return alg, e1, e2, e3, functional, lengyel, values


@app.cell
def _(e1, metric_ip):
    pairing = metric_ip(e1, e1)
    assert pairing == e1.algebra.scalar(e1.algebra.gram[0, 0])
    return (pairing,)


@app.cell
def _(functional, gm, lengyel, mo, pairing, values):
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.vstack([mo.md("**Lengyel notation**"), lengyel(pairing)]),
                    mo.vstack([mo.md("**Functional notation**"), functional(pairing)]),
                ],
                wrap=True,
                gap=2,
            ),
            gm.md(rt"""
        Both views show the **same metric inner product**. With values only:
        {values(pairing)}.

        `lengyel(pairing)` is a display view, not a new calculation.
        It also works directly inside `gm.md` interpolation.
        """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Choose what the reader should see

    Operation notation and content are independent. Content can be **name**,
    **expression**, **value**, **full**, or **auto** (a deduplicated equality
    when there is provenance or a name). The display policy also controls the
    output target (`unicode`, `ascii`, or `latex`), coefficient precision,
    basis vector style (regular $e$ or bold upright $\mathbf{e}$), and blade
    format (`compact`, `juxtaposition`, or `wedge`).

    `expr=True` enabled provenance when we created the algebra. A presenter
    cannot reconstruct a derivation that was never recorded. Other presenter
    overrides include blade vocabulary, local names, display order, and a
    complete presentation configuration.
    """)
    return


@app.cell
def _(mo):
    notation_choice = mo.ui.dropdown(
        ["Lengyel", "Functional", "Short Functional", "Conventional", "Hestenes"],
        value="Lengyel",
        label="Operation notation",
    )
    content_choice = mo.ui.dropdown(["auto", "name", "expr", "value", "full"], value="auto", label="Content")
    target_choice = mo.ui.dropdown(["unicode", "ascii", "latex"], value="unicode", label="Output target")
    precision_choice = mo.ui.slider(1, 17, value=6, step=1, label="Coefficient precision")
    return content_choice, notation_choice, precision_choice, target_choice


@app.cell
def _(mo):
    blade_choice = mo.ui.dropdown(["Compact", "Juxtaposition", "Wedge"], value="Compact", label="Blade format")
    basis_choice = mo.ui.dropdown(["Default e", "Bold e", "Bold v"], value="Default e", label="Basis vector style")
    return basis_choice, blade_choice


@app.cell
def _(
    DisplayPolicy,
    Name,
    Presenter,
    basis_choice,
    blade_choice,
    complement,
    content_choice,
    dual,
    e1,
    e2,
    e3,
    gm,
    left_hodge_dual,
    metric_inner_product,
    mo,
    notation_choice,
    precision_choice,
    presets,
    target_choice,
):
    wedge_result = (metric_inner_product(e1, e1) + e2) ^ ~e3
    gp_result = (complement(e1) + dual(e2)) * left_hodge_dual(e3)

    _notations = {
        "Lengyel": presets.notation.lengyel(),
        "Functional": presets.notation.functional(),
        "Short Functional": presets.notation.functional_short(),
        "Conventional": presets.notation.default(),
        "Hestenes": presets.notation.hestenes(),
    }
    _basis_prefixes = {
        "Default e": Name("e"),
        "Bold e": Name.from_latex(r"\mathbf{e}"),
        "Bold v": Name.from_latex(r"\mathbf{v}"),
    }
    _blade_formats = {
        "Compact": "compact",
        "Juxtaposition": "juxtapose",
        "Wedge": "wedge",
    }
    _blade_preset = presets.blades.indexed(
        3,
        prefix=_basis_prefixes[basis_choice.value],
        style=_blade_formats[blade_choice.value],
    )
    chosen_presenter = Presenter(
        blades=_blade_preset,
        notation=_notations[notation_choice.value],
        display=DisplayPolicy(target=target_choice.value, coefficient_precision=precision_choice.value),
        content=content_choice.value,
    )
    chosen_view = chosen_presenter(wedge_result)
    chosen_gp_view = chosen_presenter(gp_result)

    mo.vstack(
        [
            mo.vstack(
                [notation_choice, content_choice, target_choice, precision_choice, basis_choice, blade_choice],
            ),
            gm.md(rt"""
            <br/>**Custom presenter:**<br/>
            {chosen_view}

            {chosen_gp_view}
            """),
        ]
    )
    return chosen_gp_view, chosen_presenter, chosen_view, gp_result, wedge_result


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Blade order is not coefficient storage order

    Grade order keeps vectors together before bivectors. Bitmap order follows
    the native coefficient slots, which can interleave grades.

    These portable recipes resolve against each value's dimension. Neither
    rearranges its stored data nor changes the ordered basis or pseudoscalar.
    Here we deliberately use an untracked mixed-grade value so that the
    comparison is about **terms**, not the history of a calculation.
    """)
    return


@app.cell
def _(alg, presets):
    grade_order = presets.presenters.grade_order()
    bitmap_order = presets.presenters.bitmap_order()
    mixed = alg.multivector([0.5, 0.25, -0.375, 0.25, 0.5, 0.25, -0.375, 0.25], expr=False)
    grade_view = grade_order(mixed)
    bitmap_view = bitmap_order(mixed)
    assert grade_view.value.numeric is bitmap_view.value.numeric
    return bitmap_view, grade_view


@app.cell
def _(bitmap_view, gm, grade_view, mo):
    mo.vstack(
        [
            gm.md(rt"""**Grade, then lexicographic order**

        {grade_view}
        """),
            gm.md(rt"""**Native bitmap order**

        {bitmap_view}
        """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Blade spelling: make the exterior product visible

    In an oblique Euclidean basis, the geometric product of two basis vectors
    is not just their exterior blade. Our vectors have unit square and pairing
    $1/2$, so $ab=1/2+a\wedge b$.

    A target-aware `Name.from_latex(r"\mathbf{e}")` gives us bold upright
    $\mathbf{e}$ labels. The same blade can then be shown in the three indexed
    styles: compact, juxtaposition, or wedge. These are display conventions,
    not changes of basis or changes to the computed product.
    """)
    return


@app.cell
def _(Algebra, Name, Presenter, presets):
    oblique = Algebra(gram=((1, 0.5), (0.5, 1)), expr=True)
    a, b = oblique.basis_vectors()
    oblique_product = a * b
    assert oblique_product == 0.5 + (a ^ b)
    bold_e = Name.from_latex(r"\mathbf{e}")
    bold_e_blades = presets.blades.indexed(2, prefix=bold_e)
    compact = Presenter(blades=bold_e_blades, content="value")
    juxtaposed = Presenter(
        blades=presets.blades.indexed(2, prefix=bold_e, style="juxtapose"),
        content="value",
    )
    exterior_words = Presenter(
        blades=presets.blades.indexed(2, prefix=bold_e, style="wedge"),
        content="value",
    )
    return compact, exterior_words, juxtaposed, oblique, oblique_product


@app.cell
def _(compact, exterior_words, gm, juxtaposed, mo, oblique, oblique_product):
    mo.vstack(
        [
            mo.md("**The actual bilinear form**"),
            oblique.bilinear_form_table(),
            mo.hstack(
                [
                    mo.vstack([mo.md("**Compact labels**"), compact(oblique_product)]),
                    mo.vstack([mo.md("**Juxtaposed labels**"), juxtaposed(oblique_product)]),
                    mo.vstack([mo.md("**Wedge labels**"), exterior_words(oblique_product)]),
                ],
                wrap=True,
                gap=2,
            ),
            gm.md(rt"""
        All three views retain the scalar contribution. Only the blade spelling changes;
        the non-orthogonal geometric product is still $1/2 + a\wedge b$.
        """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Signed naming: spacetime bivectors and observer-relative sigmas

    The conventional observer-relative blade is
    $\sigma_1=\gamma_1\gamma_0$, while the native sorted blade is
    $\gamma_0\gamma_1=-\sigma_1$.

    A presenter must keep that sign. We compute the products first, then
    resolve Galaga's existing sigma recipe against the actual metric.
    Changing signature changes squares, not this anticommutation identity.
    """)
    return


@app.cell
def _(mo):
    signature_choice = mo.ui.dropdown(
        ["mostly-minus", "mostly-plus"], value="mostly-minus", label="Spacetime signature"
    )
    return (signature_choice,)


@app.cell
def _(Algebra, Presenter, gm, mo, presets, signature_choice):
    sta = Algebra(config=presets.sta(signature_choice.value))
    gamma0, gamma1, _, _ = sta.basis_vectors()
    sigma_product = gamma1 * gamma0
    native_product = gamma0 * gamma1
    sigma_labels = Presenter(blades=presets.blades.sta(sigmas=True), content="value")
    sigma_view = sigma_labels(sigma_product)
    native_sigma_view = sigma_labels(native_product)
    _sigma_ref = sigma_view.presentation.blades.resolve("s1")
    assert sta.blade(_sigma_ref) == sigma_product == -native_product
    assert sigma_view.value is sigma_product
    mo.vstack(
        [
            signature_choice,
            gm.md(rt"""**The same two products, with gamma labels**

        {sigma_product} and {native_product}.
        """),
            gm.md(rt"""**With observer-relative sigma labels**

        {sigma_view} and {native_sigma_view}.

        The displayed minus sign follows the actual product, not a hand-written correction.
        """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A CGA presentation is not a new conformal frame

    A notation-only presenter is portable; a blade recipe may have geometric
    requirements. Here we opt into the existing $I_E$, $I_C$ and $E$ names
    for the **same** origin-first null basis.

    A request to use an incompatible CGA frame is rejected. Presenters do not
    convert null coordinates into orthogonal coordinates or permute basis vectors.
    """)
    return


@app.cell
def _(Algebra, Presenter, presets):
    cga = Algebra(config=presets.cga(2))
    eo, ce1, ce2, einf = cga.basis_vectors()
    cga_parts = (ce1 ^ ce2, cga.I, eo ^ einf)
    cga_names = Presenter(blades=presets.blades.cga(2, model_pseudoscalars=True, pseudoscalar_null=True))
    cga_views = tuple(cga_names(part) for part in cga_parts)
    assert cga.I == eo ^ ce1 ^ ce2 ^ einf
    try:
        Presenter(blades=presets.blades.cga(2, frame="orthogonal"))(cga.I)
    except ValueError as _error:
        rejected_frame = str(_error)
    else:
        raise AssertionError("an incompatible frame must be rejected")
    return cga_parts, cga_views, rejected_frame


@app.cell
def _(cga_parts, cga_views, gm, mo, rejected_frame):
    mo.vstack(
        [
            gm.md(rt"""**Original labels**

        {cga_parts[0]}, {cga_parts[1]}, {cga_parts[2]}.

        **Teaching labels for those same values**

        {cga_views[0]}, {cga_views[1]}, {cga_views[2]}.
        """),
            gm.md(rt"""The orthogonal-frame request is rejected: {rejected_frame}"""),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Capture once; display when convenient

    A presenter stores a **recipe**. Applying it captures a **resolved
    presentation** together with the original value. Later scopes cannot
    silently restyle that view.

    Existing `use_*` scopes still work for rendering a block of markdown.
    Presenters are the alternative when you want a reusable choice, a cell's
    final expression, or something to assign now and display later.
    """)
    return


@app.cell
def _(alg, pairing, presets):
    inherit = presets.presenters.default()
    with alg.use_notation(presets.notation.lengyel()):
        saved_view = inherit(pairing)
    saved_latex = saved_view.latex()
    with alg.use_notation(presets.notation.functional()):
        assert saved_view.latex() == saved_latex
    return (saved_view,)


@app.cell
def _(mo, saved_view):
    mo.output.replace(saved_view)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways

    - Prepare `Presenter(...)` or `presets.presenters.*()` in one line.
    - Call it on a multivector to get a stable, renderable view.
    - Use the original multivector, or `view.value`, for further calculations.
      Views deliberately do not implement arithmetic.
    - Unspecified components inherit from the value; explicit component
      overrides win over a supplied complete presentation. `content=` wins
      over the content inside `display=DisplayPolicy(...)`.
    - Ordering is display-only. Signed blade labels preserve the represented
      value. Neither changes the metric, native basis or pseudoscalar.
    - Explicit symbol names in provenance remain explicit names: a presenter
      changes blade vocabulary, not user-authored symbol definitions.
    - These presenters currently accept multivectors and existing presentation
      views. Matrices and pre-rendered algebra tables keep their own display APIs.
    """)
    return


if __name__ == "__main__":
    app.run()
