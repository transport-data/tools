"""CLI for :mod:`.org`.

.. runblock:: console

   $ tdc org --help

"""

import pathlib

import click

from transport_data.util.click import common_params


@click.group("org")
def main():
    """TDCI itself."""


@main.command("refresh", params=common_params("version"))
def refresh(version):
    """Update the TDCI metadata."""
    from transport_data import STORE

    from . import get_agencyscheme

    STORE.write(get_agencyscheme(version=version))


@main.command("read")
@click.argument(
    "path", type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path)
)
def read(path: "pathlib.Path"):
    """Read and summarize metadata."""
    from .metadata import read_workbook, summarize_metadataset

    mds = read_workbook(path.resolve())
    summarize_metadataset(mds)


@main.command("template")
def template():
    """Generate the metadata template."""
    from .metadata import make_workbook

    make_workbook()
