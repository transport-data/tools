from click.testing import CliRunner

from transport_data.cli import main


def test_cli():
    runner = CliRunner()
    runner.invoke(main)
