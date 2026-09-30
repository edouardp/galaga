"""A small notation patch changes one operation without replacing a preset."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import galaga_marimo as gm
    from galaga import Algebra, presets

    return Algebra, gm, mo, presets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # One notation change, same algebra

    A complete preset chooses a metric, blade names, model roles, and notation.
    `presets.notation.override(reverse=...)` changes only the reverse symbol.
    The metric and every unrelated notation rule stay with the preset.
    """)
    return


@app.cell
def _(mo):
    reverse_style = mo.ui.dropdown(
        options=["dagger", "tilde"],
        value="dagger",
        label="Reverse notation",
    )
    reverse_style
    return (reverse_style,)


@app.cell
def _(Algebra, presets, reverse_style):
    notation_patch = presets.notation.override(reverse=reverse_style.value)
    base_algebra = Algebra(config=presets.sta(), expr=True)
    styled_algebra = Algebra(config=presets.sta() | notation_patch, expr=True)
    return base_algebra, notation_patch, styled_algebra


@app.cell
def _(base_algebra, styled_algebra):
    _b0, _b1, _, _ = base_algebra.basis_vectors()
    _s0, _s1, _, _ = styled_algebra.basis_vectors()
    base_vector = (_b0 + _b1).named("a")
    styled_vector = (_s0 + _s1).named("a")
    base_reverse = ~base_vector
    styled_reverse = ~styled_vector
    return base_reverse, styled_reverse


@app.cell
def _(base_reverse, gm, styled_reverse):
    gm.md(rt"""
    **Preset notation:** {base_reverse:expr}

    **Selected override:** {styled_reverse:expr}

    Both expressions evaluate to the same vector; only the reverse symbol
    changes. The patch updates the LaTeX rule as well as plain-text targets.
    """)
    return


@app.cell
def _(base_algebra, gm, styled_algebra):
    _same_metric = (base_algebra.gram == styled_algebra.gram).all()
    _same_blades = base_algebra.presentation.blades == styled_algebra.presentation.blades
    _same_model = base_algebra.model == styled_algebra.model
    gm.md(t"""
    The Gram matrices match: **{_same_metric}**. Blade conventions match:
    **{_same_blades}**. Model roles match: **{_same_model}**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two patches can also be composed with `|`; the right-hand value wins for
    an overlapping choice. A full `Notation` on the right still replaces the
    notation slot. This distinction keeps a one-rule change lightweight.
    """)
    return


@app.cell
def _(Algebra, presets):
    right_wins = (
        presets.sta()
        | presets.notation.override(reverse="dagger")
        | presets.notation.override(reverse="tilde")
    )
    Algebra(config=right_wins).presentation.notation.rule("reverse", "latex")
    return


if __name__ == "__main__":
    app.run()
