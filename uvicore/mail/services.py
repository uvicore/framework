import uvicore
from uvicore.package import ServiceProvider


@uvicore.provider()
class Mail(ServiceProvider):

    def register(self) -> None:
        pass


    def boot(self) -> None:
        pass
