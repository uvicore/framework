from app1.models.comment import Comment

async def seed():
    comments = [
        # Post 1 has 2 comments
        Comment(title='Post1 Comment1', body='Body for post1 comment1', post_id=1),
        Comment(title='Post1 Comment2', body='Body for post1 comment2', post_id=1),

        # Post 2 has 3
        Comment(title='Post3 Comment1', body='Body for post3 comment1', post_id=3),
        Comment(title='Post3 Comment2', body='Body for post3 comment2', post_id=3),
        Comment(title='Post3 Comment3', body='Body for post3 comment3', post_id=3),
    ]
    await Comment.insert(comments)


