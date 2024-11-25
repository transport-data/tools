import re

import pytest
from prompt_toolkit.input.ansi_escape_sequences import REVERSE_ANSI_SEQUENCES
from prompt_toolkit.keys import Keys

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


def _backspace(text: str) -> str:
    """Generate ANSI sequences for backspacing over `text`."""
    return len(text) * REVERSE_ANSI_SEQUENCES[Keys.ControlH]


#: ‘Script’ of CLI input to produce a code list.
SCRIPT_2 = [
    "99",  # Class: 99 → doesn't exist, return to the same meeting
    "2",  # Class: 2 = Codelist
    _backspace("TDCI") + "TEST",  # Maintainer ID
    "CL_CLI_EDIT",  # Artefact ID
    "",  # Artefact name
    "",  # Artefact version (accept default 1.0.0)
    "n",  # New Item
    "FOO",  # Item ID
    "Foo",  # Item name
    "n",
    "BAR",  # Item ID
    "Bar",
    "n",
    "BAZ",  # Item ID
    "",  # Item name
    "10",  # Edit 10th created item (doesn't exist, return to the same view)
    "2",  # Edit 2nd created item (BAR)
    "QUX",  # New Item ID
    "",  # Keep existing name
    "",  # Continue
    "y",  # Save
]


@pytest.mark.timeout(1)
def test_edit2(tmp_store) -> None:
    # CLI runs and accepts the input without error
    run_script(SCRIPT_2)

    # A code list is generated in the tmp_store
    cl = tmp_store.get("Codelist=TEST:CL_CLI_EDIT(1.0.0)")

    # The code list has 3 items
    assert {"FOO", "QUX", "BAZ"} == set(cl.items.keys())
    # The ID but not name of the second item was edited
    assert "Bar" == cl["QUX"].name["en"]


#: ‘Script’ of CLI input to produce a data flow definition.
SCRIPT_4 = [
    "4",  # Class: 4 = DataflowDefinition
    _backspace("TDCI") + "TEST",  # Maintainer ID
    "DF_CLI_EDIT",  # Artefact ID
    "",  # Artefact name
    "",  # Artefact version (accept default 1.0.0)
    "DataStructureDefinition=TEST:MASS(1.0.0)",  # URN of the DSD
    "y",  # Save
]


@pytest.mark.timeout(1)
@pytest.mark.usefixtures("sdmx_structures")
def test_edit4(tmp_store) -> None:
    # CLI runs and accepts the input without error
    run_script(SCRIPT_4)

    # A DFD is generated in the tmp_store
    tmp_store.get("Dataflow=TEST:DF_CLI_EDIT(1.0.0)")


#: ‘Script’ of CLI input to produce a data structure definition.
SCRIPT_5 = [
    "5",  # Class: 5 = DataStructureDefinition
    _backspace("TDCI") + "TEST",  # Maintainer ID
    "DS_CLI_EDIT",  # Artefact ID
    "",  # Artefact name
    "",  # Artefact version (accept default 1.0.0)
    "FOO",  # Dimension
    "BAR",
    "BAZ",
    "",  # Continue
    "OBS_VALUE",  # Measure
    "",
    "UNIT_MEASURE",  # Attribute
    "OBS_STATUS",
    "",
    "y",  # Save
]


@pytest.mark.timeout(1)
def test_edit5(tmp_store) -> None:
    # CLI runs and accepts the input without error
    run_script([REVERSE_ANSI_SEQUENCES[Keys.ControlC]])
    # Nothing was saved because ControlC was given
    with pytest.raises(KeyError):
        tmp_store.get("DataStructureDefinition=TEST:DS_CLI_EDIT(1.0.0)")

    # CLI runs and accepts the input without error
    run_script(SCRIPT_5[:-1] + [""])
    # Nothing was saved, because "y" was not given at the final, "Save" view
    with pytest.raises(KeyError):
        tmp_store.get("DataStructureDefinition=TEST:DS_CLI_EDIT(1.0.0)")

    # CLI runs and accepts the input without error
    run_script(SCRIPT_5)

    # A DSD is generated in the tmp_store
    dsd = tmp_store.get("DataStructureDefinition=TEST:DS_CLI_EDIT(1.0.0)")
    # It has contents according to the CLI inputs
    assert 3 == len(dsd.dimensions)
    assert 1 == len(dsd.measures)
    assert 2 == len(dsd.attributes)
