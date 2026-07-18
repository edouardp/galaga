"""Compatibility name for :mod:`galaga.facade` during the v2 migration."""

import warnings

from ..facade import GalagaDeprecationWarning

warnings.warn(
    "galaga.gram_bridge is deprecated; import galaga.facade",
    GalagaDeprecationWarning,
    stacklevel=2,
)

from ..facade import *  # noqa: F403
from ..facade import __all__ as __all__
