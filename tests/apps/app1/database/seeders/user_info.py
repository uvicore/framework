import uvicore
from uvicore import log
from app1.models.user_info import UserInfo

@uvicore.seeder()
async def seed():
    log.item('Seeding table user_info')

    # You can use .insert() as a List of model instances
    await UserInfo.insert([
        UserInfo(extra1='user1 extra', user_id=1),
        UserInfo(extra1='user2 extra', user_id=2),
        UserInfo(extra1='user3 extra', user_id=3),
        UserInfo(extra1='user4 extra', user_id=4),
        #UserInfo(extra1='user5 extra', user_id=5),
    ])
