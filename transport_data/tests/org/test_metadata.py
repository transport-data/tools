from functools import partial
from pathlib import Path

import pytest

from transport_data.org.metadata import contains_data_for, groupby, merge_ato, report
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


def test_make_workbook_cli(tmp_path, tdc_cli) -> None:
    with tdc_cli.isolated_filesystem(temp_dir=tmp_path) as td:
        # Expected output path
        exp = Path(td, "sample.xlsx")
        result = tdc_cli.invoke(["org", "template"])

    # Command ran without error
    assert 0 == result.exit_code

    # Expected file was generated
    assert exp.exists()


@pytest.fixture(scope="session")
def converted_adb(tmp_store):
    """Converted ADB data and structures in the test data directory."""
    # 'Proper' method: repeat the conversion in the test data directory
    # from transport_data.adb import convert

    # for part in ("ACC", "APH", "CLC", "INF", "MIS", "RSA", "SEC", "TAS"):
    #     convert(part)

    # 'Fast' method: mirror the files from the user's directory
    from shutil import copyfile

    from transport_data import Config

    source_dir = Config().data_path.joinpath("local")
    dest_dir = tmp_store.store["local"].path

    def predicate(p: Path) -> bool:
        return "ADB:" in p.name

    for p in filter(predicate, source_dir.iterdir()):
        copyfile(p, dest_dir.joinpath(p.name))


def test_merge_ato(converted_adb, example_metadata) -> None:
    mds, cs = example_metadata

    merge_ato(mds)


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


class TestMetadataSet0ODT:
    def test_render(self, tmp_path, example_metadata) -> None:
        mds, cs_dims = example_metadata

        path = tmp_path.joinpath("all.odt")

        # Function runs successfully
        report.MetadataSet0ODT(mds).write_file(path)

        # Output was created
        assert path.exists()


class TestMetadataSet0Plain:
    def test_render(self, capsys, example_metadata) -> None:
        mds, cs_dims = example_metadata

        # Function runs successfully
        result = report.MetadataSet0Plain(mds).render()

        # pathlib.Path("debug.txt").write_text(result)  # DEBUG Write to a file
        # print(result)  # DEBUG Write to stdout

        # Output contains certain text
        assert "MEASURE: 39 unique values" in result

        # TODO expand with further assertions


class TestMetadataSet1HTML:
    @pytest.mark.parametrize("ref_area, N_exp", COUNTRIES)
    def test_write_file(self, tmp_path, example_metadata, ref_area, N_exp) -> None:
        path = tmp_path.joinpath(f"{ref_area}.html")

        report.MetadataSet1HTML(example_metadata[0], ref_area=ref_area).write_file(
            path, encoding="utf-8"
        )

        # Output was created
        assert path.exists()


@pytest.mark.parametrize("ref_area, N_exp", COUNTRIES)
class TestMetadataSet1ODT:
    def test_write_file(self, tmp_path, example_metadata, ref_area, N_exp) -> None:
        path = tmp_path.joinpath(f"{ref_area}.odt")

        report.MetadataSet1ODT(example_metadata[0], ref_area=ref_area).write_file(
            path=path
        )

        # Output was created
        assert path.exists()


class TestMetadataSet2HTML:
    def test_write_file(self, tmp_path, example_metadata) -> None:
        path = tmp_path.joinpath("all.html")

        report.MetadataSet2HTML(
            example_metadata[0], ref_area=list(item[0] for item in COUNTRIES)
        ).write_file(path, encoding="utf-8")

        # Output was created
        assert path.exists()


def test_read_cli(tmp_path, tdc_cli, test_data_path) -> None:
    path_in = test_data_path.joinpath("metadata-input.xlsx")

    result = tdc_cli.invoke(["org", "read", str(path_in)])

    # Command ran without error
    assert 0 == result.exit_code, result.output

    assert "MEASURE: 39 unique values" in result.output


def test_refresh_cli(tdc_cli) -> None:
    result = tdc_cli.invoke(["org", "refresh"])

    # Command ran without error
    assert 0 == result.exit_code, result.output


def test_summarize_cli(tmp_path, tdc_cli, test_data_path) -> None:
    path_in = test_data_path.joinpath("metadata-input.xlsx")

    # --ref-area= single value
    with tdc_cli.isolated_filesystem(temp_dir=tmp_path) as td:
        path_out = Path(td, "VN")
        result = tdc_cli.invoke(["org", "summarize", "--ref-area=VN", str(path_in)])

    # Command ran without error
    assert 0 == result.exit_code, result.output
    # Output files are generated
    assert path_out.with_suffix(".html").exists()
    assert path_out.with_suffix(".odt").exists()

    # --ref-area= multiple values
    with tdc_cli.isolated_filesystem(temp_dir=tmp_path) as td:
        path_out = Path(td, "all")
        result = tdc_cli.invoke(["org", "summarize", "--ref-area=TH,VN", str(path_in)])

    # Command ran without error
    assert 0 == result.exit_code, result.output
    # Output files are generated
    assert path_out.with_suffix(".html").exists()
    assert path_out.with_suffix(".odt").exists()


def test_tuewas_cli(tmp_path, tdc_cli, test_data_path) -> None:
    path_in = test_data_path.joinpath("metadata-input.xlsx")
    with tdc_cli.isolated_filesystem(temp_dir=tmp_path) as td:
        dir_out = Path(td, "output")
        result = tdc_cli.invoke(["org", "tuewas", str(path_in)])

    # Command ran without error
    assert 0 == result.exit_code, result.output
    # Expected files were generated
    assert dir_out.joinpath("Metadata summary.odt").exists()
    assert dir_out.joinpath("Metadata summary table.html").exists()
    assert dir_out.joinpath("CN", "Summary.odt").exists()
