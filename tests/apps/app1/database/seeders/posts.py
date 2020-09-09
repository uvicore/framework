from app1.models.post import Post

async def seed():
    posts = [
        Post(slug='test-post1', title='Test Post1', other='other stuff', creator_id=1),
        Post(slug='test-post2', title='Test Post2', other=None, creator_id=2),
    ]
    await Post.insert(posts)
