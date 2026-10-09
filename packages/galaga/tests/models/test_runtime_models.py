"""Model contracts derived from products, metric roles, and incidence."""

from dataclasses import FrozenInstanceError, replace

import numpy as np
import pytest

from galaga import (
    Algebra,
    AlgebraDefinition,
    DisplayOrder,
    ModelConfig,
    Multivector,
    antimetric_apply,
    antireverse,
    antiwedge,
    complement,
    geometric_antiproduct,
    left_complement,
    metric_apply,
    outer_product,
    presets,
    reverse,
    scalar_product,
    squared,
)
from galaga.blades import BladeRef
from galaga.expression import evaluate
from galaga.models import (
    BulkWeightModel,
    ConformalEmbeddingModel,
    ConformalModel,
    ConformalSpacetimeModel,
    PGAModel,
    PointModel,
    RigidModel,
)

CASES = (
    (RigidModel, presets.rga(), (1.0, -2.0, 3.0)),
    (PGAModel, presets.pga(2), (1.0, -2.0)),
    (PGAModel, presets.pga(3), (1.0, -2.0, 3.0)),
    (ConformalModel, presets.cga(2), (1.0, -2.0)),
    (ConformalModel, presets.cga(3), (1.0, -2.0, 3.0)),
    (ConformalSpacetimeModel, presets.csta(), (2.0, 1.0, -2.0, 3.0)),
)


def model_for(cls, preset, *, expr=False):
    return cls(Algebra(config=preset, expr=expr, user_config_files=False))


@pytest.mark.parametrize("expression_form", ("operator", "expanded"))
@pytest.mark.parametrize(
    ("cls", "preset", "coords", "result_type"),
    (
        (ConformalModel, presets.cga(2), (1.0, -2.0), Multivector),
        (ConformalSpacetimeModel, presets.csta(), (2.0, 1.0, 0.0, 0.0), float),
    ),
)
def test_conformal_weight_preserves_public_return_type_and_metric_value(
    cls, preset, coords, result_type, expression_form
):
    model = model_for(cls, preset, expr=True)
    point = -3 * model.point(coords)
    weight = model.weight(point, expression_form=expression_form)
    assert isinstance(weight, result_type)
    expected = float(scalar_product(point, model.infinity)) / model.null_pair
    assert float(weight) == expected
    np.testing.assert_allclose(model.coordinates(model.homogenize(point)), coords)
    if isinstance(weight, Multivector):
        assert weight.expr is not None
        assert evaluate(weight.expr, algebra=model.algebra) == weight


@pytest.mark.parametrize(("cls", "preset", "coords"), CASES)
def test_point_protocol_round_trip_and_immutable_coordinates(cls, preset, coords):
    model = model_for(cls, preset)
    point = model.point(coords)
    assert isinstance(model, PointModel)
    assert isinstance(model, BulkWeightModel)
    assert isinstance(model, ConformalEmbeddingModel) == (cls in {ConformalModel, ConformalSpacetimeModel})
    np.testing.assert_allclose(model.coordinates(-3 * point), coords)
    assert not model.coordinates(point).flags.writeable
    classification = model.classify(point)
    assert classification.model in {"pga", "rga", "cga", "csta"}
    with pytest.raises(FrozenInstanceError):
        classification.kind = "changed"


@pytest.mark.parametrize(("cls", "preset", "coords"), CASES)
def test_ownership_requires_facade_identity_even_for_a_shared_numeric_algebra(cls, preset, coords):
    model = model_for(cls, preset)
    other = model.algebra.with_display_order(DisplayOrder(model.algebra.n, tuple(reversed(range(model.algebra.dim)))))
    assert other.numeric is model.algebra.numeric
    with pytest.raises(ValueError, match="model algebra"):
        model.classify(other.blade(1))
    with pytest.raises(ValueError, match="model algebra"):
        model.bulk_part(other.blade(1))


@pytest.mark.parametrize(("cls", "preset", "coords"), CASES)
@pytest.mark.parametrize("scale", (1e-100, -3.0, 1e100))
def test_classification_is_projectively_invariant(cls, preset, coords, scale):
    model = model_for(cls, preset)
    point = model.point(coords)
    expected = model.classify(point)
    actual = model.classify(scale * point)
    assert (actual.kind, actual.finite, actual.simple) == (expected.kind, expected.finite, expected.simple)


