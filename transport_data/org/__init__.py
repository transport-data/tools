"""Information about the TDC Initiative."""
from datetime import date
from importlib import import_module

import sdmx.model.v21 as m

from transport_data import registry


def get_agency() -> m.Agency:
    # Agency
    a = m.Agency(
        id="TDCI",
        name="Transport Data Commons Initiative",
        description="See https://transport-data.org",
    )

    # Not yet implemented in sdmx1
    # a.contact.append(m.Contact(uri="https://transport-data.org"))

    return a


def get_agencyscheme(increment_version=False):
    """Generate an AgencyScheme including some TDCI data providers."""
    a = get_agency()

    as_ = m.AgencyScheme(
        id="TDCI",
        # NameableArtefact
        name="Transport Data Commons Initiative partners and participants",
        # VersionableArtefact
        valid_from=date.today().isoformat(),
        # MaintainableArtefact
        maintainer=a,
        items=[a],
    )

    # Add agencies with corresponding modules in this repository
    for id_ in ("adb", "jrc"):
        module = import_module(f"transport_data.{id_}")
        # Call a function named get_agency() in the module
        as_.append(module.get_agency())

    registry.assign_version(as_)

    return as_
