"""Institute for Transport & Development Policy (ITDP) provider."""

from transport_data import hook


@hook
def cli_modules():
    return f"{__name__}.cli"


@hook
def get_agencies():
    from sdmx.model import common

    a = common.Agency(
        id="ITDP",
        name="Institute for Transportation and Development Policy",
        contact=[common.Contact(email=["data@itdp.org"], uri=["https://itdp.org"])],
    )

    return (a,)
