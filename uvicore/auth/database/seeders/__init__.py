import uvicore


@uvicore.seeder()
async def seed():
    # Import seeders
    from . import users

    # Run seeders. Order is critical for ForeignKey dependencies
    #await groups.seed()
    await users.seed()
