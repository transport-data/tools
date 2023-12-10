import pytest
from requests.exceptions import ConnectionError, ConnectTimeout

from transport_data.jrc import convert, fetch


@pytest.mark.xfail(
    raises=(
        NotImplementedError,  # Test is incomplete
        # Fetching data occasionally fails
        # TODO Use flaky mark instead
        ConnectionError,
        ConnectTimeout,
    )
)
def test_convert(geo="AT"):
    fetch(geo)
    convert(geo)
