from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sdmx.model.common


@lru_cache
def get_agency() -> "sdmx.model.common.Agency":
    """Return the IPCC :class:`.Agency`."""
    from sdmx.model import v21

    return v21.Agency(
        id="IPCC",
        name="Intergovernmental Panel on Climate Change",
        description="https://www.ipcc.ch/",
    )


def gen_cl_T311(**kwargs) -> "sdmx.model.Common.Codelist":
    """Generate a code list from the GNGGI, Volume 2, Table 3.1.1."""
    from sdmx.model.common import Code, Codelist

    cl = Codelist(
        id="CL_IPCC_2006_V2_T3.1.1",
        name="Detailed sector split for the Transport sector",
        description="""Transcribed from 2006 IPCC Guidelines for National Greenhouse Gas Inventories — Volume 2: Energy — Chapter 3: Mobile Combustion — Table 3.1.1, using the file https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_3_Ch3_Mobile_Combustion.pdf, as linked from https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol2.html.

This version includes the 'Explanation' text from the table as the description for individual codes, but at the moment only for the code 1 A 3. For others, see the source document.""",
        **kwargs,
    )

    # The codes have well-formed, hierarchical IDs, so it is possible to infer the ID of
    # the parent code, if it exists.
    def _c(id_, name, description=None):
        """Shorthand for adding to `cl`."""
        try:
            parent = cl[" ".join(id_.split()[:-1])]
        except KeyError:
            parent = None

        cl.append(Code(id=id_, name=name, description=description, parent=parent))

    _c(
        "1 A 3",
        "TRANSPORT",
        """Emissions from the combustion and evaporation of fuel for all transport activity (excluding military transport), regardless of the sector, specified by sub-categories below.

Emissions from fuel sold to any air or marine vessel engaged in international transport (1 A 3 a i and 1 A 3 d i) should as far as possible be excluded from the totals and subtotals in this category and should be reported separately.""",
    )
    _c("1 A 3 a", "Civil Aviation")
    _c("1 A 3 a i", "International Aviation (International Bunkers)")
    _c("1 A 3 a ii", "Domestic Aviation")
    _c("1 A 3 b", "Road Transportation")
    _c("1 A 3 b i", "Cars")
    _c("1 A 3 b i 1", "Passenger cars with 3-way catalysts")
    _c("1 A 3 b i 2", "Passenger cars without 3-way catalysts")
    _c("1 A 3 b ii", "Light duty trucks")
    _c("1 A 3 b ii 1", "Light-duty trucks with 3-way catalysts")
    _c("1 A 3 b ii 2", "Light-duty trucks without 3-way catalysts")
    _c("1 A 3 b iii", "Heavy duty trucks and buses")
    _c("1 A 3 b iv", "Motorcycles")
    _c("1 A 3 b v", "Evaporative emissions from vehicles")
    _c("1 A 3 b vi", "Urea-based catalysts")
    _c("1 A 3 c", "Railways")
    _c("1 A 3 d", "Water-borne Navigation")
    _c("1 A 3 d i", "International water-borne navigation (International bunkers)")
    _c("1 A 3 d ii", "Domestic water-borne Navigation")
    _c("1 A 3 e", "Other Transportation")
    _c("1 A 3 e i", "Pipeline Transport")
    _c("1 A 3 e ii", "Off-road")
    _c("1 A 4 c iii", "Fishing (mobile combustion)")
    _c("1 A 5 a", "Non specified stationary")
    _c("1 A 5 b", "Non specified mobile")

    return cl


def gen_structures() -> None:
    """Create or update IPCC-maintained structural metadata.

    The structures have URNs like ``TDCI:CS_IPCC_{NAME}(0.1)``
    """
    from transport_data import STORE, org

    def _make_id(value: str) -> str:
        return f"{get_agency().id}_{value}"

    ma_args = dict(
        maintainer=org.get_agency()[0],
        version="0.1",
        is_final=True,
        is_external_reference=False,
    )

    STORE.setdefault(gen_cl_T311(**ma_args))
