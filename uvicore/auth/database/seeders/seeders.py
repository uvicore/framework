from . import users

async def seed():
    # Order is critical for ForeignKey dependencies
    #await groups.seed()
    await users.seed()
