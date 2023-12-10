"""CLI for :mod:`.adb`.

.. runblock:: console

   $ tdc adb --help

.. runblock:: console

   $ tdc add fetch --help

.. runblock:: console

   $ tdc adb convert --help
"""

import click

from . import FILES, convert, fetch


@click.group("adb", help=__doc__)
def main():
    """Asian Development Bank (ADB) provider."""


@main.command("fetch")
@click.argument("part", nargs=-1)
@click.option("--go", is_flag=True, help="Actually fetch.")
@click.option("--all", "all_", is_flag=True, help="Fetch all files.")
def fetch_cmd(part, all_, go):
    """Fetch original data files."""
    if not len(part):
        if not all_:
            print(f"Supply --all or 1+ of: {' '.join(FILES)}")
            return

        part = list(FILES.keys())

    fetch(*part)


@main.command("convert")
@click.argument("part", nargs=-1)
@click.option("--all", "all_", is_flag=True, help="Convert all parts.")
def convert_cmd(part, all_):
    """Convert to SDMX data and structures."""
    if not len(part):
        if not all_:
            print(f"Supply --all or 1+ of: {' '.join(FILES)}")
            return

        part = list(FILES.keys())

    for p in part:
        convert(p)
