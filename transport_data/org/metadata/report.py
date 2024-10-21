"""Generate reports about TDC-structured metadata.

:class:`.Report` subclasses in this file **should** have names like::

    { Type }{ ID }{ Format }

…wherein:

- ``{ Type }`` refers to the type of object(s) from the SDMX Information Model that
  is/are represented in the report.
  Usually the first argument to the :py:`__init__()` method is an instance of this type.
- ``{ ID }`` is a number that distinguishes different ‘kinds’ of reports for the same
  ``{ Type }``.
  Report classes with the same ``{ Type }{ ID }`` **should** display roughly the same
  information in the same order and layout, regardless of ``{ Format }``.
- ``{ Format }`` is the output format or file type.
"""

from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

from transport_data.report import Report
from transport_data.util import uline

if TYPE_CHECKING:
    import pathlib

    from sdmx.model import v21


def odt_to_pdf(path: "pathlib.Path") -> None:
    from subprocess import check_call

    check_call(
        [
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(path.parent),
            str(path),
        ]
    )


@dataclass
class MetadataAttribute0Plain(Report):
    """Unique values appearing in `mds` for metadata attribute `mda_id`.

    Each unique value is shown with the IDs of the data flows that contain the value for
    `mda_id`.
    """

    #: Metadata set to report.
    mds: "v21.MetadataSet"
    #: ID of a Metadata Attribute to report.
    mda_id: str

    def render(self) -> str:
        from transport_data.org.metadata import map_values_to_ids

        value_id = map_values_to_ids(self.mds, self.mda_id)

        assert self.mds.structured_by
        mda = self.mds.structured_by.report_structure["ALL"].get(self.mda_id)

        lines = ["", "", uline(f"{mda}: {len(value_id)} unique values")]

        for value, df_ids in sorted(value_id.items()):
            lines.extend([value, "    " + " ".join(sorted(df_ids))])

        return "\n".join(lines)


@dataclass
class MetadataAttribute0RST(Report):
    """Unique values appearing in `mds` for the metadata attribute `mda_id`.

    Same as :class:`.MetadataAttribute0Plain`, but in reStructuredText.
    """

    #: Jinja2 reStructuredText template.
    template_name = "metadata-attribute-0.rst"
    #: Metadata set to report.
    mds: "v21.MetadataSet"
    #: ID of a Metadata Attribute to report.
    mda_id: str

    def render(self) -> str:
        from transport_data.org.metadata import map_values_to_ids

        value_id = map_values_to_ids(self.mds, self.mda_id)
        assert self.mds.structured_by
        mda = self.mds.structured_by.report_structure["ALL"].get(self.mda_id)

        return self.render_jinja_template(mda=mda, value_id=value_id)


@dataclass
class MetadataReport0HTML(Report):
    """Same as :class:`.MetadataReport0Plain`, but in HTML."""

    #: Metadata report to report.
    mdr: "v21.MetadataReport"

    def render(self) -> str:
        raise NotImplementedError


@dataclass
class MetadataReport0Plain(Report):
    """Contents of a single metadata report.

    This includes:

    1. The reported attribute values for all metadata attributes.
    2. The data flow that is targeted by the report and its dimensions.
    """

    #: Metadata report to report.
    mdr: "v21.MetadataReport"

    def render(self) -> str:
        lines = ["", uline("Metadata report")]

        # Retrieve references to the data flow and data structure
        dfd: "v21.DataflowDefinition" = self.mdr.attaches_to.key_values["DATAFLOW"].obj  # type: ignore [union-attr]
        dsd = dfd.structure

        # Summarize the data flow and data structure

        lines.extend(
            [f"Refers to {dfd!r}", f"  with structure {dsd!r}", "    with dimensions:"]
        )
        for dim in dsd.dimensions:
            line = f"    - {dim.id}:"
            try:
                anno_description = dim.get_annotation(id="tdc-description")
                if desc := str(anno_description.text):
                    line += f" {desc!s}"
                else:
                    raise KeyError
            except KeyError:
                line += " (no info)"

            try:
                original_id = dim.get_annotation(id="tdc-original-id").text
                line += f" ('{original_id!s}' in input file)"
            except KeyError:
                pass
            lines.append(line)

        lines.append("")

        for ra in self.mdr.metadata:
            if ra.value_for.id == "DATAFLOW":
                continue
            assert hasattr(ra, "value")
            lines.append(f"{ra.value_for}: {ra.value}")

        return "\n".join(lines)


