"""Compatibility re-export of :mod:`galaga.facade.catalog`."""

import warnings

from ..facade import GalagaDeprecationWarning

warnings.warn(
    "galaga.gram_bridge.catalog is deprecated; import galaga.facade.catalog",
    GalagaDeprecationWarning,
    stacklevel=2,
)

from ..facade.catalog import *  # noqa: F403
from ..facade.catalog import __all__ as __all__
