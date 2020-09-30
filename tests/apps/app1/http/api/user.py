from typing import List

#from uvicore.auth.models.user import User
from app1.models.user import User
from uvicore.auth.models.user_info import UserInfo
from uvicore.http.routing import ApiRouter

route = ApiRouter()

@route.get('/users', response_model=List[User])
async def users(include: str = ''):
    return await User.query().include('info').get()



@route.get('/user-info', response_model=List[UserInfo])
async def user_info(include: str = ''):
    return await UserInfo.query().include('user').get()
