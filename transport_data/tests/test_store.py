import pytest
import sdmx.model.v21
from click.testing import CliRunner

from transport_data.config import Config
from transport_data.org import get_agencyscheme
from transport_data.store import BaseStore, LocalStore, main


class TestBaseStore:
    @pytest.fixture
    def s(self, tmp_config: Config) -> BaseStore:
        s = LocalStore(tmp_config)
        s.write(get_agencyscheme())
        return s

    @pytest.mark.parametrize(
        "urn",
        (
            "AgencyScheme=TDCI:TDCI(0.1.0)",
            "AgencyScheme=TDCI:TDCI",
        ),
    )
    def test_get(self, sdmx_structures, s, urn) -> None:
        """Objects can be retrieved by partial URN."""
        result = s.get(urn)
        assert isinstance(result, sdmx.model.v21.AgencyScheme)


class TestUnionStore:
    def test_add_to_registry(self, tmp_store, sdmx_structures) -> None:
        s = tmp_store
        s.add_to_registry("Codelist=TEST:FRUIT(1.0.0)")

    def test_list(self, tmp_store, sdmx_structures) -> None:
        result = tmp_store.list("TEST")
        assert 5 == len(result)
        assert "Codelist=TEST:COLOUR(1.0.0)" == result[0]
        assert "DataStructureDefinition=TEST:PICKED(1.0.0)" == result[-1]


def test_cli_list(sdmx_structures):
    result = CliRunner().invoke(main, ["list", "TEST"])
    assert 0 == result.exit_code
    assert 5 == len(result.output.splitlines())


def test_cli_show(sdmx_structures):
    result = CliRunner().invoke(main, ["show", "Codelist=TEST:COLOUR(1.0.0)"])
    assert 0 == result.exit_code
    assert "  4 <Code _T: Total>" in result.output
