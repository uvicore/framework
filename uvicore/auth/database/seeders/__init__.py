import uvicore


@uvicore.seeder()
async def seed():
    # Import seeders
    from . import users, groups, roles, permissions

    # Run seeders. Order is critical for ForeignKey dependencies
    await permissions.seed()
    await roles.seed()
    await groups.seed()
    await users.seed()
