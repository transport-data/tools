import pytest
from requests.exceptions import SSLError

from transport_data.org.ckan import DEV, PROD, STAGING


@pytest.mark.parametrize(
    "instance, N_exp",
    [
        # (DEV, 451),
        (DEV, 5),
        # (PROD, 418),
        (PROD, 5),
        pytest.param(STAGING, None, marks=pytest.mark.xfail(raises=SSLError)),
    ],
)
def test_main(instance, N_exp: int) -> None:
    result = instance.package_list(max=5)

    assert N_exp <= len(result)

    p = instance.package_show(result[0])

    assert p is result[0]  # Same object instance returned

    assert "dataset" == p.data["type"]
