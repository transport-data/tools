import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Optional, Tuple

from sdmx.model import v21
from sdmx.model.v21 import MetadataStructureDefinition

if TYPE_CHECKING:
    import pathlib

    from openpyxl import Workbook
    from openpyxl.worksheet.worksheet import Worksheet

log = logging.getLogger(__name__)

#: Concepts and metadata attributes in the TDC metadata structure.
CONCEPTS = {
    "DATAFLOW": (
        "Data flow ID",
        """A unique identifier for the data flow (=data source, data set, etc.).

We suggest to use IDs like ‘VN001’, where ‘VN’ is the ISO 3166 alpha-2 country
code, and ‘001’ is a unique number. The value MUST match the name of the sheet
in which it appears.""",
    ),
    "DATA_PROVIDER": (
        "Data provider",
        """Organization or individual that provides the data and any related metadata.

This can be as general (“IEA”) or specific (organization unit/department, specific
person responsible, contact details, etc.) as appropriate.""",
    ),
    "URL": (
        "URL or web address",
        "Location on the Internet with further information about the data flow.",
    ),
    "MEASURE": (
        "Measure (‘indicator’)",
        """Statistical concept for which data are provided in the data flow.

If the data flow contains data for multiple measures, give each one separated by
semicolons. Example: “Number of cars; passengers per vehicle”.

This SHOULD NOT duplicate the value for ‘UNIT_MEASURE’. Example: “Annual driving
distance per vehicle”, not “Kilometres per vehicle”.""",
    ),
    "UNIT_MEASURE": (
        "Unit of measure",
        """Unit in which the data values are expressed.

If ‘MEASURE’ contains 2+ items separated by semicolons, give the respective units in the
same way and order. If there are no units, write ‘dimensionless’, ‘1’, or similar.""",
    ),
    "DIMENSION": (
        "Dimensions",
        """Formally, the “statistical concept used in combination with other statistical
concepts to identify a statistical series or individual observations.”

Record all dimensions of the data, either in a bulleted or numbered list, or
separated by semicolons. In parentheses, give some indication of the scope
and/or resolution of the data along each dimension. Most data have at least time
and space dimensions.

Example:

- TIME_PERIOD (annual, 5 years up to 2021)
- REF_AREA (whole country; VN only)
- Vehicle type (12 different types: […])
- Emissions species (CO2 and 4 others)""",
    ),
    "DATA_DESCR": (
        "Data description",
        """Any information about the data flow that does not fit in other attributes.

Until or unless other metadata attributes are added to this metadata structure/
template, this MAY include:

- Any conditions on data access, e.g. publicly available, proprietary, fee or
  subscription required, available on request, etc.
- Frequency of data updates.
- Any indication of quality, including third-party references that indicate data
  quality.
""",
    ),
    "COMMENT": (
        "Comment",
        """Any other information about the metadata values, for instance discrepancies or
unclear or missing information.

Precede comments with initials; append to existing comments to keep
chronological order; and include a date (for example, “2024-07-24”) if helpful.""",
    ),
}

#: README text for the TDC metadata file format.
README_TEXT = """This file is an unofficial, prototype TDC format for metadata.
loosely imitates the Eurostat format. These files contain metadata (information
*about* data) based on the SDMX information model, but their layout (sheet
names, columns, etc.) is not specified by the SDMX standard, hence ‘unofficial’.

This file has the following sheets.

README
======

This sheet.

Attributes
==========

- One row per metadata attribute (or 'field').
- Columns for the name; description; and ID (short and machine-readable) of each
  attribute. See these descriptions to learn what to write for each attribute.

One or more additional sheets
=============================

- The name (or title) of each sheet corresponds to the identity (ID) of the data
  flow that is described by the metadata in that sheet.
- In Column A, the name of the metadata attribute. Each name MUST exactly
  match one appearing in the "Attributes" sheet. Some names MAY be omitted.
- In Column B, the actual metadata. These may be empty.

TEMPLATE
========

To add information about additional data flows not included in existing sheets
(above), you can copy and rename this sheet.
"""


