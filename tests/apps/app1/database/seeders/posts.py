from app1.models.post import Post

async def seed():
    posts = [
        # 2 posts for admin
        Post(slug='test-post1', title='Test Post1', other='other stuff1', creator_id=1),
        Post(slug='test-post2', title='Test Post2', other=None, creator_id=1),

        # 3 posts for manager1
        Post(slug='test-post3', title='Test Post3', other='other stuff2', creator_id=2),
        Post(slug='test-post4', title='Test Post4', other=None, creator_id=2),
        Post(slug='test-post5', title='Test Post4', other=None, creator_id=2),

        # 2 posts for user2
        Post(slug='test-post6', title='Test Post6', other='other stuff3', creator_id=5),
        Post(slug='test-post7', title='Test Post7', other=None, creator_id=5),
    ]
    await Post.insert(posts)


