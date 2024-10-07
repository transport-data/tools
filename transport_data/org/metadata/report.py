from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

from transport_data.report import Report
from transport_data.util import uline

if TYPE_CHECKING:
    from sdmx.model import v21


@dataclass
class MetadataAttribute0HTML(Report):
    """Summarize unique values appearing in `mds` for attribute `mda_id`."""

    mds: "v21.MetadataSet"
    mda_id: str

    def render(self) -> str:
        raise NotImplementedError


@dataclass
class MetadataAttribute0Plain(Report):
    """Summarize unique values appearing in `mds` for attribute `mda_id`."""

    mds: "v21.MetadataSet"
    mda_id: str

    def render(self) -> str:
        from transport_data.org.metadata import _get

        value_id = defaultdict(set)

        for r in self.mds.report:
            value_id[_get(r, self.mda_id) or "MISSING"].add(
                _get(r, "DATAFLOW") or "MISSING"
            )

        assert self.mds.structured_by
        mda = self.mds.structured_by.report_structure["ALL"].get(self.mda_id)

        lines = ["", "", uline(f"{mda}: {len(value_id)} unique values")]

        for value, df_ids in sorted(value_id.items()):
            lines.extend([value, "    " + " ".join(sorted(df_ids))])

        return "\n".join(lines)


@dataclass
class MetadataReport0HTML(Report):
    mdr: "v21.MetadataReport"

    def render(self) -> str:
        raise NotImplementedError


@dataclass
class MetadataReport0Plain(Report):
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
            if desc := str(dim.get_annotation(id="tdc-description").text):
                line += f" {desc!s}"
            else:
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
class MetadataSet0HTML(Report):
    """Print a summary of the contents of `mds`."""

    template_name = "metadata-0.html"
    mds: "v21.MetadataSet"

    def render(self) -> str:
        lines = [
            f"Metadata set containing {len(self.mds.report)} metadata reports",
            MetadataAttribute0HTML(self.mds, "MEASURE").render(),
            MetadataAttribute0HTML(self.mds, "DATA_PROVIDER").render(),
            MetadataAttribute0HTML(self.mds, "UNIT_MEASURE").render(),
        ]

        for r in self.mds.report:
            lines.append(MetadataReport0HTML(r).render())

        return "\n".join(lines)


@dataclass
class MetadataSet0Plain(Report):
    """Print a summary of the contents of `mds`."""

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
    """Generate a summary report in HTML."""

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
class MetadataSet2HTML(Report):
    """Generate a summary report in HTML."""

    template_name = "metadata-set-2.html"

    #: Metadata set to summarize.
    mds: "v21.MetadataSet"
    #: Geography.
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


@dataclass
class MetadataSet1ODT(Report):
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
