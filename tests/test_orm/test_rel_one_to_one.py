import pytest
import uvicore
from uvicore.support.dumper import dump, dd

@pytest.mark.asyncio
async def test_select_single(app1):
    from uvicore.auth.models.user import User

    # One User has One Contact (contact table has user_id as UNIQUE)
    # Fetch One
    user = await User.include('contact').find(3)
    dump(user)
    assert user.contact.name == 'Manager Two'


@pytest.mark.asyncio
async def test_select_single_dual_relations(app1):
    from uvicore.auth.models.user import User

    # One User has One Contact (contact table has user_id as UNIQUE)
    # Fetch One with Two One-To-Ones
    user = await User.query().include('contact', 'info').find(2)
    assert user.info.extra1 == 'user2 extra'


@pytest.mark.asyncio
async def test_select_all(app1):
    from uvicore.auth.models.user import User

    # One User has One Contact (contact table has user_id as UNIQUE)
    # Fetch multiple
    users = await User.include('contact').get()
    dump(users)
    assert [
        'Administrator',
        'Manager One',
        'Manager Two',
        'User One',
        'User Two',
    ] == [x.contact.name for x in users]


@pytest.mark.asyncio
async def test_select_inverse_single(app1):
    from app1.models.contact import Contact

    # One Contact has One User (contact table has user_id as UNIQUE)
    # Fetch one
    contact: ContactModel = await Contact.include('user').find(3)
    dump(contact)
    assert contact.user.email == 'manager2@example.com'


@pytest.mark.asyncio
async def test_select_inverse_multiple(app1):
    from app1.models.contact import Contact

    # One Contact has One User (contact table has user_id as UNIQUE)
    # Fetch multiple
    contacts = await Contact.include('user').get()
    dump(contacts)
    assert [
        'administrator@example.com',
        'manager1@example.com',
        'manager2@example.com',
        'user1@example.com',
        'user2@example.com',
    ] == [x.user.email for x in contacts]


@pytest.mark.asyncio
async def test_select_inverse_through_single(app1):
    from app1.models.contact import Contact

    # One Contact has One User (contact table has user_id as UNIQUE)
    # And that user has One Info
    # Fetch one
    contact = await Contact.include('user', 'user.info').find(3)
    dump(contact)
    assert contact.user.email == 'manager2@example.com'
    assert contact.user.info.extra1 == 'user3 extra'



@pytest.mark.asyncio
async def test_select_single_through_one_to_many(app1):
    from app1.models.post import Post

    # One User has One Contact (contact table has user_id as UNIQUE)
    # But done through a Post with One-To-Many Comments
    # Fetch one
    post = await Post.include(
        'comments',  # This is the One-To-Many
        'comments.creator',  # This is the One through the Many
        'comments.creator.contact',  # This is the One through the Many second level
    ).find(3)
    dump(post)

    assert [
        'manager2@example.com',
        'user1@example.com',
        'administrator@example.com',
    ] == [x.creator.email for x in post.comments]

    assert [
        'Manager2',
        'User1',
        'God',
    ] == [x.creator.contact.title for x in post.comments]


@pytest.mark.asyncio
async def test_select_single_through_many_to_many(app1):
    from app1.models.post import Post

    # One User has One Contact (contact table has user_id as UNIQUE)
    # But done through a Post with Many-To-Many Tags
    # Fetch one
    post = await Post.include(
        'tags',  # This is the Many-To-Many
        'tags.creator' # This is the One through the Many
        'tags.creator.contact',  # This is the One through the Many second level
    ).find(1)
    #dump(post)

    assert [
        'administrator@example.com',
        'administrator@example.com',
        'manager1@example.com',
        'user1@example.com',
        'user1@example.com',
    ] == ([x.creator.email for x in post.tags])

    assert [
        'God',
        'God',
        'Manager1',
        'User1',
        'User1',
    ] == [x.creator.contact.title for x in post.tags]


@pytest.mark.asyncio
async def test_select_single_from_one_through_one_to_many(app1):
    from app1.models.user import User

    # User is the one
    user = await User.query().include(
        'posts',  # The Many
        'posts.comments',  # Through One-To-Many
        'posts.comments.creator',  # The One
    ).find(1)
    dump(user)
    posts = [x for x in user.posts]
    comments = []
    for post in posts:
        if post.comments:
            for comment in post.comments:
                comments.append(comment)
    assert [
        'administrator@example.com',
        'manager1@example.com',
    ] == [x.creator.email for x in comments]


@pytest.mark.asyncio
async def test_where(app1):
    from uvicore.auth.models.user import User
    from app1.models.post import Post

    # Test relation where
    users = await User.query().include('contact').where('contact.phone', '111-111-1111').get()
    dump(users)
    assert ['Manager1'] == [x.contact.title for x in users]

    # Test muli-level where
    posts = await Post.query().include('creator.contact').where('creator.contact.name', 'Manager One').get()
    dump(posts)
    assert [
        'test-post3',
        'test-post4',
        'test-post5',
    ] == [x.slug for x in posts]

    # Test muli-level where
    # Slug is also a column mapper, database colun is called `unique_slug`, we get that test too!
    posts = (await Post.query()
        .include('creator.contact')
        .where('creator.contact.name', 'Manager One')
        .or_where([
            ('slug', 'test-post3'),
            ('slug', 'test-post5')
        ])
        .get()
    )
    dump(posts)
    assert [
        'test-post3',
        'test-post5',
    ] == [x.slug for x in posts]


@pytest.mark.asyncio
async def test_where_through_one_to_many(app1):
    from uvicore.auth.models.user import User

    # A where on a child many only filters the parent (in this case both Users and Posts) but does NOT
    # actually filter the comments for each found post themselves.
    users = await User.query().include(
        'posts',
        'posts.comments',
        'posts.comments.creator'
    ).where('posts.comments.creator.email', 'user1@example.com').get()
    assert users[0].email == 'manager1@example.com'
    comments = users[0].posts[0].comments
    assert [
        'Post3 Comment1',
        'Post3 Comment2',
        'Post3 Comment3',
    ] == [x.title for x in comments]


@pytest.mark.asyncio
async def test_where_through_many_to_many(app1):
    from app1.models.post import Post

    # Remember these children level wheres only filter the parent (posts)
    # but all tags for those parents are still shown.  Use .filter() to filter children.
    posts = await Post.query().include('tags').where('tags.name', 'linux').get()
    dump(posts)
    assert [
        'test-post1',
        'test-post2',
    ] == [x.slug for x in posts]






















































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

