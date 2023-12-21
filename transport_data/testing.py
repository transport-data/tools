from typing import cast

import pytest
import sdmx.message
import sdmx.model.v21 as m

from transport_data.config import Config
from transport_data.store import Registry, UnionStore


@pytest.fixture(scope="session")
def sdmx_structures(tmp_store) -> sdmx.message.StructureMessage:
    """SDMX structures for use in tests."""
    sm = sdmx.message.StructureMessage()

    a = m.Agency(id="TEST")

    cs = m.ConceptScheme(id="TEST", maintainer=a)
    cs.append(m.Concept(id="MASS", name="Mass of fruit"))
    cs.append(m.Concept(id="PICKED", name="Number of fruits picked"))
    cs.append(m.Concept(id="COLOUR", name="Colour of fruit"))
    cs.append(m.Concept(id="FRUIT", name="Type of fruit"))

    cl = m.Codelist(id="COLOUR", maintainer=a)
    cl.extend([m.Code(id=c, name=c.title()) for c in "GREEN ORANGE RED YELLOW".split()])
    cl.append(m.Code(id="_T", name="Total"))
    sm.add(cl)

    cl = m.Codelist(id="FRUIT", maintainer=a)
    cl.extend(
        [m.Code(id=c, name=c.title()) for c in "APPLE BANANA GRAPE LEMON".split()]
    )
    cl.append(m.Code(id="_T", name="Total"))
    sm.add(cl)

    for id_, dims in (
        ("MASS", ("COLOUR", "FRUIT")),
        ("PICKED", ("FRUIT", "COLOUR")),
    ):
        dsd = m.DataStructureDefinition(id=id_, maintainer=a, version="1.0")
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

    tmp_store.write(sm)

    return sm


@pytest.fixture(scope="session")
def tmp_config(tmp_path_factory) -> Config:
    """A :class:`.Config` instance pointing to a temporary directory."""
    base = tmp_path_factory.mktemp("transport-data")
    return Config(
        config_path=base.joinpath("config.json"),
        data_path=base.joinpath("data"),
    )


@pytest.fixture(scope="session")
def tmp_store(tmp_config) -> UnionStore:
    """A :class`.UnionStore` in a temporary directory per :func:`.tmp_config`."""
    us = UnionStore(tmp_config)
    r = cast(Registry, us.store["registry"])
    r.path.mkdir(exist_ok=True)
    r._git("init")

    return us
