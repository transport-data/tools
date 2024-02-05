"""International Organization of Motor Vehicle Manufacturers (OICA) provider.

This module handles data from the OICA website.

"Handle" includes:

- Fetch
- Extract
- Parse the native spreadsheet layout.
- Convert to SDMX.

"""
import json
import logging
from functools import partial
from itertools import count, product
from operator import itemgetter
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Tuple

import pandas as pd

from transport_data.util.pooch import Pooch

if TYPE_CHECKING:
    import sdmx.model.common

log = logging.getLogger(__name__)

BASE_URL = "https://www.oica.net/wp-content/uploads/"

REGISTRY_FILE = Path(__file__).parent.joinpath("registry.json")

with open(REGISTRY_FILE) as f:
    POOCH = Pooch(module=__name__, base_url=BASE_URL, registry=json.load(f))


def get_agency() -> "sdmx.model.common.Agency":
    from sdmx.model import v21

    return v21.Agency(
        id="OICA",
        name="International Organization of Motor Vehicle Manufacturers",
        description="""https://www.oica.net""",
    )


def _geo_codelist(values: pd.Series) -> Tuple["sdmx.model.common.Codelist", Dict]:
    from pycountry import countries
    from sdmx.model import v21

    from transport_data.util.pycountry import NAME_MAP

    cl = v21.Codelist(id="GEO")
    counter = count()
    id_for_name: Dict[str, str] = {}

    def _make_code(value: str):
        name = value.strip()
        try:
            match = countries.lookup(NAME_MAP.get(name.lower(), name))
        except LookupError:
            try:
                # Look up an existing generated code that matches this `value`
                code = cl[id_for_name[value]]
            except KeyError:
                # Generate a new code with a serial ID
                code = v21.Code(id=str(next(counter)), name=name)
        else:
            # Found an entry in the ISO 3166-1 database; duplicate it into the codelist
            code = v21.Code(
                id=match.alpha_2,
                name=match.name,
                description="Identical to the ISO 3166-1 entry",
            )
        try:
            cl.append(code)
            id_for_name.setdefault(value, code.id)
        except ValueError:
            pass

    values.apply(_make_code)

    return cl, id_for_name


def make_structures(
    measure: str,
) -> Tuple[
    "sdmx.model.v21.DataflowDefinition", "sdmx.model.v21.DataStructureDefinition"
]:
    from sdmx.model import v21

    from transport_data import org

    ma_args = dict(
        id=f"{get_agency().id}_{measure}", maintainer=org.get_agency()[0], version="0.1"
    )
    dsd = v21.DataStructureDefinition(**ma_args)

    for d in "GEO", "VEHICLE_TYPE", "TIME_PERIOD":
        dsd.dimensions.getdefault(id=d)

    for a in ("UNIT_MEASURE",):
        dsd.attributes.getdefault(id=a)

    for m in ("OBS_VALUE",):
        dsd.measures.getdefault(id=m)

    dfd = v21.DataflowDefinition(**ma_args, structure=dsd)

    return dfd, dsd


def convert():
    """Convert OICA spreadsheets to SDMX."""
    from sdmx.model.v21 import DataSet

    from transport_data import STORE as registry
    from transport_data.util.sdmx import make_obs

    paths = fetch()
    for p in paths:
        if "PC-World" in p:
            path = Path(p)
            break

    df = (
        pd.read_excel(path)
        .dropna(how="all", axis=0, ignore_index=True)
        .dropna(how="all", axis=1)
    )

    assert "PC WORLD VEHICLES IN USE  (in thousand units)" == df.iloc[0, 0]
    units = "kvehicle"
    vehicle_type = "PC"

    def _convert_tp(time_period):
        if time_period in ("2015", "2020"):
            return pd.Series(
                dict(
                    MEASURE="STOCK",
                    UNIT_MEASURE=units,
                    VEHICLE_TYPE=vehicle_type,
                    TIME_PERIOD=time_period,
                )
            )
        elif time_period == "Average Annual Growth Rate\n 2015-2020":
            return pd.Series(
                dict(
                    MEASURE="AAGR_STOCK",
                    UNIT_MEASURE="1",
                    VEHICLE_TYPE=vehicle_type,
                    TIME_PERIOD="2015–2020",
                )
            )
        else:
            raise ValueError(time_period)

    df = (
        df.iloc[2:, :]
        .set_axis(df.iloc[1, :], axis=1)
        .rename(columns={"REGIONS/COUNTRIES": "GEO"})
        .melt(id_vars="GEO", var_name="TIME_PERIOD", value_name="OBS_VALUE")
        .replace({"TIME_PERIOD": {2015.0: "2015", 2020.0: "2020"}})
    )

    cl_geo, geo_map = _geo_codelist(df["GEO"])

    df = pd.concat(
        [
            df["GEO"].replace(geo_map),
            df["TIME_PERIOD"].apply(_convert_tp),
            df["OBS_VALUE"],
        ],
        axis=1,
    )

    for m, group_df in df.groupby("MEASURE"):
        dfd, dsd = make_structures(m)

        ds = DataSet(described_by=dsd)
        ds.add_obs(
            map(partial(make_obs, dsd=dsd), map(itemgetter(1), group_df.iterrows()))
        )

        registry.write(ds)

    cl_geo.maintainer = get_agency()
    cl_geo.version = "0.1"
    registry.write(cl_geo)


def fetch(dry_run: bool = False):
    """Fetch data files."""
    if dry_run:
        for f in POOCH.registry:
            print(f"Valid url for GEO={f}: {POOCH.is_available(f)}")
        return

    return [POOCH.fetch(f) for f in POOCH.registry]


def update_registry():
    """Update the registry.

    This function crawls :data:`.BASE_URL` for file names matching certain patterns.
    Files that exist are downloaded, hashed, and added to :file:`registry.json`.
    """
    from pooch import file_hash

    for pattern, values in (
        # Sales statistics
        ("{}_sales_{}.xlsx", ({"cv", "pc", "total"}, range(2017, 2024))),
        # Vehicles in use
        (
            "{}-World-vehicles-in-use-{}.xlsx",
            ({"CV", "PC", "Total"}, range(2017, 2024)),
        ),
        # Production data
        (
            "{}-{}.xlsx",
            (
                {
                    "By-country-region",
                    "Passenger-Cars",
                    "Light-Commercial-Vehicles",
                    "Heavy-Trucks",
                    "Buses-and-Coaches",
                },
                range(2017, 2024),
            ),
        ),
    ):
        for sub in product(*values):
            url_part = pattern.format(*sub)
            existing_hash = POOCH.registry.setdefault(url_part, None)

            if not POOCH.is_available(url_part):
                # File doesn't exist on the remote
                POOCH.registry.pop(url_part)
                continue

            if existing_hash is None:
                # Download the file to add its hash
                path = POOCH.fetch(url_part)
                POOCH.registry[url_part] = file_hash(path)

    with open(REGISTRY_FILE, "w") as f:
        json.dump(POOCH.registry, f)