@pytest.mark.parametrize(("cls", "preset", "coords"), CASES)
def test_invalid_tolerances_coordinates_and_nonfinite_values(cls, preset, coords):
    model = model_for(cls, preset)
    point = model.point(coords)
    for atol in (-1, np.nan, np.inf):
        with pytest.raises(ValueError):
            model.classify(point, atol=atol)
        with pytest.raises(ValueError):
            model.coordinates(point, atol=atol)
    with pytest.raises(TypeError):
        model.classify(point, atol=True)
    with pytest.raises(ValueError):
        model.point((np.inf, *coords[1:]))
    with pytest.raises(TypeError):
        model.point((True, *coords[1:]))
    with pytest.raises(ValueError):
        model.classify(model.algebra.multivector(np.full(model.algebra.dim, np.nan)))


@pytest.mark.parametrize("n", (2, 3))
def test_projective_split_and_pga_incidence_from_actual_metric(n):
    model = model_for(PGAModel, presets.pga(n), expr=True)
    coordinates = tuple(range(1, n + 1))
    point = model.point(coordinates)
    homogeneous = left_complement(point)
    refs = (*model._euclidean_refs, model._projective_ref)
    vectors = tuple(model.algebra.blade(ref) for ref in refs)
    expected = sum(
        (coefficient * vector for coefficient, vector in zip((*coordinates, 1), vectors, strict=True)),
        model.algebra.scalar(0),
    )
    assert homogeneous.almost_equal(expected)
    # Every hyperplane through the point has zero outer incidence.
    for i in range(n):
        normal = tuple(int(i == j) for j in range(n))
        plane = model.plane((*normal, -coordinates[i]))
        assert not np.any(model.meet(plane, point).data)
    for mask in range(model.algebra.dim):
        blade = model.algebra.blade(mask)
        bulk, weight = model.bulk_part(blade), model.weight_part(blade)
        assert bulk == metric_apply(blade)
        assert weight == antimetric_apply(blade)
        assert bulk + weight == blade
        assert model.bulk_part(bulk) == bulk
        assert model.weight_part(weight) == weight
        assert model.bulk_part(weight) == model.weight_part(bulk) == 0
        for result in (bulk, weight):
            assert result.expr is not None
            assert evaluate(result.expr, algebra=model.algebra) == result
    assert evaluate(point.expr, algebra=model.algebra) == point


def test_rga_split_restores_model_interpretation_without_generic_aliases():
    model = model_for(RigidModel, presets.rga(), expr=True)
    value = model.algebra.multivector(np.arange(model.algebra.dim))
    assert model.bulk_part(value) + model.weight_part(value) == value
    assert model.bulk_part(value) == metric_apply(value)
    assert model.weight_part(value) == antimetric_apply(value)


@pytest.mark.parametrize("n", (2, 3))
def test_pga_joins_meets_finite_and_ideal_classifications(n):
    model = model_for(PGAModel, presets.pga(n))
    a = model.point((0,) * n)
    b = model.point((1,) * (n))
    line = model.join(a, b)
    assert model.join(a, b) == antiwedge(a, b)
    assert model.classify(a).kind == "point"
    assert model.classify(model.point((1,) * n, weight=0)).kind == "ideal point"
    assert model.classify(line).kind == "line"
    assert model.meet(a, line) == outer_product(a, line)
    assert model.classify(model.projective).kind == ("ideal line" if n == 2 else "ideal plane")
    with pytest.raises(ValueError, match="ideal"):
        model.coordinates(model.point((1,) * n, weight=0))


