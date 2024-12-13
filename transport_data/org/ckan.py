""":class:`.ckan.Client` objects to access TDC instances."""

import typing
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, Optional

import click

from transport_data.util.ckan import Client, ModelProxy, Package
from transport_data.util.sdmx import fields_to_mda

if TYPE_CHECKING:
    import uuid

    from sdmx.model import v21

#: Development instance of TDC CKAN. Accessible as of 2024-11-27.
DEV = Client("https://ckan.tdc.dev.datopian.com", id="dev")

#: Production instance of TDC CKAN. Accessible as of 2024-11-27.
PROD = Client("https://ckan.transport-data.org", id="prod")

#: Staging instance of TDC CKAN. Not accessible as of 2024-11-27; SSL certificate error.
STAGING = Client("https://ckan.tdc.staging.datopian.com", id="staging")


@dataclass
class CKANMetadataReportStructure:
    """Concepts in the CKAN metadata for a :class:`Package`."""

    #: JSON data
    #:
    #: This is optional. If used, it contains the JSON content returned by the CKAN API.
    #: This **must** be identical to the values appearing in the other fields.
    JSON: dict

    author: Optional[str]
    author_email: Optional[str]
    contributors: list
    creator_user_id: "uuid.UUID"
    data_access: str
    data_provider: str
    dimensioning: str
    frequency: str
    geographies: list
    groups: list
    id: "uuid.UUID"
    indicators: list
    is_archived: bool
    isopen: bool
    language: str
    license_id: str
    license_title: str
    license_url: str
    maintainer: Optional[str]
    maintainer_email: Optional[str]
    metadata_created: str
    metadata_modified: str
    modes: list
    name: str
    notes: str
    num_resources: int
    num_tags: int
    organization: list
    owner_org: "uuid.UUID"
    private: bool
    regions: list
    relationships_as_object: list
    relationships_as_subject: list
    resources: list
    sectors: list
    services: list
    sources: list
    state: str
    tags: list
    tdc_category: str
    temporal_coverage_end: str
    temporal_coverage_start: str
    title: str
    type: str
    units: list
    url: str
    version: Optional[str]


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

    fields_to_mda(CKANMetadataReportStructure, rs, cs)

    STORE.set(msd)
    STORE.set(cs)

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
            "uuid.UUID": str,
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


@click.command("ckan")
@click.option(
    "--instance",
    type=click.Choice(["dev", "prod", "staging"]),
    default="prod",
    help="TDC CKAN instance to query.",
)
@click.option("--verbose", "-v", is_flag=True, help="Show more output.")
@click.argument("action")
@click.argument("args", nargs=-1)
def main(instance, verbose, action, args):
    """Interact with the TDC CKAN instance via its API.

    ACTION is the ID of one of endpoints of the CKAN Action API, for instance "tag_show"
    or "package_list". ARGS are a space-separated list of key=value pairs, for instance
    "sort=title limit=10".

    See https://docs.ckan.org/en/latest/api/ for the list and further documentation, or
    use the "help_show" endpoint, for example:

        tdc ckan help_show name=package_search

    For some endpoints, the output is formatted. For all others, the raw JSON response
    is shown.
    """
    client: Client = {"dev": DEV, "prod": PROD, "staging": STAGING}[instance]

    # Parse key=value args to dictionary
    data_dict = {key: value for key, _, value in map(lambda s: s.partition("="), args)}

    try:
        result = getattr(client, action)(**data_dict)
    except Exception as e:
        print(repr(e))
        return False

    if action.endswith("_list"):
        for i, obj in enumerate(result, start=1):
            print(f"{i:3d}. {obj}")
    elif isinstance(result, str):
        print(result)
    else:
        print(repr(result))
        if verbose and isinstance(result, ModelProxy):
            print(result.asdict())
