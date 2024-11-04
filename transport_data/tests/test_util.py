from transport_data.util import list_urns


def test_list_urns():
    assert 9 == len(list_urns())
