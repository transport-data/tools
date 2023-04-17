"""Information about the TDC Initiative."""
from datetime import date
from importlib import import_module
from typing import Union

import sdmx.model.v21 as m

from transport_data import registry


def get_agency() -> m.Agency:
    # Agency
    a1 = m.Agency(
        id="TDCI",
        name="Transport Data Commons Initiative",
        description="See https://transport-data.org",
    )

    # Not yet implemented in sdmx1
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


def get_agencyscheme(version: Union[None, str] = None):
    """Generate an AgencyScheme including some TDCI data providers."""
    a = get_agency()

    as_ = m.AgencyScheme(
        id="TDCI",
        # NameableArtefact
        name="Transport Data Commons Initiative partners and participants",
        # VersionableArtefact
        valid_from=date.today().isoformat(),
        # MaintainableArtefact
        maintainer=a[0],
        # ItemScheme
        items=a,
    )

    # Add agencies with corresponding modules in this repository
    for id_ in ("adb", "jrc"):
        module = import_module(f"transport_data.{id_}")
        # Call a function named get_agency() in the module
        as_.append(module.get_agency())

    as_.version = version
    if as_.version is None:
        registry.assign_version(as_)

    return as_
