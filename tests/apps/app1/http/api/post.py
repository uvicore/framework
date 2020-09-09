from typing import List

#from app1.models.post import Post
from uvicore.http.routing import ApiRouter

route = ApiRouter()

#@route.get('/users', response_model=List[User], include_in_schema=False)
#@route.get('/posts', response_model=List[Post])
@route.get('/posts')
async def posts():
    return [
        {
            "id": 1,
            "name": "Matthew"
        },
        {
            "id": 2,
            "name": "Taylor"
        },
    ]
