from . import users, posts, contacts, comments

async def seed():
    # Order is critical for ForeignKey dependencies
    await users.seed()
    await contacts.seed()

    await posts.seed()
    await comments.seed()
