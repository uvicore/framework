import uvicore
from uvicore import log
from uvicore.console import command
from uvicore.support.dumper import dump, dd
from uvicore.typing import Dict, List

@command()
async def cli():
    """Play"""
    #await mail_play()
    #await cache_play()
    #await orm_insert_play()
    #await poly_play()


    from uvicore.auth.models.permission import Permission

    # .scalar() and scalar_one and scalar_one_or_none
    # .scalars()





    # RAW sql works
    #x = await uvicore.db.fetchone("SELECT * FROM permissions where ID = 1999")
    #dd(x, type(x))





    # Returns none if not found, returns FIRST value if multiples
    # so always one or none
    #x = await uvicore.db.scalar("SELECT id FROM permissions where ID > 9")
    # dd(x)

    # Errors if more than one found
    # Errors if NO value found
    #x = await uvicore.db.scalar_one("SELECT id FROM permissions where ID = 9999")
    #dd(x)

    # Returns None if not found
    # Returns error if multiples
    #x = await uvicore.db.scalar_one_or_none("SELECT id FROM permissions where ID = 9")
    #dd(x)


    # List of single items, even if only ONE found
    # Empty list of none found
    # If selecting multiple columns, returns first column

    #x = await uvicore.db.scalars("SELECT entity, id FROM permissions where ID > 9")
    #dd(type(x))
    #dd(x)




    #x = await uvicore.db.scalars("SELECT id FROM permissions where ID > 9")


    # .execute return standard SA Result, which has all sorts of stuff like .unique(), .scalars() etc...
    #x = await uvicore.db.execute("SELECT id FROM permissions where ID > 10")
    #dd(x.scalars().all())

    # RAW sql using .execute() works
    #x = await uvicore.db.execute("SELECT * FROM permissions where ID = 1")
    # dd(x.fetchall(), type(x))

    # RAW paramaterized SQL works
    # x = await uvicore.db.fetchall("SELECT * FROM permissions where ID > :id", {'id': 5})
    # dd(x, type(x))


    dd(await uvicore.db.query().table('permissions').get())


    #x = await Permission.query().find(3)
    #x = await Permission.query().get()


    dd('DONE PLAY')






    from app1.models import Tag
    tag = await Tag.query().find(1)
    dd(tag)
    dd('hi')

    from app1.models import Post
    #posts = await Post.query().or_where([('creator_id', 1), ('creator_id', 2), ('creator_id','=', 5)]).get()

    # posts = await (Post.query()
    #     .include('comments')
    #     .where('creator_id', 1)
    #     #.filter('comments.creator_id', 2)
    #     .sort('comments.id', 'DESC')
    # ).get()

    page_size = 2
    page = 5
    posts = await Post.query().limit(page_size).offset(page_size * (page -1)).get()

    #posts = await Post.query().order_by(['id', 'DESC']).get()
    #posts = await Post.query().where('other', 'null').where('creator_id', 2).get();
    # posts = await Post.query().where([
    #     ('other', 'null'),
    #     ('creator_id', 2),
    # ]).get();
    dd(posts)

    dd('')


    # from uvicoreteam.themes import mdb
    # from uvicoreextra
    # from uvcteam import themes
    # from teamuvicore import themes
    # from uvicore_extra import themes

    # from teamuvc import themes
    # teamuvc-themes



async def poly_play():
    from app1.models import User, Post, Comment, Tag
    # # posts = await Post.query().include('attributes').get()
    # # dd(posts)

    # # user = await User.query().include('posts.attributes').find(1)
    # # dd(user)

    # comment = await Comment.query().include('post.attributes').find(1)
    # dd(comment)


    # or_where: [["creator_id", 1],["creator_id",2]]

    # where: ["creator_id", 1]
    # where: ["creator_id", "!=", 1]
    # where: [["creator_id", 1],["slug", "!=", "test-post1"]]

    # combined: ?where=["owner_id",1]&or_where=[["creator_id", 1],["creator_id",2]]


    tags = await Tag.query().key_by('name').get()

    post = {
        'slug': 'test-post11',
        'title': 'Test Post11',
        'body': 'This is the body for test post11.  I like the taste of water.',
        'creator_id': 1,
        'owner_id': 2,
        'tags': [
            #{'id': 1, 'name': 'linux', 'creator_id': 1},
            #{'id': 3, 'name': 'bsd', 'creator_id': 2},
            tags['linux'],
            tags['bsd'],
        ],
        # 'comments': [
        #     {
        #         'title': 'Post11 Comment1',
        #         'body': 'Body for post11 comment1',
        #         #'post_id': 1,  # No id needed, thats what post.create() does
        #         'creator_id': 1,
        #     }
        # ],
    }
    x = await Post.insert_with_relations(post)
    dd(x)



