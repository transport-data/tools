from transport_data.org import get_agencyscheme, refresh


def test_get_agencyscheme() -> None:
    as_ = get_agencyscheme()

    # Number of agencies associated with code in the transport_data repo
    assert 10 == len(as_)


def test_refresh() -> None:
    refresh()
