from uvicore.configuration import env
from uvicore.typing import OrderedDict


# --------------------------------------------------------------------------
# Mail Configuration
#
# Uvicore allows for multiple email stores (backends) like mailgun and smtp.
# Use 'default' to set the default backend.
# --------------------------------------------------------------------------
mail = {
    'default': env('MAIL_DRIVER', 'mailgun'),
    'mailers': {
        'mailgun': {
            'driver': 'uvicore.mail.backends.Mailgun',
            'domain': env('MAIL_MAILGUN_DOMAIN', ''),
            'secret': env('MAIL_MAILGUN_SECRET', ''),
        },
        'smtp': {
            'driver': 'uvicore.mail.backends.smtp',
            'server': env('MAIL_SMTP_SERVER', ''),
            'port': env.int('MAIL_SMTP_PORT', 587),
            'username': env('MAIL_SMTP_USERNAME', ''),
            'password': env('MAIL_SMTP_PASSWORD', ''),
            'ssl': env.bool('MAIL_SMTP_SSL', False),
        }
    },
    'from_name': env('MAIL_FROM_NAME', 'App1'),
    'from_address': env('MAIL_FROM_ADDRESS', 'app1@example.com'),
}
