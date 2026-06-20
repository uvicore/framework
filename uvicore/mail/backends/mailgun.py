import os
import uvicore
import aiofiles
from uvicore.typing import Dict, List
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Email


@uvicore.service()
class Mailgun:

    @classmethod
    async def send(cls, message: Email, options: Dict):
        # Get httpx AsyncClient
        http = uvicore.ioc.make('http_client')

        # Get message body as text or html
        body_type = 'text'
        body_content = ''
        if message.html:
            body_type = 'html'
            body_content = message.html
        elif message.text:
            body_type = 'text'
            body_content = message.text

        # Build multipart form fields.  httpx repeats a field once per value in
        # a list, which is what mailgun needs for multiple to/cc/bcc recipients.
        data = {
            'from': message.from_name + '<' + message.from_address + '>',
            'to': list(message.to),
            'cc': list(message.cc),
            'bcc': list(message.bcc),
            'subject': message.subject,
            body_type: body_content,
        }

        # Read attachments as multipart files.  httpx repeats the 'attachment'
        # field once per (filename, content) tuple.
        files = []
        for attachment in message.attachments:
            if os.path.exists(attachment):
                filename = attachment.split('/')[-1]
                async with aiofiles.open(attachment, 'rb') as f:
                    content = await f.read()
                files.append(('attachment', (filename, content)))

        # Post to mailgun using async httpx
        r = await http.post(
            url='https://api.mailgun.net/v3/' + options.domain + '/messages',
            auth=('api', options.secret),
            data=data,
            files=files or None,
        )

        # Success
        if r.status_code == 200:
            return

        # Failure
        raise Exception("Could not send mailgun email - " + r.text)
