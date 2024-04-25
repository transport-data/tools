"""Command-line interface."""

from importlib import import_module

import click

from . import CONFIG  # noqa: F401


@click.group("tdc")
def main():
    """Transport Data Commons tools."""


#: List of (sub)modules that define CLI (sub)commands. Each should contain a
#: @click.command() named "main".
MODULES_WITH_CLI = [
    "adb.cli",
    "config",
    "estat",
    "iamc.cli",
    "jrc.cli",
    "oica.cli",
    "org.cli",
    "proto.cli",
    "store",
]


# Add commands from each module that defines them
for name in MODULES_WITH_CLI:
    module = import_module(f"transport_data.{name}")
    main.add_command(getattr(module, "main"))
