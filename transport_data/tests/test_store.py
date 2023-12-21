import pytest
import sdmx.model.v21

from transport_data.config import Config
from transport_data.org import get_agencyscheme
from transport_data.store import BaseStore, LocalStore


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
