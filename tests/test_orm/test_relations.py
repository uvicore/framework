import pytest
import uvicore
from typing import List
from uvicore.support.dumper import dump

@pytest.mark.asyncio
async def xtest_one_to_one(app1):
    from uvicore.auth.models.user import User
    from app1.models.contact import Contact

    # Fetch one
    user: UserModel = await User.include('contact').find(3)
    dump(user)
    assert user.contact.name == 'Manager Two'

    # Fetch multiple
    users: List[UserModel] = await User.include('contact').get()
    dump(users)
    assert [
        'Administrator',
        'Manager One',
        'Manager Two',
        'User One',
        'User Two',
    ] == [x.contact.name for x in users]


@pytest.mark.asyncio
async def xtest_one_to_one_inverse(app1):
    from uvicore.auth.models.user import User
    from app1.models.contact import Contact

    # Fetch one
    contact: ContactModel = await Contact.include('user').find(3)
    dump(contact)
    assert contact.user.email == 'manager2@example.com'

    # Fetch multiple
    contacts: List[ContactModel] = await Contact.include('user').get()
    dump(contacts)
    assert [
        'administrator@example.com',
        'manager1@example.com',
        'manager2@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.user.email for x in contacts]



@pytest.mark.asyncio
async def test_one_to_many(app1):
    #from uvicore.auth.models.user import User
    from app1.models.user import User
    from app1.models.post import Post
    from app1.models.comment import Comment
    from app1.models.tag import Tag
    from uvicore.auth.models.user_info import UserInfo

    # A User has Many Posts
    #users: List[User] = await User.include('posts').get()
    #dump(users)

    # A Post has Many Comments
    #posts = await Post.query().include('comments').get()
    #dump(posts)


    #posts = await Post.query().include('creator.contact').order_by('id').limit(2).offset(4).get()
    #dump(posts)



    # x = (db.query()
    #     .table('wiki.posts')
    #     .join('auth.users', 'posts.creator_id', 'auth.users.id')
    #     .join('contacts', 'auth.users.id', 'contacts.user_id')
    #     .join('comments', 'posts.id', 'comments.id')
    #     .where('posts.creator_id', 1)
    #     .where('comments.post_id', 1)
    #     .get()
    # )
    #x.id, x.users.email, x.users.comments.phone


# FROM posts
# LEFT OUTER JOIN auth_users ON posts.creator_id = auth_users.id
# LEFT OUTER JOIN contacts ON auth_users.id = contacts.user_id
# LEFT OUTER JOIN comments ON posts.id = comments.post_id
# LEFT OUTER JOIN auth_users ON posts.creator_id = auth_users.id
# LEFT OUTER JOIN contacts ON auth_users.id = contacts.user_id
# LEFT OUTER JOIN comments ON posts.id = comments.post_id

# WHERE posts.creator_id = :creator_id_1 AND comments.post_id = :post_id_1



    # posts: List[PostModel] = (await Post.query()
    #     .include('creator.contact', 'comments')
    #     .where('creator_id', 1)
    #     #.where('comments.id', 1)  # No cannot where on many-to-many unless I joined and deduped

    #     #.order_by('title')                     # Exclude in 2

    #     .filter('comments.post_id', 1)      # Exclude in 1, add to 2 as where()
    #     #.order_by('comments.title')            # Exclude in 1, add to 2

    #     .get()
    # )
    # dump(posts)

    #x = await Post._find(1)
    #dump(x, 'xxxxxxx')

    # posts = await Post._include('creator').get()
    # for post in posts:
    #     dump(post.creator.email)


    #posts = await Post.include('creator').where('title', 'Test Post1').get()
    #dump(Post.connection)
    #for post in posts:
        #dump(post.creator.email)


    #posts = await Post.query().include('creator.contact').where('creator.contact.phone', '777-777-7777').get()
    #posts = await Post.query().include('creator.contact').get()
    #for post in posts:
        #post.comment2().
    #dump(posts)
    #for post in posts:
    #    dump(post.creator.contact.phone)


    #comments = await Comment.query().get()
    #dump(comments)

    #posts = await Post.query().include('creator').get()
    #dump(posts)

    #post = await Post.query().find(1)
    #dump(Post.mapper('slug').column())
    #dump(post.mapper('slug').column())
    #dump(post.to_table())
    #dump(post.mapper().table())

    #dump(await Post.query().get())


    #tags = await Tag.query().key_by('name').get()
    #dump('hi-done')

    #post = await Post.query().find(1)



    #posts = await Post.query().include('creator.contact').get()
    #for post in posts:


    # posts = await Post.query().where('email', 'asdf').include('creator', 'creator.contact').get()
    # for post in posts:
    #     post.title
    #     post.slug
    #     post.creator.contact.phone
    #     print(post.creator.email)


    # query = Post.query().include('creator.contact').where('creator.email', 'administrator@example.com')
    # posts = await query.get()
    # # print('QUERY:', query.sql())
    # for p in posts:
    #     dump(p)

    # #post = await Post.query().find(1)

    # uis = await UserInfo.query().include('user').get()
    # for ui in uis:
    #     dump(ui.user.app1_extra, '-------------')


    # # post = await Post.query().include('creator.contact').find(1)
    # # post.creator.contact.phone = 'asdf'
    # # dump(post)
    # # #await post.creator.contact.save()

    # users = await User.query().include('contact').get()
    # for u in users:
    #     dump(u)



    #import sys
    #dump(sys.path)
    #dump('USER INFO', [(key, value) for (key, value) in sys.modules.items() if 'uvicore.auth.models' in key])



    # dump('##########################################################')

    # import rx
    # import rx.operators as ops
    # from rx.subject import Subject

    # source = rx.from_iterable([1,2,3,4])

    # disposable = source.pipe(
    #     ops.map(lambda i: i - 1),
    #     ops.filter(lambda i: i % 2 == 0),
    # ).subscribe(
    #     on_next=lambda i: print("on_next: {}".format(i)),
    #     on_completed=lambda: print("on_completed"),
    # )
    # disposable.dispose()
    # print('DONE!')


    # stream = Subject()

    # d = stream.subscribe(lambda x: print("Got: %s" % x))

    # stream.on_next(42)
    # stream.on_next(43)

    # d.dispost()


    # posts = (await Post.query()
    #     .include('creator.contact')
    #     #.where('comments.post_id', 1)
    #     #.where('creator.id', 1)
    #     #.where('creator.email', 'manager1@example.com')
    #     #.where('creator.contact.phone', '111-111-1111')
    #     #.order_by('creator.contact.phone')

    #     # Filter and Sort are for HasMany ONLY
    #     #.sort('comments.title', 'DESC')
    #     #.filter('comments.title', 'Post1 Comment2')

    #     # Get
    #     .get()
    # )
    # dump(posts)


    users = (await User.query()
        .include('contact', 'posts.comments')

        .get()
    )
    dump(users)
    #dump(users[0].posts[0].comments)



    # dump('##########################################################')


    #post = await Post.query().find(1)
    #dump(Post.query2())
    #dump(post)

    #dump(col)



    #dump(posts)

    # posts = await Post
    #     .include('creator', 'comments')
    #     .order_by('title', 'desc')
    #     .order_by('comments.created_at')
    #     #.related_order_by('comments', 'created_at', 'desc')
    #     .where('deleted', False)
    #     .where('comments.deleted', False)
    #     .get()
    # #select * from posts join users where deleted = 0 order by title desc
    # #select comments.* from posts left outer join comments where posts.deleted = 0 and comments.deleted = 0 order by comments.created_at desc
    # #smash



    assert 1 == 2


@pytest.mark.asyncio
async def xtest_one_to_many_inverse(app1):
    from uvicore.auth.models.user import User
    from app1.models.post import Post
    from app1.models.comment import Comment

    # A User has Many Posts
    # This inverse is a Post has One Creator
    posts: List[Post] = await Post.include('creator').get()
    dump(posts)
    assert [
        'administrator@example.com',
        'administrator@example.com',
        'manager1@example.com',
        'manager1@example.com',
        'manager1@example.com',
        'user2@example.com',
        'user2@example.com',
    ] == [x.creator.email for x in posts]

    # A Post has Many Comments
    # This inverse is a Comment has One Post
    comments: List[Comment] = await Comment.include('post').get()
    dump(comments)
    assert [
        'test-post1',
        'test-post1',
        'test-post3',
        'test-post3',
        'test-post3',
    ] == [x.post.slug for x in comments]

    # posts = await Post
    #     .include('creator', 'comments')
    #     .order_by('title', 'desc')
    #     .order_by('comments.created_at')
    #     #.related_order_by('comments', 'created_at', 'desc')
    #     .where('deleted', False)
    #     .where('comments.deleted', False)
    #     .get()
    # #select * from posts join users where deleted = 0 order by title desc
    # #select comments.* from posts left outer join comments where posts.deleted = 0 and comments.deleted = 0 order by comments.created_at desc
    # #smash


    # comments = await Comment
    #     .include('post')
    #     .where('post.deleted', False)
    #     .order_by('created_at', 'desc')
    #     .get()
    # #select * from comments inner join posts where posts.deleted = 0 order by created_at desc




















@pytest.mark.asyncio
async def xtest_pydantic_issue_242_original(app1):
    from pydantic.main import ModelMetaclass, BaseModel

    class UsersMeta(ModelMetaclass):
        def find(cls, pk: int):
            return 'find here'

    class Users(BaseModel, metaclass=UsersMeta):
        find: int

    print(Users.find(1))
    assert 1 == 2


@pytest.mark.asyncio
async def xtest_pydantic_issue_242_attempt1(app1):
    from pydantic.main import BaseModel as PydanticBaseModel
    from pydantic.main import ModelMetaclass as PydanticMetaclass

    class Model(PydanticBaseModel):
        def save(self):
            return 'saving model'

    class ModelMetaclass(PydanticMetaclass):
        def find(cls, pk: int):
            return 'find here'

    class Users(Model, metaclass=ModelMetaclass):
        id: int
        name: str
        find: int

    class ExtendedUsers(Users):
        #find: int
        newstuff: str

    user = ExtendedUsers(id=1, name='matthew', find=1, newstuff='asdf')
    dump(user)
    assert 1 == 2


@pytest.mark.asyncio
async def xtest_pydantic_issue_242_attempt2(app1):
    from pydantic.main import BaseModel as PydanticBaseModel
    from pydantic.main import ModelMetaclass as PydanticMetaclass

    class ModelMetaclass(PydanticMetaclass):
        def find(cls, pk: int):
            return 'find here'

    class Model(PydanticBaseModel, metaclass=ModelMetaclass):
        def save(self):
            return 'saving model'

    class Users(Model):
        id: int
        name: str
        find: int

    dump(Users.find(1))
    assert 1 == 2






# @pytest.mark.asyncio
# async def test_many_to_one(app1):
#     # Many posts can have ONE user (has_one)
#     from app1.models.post import Post
#     posts = await Post.include('creator').get()
#     dump(posts)

#     #dump(uvicore.ioc.bindings)
#     # dump(uvicore.config('app'))

#     # name = 'uvicore.auth.database.tables.Users'
#     # override = None
#     # app_config = uvicore.config('app')
#     # if 'bindings' in app_config:
#     #     if name in app_config['bindings']:
#     #         override = app_config['bindings'][name]
#     # dump(override)


#     #Contact = uvicore.ioc.make('app1.models.Contact')

#     #from uvicore.auth.models.user import User
#     #x = User.find2(1)




#     assert 1 == 2
