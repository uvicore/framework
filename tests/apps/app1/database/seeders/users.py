from uvicore.auth.models.user import User

async def seed():
    users = [
        User(email='administrator@example.com'),
        User(email='manager1@example.com'),
        User(email='manager2@example.com'),
        User(email='user1@example.com'),
        User(email='user2@example.com'),
    ]
    await User.insert(users)
