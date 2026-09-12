import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, DisplayOrder, dual, null_cga_blade_convention, outer_product, presets, scalar_product
    from galaga.cga import ConformalModel

    return (
        Algebra,
        ConformalModel,
        DisplayOrder,
        dual,
        gm,
        mo,
        np,
        null_cga_blade_convention,
        outer_product,
        presets,
        scalar_product,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CGA basis order: coordinates, display and signs

    **Three questions that must not be confused:**

    1. Which ordered vectors define the native coordinates?
    2. In what order should multivector terms be printed?
    3. Relative to which oriented volume do we take a dual?

    The new default is **origin-first**, $(e_o,e_1,\ldots,e_n,e_\infty)$.
    `Algebra(config=presets.cga(n, basis_order="euclidean-first"))` keeps the
    earlier coordinates. Both describe the same geometry after an explicit
    basis identification; their coefficient arrays are not interchangeable.

    Start with [native-null foundations](native_null_foundations.py) for the
    embedding and the comparison with an orthogonal $e_+,e_-$ construction.
    Here we work through the actual coordinate and sign consequences.
    """)
    return


@app.cell
def _(mo):
    dimension_control = mo.ui.dropdown([2, 3], value=3, label="Euclidean dimension")
    order_control = mo.ui.dropdown(["origin-first", "euclidean-first"], value="origin-first", label="Native basis")
    display_control = mo.ui.dropdown(
        ["grade-lexicographic", "native-mask"], value="grade-lexicographic", label="Display order only"
    )
    return dimension_control, display_control, order_control


@app.cell
def _(
    Algebra,
    ConformalModel,
    DisplayOrder,
    dimension_control,
    display_control,
    gm,
    mo,
    order_control,
    outer_product,
    presets,
):
    spatial_dimension = dimension_control.value
    selected_order = order_control.value
    _dimension = spatial_dimension + 2
    selected_display = (
        DisplayOrder(_dimension)
        if display_control.value == "grade-lexicographic"
        else DisplayOrder(_dimension, range(1 << _dimension))
    )
    algebra = Algebra(
        config=presets.cga(spatial_dimension, basis_order=selected_order),
        display_order=selected_display,
        expr=True,
    )
    model = ConformalModel(algebra)
    euclidean_volume = outer_product(*model.euclidean_basis_vectors())
    conformal_volume = model.origin ^ euclidean_volume ^ model.infinity
    orientation_ratio = float(conformal_volume / algebra.I)
    _basis = ", ".join(vector.display(target="ascii", content="value") for vector in algebra.basis_vectors())
    mo.vstack(
        [
            mo.hstack([dimension_control, order_control, display_control], wrap=True),
            gm.md(t"""
    ## 1. Read the native frame from its table

    Actual basis: **{_basis}**. The Gram table always follows native vector order.

    {algebra.bilinear_form_table():block}

    $$I_E={euclidean_volume.latex(content="value")!s}.$$

    $$I_C=e_o\\wedge I_E\\wedge e_\\infty={conformal_volume.latex(content="value")!s}.$$

    $$I_{{\\mathrm{{native}}}}={algebra.I.latex(content="value")!s}.$$

    Computed ratio $I_C/I_{{\\mathrm{{native}}}}$: **{orientation_ratio:g}**.
    Try both dimensions: moving the origin past $n$ Euclidean vectors has
    sign $(-1)^n$. Changing only the display selector cannot alter this ratio.
    """),
        ]
    )
    return (
        algebra,
        conformal_volume,
        euclidean_volume,
        model,
        selected_order,
        spatial_dimension,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. The same blade can have a different coefficient

    Consider the deliberately mixed-grade element
    $M=1+e_1+2(e_o\wedge e_1)+3I_E+4I_C$.
    In an origin-first frame, $e_o\wedge e_1$ is a positive native blade.
    In a Euclidean-first frame, the native blade is $e_1\wedge e_o$:
    the coefficient must be negative. In 2D this lower-grade sign changes
    even though the full pseudoscalar orientation does not!

    Below we reconstruct the same semantic expression in the other frame.
    A display-only view of the selected frame is shown afterwards.
    """)
    return


