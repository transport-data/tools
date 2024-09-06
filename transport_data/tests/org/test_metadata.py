from transport_data.org.metadata import (
    make_workbook,
    read_workbook,
    summarize_metadataset,
)


def test_make_workbook(tmp_path) -> None:
    make_workbook()


def test_read_workbook(test_data_path) -> None:
    # Function runs successfully
    result = read_workbook(test_data_path.joinpath("metadata-input.xlsx"))

    # Result has a certain number of metadata reports
    assert 47 == len(result.report)


def test_summarize_metadataset(capsys, test_data_path) -> None:
    mds = read_workbook(test_data_path.joinpath("metadata-input.xlsx"))

    # Function runs successfully
    summarize_metadataset(mds)

    captured = capsys.readouterr()
    # pathlib.Path("debug.txt").write_text(captured.out)  # DEBUG Write to a file

    # Output contains certain text
    assert "MEASURE: 40 unique values" in captured.out

    # TODO expand with further assertions
