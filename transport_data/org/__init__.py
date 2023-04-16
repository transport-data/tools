"""Information about the TDC Initiative."""
from datetime import date

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
    """Generate structure & meta information about TDCI."""
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

    registry.assign_version(as_)

    return as_
