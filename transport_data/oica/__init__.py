"""International Organization of Motor Vehicle Manufacturers (OICA) provider.

This module handles data from the `OICA website <https://www.oica.net>`__. "Handle"
includes:

- Fetch data files.
- Parse the native spreadsheet layout. This layout differs across data flows and years;
  currently only the most recent formats are supported.
- Convert to SDMX following TDCI conventions.
"""

import json
import logging
import re
from functools import lru_cache, partial
from itertools import count, product
from operator import itemgetter
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Iterator, List, Tuple

import pandas as pd

from transport_data.util.pluggy import hookimpl
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


def convert(
    measure: str,
) -> Dict[str, "sdmx.model.v21.DataSet"]:
    """Convert OICA spreadsheets to SDMX.

    This method handles OICA's particular arrangement of data from a single data flow
    across multiple Microsoft Excel files, each with a single sheet. The individual
    files/sheets are processed by :func:`.convert_single_file`.

    The OICA files each mix data for multiple data flows or measures: for instance, each
    of the "Vehicles in use" files contains data for up to 3 different measures:

    - ``STOCK``: Number of vehicles in use.
    - ``STOCK_AAGR``: Average annual growth rate across a specified ``TIME_PERIOD``.
    - (in some cases) ``STOCK_CAP``: Number of vehicles in use per 1000 capita
      population.

    This function returns a dictionary in which data flow IDs for each measure are keys,
    and values are SDMX data sets, each for a single measure.
    """
    # Retrieve the DFD
    dfd, dsd = get_structures(measure)

    if "PROD" in dfd.id:
        raise NotImplementedError(f"Convert OICA data files for {dfd}")

    # Convert all fetchable/fetched files related to the DFD
    results = [convert_single_file(path, dfd) for path in filenames_for_dfd(dfd)]

    # Merge observations from multiple files into a single data set per data flow
    result: Dict[str, "sdmx.model.v21.DataSet"] = {}
    for r in results:
        for dfd_id, datasets in r.items():
            if dfd_id not in result:
                result[dfd_id] = datasets[0]
                [result[dfd_id].add_obs(ds.obs) for ds in datasets[1:]]
            else:
                [result[dfd_id].add_obs(ds.obs) for ds in datasets]

    return result


def convert_tp(time_period: str, units: str, vehicle_type: str):
    """Identify values for 4 concepts using column labels melted into TIME_PERIOD."""
    concepts = ["MEASURE", "UNIT_MEASURE", "VEHICLE_TYPE", "TIME_PERIOD"]

    def _(*values):
        return pd.Series(dict(zip(concepts, values)))

    if time_period in (2015.0, 2020.0):
        return _("STOCK", units, vehicle_type, str(int(time_period)))
    elif time_period == "Average Annual Growth Rate\n 2015-2020":
        return _("STOCK_AAGR", "1", vehicle_type, "2015–2020")
    elif time_period == "Number of vehicles per 1000 inhabitants":
        return _("STOCK_CAP", "0.001", vehicle_type, "_X")
    elif match := re.fullmatch(r"Q1-Q4 (\d{4})", time_period):
        return _("SALES", units, vehicle_type, match.group(1))
    elif match := re.fullmatch(r"(2\d{3})/\s*(2\d{3})", time_period):
        return _("SALES_GR", "1", vehicle_type, f"{match.group(2)}–{match.group(1)}")
    elif time_period == "Scope":
        # log.warning("Discard values for 'Scope' attribute")
        return _(None, None, None, None)
    else:  # pragma: no cover
        raise ValueError(time_period)


