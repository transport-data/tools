"""Institute for Transport & Development Policy (ITDP) provider."""

from transport_data.util.pluggy import hookimpl


@hookimpl
def get_agencies():
    from sdmx.model import common

    a = common.Agency(
        id="ITDP",
        name="Institute for Transportation and Development Policy",
        contact=[common.Contact(email=["data@itdp.org"], uri=["https://itdp.org"])],
    )

    return (a,)
