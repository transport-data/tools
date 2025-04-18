"""CLI for :mod:`.ato`.

.. runblock:: console

   $ tdc ato --help

.. runblock:: console

   $ tdc ato fetch --help

.. runblock:: console

   $ tdc ato convert --help
"""

import click

from . import FILES, convert, fetch


@click.group("ato")
def main():
    """Asian Transport Observatory (ATO) provider."""


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
def convert_cmd(part, all_):  # pragma: no cover
    """Convert to SDMX data and structures."""
    if not len(part):
        if not all_:
            print(f"Supply --all or 1+ of: {' '.join(FILES)}")
            return

        part = list(FILES.keys())

    for p in part:
        if p == "POL":
            print(f"Skip PART = {p}; not currently supported")
            continue

        convert(p)
