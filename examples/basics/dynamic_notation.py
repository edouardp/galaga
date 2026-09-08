import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, Name, Notation, RenderRule, exp, reverse, sandwich

    return Algebra, Name, Notation, RenderRule, exp, gm, mo, np, reverse, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # One reversal, several notations

    Reversal is an algebraic operation; its glyph is a presentation choice.
    First compute a rotor and its reverse, then render the **same value and
    expression** with a tilde, dagger, superscript R, or functional notation.

    Galaga 2 uses immutable `Notation.with_rule(...)` values. There is no
    mutable notation registry on the algebra. Here a dagger means reversal;
    it does not introduce an additional complex-conjugation operation.
    """)
    return


@app.cell
def _(Algebra, exp, np, reverse, sandwich):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors(expr=True)
    plane = (e1 ^ e2).named("B")
    assert plane * plane == -1
    theta = alg.scalar(np.pi / 3, expr=True).named("theta", latex=r"\theta")
    rotor = exp(-theta * plane / 2).named("R")
    reversed_rotor = reverse(rotor)
    vector = (3 * e1 + 4 * e2 + e3).named("v", latex=r"\vec{v}")
    rotated = sandwich(rotor, vector)
    np.testing.assert_allclose((rotor * reversed_rotor).data, alg.identity.data, atol=1e-12)
    return alg, reversed_rotor, rotated, rotor


@app.cell
def _(Name, Notation, RenderRule):
    reverse_notations = {
        "Tilde": Notation.hestenes().with_rule(
            "reverse", RenderRule("accent", symbol=Name("tilde", "̃", r"\widetilde"))
        ),
        "Dagger": Notation.hestenes().with_rule(
            "reverse", RenderRule("superscript", symbol=Name("dagger", "†", r"\dagger"))
        ),
        "Superscript R": Notation.hestenes().with_rule("reverse", RenderRule("superscript", symbol="R")),
        "Function": Notation.hestenes().with_rule("reverse", RenderRule("function", symbol="rev")),
    }
    return (reverse_notations,)


@app.cell
def _(gm, mo, reverse_notations, reversed_rotor):
    _before = reversed_rotor.expr, reversed_rotor.data.copy()
    reverse_renderings = {
        _label: reversed_rotor.latex(content="full", notation=_notation)
        for _label, _notation in reverse_notations.items()
    }
    mo.vstack([gm.md(t"""**{_label}:** $${_latex!s}$$""") for _label, _latex in reverse_renderings.items()])
    assert reversed_rotor.expr == _before[0]
    assert (reversed_rotor.data == _before[1]).all()
    return (reverse_renderings,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## An interactive rendering choice

    `notation=` affects this rendering call only. It does not reevaluate the
    sandwich or change the algebra's defaults. To keep a different default
    for future values, use `alg.with_notation(...)`: the returned facade view
    shares the original numeric algebra.
    """)
    return


@app.cell
def _(mo, reverse_notations):
    notation_choice = mo.ui.dropdown(options=list(reverse_notations), value="Dagger", label="Reverse notation")
    notation_choice
    return (notation_choice,)


@app.cell
def _(alg, gm, notation_choice, reverse_notations, rotated):
    _notation = reverse_notations[notation_choice.value]
    _latex = rotated.latex(content="full", notation=_notation)
    _view = alg.with_notation(_notation)
    assert _view.numeric is alg.numeric
    gm.md(t"""The unchanged sandwich, with the selected notation:

    $${_latex!s}$$
    """)
    return


if __name__ == "__main__":
    app.run()
