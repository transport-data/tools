"""Eurostat (ESTAT) provider.

Eurostat is used as to demonstrate interaction with a data provider that offers:

- A web service that conforms to the SDMX REST API standard.
- Data and metadata in the SDMX-ML formatl through this API.

In this case, TDC tools can retrieve the structure information and data directly, and no
provider-specific conversion code is needed.
"""

import click
import sdmx

from transport_data import STORE as registry

# General functions


def list_flows():
    """Return a list of data flows."""
    # TODO use the API to retrieve a list of transport-related data flows
    return ["TRAN_HV_MS_FRMOD"]


def get(dataflow_id: str):
    """Retrieve the ESTAT structure and data for the data flow with ID `dataflow_id`."""
    client = sdmx.Client("ESTAT")

    # Retrieve structural information as an sdmx.StructureMessage
    sm = client.dataflow(dataflow_id)

    # Write each of the structure objects received to a separate file
    registry.write(sm, annotate=False)

    # Retrieve the data itself
    dm = client.data(dataflow_id)

    # Extract a single data set from the data message
    ds = dm.data[0]
    # Assign an explicit reference to the data set. The ESTAT response comes back with
    # an "anonymous" dataflow.
    ds.described_by = sm.dataflow[dataflow_id]
    ds.structured_by = ds.described_by.structure

    # Write to file
    path = registry.write(ds)
    print(f"Retrieved {path}")
    print("          and associated structures")

    return path


# Command-line interface


@click.group("estat", help=__doc__)
def main():
    pass


@main.command("fetch")
def fetch_cmd():
    """Retrieve data."""
    for dataflow_id in list_flows():
        print(f"Retrieve data flow {dataflow_id!r} and structure")
        get(dataflow_id)
