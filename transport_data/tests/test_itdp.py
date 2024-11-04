from functools import partial
from typing import TYPE_CHECKING

import pytest
import sdmx
from sdmx.model import v21

from transport_data import testing
from transport_data.itdp.rtdb import convert, fetch

if TYPE_CHECKING:
    import pathlib


@pytest.fixture
def cached_rtdb_data(tmp_config):
    try:
        return fetch()
    except FileNotFoundError:
        if testing.GITHUB_ACTIONS:
            pytest.skip(reason="No Google Cloud API credentials on GitHub Actions")
        else:
            raise


COUNTRIES = [
    ("CN", 144),
    ("ID", 43),
    ("IN", 97),
    ("PH", 78),
    ("NP", 0),
    ("TH", 58),
    ("VN", 13),
]


def test_convert(caplog, cached_rtdb_data: "pathlib.Path") -> None:
    ds1 = convert(cached_rtdb_data)

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
