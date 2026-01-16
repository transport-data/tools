"""Command-line interface."""

from importlib import import_module
from itertools import chain

import click

from transport_data import CONFIG  # noqa: F401
from transport_data.util.pluggy import pm


@click.group("tdc")
def main():
    """Transport Data Commons tools."""


#: List of (sub)modules that define CLI (sub)commands. Each should contain a
#: @click.command() named "main".
MODULES_WITH_CLI = [
    "transport_data.config",
    "transport_data.cli.interactive",
    "transport_data.cli.check_file",
    "transport_data.cli.check_record",
    "transport_data.org.ckan",
    "transport_data.proto.cli",
    "transport_data.store",
    "transport_data.testing.cli",
]


# Add commands from hooks
for name in chain(MODULES_WITH_CLI, pm.hook.cli_modules()):
    try:
        module = import_module(name)
    except ImportError as e:
        print(f"Error: {e}")
    main.add_command(getattr(module, "main"))
