"""European Commission Joint Research Centre (JRC) provider.

This module handles data from the JRC IDEES 2015 source.

"Handle" includes:

- Fetch
- Extract
- Parse the native spreadsheet layout.
- Convert to SDMX.

"""
import re
from collections import defaultdict
from functools import partial
from itertools import chain, count
from operator import add
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import sdmx.model.v21 as m

from transport_data import STORE as registry
from transport_data.util.pooch import Pooch
from transport_data.util.sdmx import anno_generated


def get_agency() -> m.Agency:
    """Return information about the agency providing the data set.

    See :func:`.org.get_agencyscheme`.
    """
    # Agency
    a = m.Agency(
        id="JRC",
        name="Joint Research Centre of the European Commission",
        description="""See https://joint-research-centre.ec.europa.eu/index_en.

Maintainers of the IDEES data set: https://data.jrc.ec.europa.eu/dataset/jrc-10110-10001""",  # noqa: E501
    )

    a.contact.append(
        m.Contact(name="Jacopo Tattini", email=["Jacopo.TATTINI@ec.europa.eu"])
    )

    return a


BASE_URL = (
    "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/JRC-IDEES/JRC-IDEES-2015_v1/"
)

#: List of geographical areas for which data are provided. These are ISO 3166-1 alpha-2
#: codes, except for "EU28".
GEO = [
    "AT",
    "BE",
    "BG",
    "CY",
    "CZ",
    "DE",
    "DK",
    "EE",
    "EL",
    "ES",
    "EU28",
    "FI",
    "FR",
    "HR",
    "HU",
    "IE",
    "IT",
    "LT",
    "LU",
    "LV",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SE",
    "SI",
    "SK",
    "UK",
]

# Fragments for file names in each archive
MEMBERS = [
    "EmissionBalance",
    "EnergyBalance",
    "Industry",
    "Macro",
    "MBunkers",
    "PowerGen",
    "Residential",
    "Tertiary",
    "Transport",
]


def expand(fname: str) -> str:
    return f"JRC-IDEES-2015_All_xlsx_{fname}.zip"


POOCH = Pooch(
    module=__name__,
    base_url=BASE_URL,
    # TODO add copyright.txt, readme.txt, and "…Methodological Note.pdf"
    registry={expand(geo): None for geo in GEO},
    expand=expand,
    processor="unzip",
)


def fetch(*geo, dry_run: bool = False):
    if dry_run:
        for g in geo:
            print(f"Valid url for GEO={g}: {POOCH.is_available(g)}")
        return

    return list(chain(*[POOCH.fetch(g) for g in geo]))


def path_for(geo=None, member=None):
    """Return a filename and local cache path for the data file for `geo`."""
    if member:
        assert member in MEMBERS
        return POOCH.path.joinpath(f"JRC-IDEES-2015_{member}_{geo}.xlsx")
    else:
        return POOCH.path.joinpath(expand(geo))


def iter_blocks(path: Path, geo: str):
    ef = pd.ExcelFile(path)

    skip_sheets = ["cover", "index"]
    parse_args: Dict[Any, Any] = dict(usecols="A:Q", header=None)
    columns = pd.Index([])
    for sheet_name in map(str, filter(lambda n: n not in skip_sheets, ef.sheet_names)):
        common = dict(GEO=geo)

        # Extract a hint for MODE from the sheet name
        if match := re.match("Tr(Avia|Navi|Rail|Road)_...", sheet_name):
            assert match
            value = match.group(1).upper()
            common.update(MODE={"AVIA": "AIR", "NAVI": "WATER"}.get(value, value))

        df = ef.parse(sheet_name, **parse_args)

        # Identify blank rows that separate blocks of data
        breaks = df.index[df.isna().all(axis=1)].to_list()

        # Iterate over blocks
        for start, end in zip(map(partial(add, 1), [-1] + breaks), breaks):
            data = df.loc[start : end - 1, :]
            if start == 0:
                assert 1 == data.shape[0]
                columns = pd.Index(["INFO"] + data.iloc[0, 1:].astype(int).to_list())
                continue
            elif data.iloc[0, 0] == "Indicators":
                assert 1 == data.shape[0] and data.iloc[0, 1:].isna().all()
                continue

            yield data.pipe(_set_axis, columns).assign(**common).reset_index(drop=True)


