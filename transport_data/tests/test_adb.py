import pytest

from transport_data.adb import convert


@pytest.mark.parametrize(
    "part",
    (
        pytest.param("ACC", marks=pytest.mark.xfail(reason="Incomplete")),
        "APH",
        "CLC",
        "INF",
        pytest.param("MIS", marks=pytest.mark.xfail(reason="Incomplete")),
        pytest.param("POL", marks=pytest.mark.xfail(reason="Incomplete")),
        pytest.param("RSA", marks=pytest.mark.xfail(reason="Incomplete")),
        pytest.param("SEC", marks=pytest.mark.xfail(reason="Incomplete")),
        "TAS",
    ),
)
def test_convert(part):
    convert(part)
