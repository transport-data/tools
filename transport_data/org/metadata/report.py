from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

from transport_data.report import Report

if TYPE_CHECKING:
    from sdmx.model import v21


@dataclass
class SummaryHTML0(Report):
    """Generate a summary report in HTML."""

    template_name = "metadata-0.html"

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
class SummaryHTML1(Report):
    """Generate a summary report in HTML."""

    template_name = "metadata-1.html"

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
class SummaryODT(Report):
    template_name = "metadata-2.rst"

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
