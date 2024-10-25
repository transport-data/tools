import re

import pytest


@pytest.mark.parametrize(
    "command",
    (
        ("--help",),
        ("adb", "--help"),
        ("adb", "fetch", "--all"),
        ("check", "--help"),
        ("config", "--help"),
        ("estat", "--help"),
        ("estat", "fetch", "--help"),
        ("iamc", "--help"),
        ("iamc"),
        ("jrc", "--help"),
        ("jrc", "fetch", "--all"),
        ("org", "--help"),
        ("org", "--version=0.0.0"),
        ("proto", "--help"),
        ("store", "--help"),
    ),
)
def test_cli(tdc_cli, command):
    tdc_cli.invoke(command)


def test_check(tdc_cli, test_data_path):
    result = tdc_cli.invoke(
        [
            "check",
            "--sheets=sheet_2",
            "--structure=dataflow",
            "--structure-id=FOO",
            "--action=I",
            str(test_data_path.joinpath("read-csv-2.xlsx")),
        ]
    )

    # Command runs without error
    assert 0 == result.exit_code, result.output

    # Data was located, converted to CSV, read, and summary displayed
    assert re.fullmatch(
        r"""
File: .*read-csv-2.xlsx
Sheet: sheet_2

1 data set\(s\) in data flow Dataflow=TDCI:EMBER_001\(1.0.0\)

Data set 0: action=ActionType.information
120 observations
""",
        result.output,
    )
