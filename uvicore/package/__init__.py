# type: ignore
from .provider import Provider
#from uvicore.package.package import Package as _Package

# Proxy instead of import to create a nicer uvicore.package.Package namespace
# Even if you override this the acutal class, all listings will still show this consistent namespace
# NO - Not sure I like proxy as it creates 2 classes on 2 different paths which can cause issues in type()
# class Package(_Package):
#     pass

from .package import Package
