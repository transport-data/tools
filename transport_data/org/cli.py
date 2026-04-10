"""CLI for :mod:`.org`.

Use the :program:`--help` command-line option to see help for individual commands
defined in this module.

.. runblock:: console

   $ tdc org --help

"""

import pathlib
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from qrcode.image.base import BaseImageWithDrawer


@click.group("org")
def main():
    """TDCI itself."""


@main.command()
def refresh():
    """Update the TDCI metadata."""
    from transport_data import STORE

    from . import get_agencyscheme

    STORE.set(get_agencyscheme())


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
def summarize(path_in: "pathlib.Path", path_out: "pathlib.Path | None", ref_area):
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
            path_out.with_suffix(".html"), encoding="utf-8"
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
            path_out.with_suffix(".html"), encoding="utf-8"
        )


@main.command("tuewas")
@click.argument(
    "path_in", type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path)
)
def _tuewas_all(path_in):
    """Generate all outputs for TUEWAS.

    PATH_IN is the path to the .xlsx file containing collected metadata.
    """
    from zipfile import ZipFile

    from transport_data.util.libreoffice import HAS_LIBREOFFICE

    from .metadata import merge_ato, report
    from .metadata.spreadsheet import read_workbook

    ref_areas = "CN ID IN PH TH VN".split()

    # Read collected metadata for the project
    mds, _ = read_workbook(path_in.resolve())

    # Merge metadata available through ATO
    merge_ato(mds)

    dir_out = pathlib.Path.cwd().joinpath("output")
    path_out = []

    def _maybe_pdf():
        if HAS_LIBREOFFICE:
            # Also mark the auto-converted PDF to be added to the ZIP archive
            path_out.append(path_out[-1].with_suffix(".pdf"))
            print(f"Wrote {path_out[-2:]}")
        else:
            print(f"Wrote {path_out[-1]}")

    for ref_area in ref_areas:
        path_out.append(dir_out.joinpath(ref_area, "Summary.odt"))
        path_out[-1].parent.mkdir(parents=True, exist_ok=True)
        report.MetadataSet1ODT(mds, ref_area=ref_area).write_file(path_out[-1])
        _maybe_pdf()

    path_out.append(dir_out.joinpath("Metadata summary.odt"))
    report.MetadataSet0ODT(mds).write_file(path_out[-1])
    _maybe_pdf()

    path_out.append(dir_out.joinpath("Metadata summary table.html"))
    report.MetadataSet2HTML(mds, ref_area=ref_areas).write_file(
        path_out[-1], encoding="utf-8"
    )
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


@main.command("qr")
@click.option("--format", type=click.Choice(["png", "svg"]), default="png")
@click.argument("data")
def qr(format: str, data: str) -> None:
    """Generate QR codes.

    DATA should be a complete URL. A unique filename is generated from the URL, like
    qr-example-com-foo.png. With --format=png, the TDC logo is embedded.
    """
    import re
    from hashlib import blake2s
    from importlib.resources import files
    from urllib.parse import urlparse

    import qrcode

    # Parse the data as a URL
    url = urlparse(data)
    # Portion of the URL after the domain
    path_plus = data.partition(url.netloc)[2].lstrip("/")
    if re.search(r"[/\?=]", path_plus):
        # Hash of the path and subsequent URL parts, first 4 characters
        path_plus = blake2s(path_plus.encode()).hexdigest()[:5]
    # Construct the output filename
    filename = f"qr-{url.netloc.replace('.', '-')}{'-' if len(path_plus) else ''}{path_plus}.{format}"

    # Path to the TDC logo for embedding
    logo_path = files("transport_data").joinpath("data", "image", "logo.png")

    # Construct the QR code
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=2)
    # Add the URL as data
    qr.add_data(data)

    # Convert to an image
    if format == "png":
        # PNG image
        from qrcode.image.styledpil import StyledPilImage
        from qrcode.image.styles.colormasks import SolidFillColorMask
        from qrcode.image.styles.moduledrawers.pil import SquareModuleDrawer

        img: "BaseImageWithDrawer" = qr.make_image(
            image_factory=StyledPilImage,
            color_mask=SolidFillColorMask(
                back_color=(0, 96, 100),  # Same as HTML #006064
                front_color=(255, 255, 255),  # White
            ),
            module_drawer=SquareModuleDrawer(),
            embedded_image_path=logo_path,
        )
    elif format == "svg":
        # SVG image
        # NB The documentation is not clear, but it appears not possible to set the
        #    colours or an embedded image if using SVG.
        from qrcode.image.styles.moduledrawers.svg import SvgPathSquareDrawer
        from qrcode.image.svg import SvgPathImage

        img = qr.make_image(
            image_factory=SvgPathImage,
            background="#006064",  # Appears to have no effect
            module_drawer=SvgPathSquareDrawer(),
            # embedded_image_path=logo_path,  # Not supported
        )

    # Write to file
    with open(filename, "wb") as f:
        img.save(f)
    print(f"Wrote {filename}")
