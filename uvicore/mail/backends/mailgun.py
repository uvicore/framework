import os
import uvicore
import aiohttp
import aiofiles
from uvicore.typing import Dict, List
from uvicore.support.dumper import dump, dd
from uvicore.contracts import Email
from aiohttp import BasicAuth


@uvicore.service()
class Mailgun:

    @classmethod
    async def send(cls, message: Email, options: Dict):
        # Get aiohttp ClientSession
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

        # New multi-part form data (because mailgun can accept both email fields and attachment data)
        data = aiohttp.FormData()

        # Add from name and address
        data.add_field('from', message.from_name + '<' + message.from_address + '>')

        # Add to recipients
        for to in message.to:
            data.add_field('to', to)

        # Add cc recipients
        for cc in message.cc:
            data.add_field('cc', cc)

        # Add bcc recipients
        for bcc in message.bcc:
            data.add_field('bcc', bcc)

        # Add subject
        data.add_field('subject', message.subject)

        # Add body (as html or text)
        data.add_field(body_type, body_content)

        # Add attachments
        for attachment in message.attachments:
            if os.path.exists(attachment):
                filename = attachment.split('/')[-1]
                data.add_field('attachment', await aiofiles.open(attachment, 'rb'), filename=filename)

        # Post to mailgun using async aiohttp
        async with http.post(
            url='https://api.mailgun.net/v3/' + options.domain + '/messages',
            auth=BasicAuth('api', options.secret),
            data=data,
        ) as r:
            # Success
            detail = await r.text()
            if r.status == 200:
                return

            # Failure
            raise Exception("Could not send mailgun email - " + detail)
