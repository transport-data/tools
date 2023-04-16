from importlib import import_module

import click


@click.group("tdc")
def main():
    """Transport Data Commons tools."""


# Add subcommands from each module that defines them
for name in ("org", "proto"):
    # Import a CLI submodule
    module = import_module(f"transport_data.{name}.cli")
    # Add the command named "main"
    main.add_command(getattr(module, "main"))
