"""CLI for :mod:`.org`.

.. runblock:: console

   $ tdc org --help

"""

import click

from transport_data import STORE
from transport_data.util.click import common_params


@click.command("org", params=common_params("version"))
def main(version):
    """Information about the TDCI per se."""
    from . import get_agencyscheme

    STORE.write(get_agencyscheme(version=version), force=True)
