"""CLI for :mod:`.org`.

.. runblock:: console

   $ tdc org --help

"""

import pathlib
from typing import Optional

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
    from .metadata import report
    from .metadata.spreadsheet import read_workbook

    mds, _ = read_workbook(path.resolve())

    print(report.MetadataSet0Plain(mds).render())


@main.command
@click.option("--ref-area", required=True)
@click.argument(
    "path_in", type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path)
)
@click.argument(
    "path_out", type=click.Path(dir_okay=False, path_type=pathlib.Path), required=False
)
def summarize(path_in: "pathlib.Path", path_out: Optional["pathlib.Path"], ref_area):
    """Generate HTML metadata summary.

    If a single value is given for --ref-area (e.g. --ref-area=CA), a summary is
    generated of the (meta)data pertaining to that country/area. If multiple values are
    given (e.g. --ref-area=AF,ZW), a summary table is generated.
    """
    from .metadata import report
    from .metadata.spreadsheet import read_workbook

    mds, _ = read_workbook(path_in.resolve())

    ref_areas = ref_area.split(",")
    if 1 == len(ref_areas):
        # Report for a single REF_AREA
        if path_out is None:
            path_out = pathlib.Path.cwd().joinpath(f"{ref_areas[0]}.{{html,odt}}")
            print(f"Write to {path_out}")
        report.MetadataSet1HTML(mds, ref_area=ref_areas[0]).write_file(
            path_out.with_suffix(".html")
        )
        report.MetadataSet1ODT(mds, ref_area=ref_areas[0]).write_file(
            path_out.with_suffix(".odt")
        )
    elif 1 < len(ref_areas):
        # Report for multiple REF_AREA
        if path_out is None:
            path_out = pathlib.Path.cwd().joinpath("all.{html,odt}")
            print(f"Write to {path_out}")
        report.MetadataSet0ODT(mds).write_file(path_out.with_suffix(".odt"))
        report.MetadataSet2HTML(mds, ref_area=ref_areas).write_file(
            path_out.with_suffix(".html")
        )


@main.command("tuewas")
@click.argument(
    "path_in", type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path)
)
def _tuewas_all(path_in):
    """Generate all outputs for TUEWAS."""
    from zipfile import ZipFile

    from .metadata import report
    from .metadata.spreadsheet import read_workbook

    ref_areas = "CN ID IN PH TH VN".split()

    mds, _ = read_workbook(path_in.resolve())

    dir_out = pathlib.Path.cwd().joinpath("output")
    path_out = []

    for ref_area in ref_areas:
        path_out.append(dir_out.joinpath(ref_area, "Summary.odt"))
        path_out[-1].parent.mkdir(parents=True, exist_ok=True)
        report.MetadataSet1ODT(mds, ref_area=ref_areas[0]).write_file(path_out[-1])
        print(f"Wrote {path_out[-1]}")

    path_out.append(dir_out.joinpath("Metadata summary.odt"))
    report.MetadataSet0ODT(mds).write_file(path_out[-1])
    print(f"Wrote {path_out[-1]}")

    path_out.append(dir_out.joinpath("Metadata summary table.html"))
    report.MetadataSet2HTML(mds, ref_area=ref_areas).write_file(path_out[-1])
    print(f"Wrote {path_out[-1]}")

    path_zip = dir_out.joinpath("all.zip")
    with ZipFile(path_zip, mode="w") as zf:
        for p in path_out:
            zf.write(p, str(p.relative_to(dir_out)))

    print(f"Wrote {path_zip}")


@main.command("template")
def template():
    """Generate the metadata template."""
    from .metadata.spreadsheet import make_workbook

    make_workbook()
