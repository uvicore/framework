import pytest
import uvicore
from typing import List
from uvicore.support.dumper import dump

# Typechecking imports only
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from app1.models.comment import CommentModel
#     from app1.models.contact import ContactModel
#     from app1.models.post import PostModel
#     from app1.models.user import UserModel

class User1:
    id: int = ''
    name: str = ''


@pytest.mark.asyncio
async def xtest_play(bootstrap_app1):
    from uvicore.auth.models.user import User
    from app1.models.contact import Contact
    from app1.models.post import Post
    from app1.models.comment import Comment


    # def some(*args):
    #     import inspect
    #     x = inspect.currentframe()
    #     y = inspect.getouterframes(x, 1)
    #     a = y[1]
    #     dump(x, a)
    #     dump(*args)

    # some(User1.name, User1.id)


    #users: List[User] = await User.get()
    # users: List[User] = (await User
    #     .include(Contact)
    #     .select(User.id, User.email, Contact.phone)
    #     .where(Contact.phone == '555-555-5555')
    #     .get()
    # )


    # Notes, .select() may not be possible with an ORM because
    # pydantic will STILL show the fields, just NONE ,and they would
    # all have to be optional anyhow
    # users: List[User] = (await User
    #     .include('contact', 'contact.address')
    #     .includeThrough('contact', 'address')
    #     .select('id', 'email', 'contact.phone', 'address.zip')
    #     .where('contact.phone', '555-555-5555'),
    #     .get()
    # )


    # If I could do the string inspection conversion, this would be cool!
    # Impossible, why? becuase pydantic STRIPS your actual properties
    # off the class.  So Post.creator doesn't even exists.  Even if you could
    # add it back to in the metaclass, nesting Post.creator.contact behavior
    # would be very hard.  And not sure how much pydantic would complain if
    # I started added all the properties back.
    # posts = (await Post.query()
    #     .include(Post.creator, Post.comments)
    #     .where(Post.id == 1)
    #     .where(Post.creator.email == 'asdfasdf')
    #     .where(Post.creator.contact.phone == '444')
    #     .where('example' not in Post.creator.email)  # !like
    #     .where('test' in Post.title)  # like
    #     .where(Post.title is not None) # not Null
    #     .where(Post.title != 'suck it')
    #     .order_by(Post.title, 'desc')
    #     .order_by(Post.comments, 'desc')  # Relation order by on second relation query
    #     .filter(Post.comments.deleted == False)
    #     .get()
    # )



    #users: List[User] = await User.get()
    #users: List[User] = await User.include('contact').get()
    # for user in users:
    #     dump(user.contact.address)
    #dump(users)

    #user = await User.include('contact').find(3)
    #dump(user)

    #contact: Contact = await Contact.include('user').find(3)
    #dump(contact.user.email)

    #contacts: List[Contact] = await Contact.include('user').get()
    #dump(contacts)

    posts: List[Post] = await Post.include('creator').get()
    dump(posts)




    # table = User.table()
    # query = table.select()
    # results = await User.fetchall(query)
    # dump(results)

    assert 1 == 2


@pytest.mark.asyncio
async def test_one_to_one(bootstrap_app1):
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
async def test_one_to_one_inverse(bootstrap_app1):
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
async def xtest_one_to_many(bootstrap_app1):
    #from uvicore.auth.models.user import User
    from app1.models.user import User
    from app1.models.post import Post
    from app1.models.comment import Comment

    # A User has Many Posts
    #users: List[User] = await User.include('posts').get()
    #dump(users)

    # A Post has Many Comments
    # posts: List[PostModel] = (await Post
    #     .include('creator', 'comments')
    #     .where('creator_id', 1)
    #     .where('comments.id', 1)  # No cannot where on many-to-many unless I joined and deduped
    #     #filter('comments.deleted', False)
    #     .get()
    # )

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

    posts = await Post.query().include('creator').get()
    dump(posts)



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
async def test_one_to_many_inverse(bootstrap_app1):
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
async def xtest_pydantic_issue_242_original(bootstrap_app1):
    from pydantic.main import ModelMetaclass, BaseModel

    class UsersMeta(ModelMetaclass):
        def find(cls, pk: int):
            return 'find here'

    class Users(BaseModel, metaclass=UsersMeta):
        find: int

    print(Users.find(1))
    assert 1 == 2


@pytest.mark.asyncio
async def xtest_pydantic_issue_242_attempt1(bootstrap_app1):
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
async def xtest_pydantic_issue_242_attempt2(bootstrap_app1):
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
# async def test_many_to_one(bootstrap_app1):
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
