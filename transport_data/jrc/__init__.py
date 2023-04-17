"""Handle data from the JRC IDEES 2015 source.

"Handle" includes:

- Fetch
- Extract
- Parse the native spreadsheet layout.
- Convert to SDMX.

"""
import re
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import requests
import sdmx.model.v21 as m
from xdg_base_dirs import xdg_cache_home


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

    a.contact.append(m.Contact(name="Jacopo Tattini", email=["name@example.com"]))

    return a


BASE_URL = "http://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/JRC-IDEES/JRC-IDEES-2015_v1"

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


def path_for(geo=None):
    """Return a filename and local cache path for the data file for `geo`."""
    name = f"JRC-IDEES-2015_All_xlsx_{geo}.zip"
    return xdg_cache_home().joinpath("transport-data", "jrc", name)


def get(geo=None):
    """Retrieve the JRC-IDREES 2015 file for a single geography, `geo`."""
    # TODO also get copyright.txt, readme.txt, and "…Methodological Note.pdf"

    path = path_for(geo)

    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Create directory {path.parent}")

    response = requests.get(url=f"{BASE_URL}/{path.name}", stream=True)
    path.write_bytes(response.content)
    print(f"Retrieved {path}")

    return path


def extract(path: Path):
    """Extract the ZIP file at `path`."""
    with ZipFile(path) as zf:
        zf.extractall(path=path.parent)


def extract_all():
    """Retrieve and extract all files."""
    for geo in GEO:
        p = get(geo)
        extract(p)


def read(geo=None):
    """Read data from a single file.

    Notes on the format:

    - The hierarchy of some codes in column A is expressed by Excel formatting
      (indentation, with greater indentation indicating greater depth). This is not
      easily extracted with pandas.
    """
    path = path_for(geo).with_name(f"JRC-IDEES-2015_Transport_{geo}.xlsx")

    ef = pd.ExcelFile(path)

    for sheet_name, usecols in (("Transport", "A:Q"),):
        df = ef.parse(sheet_name, usecols=usecols)

        # TODO move the following in to convert()

        # - Rename the label column
        # - Melt into long format
        # - Assign GEO and empty MEASURE column
        idx = ["INFO"] + df.columns.tolist()[1:]
        df = (
            df.set_axis(idx, axis=1)
            .melt(id_vars="INFO", var_name="TIME_PERIOD", value_name="OBS_VALUE")
            .assign(GEO=geo, MEASURE="", UNIT_MEASURE="", SERVICE="")
        )

        # Identify breaks between blocks of data for the same measure
        breaks = df.isna().query("INFO and OBS_VALUE").index.to_list()
        # Iterate over paired indices for the start and end of each block
        for start, end in zip(map(lambda n: n + 1, breaks), breaks[1:] + [len(df) + 1]):
            # Identify the measure (INFO column on first row of the block)
            measure = df.loc[start, "INFO"]

            # Handle a string that combines MEASURE and UNIT_MEASURE
            if match := re.fullmatch(r"(?P<measure>[^\(]+) \((?P<unit>.*)\)", measure):
                measure = match.group("measure")
                unit = match.group("unit")
            else:
                unit = ""

            # Assign values within this block
            df.loc[start:end, "MEASURE"] = measure
            df.loc[start:end, "UNIT_MEASURE"] = unit

            # Replace the embedded value in the INFO column with "ALL"
            df.loc[start, ["INFO", "SERVICE"]] = "ALL"

        # Drop null values
        df = df.dropna(subset=["INFO", "OBS_VALUE"]).reset_index(drop=True)

        # Similar process between passenger and freight
        expr = r"(ALL|(?P<service>Freight|Passenger) transport( \((?P<unit>.*)\))?)"
        breaks = df[df["INFO"].str.fullmatch(expr)].index.to_list()
        for start, end in zip(breaks, map(lambda n: n - 1, breaks[1:] + [len(df) + 1])):
            # Identify the service (INFO column on first row of the block)
            service = df.loc[start, "INFO"]
            if service == "ALL":
                continue

            existing = list(df.loc[start:end, "UNIT_MEASURE"].unique())

            # Handle a string that combines SERVICE and UNIT_MEASURE
            if match := re.fullmatch(expr, service):
                service = match.group("service")
                unit = match.group("unit") or existing[0]
            else:
                unit = ""

            # Check for any conflict
            if unit:
                assert set(existing) < {"", unit}, f"{existing = } vs. {unit = }"

            # Assign values within this block
            df.loc[start:end, "SERVICE"] = service
            df.loc[start:end, "UNIT_MEASURE"] = unit

            # Replace the embedded value in the INFO column with "ALL"
            df.loc[start, "INFO"] = "ALL"

        # TODO extract MODE and VEHICLE from INFO
        # TODO create SDMX DSD, Dataflow, and DataSets from the resulting pd.DataFrame

        return df


def convert():
    raise NotImplementedError
