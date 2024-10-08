"""Asian Development Bank (ADB) provider."""

from itertools import chain
from typing import Callable, Tuple
from urllib.parse import quote

import numpy as np
import pandas as pd
import sdmx.model.v21 as m

from transport_data import STORE as registry
from transport_data.util.pluggy import hookimpl
from transport_data.util.pooch import Pooch
from transport_data.util.sdmx import anno_generated


@hookimpl
def get_agencies():
    a = m.Agency(
        id="ADB",
        name="Asian Transport Outlook team at the Asian Development Bank",
        description="""See https://www.adb.org/what-we-do/topics/transport/asian-transport-outlook""",  # noqa: E501
    )

    c1 = m.Contact(name="James Leather", email=["jleather@adb.org"])
    c2 = m.Contact(name="Cornie Huizenga", email=["chuizenga@cesg.biz"])
    c3 = m.Contact(name="Sudhir Gota", email=["sudhirgota@gmail.com"])
    a.contact.extend([c1, c2, c3])

    return (a,)


BASE_URL = "https://asiantransportoutlook.com/exportdl?orig=1"

#: List of all "ECONOMY" codes appearing in processed data.
CL_ECONOMY = m.Codelist(
    id="ECONOMY",
    name="Asian Transport Outlook subject economy",
    description="Equivalent to GEO or REF_AREA in other concept schemes.",
)

#: List of all measures (indicators) appearing in processed data.
#:
#: .. todo:: Validate against the master list of indicators; or read from that file and
#:    validate IDs appearing in data files.
CS_MEASURE = m.ConceptScheme(
    id="MEASURE",
    name="Asian Transport Outlook measures (indicators)",
    description="Item are automatically generated by the TDCI tools. Currently no "
    "correspondence with the list provided directly by ADB is checked or enforced.",
)

#: Mapping from short codes for ATO data categories to file names.
FILES = {
    # "ATO National Database Masterlist of Indicators",
    "INF": "ATO Workbook (INFRASTRUCTURE (INF)).xlsx",
    "TAS": "ATO Workbook (TRANSPORT ACTIVITY & SERVICES (TAS)).xlsx",
    "ACC": "ATO Workbook (ACCESS & CONNECTIVITY (ACC)).xlsx",
    "RSA": "ATO Workbook (ROAD SAFETY (RSA)).xlsx",
    "APH": "ATO Workbook (AIR POLLUTION & HEALTH (APH)).xlsx",
    "CLC": "ATO Workbook (CLIMATE CHANGE (CLC)).xlsx",
    "SEC": "ATO Workbook (SOCIO-ECONOMIC (SEC)).xlsx",
    "POL": "ATO Workbook (TRANSPORT POLICY (POL)).xlsx",
    "MIS": "ATO Workbook (MISCELLANEOUS (MIS)).xlsx",
}


def expand(fname: str) -> str:
    return FILES.get(fname, fname)


def _make_url(fname: str) -> str:
    return f"{BASE_URL}&filename={quote(expand(fname))}"


POOCH = Pooch(
    module=__name__,
    base_url=BASE_URL,
    registry={expand(key): None for key in FILES.keys()},
    urls={expand(key): _make_url(key) for key in FILES.keys()},
    expand=expand,
)


def fetch(*parts, dry_run: bool = False):
    if dry_run:
        for p in parts:
            print(f"Valid url for GEO={p}: {POOCH.is_available(p)}")
        return

    return list(chain(*[POOCH.fetch(p) for p in parts]))


def validate_economy(df: pd.DataFrame) -> pd.DataFrame:
    """Validate codes for the "ECONOMY" dimension of `df` against :data:`CL_ECONOMY`.

    - Every unique pair of (Economy Code, Economy Name) is converted to a
      :class:`~sdmx.model.common.Code`.
    - These are added to :data:`CL_ECONOMY`. If a Code with the same ID already exists,
      it is checked for an exact match (name, description, etc.)
    - The "Economy Code" column of `df` is renamed "ECONOMY", and contains only values
      from :data:`CL_ECONOMY`. The "Economy Name" column is dropped.
    """
    codes = (
        df[["Economy Code", "Economy Name"]]
        .sort_values("Economy Code")
        .drop_duplicates()
        .apply(
            lambda row: m.Code(id=row["Economy Code"], name=row["Economy Name"]), axis=1
        )
    )
    for c in codes:
        try:
            CL_ECONOMY.append(c)
        except ValueError:
            assert CL_ECONOMY[c.id].compare(
                c
            ), f"Existing {CL_ECONOMY[c.id]} does not match {c}"

    return df.rename(columns={"Economy Code": "ECONOMY"}).drop(columns=["Economy Name"])