def _header(ws: "Worksheet", *columns: Tuple[str, int]) -> None:
    """Write header columns and format their style and width."""
    for column, (value, width) in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=column, value=value)
        cell.style = "header"
        ws.column_dimensions[cell.column_letter].width = width


def add_readme(wb: "Workbook") -> None:
    """Add a "README" sheet to `wb`."""
    ws = wb.create_sheet("README")

    _header(ws, ("Transport Data Commons (TDC) metadata", 72))
    ws["A3"] = README_TEXT


def add_attributes(wb: "Workbook", msd: "MetadataStructureDefinition"):
    """Add an "Attributes" sheet to `wb` listing the metadata attributes from `msd`."""
    ws = wb.create_sheet("Attributes")

    _header(
        ws,
        ("Name", 20),  # "Element name" in Eurostat
        ("Description", 72),  # Not present in Eurostat
        ("ID", 20),  # "Element code" in Eurostat
    )

    for row, attribute in enumerate(msd.report_structure["ALL"].components, start=2):
        concept = attribute.concept_identity
        ws.cell(row=row, column=1, value=concept.name.localized_default()).style = "top"
        ws.cell(row=row, column=2, value=concept.description.localized_default())
        ws.cell(row=row, column=3, value=attribute.id).style = "top"


def add_template(wb: "Workbook", msd: "MetadataStructureDefinition"):
    """Add a "TEMPLATE" sheet to `wb` with a metadata template."""
    ws = wb.create_sheet("TEMPLATE")

    _header(
        ws,
        ("Attribute name", 20),  # "Concept name" in Eurostat
        ("Value", 72),  # "Concept value" in Eurostat
    )

    for row, attribute in enumerate(msd.report_structure["ALL"].components, start=2):
        concept = attribute.concept_identity
        ws.cell(row=row, column=1, value=concept.name.localized_default()).style = "top"
        ws.cell(row=row, column=2, value="---")


def get_msd() -> "MetadataStructureDefinition":
    from sdmx.model.common import ConceptScheme
    from sdmx.model.v21 import ReportStructure

    from transport_data import STORE

    from . import get_agencyscheme

    as_ = get_agencyscheme()
    cs = ConceptScheme(id="METADATA_CONCEPTS", maintainer=as_["TDCI"])
    msd = MetadataStructureDefinition(id="SIMPLE", version="1", maintainer=as_["TDCI"])
    rs = msd.report_structure["ALL"] = ReportStructure(id="ALL")

    for id_, (name, description) in CONCEPTS.items():
        ci = cs.setdefault(id=id_, name=name, description=description)
        rs.getdefault(id_, concept_identity=ci)

    # NB Currently not supported by sdmx1; results in an empty XML collection
    STORE.write(msd)

    return msd


