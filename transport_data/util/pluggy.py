from importlib import import_module

import pluggy

from . import hooks

hookimpl = pluggy.HookimplMarker("transport_data")


pm = pluggy.PluginManager("transport_data")
pm.add_hookspecs(hooks)


def register_internal():
    """Register hook implementations from all modules that contain them.

    .. todo:: Automatically do this for all top-level submodules of transport_data.
    """

    for id_ in ("adb", "iamc", "ipcc.structure", "jrc", "oica", "org"):
        try:
            pm.register(import_module(f"transport_data.{id_}"))
        except ValueError:
            pass
