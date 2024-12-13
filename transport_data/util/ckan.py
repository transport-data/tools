"""Utilities for interacting with CKAN instances via their Action API.

The :mod:`ckanapi` package (`PyPI <https://pypi.org/project/ckanapi/>`_,
`GitHub <https://github.com/ckan/ckanapi>`_), maintained by the CKAN organization,
provides Pythonic access to the “CKAN Action API” (
`documentation <https://docs.ckan.org/en/latest/api/index.html>`_), which itself exposes
nearly all of the functionality available through the CKAN web interface and the TDC
front-end.

The :class:`~.ckan.Client` class is a wrapper around the :class:`ckanapi.RemoteCKAN`
class that provides conveniences used by other code in :mod:`transport_data`.
"""

from functools import partialmethod
from importlib.metadata import version
from itertools import count
from typing import TYPE_CHECKING, TypeVar
from warnings import filterwarnings

if TYPE_CHECKING:
    import pathlib

    from ckanapi import RemoteCKAN

# Work around https://github.com/ckan/ckanapi/pull/218 in ckanapi <= 4.8
filterwarnings(
    "ignore", "pkg_resources is deprecated", DeprecationWarning, "ckanapi.version"
)
filterwarnings(
    "ignore", ".*pkg_resources.declare_namespace", DeprecationWarning, "pkg_resources"
)

T = TypeVar("T", bound="ModelProxy")


class ModelProxy:
    """Simple proxy for a CKAN object/model.

    :mod:`ckan` itself is a Python package, but is fairly ‘heavy’—a large package with
    many dependencies. ModelProxy allows to interact with the different classes of
    CKAN objects based on the JSON data returned by the CKAN Action API, without a
    dependency on :class:`ckan` itself.
    """

    name: str | None = None
    id: str | None = None

    _collections: dict[str, str] = dict()

    def __init__(self, data: dict | None = None, **kwargs) -> None:
        self.__dict__.update(data or {})
        self.__dict__.update(kwargs)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.__dict__ == other.__dict__

    def __len__(self) -> int:
        return len(self.__dict__)

    def __repr__(self) -> str:
        return (
            f"<CKAN {type(self).__name__} "
            + (repr(self.name) if self.name else "(no name)")
            + f" with {len(self.__dict__) - 1} fields>"
        )

    @classmethod
    def from_file(cls: type[T], path: "pathlib.Path") -> T:
        """Construct a new instance from a file `path`."""
        import json

        with open(path) as f:
            return cls(json.load(f))

    def asdict(self) -> dict:
        """Return the original dictionary of object data."""
        return self.__dict__.copy()

    def get_item(self, name: str, index: int | None = None):
        """Get a member of a collection."""
        data = self.__dict__[name][index]
        cls = get_class(name)
        assert cls
        return cls(data)

    def update(self, data: dict) -> None:
        """Update part or all of the object data."""
        # Check some items
        if self.name and data.get("name", self.name) != self.name:
            raise ValueError(f"Cannot update with {data['name']!r} != {self.name=!r}")
        elif self.id and data.get("id", self.id) != self.id:
            raise ValueError(f"Cannot update with {data['id']!r} != {self.id=!r}")
        self.__dict__.update(data)


def get_class(name: str) -> type[ModelProxy] | None:
    """Return a :class:`.ModelProxy` subclass given `name`."""
    glb = globals()
    for candidate in (
        name.title(),
        name.rstrip("s").title(),
        {"member_role": "MemberRole"}.get(name.rstrip("s"), ""),
    ):
        try:
            return glb[candidate]
        except KeyError:
            pass
    return None


class Group(ModelProxy):
    """Proxy for `ckan.model.Group
    <https://github.com/ckan/ckan/blob/master/ckan/model/group.py>`_.
    """


class Organization(Group):
    """'Organization' is a synonym for 'Group'."""

    # NB this is a subclass instead of `Organization = Group` so that type(…).__name__
    #    gives 'organization'


class MemberRole(ModelProxy):
    """Proxy for the CKAN 'MemberRole' model.

    .. todo:: Add a link to the proxied class.
    """


