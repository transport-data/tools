from functools import partial

import pytest

from transport_data.org.metadata import (
    contains_data_for,
    generate_summary_html0,
    generate_summary_html1,
    groupby,
    make_workbook,
    read_workbook,
    summarize_metadataset,
)


def test_make_workbook(tmp_path) -> None:
    make_workbook()


@pytest.fixture(scope="module")
def example_metadata(test_data_path):
    return read_workbook(test_data_path.joinpath("metadata-input.xlsx"))


def test_read_workbook(example_metadata) -> None:
    # Function runs successfully
    result, _ = example_metadata

    # Result has a certain number of metadata reports
    assert 45 == len(result.report)


def test_summarize_metadataset(capsys, example_metadata) -> None:
    mds, cs_dims = example_metadata

    # Function runs successfully
    summarize_metadataset(mds)

    captured = capsys.readouterr()
    # pathlib.Path("debug.txt").write_text(captured.out)  # DEBUG Write to a file

    # Output contains certain text
    assert "MEASURE: 39 unique values" in captured.out

    # TODO expand with further assertions


COUNTRIES = [
    ("CN", 19),
    ("ID", 17),
    ("IN", 19),
    ("PH", 14),
    ("NP", 0),
    ("TH", 17),
    ("VN", 18),
]


@pytest.mark.parametrize("ref_area, N_exp", COUNTRIES)
def test_groupby(example_metadata, ref_area, N_exp: int) -> None:
    predicate = partial(contains_data_for, ref_area=ref_area)
    result = groupby(example_metadata[0], predicate)

    # Expected counts of metadata reports with respective values
    # NB Use set notation to tolerate missing keys in `result` if N_exp == 0
    exp = {(True, N_exp), (False, 45 - N_exp)}

    # Observed counts match
    assert exp >= {(k, len(v)) for k, v in result.items()}


@pytest.mark.parametrize("ref_area, N_exp", COUNTRIES)
def test_generate_summary_html0(tmp_path, example_metadata, ref_area, N_exp) -> None:
    path = tmp_path.joinpath(f"{ref_area}.html")

    generate_summary_html0(example_metadata[0], ref_area=ref_area, path=path)

    # Output was created
    assert path.exists()


def test_generate_summary_html1(tmp_path, example_metadata) -> None:
    path = tmp_path.joinpath("all.html")

    generate_summary_html1(
        example_metadata[0], ref_area=list(item[0] for item in COUNTRIES), path=path
    )

    # Output was created
    assert path.exists()