def test_rga_classification_and_model_selected_products():
    model = model_for(RigidModel, presets.rga())
    a, b, c = [model.point(coords) for coords in ((0, 0, 0), (1, 0, 0), (0, 1, 0))]
    line = model.join(a, b)
    plane = model.join(line, c)
    for value, kind in (
        (a, "point"),
        (line, "line"),
        (plane, "plane"),
        (model.projective, "point"),
        (model.algebra.I, "antiscalar"),
    ):
        assert model.classify(value).kind == kind
    assert line == outer_product(a, b)
    assert model.meet(line, plane) == antiwedge(line, plane)
    e1, e2, e3 = model.euclidean_basis_vectors()
    assert model.classify(e1).kind == "ideal point"
    assert model.classify(e1 ^ e2).kind == "ideal line"
    assert model.classify((e1 ^ e2) + (e3 ^ model.projective)).simple is False
    motor = model.antiscalar + 0.5 * (e2 ^ e3)
    assert model.classify(motor).kind == "motor"
    assert model.classify(7 * motor).kind == "motor"


def test_pga_and_rga_motion_contracts_use_their_actual_products():
    pga = model_for(PGAModel, presets.pga())
    rga = model_for(RigidModel, presets.rga())
    e1, _, _ = pga.euclidean_basis_vectors()
    _, e2, e3 = rga.euclidean_basis_vectors()
    # Signs are established by the plane equation and each signed role frame.
    p_motor = 1 + 0.75 * (e1 ^ pga.projective)
    r_motor = rga.antiscalar + 0.75 * (e2 ^ e3)
    p, q = pga.point((-1, 0.75, 0)), rga.point((-1, 0.75, 0))
    p_moved, q_moved = pga.transform(p, p_motor), rga.transform(q, r_motor)
    assert p_moved == p_motor * p * reverse(p_motor)
    assert q_moved == geometric_antiproduct(geometric_antiproduct(r_motor, q), antireverse(r_motor))
    np.testing.assert_allclose(pga.coordinates(p_moved), rga.coordinates(q_moved))
    for model, point, motor in ((pga, p, p_motor), (rga, q, r_motor)):
        with pytest.raises(ValueError, match="normalized"):
            model.transform(point, 2 * motor)


@pytest.mark.parametrize("n", (2, 3))
def test_cga_direct_and_dual_families_are_runtime_owned(n):
    model = model_for(ConformalModel, presets.cga(n))
    offsets = [(1, 0), (0, 1), (-1, 0)] if n == 2 else [(1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, 0, 1)]
    points = [model.point(p) for p in offsets]
    pair, circle = outer_product(*points[:2]), outer_product(*points[:3])
    families = [
        (points[0], "round point"),
        (points[0] ^ model.infinity, "flat point"),
        (pair, "dipole"),
        (pair ^ model.infinity, "line"),
        (circle, "circle"),
    ]
    if n == 3:
        families += [(circle ^ model.infinity, "plane"), (outer_product(*points), "sphere")]
    for value, kind in families:
        direct = model.classify(value)
        assert direct.kind == kind
        assert direct.simple is True
        if value.homogeneous_grade() > 1:
            dual = model.classify(model.dual(value), representation="dual")
            assert dual.kind == kind
            assert dual.representation == "dual"
    assert model.classify(model.infinity).kind == "point at infinity"
    assert model.classify(model.euclidean_basis_vectors()[0]).kind == ("dual line" if n == 2 else "dual plane")
    assert model.classify(model.algebra.I).kind == "pseudoscalar"
    with pytest.raises(ValueError, match="representation"):
        model.classify(points[0], representation="bad")