def _set_axis(df: pd.DataFrame, columns: pd.Index) -> pd.DataFrame:
    melt = partial(pd.DataFrame.melt, id_vars="INFO", value_name="OBS_VALUE")

    if df.iloc[0, 0] is np.nan:
        # Handle a different structure used in TrRoad_tech
        # First row contains the single TIME_PERIOD label applying to all data
        tp = df.iloc[0, :].dropna().item()
        # Construct a different set of columns from the *second* row of `df`, and only
        # carry through the third row et seq. that contain actual data
        return (
            df.iloc[2:, :]
            .set_axis(pd.Index(["INFO"] + df.iloc[1, 1:].to_list()), axis=1)
            .pipe(melt, var_name="YEAR_REG")
            .assign(TIME_PERIOD=tp)
        )
    else:
        return df.set_axis(columns, axis=1).pipe(melt, var_name="TIME_PERIOD")


def _match_extract(df: pd.DataFrame, expr) -> pd.DataFrame:
    cols = list(re.compile(expr).groupindex.keys())

    matches = df["INFO"].str.fullmatch(expr)
    result = pd.concat([df, df["INFO"].str.extract(expr)[cols].ffill()], axis=1)
    result.loc[matches, "INFO"] = "ALL"
    return result


def _fill_unit_measure(df: pd.DataFrame, measure: str) -> pd.DataFrame:
    """Fill in the UNIT_MEASURE column of `df`."""
    # Identify the MODE, if any
    mode = df.get("MODE", default=pd.Series([None])).unique().item()  # type: ignore
    return df.assign(
        UNIT_MEASURE=lambda df: df[["U0", "U1"]]
        .fillna(UNIT_MEASURE.get((mode, measure), ""))
        .bfill(axis=1)["U0"]
    ).drop(["U0", "U1"], axis=1)


#: Mapping from (MODE, MEASURE) to UNIT_MEASURE attribute value, where these are not
#: specified in the data.
UNIT_MEASURE = {
    # Both TrRoad_act and TrRoad_tech
    ("ROAD", "New vehicle-registrations"): "vehicle",
    # TrRoad_tech
    ("ROAD", "Age structure in 2015"): "vehicle",
    # TrRail_act
    ("RAIL", "Occupancy / utilisation"): "percent",
    # TrAvia_act
    ("AIR", "Number of flights"): "1",
    ("AIR", "Stock of aircrafts - total"): "vehicle",
    ("AIR", "Stock of aircrafts - in use"): "vehicle",
    ("AIR", "New aircrafts"): "vehicle",
    ("AIR", "Flights per year by airplance"): "1",
    # TrAvia_png
    ("AIR", "Number of seats available"): "1",
    ("AIR", "Seats available per flight"): "1",
}

