import pytest
from click.testing import CliRunner
from pytest import param

from transport_data.cli import main


@pytest.mark.parametrize(
    "command",
    (
        ("",),
        ("--help",),
        ("adb", "--help"),
        ("adb", "fetch", "--all"),
        ("config", "--help"),
        ("estat", "--help"),
        ("estat", "fetch", "--help"),
        param(("estat", "fetch", "--help"), marks=pytest.mark.network),
        ("iamc", "--help"),
        ("jrc", "--help"),
        ("jrc", "fetch", "--all"),
        ("org", "--help"),
        ("org", "--version=0.0.0"),
        ("proto", "--help"),
        ("registry", "--help"),
    ),
)
def test_cli(command):
    runner = CliRunner()
    runner.invoke(main, command)
