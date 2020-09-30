from . import users, groups

async def seed():
    # Order is critical for ForeignKey dependencies
    #await groups.seed()
    await users.seed()
