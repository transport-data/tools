import pytest
import sdmx.model.v21

import transport_data
import transport_data.registry


class TestStore:
    @pytest.fixture
    def s(self) -> transport_data.registry.Store:
        return transport_data.STORE

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
