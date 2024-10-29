from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner
from sdmx.model import common, v21

from transport_data.config import Config
from transport_data.org import get_agencyscheme
from transport_data.store import main

if TYPE_CHECKING:
    import dsss.store


class TestBaseStore:
    """:mod:`dsss` classes provide features required by :mod:`transport_data`."""

    @pytest.fixture
    def s(self, tmp_config: Config, sdmx_structures) -> "dsss.store.Store":
        from dsss.store import DictStore

        # Create a DictStore
        s = DictStore()

        # Set some items
        s.set(sdmx_structures.codelist["FRUIT"])

        return s

    def test_list_versions(self, s: "dsss.store.Store") -> None:
        result = s.list_versions(common.Codelist, maintainer="TEST", id="FRUIT")

        assert ("1.0.0",) == result

        assert tuple() == s.list_versions(common.Codelist, maintainer="TEST", id="FOO")

    def test_assign_version(self, sdmx_structures, s: "dsss.store.Store") -> None:
        cl: "common.Codelist" = common.Codelist(
            id="FRUIT", maintainer=common.Agency(id="TEST")
        )

        s.assign_version(cl, major=1)

        assert "2.0.0" == cl.version


class TestUnionStore:
    """Test the :class:`transport_data.store.UnionStore` subclass."""

    @pytest.fixture(scope="class")
    def tdci_agencyscheme(self, tmp_store):
        tmp_store.set(get_agencyscheme())

    @pytest.mark.usefixtures("sdmx_structures")
    def test_add_to_registry(self, tmp_store) -> None:
        tmp_store.add_to_registry("Codelist=TEST:FRUIT(1.0.0)")

    @pytest.mark.usefixtures("sdmx_structures", "tdci_agencyscheme")
    @pytest.mark.parametrize(
        "urn, cls",
        (
            (
                "urn:sdmx:org.sdmx.infomodel.base.AgencyScheme=TDCI:TDCI",
                common.AgencyScheme,
            ),
            (
                "urn:sdmx:org.sdmx.infomodel.base.AgencyScheme=TDCI:TDCI(0.0.1)",
                common.AgencyScheme,
            ),
            ("AgencyScheme=TDCI:TDCI(0.0.1)", common.AgencyScheme),
            ("AgencyScheme=TDCI:TDCI", common.AgencyScheme),
            # DSD can be retrieved with normalized or non-normalized ID
            pytest.param(
                "DataStructure=TEST:MASS(1.0.0)",
                v21.DataStructureDefinition,
                marks=pytest.mark.xfail(  # TODO Remove when fixed upstream
                    raises=UnboundLocalError, reason="Limitation in sdmx1 v2.19.1"
                ),
            ),
            ("DataStructureDefinition=TEST:MASS(1.0.0)", v21.DataStructureDefinition),
        ),
    )
    def test_get(self, tmp_store, urn, cls) -> None:
        """Objects can be retrieved by partial URN."""
        result = tmp_store.get(urn)
        assert isinstance(result, cls)

    def test_list(self, tmp_store) -> None:
        result = sorted(tmp_store.list(maintainer="TEST"))
        assert 5 == len(result)
        assert result[0].endswith("Codelist=TEST:COLOUR(1.0.0)")
        assert result[-1].endswith("DataStructure=TEST:PICKED(1.0.0)"), result


def test_cli_list(sdmx_structures):
    result = CliRunner().invoke(main, ["list", "--maintainer=TEST"])
    assert 0 == result.exit_code
    # FIXME Avoid a result that depends on test run order
    assert len(result.output.splitlines()) in (4, 5), result.output


def test_cli_show(sdmx_structures):
    result = CliRunner().invoke(main, ["show", "Codelist=TEST:COLOUR(1.0.0)"])
    assert 0 == result.exit_code
    assert "  4 <Code _T: Total>" in result.output
