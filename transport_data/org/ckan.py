""":class:`.ckan.Client` objects to access TDC instances."""

import typing
from functools import lru_cache
from typing import TYPE_CHECKING, Optional

from transport_data.util.ckan import Client, Package

if TYPE_CHECKING:
    from sdmx.model import v21

#: Development instance of TDC CKAN. Accessible as of 2024-11-27.
DEV = Client("https://ckan.tdc.dev.datopian.com")

#: Production instance of TDC CKAN. Accessible as of 2024-11-27.
PROD = Client("https://ckan.transport-data.org")

#: Staging instance of TDC CKAN. Not accessible as of 2024-11-27; SSL certificate error.
STAGING = Client("https://ckan.tdc.staging.datopian.com")


#: Concepts in the CKAN metadata for a :class:`Package`.
CONCEPTS = {
    # Special
    "JSON": ("…", None),
    # Corresponding to JSON fields
    "author": ("", Optional[str]),
    "author_email": ("", Optional[str]),
    "contributors": ("", list),
    "creator_user_id": ("", str),
    "data_access": ("", str),
    "data_provider": ("", str),
    "dimensioning": ("", str),
    "frequency": ("", str),
    "geographies": ("", list),
    "groups": ("", list),
    "id": ("", str),
    "indicators": ("", list),
    "is_archived": ("", bool),
    "isopen": ("", bool),
    "language": ("", str),
    "license_id": ("", str),
    "license_title": ("", str),
    "license_url": ("", str),
    "maintainer": ("", Optional[str]),
    "maintainer_email": ("", Optional[str]),
    "metadata_created": ("", str),
    "metadata_modified": ("", str),
    "modes": ("", list),
    "name": ("", str),
    "notes": ("", str),
    "num_resources": ("", int),
    "num_tags": ("", int),
    "organization": ("", list),
    "owner_org": ("", str),  # UUID
    "private": ("", bool),
    "regions": ("", list),
    "relationships_as_object": ("", list),
    "relationships_as_subject": ("", list),
    "resources": ("", list),
    "sectors": ("", list),
    "services": ("", list),
    "sources": ("", list),
    "state": ("", str),
    "tags": ("", list),
    "tdc_category": ("", str),
    "temporal_coverage_end": ("", str),
    "temporal_coverage_start": ("", str),
    "title": ("", str),
    "type": ("", str),
    "units": ("", list),
    "url": ("", str),
    "version": ("", Optional[str]),
}


@lru_cache
def get_msd() -> "v21.MetadataStructureDefinition":
    """Generate and return an MSD containing all of the CKAN fields."""
    from sdmx.model import common, v21

    from transport_data import STORE
    from transport_data.org import get_agencyscheme

    TDCI = get_agencyscheme()["TDCI"]

    cs = common.ConceptScheme(id="CKAN_METADATA_CONCEPTS", maintainer=TDCI)
    msd = v21.MetadataStructureDefinition(id="CKAN", version="1", maintainer=TDCI)
    rs = msd.report_structure["ALL"] = v21.ReportStructure(id="ALL")

    for id_, (description, data_type) in CONCEPTS.items():
        ci = cs.setdefault(id=id_, description=description)
        type_anno = common.Annotation(id="data-type", text=repr(data_type))
        rs.getdefault(id_, concept_identity=ci, annotations=[type_anno])

    STORE.set(msd)

    return msd


def ckan_package_to_mdr(p) -> "v21.MetadataReport":
    """Convert a :class:`.Package` instance to a MetadataReport."""
    from sdmx.model import v21

    msd = get_msd()

    mdr = v21.MetadataReport()

    ONEAV = v21.OtherNonEnumeratedAttributeValue

    for mda in msd.report_structure["ALL"]:
        av = ONEAV(value_for=mda)
        if mda.id == "JSON":
            av.value = repr(p.asdict())
        else:
            value = getattr(p, mda.id)
            av.value = value if isinstance(value, str) else repr(value)
        mdr.metadata.append(av)

    return mdr


def mdr_to_ckan_package(mdr):
    """Convert a MetadataReport to a :class:`.Package` instance."""
    data = {}
    # Iterate over reported attributes
    for ra in mdr.metadata:
        mda = ra.value_for  # The MetadataAttribute for which this

        # Don't store the raw JSON
        # TODO Branch within this function: either use the "JSON" attribute directly and
        #      ignore all other reported attributes, or vice versa
        if mda.id == "JSON":
            continue

        # Determine the data type from a "data-type" annotation on the MetadataAttribute
        dt_anno = mda.eval_annotation(id="data-type", globals=dict(typing=typing))
        data_type = {
            "<class 'bool'>": bool,
            "<class 'int'>": int,
            "<class 'list'>": list,
            "<class 'str'>": str,
        }.get(dt_anno, dt_anno)

        # Convert the string representation of the value to its Python/JSON data
        # structure
        if data_type is None:
            raise NotImplementedError
        elif data_type in (bool, list):
            data[ra.value_for.id] = eval(ra.value)
        elif data_type is Optional[str]:
            data[ra.value_for.id] = None if ra.value == "None" else str(ra.value)
        else:
            data[ra.value_for.id] = data_type(ra.value)

    return Package(data)