class License(ModelProxy):
    """Proxy for `ckan.model.License
    <https://github.com/ckan/ckan/blob/master/ckan/model/license.py>`_.
    """


class Package(ModelProxy):
    """Proxy for `ckan.model.Package
    <https://github.com/ckan/ckan/blob/master/ckan/model/package.py>`_.
    """


class Resource(ModelProxy):
    """Proxy for `ckan.model.Resource
    <https://github.com/ckan/ckan/blob/master/ckan/model/resource.py>`_.
    """


class Tag(ModelProxy):
    """Proxy for the CKAN 'Tag' model.

    The source code for the proxied class is `here
    <>`_.
    """


class Client:
    """Wrapper around :class:`ckanapi.RemoteCKAN`.

    This provides features such as:

    - Iterating over calls with rate limits.
    - Caching results, including combined results from multiple calls.
    - Converting return values to instances of :class:`ModelProxy` subclasses.

    .. todo::
       - Handle API keys via :mod:`transport_data.config`.
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

    def list_action(
        self,
        kind: str,
        limit: int | None = None,
        max: int | None = None,
        **kwargs,
    ) -> list:
        """Call the ``{kind}_list`` API endpoint.

        Parameters
        ----------
        kind
            String identifying the kind of CKAN object to fetch.
        limit
            Number of results to fetch in a single query.
        max
            Maximum number of results to fetch.
        """
        cls = get_class(kind)
        assert cls

        limit = limit or 100

        c = self._cache[f"{kind}_list"] = list()

        data_dict = {"limit": limit}
        data_dict.update(kwargs)

        for i in count():
            data_dict.update(offset=i * limit)
            result = self._api.call_action(f"{kind}_list", data_dict=data_dict)
            c.extend(result)
            if len(result) < limit or (max and max < (i + 1) * limit):
                break
        return [(cls(name=v) if isinstance(v, str) else cls(v)) for v in c]

    # Use list_action() to invoke certain CKAN API endpoints
    group_list = partialmethod(list_action, "group")
    license_list = partialmethod(list_action, "license")
    member_roles_list = partialmethod(list_action, "member_roles")
    organization_list = partialmethod(list_action, "organization")
    package_list = partialmethod(list_action, kind="package")
    tag_list = partialmethod(list_action, kind="tag")

    def show_action(self, obj_or_id: str | dict | T, _cls: type[T], **kwargs) -> T:
        """Call the ``{kind}_show`` API endpoint.

        If `obj_or_id` is an instance of :class:`.ModelProxy`, its
        :attr:`~ModelProxy.name` or :attr:`~.ModelProxy.id` is used for the query, and
        the same instance is updated with the response data and returned. If `obj_or_id`
        is :class:`str` or :class:`dict` a new instance of a :class:`.ModelProxy`
        subclass is returned.

        The return value is cached.
        """
        if isinstance(obj_or_id, dict):
            kw: dict[str, str | None] = obj_or_id
            kw.update(id=kw.pop("name", kw.get("id", "")))
            result: T | None = _cls()
        else:
            kw = dict()

        if isinstance(obj_or_id, str) or obj_or_id is None:
            # Query using the "id" keyword
            kw.update(id=obj_or_id)
            # Create a new result object according to the type of
            result = None
        elif isinstance(obj_or_id, _cls):
            if obj_or_id.id:
                kw.update(id=obj_or_id.id)
            elif obj_or_id.name:
                kw.update(id=obj_or_id.name)
            result = obj_or_id

        kw.update(kwargs)

        kind = _cls.__name__.lower()

        response = self._api.call_action(f"{kind}_show", kw)

        # TODO Handle whatever exception is raised for an invalid `package`
        if result is None:
            result = _cls(response)
        else:
            result.update(response)

        # Update cache by both UUID and name
        self._cache[result.id] = result
        self._cache.setdefault(kind, dict())
        self._cache[kind][result.name] = result

        return result

    # Use show_action() to invoke certain CKAN API endpoints
    # TODO Extend to cover all "*_show" endpoints.
    organization_show = partialmethod(show_action, _cls=Organization)
    package_show = partialmethod(show_action, _cls=Package)
    tag_show = partialmethod(show_action, _cls=Tag)
