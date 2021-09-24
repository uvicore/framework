import pytest
import uvicore
from fastapi.testclient import TestClient
from uvicore.support.dumper import dump


seeded_posts = ['test-post1', 'test-post2', 'test-post3', 'test-post4', 'test-post5', 'test-post6', 'test-post7'];

@pytest.mark.asyncio
async def Xtest_single(app1, client):
    # Create a single item, NO relations
    from app1.models import Post

    res = await client.post("/api/posts", json={
        # Minimum required fields for a post
        'slug': 'test-post8',
        'title': 'Test Post8',
        'body': 'This is the body for test post8.  I like the taste of water.',
        'creator_id': 1,
        'owner_id': 2,
    })
    assert res.status_code == 200, res.text

    # Convert post JSON Dict into actual Model to see if pydantic validation passes
    result = res.json()
    assert type(result) == dict
    post = Post.mapper(result).model(perform_mapping=False)
    assert type(post) == Post
    dump(post)

    # Check if new posts exists in all posts
    posts = await Post.query().get()
    new_posts = seeded_posts.copy()
    new_posts.extend(['test-post8'])
    assert(new_posts == [x.slug for x in posts])

    # Delete test post using API
    res = await client.delete('/api/posts/' + str(post.id))
    assert res.status_code == 200, res.text

    # Check normal seeded posts
    posts = await Post.query().get()
    assert(seeded_posts == [x.slug for x in posts])


@pytest.mark.asyncio
async def Xtest_bulk(app1, client):
    # Create multiple bulk items, NO relations
    from app1.models import Post

    res = await client.post("/api/posts", json=[
        {
            'slug': 'test-post9',
            'title': 'Test Post9',
            'body': 'This is the body for test post9.  I like the taste of water.',
            'creator_id': 1,
            'owner_id': 2,
        },
        {
            'slug': 'test-post10',
            'title': 'Test Post10',
            'body': 'This is the body for test post10.  I like the taste of water.',
            'creator_id': 1,
            'owner_id': 2,
        },
    ])
    assert res.status_code == 200, res.text

    # Convert each post JSON Dict into actual Model to see if pydantic validation passes
    results = res.json()
    assert type(results) == list
    created_posts = []
    for result in results:
        post = Post.mapper(result).model(perform_mapping=False)
        assert type(post) == Post
        created_posts.append(post)
    dump(created_posts)

    # Check if new posts exists in all posts
    posts = await Post.query().get()
    new_posts = seeded_posts.copy()
    new_posts.extend(['test-post9', 'test-post10'])
    assert(new_posts == [x.slug for x in posts])

    # Delete test posts using API
    for post in created_posts:
        res = await client.delete('/api/posts/' + str(post.id))
        assert res.status_code == 200, res.text

    # Check normal seeded posts
    posts = await Post.query().get()
    assert(seeded_posts == [x.slug for x in posts])


@pytest.mark.asyncio
async def test_single_relations(app1, client):
    # Create a single item, with multiple types of relations
    from app1.models import Post, Tag, Hashtag

    # Get all tags keyed by name
    tags = await Tag.query().key_by('name').get()

    # Get all hastags keyed by name
    hashtags = await Hashtag.query().key_by('name').get()

    res = await client.post("/api/posts/with_relations", json={
        'slug': 'test-post11',
        'title': 'Test Post11',
        'body': 'This is the body for test post11.  I like the taste of water.',
        'creator_id': 1,
        'owner_id': 2,

        # Many-To-Many tags
        'tags': [
            tags['linux'].dict(),
            tags['bsd'].dict(),

            # New Tag as Model (tag created and linked)
            Tag(name='test11', creator_id=4).dict(),

            # New Tag as Dict (tag created and linked)
            {'name': 'test11-2', 'creator_id': 4},
        ],

        # Polymorphic Many-To-Many Hashtags
        'hashtags': [
            hashtags['important'].dict(),
            hashtags['outdated'].dict(),
            hashtags['outdated'].dict(),  # Yes its a duplicate, testing that it doesn't fail

            # New hashtag by model
            Hashtag(name='test11').dict(),

            # New hashtag by dict
            {'name': 'test11-2'},
        ],

        # Polymorphic One-To-Many Attributes
        'attributes': [
            {'key': 'post11-test1', 'value': 'value for post11-test1'},
            {'key': 'post11-test2', 'value': 'value for post11-test2'},
            {'key': 'badge', 'value': 'IT'},
        ],

        # Polymorphic One-To-One
        'image': {
            'filename': 'post11-image.png',
            'size': 1234932,
        },

        # One-To-Many comments
        'comments': [
            {
                'title': 'Post11 Comment1',
                'body': 'Body for post11 comment1',
                #'post_id': 1,  # No id needed, thats what post.create() does
                'creator_id': 1,
            }
        ],
    })
    assert res.status_code == 200, res.text
    post = res.json()
    dump(post)

    assert False


def Xtest_bulk_relations_many_to_many(app1):
    client = TestClient(uvicore.app.http)

    # Cannot use await with TestClient for some reason, loop already started
    # So use API go get tags
    res = client.get("/api/tags")
    tags = {x['name']:x for x in res.json()}

    res = client.post("/api/posts/with_relations", json=[
        {
            'slug': 'test-post12',
            'title': 'Test Post12',
            'body': 'This is the body for test post12.  I like the taste of water.',
            'creator_id': 1,
            'owner_id': 2,
            'tags': [
                tags['laravel'],
                tags['lumen'],
            ],
            'comments': [
                {
                    'title': 'Post12 Comment1',
                    'body': 'Body for post12 comment1',
                    #'post_id': 1,  # No id needed, thats what post.create() does
                    'creator_id': 1,
                }
            ],
        },
        {
            'slug': 'test-post13',
            'title': 'Test Post13',
            'body': 'This is the body for test post13.  I like the taste of water.',
            'creator_id': 1,
            'owner_id': 2,
            'tags': [
                tags['fastapi'],
                tags['starlette'],
            ],
            'comments': [
                {
                    'title': 'Post13 Comment1',
                    'body': 'Body for post13 comment1',
                    #'post_id': 1,  # No id needed, thats what post.create() does
                    'creator_id': 1,
                }
            ],
        },
    ])
    assert res.status_code == 200, res.text
    post = res.json()
    dump(post)
    #assert False
