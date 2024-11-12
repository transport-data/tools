"""Utilities for :mod:`pluggy`."""

from importlib import import_module

import pluggy

from . import hooks

hookimpl = pluggy.HookimplMarker("transport_data")


pm = pluggy.PluginManager("transport_data")
pm.add_hookspecs(hooks)


def register_internal(*submodules: str) -> None:
    """Register hook implementations from `submodules` of :mod:`transport_data`."""
    for submodule in submodules:
        pm.register(import_module(f"transport_data.{submodule}"))
