"""CLI for :mod:`.oica`.

.. runblock:: console

   $ tdc oica --help

.. runblock:: console

   $ tdc oica fetch --help

"""

import click

from . import fetch


@click.group("oica", help=__doc__.splitlines()[0])
def main():
    """International Organization of Motor Vehicle Manufacturers (OICA) provider."""


@main.command("fetch")
@click.option("--go", is_flag=True, help="Actually fetch.")
def fetch_cmd(go):
    """Fetch original data files."""
    fetch(dry_run=not go)
