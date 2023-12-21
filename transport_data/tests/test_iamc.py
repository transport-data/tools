from pathlib import Path

import pandas as pd
import sdmx

from transport_data.iamc import structures_for_data, variable_cl_for_dsd


def test_structures_for_data():
    # Load test data
    test_data_path = Path(__file__).parents[1].joinpath("data", "tests")
    df = pd.read_csv(test_data_path.joinpath("iamc.csv"))

    # Function runs, returns a SDMX StructureMessage containing multiple structure
    # objects
    sm = structures_for_data(df, base_id="TEST")

    # Code lists have expected length
    expected = {
        "MODEL": 1,
        "SCENARIO": 6,
        "REGION": 10,
        "UNIT": 39,
    }

    for name, N in expected.items():
        assert N == len(sm.codelist[name])

    # Concept schemes have expected length
    assert 31 == len(sm.concept_scheme["MEASURE"])

    # DSD is annotated with a description of the data from which it was derived
    dsd = sm.structure["TEST"]
    assert str(dsd.description).startswith("The original data are in")


def test_variables_cl_for_dsd(tmp_path, sdmx_structures):
    # Function runs on the "MASS" DSD
    cl = variable_cl_for_dsd(sdmx_structures.structure["MASS"])

    # Expected number of variable names is generated
    assert 25 == len(cl)

    # Function runs on the "PICKED" DSD
    variable_cl_for_dsd(sdmx_structures.structure["PICKED"], cl)

    # Items are appended to `cl`
    assert 50 == len(cl)

    # Codelist can be roundtripped via file
    path = tmp_path.joinpath("data.xml")
    # print(f"{path = }")

    sm_out = sdmx.message.StructureMessage()
    sm_out.add(cl)

    with open(path, "wb") as f:
        f.write(sdmx.to_xml(sm_out, pretty_print=True))

    sm_in = sdmx.read_sdmx(path)
    cl_in = sm_in.codelist["VARIABLE"]

    # Codes can be accessed by ID == IAMC variable name
    code = cl_in["Mass of fruit|Green"]

    # Code is annotated with the URN of the full-dimensionality DSD
    assert code.eval_annotation("iamc-full-dsd").endswith(
        "DataStructureDefinition=TEST:MASS(1.0)"
    )
    # Code is annotated with its full key; no missing dimensions
    assert {"COLOUR": "GREEN", "FRUIT": "_T"} == code.eval_annotation("iamc-full-key")
