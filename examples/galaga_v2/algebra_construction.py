import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga import (
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
    return (
        euclidean_counts,
        oblique_metric,
        projective_signature,
        spacetime_signature,
    )


@app.cell
def _(
    euclidean_counts,
    gm,
    oblique_metric,
    projective_signature,
    spacetime_signature,
):
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
    _euclidean_model = Algebra(config=p_euclidean(spatial_dim=3), display=_full)
    spacetime_model = Algebra(config=p_sta("mostly-minus"), display=_full)
    projective_model = Algebra(config=p_pga(spatial_dim=3), display=_full)
    conformal_model = Algebra(config=p_cga(spatial_dim=3, frame="null"), display=_full)
    rga_model = Algebra(config=p_rga(), display=_full)
    return conformal_model, projective_model, rga_model, spacetime_model


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
    ## STA names describe signed products

    The default STA convention keeps gamma words. Opt into `sigmas=True` to
    name $\sigma_k=\gamma_k\gamma_0$ and $i\sigma_k=I\gamma_k\gamma_0$;
    `pseudovectors=True` names $i\gamma_k=I\gamma_k$, where
    $I=\gamma_0\gamma_1\gamma_2\gamma_3$.

    These are definitions of products, not aliases for unsigned storage
    slots. In particular, $\gamma_0\wedge\gamma_1=-\sigma_1$ in either
    orthogonal frame below. The sign of the spatial trivector expressed as
    $i\gamma_0$ changes when the ordered metric changes.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy, gm, p_sta):
    _minus = Algebra(
        config=p_sta("mostly-minus", sigmas=True, pseudovectors=True),
        display=DisplayPolicy(content="full"),
    )
    _plus = Algebra(
        config=p_sta("mostly-plus", sigmas=True, pseudovectors=True),
        display=DisplayPolicy(content="full"),
    )
    _m0, _m1, _m2, _m3 = _minus.basis_vectors(expr=True)
    _p0, _p1, _p2, _p3 = _plus.basis_vectors(expr=True)
    _minus_sigma = _m1 * _m0
    _plus_sigma = _p1 * _p0
    _minus_spatial = _m1 ^ _m2 ^ _m3
    _plus_spatial = _p1 ^ _p2 ^ _p3
    _native_bivector = _m0 ^ _m1

    assert _minus.blade("s1") == _minus_sigma
    assert _plus.blade("s1") == _plus_sigma
    assert _minus.blade("g0g1") == _native_bivector == -_minus_sigma
    assert _minus.locals()["ig0"] == _minus.I * _m0
    assert _plus.locals()["ig0"] == _plus.I * _p0

    gm.md(rt"""
    Both rows are computed from their own metric:

    | Ordered metric | Relative vector | Spatial trivector |
    |---|---|---|
    | $(+,-,-,-)$ | {_minus_sigma} | {_minus_spatial} |
    | $(-,+,+,+)$ | {_plus_sigma} | {_plus_spatial} |

    The canonical bivector and the named relative vector have opposite
    orientations: {_native_bivector}.

    `blade("s1")` and `blade("σ₁")` return the relative vector.
    `blade("g0g1")` retains the positive canonical gamma word; these
    lookups must not be conflated. The Python local `ig0` is the actual
    computed product $I\gamma_0$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `p_sta` derives the signs from its own time-first metric. If configuring
    only presentation, use
    `spacetime_blade_convention(signature=algebra.basis_squares, sigmas=True)`
    **only for an orthogonal frame whose basis squares are all ±1**.
    The plain gamma convention needs no metric; the signed options require
    the actual ordered signature.

    `Algebra(3, 1)` orders its metric $(+,+,+,-)$, so it is not the
    time-first mostly-plus preset. In a general Gram frame, products can
    contain multiple blades or non-unit coefficients: keep plain blade
    labels and give those computed multivectors their own names.
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
    return


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A blade word is a label, not a product parser

    A complete blade convention supplies one label per native exterior mask,
    including the scalar. Its ASCII, Unicode and LaTeX spellings can differ.
    Here the ASCII lookup key `ab` denotes $a\wedge b$; we use explicit wedge
    glyphs in the mathematical targets to make that meaning visible.

    In an orthogonal basis, the geometric product of distinct basis vectors
    happens to equal their exterior product. In a general Gram frame,
    $ab=G_{12}+a\wedge b$. A three-vector geometric word can also contain a
    vector part. Merely choosing names cannot remove those metric terms.
    """)
    return


@app.cell
def _(Algebra, gm):
    from galaga_matrix import MatrixRepr

    import galaga as _ga

    naming_algebra = Algebra(gram=((2, 0.5, -0.25), (0.5, -1, 0.75), (-0.25, 0.75, 3)))
    naming_gram = MatrixRepr(naming_algebra.gram).name(latex="G")
    _names = (_ga.Name("a", "𝐚", r"\mathbf{a}"), _ga.Name("b", "𝐛", r"\mathbf{b}"), _ga.Name("c", "𝐜", r"\mathbf{c}"))
    _labels = {}
    for _mask in range(naming_algebra.dim):
        _parts = [_name for _index, _name in enumerate(_names) if _mask & (1 << _index)]
        _labels[_mask] = _ga.Name(
            "".join(_name.ascii for _name in _parts) or "1",
            "∧".join(_name.unicode for _name in _parts) or "1",
            r" \wedge ".join(_name.latex for _name in _parts) or "1",
        )
    naming_view = naming_algebra.with_blades(_ga.BladeConvention(naming_algebra.n, _labels))
    naming_a, naming_b, naming_c = naming_view.basis_vectors(expr=True)
    naming_plane = naming_view.blade("ab")
    naming_volume = naming_view.blade("abc")
    naming_gp = naming_a * naming_b
    naming_triple = naming_a * naming_b * naming_c
    naming_local_view = naming_view.with_local_names(
        _ga.LocalNamePolicy.from_convention(naming_view.presentation.blades)
    )
    _shared_numeric = naming_view.numeric is naming_algebra.numeric
    _local_before = "a" in naming_view.locals()
    _local_after = "a" in naming_local_view.locals()
    _cross_term = naming_view.gram[0, 1]

    gm.md(rt"""
    Work in this Gram frame:

    {naming_gram}

    The presentation view shares its numeric algebra: `{_shared_numeric!s}`.

    | Construction | Meaning | Computed result |
    |---|---|---|
    | `blade("ab")` | Native exterior plane | {naming_plane:value} |
    | `a * b` | Geometric product, with scalar term {_cross_term} | {naming_gp:full} |
    | `blade("abc")` | Native exterior volume | {naming_volume:value} |
    | `a * b * c` | Geometric word, possibly mixed grade | {naming_triple:full} |

    `blade("ab")` is a configured lookup, not evaluation of the Python text
    `a*b`. Use `a ^ b` for the exterior product and `a * b` for the geometric
    product.

    Display labels and Python locals are independent. Replacing blade labels
    leaves `"a" in view.locals()` equal to `{_local_before!s}`. Explicitly
    applying `LocalNamePolicy.from_convention(...)` makes it
    `{_local_after!s}`, without changing the numeric algebra.
    """)
    return


if __name__ == "__main__":
    app.run()
