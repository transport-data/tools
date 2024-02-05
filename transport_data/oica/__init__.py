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
from functools import lru_cache, partial
from itertools import count, product
from operator import itemgetter
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Tuple

import pandas as pd

from transport_data.util.pooch import Pooch

if TYPE_CHECKING:
    import sdmx.model.common

log = logging.getLogger(__name__)

#: Base URL for data files.
BASE_URL = "https://www.oica.net/wp-content/uploads/"

#: Package data file containing :mod:`.pooch` registry information (file names and
#: hashes).
REGISTRY_FILE = Path(__file__).parent.joinpath("registry.json")

# Read the registry file
with open(REGISTRY_FILE) as f:
    POOCH = Pooch(module=__name__, base_url=BASE_URL, registry=json.load(f))


@lru_cache
def get_agency() -> "sdmx.model.common.Agency":
    """Return the OICA Agency."""
    from sdmx.model import v21

    return v21.Agency(
        id="OICA",
        name="International Organization of Motor Vehicle Manufacturers",
        description="https://www.oica.net",
    )


def _geo_codelist(
    values: pd.Series, **kwargs
) -> Tuple["sdmx.model.common.Codelist", Dict]:
    """Create a codelist for the ``GEO`` concept, given certain `values`.

    For each unique value in `values`:

    1. Strip leading and trailing whitespace.
    2. Pass the data through :data`.transport_data.util.pycountry.NAME_MAP` for commonly
       used non-ISO values.
    3. Look up the value in ISO 3166-1 via :any:`pycountry.countries`.
    4. Add a code to the returned code list. If the lookup in (3) succeeds, the code ID
       is the alpha-2 code, and the name and description are populated from the
       database. If the lookup in (3) fails, the code ID is a unique integer.

    Returns
    -------
    .Codelist
        One entry for each unique value in `values`.
    dict
        Mapping from `values` to codes in the code list. Passing this to
        :meth:`pandas.Series.replace` should convert the `values` to the corresponding
        codes.
    """
    from pycountry import countries
    from sdmx.model import v21

    from transport_data.util.pycountry import NAME_MAP

    cl = v21.Codelist(id="GEO", **kwargs)
    counter = count()
    id_for_name: Dict[str, str] = {}

    @lru_cache
    def _make_code(value: str):
        name = value.strip()
        try:
            # - Apply replacements from NAME_MAP.
            # - Lookup in ISO 3166-1.
            match = countries.lookup(NAME_MAP.get(name.lower(), name))
        except LookupError:
            try:
                # Look up an already-generated code that matches this `value`
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
            cl.append(code)  # Add to the code list
        except ValueError:
            pass  # Already exists
        else:
            id_for_name.setdefault(value, code.id)  # Update the map

    values.sort_values().drop_duplicates().apply(_make_code)

    return cl, id_for_name


def get_structures(
    measure: str,
) -> Tuple[
    "sdmx.model.v21.DataflowDefinition", "sdmx.model.v21.DataStructureDefinition"
]:
    """Create a data flow and data structure definitions for a given OICA `measure`.

    The DFD and DSD have URNs like ``TDCI:OICA_{MEASURE}(0.1)``. The DSD has:

    - dimensions ``GEO``, ``VEHICLE_TYPE``, ``TIME_PERIOD``,
    - attributes ``UNIT_MEASURE``, and
    - primary measure with ID ``OBS_VALUE``.
    """
    from sdmx.model import v21

    from transport_data import STORE, org

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

    STORE.write(dfd)
    STORE.write(dsd)

    return dfd, dsd


def convert():
    """Convert OICA stock (vehicle in use) spreadsheets to SDMX."""
    from sdmx.model.v21 import DataSet

    from transport_data import STORE
    from transport_data.util.sdmx import make_obs

    # Select just one spreadsheet
    paths = fetch()
    for p in paths:
        if "PC-World" in p:
            path = Path(p)
            break

    # - Read data
    # - Drop entirely empty rows.
    # - Drop entirely empty columns.
    df = (
        pd.read_excel(path)
        .dropna(how="all", axis=0, ignore_index=True)
        .dropna(how="all", axis=1)
    )

    # Confirm vehicle type and measure vs. contents of the title cell
    assert "PC WORLD VEHICLES IN USE  (in thousand units)" == df.iloc[0, 0]
    units = "kvehicle"
    vehicle_type = "PC"

    # - Drop title cell.
    # - Set index.
    # - Rename REGIONS/COUNTRIES to GEO.
    # - Melt to long format.
    # - Replace float with string year values.
    df = (
        df.iloc[2:, :]
        .set_axis(df.iloc[1, :], axis=1)
        .rename(columns={"REGIONS/COUNTRIES": "GEO"})
        .melt(id_vars="GEO", var_name="TIME_PERIOD", value_name="OBS_VALUE")
    )

    def _convert_tp(time_period):
        """Identify values for 4 concepts using the TIME_PERIOD."""
        if time_period in (2015.0, 2020.0):
            return pd.Series(
                dict(
                    MEASURE="STOCK",
                    UNIT_MEASURE=units,
                    VEHICLE_TYPE=vehicle_type,
                    TIME_PERIOD=str(int(time_period)),
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

    # Prepare a GEO codelist and map using the "GEO" column
    cl_geo, geo_map = _geo_codelist(df["GEO"], maintainer=get_agency(), version="0.1")
    # Store `cl_geo`
    STORE.write(cl_geo)

    # Transform data
    # - Replace GEO values with codes from `cl_geo`.
    # - Replace TIME_PERIOD values with new TIME_PERIOD, MEASURE, UNIT_MEASURE,
    #   VEHICLE_TYPE.
    # - Preserve OBS_VALUE.
    df = pd.concat(
        [
            df["GEO"].replace(geo_map),
            df["TIME_PERIOD"].apply(_convert_tp),
            df["OBS_VALUE"],
        ],
        axis=1,
    )

    # Group data by MEASURE ~ dataflow
    for m, group_df in df.groupby("MEASURE"):
        # Create structures for this measure
        # TODO Retrieve possibly-cached or -stored structures
        dfd, dsd = get_structures(m)

        # Create a data set
        ds = DataSet(described_by=dsd)

        # Convert rows of `group_df` to observations
        ds.add_obs(
            map(partial(make_obs, dsd=dsd), map(itemgetter(1), group_df.iterrows()))
        )

        # Write the data set to file
        # TODO Merge with with other data for the same flow
        STORE.write(ds)


def fetch(dry_run: bool = False):
    """Fetch all known OICA data files."""
    if dry_run:
        for f in POOCH.registry:
            print(f"Valid url for GEO={f}: {POOCH.is_available(f)}")
        return

    return [POOCH.fetch(f) for f in POOCH.registry]


def update_registry():
    """Update the registry.

    This function crawls :data:`.BASE_URL` for file names matching certain patterns.
    Files that exist are downloaded, hashed, and added to the :data:`.REGISTRY_FILE`.
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