def read_sheet(
    ef: pd.ExcelFile, sheet_name: str
) -> Tuple[pd.DataFrame, m.AnnotableArtefact]:
    """Read a single sheet.

    This function handles the particular layout of sheets in files like those listed in
    :data:`FILES`. These combine data and metadata.

    - Row 1 is a title row.
    - Cell range A2:B10 contain a set of metadata fields, with the field name in column
      A and the value in column B.
    - Rows 11:13 contain no data or metadata; only a link back to a table of contents
      sheet.
    - Row 14 contains a label "Series" centre-spanned across
    - Row 15 contains column labels, described below.
    - Row 16 and onwards contain data, followed by two blank rows, and two rows with
      attribution/acknowledgements.

    - Columns labeled (i.e. in row 15) "Economy Code" and "Economy Name" contain codes
      and names, respectively, for the geographic units.
    - Columns with numeric labels describe time periods, specifically years, that are
      part of observation keys.
    - Some sheets have additional columns with non-numeric labels like "Remarks",
      "Source (2022-04)", etc.; these give annotations applying to the observations on
      the same row (i.e. for a single "Economy Code" and 1 or more time periods).
    """
    # Read metadata section
    meta_df = ef.parse(sheet_name, skiprows=1, nrows=9, usecols="A:B").dropna(how="all")

    # Convert metadata rows to a collection of temporary annotations
    aa = m.AnnotableArtefact()
    for _, data in meta_df.iterrows():
        title = data[0].rstrip(":")
        anno_id = title.upper().replace(" ", "-")
        aa.annotations.append(
            m.Annotation(
                id=anno_id,
                title=title,
                text=data[1] if isinstance(data[1], str) else repr(data[1]),
            )
        )

    # Read data section
    df = ef.parse(sheet_name, skiprows=14, skipfooter=2).dropna(how="all")

    # Identify data columns: those with numeric labels
    data_col_mask = list(map(str.isnumeric, df.columns))

    # Handle values not parsed by pd.ExcelFile.parse(). Some cells have values like
    # "12,345.6\t", which are not parsed to float.
    #
    # - Strip trailing whitespace.
    # - Remove thousands separators ("," in 2022-10-17 edition; " " in 2024-05-20
    #   edition) and whitespace before the decimal separator ("10860 .6", 2024-05-20
    #   edition).
    # - Replace "-" (no data) and "long ton" (erroneous) appearing since 2024-05-20
    #   edition.
    # - Finally, convert to float.
    dtypes = df.loc[:, data_col_mask].dtypes  # Dtypes of data columns only
    for col, _ in filter(lambda x: x[1] != "float", dtypes.items()):
        df[col] = (
            df[col]
            .str.strip()
            .str.replace(r"(\d)[, ]([\d\.])", r"\1\2", regex=True)
            .replace("^(-|long ton)$", np.nan, regex=True)
            .astype(float)
        )

    # Identify remarks columns: any entries at the *end* of `df.columns` with non-
    # numeric labels. Use the index of last data column, counting backwards.
    N = list(reversed(data_col_mask)).index(True)
    # Label(s) of any remarks columns
    remark_cols = df.columns.tolist()[-N:] if N else []
    # Store a list of these as another annotation
    aa.annotations.append(m.Annotation(id="remark-cols", text=repr(remark_cols)))

    return df, aa


def convert_sheet(df: pd.DataFrame, aa: m.AnnotableArtefact):
    """Convert `df` and `aa` from :func:`read_sheet` into SDMX data structures."""
    # Prepare an empty data set, associated structures, and a helper function
    ds, _make_obs = prepare(aa)

    # - Validate values in "Economy Code", "Economy Name" against CL_ECONOMY; then keep
    #   only the former as "ECONOMY".
    # - Melt into long format (one observation per row), preserving remarks columns.
    # - Drop NA values in the "OBS_VALUE" column
    data = (
        df.pipe(validate_economy)
        .melt(
            id_vars=["ECONOMY"] + (ds.eval_annotation("remark-cols") or []),
            var_name="TIME_PERIOD",
            value_name="OBS_VALUE",
        )
        .dropna(subset=["OBS_VALUE"])
    )

    # Convert rows of `data` into SDMX Observation objects
    ds.obs.extend(_make_obs(row) for _, row in data.iterrows())
    assert len(ds) == len(data)

    ds.pop_annotation(id="remark-cols")

    return ds