async def orm_insert_play():

    from app1.models import Post, Tag, Hashtag, Comment

    post = Post(
        id=None,
        slug='test-post8',
        title='Test Post8',
        body='This is the body for test post8.  I like the taste of water.',
        other=None,
        cb='test-post8 callback',
        creator_id=1,
        creator=None,
        owner_id=2,
        owner=None,
        #comments=None,
        comments=[
            Comment(
                id=None,
                title='Post1 Comment1',
                body='Body for post1 comment1',
                post_id=None,
                post=None,
                creator_id=1,
                creator=None
            )
        ],
        tags=None,
        image=None,
        attributes=None,
        hashtags=None
    )
    #dump(post)
    #await Post.insert_with_relations2(post)

    # Get all tags keyed by name
    tags = await Tag.query().key_by('name').get()

    # Get all hastags keyed by name
    hashtags = await Hashtag.query().key_by('name').get()

    postX = [
        {
            'slug': 'test-post1',
            'title': 'Test Post1',
            'body': 'This is the body for test post1.  I like the color red and green.',
            'other': 'other stuff1',
            'creator_id': 1,
            'owner_id': 2,
            'comments': [
                {
                    'title': 'Post1 Comment1',
                    'body': 'Body for post1 comment1',
                    #'post_id': 1,  # No id needed, thats what post.create() does
                    'creator_id': 1,
                }
            ],

            # Many-To-Many tags works with existing Model, new Model or new Dict
            'tags': [
               # Existing Tag
               tags['linux'],
               tags['mac'],
               tags['bsd'],
               tags['bsd'],  # Yes its a duplicate, testing that it doesn't fail

               # New Tag as Model (tag created and linked)
               Tag(name='test1', creator_id=4),

               # New Tag as Dict (tag created and linked)
               {'name': 'test2', 'creator_id': 4},
            ],

            # Polymorphic One-To-One
            'image': {
                'filename': 'post1-image.png',
                'size': 1234932,
            },

            # Polymorphic One-To-Many Attributes
            'attributes': [
                {'key': 'post1-test1', 'value': 'value for post1-test1'},
                {'key': 'post1-test2', 'value': 'value for post1-test2'},
                {'key': 'badge', 'value': 'IT'},
            ],

            # Polymorphic Many-To-Many Hashtags
            'hashtags': [
                hashtags['important'],
                hashtags['outdated'],
                hashtags['outdated'],  # Yes its a duplicate, testing that it doesn't fail

                # New hashtag by model
                Hashtag(name='test1'),

                # New hashtag by dict
                {'name': 'test2'},
            ],
        },
    ]


    await Post.insert_with_relations2(post)



async def mail_play():

    from uvicore.mail import Mail
    # await mail.to('').subject('').send()
    # await mail.mailer('smtp').from_name('matthew').from_address('asdf').to(['']).subject('').cc([]).bcc([]).attachments([]).body('adsfasdf').send()

    # # Custom options, as dict since each drive has their own
    # await mail.mailer('smtp').options({
    #     'server': 'smtp.asdf.com',
    #     'port': 587,
    #     '...'
    # })

    # x = Mail(
    #     #mailer='smtp',
    #     #mailer_options={'port': 124},
    #     to=['mreschke@sundiallabs.com'],
    #     cc=['mreschke19@gmail.com'],
    #     bcc=['mreschke@sunfinity.com'],
    #     from_name='Matthew',
    #     from_address='mail@mreschke.com',
    #     subject='Hello1',
    #     html='Hello1 <b>Body</b> Here',
    #     attachments=[
    #         '/tmp/test.txt',
    #         '/tmp/test2.txt',
    #         '/tmp/test3.txt',
    #     ]
    # )

    x = (Mail()
        #.mailer('mailgun')
        #.mailer_options({'port': 124})
        .to(['mreschke@sundiallabs.com'])
        .cc(['mreschke19@gmail.com'])
        .bcc(['mreschke@sunfinity.com'])
        .from_name('Matthew')
        .from_address('mail@mreschke.com')
        .subject('Hello1')
        .text('Hello1 <b>Body</b> Here')
        .attachments([
            '/tmp/test.txt',
            '/tmp/test2.txt',
            '/tmp/test3.txt',
        ])
    )


    await x.send()




async def cache_play():

    # These options are already .connect() to the default cache store
    #from uvicore import cache
    #cache = uvicore.cache


    # These options require you to run .connect().  If .connect() is empty, the default
    # cache store is used.  You may also specify the store with .connect('redis')
    #from uvicore.cache.manager import Manager as Cache
    #cache = Cache.connect()

    cache = uvicore.ioc.make('cache').connect()


    #from uvicore.cache.manager import Manager as cache
    #cache = uvicore.ioc.make('uvicore.cache.manager.Manager')
    #cache = uvicore.ioc.make('cache')
    #cache = uvicore.ioc.make('Cache')

    #cache = uvicore.cache
    #cache = uvicore.cache.connect('app1')
    #cache = Cache.connect('app1')

    dump(cache)


    await cache.put('key1', 'value1', seconds=15)

    await cache.put('key2', 'value2')

    await cache.put({
        'key3': 'value 3',
        'key4': 'value 4',
    })

    dump(await cache.store('redis').get('key1'))

    dump(await cache.get(['key1', 'key2']))

    dump(await cache.get(['key5', 'key2'], default='5 not found'))

    dump(await cache.remember('key6', 'new key6'))

    #dump(await cache.pull(['key1', 'key2']))


    await cache.add('key1', 'value1000002')
    dump(await cache.get(['key1', 'key2']))

    await cache.increment('key10', 10, seconds=10)
    dump(await cache.get('key10'))

    #await cache.flush()

async def other_play():

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
