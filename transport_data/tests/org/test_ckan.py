import pytest
from requests.exceptions import SSLError

from transport_data.org.ckan import (
    DEV,
    PROD,
    STAGING,
    ckan_package_to_mdr,
    mdr_to_ckan_package,
)
from transport_data.util.ckan import Package


@pytest.fixture
def package(test_data_path) -> Package:
    """A :class:`.Package` from a test specimen."""
    return Package.from_file(test_data_path.joinpath("ckan", "package.json"))


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

    assert "dataset" == p.type


def test_ckan_package_to_mdr(package: Package) -> None:
    """:func:`.ckan_package_to_mdr` works as expected."""
    from transport_data.org.metadata import _get

    # Function runs
    mdr = ckan_package_to_mdr(package)

    # Resulting MetadataReport has the expected number of attributes
    assert 48 == len(mdr.metadata)

    # Structured attributes are stored as their string representations
    assert repr(["cars", "private-cars", "truck", "bus"]) == _get(mdr, "modes")
    # Python types are stored as their representations
    assert "False" == _get(mdr, "is_archived")
    assert "True" == _get(mdr, "isopen")
    assert "None" == _get(mdr, "author")


def test_mdr_to_ckan_package(package: Package) -> None:
    """:func:`.mdr_to_ckan_package` works as expected."""

    # Convert to a MetadataReport
    mdr = ckan_package_to_mdr(package)

    # Convert back to a Package instance
    p = mdr_to_ckan_package(mdr)

    if package != p:
        assert package.__dict__ == p.__dict__  # `pytest -vv` shows the rich comparison
