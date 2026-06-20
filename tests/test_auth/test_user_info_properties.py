"""
Unit tests for the UserInfo permission helpers and computed properties.

UserInfo is the authenticated-user dataclass returned by authenticators and
injected as request.user. Its can()/can_any()/cant() logic gates authorization
throughout the framework, so it is worth covering directly (no HTTP needed).
"""
import pytest


def make_user(**overrides):
    from uvicore.auth.user_info import UserInfo
    defaults = dict(
        id=5, uuid='u-5', username='jdoe', email='jdoe@example.com',
        first_name='John', last_name='Doe', title=None, avatar=None,
        groups=['Employees'], roles=['Employee'],
        permissions=['posts.read', 'posts.create'],
        superadmin=False, authenticated=True,
    )
    defaults.update(overrides)
    return UserInfo(**defaults)


@pytest.mark.asyncio
async def test_name_and_alias_properties(app1):
    user = make_user()
    assert user.name == 'John Doe'
    assert user.is_authenticated is True
    assert user.loggedin is True
    assert user.is_loggedin is True
    assert user.check is True
    assert user.is_not_authenticated is False


@pytest.mark.asyncio
async def test_admin_aliases_reflect_superadmin(app1):
    normal = make_user(superadmin=False)
    assert normal.admin is False
    assert normal.is_admin is False
    assert normal.is_superadmin is False
    assert normal.is_not_admin is True

    admin = make_user(superadmin=True)
    assert admin.admin is True
    assert admin.is_admin is True
    assert admin.is_superadmin is True
    assert admin.is_not_admin is False


@pytest.mark.asyncio
async def test_can_requires_all_permissions(app1):
    user = make_user(permissions=['posts.read', 'posts.create'])
    assert user.can('posts.read') is True
    assert user.can(['posts.read', 'posts.create']) is True
    # Missing one of the requested permissions -> False (AND semantics)
    assert user.can(['posts.read', 'posts.delete']) is False
    assert user.can('posts.delete') is False


@pytest.mark.asyncio
async def test_can_any_requires_one_permission(app1):
    user = make_user(permissions=['posts.read'])
    assert user.can_any(['posts.delete', 'posts.read']) is True
    assert user.can_any(['posts.delete', 'posts.update']) is False


@pytest.mark.asyncio
async def test_cant_is_inverse_of_can(app1):
    user = make_user(permissions=['posts.read'])
    assert user.cant('posts.delete') is True
    assert user.cannot('posts.delete') is True
    assert user.cant('posts.read') is False


@pytest.mark.asyncio
async def test_superadmin_bypasses_all_permission_checks(app1):
    user = make_user(superadmin=True, permissions=[])
    assert user.can('anything.at.all') is True
    assert user.can(['a', 'b', 'c']) is True
    assert user.can_any(['x']) is True
    assert user.cant('anything') is False
