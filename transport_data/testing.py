from pathlib import Path
from typing import TYPE_CHECKING, Generator, cast

import click.testing
import pytest
import sdmx.message
import sdmx.model.v21 as m

import transport_data
from transport_data.config import Config
from transport_data.store import UnionStore

if TYPE_CHECKING:
    import dsss.store


@pytest.fixture(scope="session")
def sdmx_structures(tmp_store) -> sdmx.message.StructureMessage:
    """SDMX structures for use in tests."""
    sm = sdmx.message.StructureMessage()

    ma_attrib = dict(maintainer=m.Agency(id="TEST"), version="1.0.0")

    cs = m.ConceptScheme(id="TEST", **ma_attrib)
    cs.append(m.Concept(id="MASS", name="Mass of fruit"))
    cs.append(m.Concept(id="PICKED", name="Number of fruits picked"))
    cs.append(m.Concept(id="COLOUR", name="Colour of fruit"))
    cs.append(m.Concept(id="FRUIT", name="Type of fruit"))

    cl = m.Codelist(id="COLOUR", **ma_attrib)
    cl.extend([m.Code(id=c, name=c.title()) for c in "GREEN ORANGE RED YELLOW".split()])
    cl.append(m.Code(id="_T", name="Total"))
    sm.add(cl)

    cl = m.Codelist(id="FRUIT", **ma_attrib)
    cl.extend(
        [m.Code(id=c, name=c.title()) for c in "APPLE BANANA GRAPE LEMON".split()]
    )
    cl.append(m.Code(id="_T", name="Total"))
    sm.add(cl)

    for id_, dims in (
        ("MASS", ("COLOUR", "FRUIT")),
        ("PICKED", ("FRUIT", "COLOUR")),
    ):
        dsd = m.DataStructureDefinition(id=id_, **ma_attrib)
        dsd.urn = sdmx.urn.make(dsd)
        dsd.measures.append(m.PrimaryMeasure(id=id_, concept_identity=cs[id_]))
        dsd.dimensions.extend(
            m.Dimension(
                id=d,
                concept_identity=cs[d],
                local_representation=m.Representation(enumerated=sm.codelist[d]),
            )
            for d in dims
        )
        sm.add(dsd)

    tmp_store.update_from(sm)

    return sm


class CliRunner(click.testing.CliRunner):
    def invoke(self, *args, **kwargs):
        import transport_data.cli

        return super().invoke(transport_data.cli.main, *args, **kwargs)


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
