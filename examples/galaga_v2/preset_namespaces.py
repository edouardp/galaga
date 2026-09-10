"""Teach the difference between complete algebra and blade-vocabulary presets."""

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy, presets

    return Algebra, DisplayPolicy, gm, mo, presets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Choosing an algebra and choosing its vocabulary

    Galaga separates two decisions:

    1. A complete preset chooses a Gram matrix, model roles, notation, and
       coordinated basis names.
    2. A blade preset chooses only the names and signed aliases for an
       algebra whose metric we specify separately.

    The second form is especially useful when teaching a familiar metric
    with a different vocabulary.
    """)
    return


@app.cell
def _(Algebra, presets):
    complete_cga = Algebra(config=presets.cga(3))
    complete_cga.bilinear_form_table()
    return


@app.cell
def _(Algebra, presets):
    named_sta = Algebra(1, 3, blades=presets.blades.sta(sigmas=True, pseudovectors=True))
    named_sta.basis_vectors(expr=True)
    return (named_sta,)


@app.cell
def _(gm, named_sta):
    _sigma = named_sta.blade("s1")
    _native_bivector = named_sta.blade(0b0011)
    _sigma_sign = float(_sigma.data[0b0011])
    gm.md(rt"""
        The sigma name is derived from the ordered metric, not guessed from
        the label. For this $(+---)$ algebra,

        $$\sigma_1={_sigma_sign:g}\,e_{{01}}.$$

        The actual native coefficient is computed as `{_sigma_sign:g}`.
        The vocabulary changes display and signed lookup; it does not change
        the Gram matrix or the underlying basis mask.
        """)
    return


@app.cell
def _(Algebra, DisplayPolicy, gm, presets):
    _small = Algebra(3, display=DisplayPolicy(content="full"))
    _plain_blades = _small.with_blades(presets.blades.euclidean(3))
    _full_wedge = _plain_blades.wedge_product_table(full=True, colour=True)
    gm.md(rt"""
        A blade recipe can be combined with the wedge-table renderer. This
        full table starts at the scalar $1$ and is grouped by grade:

        {_full_wedge:block}
        """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(
        r"""
        Complete presets are convenient when the metric and model belong
        together. Blade-only recipes are deliberately narrower: they cannot
        turn an orthogonal conformal metric into a null-pair CGA, and
        metric-aware STA names reject unsupported Gram matrices.
        """
    )
    return


if __name__ == "__main__":
    app.run()
