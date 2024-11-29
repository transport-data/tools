"""Asian Development Bank (ADB) provider."""

from collections import defaultdict
from itertools import chain, product
from typing import Callable, Iterable, Tuple
from urllib.parse import quote, urlparse

import pandas as pd
import sdmx.model.v21 as m
from sdmx.model import v21

from transport_data.util.pluggy import hookimpl
from transport_data.util.pooch import Pooch
from transport_data.util.sdmx import anno_generated

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
    "ACC": (
        "ATO Workbook (ACCESS & CONNECTIVITY (ACC)).xlsx",
        "sha256:21c3b7e662d932f5cc61c22489acb3cf0e8a70200abc2372c7fe212602903fd7",
    ),
    "APH": (
        "ATO Workbook (AIR POLLUTION & HEALTH (APH)).xlsx",
        "sha256:b06c102a1184ed83d77673146599e11c2b6c81d784ebcee6b46f4d43713e899a",
    ),
    "CLC": (
        "ATO Workbook (CLIMATE CHANGE (CLC)).xlsx",
        "sha256:7fe2d4bb656508bf3194406d25ed04c1ac403daaaf1ada74847a2c330efcfb2a",
    ),
    "INF": (
        "ATO Workbook (INFRASTRUCTURE (INF)).xlsx",
        "sha256:30b9d05330838809ff0d53b2e61ade935eccdb4b73c0509fd1fc49b405699ac3",
    ),
    "MIS": (
        "ATO Workbook (MISCELLANEOUS (MIS)).xlsx",
        "sha256:2ef3cdc5e6363cdca1f671bbf12bf0463fe8a4210cb49b3d32ebd2440c6fe6df",
    ),
    "POL": (
        "ATO Workbook (TRANSPORT POLICY (POL)).xlsx",
        "sha256:fbf23b012590b631239654d255d23ccb70fa717b466be8343a5b0f1e8b4ce720",
    ),
    "RSA": (
        "ATO Workbook (ROAD SAFETY (RSA)).xlsx",
        "sha256:a4285d129c2739c8660a07a5d1c9902ec21c3cd4d13a2a9dfe9d49daca2c0dd5",
    ),
    "SEC": (
        "ATO Workbook (SOCIO-ECONOMIC (SEC)).xlsx",
        "sha256:b5d2ee5d07b5554ef262436ef898afd976fbb4956bd7cb850829cb7391d207c0",
    ),
    "TAS": (
        "ATO Workbook (TRANSPORT ACTIVITY & SERVICES (TAS)).xlsx",
        "sha256:628d4e9774f84d30d80706e982e4ddf7187d77f8676e69765c307701da1caf77",
    ),
}

VERSION = "0.1.0"


def expand(fname: str) -> str:
    return FILES.get(fname, (fname, None))[0]


def _make_url(fname: str) -> str:
    return f"{BASE_URL}&filename={quote(expand(fname))}"


POOCH = Pooch(
    module=__name__,
    base_url=BASE_URL,
    registry={v[0]: v[1] for v in FILES.values()},
    urls={expand(key): _make_url(key) for key in FILES.keys()},
    expand=expand,
)


def convert(part: str):
    from tqdm import tqdm

    from transport_data import STORE

    path = POOCH.fetch(part)
    ef = pd.ExcelFile(path, engine="openpyxl")

    # Maximum length of a sheet name, for formatting the description
    L = max(map(lambda v: len(str(v)), ef.sheet_names))

    for sheet_name in (progress := tqdm(ef.sheet_names)):
        if sheet_name == "TOC":
            # Skip the TOC
            continue
        progress.set_description(f"Process sheet {sheet_name!r:>{L}}")

        df, annos = read_sheet(ef, str(sheet_name))
        ds = convert_sheet(df, annos)

        # Write the DSD and DFD
        STORE.set(ds.described_by)
        STORE.set(ds.structured_by)
        # Write the data itself, to SDMX-ML and CSV
        STORE.set(ds)

    # Write the lists of "Economy" codes and measures/concepts accumulated while
    # converting
    a = get_agencies()[0]
    for obj in (CL_ECONOMY, CS_MEASURE):
        obj.maintainer = a
        obj.version = VERSION
        STORE.set(obj)


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


ATTRIBUTES: set[str] = set()


def _is_url(value: str) -> bool:
    """Return :any:`True` if `value` contains a URL."""
    return urlparse(value).path != value


