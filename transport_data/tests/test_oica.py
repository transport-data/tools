import pytest

from transport_data.oica import convert, update_registry


@pytest.mark.parametrize(
    "measure",
    (
        pytest.param("PROD", marks=pytest.mark.xfail(raises=NotImplementedError)),
        pytest.param("SALES", marks=pytest.mark.xfail(raises=NotImplementedError)),
        "STOCK",
        "STOCK_AAGR",
    ),
)
def test_convert(measure):
    convert(measure)


def test_update_registry():
    update_registry()