@app.cell
def _(
    Algebra,
    ConformalModel,
    algebra,
    conformal_volume,
    euclidean_volume,
    gm,
    mo,
    model,
    outer_product,
    presets,
    selected_order,
    spatial_dimension,
):
    other_order = "euclidean-first" if selected_order == "origin-first" else "origin-first"
    other_algebra = Algebra(config=presets.cga(spatial_dimension, basis_order=other_order))
    other_model = ConformalModel(other_algebra)
    _e1 = model.euclidean_basis_vectors()[0]
    _other_e1 = other_model.euclidean_basis_vectors()[0]
    origin_axis_blade = model.origin ^ _e1
    other_origin_axis_blade = other_model.origin ^ _other_e1
    _other_ie = outer_product(*other_model.euclidean_basis_vectors())
    _other_ic = other_model.origin ^ _other_ie ^ other_model.infinity
    mixed = algebra.identity + _e1 + 2 * origin_axis_blade + 3 * euclidean_volume + 4 * conformal_volume
    other_mixed = other_algebra.identity + _other_e1 + 2 * other_origin_axis_blade + 3 * _other_ie + 4 * _other_ic
    mo.vstack(
        [
            gm.md(t"""
    **Selected frame: {selected_order}**

    $$e_o\\wedge e_1={origin_axis_blade.latex(content="value")!s}.$$

    $$M={mixed.latex(content="value")!s}.$$
    """),
            gm.md(t"""
    **Other frame: {other_order}**

    $$e_o\\wedge e_1={other_origin_axis_blade.latex(content="value")!s}.$$

    $$M={other_mixed.latex(content="value")!s}.$$
    """),
        ]
    )
    return mixed, other_algebra, other_mixed, other_model


