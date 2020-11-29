from .provider import ServiceProvider

# No, not used by public
#from .package import Package



from uvicore.package.package import Package as _Package
class Package(_Package):
    pass
