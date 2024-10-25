import pytest
import sdmx
from sdmx.model import common, v30

from transport_data.util.sdmx import read_csv


@pytest.fixture(scope="module")
def dfd():
    # Construct a DSD corresponding to the data
    ma_kw = dict(id="EMBER_001", version="1.0.0", maintainer=common.Agency(id="TDCI"))
    dsd = v30.DataStructureDefinition(**ma_kw)
    dsd.dimensions.append(v30.Dimension(id="COUNTRY"))
    dsd.dimensions.append(v30.Dimension(id="YEAR"))
    dsd.measures.append(v30.Measure(id="OBS_VALUE"))
    dsd.attributes.append(common.DataAttribute(id="COMMENT"))
    # Construct a DFD
    yield v30.Dataflow(**ma_kw, structure=dsd)


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
def test_read_csv(test_data_path, dfd, filename, adapt) -> None:
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
