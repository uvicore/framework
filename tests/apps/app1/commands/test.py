import uvicore
from uvicore import log
from uvicore.console import command
from uvicore.support.dumper import dump, dd

@command()
async def cli():
    """Play"""

    from app1 import models




    user = await models.User.query().include(
        'groups.roles.permissions',
        #'roles',
        'roles.permissions',
        'posts.creator.info',
        'posts.creator.creator.info',
        #'creator.info',
    ).find(2)
    dd(user)









    dd('doneo play')




    # Redis
    # from uvicore.redis import Redis

    # redis = await Redis.connect()
    # cache = await Redis.connect('cache')

    # dump(await redis.get('name'))
    # dump(await cache.get('name'))

    # dump(await redis.keys('*'))



    # Cache
    #from uvicore.cache import Cache

    cache = uvicore.cache
    #cache = uvicore.cache.connect('app1')
    #cache = Cache.connect('app1')

    #dump( await Cache.connect('app1').get('name') )


    await cache.put('k0', 'k0 value')
    await cache.put({
        'k1': 'k1 value',
        'k2': 'k2 value',
    })

    dump( await cache.get('k0') )
    x = await cache.get(['k1', 'k2'])
    dump(x)
    #dump(x.k1)

    #dump( await cache.pull('k0'))
    #x = await cache.pull(['k1', 'k2'])
    #dump(x)


    #dump( await cache.get('name') )
    #dump( await cache.store('redis').get('name') )
    #dump( await cache.store('app1').get('name') )
    #dump( await cache.get('name2') )
    #dump( await cache.store('redis').get('name') )
    #dump( await cache.get('name') )
    #dump( await cache.store('redis2').get('name') )
    #dump( await cache.store('redis').get('name') )


    #await cache.increment('inc1')
    #dump( await cache.get('inc1') )

    #await cache.put('one', 'one here')
    #dump( await cache.get('one') )


    #await cache.put('two', 'two here', 5)
    #dump( await cache.has('two') )

    async def method0():
        #return 'method0 here'
        dump('query here')
        return await models.Post.query().find(1)

    async def method1():
        return 'method1 here'

    async def method2():
        return {
            'asdf': 'asdfasdf',
            'xafd': 'casdfasdf',
        }

    # await cache.remember('method0', method0, seconds=5)
    # await cache.remember({
    #     'method1': method1,
    #     'method2': method2,
    # }, seconds=5)
    # #dump( await cache.get('method1') )

    # dump( await cache.get(['method0', 'method1', 'method2']) )

    #post = await uvicore.db.query().table('posts').cache(seconds=5).find(unique_slug='test-post3')
    #dump(post)


    #post = await models.Post.query().include().cache(seconds=10).find(1)
    #dump(post)

    user = await models.User.query().include('contact', 'info', 'groups', 'groups.roles', 'groups.roles.permissions').cache(seconds=10).find(2)
    dd(user)

    #await cache.forget(['k0', 'k1', 'k2'])
    #await cache.flush()


    #( await cache.add('add1', 'add1 here') )
    #dump( await cache.has('add1') )
    #x = await cache.pull('add1')
    #dump(x)
    #dump( await cache.has('add1') )


    #await cache.put({
        #'k1': 'value of k1',
        #'k2': 'value of k2',
    #})
    #dump( await cache.get('k1') )
    #dump( await cache.get('k2') )

    #x = await cache.get(['k1', 'k2'])
    #dump(x)
    #dump(x.k1)





    #from uvicore.cache.cache import Cache
    #cache = uvicore.ioc.make('cache')

    #dump(uvicore.ioc.binding('uvicore.cache.cache.Cache'))

    #redis = await uvicore.ioc.make('redis').connect()
    #cache = await uvicore.ioc.make('redis').connect('cache')
    #dump(redis, cache)


    #x = await redis.connection('app1').get('key')
    #dump(x)

    # Swap connections
    #await redis.connection('cache').set('name', 'matthew2')
    #dump(await redis.connection('cache').get('name'))

    #await redis.set('name', 'matthew')
    #dump(await redis.get('name'))



    #dump(redis.connections)
    #dump(redis.engines)





    #dump(uvicore.cache.get('key'))

    #dump(uvicore.ioc.bindings)


    # # cache as a singleton in Ioc
    # cache = uvicore.ioc.make('cache')

    # # Or on global
    # cache = uvicore.cache

    # cache.get('key')
    # cache.get('key', 'default')  # does NOT set default back to redis
    # cache.put('key', 'value')


    # def users_db_query():
    #     pass

    # users = cache.get('mreschke', users_db_query)  # does NOT set results back to redis
    # users = cache.remember('mreschke', users_db_query)  # DOES set back to redis, true caching

    # cache.has('key')
    # cache.increment('key')
    # cache.increment('key', 4)
    # cache.decrement('key')
    # cache.decrement('key', 5)

    # cache.pull('key')  # DELETES from redis once pulled


    # # Integrate with ORM
    # users = User.query().cache().get()  # cache key will be complex parameters, or hash of entire SQL itself?


    # # In package.py config
    # config = {
    #     'default': 'array',
    #     'stores': {
    #         'array': {
    #             'driver': 'array'
    #         },
    #         'file': {
    #             'driver': 'file',
    #             'path': '/tmp/cache'
    #         }
    #         'redis': {
    #             'driver': 'redis',
    #             'connection': 'cache', # From redis db connections config
    #         }
    #     }
    # }

    # # In package.py config
    # redis = {
    #     'default': 'app1',
    #     'connections': {
    #         'app1': {
    #             'host': '127.0.0.1',
    #             'post': 6379,
    #             'database': 0,
    #             'password': None
    #         },
    #         'cache': {
    #             'host': '127.0.0.1',
    #             'post': 6379,
    #             'database': 99,
    #             'password': None
    #         }
    #     }
    # }





    # Keystone




















    dd('DONE PLAY!')


 #class argon2.PasswordHasher(time_cost=2, memory_cost=102400, parallelism=8, hash_len=16, salt_len=16, encoding='utf-8', type=<Type.ID: 2>)






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
