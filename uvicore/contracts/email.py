from uvicore.typing import Dict, List

class Email(Dict):
    """Email Message Definition"""

    # These class level properties for for type annotations only.
    # They do not restrict of define valid properties like a dataclass would.
    # This is still a fully dynamic SuperDict!
    to: List
    cc: List
    bcc: List
    from_name: str
    from_address: str
    subject: str
    html: str
    text: str
    attachments: List
