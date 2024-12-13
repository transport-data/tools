from dataclasses import dataclass

import pytest
import sdmx
from sdmx.model import v21

from transport_data.testing import ember_dfd
from transport_data.util.sdmx import fields_to_mda, read_csv


def test_fields_to_mda() -> None:
    mdsd = v21.MetadataStructureDefinition()
    rs = mdsd.report_structure["ALL"] = v21.ReportStructure(id="ALL")

    assert 0 == len(rs)

    @dataclass
    class MDSExample:
        #: Foo
        #:
        #: Description of Foo.
        foo: str

        bar: int

    fields_to_mda(MDSExample, rs)

    # Report structure has 1 metadata attribute for each of the fields in MDSExample
    assert 2 == len(rs)

    # Metadata attributes have expected IDs
    assert "foo" == rs.components[0].id == rs.components[0].concept_identity.id
    assert "bar" == rs.components[1].id == rs.components[1].concept_identity.id

    # Python type annotations are stored as 'data-type' SDMX annotations
    assert "<class 'str'>" == rs.components[0].eval_annotation(id="data-type")
    assert "<class 'int'>" == rs.components[1].eval_annotation(id="data-type")

    # Python docstrings are stored as name and description on the ConceptIdentity
    assert "Foo" == str(rs.components[0].concept_identity.name)
    assert "Description of Foo." == str(rs.components[0].concept_identity.description)
    assert 0 == len(rs.components[1].concept_identity.name.localizations)
    assert 0 == len(rs.components[1].concept_identity.description.localizations)


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
def test_read_csv(test_data_path, tmp_store, filename, adapt) -> None:
    dfd = ember_dfd(tmp_store)

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
