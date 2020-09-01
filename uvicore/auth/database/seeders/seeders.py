from . import users

def seed():
    # Order is critical for ForeignKey dependencies
    users.seed()
