import pytest

from transport_data.adb import convert_all


@pytest.mark.xfail(reason="Incomplete test")
def test_convert_all():
    convert_all()
