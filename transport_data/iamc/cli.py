"""CLI for :mod:`iamc`.

.. runblock:: console

   $ tdc iamc --help

"""
from pathlib import Path

import click
import pandas as pd

from transport_data import registry
from transport_data.iamc import make_structures_for


@click.command(name="iamc")
def main():
    """Demonstrate IAMC structure generation.

    This command uses a test snippet of data from the IPCC AR6 database.
    """
    # Load test data
    test_data_path = Path(__file__).parents[1].joinpath("data", "tests")
    df = pd.read_csv(test_data_path.joinpath("iamc.csv"))

    # Function runs, returns a SDMX StructureMessage containing multiple structure
    # objects
    sm = make_structures_for(df, base_id="TEST")

    # Write each of the structure objects received to a separate file
    registry.write(sm, annotate=True, force=True)
