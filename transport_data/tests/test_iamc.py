from pathlib import Path

import pandas as pd

from transport_data.iamc import make_dsd_for


def test_make_dsd_for():
    # Load test data
    test_data_path = Path(__file__).parents[1].joinpath("data", "tests")
    df = pd.read_csv(test_data_path.joinpath("iamc.csv"))

    # Function runs, returns a SDMX StructureMessage containing multiple structure
    # objects
    sm = make_dsd_for(df)

    # Code lists have expected length
    expected = {
        "MODEL": 1,
        "SCENARIO": 6,
        "REGION": 10,
        "UNIT": 39,
        "MEASURE": 31,
    }

    for name, N in expected.items():
        assert N == len(sm.codelist[name])

    # DSD is annotated with a description of the data from which it was derived
    dsd = sm.structure["GENERATED"]
    assert str(dsd.description).startswith("The original data are in")
