# Mail


Sending email


As Mail() parameters
```python
from uvicore.mail import Mail

x = Mail(
    #mailer='smtp',
    #mailer_options={'port': 124},
    to=['to@example.com'],
    cc=['cc@example.com'],
    bcc=['bcc@example.com'],
    from_name='Matthew',
    from_address='from@example.com',
    subject='Hello1',
    html='Hello1 <b>Body</b> Here',
    attachments=[
        '/tmp/test.txt',
        '/tmp/test2.txt',
    ]
)
await x.send()
```

As Mail() method chaining
```python
from uvicore.mail import Mail
x = (Mail()
    #.mailer('mailgun')
    #.mailer_options({'port': 124})
    .to(['to@example.com'])
    .cc(['cc@example.com'])
    .bcc(['bcc@example.com'])
    .from_name('Matthew')
    .from_address('from@example.com')
    .subject('Hello1')
    .text('Hello1 <b>Body</b> Here')
    .attachments([
        '/tmp/test.txt',
        '/tmp/test2.txt',
    ])
)
await x.send()
```


FIXME.  Add docs on route background tasks.  How to send email using starlette background on a route.
