import pytest
from pytest import param

from transport_data.oica import convert, get_cl_geo, update_registry
from transport_data.testing import MARK


@pytest.mark.parametrize(
    "measure, N_obs",
    (
        param("PROD", None, marks=pytest.mark.xfail(raises=NotImplementedError)),
        param("SALES", dict(SALES=1332, SALES_GR=444)),
        param(
            "STOCK", dict(STOCK=462, STOCK_AAGR=230, STOCK_CAP=77), marks=MARK["#52"]
        ),
        param(
            "STOCK_AAGR",
            dict(STOCK=462, STOCK_AAGR=230, STOCK_CAP=77),
            marks=MARK["#52"],
        ),
    ),
)
def test_convert(measure: str, N_obs: dict[str, int]) -> None:
    result = convert(measure)

    # GEO codelist written with some elements
    assert 0 < len(get_cl_geo())

    # Results contain the expected number of data sets
    assert len(N_obs) == len(result)

    # Each data set contains the expected number of observations
    observed = {dfd_id.split("DF_OICA_")[-1]: len(ds) for dfd_id, ds in result.items()}
    assert N_obs == observed

    # DEBUG
    # import sdmx
    #
    # for _, ds in result.items():
    #     print(sdmx.to_pandas(ds).to_string())


def test_update_registry() -> None:
    update_registry()
