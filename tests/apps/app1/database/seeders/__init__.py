import uvicore


@uvicore.seeder()
async def seed():
    # Import seeders
    from . import (comments, contacts, groups, hashtags, images, posts, tags,
                   user_info, users, roles, warehouses, depots)

    # Order is critical for ForeignKey dependencies
    await roles.seed()
    await groups.seed()
    await users.seed()
    await user_info.seed()
    await contacts.seed()

    await hashtags.seed()
    await tags.seed()
    await posts.seed()
    await comments.seed()

    # Poly
    await images.seed()

    # Natural-key (non-pk local_key) relations
    await warehouses.seed()

    # Composite (multi-column) natural-key relations
    await depots.seed()
