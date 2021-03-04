import uvicore
from uvicore.http.middleware import Security


@uvicore.service()
class Guard(Security):
    """Uvicore Auth Security Depends"""
    pass

