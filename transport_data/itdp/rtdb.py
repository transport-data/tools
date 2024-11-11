import logging
from functools import partial
from pathlib import Path

import pandas as pd
from sdmx.model import common, v21

from transport_data.util.google import get_service

log = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    # "https://www.googleapis.com/auth/spreadsheets.readonly",
]

# The file ID of the Google Drive file.
FILE_ID = "1uMuNG9rTGO52Vuuq6skyqmkH9U5yv1iSJDJYjH64MJM"


def convert(path: Path) -> "v21.DataSet":
    return read_workbook(path)


def read_workbook(path: Path) -> "v21.DataSet":
    """Read a metadata set from the workbook at `path`."""
    ef = pd.ExcelFile(path)

    return read_worksheet_rtr(ef)


def get_dsd_rtr() -> "v21.DataStructureDefinition":
    cs_measure = common.ConceptScheme(id="MEASURE")
    cs_measure.setdefault(
        id="RTR",
        name="Rapid Transit to Resident Ratio (RTR)",
        description="km of Rapid Transit / Million Urban Residents (in cities with populations above 500,000)",
    )

    result = v21.DataStructureDefinition(id="RTR")

    result.dimensions.getdefault(id="GEO")
    result.dimensions.getdefault(id="TYPE")
    result.dimensions.getdefault(id="TIME_PERIOD")

    result.measures.getdefault(id="OBS_VALUE", concept_identity=cs_measure["RTR"])

    return result


def read_worksheet_rtr(ef: "pd.ExcelFile", sheet_name="Country RTR") -> "v21.DataSets":
    """Read the “Country RTR” sheet of the RTDB."""
    from pycountry import countries

    from transport_data.util.pycountry import NAME_MAP
    from transport_data.util.sdmx import make_obs

    def _geo_alpha_2(value: str) -> str:
        try:
            return countries.lookup(NAME_MAP.get(value.lower(), value)).alpha_2
        except LookupError:
            if value == "Grand TOTAL":
                return "_T"
            else:
                raise

    # Read and transform the worksheet
    df = (
        ef.parse(sheet_name=sheet_name)
        .rename(columns={"RTR": "GEO", "Unnamed: 2": "TYPE"})
        .drop("Region", axis=1)
        .assign(
            GEO=lambda df: df["GEO"].ffill().apply(_geo_alpha_2),
            TYPE=lambda df: df["TYPE"].str.replace("Total", "_T"),
        )
        .set_index(["GEO", "TYPE"])
        .melt(var_name="TIME_PERIOD", value_name="OBS_VALUE", ignore_index=False)
        .reset_index()
    )

    # Obtain the data structure definition
    dsd = get_dsd_rtr()

    # Convert data to SDMX
    return v21.DataSet(
        structured_by=dsd, obs=df.apply(partial(make_obs, dsd=dsd), axis=1).to_list()
    )


FETCH_MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def fetch() -> Path:
    """Fetch the RTDB file.

    This function uses the Google Drive API v3 to export the upstream database
    """
    from datetime import datetime, timezone

    from platformdirs import user_cache_path

    cache_dir = user_cache_path("transport-data").joinpath("itdp")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir.joinpath("rtdp.xlsx")

    # Local modified time
    tz = datetime.now(timezone.utc).astimezone().tzinfo
    try:
        mtime_cache = datetime.fromtimestamp(cache_path.stat().st_mtime, tz=tz)
    except FileNotFoundError:
        mtime_cache = datetime.fromtimestamp(0, tz=tz)

    # Call the Drive API
    try:
        drive = get_service("drive", "v3", scopes=SCOPES).files()
        result = drive.get(fileId=FILE_ID, fields="modifiedTime").execute()

        # Last modified time of the remote file
        mtime_remote = datetime.fromisoformat(result["modifiedTime"])
    except RuntimeError as e:
        if cache_path.exists():
            # Continue with returning cache_path, even though it may be stale
            log.warning(
                f"Could not check remote file modification time; {cache_path} may be "
                "stale"
            )
            log.debug(e)
        else:
            raise RuntimeError("Could not fetch remote file") from e
    else:
        if not cache_path.exists() or mtime_cache < mtime_remote:
            # Export the file to .xlsx
            request = drive.export(fileId=FILE_ID, mimeType=FETCH_MIME_TYPE)

            # Write to the cache path
            with open(cache_path, "wb") as f:
                f.write(request.execute())

    return cache_path
