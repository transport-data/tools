"""SUM4All structural metadata."""

import sdmx.model.v21 as m


def get_cs_indicator():
    from transport_data import STORE, org

    from . import get_agencies

    a_SUM4ALL = get_agencies()[0]
    a_TDCI, *_ = org.get_agencies()[0]

    cs = m.ConceptScheme(
        maintainer=a_TDCI,
        id=f"{a_SUM4ALL.id}_INDICATOR",
        name="Elementary Global Tracking Framework for Transport",
        description="""Transcribed from “Global Mobility Report 2017: Tracking Sector Performance” https://hdl.handle.net/10986/28542, Annex I, pp.95–102.""",
    )

    parent = None
    type_ = None

    def _c(**kwargs):
        """Shorthand for adding to `cs`."""
        annotations = []
        if type_:
            annotations.append(m.Annotation(id="sum4all-indicator-type", text=type_))

        concept = m.Concept(**kwargs, annotations=annotations)
        if parent:
            parent.append_child(concept)
        cs.items[concept.hierarchical_id] = concept

        return concept

    parent = UA = _c(
        id="UA",
        name="Universal access",
        description="Global Objective: Ensure for all equitable access to economic and social opportunities by 2030",
    )

    type_ = "principal"
    _c(
        id="PI1",
        name="Proportion of the rural population who live within 2 km of all-season road (SDG 9.1.1)",
    )
    _c(
        id="PI2",
        name="Proportion of population that has convenient access to public transport, by age, sex and persons with disabilities (SDG 11.2.1)",
    )

    # “Supporting indicator”
    type_ = "supporting"
    parent = _c(id="1", name="Quality of roads")
    _c(id="1.1", name="Quality of roads [value: 1= worst to 7 = best]")
    _c(id="1.2", name="Quality of roads [rank]")

    parent = UA
    parent = _c(id="2", name="Quality of railroad infrastructure")
    _c(
        id="2.1",
        name="Quality of railroad infrastructure [value: 1= worst to 7 = best]",
    )
    _c(id="2.2", name="Quality of railroad infrastructure [rank]")

    parent = UA
    parent = _c(id="3", name="Quality of port infrastructure")
    _c(
        id="3.1",
        name="Quality of port infrastructure [value: 1= worst to 7 = best]",
    )
    _c(id="3.2", name="Quality of port infrastructure [rank]")

    parent = UA
    parent = _c(id="4", name="Quality of air transport infrastructure")
    _c(
        id="4.1",
        name="Quality of air transport infrastructure [value: 1= worst to 7 = best]",
    )
    _c(id="4.2", name="Quality of air transport infrastructure [rank]")

    parent = UA
    parent = _c(id="5", name="Passenger volume by mode of transport")
    _c(id="5.1", name="Railways, passengers carried (million passenger-km)")
    _c(id="5.2", name="Air Transport, passengers carried")

    parent = UA
    parent = _c(
        id="6",
        name="Proportion of rural roads in “good and fair condition” (as developed by new RAI)*",
    )
    _c(id="7", name="Percentage of markets accessible by all-season road*")
    _c(
        id="8",
        name="Percentage of national government budget spent on low volume rural transport infrastructure*",
    )
    _c(
        id="9",
        name="Percentage of the rural population with access to affordable and reliable passenger transport services*",
    )
    _c(
        id="10",
        name="Ratio of national to local passenger transport fares (collection of data on rural passenger transport US$ per km for short distance and long distance trips which would be disaggregated by most common modes e.g. bus, motorbike, other IMT)*",
    )
    _c(
        id="11",
        name="Percentage of household monthly expenditure spent on transport*",
    )
    _c(
        id="12",
        name="Percentage of rural population with at least daily transport service – from Living Standards Surveys (LSS)*",
    )
    _c(
        id="13",
        name="Percentage of households that make one motorized trip per month*",
    )
    _c(
        id="14",
        name="Length of public transport lines (particularly high capacity but also informal public transport if possible) per area, dedicated bicycle lane and side walk coverage (this parameter will also help to determine urban density i.e. people / sq km)*",
    )
    _c(
        id="15",
        name="Vehicle fleets per motorized transport mode (public transport and all other modes, such as, taxis and shared taxis, informal / paratransit (if possible) and motor cars, motorized two-wheelers (annual update)*",
    )
    _c(
        id="16",
        name="Number of public transport journeys by mode of transport (annual update)*",
    )
    _c(
        id="17",
        name="Vehicle km offered per public transport mode (annual update)*",
    )
    _c(
        id="18",
        name="Number of public transport stops per area (annual update)*",
    )
    _c(
        id="19",
        name="Percentage of the population within 500 m of a frequent public transport stop/station*",
    )
    _c(
        id="20",
        name="Average income (percent) per resident spent on transport (affordability)*",
    )
    _c(
        id="21",
        name="Modal share of different passenger modes in the city (public transport, walking, cycling, private vehicles and motorcycles and taxis, including informal / paratransit if possible). The aim should be to increase use of sustainable transport modes. Consideration should also be given to applying this to freight transport. (inter-modality)*",
    )
    _c(
        id="22",
        name="Passenger km travelled by public transport by mode of transport (annual update) – using this indicator the average length of public transport journeys (Tier 1) can also be assessed. (inter-modality)*",
    )
    _c(id="23", name="Goods VKM travelled in the city per capita (freight)*")
    _c(
        id="24",
        name="Percentage of jobs and urban services accessible within 60 minutes by each transport mode in the city*",
    )
    _c(
        id="25",
        name="Accessibility of the public transport network to persons with disabilities / vulnerable situations (percent of vehicles allowing wheelchair access, percent of stations / network with step free access etc.) (usability)*",
    )
    _c(
        id="26",
        name="Reduction in the percentage of women who are deterred by fear of crime from getting to and from public transport. (usability)*",
    )

    parent = SE = _c(
        id="SE",
        name="System efficiency",
        description="""Global Objective: Increase the efficiency of transport systems by 2030

Target: TBD (Meet the demand for mobility at the least possible cost for society)""",
    )

    # “Principal indicator”
    type_ = "principal"
    _c(id="PI", name="Connectivity index")

    # “Supporting Indicator”
    type_ = "supporting"
    _c(
        id="1",
        name="Energy consumption of transport relative to GDP (PPP) (GOE per dollar)",
    )
    parent = _c(
        id="2",
        name="Logistics performance Index – Customs Clearance Component",
    )
    _c(
        id="2.1",
        name="Logistics performance index – customs [value: 1=low to 5=high]",
    )
    _c(id="2.2", name="Logistics performance index – customs [rank]")

    parent = SE
    parent = _c(id="3", name="Good Governance Index – under influence component")
    _c(
        id="3.1",
        name="Good Governance Index – Under Influence [value: 1=worst to 7=best]",
    )
    _c(id="3.2", name="Good Governance Index – Under Influence [rank]")

    parent = SE
    _c(id="4", name="Air and linear shipping connectivity index")
    parent = _c(id="5", name="Freight volumes by mode of transport")
    _c(id="5.1", name="Freight volume by air transport (ton-km)")
    _c(id="5.2", name="Mail volumes by air transport (ton km)")
    _c(id="5.3", name="Freight volumes by road transport (ton-km)")
    _c(id="5.4", name="Freight volumes by road transport (ton-km)")
    _c(
        id="5.5",
        name="Container port traffic (TEU: 20 foot equivalent units)",
    )

    parent = SE
    _c(id="6", name="Accession to the UN transport conventions")
    _c(id="7", name="Truck Licensing Index (0-11)")
    _c(id="8", name="Freight connectivity*")
    _c(
        id="9",
        name="Percentage of agricultural potential connected to a major port or market by a certain road category within a given time period*",
    )
    _c(id="10", name="Rail lines*")
    _c(id="11", name="Average age of vehicle fleet*")

    parent = S = _c(
        id="S",
        name="Safety",
        description="""Global Objective: Improve safety of mobility across transport modes

Target:
1. Halve the number of global deaths and injuries from road traffic accidents by 2020 (SDG target 3.6)
2. Reduce by 5 percent the fatalities and injuries in each other mode of transport (waterborne, air, and rail transport) by 2020""",
    )

    type_ = "principal"
    _c(
        id="1",
        name="Number of deaths and injuries from road traffic accidents by 2020 (absolute number)",
    )
    _c(
        id="2",
        name="Number of fatalities and injuries in each mode of transport (waterborne, air, and rail transport)",
    )

    type_ = "supporting"
    parent = _c(id="1", name="Distribution of road deaths by use type")
    _c(id="1.1", name="Death by road user category – 4-wheeler [%]")
    _c(id="1.2", name="Death by road user category – 2- or 3-wheeler [%]")
    _c(id="1.3", name="Death by road user category – cyclist [%]")
    _c(id="1.4", name="Death by road user category – pedestrian [%]")
    _c(id="1.5", name="Death by road user category – others [%]")

    parent = S
    parent = _c(id="2", name="Indicators for overall transport sector:")
    _c(
        id="2.1",
        name="Increase in modal shift for safer and efficient modes of transport in urban areas (safer modes: mass transit, rail transport, metro, BRT) and increase walking and biking providing safe facilities for them as they are the most efficient and equitable modes of transportation*",
    )
    _c(
        id="2.2",
        name="Decrease in number of fatalities and serious injuries among pedestrians and cyclists, while increasing their mode share in urban areas*",
    )

    parent = S
    parent = _c(id="3", name="Indicators for road safety:")
    _c(
        id="3.1",
        name="Progress with 5 Pillars of Road Safety as defined in Global Plan and WHO´s document on road safety targets and indicators1*",
    )
    _c(
        id="3.2",
        name="% of existing roads that have safety rating or high-risk spots or sections identified and improved in each country*",
    )
    _c(
        id="3.3",
        name="Countries that have compulsory road safety audits and inspections or minimum star rating standards for new roads*",
    )
    _c(
        id="3.4",
        name="Countries that have speed limits consistent with safe system principles*",
    )
    _c(
        id="3.5",
        name="Number of cities (more than 500.000 inhabitants) that have road safety plans consistent with safe systems and focus in particular on (of) vulnerable users*",
    )
    _c(id="3.6", name="Number of national Road Safety lead agencies*")
    _c(
        id="3.7",
        name="Effective legislation and enforcement of key road safety legislation*",
    )
    _c(
        id="3.8",
        name="Countries acceding to each core UN convention on road safety*",
    )
    _c(
        id="3.9",
        name="Countries with road safety crash mitigation protocols*",
    )
    _c(
        id="3.10",
        name="Countries with licensing processes for all drivers that include written and practical examination (cars, trucks, motorized two-wheelers, professional drivers)*",
    )
    _c(id="3.11", name="Number of countries with a sound crash database*")

    parent = S
    parent = _c(id="4", name="Indicators for aviation:")
    _c(
        id="4.1",
        name="Number of fatalities in scheduled commercial air transport*",
    )
    _c(
        id="4.2",
        name="Countries having implemented an effective safety oversight system*",
    )
    _c(
        id="4.3",
        name="Countries having implemented an effective State Safety Program*",
    )

    parent = S
    parent = _c(id="5", name="Indicators for rail transport:")
    _c(
        id="5.1",
        name="Number of countries that have a specific safety railroad department or administration*",
    )
    _c(
        id="5.2",
        name="Number of railways that have a Safety Management System (SMS) in place*",
    )
    _c(
        id="5.3",
        name="Number of countries that have an effective safety protocol or regional rail safety agreements*",
    )
    _c(
        id="5.4",
        name="Number of train and passenger train operators with guidelines for emergency response/preparedness*",
    )
    _c(
        id="5.5",
        name="Number of countries that have active programs to promote safety in the road/rail level crossing*",
    )
    _c(
        id="5.6",
        name="Number of countries that have active programs to prevent trespasser crashes*",
    )

    parent = S
    _c(id="6", name="Indicators for waterborne transport:")
    _c(
        id="6.1",
        name="Maritime casualties*",
        description="Mislabeled in the original as ‘7.1’ without any parent item ‘7’",
    )

    parent = GM = _c(
        id="GM",
        name="Green mobility",
        description="""Shift transport systems to low polluting (GHG/air/noise) and climate resilient path.

Sub-Objective 1: Reduce global transport sector GHG emissions as consistent with limiting global average temperature increase to well below 2 degrees Celsius above pre-industrial levels by 2050.
Target: 3-6 GT CO2e by 2050 (absolute in aggregate; specific targets to be determined for each sub-sector/income level)

Sub-Objective 2: Strengthen resilience and adaptive capacity of transport systems to climate-related hazards and natural disasters in all countries.
Target: (X countries) taking actions to reduce vulnerability by 2030 and (Y countries) by 2050.

Sub-Objective 3: Substantially reduce premature deaths and illnesses from air pollution and physical inactivity due to transport-related sources and choices.
Target: (A) 50 percent reduction by 2030 compared to 2010 baseline (relative) or (B) fewer than 60,000 deaths by 2030 (absolute); and (C) percentage of adults walking or cycling for transport increased by 20 percent by 2030

Sub-Objective 4: Substantially reduce global mortality and burden of disease from transport-related noise levels.
Target: Number of urban dwellers exposed to excessive noise levels reduced by 50 percent by 2030""",
    )

    type_ = "principal"
    _c(
        id="1",
        name="Global GHG emissions from the transport sector (GT CO2e), disaggregated by purpose (pkm and tkm), income (HIC, MIC, and LIC), and mode (cars, 2- and 3- wheelers, light commercial vehicles, medium and heavy trucks, buses, and minibuses, domestic and international aviation, and domestic and international shipping)",
    )
    _c(
        id="2",
        name="Number of countries that have taken intentional action to build resilience against climate-related hazards and national disasters within the transport sector",
    )
    _c(
        id="3",
        name="Annual premature deaths due to air pollution and physical inactivity from transport-related sources (# of deaths/year)",
    )
    _c(
        id="4",
        name="Percentage of urban dwellers exposed to Lden/Lnight noise levels from transport above 55dB/40dB (percent of total inhabitants)",
    )

    type_ = "supporting"
    _c(id="1", name="Transport-related GHG emissions (million tonnes)")
    _c(
        id="2",
        name="CO2 emission from transport relative to GDP (PPP) (kg per dollar)",
    )
    _c(
        id="3",
        name="CO2 emission from road transport relative to GDP (PPP) (kg per dollar)",
    )
    _c(
        id="4",
        name="PM 2.5 Air pollution, mean annual exposure (micrograms per cubic meter)",
    )
    _c(
        id="5",
        name="PM 2.5 Air pollution, population exposed to levels exceeding WHO guideline value (% total)",
    )

    parent = _c(id="6", name="Indicators of Climate Change Mitigation")
    _c(
        id="6.1",
        name="(SDG 9.4.1) GHG emissions from transport per unit of value added (MT CO2e/unit GDP, calculated from transport UNFCCC/IEA emissions data and World Bank GDP growth data)*",
    )
    _c(
        id="6.2",
        name="Low emission vehicle share of light-duty 4-wheel and motorized 2-wheel vehicle sales, (percent of total sales, calculated from OICA vehicle sales data and IEA electric vehicle data)*",
    )
    _c(
        id="6.3",
        name="Share of alternative fuels in transport (by gCO2e/MJ for each fuel type), (% of total fuels, calculated from IEA biofuels data and electric vehicle data)*",
    )
    _c(
        id="6.4",
        name="Modal share of passenger transport (by private transport, public transport, walking, cycling, air), (percent of total pkm, calculated from UITP Mobility in Cities database)*",
    )
    _c(
        id="6.5",
        name="Modal share of freight transport (by rail, water, air, road), (percent of total tkm, calculated from World Bank freight data) *",
    )
    _c(
        id="6.6",
        name="Average trip length per country (by passenger transport and freight transport mode), (km)*",
    )

    parent = GM
    parent = _c(id="7", name="Indicators for Climate Change Adaptation")
    _c(
        id="7.1",
        name="Incidents/climate change related disasters/losses/damages/disruptions to transport service (number of total incidents, data sources TBD)*",
    )
    _c(
        id="7.2",
        name="Time and GDP loss due to climate-related disruptions to service (minutes and $/year, data sources TBD)*",
    )
    _c(
        id="7.3",
        name="Investment in retrofitting existing transport infrastructure investments to withstand extreme climate conditions or climate disasters ($, calculated from MDB/IFI transport investment data)*",
    )
    _c(
        id="7.4",
        name="Percentage of new transport infrastructure investments designed to withstand extreme climate conditions or climate disasters (% total infrastructure, calculated from MDB/IFI transport investment data)*",
    )
    _c(
        id="7.5",
        name="Percentage of countries or transport companies that have adopted adaptation plans that cover transport infrastructure (% total countries/companies, calculated from UNFCCC NAPs/NAPAs, available private sector data sources)*",
    )
    _c(
        id="7.6",
        name="Percentage of countries, sub-national regions, and cities with structured vulnerability assessments incorporated into the road and transport management systems (% total countries/sub-national regions/cities, calculated from available data from national, subnational and corporate networks)",
    )

    parent = GM
    parent = _c(id="8", name="Indicators for Air Quality and Physical Activity")
    _c(
        id="8.1",
        name="Emissions of PM10, PM2.5, black carbon, NOx, SOx, and VOCs from passenger and freight vehicles (tonnes/year, calculated from WHO/World Bank data)*",
    )
    _c(
        id="8.2",
        name="Percentage of cities with air quality levels in compliance with WHO guideline values disaggregated by type (PM10 and PM2.5) and income (HIC, MIC, and LIC) (% of all cities, calculate",
    )
    _c(
        id="8.3",
        name="Share of countries with Euro 6 equivalent vehicle emission standards in place for light-duty and heavy-duty vehicles, disaggregated by income (HIC, MIC, and LIC) (% of all countries, calculated from UNEP/Partnership for Clean Fuels and Vehicles data)*",
    )
    _c(
        id="8.4",
        name="Share of countries with low-sulphur (max 50 ppm) and ultra-low-sulphur (max 10 ppm) standards for gasoline and diesel, disaggregated by mode (land, maritime transport) income (HIC, MIC, and LIC) (% of all countries, calculated from UNEP/Partn",
    )
    _c(
        id="8.5",
        name="Average minutes per day walked or cycled by adults for transport (minutes/day)",
    )
    _c(
        id="8.6",
        name="Percentage of adolescents walking or cycling for transport to school (%)",
    )
    _c(
        id="8.7",
        name="Average minutes per day walked or cycled by adolescent for transport to school (minutes/day)",
    )

    parent = GM
    parent = _c(id="9", name="Indicators for Noise Pollution:")
    _c(
        id="9.1",
        name="Percent change in average noise level for cars/vans (% dB, from WHO/EEA and other available time series data)*",
    )
    _c(
        id="9.2",
        name="Percent change in average noise level for lorries/buses (% dB, from WHO/EEA and other available time series data)*",
    )
    _c(
        id="9.3",
        name="Percent change in average vehicle noise (axel, engine, exhaust, tires) inside agglomerations (% dB, from WHO/EEA and other available time series data)*",
    )
    _c(
        id="9.4",
        name="Percent change in average tire noise outside agglomerations (% dB, from WHO/EEA and other available time series data)*",
    )
    _c(
        id="9.5",
        name="Reduction in average vehicle noise (axel, engine, exhaust, tires) inside agglomerations (dB)*",
    )
    _c(
        id="9.6",
        name="Highest vehicle noise level under any operating conditions (dB, calculated from OICA and other available data)*",
    )

    STORE.set(cs)

    return cs
