import pytest
from ckanapi.errors import CKANAPIError, NotAuthorized, ValidationError
from pytest import param

from transport_data.util.ckan import Client

_500 = pytest.mark.xfail(raises=CKANAPIError, reason="500 Internal Server Error")
_Incomplete = pytest.mark.xfail(
    raises=ValidationError, reason="Incomplete test; needs args"
)
_NotImplemented = pytest.mark.xfail(
    raises=CKANAPIError, reason="Not implemented by .org.ckan.DEV"
)
_NotAuthorized = pytest.mark.xfail(raises=NotAuthorized, reason="Needs API key")


class TestClient:
    @pytest.fixture
    def c(self) -> "Client":
        # FIXME Use the TestCKAN provided by the ckanapi package
        from transport_data.org.ckan import DEV

        return DEV

    # Tests of explicit methods
    def test_package_list(self, c) -> None:
        result = c.package_list()
        assert 1 <= len(result)

    def test_package_show(self, c) -> None:
        packages = c.package_list(limit=1, max=1)
        p = c.package_show(packages[0])
        assert p.id is not None

    def test_tag_list(self, c) -> None:
        result = c.tag_list()
        assert 1 <= len(result)

    # Tests of other HTTP GET API endpoints via call_action
    @pytest.mark.parametrize(
        "action",
        [
            param("am_following_dataset", marks=_Incomplete),
            param("am_following_group", marks=_Incomplete),
            param("am_following_organization", marks=_NotImplemented),
            param("am_following_user", marks=_Incomplete),
            param("api_token_list", marks=_Incomplete),
            param("config_option_list", marks=_NotAuthorized),
            param("config_option_show", marks=_NotAuthorized),
            "current_package_list_with_resources",
            param("dataset_followee_count", marks=_Incomplete),
            param("dataset_followee_list", marks=_NotAuthorized),
            param("dataset_follower_count", marks=_Incomplete),
            param("dataset_follower_list", marks=_NotAuthorized),
            param("followee_count", marks=_Incomplete),
            param("followee_list", marks=_Incomplete),
            param("format_autocomplete", marks=_Incomplete),
            param("get_site_user", marks=_NotAuthorized),
            param("group_autocomplete", marks=_NotImplemented),
            param("group_followee_count", marks=_Incomplete),
            param("group_followee_list", marks=_NotAuthorized),
            param("group_follower_count", marks=_Incomplete),
            param("group_follower_list", marks=_NotAuthorized),
            "group_list_authz",
            "group_list",
            param("group_package_show", marks=_Incomplete),
            param("group_show", marks=_Incomplete),
            param("help_show", marks=_Incomplete),
            param("job_list", marks=_NotAuthorized),
            param("job_show", marks=_NotAuthorized),
            "license_list",
            param("member_list", marks=_Incomplete),
            "member_roles_list",
            param("organization_autocomplete", marks=_500),
            param("organization_followee_count", marks=_Incomplete),
            param("organization_followee_list", marks=_NotAuthorized),
            param("organization_follower_count", marks=_Incomplete),
            param("organization_follower_list", marks=_NotAuthorized),
            "organization_list_for_user",
            "organization_list",
            param("organization_show", marks=_Incomplete),
            param("package_autocomplete", marks=_Incomplete),
            param("package_collaborator_list_for_user", marks=_Incomplete),
            param("package_collaborator_list", marks=_Incomplete),
            param("package_relationships_list", marks=_Incomplete),
            "package_search",
            param("recently_changed_packages_activity_list", marks=_NotImplemented),
            param("resource_search", marks=_Incomplete),
            param("resource_show", marks=_Incomplete),
            param("resource_view_list", marks=_Incomplete),
            param("resource_view_show", marks=_Incomplete),
            "status_show",
            "tag_autocomplete",
            "tag_search",
            param("tag_show", marks=_Incomplete),
            param("task_status_show", marks=_Incomplete),
            param("term_translation_show", marks=_Incomplete),
            param("user_autocomplete", marks=_Incomplete),
            param("user_followee_count", marks=_Incomplete),
            param("user_followee_list", marks=_NotAuthorized),
            param("user_follower_count", marks=_Incomplete),
            param("user_follower_list", marks=_NotAuthorized),
            param("user_list", marks=_NotAuthorized),
            param("user_show", marks=_NotAuthorized),
            "vocabulary_list",
            param("vocabulary_show", marks=_Incomplete),
        ],
    )
    def test_call_action_getattr(self, c, action) -> None:
        result = getattr(c, action)()
        del result