def convert_single_file(
    path: Path, dfd: "sdmx.model.v21.DataflowDefinition"
) -> Dict[str, List["sdmx.model.v21.DataSet"]]:
    """Convert single OICA data spreadsheet to SDMX.

    This function currently handles the 2020 and later file format used for sales and
    stock data.
    """
    from sdmx.model.v21 import DataSet

    from transport_data import STORE
    from transport_data.util.sdmx import make_obs

    if path.stem.endswith("2018") or path.stem.endswith("2019"):
        log.warning("Skip not implemented 2018–2019 OICA file format")
        return dict()

    # - Read data
    # - Drop entirely empty rows.
    # - Drop entirely empty columns.
    df = (
        pd.read_excel(path)
        .dropna(axis=0, how="all", ignore_index=True)  # type: ignore [call-overload]
        .dropna(axis=1, how="all")
    )

    # Confirm vehicle type and measure vs. contents of the title cell
    if "SALES" in dfd.id:
        pattern = r"REGISTRATIONS OR SALES OF NEW VEHICLES - (ALL TYPES|COMMERCIAL VEHICLES|PASSENGER CARS)"
        units = "vehicle"
    elif "STOCK" in dfd.id:
        pattern = r"(PC|CV|TOTAL) WORLD VEHICLES IN USE +\(in thousand units\)"
        units = "kvehicle"

    if match := re.fullmatch(pattern, df.iloc[0, 0]):
        # Codes are inconsistent across files; use shorter codes
        vehicle_type = {
            "ALL TYPES": "_T",
            "COMMERCIAL VEHICLES": "CV",
            "PASSENGER CARS": "PC",
            "TOTAL": "_T",
        }.get(match.group(1), match.group(1))
    else:  # pragma: no cover
        raise ValueError(f"Unrecognized table header: {df.iloc[0, 0]!r}")

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
        .dropna(subset=["GEO", "OBS_VALUE"], how="any")
    )

    # Prepare a GEO codelist and map using the "GEO" column
    cl_geo = get_cl_geo()
    geo_map = _make_geo_codes(
        cl_geo, df["GEO"], maintainer=get_agencies()[0], version="0.1"
    )
    # Store `cl_geo`, including any added entries
    STORE.set(cl_geo)

    # Transform data
    # - Replace GEO values with codes from `cl_geo`.
    # - Replace TIME_PERIOD values with new TIME_PERIOD, MEASURE, UNIT_MEASURE,
    #   VEHICLE_TYPE.
    # - Preserve OBS_VALUE.
    df = pd.concat(
        [
            df["GEO"].replace(geo_map),
            df["TIME_PERIOD"].apply(convert_tp, units=units, vehicle_type=vehicle_type),
            df["OBS_VALUE"],
        ],
        axis=1,
    ).dropna(subset=["MEASURE", "VEHICLE_TYPE"], how="any")

    result: Dict[str, List[DataSet]] = {}

    # Group data by MEASURE ~ dataflow
    for m, group_df in df.groupby("MEASURE"):
        # Create structures for this measure
        # TODO Retrieve possibly-cached or -stored structures
        dfd, dsd = get_structures(m)

        # Create a data set
        ds = DataSet(described_by=dfd, structured_by=dsd)

        # Convert rows of `group_df` to observations
        ds.add_obs(
            map(partial(make_obs, dsd=dsd), map(itemgetter(1), group_df.iterrows()))
        )

        # Store the data set
        result.setdefault(dfd.id, [])
        result[dfd.id].append(ds)

    return result


def fetch(dry_run: bool = False):
    """Fetch all known OICA data files."""
    if dry_run:
        for f in POOCH.registry:
            print(f"Valid url for GEO={f}: {POOCH.is_available(f)}")
        return

    return [POOCH.fetch(f) for f in POOCH.registry]


def filenames_for_dfd(
    dfd: "sdmx.model.v21.DataflowDefinition", fetch: bool = True
) -> Iterator[Path]:
    """Yield OICA's file names for individual files in `dfd`.

    Parameters
    ----------
    fetch : bool, optional
        If :obj:`.True` (the default), yield only files that are fetched and available
        locally. Otherwise, yield all possible names conforming to a known pattern.
    """
    if "PROD" in dfd.id:
        pattern = "{}-{}.xlsx"
        values = (
            {
                "By-country-region",
                "Passenger-Cars",
                "Light-Commercial-Vehicles",
                "Heavy-Trucks",
                "Buses-and-Coaches",
            },
            range(2017, 2024),
        )
    elif "SALES" in dfd.id:
        pattern = "{}_sales_{}.xlsx"
        values = {"cv", "pc", "total"}, range(2017, 2024)
    elif "STOCK" in dfd.id:
        pattern = "{}-World-vehicles-in-use-{}.xlsx"
        values = {"CV", "PC", "Total"}, range(2017, 2024)
    else:  # pragma: no cover
        raise NotImplementedError(f"Construct OICA file names for {dfd}")

    # Generate a cartesian product of the iterables in `values`
    for name_parts in product(*values):
        # Format a file name
        name = pattern.format(*name_parts)

        try:
            # Try to fetch if `fetch` is True; else return every name
            yield Path(POOCH.fetch(name) if fetch else name)
        except ValueError:
            pass


def _make_geo_codes(
    cl: "sdmx.model.common.Codelist", values: pd.Series, **kwargs
) -> Dict:
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

        # Update the map
        id_for_name.setdefault(value, code.id)

    values.sort_values().drop_duplicates().apply(_make_code)

    return id_for_name


@hookimpl
def get_agencies():
    """Return the OICA Agency."""
    from sdmx.model import v21

    a = v21.Agency(
        id="OICA",
        name="International Organization of Motor Vehicle Manufacturers",
        description="https://www.oica.net",
    )
    return (a,)


@hookimpl
def provides():
    return (
        "Codelist=TDCI:CL_OICA_GEO",
        "ConceptScheme=TDCI:CS_OICA_CONCEPTS",
    )


def get_cl_geo() -> "sdmx.model.common.Codelist":
    """Retrieve or create the ``Codelist=TDCI:OICA_GEO``."""
    import sdmx.urn
    from sdmx.model import common

    from transport_data import STORE, org

    candidate: common.Codelist = common.Codelist(
        id=f"{get_agencies()[0].id}_GEO",
        maintainer=org.get_agencies()[0],
    )
    assert candidate.maintainer is not None

    # Check for an existing version of this object
    if versions := STORE.list_versions(
        common.Codelist, candidate.maintainer.id, candidate.id
    ):
        # ≥1 version exists; get and return it
        candidate.version = versions[-1]
        return STORE.get(sdmx.urn.make(candidate))
    else:
        # No existing artefact; store the candidate with a default version and return it
        candidate.version = "1.0.0"
        STORE.set(candidate)
        return candidate


