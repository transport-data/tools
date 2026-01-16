"""Plug-in hooks to be implemented by submodules and other packages."""

from typing import TYPE_CHECKING, Iterable

import pluggy

if TYPE_CHECKING:
    import sdmx.model.v21


hookspec = pluggy.HookspecMarker("transport_data")


@hookspec
def cli_modules() -> str | Iterable[str]:
    """Return the fully-qualified name(s) of (a) module(s) with :mod:`click` commands.

    The module(s) **must** contain a :class:`click.Group` or command named :py:`main`.
    """
    raise NotImplementedError


@hookspec
def get_agencies() -> Iterable["sdmx.model.v21.Agency"]:
    """Return :class:`sdmx.model.common.Agency` identifying (meta)data provider(s).

    An implementation **must** return an iterable of 0 or more Agency instances.
    """
    raise NotImplementedError


@hookspec
def provides() -> Iterable[str]:
    """Return 0 or more URNs of SDMX artefacts available from a module."""
    raise NotImplementedError
