from functools import partial
from shutil import copyfile
from typing import TYPE_CHECKING

import pytest
import sdmx
from sdmx.model import v21

from transport_data import Config, testing
from transport_data.itdp.rtdb import convert, fetch

if TYPE_CHECKING:
    import pathlib


@pytest.fixture(scope="session")
def rtdb_test_data(test_data_path, tmp_config: Config) -> "pathlib.Path":
    """Copy of the RTDB snapshot in the test cache directory."""
    source = test_data_path.joinpath("itdp", "rtdb.xlsx")
    dest = tmp_config.cache_path.joinpath("itdp", "rtdb.xlsx")
    dest.parent.mkdir(parents=True, exist_ok=True)

    copyfile(source, dest)

    return dest


COUNTRIES = [
    ("CN", 144),
    ("ID", 43),
    ("IN", 97),
    ("PH", 78),
    ("NP", 0),
    ("TH", 58),
    ("VN", 13),
]


def test_convert(caplog, rtdb_test_data: "pathlib.Path") -> None:
    ds1 = convert(rtdb_test_data)

    def _filter_geo(value: str, obs: "v21.Observation") -> bool:
        assert obs.dimension
        return obs.dimension["GEO"].value == value

    for geo, N in COUNTRIES:
        ds2 = v21.DataSet(
            structured_by=ds1.structured_by,
            obs=list(filter(partial(_filter_geo, geo), ds1.obs)),
        )

        df = sdmx.to_pandas(ds2).reset_index()
        if len(df):
            df = df.query("value > 0")

        assert N == len(df)


@pytest.mark.xfail(
    condition=testing.GITHUB_ACTIONS,
    reason="No Google Cloud API credentials on GitHub Actions",
    raises=RuntimeError,
)
def test_fetch():
    fetch()