UNPACK: Dict[str, Dict[str, str]] = {
    "ALL": dict(),
    "Road transport": dict(MODE="ROAD", VEHICLE_TYPE="_T"),
    "Powered 2-wheelers": dict(MODE="ROAD", VEHICLE_TYPE="2W"),
    "Powered 2-wheelers (Gasoline)": dict(
        MODE="ROAD", VEHICLE_TYPE="2W", FUEL="Gasoline"
    ),
    "of which biofuels": dict(FUEL="Biofuels"),
    "Passenger cars": dict(MODE="ROAD", VEHICLE_TYPE="LDV"),
    "Gasoline engine": dict(MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="GAS"),
    "Diesel oil engine": dict(MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="DIES"),
    "LPG engine": dict(MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="LPG"),
    "Natural gas engine": dict(MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="NG"),
    "of which biogas": dict(FUEL="Biogas"),
    "Plug-in hybrid electric": dict(MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="PHEV"),
    "Plug-in hybrid electric (Gasoline and electricity)": dict(
        MODE="ROAD",
        VEHICLE_TYPE="LDV",
        POWERTRAIN="PHEV",
        FUEL="ALL",
    ),
    "of which electricity": dict(FUEL="ELE"),
    "Battery electric vehicles": dict(
        MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="BEV"
    ),
    "Motor coaches, buses and trolley buses": dict(MODE="ROAD", VEHICLE_TYPE="BUS"),
    "Rail, metro and tram": dict(MODE="RAIL", VEHICLE_TYPE="ALL"),
    "Metro and tram, urban light rail": dict(MODE="RAIL", VEHICLE_TYPE="L"),
    "Conventional passenger trains": dict(MODE="RAIL", VEHICLE_TYPE="H"),
    "High speed passenger trains": dict(MODE="RAIL", VEHICLE_TYPE="HS"),
    "Aviation": dict(MODE="AIR", SEGMENT="ALL"),
    "Domestic": dict(MODE="AIR", SEGMENT="DOM"),
    "International - Intra-EU": dict(MODE="AIR", SEGMENT="IN_EU"),
    "International - Extra-EU": dict(MODE="AIR", SEGMENT="EX_EU"),
    # Freight
    "Light duty vehicles": dict(MODE="ROAD", VEHICLE_TYPE="LDV"),
    "Heavy duty vehicles": dict(MODE="ROAD", VEHICLE_TYPE="HDV"),
    "Heavy duty vehicles (Diesel oil incl. biofuels)": dict(
        MODE="ROAD",
        VEHICLE_TYPE="HDV",
        FUEL="Diesel oil incl. biofuels",
    ),
    "Rail transport": dict(MODE="RAIL", VEHICLE_TYPE="_T"),
    "Domestic and International - Intra-EU": dict(MODE="RAIL", SEGMENT="DOM_IN_EU"),
    "Coastal shipping and inland waterways": dict(MODE="WATER", SEGMENT="ALL"),
    "Domestic coastal shipping": dict(MODE="WATER", SEGMENT="DOM"),
    "Inland waterways": dict(MODE="WATER", SEGMENT="IWW"),
    # Sheet TrRoad_ene, table "Total energy consumption (ktoe)"
    # "Domestic": dict(MODE="ROAD", VEHICLE_TYPE="TRUCK", SEGMENT="DOM"),
    "International": dict(SEGMENT="INTL"),
    # Sheet TrRoad_ene
    "by fuel": dict(FUEL="ALL"),
    "by fuel (EUROSTAT DATA)": dict(FUEL="ALL"),
    "Liquids": dict(FUEL="Liquids"),
    "Liquids (Petroleum products)": dict(FUEL="Liquids (without biofuels)"),
    "Liquified petroleum gas (LPG)": dict(FUEL="LPG"),
    "LPG": dict(FUEL="LPG"),
    "Gasoline (without biofuels)": dict(FUEL="Gasoline (without biofuels)"),
    "Gasoline (incl. biofuels)": dict(FUEL="Gasoline (incl. biofuels)"),
    "Gas/Diesel oil (without biofuels)": dict(FUEL="Gas/Diesel oil (without biofuels)"),
    "Diesel": dict(FUEL="Diesel"),
    "Diesel oil": dict(FUEL="Diesel"),
    "Diesel oil (incl. biofuels)": dict(FUEL="Diesel oil (incl. biofuels)"),
    "Kerosene": dict(FUEL="Kerosene"),
    "Residual fuel oil": dict(FUEL="Residual fuel oil"),
    "Other petroleum products": dict(FUEL="Other petroleum products"),
    "Natural gas": dict(FUEL="NG"),
    "Natural gas (incl. biogas)": dict(FUEL="Natural gas (incl. biogas)"),
    "Renewable energies and wastes": dict(FUEL="Renewable energies and wastes"),
    "Biogas": dict(FUEL="Biogas"),
    "Biogasoline": dict(FUEL="Biogasoline"),
    "Biodiesel": dict(FUEL="Biodiesel"),
    "Biomass and wastes": dict(FUEL="Biomass and wastes"),
    "Other biofuels": dict(FUEL="Other biofuels"),
    "Electricity": dict(FUEL="ELE"),
    "Electric": dict(FUEL="ELE"),
    "Solids": dict(FUEL="Solids"),
}


