"""Command-line interface."""

from importlib import import_module
from pathlib import Path

import click

from . import CONFIG  # noqa: F401


@click.group("tdc")
def main():
    """Transport Data Commons tools."""


#: List of (sub)modules that define CLI (sub)commands. Each should contain a
#: @click.command() named "main".
MODULES_WITH_CLI = [
    "adb.cli",
    "config",
    "estat",
    "iamc.cli",
    "iso.cli",
    "jrc.cli",
    "oica.cli",
    "org.cli",
    "proto.cli",
    "store",
]


# Add commands from each module that defines them
for name in MODULES_WITH_CLI:
    module = import_module(f"transport_data.{name}")
    main.add_command(getattr(module, "main"))


@main.command("check")
@click.argument(
    "path", metavar="FILE", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
@click.option("--structure", help="Value for STRUCTURE field.")
@click.option("--structure-id", "structure_id", help="Value for STRUCTURE_ID field.")
@click.option("--action", help="Value for ACTION field.")
def check_csv(path: Path, verbose, **adapt):
    """Check that FILE can be read as SDMX-CSV."""
    import sdmx
    import sdmx.urn

    from transport_data.testing import ember_dfd
    from transport_data.util.sdmx import read_csv

    # Check for a supported file extension
    if not path.suffix == ".csv":
        raise click.UsageError(f"Unsupported file extension: {path.suffix!r}")

    print(f"File: {path}")

    # TEMPORARY Use a test utility function to get a DFD that describes the file
    structure = ember_dfd()
    # TODO Look up a data structure to use in STORE

    # Read the file into an SDMX data message
    try:
        dm = read_csv(path, structure, adapt)
    except Exception as e:
        message = [f"read failed with\n{type(e).__name__}: {' '.join(e.args)}"]

        if "line 1" in e.args[0]:
            message.append(
                "Hint: try giving --structure= or --structure-id argument(s) to adapt"
                " to SDMX-CSV."
            )
        elif isinstance(e, KeyError):
            message.append("Hint: try giving --action argument to adapt to SDMX-CSV.")

        print("")
        raise click.ClickException("\n\n".join(message))

    dfd_urn = sdmx.urn.shorten(sdmx.urn.make(dm.dataflow))
    print(f"\n{len(dm.data)} data set(s) in data flow {dfd_urn!s}")

    for i, ds in enumerate(dm.data):
        print(f"\nData set {i}: action={ds.action}")
        if verbose == 0:
            print(f"{len(ds)} observations")
        elif verbose == 1:
            print(sdmx.to_pandas(ds))
        else:
            print(sdmx.to_pandas(ds).to_string())
