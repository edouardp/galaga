import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "galaga_marimo")
    for p in [_root, _gamo]:
        if p not in sys.path:
            sys.path.insert(0, p)

    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import galaga_marimo as gm
    from galaga import (
        Algebra, exp, log, dual, undual, inverse, reverse,
        complement, uncomplement,
    )
    from galaga.notation import Notation, NotationRule


    return Algebra, NotationRule, exp, gm, np, reverse


@app.cell
def _(Algebra, NotationRule):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors(lazy=True)

    # 1. Superscript R
    #alg.notation.set("Reverse", "latex", NotationRule(kind="superscript", symbol="R"))

    # 2. Superscript sim (tilde)
    alg.notation.set("Reverse", "latex", NotationRule(kind="superscript", symbol=r"\sim"))

    # 3. Postfix tilde (literal ~)
    #alg.notation.set("Reverse", "latex", NotationRule(kind="postfix", symbol=r"\tilde{}"))

    # 4. Function style: rev(x)
    #alg.notation.set("Reverse", "latex", NotationRule(kind="function", symbol="rev"))

    # 5. Accent (default — should work)
    #alg.notation.set("Reverse", "latex", NotationRule(kind="accent", latex_cmd=r"\tilde", latex_wide_cmd=r"\widetilde"))

    # 6. Superscript dagger
    alg.notation.set("Reverse", "latex", NotationRule(kind="superscript", symbol=r"\dagger"))

    # 7. Superscript star
    #alg.notation.set("Reverse", "latex", NotationRule(kind="superscript", symbol="*"))

    # 8. Prefix with space: \tilde{} before operand
    #alg.notation.set("Reverse", "latex", NotationRule(kind="prefix", symbol=r"\tilde{} "))

    # 9. Prefix with space: \sim{} before operand
    #alg.notation.set("Reverse", "latex", NotationRule(kind="prefix", symbol=r"\sim{} "))

    # 10. Hacky sim
    #alg.notation.set("Reverse", "latex", NotationRule(kind="prefix", symbol=r"{}^{\sim}\!"))

    # 11. Hacky ~
    #alg.notation.set("Reverse", "latex", NotationRule(kind="prefix", symbol=r"\text{\textasciitilde}"))

    return alg, e1, e2, e3


@app.cell
def _(alg, e1, e2, e3, exp, gm, np, reverse):
    _theta = alg.scalar(np.radians(60)).name(latex=r"\theta")

    _B = (e1 * e2).name("B")
    _v = (3 * e1 + 4 * e2 + e3).name(latex=r"\vec{v}")
    _R = exp((-_theta / 2) * _B).name("R")

    _rotated = _R * _v * reverse(_R)

    gm.md(t"""{_rotated} = {_rotated.eval():.2f}""")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