@app.cell
def _(DisplayOrder, algebra, dual, gm, mixed, mo, np):
    _natural = algebra.with_display_order(DisplayOrder(algebra.n))
    _storage = algebra.with_display_order(DisplayOrder(algebra.n, range(algebra.dim)))
    natural_display_value = _natural.multivector(mixed.data, expr=False)
    storage_display_value = _storage.multivector(mixed.data, expr=False)
    np.testing.assert_array_equal(natural_display_value.data, storage_display_value.data)
    assert dual(natural_display_value) == dual(storage_display_value)
    mo.vstack(
        [
            gm.md(t"""
    **Grade-then-lexicographic display**

    {natural_display_value:block}
    """),
            gm.md(t"""
    **Native-mask display of exactly the same coefficients**

    {storage_display_value:block}

    The arrays and duals agree exactly. The order of printed terms changes,
    not the order of factors inside a blade. An override is passed as
    `Algebra(config=..., display_order=DisplayOrder(...))` or applied via
    `with_display_order(...)`.
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Worked conversion: extend the vector map with wedges

    Merely copying `M.data` into the other algebra would reinterpret the masks.
    Instead, identify vectors by their semantic roles, map each native blade
    to the wedge of its mapped vectors, then apply that linear map to the
    full coefficient array. This handles the permutation signs at **every grade**.

    Read the code in the next cell: its columns are computed exterior
    products, not a hardcoded sign table. This is an explicit teaching
    construction, not a new library conversion API.
    """)
    return


@app.cell
def _(algebra, gm, mixed, np, other_algebra, other_mixed):
    _roles = {ref.mask: role for role, ref in algebra.presentation.blades.roles}
    _images = tuple(other_algebra.blade(_roles[1 << index]) for index in range(algebra.n))
    _columns = []
    for _mask in range(algebra.dim):
        _image = other_algebra.identity
        for _index, _vector in enumerate(_images):
            if _mask & (1 << _index):
                _image = _image ^ _vector
        _columns.append(_image.data)
    exterior_map = np.column_stack(_columns)
    converted_mixed = other_algebra.multivector(exterior_map @ mixed.data)
    conversion_residual = float(np.linalg.norm(converted_mixed.data - other_mixed.data))
    copied_mixed = other_algebra.multivector(mixed.data)
    assert converted_mixed == other_mixed
    assert copied_mixed != other_mixed
    gm.md(t"""
    **Correctly converted**

    {converted_mixed:block}

    Agreement with the independently reconstructed expression: {conversion_residual:.2e}.

    **Incorrectly copied without conversion**

    {copied_mixed:block}

    The second expression is a different element. Persist the basis order,
    Gram matrix and normalization with coefficient arrays. To retain older
    arrays unchanged, select the Euclidean-first compatibility preset.
    """)
    return (exterior_map,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. A directed flat and a unit round: exact dual signs

    In 2D take the directed line through $(0,0)$ and $(1,0)$.
    In 3D take the directed plane through $(0,0,0)$, $(1,0,0)$ and $(0,1,0)$.
    Wedge those lifted points, **in that order**, with infinity.
    Its IPNS normal is proportional to the last Euclidean axis; we compute
    the signed factor, not merely test that it has the same locus.

    For the unit circle/sphere, wedge the lifted points
    $e_1,e_2,\ldots,e_n,-e_1$ in that order. Compare its dual with
    $S=e_o-\tfrac12e_\infty$. Both point order and dual convention affect scale.

    Galaga offers different operations:

    - `dual(A)` is $AI_{\mathrm{native}}^{-1}$.
    - `model.dual(A)` is **right Hodge duality**, not a synonym.

    Their agreement in this 2D example does not make them interchangeable:
    switch to 3D and inspect the computed signs. A global minus sign does
    not change the zero set, but it matters for a chosen normal/orientation
    and for signed evaluations away from the locus.
    """)
    return


@app.cell
def _(
    algebra,
    dual,
    exterior_map,
    gm,
    mo,
    model,
    np,
    other_algebra,
    other_model,
    outer_product,
    scalar_product,
    spatial_dimension,
):
    _zero = (0,) * spatial_dimension
    _axes = tuple(tuple(int(i == j) for i in range(spatial_dimension)) for j in range(spatial_dimension))
    flat_coordinates = (_zero, *_axes[:-1])
    round_coordinates = (*_axes, (-1, *((0,) * (spatial_dimension - 1))))
    flat = outer_product(*(model.up(point) for point in flat_coordinates), model.infinity)
    round_blade = outer_product(*(model.up(point) for point in round_coordinates))
    other_flat = outer_product(*(other_model.up(point) for point in flat_coordinates), other_model.infinity)
    other_round = outer_product(*(other_model.up(point) for point in round_coordinates))
    normal = model.euclidean_basis_vectors()[-1]
    normalized_sphere = model.origin - 0.5 * model.infinity
    flat_dual, flat_hodge = dual(flat), model.dual(flat)
    round_dual, round_hodge = dual(round_blade), model.dual(round_blade)
    flat_dual_factor = float(scalar_product(flat_dual, normal))
    flat_hodge_factor = float(scalar_product(flat_hodge, normal))
    round_dual_factor = float(model.weight(round_dual))
    round_hodge_factor = float(model.weight(round_hodge))
    assert flat_dual == flat_dual_factor * normal
    assert flat_hodge == flat_hodge_factor * normal
    assert round_dual == round_dual_factor * normalized_sphere
    assert round_hodge == round_hodge_factor * normalized_sphere
    mapped_native_volume = other_algebra.multivector(exterior_map @ algebra.I.data)
    orientation_map_factor = float(mapped_native_volume / other_algebra.I)
    for _source, _target in ((flat, other_flat), (round_blade, other_round)):
        np.testing.assert_allclose(exterior_map @ _source.data, _target.data, rtol=0, atol=1e-12)
        np.testing.assert_allclose(
            exterior_map @ dual(_source).data,
            (orientation_map_factor * dual(_target)).data,
            rtol=0,
            atol=1e-12,
        )
        np.testing.assert_allclose(
            exterior_map @ model.dual(_source).data,
            (orientation_map_factor * other_model.dual(_target)).data,
            rtol=0,
            atol=1e-12,
        )
    _probe = model.up(_axes[-1])
    signed_probe = float(scalar_product(_probe, flat_dual))
    mo.vstack(
        [
            gm.md(t"""
    **Directed line / plane**

    $$F={flat.latex(content="value")!s}.$$

    $$\\operatorname{{dual}}(F)={flat_dual.latex(content="value")!s}.$$

    $$\\operatorname{{Hodge}}(F)={flat_hodge.latex(content="value")!s}.$$

    Signed normal factors: **{flat_dual_factor:g}** and **{flat_hodge_factor:g}**.
    Evaluating the inverse-pseudoscalar dual at the probe on the positive
    last axis gives **{signed_probe:g}**. Swapping two defining points
    would reverse this sign.
    """),
            gm.md(t"""
    **Unit circle / sphere**

    $$C={round_blade.latex(content="value")!s}.$$

    $$\\operatorname{{dual}}(C)={round_dual.latex(content="value")!s}.$$

    $$\\operatorname{{Hodge}}(C)={round_hodge.latex(content="value")!s}.$$

    Signed scale factors relative to $S=e_o-\\tfrac12 e_\\infty$:
    **{round_dual_factor:g}** and **{round_hodge_factor:g}**.

    Under the explicit map to the other native frame, the native duality
    orientation factor is **{orientation_map_factor:g}**. The assertions
    verify this for both operations and both geometric objects.
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. What the tables promise

    Gram and vector-only wedge tables use the **actual native vector order**.
    Full wedge tables use the active multivector display order, including the
    scalar `1`. Try the display selector: the full table below changes order,
    but no product changes sign merely because its row moves.

    We use a tiny 1D conformal model here so the full table stays readable:
    three basis vectors give eight blades. A full 3D CGA table has 32 rows
    and 32 columns.
    """)
    return


@app.cell
def _(Algebra, DisplayOrder, display_control, gm, mo, presets, selected_order):
    _display = DisplayOrder(3) if display_control.value == "grade-lexicographic" else DisplayOrder(3, range(8))
    table_algebra = Algebra(config=presets.cga(1, basis_order=selected_order), display_order=_display)
    vector_table = table_algebra.wedge_product_table(colour=True)
    full_table = table_algebra.wedge_product_table(full=True, colour=True)
    mo.vstack(
        [
            gm.md(t"""
    **Native vector axes**

    {vector_table:block}
    """),
            gm.md(t"""
    **All blades in the selected display order**

    {full_table:block}
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Names and local bindings: no suppressed signs

    The default preset displays the native pseudoscalar as $I$.
    Enable paired model names to display $I_E$ and $I_C$ (Python names
    `IE` and `IC`, matching the compact `e1` style), or name the
    null-plane bivector $E=e_o\wedge e_\infty$ independently.
    An explicit PSS override names the **native** pseudoscalar and takes
    precedence over the automatic $I$/$I_C$ choice.

    $I_E\wedge E=(-1)^n I_C$ is an exact signed identity. In origin-first 3D
    this is $I_E\wedge E=-I$, not $I$. $I_C$ is the full conformal volume,
    so $I_C\wedge I_E=0$. The expanded expressions below expose every sign.
    """)
    return


@app.cell
def _(mo):
    model_names_control = mo.ui.checkbox(value=False, label="model_pseudoscalars")
    null_name_control = mo.ui.checkbox(value=False, label="pseudoscalar_null")
    pss_control = mo.ui.dropdown(["Automatic", "I", "J"], value="Automatic", label="Native PSS override")
    return model_names_control, null_name_control, pss_control


@app.cell
def _(
    Algebra,
    ConformalModel,
    gm,
    mo,
    model_names_control,
    null_cga_blade_convention,
    null_name_control,
    outer_product,
    presets,
    pss_control,
    selected_order,
    spatial_dimension,
):
    _pss = None if pss_control.value == "Automatic" else pss_control.value
    naming_algebra = Algebra(
        config=presets.cga(
            spatial_dimension,
            basis_order=selected_order,
            model_pseudoscalars=model_names_control.value,
            pseudoscalar_null=null_name_control.value,
            pss=_pss,
        )
    )
    _model = ConformalModel(naming_algebra)
    named_euclidean_volume = outer_product(*_model.euclidean_basis_vectors())
    named_null_plane = _model.origin ^ _model.infinity
    named_conformal_volume = _model.origin ^ named_euclidean_volume ^ _model.infinity
    named_volume_product = named_euclidean_volume ^ named_null_plane
    assert named_volume_product == (-1) ** spatial_dimension * named_conformal_volume
    assert named_conformal_volume ^ named_euclidean_volume == 0
    _expanded = naming_algebra.with_blades(null_cga_blade_convention(spatial_dimension, basis_order=selected_order))
    _expanded_ie = _expanded.multivector(named_euclidean_volume.data)
    _expanded_e = _expanded.multivector(named_null_plane.data)
    _expanded_ic = _expanded.multivector(named_conformal_volume.data)
    _local_names = ", ".join(name for name in naming_algebra.locals() if name.startswith("I") or name in ("E", "J"))
    naming_small_algebra = Algebra(
        config=presets.cga(
            1,
            basis_order=selected_order,
            model_pseudoscalars=model_names_control.value,
            pseudoscalar_null=null_name_control.value,
            pss=_pss,
        )
    )
    _axis = naming_small_algebra.blade("e1")
    assert _axis.latex(content="value") == r"e_{1}"
    mo.vstack(
        [
            mo.hstack([model_names_control, null_name_control, pss_control], wrap=True),
            gm.md(rt"""
    **Selected names and their expanded blade values**

    $$I_E={named_euclidean_volume.latex(content="value")!s}={_expanded_ie.latex(content="value")!s}.$$

    $$E={named_null_plane.latex(content="value")!s}={_expanded_e.latex(content="value")!s}.$$

    $$I_C={named_conformal_volume.latex(content="value")!s}={_expanded_ic.latex(content="value")!s}.$$

    $$I_{{\mathrm{{native}}}}={naming_algebra.I.latex(content="value")!s}={_expanded.I.latex(content="value")!s}.$$

    $$I_E\wedge E={named_volume_product.latex(content="value")!s}.$$

    Canonical volume names in `locals()`: **{_local_names}**.
    `alg.I` and `alg.blade("I")` always return the native pseudoscalar.
    With model naming enabled, `blade("IC")` returns the oriented conformal
    volume even when the preferred top-grade label is a custom name.

    `locals()` includes canonical Python-safe names, not every alias.
    Custom `local_names=` policies and blade-only presentation overrides remain
    independent. Changing display order does not change any local binding.

    **The 1D axis stays e1**

    In 1D CGA, $I_E=e_1$: its displayed name remains ${_axis.latex(content="value")!s}$,
    and `locals()["e1"]` remains available. When model names are enabled,
    `blade("IE")` is a lookup alias only.

    Here is the full small 1D CGA table with the same naming choices. Its
    headings are native blades: a negative $I_C$ heading is intentional when
    that native blade has the opposite orientation.

    {naming_small_algebra.wedge_product_table(full=True, colour=True):block}
    """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Takeaways and boundaries

    - Use the origin-first default when starting new native-null work.
    - Select Euclidean-first explicitly when retaining older coordinates or
      formulas tied to that orientation.
    - Display overrides do not change coordinates, products or dual signs.
    - Compare frames through semantic roles and an exterior basis map.
    - State the dual operation and point order when interpreting signed results.

    Orthogonal CGA keeps $(e_1,\ldots,e_n,e_+,e_-)$; omit `basis_order` for
    `presets.cga(..., frame="orthogonal")`. Explicit null-order choices there
    are rejected. Lengyel CGA, RGA and quaternion presets keep their existing
    conventions and deliberate display orders.

    [ADR-134](../../docs/adrs/134-origin-first-native-null-cga.md) records the
    decision. [CGA via its Gram matrix](../matrix/cga_via_gram_matrix.py) continues
    to compact matrix roundtrips; changing native GA coordinates is distinct
    from a similarity change between matrix representations.
    """)
    return


if __name__ == "__main__":
    app.run()
