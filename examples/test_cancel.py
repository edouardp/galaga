"""Automatically cancel zero-valued subexpressions."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from galaga import Algebra, presets
    import galaga_annotation as ga

    return Algebra, ga, mo, presets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Cancelling expressions that evaluate to zero

    With expression provenance enabled, Galaga retains both an eager numeric
    result and the operation tree that produced it. `ga.cancel_zeros()` walks
    that tree when the annotator is applied, evaluates its operation subtrees,
    and crosses out the innermost ones whose coefficients are all zero.

    Choosing the innermost zero operations avoids nested cancellation marks and
    normally exposes the mathematical reason a larger expression simplifies.
    """)
    return


@app.cell
def _(Algebra, presets):
    alg = Algebra(config=presets.euclidean(3), expr=True)
    e1, e2, e3 = alg.basis_vectors()
    return e1, e2, e3


@app.cell
def _(ga):
    cancel_exact_zeros = ga.cancel_zeros(color="#aaaf")
    return (cancel_exact_zeros,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Orthogonality inside a nonzero expression

    In an orthonormal Euclidean basis, $e_1\mathbin{\cdot}e_2=0$, while
    $e_1\wedge e_2$ is nonzero. The annotator discovers only the vanishing
    inner-product subtree.
    """)
    return


@app.cell
def _(cancel_exact_zeros, e1, e2):
    v = ((e1 | e2) + (e1 ^ e2)).named("v")
    first_view = cancel_exact_zeros(v)
    first_view
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Several independent zeros

    Each innermost zero operation receives its own cancellation mark. Their
    zero-valued parent sum is not cancelled again.
    """)
    return


@app.cell
def _(cancel_exact_zeros, e1, e2, e3):
    several = ((e1 | e2) + (e1 | e3) + (e1 ^ e2)).named("w")
    several_view = cancel_exact_zeros(several)
    several_view
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A zero composite inside a nonzero expression

    Neither geometric product below is zero on its own. Their sum is the
    anticommutator of two orthogonal vectors, so that complete subtree is the
    smallest vanishing operation. The trailing $e_1e_1=1$ deliberately keeps
    the whole expression nonzero and makes the selector's scope visible:

    $$a=(e_1e_2+e_2e_1)+e_1e_1=2(e_1\mathbin{\cdot}e_2)+1=1.$$
    """)
    return


@app.cell
def _(cancel_exact_zeros, e1, e2):
    anticommutator_example = ((e1 * e2 + e2 * e1) + e1 * e1).named("a")
    anticommutator_view = cancel_exact_zeros(anticommutator_example)
    anticommutator_view
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exact zero versus numerical tolerance

    The default `atol=0` means exactly zero coefficients. This is appropriate
    for basis identities computed exactly by the algebra. A positive absolute
    tolerance is an explicit teaching choice for floating-point calculations;
    it should reflect the scale and error model of the lesson.
    """)
    return


@app.cell
def _(cancel_exact_zeros, e1, e2):
    almost_zero = (1e-13 * (e1 | e1) + (e1 ^ e2)).named("n")
    exact_view = cancel_exact_zeros(almost_zero)
    exact_view
    return (almost_zero,)


@app.cell
def _(almost_zero, ga):
    cancel_small_values = ga.cancel_zeros(atol=1e-12, color="#aaaf")
    tolerant_view = cancel_small_values(almost_zero)
    tolerant_view
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A nonzero control

    Evaluation drives the selector: a structurally similar but nonzero inner
    product is left alone.
    """)
    return


@app.cell
def _(cancel_exact_zeros, e1, e2):
    nonzero_control = ((e1 | e1) + (e1 ^ e2)).named("c")
    control_view = cancel_exact_zeros(nonzero_control)
    control_view
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Limits and intent

    - The selector annotates retained operation provenance; it does not run a
      symbolic algebra rewrite looking for equivalent expressions elsewhere.
    - Literal zeros are not crossed out. The feature is meant to explain why
      an operation vanishes, not decorate already-written `0` values.
    - A subtree containing an unresolved named symbol cannot be re-evaluated
      from provenance alone and is skipped. Its self-contained descendants can
      still match; use `ga.subexpression(...)` when the intended symbolic
      identity should be selected explicitly.
    - Applying the annotator never changes the eager multivector value.
    """)
    return


if __name__ == "__main__":
    app.run()
