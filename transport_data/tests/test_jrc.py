import pytest

from transport_data.jrc import convert, fetch


@pytest.mark.xfail(raises=NotImplementedError)
def test_convert(geo="AT"):
    fetch(geo)
    convert(geo)
