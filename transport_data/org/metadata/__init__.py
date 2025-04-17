"""Handle TDC-structured metadata."""

import itertools
import logging
import re
from collections import defaultdict
from functools import lru_cache, partial
from itertools import count
from typing import Any, Callable, Hashable, Iterable, Optional, cast

from pycountry import countries
from sdmx.model import common, v21

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
    "METHOD": (
        "Methodology",
        """Any information about methods used by the data provider to collect, process,
or prepare the data.""",
    ),
    "COMMENT": (
        "Comment",
        """Any other information about the metadata values, for instance discrepancies or
unclear or missing information.

Precede comments with initials; append to existing comments to keep
chronological order; and include a date (for example, “2024-07-24”) if helpful.""",
    ),
}


def contains_data_for(mdr: "v21.MetadataReport", ref_area: str) -> bool:
    """Return :any:`True` if `mdr` contains data for `ref_area`.

    :any:`True` is returned if any of the following:

    1. The referenced data flow definition has an ID that starts with `ref_area`.
    2. The country's ISO 3166 alpha-2 code, alpha-3 code, official name, or common name
       appears in the value of the ``DATA_DESCR`` metadata attribute.


    Parameters
    ----------
    ref_area : str
        ISO 3166 alpha-2 code for a country. Passed to
        :meth:`pycountry.countries.lookup`.
    """
    if mdr.attaches_to.key_values["DATAFLOW"].obj.id.startswith(ref_area):  # type: ignore [union-attr]
        return True

    # Valid identifiers for `country`: its ISO 3166 alpha-[23] codes and names
    # NB In pycountry 23.12.11, "common_name" would fall back to "official_name" or
    #    "name" if not explicitly defined. In 24.6.1, this was reverted and
    #    AttributeError is raised.
    country = countries.lookup(ref_area)
    values: Iterable[str] = filter(
        None,
        (
            getattr(country, a, None)
            for a in "alpha_2 alpha_3 common_name name official_name".split()
        ),
    )
    # Pattern to match in DATA_DESCR
    pat = re.compile("(" + "|".join(values) + ")")

    for ra in mdr.metadata:
        assert hasattr(ra, "value")
        if ra.value_for.id == "DATA_DESCR" and pat.search(str(ra.value)):
            return True

    return False


def dfd_id(mdr: "v21.MetadataReport") -> str:
    """Return the ID of the dataflow targeted by `mdr`."""
    assert mdr.attaches_to is not None
    return cast(
        "v21.TargetIdentifiableObject", mdr.attaches_to.key_values["DATAFLOW"]
    ).obj.id


@lru_cache
def get_cs_common() -> "common.ConceptScheme":
    """Create a shared concept scheme for the concepts referenced by dimensions.

    Concepts in this scheme have an annotation ``tdc-aka``, which is a list of alternate
    IDs recognized for the concept.
    """
    from transport_data.org import get_agencyscheme

    as_ = get_agencyscheme()
    cs = common.ConceptScheme(id="CONCEPTS", maintainer=as_["TDCI"])

    cs.setdefault(
        id="CONFIDENTIALITY",
        annotations=[v21.Annotation(id="tdc-aka", text=repr(["CONFIDIENTALITY"]))],
    )
    cs.setdefault(
        id="FUEL_TYPE",
        annotations=[v21.Annotation(id="tdc-aka", text=repr(["Fuel type"]))],
    )
    cs.setdefault(
        id="GEO",
        annotations=[
            v21.Annotation(
                id="tdc-aka",
                text=repr(
                    ["Area", "Country", "Country code", "ECONOMY", "REF_AREA", "Region"]
                ),
            )
        ],
    )
    cs.setdefault(
        id="SERVICE",
        annotations=[v21.Annotation(id="tdc-aka", text=repr(["FREIGHT_PASSENGER"]))],
    )
    cs.setdefault(
        id="TIME_PERIOD",
        annotations=[v21.Annotation(id="tdc-aka", text=repr(["Time", "Year"]))],
    )

    return cs


@lru_cache
def get_msd() -> "v21.MetadataStructureDefinition":
    """Generate and return the TDC metadata structure definition."""
    from transport_data import STORE
    from transport_data.org import get_agencyscheme

    TDCI = get_agencyscheme()["TDCI"]

    cs = common.ConceptScheme(id="METADATA_CONCEPTS", maintainer=TDCI)
    msd = v21.MetadataStructureDefinition(id="SIMPLE", version="1", maintainer=TDCI)
    rs = msd.report_structure["ALL"] = v21.ReportStructure(id="ALL")

    for id_, (name, description) in CONCEPTS.items():
        ci = cs.setdefault(id=id_, name=name, description=description)
        rs.getdefault(id_, concept_identity=ci)

    # NB Currently not supported by sdmx1; results in an empty XML collection
    STORE.set(msd)

    return msd


def groupby(
    mds: "v21.MetadataSet", key=Callable[["v21.MetadataReport"], Hashable]
) -> dict[Hashable, list["v21.MetadataReport"]]:
    """Group metadata reports in `mds` according to a `key` function.

    Similar to :func:`itertools.groupby`.
    """
    result: dict[Hashable, list["v21.MetadataReport"]] = defaultdict(list)
    for k, g in itertools.groupby(mds.report, key):
        result[k].extend(g)
    return result


