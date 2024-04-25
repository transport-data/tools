"""CLI for :mod:`.iamc`.

.. runblock:: console

   $ tdc iamc --help

"""

from pathlib import Path

import click


@click.command(name="iamc")
def main():
    """Demonstrate IAMC structure generation.

    This command uses a test snippet of data from the IPCC AR6 database.
    """
    import pandas as pd

    from transport_data import registry
    from transport_data.iamc import structures_for_data

    # Load test data
    test_data_path = Path(__file__).parents[1].joinpath("data", "tests")
    df = pd.read_csv(test_data_path.joinpath("iamc.csv"))

    # Function runs, returns a SDMX StructureMessage containing multiple structure
    # objects
    sm = structures_for_data(df, base_id="TEST")

    # Write each of the structure objects received to a separate file
    registry.write(sm, annotate=True, force=True)
