from . import users, posts

async def seed():
    # Order is critical for ForeignKey dependencies
    await users.seed()
    await posts.seed()
