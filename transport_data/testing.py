from pathlib import Path
from typing import TYPE_CHECKING, Generator, cast

import click.testing
import pytest
import sdmx.message
from sdmx.model import common, v21

import transport_data
from transport_data.config import Config
from transport_data.store import UnionStore

if TYPE_CHECKING:
    import dsss.store

    from transport_data.util.sdmx import MAKeywords


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
def test_data_path() -> Generator[Path, None, None]:
    """Path containing test data."""
    yield Path(__file__).parent.joinpath("data", "tests")


@pytest.fixture(scope="session")
def tmp_config(tmp_path_factory) -> Generator[Config, None, None]:
    """A :class:`.Config` instance pointing to a temporary directory."""
    from platformdirs import user_data_path

    base = tmp_path_factory.mktemp("transport-data")
    result = Config(
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
