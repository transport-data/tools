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
    "ato.cli",
    "config",
    "cli.interactive",
    "estat",
    "iamc.cli",
    "iso.cli",
    "itdp.cli",
    "jrc.cli",
    "oica.cli",
    "org.cli",
    "org.ckan",
    "proto.cli",
    "store",
]


# Add commands from each module that defines them
for name in MODULES_WITH_CLI:
    module = import_module(f"transport_data.{name}")
    main.add_command(getattr(module, "main"))


@main.command()
@click.argument("structure_urn", metavar="URN")
@click.argument(
    "path", metavar="FILE", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("--sheets", help="Sheet(s) in .xlsx FILE to check.")
@click.option("-v", "--verbose", count=True, help="Increase verbosity.")
@click.option("--structure", help="Value for STRUCTURE field.")
@click.option("--structure-id", "structure_id", help="Value for STRUCTURE_ID field.")
@click.option("--action", default="I", help="Value for ACTION field.")
def check(structure_urn: str, path: Path, sheets, verbose, **options):  # noqa: C901
    """Check that FILE can be read as SDMX-CSV.

    URN is the shortened SDMX URN of a data flow or data structure definition that
    describes the data in FILE, for example "Dataflow=PROVIDER:EXAMPLE(1.2.3)" (the
    version is not required). This artefact must already be present in the local store.

    FILE may have a ".csv" or ".xlsx" suffix. In the latter case, it is converted to a
    temporary set of CSV files. If --sheets are given, only these worksheets are
    converted and checked.

    If not given, --structure and --structure-id are inferred from URN.
    """
    from traceback import format_exception

    import sdmx
    import sdmx.urn
    from sdmx.model import common

    from transport_data import STORE
    from transport_data.util.sdmx import read_csv

    # Pieces of any error message
    message = []

    # Handle `structure_urn`: retrieve a data structure that describes the data
    try:
        structure = STORE.get(structure_urn)
    except Exception:
        message.append(f"Structure {structure_urn!r} could not be loaded")
        structure = structure_cls = structure_id = None
    else:
        structure_cls = type(structure).__name__.lower().replace("definition", "")
        structure_id = sdmx.urn.shorten(structure.urn).split("=")[-1]

    if isinstance(structure, common.BaseDataflow):
        # Also retrieve the data structure definition
        STORE.resolve(structure, "structure")
        assert len(structure.structure.dimensions)

    # Construct keyword arguments for CSVAdapter
    # TODO Check if this works for full SDMX-CSV
    adapt = {
        "structure": options.pop("structure") or structure_cls,
        "structure_id": options.pop("structure_id") or structure_id,
        "action": options.pop("action"),
    }

    # Handle `path`; construct a sequence of (label, path) of CSV files to be processed
    label_path = []

    if path.suffix == ".csv":
        label_path.append((f"File: {path}", path))
    elif path.suffix == ".xlsx":
        # Explode an Excel file into one or more CSV files in a temporary directory
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

    # Process `label_path`
    for label, p in label_path:
        print(f"\n{label}")

        # Read the file into an SDMX data message
        try:
            dm = read_csv(p, structure, adapt)
        except Exception as e:
            message.append(f"read failed with\n{type(e).__name__}: {' '.join(e.args)}")

            if len(e.args) and "line 1" in e.args[0]:
                message.append(
                    "Hint: try giving --structure= or --structure-id argument(s) to "
                    "adapt to SDMX-CSV."
                )
            elif structure is None:
                pass
            else:  # pragma: no cover
                message.append("\n".join(format_exception(e)))

            print("")
            raise click.ClickException("\n\n".join(message))

        # Show the contents of the data message
        dfd_urn = sdmx.urn.shorten(sdmx.urn.make(dm.dataflow))
        print(f"\n{len(dm.data)} data set(s) in: {dfd_urn!s}")

        # Show information about each data set
        for i, ds in enumerate(dm.data):
            print(f"\nData set {i}: action={ds.action}")

            # Show the data set contents or summary, according to verbosity
            if verbose == 0:
                print(f"{len(ds)} observations")
            elif verbose == 1:
                print(sdmx.to_pandas(ds))
            else:
                print(sdmx.to_pandas(ds).to_string())
