"""IPCC structural metadata."""

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
    """Generate a code list from the GNGGI, Volume 2, Table 3.1.1.

    The generated code list's URN ends with ``Codelist=TDCI:CL_IPCC_2006_V2_T3.1.1(…)``.

    .. todo:: Expand to include 'Explanation' text from the table as descriptions for
       codes.

    .. todo:: Include internationalized texts (names, descriptions) from the Arabic,
       Chinese, French, Russian, and/or Spanish versions of the documents.
    """
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


def gen_cs_ch3(**kwargs) -> "sdmx.model.common.ConceptScheme":
    """Generate a scheme of concepts included in equations in Chapter 3.

    The generated code list's URN ends with
    ``ConceptScheme=TDCI:CS_IPCC_2006_V2_CH3(…)``.

    .. todo:: Include concepts used as table dimensions.

    .. todo:: Include internationalized texts (names, descriptions) from the Arabic,
       Chinese, French, Russian, and/or Spanish versions of the documents.
    """
    from sdmx.model.common import Annotation, Concept, ConceptScheme

    cs = ConceptScheme(
        id="CS_IPCC_2006_V2_CH3", name="Concepts appearing in equations", **kwargs
    )

    equation, page = "", ""

    def _c(id_, name=None, units=None, description=None):
        c = Concept(
            id=id_,
            name=name,
            description=f"First appears in Equation {equation} on p.{page}",
        )

        if units:
            c.annotations.append(Annotation(id="preferred-units", text=units))
        cs.append(c)

    # §3.2 Road transportation

    equation, page = "3.2.1", "3.12"
    _c(
        "EMI 1",
        "Emissions",
        "kg",
        """Variously "Emissions of CO₂" (Eq. 3.2.1), or of varying species (Eq. 3.2.3, 3.2.5)""",
    )
    _c("Fuel 1", "Fuel sold", "TJ")
    _c("EF 1", "Emission factor", "kg/TJ")
    _c(
        "a",
        "Type of fuel (e.g. petrol, diesel, natural gas, lpg)",
        None,
        "In Eq 3.2.6, 'j' is used for the same concept.",
    )

    equation, page = "3.2.2", "3.12"
    _c(
        "EMI 2",
        "CO₂ Emissions from urea-based additive in catalytic converters",
        "Gg CO₂",
    )
    _c(
        "Activity",
        "amount of urea-based additive consumed for use in catalytic converters",
        "Gg",
    )
    _c(
        "Purity",
        "the mass fraction (=percentage divided by 100) of urea in the urea-based additive",
    )

    # Eq. 3.2.3 —same concepts as 3.2.1

    equation, page = "3.2.4", "3.13"
    _c(
        "Fuel 2",
        "fuel consumed (as represented by fuel sold) for a given mobile source activity",
        "TJ",
    )
    _c(
        "b",
        "vehicle type",
        None,
        "In Eq 3.2.6, 'i' is used for the same concept (e.g., car, bus)",
    )
    _c(
        "c",
        "emission control technology (such as uncontrolled, catalytic converter, etc.)",
    )

    equation, page = "3.2.5", "3.15"
    _c("EF 2", "emission factor", "kg / km")
    _c(
        "Distance 1",
        "distance travelled during thermally stabilized engine operation phase for a given mobile source activity",
        "km",
    )
    _c("C", "emissions during warm-up phase (cold start)", "kg")
    _c(
        "d",
        "operating conditions (e.g. urban or rural road type, climate, or other environmental factors)",
    )

    equation, page = "3.2.6", "3.26"
    _c(
        "Estimated fuel",
        "total estimated fuel use estimated from distance travelled (VKT) data",
        "litre",
    )
    _c("Vehicles", "number of vehicles of type i and using fuel j on road type t")
    _c(
        "Distance 2",
        "annual kilometres travelled per vehicle of type i and using fuel j on road type t",
        "km",
    )
    _c("t", "type of road (e.g., urban, rural)")

    # §3.3 Off-road transportation
    # Eq. 3.3.1 —no additional concepts
    # Eq. 3.3.2 —no additional concepts

    equation, page = "3.3.3", "3.34"
    _c(
        "N",
        "source population",
        None,
        """In Eq. 3.4.3 this is given as 'number of locomotives of type i".""",
    )
    # Ditto below, all used in Eq. 3.4.3
    _c("H", "annual hours of use of vehicle i", "hour")
    _c("P", "average rated power of vehicle i", "kW")
    _c("LF", "typical load factor of vehicle i (fraction between 0 and 1)")
    _c("EF 3", "average emission factor for use of fuel j in vehicle i", "kg / kWh")

    # Eq. 3.3.4 —no additional concepts

    # §3.4 Railways
    # Eq. 3.4.1 —no additional concepts
    # Eq. 3.4.2 —no additional concepts

    equation, page = "3.4.3", "3.42"
    _c("i", "locomotive type and journey type")

    equation, page = "3.4.4", "3.43"
    _c("EF 4", "engine specific emission factor for locomotive of type i", "kg/TJ")
    _c("PWF", "pollutant weighting factor for locomotive of type i", "dimensionless")
    _c("EF 5", "default emission factor for diesel (applies to CH₄, N₂O)", "kg/TJ")

    # §3.6 Civil Aviation
    # Eq. 3.6.1 —no additional concepts

    equation, page = "3.6.2", "3.59"
    _c(
        "Emissions.LTO",
        "",
        None,
        """'LTO' is defined on p.3.56 as "Landing/Take-Off cycle".""",
    )
    _c(
        "Emissions.Cruise",
        "",
        None,
        """'Cruise' is defined on p.3.56 in contrast with 'LTO'.""",
    )

    equation, page = "3.6.3", "3.59"
    _c("Number of LTOs")
    _c("EF.LTO")

    equation, page = "3.6.4", "3.59"
    _c("Fuel consumption.LTO")
    _c("Fuel consumption per LTO")

    equation, page = "3.6.5", "3.59"
    _c("Total Fuel Consumption")
    _c("EF.Cruise")

    return cs


def gen_structures() -> None:
    """Create or update IPCC-maintained structural metadata."""
    from transport_data import STORE, org

    ma_args = dict(
        maintainer=org.get_agency()[0],
        version="0.1",
        is_final=True,
        is_external_reference=False,
    )

    STORE.setdefault(gen_cl_T311(**ma_args))
    STORE.setdefault(gen_cs_ch3(**ma_args))