def _unpack_info(df: pd.DataFrame) -> pd.DataFrame:
    """Unpack values from the INFO column."""
    info = df["INFO"].drop_duplicates()
    try:
        unpacked = pd.concat([info, info.apply(lambda v: pd.Series(UNPACK[v]))], axis=1)
    except KeyError as e:
        print(f"Failed to unpack INFO for {e.args[0]!r}:")
        print(info.to_string())
        assert False

    def _merge_mode(df: pd.DataFrame) -> pd.DataFrame:
        cols = ["MODE_x", "MODE_y"]
        try:
            return df.assign(MODE=df[cols].ffill(axis=1)[cols[-1]]).drop(cols, axis=1)
        except KeyError:
            return df

    return (
        df.merge(unpacked, on="INFO")
        .drop("INFO", axis=1)
        .pipe(_merge_mode)
        .fillna("_X")
    )


def read(geo=None):
    """Read data from a single file.

    Notes on the format:

    - The hierarchy of some codes in column A is expressed by Excel formatting
      (indentation, with greater indentation indicating greater depth). This is not
      easily extracted with pandas.
    """
    path = path_for(geo, "Transport")

    # Metadata across all blocks
    CS_MEASURE = m.ConceptScheme(id="MEASURE")
    _measure_id = dict()
    # Data per measure
    data = defaultdict(list)

    print(f"Read data for {geo = }")

    # Iterate over blocks of data
    i = count(start=1)
    for block in iter_blocks(path, geo):
        # Identify the measure (INFO column on first row of the block)
        measure_unit = block.loc[0, "INFO"]

        # Unpack a string that combines MEASURE and, possibly, UNIT_MEASURE
        match = re.fullmatch(r"(?P<measure>[^\(]+) \((?P<unit>.*)\)\*?", measure_unit)
        try:
            measure, unit = match.group("measure", "unit")
        except AttributeError:
            measure, unit = measure_unit, None

        # The measure concept
        try:
            mc_id = _measure_id[measure]
        except KeyError:
            mc_id = f"{next(i):02d}"
            CS_MEASURE.append(m.Concept(id=mc_id, name=measure))
            _measure_id[measure] = mc_id

        # - Assign `unit` from above as U0, one candidate from UNIT_MEASURE.
        # - Replace the embedded measure/unit expression with "ALL transport".
        # - Unpack and fill forward SERVICE values from "Passenger transport" or
        #   "Freight transport" entries in the INFO column. Also unpack U1.
        # - Choose the right
        # - If UNIT_MEASURE is still missing, fill from explicit values above.
        # - Drop rows with missing values in "OBS_VALUE"
        block = (
            block.assign(U0=unit)
            .replace({"INFO": {measure_unit: "ALL transport"}})
            .pipe(
                _match_extract,
                r"(?P<SERVICE>ALL|Freight|Passenger) transport( +\((?P<U1>.*)\))?",
            )
            .pipe(_fill_unit_measure, measure)
            .dropna(subset="OBS_VALUE", ignore_index=True)
            .pipe(_unpack_info)
        )

        data[mc_id].append(block)

    print(f"{sum(map(len, data.values()))} data sets for {len(CS_MEASURE)} measures")

    # Join multiple data frames
    return {
        CS_MEASURE[mc_id]: pd.concat(dfs).fillna("_X") for mc_id, dfs in data.items()
    }


