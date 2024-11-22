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


CHECK_ARGS = [
    "--structure=dataflow",
    "--structure-id=FOO",
    "--action=I",
    "--sheets=sheet_2",
    "Dataflow=TDCI:EMBER_001(1.0.0)",
]


def test_check0(tdc_cli, test_data_path, tmp_store):
    """Check a successful read of a .xlsx file."""
    ember_dfd(tmp_store)

    path = test_data_path.joinpath("read-csv-2.xlsx")
    result = tdc_cli.invoke(["check"] + CHECK_ARGS + [str(path)])

    # Command runs without error
    assert 0 == result.exit_code, result.output

    # Data was located, converted to CSV, read, and summary displayed
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


@pytest.mark.parametrize(
    "args, exit_code, text",
    (
        (["X"], 1, "line 1, field 1"),  # Omit all options and URN
        (CHECK_ARGS[:1] + ["X"], 1, "line 1, field 2"),  # Only --structure=
        (CHECK_ARGS[:2] + ["X"], 1, "'X' could not be loaded"),  # Invalid structure URN
        (CHECK_ARGS + ["-v"], 0, "..."),  # Show pd.DataFrame abbreviated string repr
        (CHECK_ARGS + ["-vv"], 0, ""),  # Show pd.DataFrame full string repr
    ),
)
def test_check1(tdc_cli, test_data_path, tmp_store, args, exit_code, text):
    """Check various other argument combinations."""
    ember_dfd(tmp_store)

    path = test_data_path.joinpath("read-csv-1.csv")
    result = tdc_cli.invoke(["check"] + args + [str(path)])

    # Command gives the expected exit code
    assert exit_code == result.exit_code, result.output

    # Expected text is contained in the output
    if text:
        assert text in result.output


def test_check2(tdc_cli, tmp_path):
    path = tmp_path.joinpath("foo.txt")
    path.touch()
    result = tdc_cli.invoke(["check", "X", str(path)])

    assert 2 == result.exit_code, result.output
    assert "Unsupported file extension" in result.output


# ‘Script’ of CLI input to produce a data structure definition
SCRIPT0 = [
    # Class: 1 = DataStructureDefinition
    "1",
    # Maintainer ID: accept the default (TDCI)
    "TDCI",
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

# ‘Script’ of CLI input to produce a data flow definition
SCRIPT1 = [
    # Class: 1 = DataStructureDefinition
    "0",
    # Maintainer ID: accept the default (TDCI)
    "TDCI",
    # DSD ID
    "CLI_TEST",
    # Version
    "1.0.0",
    # Structure URN
    "DataStructureDefinition=TDCI:CLI_TEST(1.0.0)",
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


def test_edit0(tmp_store) -> None:
    from prompt_toolkit.input.ansi_escape_sequences import REVERSE_ANSI_SEQUENCES
    from prompt_toolkit.keys import Keys

    # CLI runs and accepts the input without error
    run_script([REVERSE_ANSI_SEQUENCES[Keys.ControlC]])
    # Nothing was saved because ControlC was given
    with pytest.raises(KeyError):
        tmp_store.get("DataStructureDefinition=TDCI:CLI_TEST(1.0.0)")

    # CLI runs and accepts the input without error
    run_script(SCRIPT0[:-1] + [""])
    # Nothing was saved, because "y" was not given at the final, "Save" view
    with pytest.raises(KeyError):
        tmp_store.get("DataStructureDefinition=TDCI:CLI_TEST(1.0.0)")

    # CLI runs and accepts the input without error
    run_script(SCRIPT0)

    # A DSD is generated in the tmp_store
    dsd = tmp_store.get("DataStructureDefinition=TDCI:CLI_TEST(1.0.0)")
    # It has contents according to the CLI inputs
    assert 3 == len(dsd.dimensions)
    assert 1 == len(dsd.measures)
    assert 2 == len(dsd.attributes)


def test_edit1(tmp_store) -> None:
    # CLI runs and accepts the input without error
    run_script(SCRIPT1)

    # A DFD is generated in the tmp_store
    tmp_store.get("Dataflow=TDCI:CLI_TEST(1.0.0)")
