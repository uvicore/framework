import uvicore
from . import users, posts, contacts, comments, tags, user_info, images, hashtags
@uvicore.seeder()
async def seed():
    # Order is critical for ForeignKey dependencies
    await users.seed()
    await user_info.seed()
    await contacts.seed()

    await hashtags.seed()
    await tags.seed()
    await posts.seed()
    await comments.seed()

    # Poly
    await images.seed()
