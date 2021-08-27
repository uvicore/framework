import pytest
from uvicore.support import module
from uvicore.support.dumper import dump


def test_location():
    # Find folder of package
    x = module.location('uvicore.container')
    assert 'uvicore/container' in x

    # Find folder of namespace package
    x = module.location('uvicore.foundation')
    assert 'uvicore/foundation' in x

    # Find folder of module (file)
    x = module.location('uvicore.foundation.config.package')
    assert 'uvicore/foundation/config' in x

    # Find folder of method/class
    x = module.location('uvicore.foundation.config.package.config')
    assert 'uvicore/foundation/config' in x


def test_load_root():
    # Import root level package (has __init__.py)
    # Module(
    #     object=<module 'uvicore' from '/home/mreschke/Code/mreschke/python/uvicore/uvicore/uvicore/__init__.py'>,
    #     name='uvicore',
    #     path='uvicore',
    #     fullpath='uvicore',
    #     package='uvicore',
    #     file='/home/mreschke/Code/mreschke/python/uvicore/uvicore/uvicore/__init__.py')
    x = module.load('uvicore')
    assert "<module 'uvicore' from " in str(x.object)
    assert x.name == 'uvicore'
    assert x.path == 'uvicore'
    assert x.fullpath == 'uvicore'
    assert x.package == 'uvicore'
    assert 'uvicore/__init__.py' in x.file


def test_load_package():
    # Import non root level package (has __init__.py)
    # Module(
    #     object=<module 'uvicore.container' from '/home/mreschke/Code/mreschke/python/uvicore/uvicore/uvicore/container/__init__.py'>,
    #     name='container',
    #     path='uvicore',
    #     fullpath='uvicore.container',
    #     package='uvicore.container',
    #     file='/home/mreschke/Code/mreschke/python/uvicore/uvicore/uvicore/container/__init__.py')
    x = module.load('uvicore.configuration')
    assert "<module 'uvicore.configuration' from " in str(x.object)
    assert x.name == 'configuration'
    assert x.path == 'uvicore'
    assert x.fullpath == 'uvicore.configuration'
    assert x.package == 'uvicore.configuration'
    assert 'uvicore/configuration/__init__.py' in x.file


def test_load_namespace():
    # Import namespace package (no __init__.py)
    # Module(
    #     object=<module 'uvicore.foundation' (namespace)>,
    #     name='foundation',
    #     path='uvicore',
    #     fullpath='uvicore.foundation',
    #     package='uvicore.foundation',
    #     file='/home/mreschke/Code/mreschke/python/uvicore/uvicore/uvicore/foundation')
    x = module.load('uvicore.foundation')
    assert str(x.object) == "<module 'uvicore.foundation' (namespace)>"
    assert x.name == 'foundation'
    assert x.path == 'uvicore'
    assert x.fullpath == 'uvicore.foundation'
    assert x.package == 'uvicore.foundation'
    assert 'uvicore/foundation' in x.file


def test_load_file():
    # Import actual module (file) but not a method inside it
    # Module(
    #     object=<module 'uvicore.foundation.config.package' from '/home/mreschke/Code/mreschke/python/uvicore/uvicore/uvicore/foundation/config/package.py'>,
    #     name='package',
    #     path='uvicore.foundation.config',
    #     fullpath='uvicore.foundation.config.package',
    #     package='uvicore.foundation.config',
    #     file='/home/mreschke/Code/mreschke/python/uvicore/uvicore/uvicore/foundation/config/package.py')
    x = module.load('uvicore.foundation.config.package')
    assert "<module 'uvicore.foundation.config.package' from " in str(x.object)
    assert x.name == 'package'
    assert x.path == 'uvicore.foundation.config'
    assert x.fullpath == 'uvicore.foundation.config.package'
    assert x.package == 'uvicore.foundation.config'
    assert 'uvicore/foundation/config/package.py' in x.file


def test_load_object():
    # Import class from inside a file
    # uvicore.support.module.Module(
    #     object=uvicore.container.ioc._Ioc,  # class
    #     name='_Ioc',
    #     path='uvicore.container.ioc',
    #     fullpath='uvicore.container.ioc._Ioc',
    #     package='uvicore.container',
    #     file='/home/mreschke/Code/mreschke/python/uvicore/uvicore/uvicore/'
    #         'container/ioc.py'
    # )
    x = module.load('uvicore.container.ioc.Ioc')
    assert "<class 'uvicore.container.ioc.Ioc'>" in str(x.object)
    assert x.name == 'Ioc'
    assert x.path == 'uvicore.container.ioc'
    assert x.fullpath == 'uvicore.container.ioc.Ioc'
    assert x.package == 'uvicore.container'
    assert 'uvicore/container/ioc.py' in x.file


def test_load_invalid():
    # Import invalid module
    with pytest.raises(ModuleNotFoundError):
        module.load('uvicorex')


def test_load_invalid_attribute():
    # Import invalid attribute
    with pytest.raises(Exception):
        module.load('uvicore.nothing')


def test_load_wildcard():
    # Import wildcard
    module.load('uvicore.foundation.config.*')