@pytest.mark.parametrize(("cls", "preset", "coords"), [CASES[3], CASES[4], CASES[5]])
def test_conformal_shared_operations_against_algebra_and_expression_replay(cls, preset, coords):
    model = model_for(cls, preset, expr=True)
    point = model.point(coords)
    assert squared(point).almost_equal(model.algebra.scalar(0))
    base = model.down(point)
    actual_embedding = model.origin + base - squared(base) * model.infinity / (2 * model.null_pair)
    assert point.almost_equal(actual_embedding)
    assert model.dual(base) == complement(metric_apply(base))
    assert model.antidual(base) == complement(antimetric_apply(base))
    other = model.point(tuple(x + 0.25 for x in coords))
    blade = point ^ other
    families = [
        model.round_bulk_part(blade),
        model.round_weight_part(blade),
        model.flat_bulk_part(blade),
        model.flat_weight_part(blade),
    ]
    assert sum(families, model.algebra.scalar(0)) == blade
    assert model.bulk_part(blade) + model.weight_part(blade) == blade
    assert model.round_part(blade) + model.flat_part(blade) == blade
    assert model.conformal_conjugate(model.conformal_conjugate(blade)) == blade
    assert model.carrier(blade) == blade ^ model.infinity
    for method in (
        "round_bulk_part",
        "round_weight_part",
        "flat_bulk_part",
        "flat_weight_part",
        "bulk_part",
        "weight_part",
        "round_part",
        "flat_part",
        "conformal_conjugate",
        "attitude",
        "carrier",
        "cocarrier",
    ):
        result = getattr(model, method)(blade)
        assert result.expr is not None
        assert evaluate(result.expr, algebra=model.algebra).almost_equal(result)
    for result in (point, model.homogenize(3 * point), model.down(point), model.radius_squared(point)):
        assert result.expr is not None
        assert evaluate(result.expr, algebra=model.algebra).almost_equal(result)


def test_signed_radius_preserves_the_existing_cga_and_csta_definitions():
    cga = model_for(ConformalModel, presets.cga(), expr=True)
    csta = model_for(ConformalSpacetimeModel, presets.csta(), expr=True)
    for model, value, sign in (
        (cga, cga.round_point((1, 2, 3), radius_squared=4), -1),
        (csta, csta.signed_round((1, 2, 3, 4), 4), 1),
    ):
        result = model.radius_squared(value)
        assert float(result) == pytest.approx(sign * float(squared(value)) / float(model.weight(value)) ** 2)
        assert float(result) == pytest.approx(4)
        assert evaluate(result.expr, algebra=model.algebra).almost_equal(result)


@pytest.mark.parametrize(("cls", "preset", "coords"), CASES)
def test_signed_and_reordered_roles_derive_behavior_from_the_metric(cls, preset, coords):
    config = preset.build()
    original = Algebra(config=config, user_config_files=False)
    n = original.n
    permutation = tuple(reversed(range(n)))
    signs = np.array([(-1) ** i for i in range(n)])
    gram = original.gram[np.ix_(permutation, permutation)] * signs[:, None] * signs[None, :]

    def mapped(ref):
        indices = [permutation.index(i) for i in range(n) if ref.mask & (1 << i)]
        orientation = ref.orientation
        for i in indices:
            orientation *= int(signs[i])
        orientation *= (-1) ** sum(i > j for k, i in enumerate(indices) for j in indices[k + 1 :])
        return BladeRef(sum(1 << i for i in indices), orientation)

    roles = tuple((name, mapped(ref)) for name, ref in config.model.roles)
    # Existing Lengyel constraint methods require its positive native antiscalar role.
    if cls is RigidModel:
        roles = tuple((name, BladeRef((1 << n) - 1)) if name == "antiscalar" else (name, ref) for name, ref in roles)
    revised = replace(config, definition=AlgebraDefinition(gram=gram), model=ModelConfig(config.model.id, roles))
    model = model_for(cls, revised)
    point = model.point(coords)
    np.testing.assert_allclose(model.coordinates(point), coords)
    classified = model.classify(point)
    assert classified.simple is True
    assert classified.finite is True
    if cls is RigidModel:
        line = model.join(point, model.point(tuple(x + 1 for x in coords)))
        assert model.is_valid_line(line)
    if cls in {ConformalModel, ConformalSpacetimeModel}:
        assert float(squared(point)) == pytest.approx(0, abs=1e-12)
    else:
        assert model.bulk_part(point) + model.weight_part(point) == point


def test_models_reject_bare_matching_metrics_and_wrong_metadata():
    for cls in (PGAModel, RigidModel):
        with pytest.raises(ValueError):
            cls(Algebra(3, 0, 1, user_config_files=False))
        with pytest.raises(ValueError):
            cls(Algebra(0, 0, 4, user_config_files=False))
    for cls, preset in (
        (PGAModel, presets.rga()),
        (RigidModel, presets.pga()),
        (ConformalModel, presets.csta()),
        (ConformalSpacetimeModel, presets.cga()),
    ):
        with pytest.raises(ValueError):
            model_for(cls, preset)
    with pytest.raises(ValueError):
        model_for(PGAModel, presets.pga(4))
    config = presets.pga().build()
    for gram in (np.zeros((4, 4)), np.diag((2, 1, 1, 0))):
        with pytest.raises(ValueError, match="normalized"):
            model_for(PGAModel, replace(config, definition=AlgebraDefinition(gram=gram)))


