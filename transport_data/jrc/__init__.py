"""Handle data from the JRC IDEES 2015 source.

"Handle" includes:

- Fetch
- Extract
- Parse the native spreadsheet layout.
- Convert to SDMX.

"""
import re
from functools import partial
from operator import add
from pathlib import Path

import numpy as np
import pandas as pd
import sdmx.model.v21 as m

from transport_data.util.pooch import Pooch


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
    parse_args = dict(usecols="A:Q", header=None)
    columns = pd.Index([])
    for sheet_name in filter(lambda n: n not in skip_sheets, ef.sheet_names):
        common = dict(GEO=geo)

        # Extract a hint for MODE from the sheet name
        if match := re.match("Tr(Avia|Navi|Rail|Road)_...", sheet_name):
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
    melt_kw = dict(id_vars="INFO", value_name="OBS_VALUE")
    if df.iloc[0, 0] is np.nan:
        # Handle a different structure used in TrRoad_tech
        # First row contains the single TIME_PERIOD label applying to all data
        tp = df.iloc[0, :].dropna().item()
        # Construct a different set of columns from the *second* row of `df`, and only
        # carry through the third row et seq. that contain actual data
        return (
            df.iloc[2:, :]
            .set_axis(pd.Index(["INFO"] + df.iloc[1, 1:].to_list()), axis=1)
            .melt(**melt_kw, var_name="YEAR_REG")
            .assign(TIME_PERIOD=tp)
        )
    else:
        return df.set_axis(columns, axis=1).melt(**melt_kw, var_name="TIME_PERIOD")


def _match_extract(df: pd.DataFrame, expr) -> pd.DataFrame:
    expr_ = re.compile(expr)
    cols = list(expr_.groupindex.keys())

    matches = df["INFO"].str.fullmatch(expr_)
    result = pd.concat([df, df["INFO"].str.extract(expr_)[cols].ffill()], axis=1)
    result.loc[matches, "INFO"] = "ALL"
    return result


def _fill_unit_measure(df: pd.DataFrame, measure: str) -> pd.DataFrame:
    """Fill in the UNIT_MEASURE column of `df`."""
    # Identify the MODE, if any
    mode = df.get("MODE", pd.Series([None])).unique().item()
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

UNPACK = {
    "ALL": dict(MODE="ALL"),
    "Road transport": dict(MODE="ROAD", VEHICLE_TYPE="ALL"),
    "Powered 2-wheelers": dict(MODE="ROAD", VEHICLE_TYPE="2W"),
    "Passenger cars": dict(MODE="ROAD", VEHICLE_TYPE="LDV"),
    "Gasoline engine": dict(MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="GAS"),
    "Diesel oil engine": dict(MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="DIES"),
    "LPG engine": dict(MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="LPG"),
    "Natural gas engine": dict(MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="NG"),
    "Plug-in hybrid electric": dict(MODE="ROAD", VEHICLE_TYPE="LDV", POWERTRAIN="PHEV"),
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
    "Rail transport": dict(MODE="RAIL", VEHICLE_TYPE="ALL"),
    "Domestic and International - Intra-EU": dict(MODE="RAIL", SEGMENT="DOM_IN_EU"),
    "Coastal shipping and inland waterways": dict(MODE="WATER", SEGMENT="ALL"),
    "Domestic coastal shipping": dict(MODE="WATER", SEGMENT="DOM"),
    "Inland waterways": dict(MODE="WATER", SEGMENT="IWW"),
}


def _unpack_info(df: pd.DataFrame) -> pd.DataFrame:
    print(
        df["INFO"]
        .drop_duplicates()
        .apply(lambda v: pd.Series(UNPACK[v]))
        .fillna("_Z")
        .to_string()
    )

    raise NotImplementedError


def read(geo=None):
    """Read data from a single file.

    Notes on the format:

    - The hierarchy of some codes in column A is expressed by Excel formatting
      (indentation, with greater indentation indicating greater depth). This is not
      easily extracted with pandas.
    """
    path = path_for(geo, "Transport")

    # Metadata across all blocks
    ALL_INFO = set()
    CS_MEASURE = m.ConceptScheme(id="MEASURE")
    CL_UNIT_MEASURE = m.Codelist(id="UNIT_MEASURE")

    # Iterate over blocks of data
    for i, block in enumerate(iter_blocks(path, geo)):
        # Identify the measure (INFO column on first row of the block)
        measure_unit = block.loc[0, "INFO"]

        # Unpack a string that combines MEASURE and UNIT_MEASURE
        match = re.fullmatch(r"(?P<measure>[^\(]+) \((?P<unit>.*)\)\*?", measure_unit)
        try:
            measure, unit = match.group("measure", "unit")
        except AttributeError:
            measure, unit = measure_unit, None

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

        # Update the structure information

        # Units of measure
        for unit in block["UNIT_MEASURE"].unique():
            try:
                CL_UNIT_MEASURE.append(m.Code(id=unit, name=unit))
            except ValueError:
                pass  # Already exists

        # The measure concept
        measure_concept = m.Concept(id=str(i), name=measure)
        CS_MEASURE.append(measure_concept)

        # Remaining labels appearing in the "INFO" dimension
        ALL_INFO.update(block["INFO"].unique())

        # First two rows, transposed
        print("\n", repr(measure_concept))
        print(block.head(2).transpose().to_string())

        # print("\n", repr(measure_concept))
        # print(block.to_string())

    print(
        "---",
        f"{len(ALL_INFO)} distinct INFO labels",
        "\n".join(sorted(ALL_INFO)),
        "---",
        sep="\n",
    )
    print("---", repr(CL_UNIT_MEASURE), CL_UNIT_MEASURE.items, sep="\n")

    # TODO extract MODE and VEHICLE from INFO
    # TODO create SDMX DSD, Dataflow, and DataSets from the resulting pd.DataFrame

    # raise NotImplementedError


def convert(geo):
    read(geo)
    raise NotImplementedError
