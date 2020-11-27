import uvicore
from . import users

@uvicore.seeder()
async def seed():
    # Order is critical for ForeignKey dependencies
    #await groups.seed()
    await users.seed()
