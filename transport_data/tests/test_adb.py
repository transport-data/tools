import pytest

from transport_data.adb import convert


@pytest.mark.parametrize(
    "part",
    (
        "ACC",
        "APH",
        "CLC",
        "INF",
        "MIS",
        pytest.param("POL", marks=pytest.mark.xfail(reason="File format differs")),
        "RSA",
        "SEC",
        "TAS",
    ),
)
def test_convert(part):
    convert(part)