@lru_cache
def get_conceptscheme() -> "sdmx.model.common.ConceptScheme":
    """Return a concept scheme with OICA concepts."""
    from sdmx.model import common

    from transport_data import STORE, org

    cs = common.ConceptScheme(
        id=f"{get_agencies()[0].id}_CONCEPTS",
        maintainer=org.get_agencies()[0],
        version="0.1",
    )

    # Measures
    for id_, name in (
        ("PROD", "Production"),
        ("SALES", "Sales"),
        ("SALES_GR", "Sales growth over a given period"),
        ("STOCK", "Vehicles in use"),
        ("STOCK_AAGR", "Vehicles in use, average annual growth rate"),
        ("STOCK_CAP", "Vehicles in use per capita"),
    ):
        cs.append(common.Concept(id=id_, name=name))

    # TODO replace the following with references to a common TDCI concept scheme
    # Used as dimensions
    for id_, core_rep in (
        ("GEO", get_cl_geo()),
        ("VEHICLE_TYPE", None),
        ("TIME_PERIOD", None),
    ):
        c = common.Concept(id=id_)
        c.core_representation = (
            common.Representation(enumerated=core_rep) if core_rep else None
        )
        cs.append(c)
    # Used as attributes
    for id_ in ("UNIT_MEASURE",):
        cs.append(common.Concept(id=id_))
    # Used as primary measure
    for id_ in ("OBS_VALUE",):
        cs.append(common.Concept(id=id_))

    STORE.set(cs)

    return cs


def get_structures(
    measure: str,
) -> Tuple[
    "sdmx.model.v21.DataflowDefinition", "sdmx.model.v21.DataStructureDefinition"
]:
    """Create a data flow and data structure definitions for a given OICA `measure`.

    The DFD and DSD have URNs like ``TDCI:DF_OICA_{MEASURE}(0.1)``. The DSD has:

    - dimensions ``GEO``, ``VEHICLE_TYPE``, ``TIME_PERIOD``,
    - attributes ``UNIT_MEASURE``, and
    - primary measure with ID ``OBS_VALUE``.
    """
    from sdmx.model import v21

    from transport_data import STORE, org

    base = f"{get_agencies()[0].id}_{measure}"
    ma_args = dict(
        maintainer=org.get_agencies()[0],
        version="0.1",
        is_final=False,
        is_external_reference=False,
    )

    dfd = v21.DataflowDefinition(id=f"DF_{base}", **ma_args)
    STORE.set(dfd)
    dsd = v21.DataStructureDefinition(id=f"DS_{base}", **ma_args)
    STORE.set(dsd)

    if not dfd.is_final:
        # Associate
        dfd.structure = dsd

        # Mark as complete
        dfd.is_final = True
        STORE.set(dfd)

    if not dsd.is_final:
        cs = get_conceptscheme()

        for d, local_rep in (
            ("GEO", get_cl_geo()),
            ("VEHICLE_TYPE", None),
            ("TIME_PERIOD", None),
        ):
            dsd.dimensions.getdefault(
                id=d,
                concept_identity=cs[d],
                local_representation=v21.Representation(enumerated=local_rep),
            )

        for a in ("UNIT_MEASURE",):
            dsd.attributes.getdefault(id=a, concept_identity=cs[d])

        for m in ("OBS_VALUE",):
            dsd.measures.getdefault(id=m, concept_identity=cs[d])

        # Mark as complete
        dsd.is_final = True
        STORE.set(dsd)

    return dfd, dsd


def update_registry():
    """Update the registry.

    This function crawls :data:`.BASE_URL` for file names matching certain patterns.
    Files that exist are downloaded, hashed, and added to the :data:`.REGISTRY_FILE`.

    As of 2024-02-05, about 40 distinct files can be retrieved with :data:`.POOCH`. To
    view the list of files, use:

    .. code-block:: python

       from transport_data import oica
       print(oica.POOCH.registry)
    """
    from pooch import file_hash

    for dfd, _ in map(get_structures, ["PROD", "SALES", "STOCK"]):
        for file in filenames_for_dfd(dfd, fetch=False):
            filename = file.name
            existing_hash = POOCH.registry.setdefault(filename, None)

            if not POOCH.is_available(filename):
                # File doesn't exist on the remote
                POOCH.registry.pop(filename)
                continue

            if existing_hash is None:  # pragma: no cover
                # Download the file to add its hash
                path = POOCH.fetch(filename)
                POOCH.registry[filename] = file_hash(path)

    with open(REGISTRY_FILE, "w") as f:
        json.dump(POOCH.registry, f, indent=2, sort_keys=True)
