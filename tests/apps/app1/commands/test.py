import uvicore
from uvicore import log
from uvicore.console import command
from uvicore.support.dumper import dump, dd

@command()
async def cli():
    """Play"""

    from app1.models.post import Post
    from app1.models.comment import Comment
    from app1.models.tag import Tag
    from app1.models.user import User


    # All posts
    # SELECT * FROM posts
    #posts = await Post.query().get()



    posts = (await Post.query()
        .include(
            # One
            'creator',
            #'creator.info',
            #'creator.contact',

            'owner',
            #'owner.info',
            #'owner.contact',

            # One-To-Many Comments
            'comments',
            'comments.creator',
            #'comments.creator.info',
            #'comments.creator.contact',

            # Many-To-Many Tags
            'tags',
            #'tags.creator',
            #'tags.creator.info',
            #'tags.creator.contact',
        )
        .get()
    )
    log.nl().header('Posts Model Results')
    #dump(posts)

    # tags
    #     posts
    #         comments
    #           files
    #         files
    #     files
    # ---------------------------
    # posts
    # posts_comments
    # posts_comments_files
    # posts_files
    # files



    # tags = (await Tag.query()
    #     .include(
    #         # One
    #         'creator',
    #         'creator.info',
    #         'creator.contact',

    #         # Many-To-Many Posts
    #         'posts',

    #         # One Stuff on Many Posts
    #         'posts.creator',
    #         'posts.creator.info',
    #         'posts.creator.contact',

    #         # Many Comments on Many Posts
    #         'posts.comments',

    #         # One Stuff on Many Comments on Many Posts
    #         'posts.comments.creator',
    #         'posts.comments.creator.info',
    #         'posts.comments.creator.contact',

    #     )
    #     .get()
    # )
    # log.nl().header('Tag Model Results')
    # dump(tags)



    # comments = (await Comment.query()
    #     .include(
    #         # One
    #         'creator',
    #         'creator.info',
    #         'creator.contact',

    #         'post',
    #         'post.creator',
    #         'post.creator.info',
    #         'post.creator.contact',

    #         #'post.comments',

    #         'post.tags',
    #         'post.tags.creator',
    #     )
    #     #.key_by('title')
    #     .get()
    # )
    # log.nl().header('Comments Model Results')

    # # Test model caching (same class instances)
    # #comments[0].post.creator.email = 'x' * 50
    # #comments[0].post.creator.contact.address = 'y' * 50

    # dump(comments)

    #posts = await Post.query().include('creator.contact', 'comments.creator.info', 'tags.creator.contact', 'tags.creator.info').get()
