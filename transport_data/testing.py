import pytest
import sdmx.message
import sdmx.model.v21 as m


@pytest.fixture(scope="session")
def sdmx_structures() -> sdmx.message.StructureMessage:
    """SDMX structures for use in tests."""
    sm = sdmx.message.StructureMessage()

    a = m.Agency(id="TEST")

    cs = m.ConceptScheme(id="TEST")
    cs.append(m.Concept(id="MASS", name="Mass of fruit"))
    cs.append(m.Concept(id="PICKED", name="Number of fruits picked"))
    cs.append(m.Concept(id="COLOUR", name="Colour of fruit"))
    cs.append(m.Concept(id="FRUIT", name="Type of fruit"))

    cl = m.Codelist(id="COLOUR")
    cl.extend([m.Code(id=c, name=c.title()) for c in "GREEN ORANGE RED YELLOW".split()])
    cl.append(m.Code(id="_T", name="Total"))
    sm.add(cl)

    cl = m.Codelist(id="FRUIT")
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

    return sm
