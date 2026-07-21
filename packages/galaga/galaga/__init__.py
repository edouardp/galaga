"""Galaga 2 — geometric algebra over a Gram-matrix numeric core.

The top-level package is the canonical Galaga 2 API.  Its public objects are
the exact objects owned by :mod:`galaga.facade`; no wrapper or parallel public
implementation is created here.  The presentation-independent numeric engine
remains available as :mod:`galaga.core`.

Galaga 1 is retained temporarily during the Phase 8 shadow cutover through an
explicit import::

    from galaga import legacy

Legacy algebras, multivectors, and operations form a separate value domain and
must not be mixed with their Galaga 2 counterparts.  The legacy namespace is a
migration and test-oracle facility scheduled for removal in Phase 9.
"""

from __future__ import annotations

from . import facade as facade
from .facade import *  # noqa: F401,F403

# The facade owns the public manifest.  Copy the list so consumers cannot
# mutate the implementation namespace through ``galaga.__all__``.
__all__ = list(facade.__all__)


def __getattr__(name: str) -> object:
    """Delegate rejected or future facade attributes without API duplication."""
    try:
        return getattr(facade, name)
    except AttributeError as error:
        message = str(error).replace("galaga.facade", "galaga")
        raise AttributeError(message) from None
