from uvicore.auth.models.user_info import UserInfo

async def seed():

    # You can use .insert() as a List of model instances
    await UserInfo.insert([
        UserInfo(extra1='extra here', user_id=1)
    ])
