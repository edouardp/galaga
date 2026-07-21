import marimo

__generated_with = "0.23.11"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _repository = Path(__file__).resolve().parent.parent.parent
    for _source in (
        _repository,
        _repository / "packages" / "galaga",
        _repository / "packages" / "galaga_marimo",
    ):
        _path = str(_source)
        if _path not in sys.path:
            sys.path.insert(0, _path)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga.facade import (
        Algebra,
        DisplayPolicy,
        Notation,
        geometric_product,
        p_cga,
        p_euclidean,
        p_pga,
        p_rga,
        p_sta,
    )

    return (
        Algebra,
        DisplayPolicy,
        Notation,
        geometric_product,
        gm,
        mo,
        np,
        p_cga,
        p_euclidean,
        p_pga,
        p_rga,
        p_sta,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Constructing a Galaga 2 algebra

    **Claim:** constructing a metric and choosing how to present it are
    separate decisions. Use a direct metric constructor when the basis is the
    subject of the calculation; use a preset when the algebra represents a
    conventional geometric model.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The facade owns two layers

    A `galaga.facade.Algebra` contains:

    1. a presentation-free `galaga.core.Algebra`, determined by its Gram
       matrix; and
    2. an immutable `PresentationConfig`, which controls blade labels,
       notation, local names, display order, and numeric display policy.

    Changing the metric creates a different algebra. Changing presentation
    creates only a different view of the same numeric algebra.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Direct metric constructors

    There are three primary forms:

    | Form | Meaning |
    |---|---|
    | `Algebra(p, q=0, r=0)` | Counts of positive, negative, and null basis vectors. Null vectors are stored first. |
    | `Algebra(signature=(...))` | An explicitly ordered diagonal metric using `+1`, `-1`, and `0`. |
    | `Algebra(gram=matrix)` | Any finite real symmetric Gram matrix, including oblique and native-null bases. |

    `sig=` is a short alias for `signature=`. The facade also accepts a single
    positional signature tuple for migration compatibility, but new code is
    clearest with the explicit `signature=` spelling.
    """)
    return


@app.cell
def _(Algebra, np):
    euclidean_counts = Algebra(3)
    spacetime_signature = Algebra(signature=(1, -1, -1, -1), id="sta-example")
    projective_signature = Algebra(signature=(1, 1, 1, 0))
    oblique_metric = Algebra(
        gram=np.array(
            [
                [1.0, 0.25],
                [0.25, 1.0],
            ]
        )
    )
    return euclidean_counts, oblique_metric, projective_signature, spacetime_signature


@app.cell
def _(euclidean_counts, gm, oblique_metric, projective_signature, spacetime_signature):
    _euclidean_signature = euclidean_counts.signature
    _spacetime_inertia = spacetime_signature.inertia
    _projective_inertia = projective_signature.inertia
    _oblique_gram = oblique_metric.gram
    _oblique_orthogonal = oblique_metric.is_orthogonal_basis

    gm.md(rt"""
    - `Algebra(3)` has ordered signature `{_euclidean_signature!s}`.
    - The spacetime metric has inertia `{_spacetime_inertia!s}`.
    - The projective metric has inertia `{_projective_inertia!s}`.
    - The oblique basis has Gram matrix

      ```text
      {_oblique_gram!s}
      ```

      and `is_orthogonal_basis == {_oblique_orthogonal!s}`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The optional `id=` is diagnostic metadata. `product_backend=` can force
    `"diagonal"`, `"packed"`, `"lazy"`, or `"reference"`, but normal code
    should leave its default as `"auto"`.

    Metric forms are mutually exclusive: do not combine `gram=` with a
    signature or with `p`, `q`, and `r`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Complete presets

    A preset configures more than a signature. It supplies a deterministic
    numeric definition, blade convention, notation, local-name policy,
    display order, and optional semantic model roles.

    The `p_*` functions return inspectable preset objects. Passing one through
    `config=` expands the complete configuration exactly once.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, p_cga, p_euclidean, p_pga, p_rga, p_sta):
    _full = DisplayPolicy(content="full")
    euclidean_model = Algebra(config=p_euclidean(spatial_dim=3), display=_full)
    spacetime_model = Algebra(config=p_sta("mostly-minus"), display=_full)
    projective_model = Algebra(config=p_pga(spatial_dim=3), display=_full)
    conformal_model = Algebra(config=p_cga(spatial_dim=3, frame="null"), display=_full)
    rga_model = Algebra(config=p_rga(), display=_full)
    return conformal_model, euclidean_model, projective_model, rga_model, spacetime_model


@app.cell
def _(conformal_model, gm, projective_model, rga_model, spacetime_model):
    _gamma_0, _gamma_1, _, _ = spacetime_model.basis_vectors(expr=True)
    _pga_e1, _, _, _pga_e0 = projective_model.basis_vectors(expr=True)
    _cga_e1, _, _, _origin, _infinity = conformal_model.basis_vectors(expr=True)
    _rga_e1, _, _, _rga_e4 = rga_model.basis_vectors(expr=True)

    gm.md(rt"""
    The model-specific basis vocabulary is immediately available:

    | Preset | Representative configured blades |
    |---|---|
    | spacetime | {_gamma_0}, {_gamma_1} |
    | projective | {_pga_e1}, {_pga_e0} |
    | conformal native-null | {_cga_e1}, {_origin}, {_infinity} |
    | Lengyel RGA | {_rga_e1}, {_rga_e4} |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `config=` already defines the metric, so combining it with `gram=`, a
    signature, or `p/q/r` is deliberately an error. Presentation components
    are different: they may be overridden independently without redefining
    the algebra.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, Notation, geometric_product, gm, p_euclidean):
    teaching_algebra = Algebra(
        config=p_euclidean(2),
        notation=Notation.functional(short=True),
        display=DisplayPolicy(content="full", coefficient_precision=4),
    )
    _teaching_e1, _teaching_e2 = teaching_algebra.basis_vectors(expr=True)
    _teaching_product = geometric_product(_teaching_e1, _teaching_e2).named("B")

    gm.md(rt"""
    Here the Euclidean preset still defines the numeric algebra, while two
    presentation components are overridden at construction:

    {_teaching_product}
    """)
    return (teaching_algebra,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Constructor decision rule

    - Use **counts** for a conventional diagonal `Cl(p, q, r)` where the
      null-first basis order is acceptable.
    - Use an explicit **signature** when diagonal basis order matters.
    - Use a **Gram matrix** for oblique or native-null bases.
    - Use a complete **preset** for PGA, CGA, STA, RGA, complex, quaternion,
      exterior, and other model-specific conventions.
    - Override `presentation=`, `blades=`, `notation=`, `local_names=`,
      `display_order=`, or `display=` only when fine-grained control is the
      point.
    """)
    return


if __name__ == "__main__":
    app.run()