def test_established_imports_are_the_same_classes():
    from galaga.cga import ConformalModel as OldConformal
    from galaga.rga import RigidModel as OldRigid

    assert OldConformal is ConformalModel
    assert OldRigid is RigidModel


@pytest.mark.parametrize(("cls", "preset", "coords"), CASES)
def test_missing_repeated_and_nonvector_roles_are_rejected(cls, preset, coords):
    config = preset.build()
    roles = config.model.roles
    vector_names = [name for name, ref in roles if ref.mask.bit_count() == 1]
    first, second = vector_names[:2]
    invalid_roles = (
        tuple((name, ref) for name, ref in roles if name != first),
        tuple((name, dict(roles)[second] if name == first else ref) for name, ref in roles),
        tuple((name, BladeRef(3) if name == first else ref) for name, ref in roles),
    )
    for invalid in invalid_roles:
        with pytest.raises(ValueError):
            model_for(cls, replace(config, model=ModelConfig(config.model.id, invalid)))


@pytest.mark.parametrize(("cls", "preset", "coords"), CASES)
def test_tracking_policy_and_point_replay(cls, preset, coords):
    model = model_for(cls, preset, expr=True)
    point = model.point(coords)
    assert evaluate(point.expr, algebra=model.algebra).almost_equal(point)
    assert model.point(coords, expr=False).expr is None
    plain = model_for(cls, preset)
    assert plain.point(coords).expr is None
    assert plain.point(coords, expr=True).expr is not None
    if cls in {PGAModel, RigidModel}:
        other = model.point(tuple(x + 0.5 for x in coords))
        for result in (model.join(point, other), model.meet(point, other)):
            assert evaluate(result.expr, algebra=model.algebra).almost_equal(result)


@pytest.mark.parametrize("null_pair", (-2.0, -0.5, 0.75))
def test_cga_round_invariants_derive_from_native_gram_and_pairing(null_pair):
    model = model_for(ConformalModel, presets.cga(2, null_pair=null_pair))
    samples = [model.point(q) for q in ((3, 2), (2, 3), (1, 2))]
    circle = outer_product(*samples)
    classified = model.classify(circle)
    assert classified.kind == "circle"
    props = dict(classified.properties)
    np.testing.assert_allclose(props["center"], (2, 2), atol=1e-12)
    assert props["radius_squared"] == pytest.approx(1)
    center = model.point(props["center"])
    for sample in samples:
        separation = squared(model.down(sample) - model.down(center))
        assert float(separation) == pytest.approx(props["radius_squared"])
        assert (sample ^ circle).almost_equal(model.algebra.scalar(0))


def test_cga_simplicity_uses_span_and_reports_degenerate_rounds():
    model = model_for(ConformalModel, presets.cga(3))
    e1, e2, e3 = model.euclidean_basis_vectors()
    non_simple = (e1 ^ e2 ^ e3) + (e1 ^ model.origin ^ model.infinity)
    assert not np.any((non_simple ^ non_simple).data)  # An odd blade's self-wedge proves nothing.
    assert model.classify(non_simple).simple is False
    degenerate = model.classify(e1 ^ e2)
    assert degenerate.kind == "degenerate"
    assert dict(degenerate.properties)["reason"] == "round span has no finite weight"
    higher = model_for(ConformalModel, presets.cga(4))
    with pytest.raises(ValueError, match="two or three"):
        higher.classify(higher.origin)


def test_constrained_rga_operator_names_require_verified_actions():
    from galaga import exp

    model = model_for(RigidModel, presets.rga())
    e1, e2, e3 = model.euclidean_basis_vectors()
    motor = complement(exp(0.3 * e2 * e3))
    flector = geometric_antiproduct(motor, model.algebra.blade("e423"))
    assert model.is_valid_flector(flector)
    assert model.classify(flector).kind == "flector"
    assert model.classify(model.algebra.scalar(1) + model.antiscalar).kind == "general"


