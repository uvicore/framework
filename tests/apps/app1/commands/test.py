import uvicore
from uvicore import log
from uvicore.console import command
from uvicore.support.dumper import dump, dd

@command()
async def cli():
    """Play"""

    import sys

    #from uvicore.auth.database.tables.users import Users
    #from uvicore.auth.models.user import User
    from app1.models import User, Post

    #dump(User)


    # from app1.models.user import User as User2


    # print(sys.modules['uvicore.auth.models.user'])

    # #dump(uvicore.app.providers)


    # dump(id(User))
    # dump(User)
    # dump(id(User2))
    # dump(User2)

    # dump(id(sys.modules.get('uvicore.auth.models.user')))
    # dump((sys.modules.get('uvicore.auth.models.user')))

    # dump(id(sys.modules.get('app1.models.user')))
    # dump((sys.modules.get('app1.models.user')))

    # #dump(sys.modules)


    posts = await Post.query().include('creator.contact', 'attributes').get()
    dump(posts)

    #dump(uvicore.ioc.bindings)



    #dump(uvicore.ioc.bindings['uvicore.auth.database.tables.users.Users'])
    #dump(uvicore.ioc.bindings)


    dump('Play Done')

    # from app1.models.post import Post
    # from app1.models.comment import Comment
    # from app1.models.tag import Tag
    # from app1.models.user import User


    # All posts
    # SELECT * FROM posts
    #posts = await Post.query().get()

    # users = await User.query().include([
    #     'posts',
    #     'posts.comments',
    #     'posts.comments.creator'
    # ]).where([
    #     ('posts.comments.creator.email', 'user1@example.com'),
    # ]).get()
    # dump(users)


    # posts = (await Post.query()
    #     .include(
    #         # One
    #         'creator',
    #         #'creator.info',
    #         #'creator.contact',

    #         'owner',
    #         #'owner.info',
    #         #'owner.contact',

    #         # One-To-Many Comments
    #         'comments',
    #         'comments.creator',
    #         #'comments.creator.info',
    #         #'comments.creator.contact',

    #         # Many-To-Many Tags
    #         'tags',
    #         #'tags.creator',
    #         #'tags.creator.info',
    #         #'tags.creator.contact',
    #     )
    #     .order_by('id')
    #     .get()
    # )
    # log.nl().header('Posts Model Results')
    # dump(posts)

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
