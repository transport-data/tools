import pytest
from ckanapi.errors import (
    CKANAPIError,
    # NotAuthorized,
    ValidationError,
)
from pytest import param

from transport_data.util.ckan import (
    Client,
    Group,
    Organization,
    Package,
    Resource,
    get_class,
)

_500 = pytest.mark.xfail(raises=CKANAPIError, reason="500 Internal Server Error")
_Incomplete = pytest.mark.xfail(
    raises=ValidationError, reason="Incomplete test; needs args"
)
_NotImplemented = pytest.mark.xfail(
    raises=CKANAPIError, reason="Not implemented by .org.ckan.DEV"
)
# _NotAuthorized = pytest.mark.xfail(raises=NotAuthorized, reason="Needs API key")
_NotAuthorized = pytest.mark.skip(reason="Needs API key")


class TestOrganization:
    @pytest.fixture
    def obj(self, test_data_path) -> Organization:
        p = Package.from_file(test_data_path.joinpath("ckan", "package.json"))
        return Organization(name="test-org", packages=[p, p])

    def test_repr(self, obj: Organization) -> None:
        assert "<CKAN Organization 'test-org'" in repr(obj)
        assert "\n  <CKAN Package '2023-production" in repr(obj)


class TestPackage:
    """These also function as tests of :class:`.ModelProxy`."""

    @pytest.fixture
    def obj(self, test_data_path) -> Package:
        """:class:`.Package` instance from a test specimen file."""
        return Package.from_file(test_data_path.joinpath("ckan", "package.json"))

    def test_asdict(self, obj) -> None:
        obj.asdict()

    def test_get_item(self, obj) -> None:
        g = obj.get_item("groups", 0)
        assert isinstance(g, Group)

        r = obj.get_item("resources", 0)
        assert isinstance(r, Resource)

    def test_init_name_only(self) -> None:
        p = Package(name="foo-bar")
        assert "<CKAN Package 'foo-bar' with 0 fields>" == repr(p)

    def test_len(self, obj) -> None:
        assert 47 == len(obj)

    def test_update(self, obj) -> None:
        with pytest.raises(ValueError):
            obj.update({"id": "foo"})
        with pytest.raises(ValueError):
            obj.update({"name": "foo"})

    def test_repr(self, obj) -> None:
        assert "46 fields" in repr(obj)


class TestClient:
    @pytest.fixture
    def c(self) -> "Client":
        # FIXME Use a mock API
        from transport_data.org.ckan import DEV

        return DEV

    # Tests of explicit methods
    def test_package_list(self, c) -> None:
        result = c.package_list()
        assert 1 <= len(result)

    def test_package_show(self, c) -> None:
        packages = c.package_list(limit=1, max=1)
        p = c.package_show(packages[0])
        assert isinstance(p, Package)
        assert p.id is not None

    # Generic tests of other HTTP GET API endpoints via call_action
    @pytest.mark.parametrize(
        "action, args",
        [
            param("am_following_dataset", {}, marks=_Incomplete),
            param("am_following_group", {}, marks=_Incomplete),
            param("am_following_organization", {}, marks=_NotImplemented),
            param("am_following_user", {}, marks=_Incomplete),
            param("api_token_list", {}, marks=_Incomplete),
            param("config_option_list", {}, marks=_NotAuthorized),
            param("config_option_show", {}, marks=_NotAuthorized),
            ("current_package_list_with_resources", {}),
            param("dataset_followee_count", {}, marks=_Incomplete),
            param("dataset_followee_list", {}, marks=_NotAuthorized),
            param("dataset_follower_count", {}, marks=_Incomplete),
            param("dataset_follower_list", {}, marks=_NotAuthorized),
            param("followee_count", {}, marks=_Incomplete),
            param("followee_list", {}, marks=_Incomplete),
            param("format_autocomplete", {}, marks=_Incomplete),
            param("get_site_user", {}, marks=_NotAuthorized),
            param("group_autocomplete", {}, marks=_NotImplemented),
            param("group_followee_count", {}, marks=_Incomplete),
            param("group_followee_list", {}, marks=_NotAuthorized),
            param("group_follower_count", {}, marks=_Incomplete),
            param("group_follower_list", {}, marks=_NotAuthorized),
            ("group_list_authz", {}),
            ("group_list", {}),
            param("group_package_show", {}, marks=_Incomplete),
            param("group_show", {}, marks=_Incomplete),
            param("help_show", {}, marks=_Incomplete),
            param("job_list", {}, marks=_NotAuthorized),
            param("job_show", {}, marks=_NotAuthorized),
            ("license_list", {}),
            param("member_list", {}, marks=_Incomplete),
            ("member_roles_list", {}),
            param("organization_autocomplete", {}, marks=_500),
            param("organization_followee_count", {}, marks=_Incomplete),
            param("organization_followee_list", {}, marks=_NotAuthorized),
            param("organization_follower_count", {}, marks=_Incomplete),
            param("organization_follower_list", {}, marks=_NotAuthorized),
            ("organization_list_for_user", {}),
            ("organization_list", {}),
            ("organization_show", {"name": "tdci"}),
            param("package_autocomplete", {}, marks=_Incomplete),
            param("package_collaborator_list_for_user", {}, marks=_Incomplete),
            param("package_collaborator_list", {}, marks=_Incomplete),
            param("package_relationships_list", {}, marks=_Incomplete),
            ("package_search", {}),
            ("package_show", {"id": "8decd067-a38a-4834-a70c-40419b17fe9c"}),
            ("package_show", {"name": "2023-production-statistics"}),
            param("recently_changed_packages_activity_list", {}, marks=_NotImplemented),
            param("resource_search", {}, marks=_Incomplete),
            param("resource_show", {}, marks=_Incomplete),
            param("resource_view_list", {}, marks=_Incomplete),
            param("resource_view_show", {}, marks=_Incomplete),
            ("status_show", {}),
            ("tag_autocomplete", {}),
            ("tag_list", {}),
            ("tag_search", {}),
            ("tag_show", {"name": "transport"}),
            param("task_status_show", {}, marks=_Incomplete),
            param("term_translation_show", {}, marks=_Incomplete),
            param("user_autocomplete", {}, marks=_Incomplete),
            param("user_followee_count", {}, marks=_Incomplete),
            param("user_followee_list", {}, marks=_NotAuthorized),
            param("user_follower_count", {}, marks=_Incomplete),
            param("user_follower_list", {}, marks=_NotAuthorized),
            param("user_list", {}, marks=_NotAuthorized),
            param("user_show", {}, marks=_NotAuthorized),
            ("vocabulary_list", {}),
            param("vocabulary_show", {}, marks=_Incomplete),
        ],
    )
    def test_call_action_getattr(self, c, action, args) -> None:
        """Test calling actions accessed as class attributes."""
        method = getattr(c, action)

        result = method(args) if args else method()

        del result

    @pytest.mark.parametrize(
        "arg",
        (
            "tdci",
            "94861715-012e-4467-8353-ab6d1a9c32f9",
            {"name": "tdci"},
            {"id": "94861715-012e-4467-8353-ab6d1a9c32f9"},
            Organization(name="tdci"),
            Organization(id="94861715-012e-4467-8353-ab6d1a9c32f9"),
        ),
    )
    def test_show_action(self, c, arg) -> None:
        result = c.show_action(arg, _cls=Organization)
        del result


def test_get_class() -> None:
    assert None is get_class("foo")
