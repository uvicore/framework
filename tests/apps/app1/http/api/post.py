from typing import List

from app1.models.post import Post
from uvicore.http.routing import ApiRouter

route = ApiRouter()

@route.get('/posts', response_model=List[Post])
async def posts(include: str = ''):
    return await Post.query().include(*include.split(',')).get()


@route.get('/posts/{id}', response_model=Post)
async def post(id: int, include: str = ''):
    return await Post.query().include(*include.split(',')).find(id)
