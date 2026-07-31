from transport_data.sum4all.structure import get_cs_indicator


def test_get_cs_indicator() -> None:
    cs = get_cs_indicator()

    assert 131 == len(cs)