def make_workbook(name="sample.xlsx") -> None:
    """Generate a :class:`openpyxl.Workbook` for exchange of metadata."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, NamedStyle, PatternFill

    wb = Workbook()

    # Delete the default sheet
    assert wb.active
    wb.remove(wb.active)

    # Create two named styles
    header = NamedStyle(name="header")
    header.fill = PatternFill("solid", fgColor="000000")
    header.font = Font(bold=True, color="ffffff", name="Calibri")
    wb.add_named_style(header)

    top = NamedStyle(name="top")
    top.alignment = Alignment(vertical="top", wrap_text=True)
    top.font = Font(name="Calibri")
    wb.add_named_style(top)

    # Generate the metadata structure definition
    msd = get_msd()

    # Add sheets
    add_readme(wb)
    add_attributes(wb, msd)
    add_template(wb, msd)

    # Save the file
    wb.save(name)


def read_workbook(path: "pathlib.Path") -> "v21.MetadataSet":
    """Read a metadata set from the workbook at `path`."""
    from openpyxl import load_workbook

    wb = load_workbook(path)
    # Generate/retrieve the metadata structure definition
    msd = get_msd()

    mds = v21.MetadataSet(structured_by=msd)

    for ws in wb.worksheets:
        # Skip information sheets generated by methods in this file
        if ws.title in ("README", "Attributes", "TEMPLATE"):
            continue

        mds.report.append(read_worksheet(ws, msd))

    return mds


def read_worksheet(
    ws: "Worksheet", msd: "MetadataStructureDefinition"
) -> "v21.MetadataReport":
    """Read a metadata report from the worksheet `ws`.

    Parameters
    ----------
    msd :
       Metadata structure definition.
    """
    # Mapping from names (not IDs) to MetadataAttributes
    mda_for_name = {
        str(mda.concept_identity.name): mda
        for mda in msd.report_structure["ALL"].components
    }

    # Create the target of the report: a data flow definition
    # TODO Expand this DFD and its associated data structure definition
    df_id_from_title = ws.title
    dfd = v21.DataflowDefinition(id=ws.title, maintainer=msd.maintainer)

    # Create objects to associate the metadata report with the data flow definition
    iot = v21.IdentifiableObjectTarget()
    tok = v21.TargetObjectKey(
        key_values={"DATAFLOW": v21.TargetIdentifiableObject(value_for=iot, obj=dfd)}
    )

    # Create the report itself
    mdr = v21.MetadataReport()
    mdr.attaches_to = tok

    # Iterate over rows in the worksheet
    mda = None
    for row in ws.iter_rows():
        # Column B: value in the row
        ra_value = row[1].value

        if ra_value is None:
            continue

        # Column A: name of the metadata attribute
        mda_name = row[0].value

        # Identify the MDA
        # NB if `mda_name` is none, then `mda` retains the value found on the previous
        #    row. This allows e.g. multiple rows to give values for DIMENSION
        # TODO Protect against other malformed data.
        mda = mda_for_name.get(str(mda_name), mda)

        # Store as OtherNonEnumeratedAttributeValue
        # TODO Use EnumeratedAttributeValue, once code lists are available corresponding
        #      to dimensions
        ra = v21.OtherNonEnumeratedAttributeValue(value=str(ra_value), value_for=mda)

        # Attend the reported attribute to the report
        mdr.metadata.append(ra)

    # Basic checks
    df_id_from_cell = _get(mdr, "DATAFLOW")
    if not df_id_from_cell:
        log.warning(f"Sheet {df_id_from_title!r} does not identify a data flow; skip")

    return mdr


def _get(mdr: "v21.MetadataReport", mda_id: str) -> Optional[str]:
    """Retrieve from `mdr` the reported value of the metadata attribute `mda_id`."""
    for mda in mdr.metadata:
        if mda.value_for is not None and mda.value_for.id == mda_id:
            assert hasattr(mda, "value")  # Exclude ReportedAttribute without value attr
            return mda.value
    # No match
    return None


def summarize_metadataset(mds: "v21.MetadataSet") -> None:
    """Print a summary of the contents of `mds`."""
    print(f"Metadata set containing {len(mds.report)} metadata reports")

    def uline(text: str, char: str = "=") -> str:
        """Underline `text`."""
        return f"{text}\n{char * len(text)}"

    def summarize_metadataattribute(mda_id: str) -> None:
        """Summarize unique values appear in metadata for attribute `mda_id`."""
        value_id = defaultdict(set)

        for r in mds.report:
            value_id[_get(r, mda_id) or "MISSING"].add(_get(r, "DATAFLOW") or "MISSING")

        assert mds.structured_by
        mda = mds.structured_by.report_structure["ALL"].get(mda_id)

        print("\n\n" + uline(f"{mda}: {len(value_id)} unique values"))
        for value, df_ids in sorted(value_id.items()):
            print(f"{value}\n    " + " ".join(sorted(df_ids)))

    summarize_metadataattribute("MEASURE")
    summarize_metadataattribute("DATA_PROVIDER")
    summarize_metadataattribute("UNIT_MEASURE")
