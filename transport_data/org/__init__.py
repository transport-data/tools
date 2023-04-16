"""Information about the TDC Initiative."""
import sdmx.model.v21 as m


def gen_structures():
    """Generate structure & meta information about TDCI."""
    a = m.Agency(
        id="TDCI",
        name="Transport Data Commons Initiative",
        description="See https://transport-data.org",
    )

    # Not implemented in sdmx1
    # a.contact.append(m.Contact(uri="https://transport-data.org"))

    return a
