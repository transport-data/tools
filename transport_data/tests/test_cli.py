import re

import pytest

from transport_data.cli.interactive import Editor
from transport_data.testing import ember_dfd


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


def test_check(tdc_cli, test_data_path, tmp_store):
    ember_dfd(tmp_store)

    result = tdc_cli.invoke(
        [
            "check",
            "--sheets=sheet_2",
            "--structure=dataflow",
            "--structure-id=FOO",
            "--action=I",
            "Dataflow=TDCI:EMBER_001(1.0.0)",
            str(test_data_path.joinpath("read-csv-2.xlsx")),
        ]
    )

    # Command runs without error
    assert 0 == result.exit_code, result.output

    # Data was located, converted to CSV, read, and summary displayed
    print(result.output)
    assert re.fullmatch(
        r"""
File: .*read-csv-2.xlsx
Sheet: sheet_2

1 data set\(s\) in: Dataflow.*=TDCI:EMBER_001\(1.0.0\)

Data set 0: action=ActionType.information
120 observations
""",
        result.output,
    )


# ‘Script’ of CLI input to produce a data structure definition
SCRIPT = [
    # Maintainer ID: accept the default (TDCI)
    "",
    # DSD ID
    "CLI_TEST",
    # Version
    "1.0.0",
    # Dimension
    "FOO",
    "BAR",
    "BAZ",
    "",
    # Measure
    "OBS_VALUE",
    "",
    # Attribute
    "UNIT_MEASURE",
    "OBS_STATUS",
    "",
    # Save
    "y",
]


def run_script(lines: list[str]) -> None:
    """Create a contained instance of :class:`.Editor` and feed it `lines`."""
    from prompt_toolkit.application import create_app_session
    from prompt_toolkit.input import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    # Create an input pipe
    with create_pipe_input() as pipe_input:
        # Feed the script into the pipe
        for line in lines:
            pipe_input.send_text(line + "\r")

        # Create an app session; run the app within the session
        with create_app_session(input=pipe_input, output=DummyOutput()):
            Editor().run()


def test_edit(tmp_store) -> None:
    from prompt_toolkit.input.ansi_escape_sequences import REVERSE_ANSI_SEQUENCES
    from prompt_toolkit.keys import Keys

    # CLI runs and accepts the input without error
    run_script([REVERSE_ANSI_SEQUENCES[Keys.ControlC]])
    # Nothing was saved because ControlC was given
    with pytest.raises(KeyError):
        tmp_store.get("DataStructureDefinition=TDCI:CLI_TEST(1.0.0)")

    # CLI runs and accepts the input without error
    run_script(SCRIPT[:-1] + [""])
    # Nothing was saved, because "y" was not given at the final, "Save" view
    with pytest.raises(KeyError):
        tmp_store.get("DataStructureDefinition=TDCI:CLI_TEST(1.0.0)")

    # CLI runs and accepts the input without error
    run_script(SCRIPT)

    # A DSD is generated in the tmp_store
    dsd = tmp_store.get("DataStructureDefinition=TDCI:CLI_TEST(1.0.0)")
    # It has contents according to the CLI inputs
    assert 3 == len(dsd.dimensions)
    assert 1 == len(dsd.measures)
    assert 2 == len(dsd.attributes)
