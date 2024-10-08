"""CLI for :mod:`.jrc`.

.. runblock:: console

   $ tdc jrc --help

.. runblock:: console

   $ tdc jrc fetch --help

.. runblock:: console

   $ tdc jrc convert --help
"""

import click

from . import GEO, convert, fetch


@click.group("jrc")
def main():
    """EU Joint Research Center (JRC) provider."""


@main.command("fetch")
@click.argument("geo", nargs=-1)
@click.option("--go", is_flag=True, help="Actually fetch.")
@click.option("--all", "all_", is_flag=True, help="Fetch all files.")
def fetch_cmd(geo, all_, go):
    """Fetch original data files."""
    if not len(geo):
        if not all_:
            print(f"Supply --all or 1+ of {' '.join(sorted(GEO))}")
            return

        geo = GEO

    fetch(*geo, dry_run=not go)


@main.command("convert")
@click.argument("geo", nargs=-1)
@click.option("--all", "all_", is_flag=True, help="Fetch all files.")
def convert_cmd(geo, all_):
    """Convert to SDMX data and structures."""
    if not len(geo):
        if not all_:
            print(f"Supply --all or 1+ of {' '.join(sorted(GEO))}")
            return

        geo = GEO

    try:
        for g in geo:
            convert(g)
    except AssertionError:
        raise click.Abort
