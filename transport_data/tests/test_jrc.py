import pytest

from transport_data.jrc import convert


@pytest.mark.xfail(reason="Incomplete test", raises=FileNotFoundError)
def test_convert():
    convert("AT")
