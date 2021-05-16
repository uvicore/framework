import uvicore
from uvicore.support import module
from uvicore.typing import Dict, List
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Email


@uvicore.service()
class Mail:

    def __init__(self, *,
        mailer: str = None,
        mailer_options: Dict = None,
        to: List = [],
        cc: List = [],
        bcc: List = [],
        from_name: str = None,
        from_address: str = None,
        subject: str = None,
        html: str = None,
        text: str = None,
        attachments: List = [],
    ) -> None:
        # Get mailer and options from config
        self._config = uvicore.config.app.mail.clone()
        self._mailer = mailer or self._config.default
        self._mailer_options = self._config.mailers[self._mailer].clone().merge(mailer_options)

        # New message superdict
        self._message: Email = Email()
        self._message.to = to
        self._message.cc = cc
        self._message.bcc = bcc
        self._message.from_name = from_name or self._config.from_name
        self._message.from_address = from_address or self._config.from_address
        self._message.subject = subject
        self._message.html = html
        self._message.text = text
        self._message.attachments = attachments

    def mailer(self, mailer: str):
        self._mailer = mailer
        self._mailer_options = self._config.mailers[self._mailer].clone()
        return self

    def mailer_options(self, options: Dict):
        self._mailer_options.merge(Dict(options))
        return self

    def to(self, to: List):
        self._message.to = to
        return self

    def cc(self, cc: List):
        self._message.cc = cc
        return self

    def bcc(self, bcc: List):
        self._message.bcc = bcc
        return self

    def from_name(self, from_name: str):
        self._message.from_name = from_name
        return self

    def from_address(self, from_address: str):
        self._message.from_address = from_address
        return self

    def subject(self, subject: str):
        self._message.subject = subject
        return self

    def html(self, html: str):
        self._message.html = html
        return self

    def text(self, text: str):
        self._message.text = text
        return self

    def attachments(self, attachments: List):
        self._message.attachments = attachments
        return self

    async def send(self):
        # Use dynamic module based on mailer driver
        driver = module.load(self._mailer_options.driver).object
        await driver.send(self._message, self._mailer_options)
