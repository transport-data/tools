"""Command-line interface."""

from importlib import import_module
from pathlib import Path

import click

from transport_data import CONFIG  # noqa: F401


@click.group("tdc")
def main():
    """Transport Data Commons tools."""


#: List of (sub)modules that define CLI (sub)commands. Each should contain a
#: @click.command() named "main".
MODULES_WITH_CLI = [
    "adb.cli",
    "config",
    "cli.interactive",
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


@main.command()
@click.argument(
    "path", metavar="FILE", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("--sheets", help="Sheet(s) in .xlsx FILE to check.")
@click.option("-v", "--verbose", count=True, help="Increase verbosity.")
@click.option("--structure", help="Value for STRUCTURE field.")
@click.option("--structure-id", "structure_id", help="Value for STRUCTURE_ID field.")
@click.option("--action", help="Value for ACTION field.")
def check(path: Path, sheets, verbose, **adapt):  # noqa: C901
    """Check that FILE can be read as SDMX-CSV."""
    import sdmx
    import sdmx.urn

    from transport_data.testing import ember_dfd
    from transport_data.util.sdmx import read_csv

    # Sequence of (label, path) for CSV files to be processed
    label_path = []

    if path.suffix == ".csv":
        label_path.append((f"File: {path}", path))
    elif path.suffix == ".xlsx":
        import pandas as pd
        from platformdirs import user_cache_path

        # Create a cache directory
        cache_dir = user_cache_path("transport-data").joinpath("check")
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Explode Excel file into one CSV file per sheet
        ef = pd.ExcelFile(path)
        _sheets = set(sheets.split(",")) if sheets else set(ef.sheet_names)
        for sheet_name in filter(_sheets.__contains__, ef.sheet_names):
            # Construct a temporary path
            label_path.append(
                (
                    f"File: {path}\nSheet: {sheet_name}",
                    cache_dir.joinpath(f"{path.stem}_xlsx_{sheet_name}.csv"),
                )
            )
            # Read the sheet from the ExcelFile and write to a CSV file
            pd.read_excel(ef, sheet_name).to_csv(label_path[-1][1], index=False)
        ef.close()
    else:
        raise click.UsageError(f"Unsupported file extension: {path.suffix!r}")

    # TEMPORARY Use a test utility function to get a DFD that describes the file(s)
    structure = ember_dfd()
    # TODO Look up a data structure to use in STORE

    for label, p in label_path:
        print(f"\n{label}")

        # Read the file into an SDMX data message
        try:
            dm = read_csv(p, structure, adapt)
        except Exception as e:
            message = [f"read failed with\n{type(e).__name__}: {' '.join(e.args)}"]

            if "line 1" in e.args[0]:
                message.append(
                    "Hint: try giving --structure= or --structure-id argument(s) to "
                    "adapt to SDMX-CSV."
                )
            elif isinstance(e, KeyError):
                message.append(
                    "Hint: try giving --action argument to adapt to SDMX-CSV."
                )

            print("")
            raise click.ClickException("\n\n".join(message))

        dfd_urn = sdmx.urn.shorten(sdmx.urn.make(dm.dataflow))
        print(f"\n{len(dm.data)} data set(s) in data flow {dfd_urn!s}")

        for i, ds in enumerate(dm.data):
            print(f"\nData set {i}: action={ds.action}")

            # Show information about the contents, according to verbosity
            if verbose == 0:
                print(f"{len(ds)} observations")
            elif verbose == 1:
                print(sdmx.to_pandas(ds))
            else:
                print(sdmx.to_pandas(ds).to_string())
