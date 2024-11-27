from dataclasses import dataclass, field
from importlib.metadata import version
from itertools import count
from typing import TYPE_CHECKING, Optional, Union
from warnings import filterwarnings

if TYPE_CHECKING:
    from ckanapi import RemoteCKAN

filterwarnings(
    "ignore", "pkg_resources is deprecated", DeprecationWarning, "ckanapi.version"
)
filterwarnings(
    "ignore", ".*pkg_resources.declare_namespace", DeprecationWarning, "pkg_resources"
)


@dataclass
class Package:
    """Simple proxy for the JSON :attr:`data` about a CKAN 'package'.

    This mirrors, in a much reduced form, `ckan.model.Package
    <https://github.com/ckan/ckan/blob/master/ckan/model/package.py>`_. A separate class
    is used to avoid a dependency on CKAN itself and its heavier dependencies.
    """

    name: str
    id: Optional[str] = None

    data: dict = field(default_factory=dict)

    def update(self, data: dict) -> None:
        # Update the full data
        self.data = data

        # Check and unpack some items
        assert data["name"] == self.name

        assert (self.id or data["id"]) == data["id"]
        self.id = data["id"]


@dataclass
class Resource:
    """Simple proxy for the JSON :attr:`data` about a CKAN 'resource'.

    This mirrors, in a much reduced form, `ckan.model.Resource
    <https://github.com/ckan/ckan/blob/master/ckan/model/resource.py>`_. A separate
    class is used to avoid a dependency on CKAN itself and its heavier dependencies.
    """


class Client:
    """Wrapper around :class:`ckanapi.RemoteCKAN`.

    This provides features such as:

    - Iterating over calls with rate limits.
    - Caching results, including combined results from multiple calls.
    - Converting return values to instances of :class:`Package` and :class:`Resource`.
    """

    _api: "RemoteCKAN"
    _cache: dict

    def __init__(self, address: str) -> None:
        from ckanapi import RemoteCKAN

        # Construct a user-agent string
        user_agent = (
            f"transport_data/{version('transport_data')} "
            "(+https://docs.transport-data.org)"
        )

        self._api = RemoteCKAN(address, user_agent=user_agent)

        self._cache = dict(package=dict())

    def __getattr__(self, name: str):
        return getattr(self._api.action, name)

    def package_list(
        self, limit: Optional[int] = None, max: Optional[int] = None
    ) -> list[Package]:
        """Call the 'package_list' API endpoint.

        Parameters
        ----------
        limit
            Number of results to fetch in a single query.
        max
            Maximum number of results to fetch.
        """
        limit = limit or 100
        c = self._cache["package_list"] = list()
        for i in count():
            result = self._api.call_action(
                "package_list", data_dict={"limit": limit, "offset": i * limit}
            )
            c.extend(result)
            if len(result) < limit or (max and max < (i + 1) * limit):
                break
        return [Package(v) for v in c]

    def tag_list(self):
        """Call the 'tag_list' API endpoint."""
        return self._api.call_action("tag_list")

    def package_show(self, package: Union[str, Package]) -> Package:
        """Call the 'package_show' API endpoint.

        If `package` is an instance of :class:`.Package`, its :attr:`~Package.name` is
        used for the query, and it is updated with the return value. If `package` is
        :class:`str`, a new :class:`.Package` is returned.

        The return value is cached.
        """
        data_dict: dict[str, str] = dict()
        if isinstance(package, str):
            data_dict.update(id=package)
            result = Package(package)
        else:
            data_dict.update(id=package.name)
            result = package

        response = self._api.call_action("package_show", data_dict)

        # TODO Handle whatever exception is raised for an invalid `package`
        result.update(response)

        # Update cache by both UUID and name
        self._cache[result.id] = result
        self._cache["package"][result.name] = result

        return result
