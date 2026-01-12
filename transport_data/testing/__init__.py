import json
import os
import platform
import re
import zipfile
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING, cast

import click.testing
import pytest
import responses
import sdmx.message
from requests.exceptions import HTTPError
from sdmx.model import common, v21

import transport_data
from transport_data.config import Config
from transport_data.store import UnionStore

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

    import dsss.store

    from transport_data.util.sdmx import MAKeywords

#: List of CKAN UUIDs for objects used for testing.
CKAN_UUID = {
    "DEV org test": "538d7317-fa7b-4890-a945-ae4d30021f38",
    "PROD org test": "8bc58a55-fd85-4667-b23e-a5dba18cdb9a",
}

#: :any:`True` if tests are being run on GitHub Actions.
GITHUB_ACTIONS: bool = "GITHUB_ACTIONS" in os.environ

#: Marks to be reused throughout the test suite. Do not reuse keys in the mapping.
MARK = {
    0: pytest.mark.xfail(
        condition=GITHUB_ACTIONS and platform.system() == "Windows",
        raises=zipfile.BadZipFile,
        reason="'Truncated file header' on GHA runner",
    ),
    "#52": pytest.mark.xfail(
        raises=HTTPError,
        reason="File removed; https://github.com/transport-data/tools/issues/52",
    ),
}


class CliRunner(click.testing.CliRunner):
    def invoke(self, *args, **kwargs):
        import transport_data.cli

        return super().invoke(transport_data.cli.main, *args, **kwargs)


def ember_dfd(store: "dsss.store.Store") -> "v21.Dataflow":
    """Construct a Dataflow used in testing :func:`.read_csv` and related code.

    .. todo:: Instead ensure these artefacts are available from :data:`.STORE`.
    """

    # Construct a DSD corresponding to the data
    ma_kw: "MAKeywords" = dict(
        id="EMBER_001", version="1.0.0", maintainer=common.Agency(id="TDCI")
    )
    dsd = v21.DataStructureDefinition(**ma_kw)
    dsd.dimensions.append(v21.Dimension(id="COUNTRY"))
    dsd.dimensions.append(v21.Dimension(id="YEAR"))
    dsd.measures.append(v21.PrimaryMeasure(id="OBS_VALUE"))
    dsd.attributes.append(common.DataAttribute(id="COMMENT"))

    # Construct a DFD
    dfd = v21.DataflowDefinition(**ma_kw, structure=dsd)

    store.set(dfd)
    store.set(dsd)

    return dfd


@pytest.fixture(scope="session")
def mock_zenodo_api(
    test_data_path: "Traversable",
) -> Iterator["responses.RequestsMock"]:
    """Mock Zenodo API responses to avoid hitting rate limits."""
    from transport_data.util.responses import RepeatRegistry, RequestsMock

    # Use a registry that repeats the same response for a given URL
    mock = RequestsMock(assert_all_requests_are_fired=False, registry=RepeatRegistry)

    # Pass through requests to certain other domains
    mock.add_passthru("https://asiantransportobservatory.org")
    mock.add_passthru("https://doi.org")
    # Pass through requests for actual files
    mock.add_passthru(
        re.compile(r"^https://zenodo\.org/api/records/\d+/files/.*/content$")
    )

    # Mock API responses with record information
    base = "https://zenodo.org/api"
    for doi in "14913730", "15232577":
        with open(str(test_data_path.joinpath(f"zenodo-{doi}.json"))) as f:
            mock.add(method="GET", url=f"{base}/records/{doi}", json=json.load(f))

    yield mock


@pytest.fixture(scope="session")
def sdmx_structures(tmp_store) -> sdmx.message.StructureMessage:
    """SDMX structures for use in tests."""
    sm = sdmx.message.StructureMessage()

    ma_attrib: "MAKeywords" = dict(maintainer=common.Agency(id="TEST"), version="1.0.0")

    cs = common.ConceptScheme(id="TEST", **ma_attrib)  # type: ignore [misc]
    cs.append(common.Concept(id="MASS", name="Mass of fruit"))
    cs.append(common.Concept(id="PICKED", name="Number of fruits picked"))
    cs.append(common.Concept(id="COLOUR", name="Colour of fruit"))
    cs.append(common.Concept(id="FRUIT", name="Type of fruit"))

    cl: "common.Codelist" = common.Codelist(id="COLOUR", **ma_attrib)  # type: ignore [misc]
    cl.extend(
        [common.Code(id=c, name=c.title()) for c in "GREEN ORANGE RED YELLOW".split()]
    )
    cl.append(common.Code(id="_T", name="Total"))
    sm.add(cl)

    cl = common.Codelist(id="FRUIT", **ma_attrib)  # type: ignore [misc]
    cl.extend(
        [common.Code(id=c, name=c.title()) for c in "APPLE BANANA GRAPE LEMON".split()]
    )
    cl.append(common.Code(id="_T", name="Total"))
    sm.add(cl)

    for id_, dims in (
        ("MASS", ("COLOUR", "FRUIT")),
        ("PICKED", ("FRUIT", "COLOUR")),
    ):
        dsd = v21.DataStructureDefinition(id=id_, **ma_attrib)  # type: ignore [misc]
        dsd.urn = sdmx.urn.make(dsd)
        dsd.measures.append(v21.PrimaryMeasure(id=id_, concept_identity=cs[id_]))
        dsd.dimensions.extend(
            common.Dimension(
                id=d,
                concept_identity=cs[d],
                local_representation=common.Representation(enumerated=sm.codelist[d]),
            )
            for d in dims
        )
        sm.add(dsd)

    tmp_store.update_from(sm)

    return sm


@pytest.fixture
def tdc_cli():
    """A :class:`.CliRunner` object that invokes the :program:`tdc` CLI."""
    yield CliRunner()


@pytest.fixture(scope="session")
def test_data_path() -> Iterator["Traversable"]:
    """Path containing test data."""
    from importlib.resources import files

    # TODO When Python 3.11 is the minimum supported, use separate "data", "tests" args
    yield files("transport_data").joinpath("data/tests")


@pytest.fixture(scope="session")
def tmp_config(tmp_path_factory) -> Generator[Config, None, None]:
    """A :class:`.Config` instance pointing to a temporary directory."""
    from platformdirs import user_data_path

    base = tmp_path_factory.mktemp("transport-data")
    result = Config(
        cache_path=base.joinpath("cache"),
        config_path=base.joinpath("config.json"),
        data_path=base.joinpath("data"),
        # Default value in .config.Config.data_path → clone from another local directory
        registry_remote_url=str(user_data_path("transport-data").joinpath("registry")),
    )

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(transport_data, "CONFIG", result)
        yield result


@pytest.fixture(scope="session")
def tmp_store(tmp_config) -> Generator[UnionStore, None, None]:
    """A :class`.UnionStore` in a temporary directory per :func:`.tmp_config`."""
    result = UnionStore(tmp_config)

    # Initialize an empty Git repo
    cast("dsss.store.GitStore", result.store["registry"]).path.mkdir(exist_ok=True)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(transport_data, "STORE", result)
        yield result