def prepare(aa: m.AnnotableArtefact) -> Tuple[m.DataSet, Callable]:
    """Prepare an empty data set and associated structures."""
    # Measure identifier and description
    measure_id = str(aa.pop_annotation(id="INDICATOR-ATO-CODE").text)
    measure_desc = str(aa.pop_annotation(id="DESCRIPTION").text)

    # Add to the "Measure" concept scheme
    # TODO avoid duplicating items for e.g. TDC-PAT-001(1), TDC-PAT-001(2)
    c = m.Concept(id=measure_id, description=measure_desc)
    CS_MEASURE.append(c)

    # Data structure definition with an ID matching the measure
    # NB here we set ADB as the maintainer. Precisely, ADB establishes the data
    #    structure, but TDCI is maintaining the SDMX representation of it.
    dsd = m.DataStructureDefinition(id=measure_id, maintainer=get_agencies()[0])
    anno_generated(dsd)

    dfd = m.DataflowDefinition(
        id=measure_id, maintainer=get_agencies()[0], structure=dsd
    )

    pm = m.PrimaryMeasure(id="OBS_VALUE", concept_identity=c)
    dsd.measures.append(pm)

    # Dimensions
    dsd.dimensions.extend(m.Dimension(id=d) for d in ("ECONOMY", "TIME_PERIOD"))

    # Convert annotations to DataAttributes. "NoSpecifiedRelationship" means that the
    # attribute is attached to an entire data set (not a series, individual obs, etc.).
    da = {}  # Store references for use below
    for a in filter(lambda a: a.id != "remark-cols", aa.annotations):
        da[a.id] = m.DataAttribute(id=a.id, related_to=m.NoSpecifiedRelationship())
        dsd.attributes.append(da[a.id])

    _PMR = m.PrimaryMeasureRelationship  # Shorthand

    # Convert remark column labels to DataAttributes. "PrimaryMeasureRelationship" means
    # that the attribute is attached to individual observations.
    for name in aa.eval_annotation("remark-cols"):
        dsd.attributes.append(m.DataAttribute(id=name, related_to=_PMR()))

    # Empty data set structured by this DSD
    ds = m.DataSet(
        described_by=dfd,
        structured_by=dsd,
        annotations=[aa.get_annotation(id="remark-cols")],
    )
    anno_generated(ds)

    # Convert temporary annotation values to attributes attached to the data set
    for a in filter(lambda a: a.id != "remark-cols", aa.annotations):
        ds.attrib[a.id] = m.AttributeValue(value=str(a.text), value_for=da[a.id])

    def _make_obs(row):
        """Helper function for making :class:`sdmx.model.Observation` objects."""
        key = dsd.make_key(m.Key, row[[d.id for d in dsd.dimensions]])

        # Attributes
        attrs = {}
        for a in filter(lambda a: a.related_to is _PMR, dsd.attributes):
            # Only store an AttributeValue if there is some text
            value = row[a.id]
            if not pd.isna(value):
                attrs[a.id] = m.AttributeValue(value_for=a, value=value)

        return m.Observation(
            dimension=key, attached_attribute=attrs, value_for=pm, value=row[pm.id]
        )

    return ds, _make_obs


def convert(part):
    path = POOCH.fetch(part)
    ef = pd.ExcelFile(path, engine="openpyxl")

    for sheet_name in ef.sheet_names:
        if sheet_name == "TOC":
            # Skip the TOC
            continue
        print(f"Process data flow {sheet_name!r}")

        df, annos = read_sheet(ef, sheet_name)
        ds = convert_sheet(df, annos)

        # Write the DSD and DFD
        registry.write(ds.described_by)
        registry.write(ds.structured_by)
        # Write the data itself, to SDMX-ML and CSV
        registry.write(ds)

    # Write the lists of "Economy" codes and measures/concepts accumulated while
    # converting
    a = get_agencies()[0]
    for obj in (CL_ECONOMY, CS_MEASURE):
        obj.maintainer = a
        obj.version = "0.1.0"
        registry.write(obj)
