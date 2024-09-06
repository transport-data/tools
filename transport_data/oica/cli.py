"""CLI for :mod:`.oica`.

.. runblock:: console

   $ tdc oica --help

.. runblock:: console

   $ tdc oica convert-all --help

.. runblock:: console

   $ tdc oica fetch --help

"""

import click


@click.group("oica", short_help="OICA provider.")
def main():
    """International Organization of Motor Vehicle Manufacturers (OICA) provider."""


@main.command("convert-all")
def convert_all():
    """Convert all data to SDMX."""
    from . import convert

    for measure in "SALES", "STOCK":
        convert(measure)


@main.command("fetch")
@click.option("--go", is_flag=True, help="Actually fetch.")
def fetch_cmd(go):
    """Fetch original data files."""
    from . import fetch

    fetch(dry_run=not go)
