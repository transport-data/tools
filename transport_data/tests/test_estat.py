import pytest

from transport_data.estat import get, list_flows


def test_list_flows():
    list_flows()


@pytest.mark.parametrize("df_id", list_flows())
def test_get(df_id):
    get(df_id)