def dataset_to_metadata_reports(
    ds: "v21.DataSet", msd: "v21.MetadataStructureDefinition"
) -> Iterable["v21.MetadataReport"]:
    """Convert the attributes of ATO `ds` to 1 or more :class:`.MetadataReport`.

    The metadata reports conform to the TDC metadata structure (
    :func:`.org.metadata.get_msd`).

    If `ds` contains per-series values for attributes named “Source”, “Source
    (2024-11)”, or similar, then additional metadata reports are generated, one for each
    series (=GEO, or ‘economy’) and each distinct upstream source indicated by these
    attribute values.
    """
    import sdmx.urn
    from pycountry import countries

    from transport_data import STORE
    from transport_data.org.metadata import make_ra, make_tok

    # Retrieve the DSD and DFD
    assert ds.structured_by and ds.structured_by.urn
    urn_dsd = sdmx.urn.normalize(ds.structured_by.urn)
    dsd = STORE.get(urn_dsd)
    dfd = STORE.get(urn_dsd.replace("DataStructure", "Dataflow"))
    # Assign the loaded DSD to the DFD's `structure` attribute, as these are loaded
    # separately
    dfd.structure = dsd

    # - Create a TargetObjectKey to associate the metadata report with the data flow
    #   definition
    # - Create the report itself
    mdr = v21.MetadataReport(attaches_to=make_tok(dfd))

    # Add the "DATAFLOW" metadata attribute, containing the same information
    mdr.metadata.append(make_ra("DATAFLOW", f"ATO:{dfd.id}"))

    # Map:
    # - from ATO IDs for attributes attached to data sets
    # - to TDC IDs for metadata attributes
    for attribute_id, mda_id in (
        ("SOURCE", "DATA_PROVIDER"),
        ("UNITS", "UNIT_MEASURE"),
        ("WEBSITE", "URL"),
    ):
        # Retrieve the (data) attribute value
        value = str(ds.attrib[attribute_id].value)
        # Convert to a reported (metadata) attribute; append to the report
        value = format_data_provider(value) if mda_id == "DATA_PROVIDER" else value
        mdr.metadata.append(make_ra(mda_id, value))

    # Retrieve the MEASURE from CS_MEASURE
    cs_measure = STORE.get("ConceptScheme=ADB:MEASURE(0.1.0)")
    measure_concept = cs_measure[dsd.id]
    # Construct a metadata attribute
    mdr.metadata.append(make_ra("MEASURE", measure_concept.name))

    # Assemble description
    description_lines = [
        f"Original (ATO) description of {dsd.id!r}:",
        str(measure_concept.description),
    ]

    ra_comment = make_ra("COMMENT", "Metadata generated by transport_data.tools.")
    mdr.metadata.append(ra_comment)

    geo_all = set()  # All GEO/REF_AREA for which the data set contains data
    sources = defaultdict(set)  # Mapping from GEO → "Source…" attribute values

    for observation in ds.obs:
        # Identify GEO/REF_AREA for which the data set contains data
        # Key value for the 'ECONOMY' dimension of `observation`
        geo_alpha_3 = observation.key["ECONOMY"].value
        # Convert from ISO 3166-1 alpha-3 (used by ATO) to alpha-2 (SDMX convention)
        geo_alpha_2 = countries.lookup(geo_alpha_3).alpha_2
        geo_all.add(geo_alpha_2)

        # Iterate over source attributes
        for av in observation.attached_attribute.values():
            ATTRIBUTES.add(av.value_for.id)  # DEBUG Track all attributes

            if not av.value_for.id.startswith("Source"):
                continue
            sources[geo_alpha_2].add(av.value)

    # Append a sorted list of GEO to the description
    description_lines.extend(
        ["", "The data contain non-null values for GEO:"] + sorted(geo_all)
    )

    # Finalise description
    mdr.metadata.append(make_ra("DATA_DESCR", "\n".join(description_lines)))

    # List of 1 or more metadata reports to return
    result = [mdr]

    # Generate additional metadata reports for upstream data
    for geo, source in chain(*[product([g], sorted(s)) for g, s in sources.items()]):
        dfd_geo = v21.DataflowDefinition(id=f"{geo}_{hash(dfd.id + source)}")
        mdr_geo = v21.MetadataReport(
            attaches_to=make_tok(dfd_geo), metadata=[ra_comment]
        )

        # Store the source attribute value as either the URL or DATA_PROVIDER
        # reported metadata attribute, depending on whether it is a URL
        mda_id = "URL" if _is_url(source) else "DATA_PROVIDER"
        mdr_geo.metadata.append(make_ra(mda_id, source))

        desc = (
            f"Upstream source(s) for 'ATO:{dfd.id}' (“{measure_concept.name}”) "
            f"data for GEO={geo!r}."
        )
        mdr_geo.metadata.append(make_ra("DATA_DESCR", desc))

        result.append(mdr_geo)

    return result


def fetch(*parts, dry_run: bool = False):
    if dry_run:
        for p in parts:
            print(f"Valid url for GEO={p}: {POOCH.is_available(p)}")
        return

    return list(chain(*[POOCH.fetch(p) for p in parts]))


