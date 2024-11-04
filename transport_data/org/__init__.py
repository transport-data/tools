"""Information about the TDCI *per se*."""

from datetime import date
from itertools import chain
from typing import TYPE_CHECKING, Union

import sdmx.model.v21 as m

from transport_data import STORE as registry
from transport_data.util.pluggy import hookimpl, pm

if TYPE_CHECKING:
    import sdmx.model.v21


@hookimpl
def get_agencies() -> "sdmx.model.v21.Agency":
    """Return agencies and organizations including and subsidiary to TDCI itself."""
    # Agency
    a1 = m.Agency(
        id="TDCI",
        name="Transport Data Commons Initiative",
        description="See https://transport-data.org",
    )
    c1 = m.Contact(
        responsibility="Organization team",
        email=["kirsten.orschulok@giz.de", "verena.knoell@giz.de"],
        uri=["https://transport-data.org"],
    )
    a1.contact.append(c1)

    a2 = m.Agency(id="EPT", name="Expert Prototype Team")

    c2 = m.Contact(
        name="Paul Natsuo Kishimoto",
        email=["mail@paul.kishimoto.name"],
        responsibility="Admin for https://github.com/transport-data",
    )
    c3 = m.Contact(name="Marie Colson", email=["marie.colson@ifeu.de"])
    c4 = m.Contact(name="Pierpaolo Cazzola", email=["pierpaolo.cazzola@gmail.com"])
    c5 = m.Contact(name="James Dixon", email=["james.dixon@ouce.ox.ac.uk"])
    c6 = m.Contact(name="Dominic Sheldon", email=["dominic.sheldon@ricardo.com"])
    c7 = m.Contact(name="Alex Blackburn", email=["blackburna@un.org"])
    c8 = m.Contact(name="François Cuenot", email=["francois.cuenot@un.org"])
    a2.contact.extend([c2, c3, c4, c5, c6, c7, c8])

    a1.append_child(a2)

    return a1, a2


def get_agencyscheme(version: Union[None, str] = None) -> "sdmx.model.v21.AgencyScheme":
    """Generate an AgencyScheme including some TDCI data providers."""
    as_ = m.AgencyScheme(
        id="TDCI",
        # NameableArtefact
        name="Transport Data Commons Initiative partners and participants",
        # VersionableArtefact
        valid_from=date.today().isoformat(),
        # MaintainableArtefact
        maintainer=None,
    )

    for agency in chain(*pm.hook.get_agencies()):
        as_.append(agency)

    # TDCI itself is the maintainer
    as_.maintainer = as_["TDCI"]

    as_.version = version
    if as_.version is None:
        registry.assign_version(as_, patch=1)

    return as_


def refresh():
    """Refresh the registry with structures from this module."""
    from transport_data import STORE

    as_ = get_agencyscheme()
    STORE.set(as_)
