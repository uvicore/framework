from app1.models.post import Post, PostModel
from app1.models.comment import Comment, CommentModel
from app1.models.tag import Tag
from uvicore.support.dumper import dump, dd

async def seed():

    # Get all tags keyed by 'name' column
    tags = await Tag.query().key_by('name').get()

    #post = PostModel(slug='test-post1', title='Test Post1', other='other stuff1', creator_id=1)
    #await post.save()

    # Now I want to do inline, though has to be DIct
    # where I create the post with comments=[{dict}]

    # WORK!!!
    await Post.insert_with_relations([
        {
            'slug': 'test-post1',
            'title': 'Test Post1',
            'other': 'other stuff1',
            'creator_id': 1,
            'comments': [
                {
                    'title': 'Post1 Comment1',
                    'body': 'Body for post1 comment1',
                    #'post_id': 1,  # No id needed, thats what post.create() does
                }
            ],
        },
    ])

    # Easier than .tags()
    # Link and unlink should be ONLY for ManyToMany
    # Because all othe relations the ID is a foreing key on one of the tables
    # So to unlink it, you have to DELETE the record, there is no "link"

    # post.link('tags', tags)
    # post.unlink('tags', tag[0]) #unlink one tag
    # post.unlink('tags')  # unlink all tags


    # You can use .insert() as a List of model instances
    await Post.insert([
        # 2 posts for admin
        #Post(slug='test-post1', title='Test Post1', other='other stuff1', creator_id=1),
        Post(slug='test-post2', title='Test Post2', other=None, creator_id=1),

        # 3 posts for manager1
        Post(slug='test-post3', title='Test Post3', other='other stuff2', creator_id=2),
        Post(slug='test-post4', title='Test Post4', other=None, creator_id=2),
        Post(slug='test-post5', title='Test Post5', other=None, creator_id=2),

        # 2 posts for user2
        #Post(slug='test-post6', title='Test Post6', other='other stuff3', creator_id=5),
        #Post(slug='test-post7', title='Test Post7', other=None, creator_id=5),
    ])

    # You can also user .insert() as a list of Dict
    # This one inserts BelongsTo children FIRST (user, then contact, then post)
    # This is a multi nesting deep insert (NOT bulk, in a loop because of relations)
    # Creates User First, then Contact Second, Then finally Post with new creator_id
    await Post.insert_with_relations([
        {
            'slug': 'test-post6',
            'title': 'Test Post6',
            'other': 'other stuff3',
            #NO - 'creator_id': 5,
            'creator': {
                'email': 'user2@example.com',
                'contact': {
                    'name': 'User Two',
                    'title': 'User2',
                    'address': '444 User Dr.',
                    'phone': '444-444-4444'
                    # NO user_id=5
                }
            }
        }
    ])

    # You can insert a single model with .save()
    post = Post(slug='test-post7', title='Test Post7', other=None, creator_id=5)
    await post.save()
