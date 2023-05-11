import pytest

from transport_data.adb import convert


@pytest.mark.parametrize(
    "part",
    (pytest.param("TAS", marks=pytest.mark.xfail(raises=KeyError)),),
)
def test_convert(part):
    convert(part)
