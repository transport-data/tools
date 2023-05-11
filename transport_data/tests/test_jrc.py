import pytest

from transport_data.jrc import read


@pytest.mark.xfail(reason="Incomplete test", raises=FileNotFoundError)
def test_read():
    read()
