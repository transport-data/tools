"""Plug-in hooks to be implemented by submodules and other packages."""

from typing import TYPE_CHECKING, Iterable

import pluggy

if TYPE_CHECKING:
    import sdmx.model.v21

hookspec = pluggy.HookspecMarker("transport_data")


@hookspec
def get_agencies() -> Iterable["sdmx.model.v21.Agency"]:
    """Return :class:`sdmx.model.common.Agency` identifying (meta)data provider(s).

    An implementation **must** return an iterable of 0 or more Agency instances.
    """
    raise NotImplementedError
