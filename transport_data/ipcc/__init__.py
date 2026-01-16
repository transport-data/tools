"""Intergovernmental Panel on Climate Change metadata provider."""

from transport_data import hook


@hook
def get_agencies():
    """Return the IPCC :class:`.Agency`."""
    from sdmx.model import common

    a = common.Agency(
        id="IPCC",
        name="Intergovernmental Panel on Climate Change",
        description="https://www.ipcc.ch/",
    )
    return (a,)


@hook
def provides():
    return (
        "Codelist=TDCI:CL_IPCC_2006_V2_T3.1.1",
        "ConceptScheme=TDCI:CS_IPCC_2006_V2_CH3",
    )
