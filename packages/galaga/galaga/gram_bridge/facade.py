"""Compatibility re-export of the numeric objects owned by :mod:`galaga.facade`."""

import warnings

from ..facade import GalagaDeprecationWarning

warnings.warn(
    "galaga.gram_bridge.facade is deprecated; import galaga.facade",
    GalagaDeprecationWarning,
    stacklevel=2,
)

from ..facade._numeric import *  # noqa: F403
from ..facade._numeric import __all__ as __all__
