import pytest

from transport_data.oica import convert, get_cl_geo, update_registry


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

    # GEO codelist written with some elements
    assert 0 < len(get_cl_geo())


def test_update_registry():
    update_registry()
