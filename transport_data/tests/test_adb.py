import pytest

from transport_data.adb import convert


@pytest.mark.parametrize("part", ["TAS"])
def test_convert(part):
    convert(part)
