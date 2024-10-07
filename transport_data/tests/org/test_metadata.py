from functools import partial

import pytest

from transport_data.org.metadata import contains_data_for, groupby, report
from transport_data.org.metadata.spreadsheet import make_workbook, read_workbook

#: Number of metadata reports in the test specimen for which contains_data_for() returns
#: :any:`True`.
COUNTRIES = [
    ("CN", 19),
    ("ID", 17),
    ("IN", 19),
    ("PH", 14),
    ("NP", 0),
    ("TH", 17),
    ("VN", 18),
]


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


@pytest.mark.parametrize("ref_area, N_exp", COUNTRIES)
def test_groupby(example_metadata, ref_area, N_exp: int) -> None:
    predicate = partial(contains_data_for, ref_area=ref_area)
    result = groupby(example_metadata[0], predicate)

    # Expected counts of metadata reports with respective values
    # NB Use set notation to tolerate missing keys in `result` if N_exp == 0
    exp = {(True, N_exp), (False, 45 - N_exp)}

    # Observed counts match
    assert exp >= {(k, len(v)) for k, v in result.items()}


class TestMetadataSetHTML0:
    @pytest.mark.parametrize("ref_area, N_exp", COUNTRIES)
    def test_write_file(self, tmp_path, example_metadata, ref_area, N_exp) -> None:
        path = tmp_path.joinpath(f"{ref_area}.html")

        report.MetadataSetHTML0(example_metadata[0], ref_area=ref_area).write_file(
            path, encoding="utf-8"
        )

        # Output was created
        assert path.exists()


class TestMetadataSetHTML1:
    def test_write_file(self, tmp_path, example_metadata) -> None:
        path = tmp_path.joinpath("all.html")

        report.MetadataSetHTML1(
            example_metadata[0], ref_area=list(item[0] for item in COUNTRIES)
        ).write_file(path, encoding="utf-8")

        # Output was created
        assert path.exists()


@pytest.mark.parametrize("ref_area, N_exp", COUNTRIES)
class TestMetadataSetODT:
    def test_write_file(self, tmp_path, example_metadata, ref_area, N_exp) -> None:
        path = tmp_path.joinpath(f"{ref_area}.odt")

        report.MetadataSetODT(example_metadata[0], ref_area=ref_area).write_file(
            path=path
        )

        # Output was created
        assert path.exists()


class TestMetadataSetPlain:
    def test_render(self, capsys, example_metadata) -> None:
        mds, cs_dims = example_metadata

        # Function runs successfully
        result = report.MetadataSetPlain(mds).render()

        # pathlib.Path("debug.txt").write_text(result)  # DEBUG Write to a file
        # print(result)  # DEBUG Write to stdout

        # Output contains certain text
        assert "MEASURE: 39 unique values" in result

        # TODO expand with further assertions
