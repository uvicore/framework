"""
NOTES on how to get this working


Connection string has a new 'backend' set to 'sqlalchemy' by default

A connection for uvicore remote API might look like

# Example of ORM over Remote Uvicore API
'iam': {
    'backend': 'api',
    'driver': 'uvicore.orm.drivers.api.Api',
    'url': 'https://iam.example.com/api',
    'prefix': None
},

prefix required because the model will be user, but of backend prefix is auth_, url is auth_user


"""