def test_new_model_semantic_ids_render_and_accept_notation_overrides():
    model = model_for(PGAModel, presets.pga(), expr=True)
    point = model.point((1, 2, 3)).named("P")
    result = model.bulk_part(point)
    assert result.latex(content="expr") == r"\operatorname{bulk\_part}(P)"
    patch = presets.notation.override(projective_bulk_part="prefix:star")
    view = Algebra(config=presets.pga() | patch, user_config_files=False)
    assert r"\star" in view.multivector(result.data).with_expr(result.expr).latex(content="expr")


@pytest.mark.parametrize("expression_form", ("operator", "expanded"))
def test_csta_shared_normalization_and_radius_replay_follow_rebound_weight(expression_form):
    model = model_for(ConformalSpacetimeModel, presets.csta(), expr=True).with_expression_form(expression_form)
    round_value = model.signed_round((1, 2, 3, 4), 4).named("S")
    replacement = 3 * model.signed_round((2, -1, 0, 0), 9)
    for method in (model.homogenize, model.down, model.radius_squared):
        original_result = method(round_value)
        replay = evaluate(original_result.expr, algebra=model.algebra, environment={"S": replacement})
        assert replay.almost_equal(method(replacement))


def test_csta_classifier_respects_grade_tolerance_before_vector_validation():
    model = model_for(ConformalSpacetimeModel, presets.csta())
    g0, g1, _, _ = model.spacetime_basis_vectors()
    point = model.event((1, 0, 0, 0))
    almost_point = point + 1e-10 * (g0 ^ g1)
    assert model.classify(almost_point, representation="direct", atol=1e-9).kind == "event"
    assert model.classify(almost_point, representation="direct", atol=1e-12).kind == "general"


def test_csta_retains_exact_normalized_metric_validation():
    config = presets.csta().build()
    gram = np.array(config.definition.gram)
    gram[0, 0] += 1e-13
    with pytest.raises(ValueError, match="Gram block"):
        model_for(ConformalSpacetimeModel, replace(config, definition=AlgebraDefinition(gram)))


@pytest.mark.parametrize(
    ("cls", "preset"), ((RigidModel, presets.rga()), (PGAModel, presets.pga()), (ConformalModel, presets.cga()))
)
def test_euclidean_role_indices_have_one_canonical_spelling(cls, preset):
    config = preset.build()
    duplicate = (*config.model.roles, ("euclidean_01", dict(config.model.roles)["euclidean_1"]))
    with pytest.raises(ValueError, match="unique indices"):
        model_for(cls, replace(config, model=ModelConfig(config.model.id, duplicate)))


def test_projective_point_provenance_rejects_invalid_rebound_coordinates_and_parameters():
    from galaga.expression import Call

    model = model_for(RigidModel, presets.rga(), expr=True)
    vector = model.euclidean_vector((1, 2, 3)).named("x")
    point = model.point(vector)
    replacement = model.euclidean_vector((2, 0, -1))
    assert evaluate(point.expr, algebra=model.algebra, environment={"x": replacement}) == model.point(replacement)
    for invalid in (model.projective, model.algebra.scalar(2), model.algebra.blade(3)):
        with pytest.raises(ValueError, match="Euclidean subspace"):
            evaluate(point.expr, algebra=model.algebra, environment={"x": invalid})
    with pytest.raises(TypeError, match="boolean"):
        Call("projective_point", point.expr.operands, {"projective": (8, 1), "dual": 1})
    invalid_role = Call("projective_point", point.expr.operands, {"projective": (3, 1)})
    with pytest.raises(ValueError, match="basis vector"):
        evaluate(invalid_role, algebra=model.algebra, environment={"x": vector})
    nonscalar_weight = Call(
        "projective_point", (vector.expr, model.projective.with_expr().expr), {"projective": (8, 1)}
    )
    with pytest.raises(ValueError, match="weight must be scalar"):
        evaluate(nonscalar_weight, algebra=model.algebra, environment={"x": vector})