def format_data_provider(value: str) -> str:
    """Format the ATO “Source” data attribute as TDC ``DATA_PROVIDER`` metadata.

    This makes more explicit how the ATO has handled upstream data.
    """
    if value.startswith("ATO analysis"):
        return value.replace("ATO analysis", "Asian Transport Outlook (ATO) analysis")
    elif value.startswith("Estimated"):
        return value.replace("Estimated", "Asian Transport Outlook (ATO); estimated")
    elif value.startswith("Calculated"):
        return "Asian Transport Outlook (ATO) calculation"
    else:
        return value + "—republished by ATO"


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


@hookimpl
def provides():
    return (
        "Codelist=TDCI:CL_ATO_ECONOMY",
        "ConceptScheme=TDCI:CS_ATO_MEASURE",
    )


def prepare(aa: m.AnnotableArtefact) -> Tuple[m.DataSet, Callable]:
    """Prepare an empty data set and associated structures."""
    # Measure identifier and description
    measure_id = (
        str(aa.pop_annotation(id="INDICATOR-ATO-CODE").text)
        .replace("(", "_")
        .replace(")", "")
    )
    measure_name = aa.pop_annotation(id="INDICATOR").text
    measure_desc = aa.pop_annotation(id="DESCRIPTION").text

    # Add to the "Measure" concept scheme
    # TODO avoid duplicating items for e.g. TDC-PAT-001(1), TDC-PAT-001(2)
    c = m.Concept(id=measure_id, name=measure_name, description=measure_desc)
    # TODO Extend an existing code list if converting only 1 or a few data sets
    CS_MEASURE.append(c)

    # Data structure definition with an ID matching the measure
    # NB here we set ADB as the maintainer. Precisely, ADB establishes the data
    #    structure, but TDCI is maintaining the SDMX representation of it.
    ma_args = dict(maintainer=get_agencies()[0], version=VERSION)
    dsd = m.DataStructureDefinition(id=measure_id, **ma_args)
    anno_generated(dsd)

    dfd = m.DataflowDefinition(id=measure_id, structure=dsd, **ma_args)

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
        for a in filter(lambda a: isinstance(a.related_to, _PMR), dsd.attributes):
            # Only store an AttributeValue if there is some text
            value = row[a.id]
            if not pd.isna(value):
                attrs[a.id] = m.AttributeValue(value_for=a, value=str(value))

        return m.Observation(
            dimension=key, attached_attribute=attrs, value_for=pm, value=row[pm.id]
        )

    return ds, _make_obs


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

    .. note:: Sheets in the ``POL`` category have a different format.
    """
    # Read metadata section
    meta_df = ef.parse(
        sheet_name, header=None, skiprows=1, nrows=9, usecols="A:B"
    ).dropna(how="all")

    # Convert metadata rows to a collection of temporary annotations
    aa = m.AnnotableArtefact()
    for _, data in meta_df.iterrows():
        title = data.iloc[0].rstrip(":")
        anno_id = title.upper().replace(" ", "-")
        aa.annotations.append(
            m.Annotation(
                id=anno_id,
                title=title,
                text=data.iloc[1]
                if isinstance(data.iloc[1], str)
                else repr(data.iloc[1]),
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
    # - RSA-RSI-007_1 contains erroneous values like "55.0g", likely intended to be
    #   "55.0%"; correct this.
    # - Replace miscellaneous erroneous values appearing since the 2024-05-20 edition:
    #   - "-", "n/a", "N/Appl." (both indicating no data)
    #   - "_" (likely erroneous)
    #   - "long ton" (erroneous)
    # - Some sheets contain columns with text labels in miscellaneous/undocumented
    #   formats, not supported by this function:
    #   - SEC-SEG-009: "land", "port"
    #   - MIS-SUM-002: "A", "B", "C", "D"
    #
    #   TODO Ask ATO to provide these data as SDMX, or extend code to convert
    # - Finally, convert to float.
    dtypes = df.loc[:, data_col_mask].dtypes  # Dtypes of data columns only
    for col, _ in filter(lambda x: x[1] != "float", dtypes.items()):
        df[col] = (
            df[col]
            .str.strip()
            .str.replace(r"(\d)[, ]([\d\.])", r"\1\2", regex=True)
            .str.replace(r"^([\d\.]+)g", r"\1", regex=True)
            .str.replace(r"^(-|long ton|N/Appl\.|n/a|_)$", "NaN", regex=True)
            .str.replace(r"^(land|port|A|B|C|D)$", "NaN", regex=True)
            .astype(float)
        )

    # Identify remarks columns: any entries at the *end* of `df.columns` with non-
    # numeric labels. Use the index of last data column, counting backwards.
    try:
        N = list(reversed(data_col_mask)).index(True)
    except ValueError:
        N = 0

    # Label(s) of any remarks columns
    remark_cols = df.columns.tolist()[-N:] if N else []
    # Store a list of these as another annotation
    aa.annotations.append(m.Annotation(id="remark-cols", text=repr(remark_cols)))

    return df, aa


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
