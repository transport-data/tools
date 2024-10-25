import pytest
import sdmx

from transport_data.testing import ember_dfd
from transport_data.util.sdmx import read_csv


@pytest.mark.parametrize(
    "filename, adapt",
    (
        # SDMX-CSV
        ("read-csv-0.csv", {}),
        # Simplified CSV with CSVAdapter arguments
        (
            "read-csv-1.csv",
            dict(
                structure="dataflow",
                structure_id="TDCI:EMBER_001(1.0.0)",
                action="I",
            ),
        ),
    ),
)
def test_read_csv(test_data_path, filename, adapt) -> None:
    dfd = ember_dfd()

    # CSV data are read without error
    dm = read_csv(test_data_path.joinpath(filename), dfd, adapt)

    # A single data set is returned
    assert 1 == len(dm.data)

    # Data have the expected number of observations
    ds = dm.data[0]
    assert 120 == len(ds)

    # Data are structured by the given DFD and DSD
    assert set(ds.obs[0].dimension.values.keys()) == set(
        d.id for d in dfd.structure.dimensions
    )

    # Data can be converted to pandas
    df = sdmx.to_pandas(ds, attributes="o")

    # Observation values and attributes are accessible and have expected type and values
    assert 599.0 == df.loc[("China", "2021"), "value"]
    assert "FOO" == df.loc[("China", "2021"), "COMMENT"]
