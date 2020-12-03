import pytest
import uvicore
from typing import List
from uvicore.support.dumper import dump


@pytest.mark.asyncio
async def test_package(app1):
    from uvicore.package.package import Package
    assert Package.__module__ + '.' + Package.__name__ == 'app1.overrides.package.Package'
    assert Package.__annotations__.get('custom1') is not None

    # Should be able to pull the original via _BASE
    original = uvicore.ioc.make('uvicore.package.package.Package_BASE')
    assert original.__module__ + '.' + original.__name__ == 'uvicore.package.package.Package'


@pytest.mark.asyncio
async def test_provider(app1):
    from uvicore.package.provider import ServiceProvider
    assert ServiceProvider.__module__ + '.' + ServiceProvider.__name__ == 'app1.overrides.provider.ServiceProvider'
    assert ServiceProvider.__annotations__.get('custom1') is not None

    # Should be able to pull the original via _BASE
    original = uvicore.ioc.make('uvicore.package.provider.ServiceProvider_BASE')
    assert original.__module__ + '.' + original.__name__ == 'uvicore.package.provider.ServiceProvider'


@pytest.mark.asyncio
async def test_application(app1):
    package = uvicore.app.package('uvicore.configuration')
    assert hasattr(package, 'custom1')

    # Should be able to pull the original via _BASE
    original = uvicore.ioc.make('uvicore.foundation.application._Application_BASE')
    assert original.__module__ + '.' + original.__name__ == 'uvicore.foundation.application._Application'


@pytest.mark.asyncio
async def test_user_model(app1):
    # Should return the same class (not an instance, not a singleton)
    from uvicore.auth.models.user import User
    from app1.models.user import User as Override
    assert User == Override

    # Should be able to pull the original via _BASE
    original = uvicore.ioc.make('uvicore.auth.models.user.User_BASE')
    assert original.__module__ + '.' + original.__name__ == 'uvicore.auth.models.user.User'


@pytest.mark.asyncio
async def test_users_table(app1):
    # These are singletons and should match the same single instance
    from uvicore.auth.database.tables.users import Users
    from app1.database.tables.users import Users as Override
    assert Users == Override

    # Should be able to pull the original via _BASE
    original = uvicore.ioc.make('uvicore.auth.database.tables.users.Users_BASE')
    assert original.__module__ + '.' + original.__name__ == 'uvicore.auth.database.tables.users.Users'
