import uvicore


@uvicore.seeder()
async def seed():
    # Import seeders
    from . import users, groups, roles

    # Run seeders. Order is critical for ForeignKey dependencies
    await roles.seed()
    await groups.seed()
    await users.seed()
