import pytest

from transport_data.util.pycountry import get_database


def test_get_database():
    with pytest.raises(ValueError):
        get_database("1234")