def _get(mdr: "v21.MetadataReport", mda_id: str) -> Optional[str]:
    """Retrieve from `mdr` the reported value of the metadata attribute `mda_id`."""
    for mda in mdr.metadata:
        if mda.value_for is not None and mda.value_for.id == mda_id:
            assert hasattr(mda, "value")  # Exclude ReportedAttribute without value attr
            return str(mda.value) if mda.value else None
    # No match
    return None


# TODO Keep this dictionary as small as possible, by making appropriate changes in the
# input metadata
RENAME = {
    "IRF - International Road Federation": "International Road Federation (IRF)",
    "UIC": "International Union of Railways (UIC)",
}


def make_ra(mda_id: str, value: Any) -> "v21.OtherNonEnumeratedAttributeValue":
    """Generate a ReportedAttribute for `mda_id` with the given `value`."""
    mda = get_msd().report_structure["ALL"].get(mda_id)
    return v21.OtherNonEnumeratedAttributeValue(value=str(value), value_for=mda)


def make_tok(dfd: "common.BaseDataflow") -> "v21.TargetObjectKey":
    """Generate a :class:`.TargetObjectKey` that refers to `dfd`."""
    iot = v21.IdentifiableObjectTarget()
    return v21.TargetObjectKey(
        key_values={"DATAFLOW": v21.TargetIdentifiableObject(value_for=iot, obj=dfd)}
    )


def map_values_to_ids(mds: "v21.MetadataSet", mda_id: str) -> dict[str, set[str]]:
    """Return a mapping from unique reported attribute values to data flow IDs."""
    result = defaultdict(set)

    for r in mds.report:
        value = _get(r, mda_id) or "MISSING"

        # Merge or relabel certain values
        value = RENAME.get(value, value)

        result[value].add(_get(r, "DATAFLOW") or "MISSING")

    return result


def map_dims_to_ids(mds: "v21.MetadataSet") -> dict[str, set[str]]:
    """Return a mapping from unique concept IDs used for dimensions to data flow IDs."""
    result = defaultdict(set)

    for r in mds.report:
        dfd = r.attaches_to.key_values["DATAFLOW"].obj  # type: ignore [union-attr]
        for dim in dfd.structure.dimensions:
            key = f"{dim.id!r}"
            try:
                anno = dim.get_annotation(id="tdc-original-id")
                key += f" (as '{anno.text!s}')"
            except KeyError:
                pass

            result[key].add(dfd.id)

    return result


def unique_dfd_id(mdr: "v21.MetadataReport", existing: set[str]) -> str:
    """Generate a unique DSD ID for `mdr`."""
    template = f"{dfd_id(mdr)[:2]}{{:03d}}"
    for i in count():
        candidate = template.format(i)
        if candidate not in existing:
            existing.add(candidate)
            break
    return candidate


def merge_ato(mds: "v21.MetadataSet") -> None:
    """Extend `mds` with metadata reports for ATO/ATO data flows."""
    from transport_data import STORE
    from transport_data.ato import dataset_to_metadata_reports

    assert mds.structured_by

    N = len(mds.report)  # Initial number of reports
    all_dfd_ids = set(map(dfd_id, mds.report))  # Existing IDs of DFDs

    # Silence warnings from SDMX
    logging.getLogger("sdmx").setLevel(logging.ERROR)

    # Mapping from upstream URLs to metadata reports
    reports = defaultdict(list)

    # Iterate over existing data sets
    for ds in map(
        STORE.get,
        filter(
            lambda k: True,  # All results
            # lambda k: "-VEP-" in k,  # DEBUG Filter for a subset of data sets
            STORE.list(v21.DataSet, maintainer="ATO"),
        ),
    ):
        try:
            # Convert the attributes of `ds` into 1+ metadata report(s)
            for mdr in dataset_to_metadata_reports(ds, mds.structured_by):
                # Split URLs on multiple lines to a list
                for url in (_get(mdr, "URL") or "").split("\n"):
                    # Store a reference to each report in a collection for each URL
                    reports[url].append(mdr)
        except KeyError:
            # log.debug(f"Not in local store: {e.args[0]}")
            continue

    # Reports to attend to `mds` last
    sort_last = []

    # Iterate over URLs and lists of reports
    for url, report_group in reports.items():
        # Single report associated with this URL, or multiple reports but not with an
        # ID prefix like "CA_" that indicates a country-specific generated report
        if 1 == len(report_group) or not dfd_id(report_group[0])[2] == "_":
            mds.report.extend(report_group)  # Store directly
            continue

        # Identify the first report in the group
        mdr = report_group[0]

        # Identify the DATA_DESCR reported attribute
        for mda in mdr.metadata:
            if mda.value_for is not None and mda.value_for.id == "DATA_DESCR":
                break

        # Extend DATA_DESCR of `mdr` with values from other reports in `report_group`
        for other_value in filter(
            None, map(partial(_get, mda_id="DATA_DESCR"), report_group[1:])
        ):
            assert isinstance(mda, v21.OtherNonEnumeratedAttributeValue)
            mda.value = (mda.value or "") + "\n\n" + other_value

        # Replace the ID of `mdr` with a new, unique DFD ID including the country code
        assert mdr.attaches_to is not None
        cast(
            "v21.TargetIdentifiableObject", mdr.attaches_to.key_values["DATAFLOW"]
        ).obj.id = unique_dfd_id(mdr, all_dfd_ids)

        sort_last.append(mdr)

    mds.report.extend(sort_last)

    log.info(f"Appended {len(mds.report) - N} metadata reports for ATO data flows")

    # Restore log level
    logging.getLogger("sdmx").setLevel(logging.WARNING)
