"""Real principal logarithm action using resolvent quadrature, not eigenvectors."""

from collections.abc import Iterator
from functools import lru_cache

import numpy as np
from numpy.typing import NDArray

_QUADRATURE_ORDERS = (8, 16, 32, 64, 128, 256)


@lru_cache(maxsize=len(_QUADRATURE_ORDERS))
def _quadrature(order: int) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    nodes, weights = (nodes + 1) / 2, weights / 2
    nodes.setflags(write=False)
    weights.setflags(write=False)
    return nodes, weights


def principal_log_candidates(action: NDArray[np.float64]) -> Iterator[NDArray[np.float64]]:
    """Yield increasingly accurate first columns of the principal ``log(action)``.

    Use log(A) = integral_0^1 (A-I) (I+t(A-I))^-1 dt. The caller verifies
    convergence and exponentiation in the original algebra. Eigenvalues
    only diagnose the branch; no diagonalizability assumption is made.
    """
    if not np.all(np.isfinite(action)):
        raise ValueError("log cannot resolve a non-finite action")
    try:
        eigenvalues = np.linalg.eigvals(action)
        condition = np.linalg.cond(action)
    except np.linalg.LinAlgError as error:
        raise ValueError("log cannot resolve the principal real branch numerically") from error
    if not np.isfinite(condition) or condition * np.finfo(float).eps >= 1:
        raise ValueError("log input is singular or too ill-conditioned to resolve")
    spectral_error = 32 * np.finfo(float).eps * max(1.0, float(np.linalg.norm(action, ord=np.inf)))
    if np.any((eigenvalues.real <= 0) & (np.abs(eigenvalues.imag) <= spectral_error)):
        raise ValueError("log principal real branch is undefined or unresolved on the nonpositive real axis")

    identity = np.eye(len(action))
    delta = action - identity
    for order in _QUADRATURE_ORDERS:
        nodes, weights = _quadrature(order)
        result = np.zeros(len(action))
        try:
            for node, weight in zip(nodes, weights):
                result += weight * np.linalg.solve(identity + node * delta, delta[:, 0])
        except np.linalg.LinAlgError as error:
            raise ValueError("log quadrature encountered a singular resolvent") from error
        yield result
