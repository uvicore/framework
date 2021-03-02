from typing import List

from app1 import models
from uvicore.auth import models as auth_models
from uvicore.http.routing import ApiRouter

route = ApiRouter()


@route.post('/hastags2')
def post(entity):
    return {'hi': 'there'}



# @route.get('/auth_groups', response_model=List[auth_models.Group])
# async def auth_groups():
#     return await auth_models.Group.query().get()


# @route.get('/auth_user_info', response_model=List[auth_models.UserInfo])
# async def auth_user_info():
#     return await auth_models.UserInfo.query().get()

# @route.get('/auth_users', response_model=List[auth_models.User])
# async def auth_users():
#     return await auth_models.User.query().get()

# There were two of these, probably why it errored
# @route.get('/auth_users', response_model=List[auth_models.User])
# async def auth_users():
#     return await auth_models.User.query().get()


# @route.get('/posts', response_model=List[Post])
# async def posts(include: str = ''):
#     return await Post.query().include(*include.split(',')).get()


# @route.get('/posts/{id}', response_model=Post)
# async def post(id: int, include: str = ''):
#     return await Post.query().include(*include.split(',')).find(id)
