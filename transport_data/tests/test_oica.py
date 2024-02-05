import pytest

from transport_data.oica import convert, get_cl_geo, update_registry


@pytest.mark.parametrize(
    "measure, N_obs",
    (
        pytest.param("PROD", None, marks=pytest.mark.xfail(raises=NotImplementedError)),
        ("SALES", dict(SALES=1554, SALES_GR=886)),
        ("STOCK", dict(STOCK=462, STOCK_AAGR=231, STOCK_CAP=77)),
        ("STOCK_AAGR", dict(STOCK=462, STOCK_AAGR=231, STOCK_CAP=77)),
    ),
)
def test_convert(measure, N_obs):
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


def test_update_registry():
    update_registry()