@dataclass
class MetadataSet0ODT(Report):
    """Summary of the unique reported attribute values in `mds`.

    Similar to :class:`.MetadataSet0Plain`, but also including:

    - The unique dimension concepts appearing in the data structure definitions.
    """

    template_name = "metadata-set-0.rst"
    #: Metadata set to report.
    mds: "v21.MetadataSet"

    def render(self) -> bytes:
        from transport_data.org.metadata import map_dims_to_ids

        # Mapping from reported attribute values to data flow IDs
        mda = [
            MetadataAttribute0RST(self.mds, "DATA_PROVIDER").render(),
            MetadataAttribute0RST(self.mds, "MEASURE").render(),
            MetadataAttribute0RST(self.mds, "UNIT_MEASURE").render(),
        ]
        # Mapping from dimension IDs to data flow IDs
        dim_id = map_dims_to_ids(self.mds)

        rst_source = self.render_jinja_template(mda=mda, dim_id=dim_id)
        # print(rst_source)  # DEBUG
        return self.rst2odt(rst_source)

    def write_file(self, path: "pathlib.Path", **kwargs) -> None:
        """:meth:`render` the report and write to `path`."""
        super().write_file(path, **kwargs)
        odt_to_pdf(path)


@dataclass
class MetadataSet0Plain(Report):
    """Summary of the unique reported attribute values in `mds`.

    This includes:

    - Unique values of the metadata attributes ``MEASURE``, ``DATA_PROVIDER``, and
      ``UNIT_MEASURE``.
    """

    #: Metadata set to report.
    mds: "v21.MetadataSet"

    def render(self) -> str:
        lines = [
            f"Metadata set containing {len(self.mds.report)} metadata reports",
            MetadataAttribute0Plain(self.mds, "MEASURE").render(),
            MetadataAttribute0Plain(self.mds, "DATA_PROVIDER").render(),
            MetadataAttribute0Plain(self.mds, "UNIT_MEASURE").render(),
        ]

        for r in self.mds.report:
            lines.append(MetadataReport0Plain(r).render())

        return "\n".join(lines)


@dataclass
class MetadataSet1HTML(Report):
    """Metadata reports related to `ref_area`."""

    template_name = "metadata-set-1.html"

    #: Metadata set to summarize.
    mds: "v21.MetadataSet"
    #: Geography.
    ref_area: str

    def render(self) -> str:
        from transport_data.org.metadata import contains_data_for, groupby

        grouped = groupby(
            self.mds, key=partial(contains_data_for, ref_area=self.ref_area)
        )

        return self.render_jinja_template(
            ref_area=self.ref_area, matched=grouped[True], no_match=grouped[False]
        )


@dataclass
class MetadataSet1ODT(Report):
    """Metadata reports related to `ref_area`.

    Same as :class:`.MetadataSet1HTML` but as OpenDocument Text.
    """

    template_name = "metadata-set-1.rst"

    #: Metadata set to summarize.
    mds: "v21.MetadataSet"
    #: Geography.
    ref_area: str

    def render(self) -> bytes:
        from transport_data.org.metadata import contains_data_for, groupby

        # Prepare data; same as SummaryHTML0
        grouped = groupby(
            self.mds, key=partial(contains_data_for, ref_area=self.ref_area)
        )

        # Render the report as reStructuredText using Jinja2 and a template
        rst_source = self.render_jinja_template(
            ref_area=self.ref_area,
            matched=grouped[True],
            no_match=grouped[False],
        )
        # print(rst_source)  # DEBUG

        # Convert reStructuredText → OpenDocumentText
        return self.rst2odt(rst_source)

    def write_file(self, path: "pathlib.Path", **kwargs) -> None:
        """:meth:`render` the report and write to `path`."""
        super().write_file(path, **kwargs)
        odt_to_pdf(path)


@dataclass
class MetadataSet2HTML(Report):
    """Table of metadata reports.

    This table has:

    - One *column* per value in `ref_areas`.
    - One *row* per metadata report in `mds`.
    - A check-mark in cells where :func:`.contains_data_for` indicates that the metadata
      report targets a data flow that contains data for the reference area.
    """

    template_name = "metadata-set-2.html"

    #: Metadata set to summarize.
    mds: "v21.MetadataSet"
    #: Geographies to show.
    ref_area: list[str]

    def render(self) -> str:
        from transport_data.org.metadata import contains_data_for

        data = {
            mdr.attaches_to.key_values["DATAFLOW"].obj.id: {  # type: ignore [union-attr]
                ra: contains_data_for(mdr, ra) for ra in self.ref_area
            }
            for mdr in self.mds.report
        }

        return self.render_jinja_template(ref_area=self.ref_area, data=data)
