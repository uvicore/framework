import uvicore
from uvicore.package import Provider


@uvicore.provider()
class Mail(Provider):

    def register(self) -> None:
        pass


    def boot(self) -> None:
        pass
