import pytest

from transport_data.jrc import convert


@pytest.mark.xfail(raises=NotImplementedError)
def test_convert():
    convert("AT")