def convert(geo):
    data = read(geo)

    # TODO create SDMX DSD, Dataflow, and DataSets from the resulting pd.DataFrame

    # Code lists
    CL = dict()

    # Retrieve the parent concept scheme
    CS_MEASURE = list(data.keys())[0].parent

    # Iterate over measure_concepts
    for measure_concept, df in data.items():
        # Update the structure information
        for concept, values in df.items():
            if concept in ("GEO", "OBS_VALUE", "TIME_PERIOD"):
                continue

            cl = CL.setdefault(concept, m.Codelist(id=concept))

            for value in values.unique():
                try:
                    cl.append(m.Code(id=value, name=value))
                except ValueError:
                    pass  # Already exists

        # Prepare an empty data set, associated structures, and a helper function
        dims = []
        for c in df.columns:
            if c in ("OBS_VALUE",):
                continue
            dims.append(c)
        ds, _make_obs = prepare(measure_concept, dims)

        # Convert rows of `data` into SDMX Observation objects
        ds.obs.extend(_make_obs(row) for _, row in df.iterrows())
        assert len(ds) == len(df)

        # Write the data set, DSD, and DFD to file
        for obj in (ds, ds.described_by, ds.structured_by):
            obj.annotations.append(
                m.Annotation(
                    id="tdc-comment", text=f"Primary measure is {measure_concept!r}"
                )
            )
            registry.write(obj, force=True, _show_status=False)

    # Write code lists, measure concept scheme to file
    a = get_agency()
    for obj in chain(CL.values(), [CS_MEASURE]):
        obj.maintainer = a
        obj.version = "0.1.0"
        registry.write(obj, force=True, _show_status=False)

    raise NotImplementedError("Merging data for multiple GEO")


def prepare(measure_concept, dims):
    # TODO merge with the similar function in .adb.__init__

    measure_id = measure_concept.id
    c = measure_concept
    aa = measure_concept

    # Data structure definition with an ID matching the measure
    # NB here we set ADB as the maintainer. Precisely, ADB establishes the data
    #    structure, but TDCI is maintaining the SDMX representation of it.
    dsd = m.DataStructureDefinition(
        id=measure_id, maintainer=get_agency(), version="0.0.0"
    )
    anno_generated(dsd)

    dfd = m.DataflowDefinition(
        id=measure_id, maintainer=get_agency(), version="0.0.0", structure=dsd
    )

    pm = m.PrimaryMeasure(id="OBS_VALUE", concept_identity=c)
    dsd.measures.append(pm)

    # Dimensions
    dsd.dimensions.extend(m.Dimension(id=d) for d in dims)

    # Convert annotations to DataAttributes. "NoSpecifiedRelationship" means that the
    # attribute is attached to an entire data set (not a series, individual obs, etc.).
    da = {}  # Store references for use below
    for a in filter(lambda a: a.id != "remark-cols", aa.annotations):
        da[a.id] = m.DataAttribute(id=a.id, related_to=m.NoSpecifiedRelationship())
        dsd.attributes.append(da[a.id])

    _PMR = m.PrimaryMeasureRelationship  # Shorthand

    # Convert remark column labels to DataAttributes. "PrimaryMeasureRelationship" means
    # that the attribute is attached to individual observations.
    for name in aa.eval_annotation("remark-cols") or []:
        dsd.attributes.append(m.DataAttribute(id=name, related_to=_PMR()))

    # Empty data set structured by this DSD

    ds = m.StructureSpecificDataSet(described_by=dfd, structured_by=dsd)
    try:
        ds.annotations.append(aa.get_annotation(id="remark-cols"))
    except KeyError:
        pass
    anno_generated(ds)

    # Convert temporary annotation values to attributes attached to the data set
    for a in filter(lambda a: a.id != "remark-cols", aa.annotations):
        ds.attrib[a.id] = m.AttributeValue(value=str(a.text), value_for=da[a.id])

    def _make_obs(row):
        """Helper function for making :class:`sdmx.model.Observation` objects."""
        key = dsd.make_key(m.Key, row[[d.id for d in dsd.dimensions]])

        # Attributes
        attrs = {}
        for a in filter(lambda a: a.related_to is _PMR, dsd.attributes):
            # Only store an AttributeValue if there is some text
            value = row[a.id]
            if not pd.isna(value):
                attrs[a.id] = m.AttributeValue(value_for=a, value=value)

        return m.Observation(
            dimension=key, attached_attribute=attrs, value_for=pm, value=row[pm.id]
        )

    return ds, _make_obs
