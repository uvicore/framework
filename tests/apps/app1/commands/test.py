import uvicore
from uvicore import log
from uvicore.console import command
from uvicore.support.dumper import dump, dd

@command()
async def cliX():

    from uvicore.support import str


    print(str.camel('AcmeApp'))
    print(str.camel('acmeApp'))
    print(str.camel('Acme_App'))
    print(str.camel('Acme_app'))
    print(str.camel('acme_App'))
    print(str.camel('Acme-app'))
    print(str.camel('Acme-App'))
    print(str.camel('Acme App'))
    print(str.camel('acme app'))
    print(str.camel('Acme app'))
    print(str.camel('acme App'))

    print(str.camel('AcmeAppTwo'))
    print(str.camel('acmeAppTwo'))
    print(str.camel('Acme_App_Two'))
    print(str.camel('Acme_app_two'))
    print(str.camel('acme_App_Two'))
    print(str.camel('Acme-app-two'))
    print(str.camel('Acme-App-Two'))
    print(str.camel('Acme App Two'))
    print(str.camel('acme app two'))
    print(str.camel('Acme app two'))
    print(str.camel('acme App Two'))


    print(str.camel("Hi don't 12 there! my$ name 'is' matthew reschke, what is your name please???"))


@command()
async def cli():
    """Play"""

    from uvicore.http.middleware import Middleware as x
    dd(x)











    #dd('DONE')



    #import sys

    #from uvicore.auth.database.tables.users import Users
    #from uvicore.auth.models.user import User
    #from app1.models import User, Post

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


    #posts = await Post.query().include('creator.contact', 'attributes').get()
    #posts = await User.query().include('info').get()
    #dump(posts)

    #dump("Hi there, my name is matthew reschke, what is your name?  Again, my name is Matthew Reschke, what is your name?  Again, my name is Matthew Reschke, what is your name? Hi there, my name is matthew reschke, what is your name?  Again, my name is Matthew Reschke, what is your name?  Again, my name is Matthew Reschke, what is your name?")
    #dump(123.32)

    #db = await uvicore.db.database()
    #await db.disconnect()
    #dump(db)


    #dump(uvicore.ioc.bindings)



    #dump(uvicore.ioc.bindings['uvicore.auth.database.tables.users.Users'])
    #dump(uvicore.ioc.bindings)

    #dump(User.modelfields)

    # from uvicore.orm import Field
    # x = Field('id', name='user_id')
    # dump(x)


    #await uvicore.db.disconnect_all()
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


# @cli.resultcallback()
# await def after_command(result, **kwargs):
#     await uvicore.db.disconnect_all()
