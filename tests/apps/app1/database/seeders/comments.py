from app1.models.comment import Comment
from app1.models.post import Post
from uvicore.support.dumper import dump, dd

async def seed():

    # You can use the parent with child relations for creating
    # Have to use Dict notation.  If you use Model pydantic class, post_id is required which defeats the purpose of auto ID linkage
    post = await Post.query().find(1)
    await post.create('comments', [
        {
            'title': 'Post1 Comment2',
            'body': 'Body for post1 comment2',
            #'post_id': 1,  # No id needed, thats what post.create() does
            'creator_id': 2,
        },
    ])

    # You can use .insert() as a List of model instances
    await Comment.insert([
        # Post 1 has 2 comments
        #NO-Comment(title='Post1 Comment1', body='Body for post1 comment1', post_id=1),
        #Comment(title='Post1 Comment2', body='Body for post1 comment2', post_id=1),

        # Post 2 has 3
        Comment(title='Post3 Comment1', body='Body for post3 comment1', post_id=3, creator_id=3),
        Comment(title='Post3 Comment2', body='Body for post3 comment2', post_id=3, creator_id=4),
        #NO-Comment(title='Post3 Comment3', body='Body for post3 comment3', post_id=3),
    ])

    # You can also user .insert() as a list of Dict
    await Comment.insert([
        {
            'title': 'Post3 Comment3',
            'body': 'Body for post3 comment3',
            'post_id': 3,
            'creator_id': 1,
        }
    ])
