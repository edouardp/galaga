"""Scale-sensitive algebraic traits and checked conformal versor actions."""

import math

import numpy as np

from ..facade import Multivector, scalar_product
from .classification import CSTAOperatorClassification


def classify_operator(
    value: Multivector, vectors: tuple[Multivector, ...], *, atol: float, rtol: float, max_power: int
) -> CSTAOperatorClassification:
    data = value.data
    if not np.all(np.isfinite(data)):
        raise ValueError("operator coefficients must be finite")
    one = value.algebra.scalar(1)

    def close(a: np.ndarray, b: np.ndarray) -> bool:
        return bool(np.allclose(a, b, atol=atol, rtol=rtol))

    traits = []
    if not np.any(data):
        traits.append("zero")
    if close(data, one.data):
        traits.append("identity")
    with np.errstate(over="ignore", invalid="ignore"):
        square = value * value
    if close(square.data, data):
        traits.append("idempotent")
    if close(square.data, one.data):
        traits.append("involution")
    index = _nilpotency_index(value, atol=atol, rtol=rtol, max_power=max_power)
    if index is not None:
        traits.append("nilpotent")
    action, parity, norm = _versor_action(value, vectors, atol=atol, rtol=rtol)
    if action is None:
        return CSTAOperatorClassification(tuple(traits), nilpotency_index=index)
    traits.append("versor")
    scale = float(np.max(np.abs(data)))
    if parity == "even" and math.isfinite(scale * scale * norm) and close(np.array(scale * scale * norm), np.array(1)):
        traits.append("rotor")
    transformation, properties = _transformation(action, atol=atol, rtol=rtol)
    properties += (("parity", parity), ("action", tuple(tuple(float(x) for x in row) for row in action)))
    return CSTAOperatorClassification(tuple(traits), transformation, index, properties)


def _nilpotency_index(value: Multivector, *, atol: float, rtol: float, max_power: int) -> int | None:
    scale = float(np.max(np.abs(value.data)))
    if scale == 0:
        return 1
    normalized = value.algebra.multivector(value.data / scale, expr=False)
    power = normalized
    for index in range(1, max_power + 1):
        magnitude = float(np.max(np.abs(power.data)))
        if magnitude <= atol + rtol:
            return index
        # Rescaling does not change whether a power is zero, and prevents
        # a small nonnilpotent value from masquerading as nilpotent by decay.
        if index < max_power:
            power = value.algebra.multivector(power.data / magnitude, expr=False) * normalized
    return None


def _versor_action(
    value: Multivector, vectors: tuple[Multivector, ...], *, atol: float, rtol: float
) -> tuple[np.ndarray | None, str | None, float]:
    scale = float(np.max(np.abs(value.data)))
    if scale == 0:
        return None, None, 0
    operator = value.algebra.multivector(value.data / scale, expr=False)
    odd = np.array([mask.bit_count() % 2 == 1 for mask in range(value.algebra.dim)])
    has_odd = bool(np.any(np.abs(operator.data[odd]) > atol + rtol))
    has_even = bool(np.any(np.abs(operator.data[~odd]) > atol + rtol))
    if has_odd == has_even:
        return None, None, 0
    parity = "odd" if has_odd else "even"
    product = operator * ~operator
    norm = float(product.data[0])
    if abs(norm) <= atol + rtol or not np.allclose(product.data[1:], 0, atol=atol, rtol=rtol):
        return None, None, norm
    inverse = ~operator / norm
    if not np.allclose((inverse * operator).data, value.algebra.scalar(1).data, atol=atol, rtol=rtol):
        return None, None, norm
    images = tuple((-1 if has_odd else 1) * operator * vector * inverse for vector in vectors)
    gram = np.array([[float(scalar_product(a, b)) for b in vectors] for a in vectors])
    pairings = np.array([[float(scalar_product(a, b)) for b in images] for a in vectors])
    action = np.linalg.solve(gram, pairings)
    basis_data = np.column_stack([vector.data for vector in vectors])
    if not np.allclose(basis_data @ action, np.column_stack([image.data for image in images]), atol=atol, rtol=rtol):
        return None, None, norm
    if not np.allclose(action.T @ gram @ action, gram, atol=atol, rtol=rtol):
        return None, None, norm
    return action, parity, norm


def _along(vector: np.ndarray, index: int, *, atol: float, rtol: float) -> bool:
    if abs(vector[index]) <= atol:
        return False
    direction = np.zeros(6)
    direction[index] = vector[index]
    return bool(np.allclose(vector, direction, atol=atol, rtol=rtol))


def _transformation(action: np.ndarray, *, atol: float, rtol: float) -> tuple[str, tuple[tuple[str, object], ...]]:
    if np.allclose(action, np.eye(6), atol=atol, rtol=rtol):
        return "identity", (("components", ()),)
    if not _along(action[:, 5], 5, atol=atol, rtol=rtol):
        if _along(action[:, 4], 4, atol=atol, rtol=rtol) and np.allclose(
            action[:4, :4] / action[4, 4], np.eye(4), atol=atol, rtol=rtol
        ):
            return "special conformal transformation", ()
        if (
            _along(action[:, 4], 5, atol=atol, rtol=rtol)
            and _along(action[:, 5], 4, atol=atol, rtol=rtol)
            and np.allclose(action[:4, :4], np.eye(4), atol=atol, rtol=rtol)
        ):
            return "conformal inversion", ()
        return "conformal transformation", ()

    weight = float(action[4, 4])
    # Preservation of infinity makes the physical map affine: q -> T + Lq.
    translation = action[:4, 4] / weight
    linear = action[:4, :4] / weight
    dilation = abs(1 / weight)
    lorentz = linear / dilation
    components = []
    if not np.allclose(translation, 0, atol=atol, rtol=rtol):
        components.append("translation")
    if not math.isclose(dilation, 1, abs_tol=atol, rel_tol=rtol):
        components.append("dilation")
    lorentz_kind = _lorentz_kind(lorentz, atol=atol, rtol=rtol)
    if lorentz_kind != "identity":
        components.append(lorentz_kind)
    name = components[0] if len(components) == 1 else "affine conformal transformation"
    properties = (
        ("components", tuple(components)),
        ("translation", tuple(float(x) for x in translation)),
        ("dilation_factor", dilation),
        ("lorentz_action", tuple(tuple(float(x) for x in row) for row in lorentz)),
    )
    return name, properties


def _lorentz_kind(action: np.ndarray, *, atol: float, rtol: float) -> str:
    if np.allclose(action, np.eye(4), atol=atol, rtol=rtol):
        return "identity"
    time = np.array((1, 0, 0, 0))
    if np.allclose(action[:, 0], time, atol=atol, rtol=rtol):
        if np.linalg.det(action) > 0:
            return "rotation"
        if (
            np.allclose(action @ action, np.eye(4), atol=atol, rtol=rtol)
            and np.linalg.matrix_rank(np.eye(4) - action, tol=atol + rtol) == 1
        ):
            return "spatial reflection"
        return "improper spatial transformation"
    gamma = float(action[0, 0])
    spatial = action[1:, 0]
    if gamma >= 1 - atol:
        boost = np.eye(4)
        boost[0, 0] = gamma
        boost[0, 1:] = spatial
        boost[1:, 0] = spatial
        boost[1:, 1:] += np.outer(spatial, spatial) / (gamma + 1)
        if np.allclose(action, boost, atol=atol, rtol=rtol):
            return "boost"
    return "Lorentz transformation"
