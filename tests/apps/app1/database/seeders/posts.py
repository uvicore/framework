import uvicore
from app1.models.post import Post
from app1.models.comment import Comment
from app1.models.tag import Tag
from app1.models.hashtag import Hashtag
from app1.models.image import Image
from uvicore.support.dumper import dump, dd
from uvicore import log

@uvicore.seeder()
async def seed():
    log.item('Seeding table posts')

    # Get all tags keyed by name
    tags = await Tag.query().key_by('name').get()

    # Get all hastags keyed by name
    hashtags = await Hashtag.query().key_by('name').get()

    #post = PostModel(slug='test-post1', title='Test Post1', other='other stuff1', creator_id=1)
    #await post.save()

    # Now I want to do inline, though has to be DIct
    # where I create the post with comments=[{dict}]

    # WORKS!!!
    await Post.insert_with_relations([
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
    ])

    # Example of adding attributes later
    post = await Post.query().find(1)

    # ISSUE:  How can we update an attribute that is a dict?
    # If it weren't a dict we could get it (post.attributes['badge']) then change an attribute then call post.attributes['badge'].save() probably
    # But if a dict, how can we update a value?  Doing a .create/.add like so
    # await post.add('attributes', [
    #     {'key': 'post1-test2', 'value': 'xxxx'},
    # ])
    # Gives us an Integrity error due to models.py insert() around line 92.  It assume a bulk insert and cannot upsert
    # If we don't pass a list it does a single insert which will also fail with IntegrityError.  I would have to add code
    # to know how to SELECT to see if exists based on PK or in the case of polymorphism, all 3 or more poly columns.

    # Example of adding attributes whos value is also a Dict - DOES NOT WORK YET, need auto-serialization, though I could serialize manually to str
    # await post.add('attributes', [
    #     {'key': 'post1-test3', 'value': {
    #         'this': 'value',
    #         'is': 'a dict itself!'
    #     }},
    #     {'key': 'post1-test4', 'value': ['one', 'two', 'three']}
    # ])

    # # Blow out all attributes and set this complete List
    # await post.set('attributes', [
    #     {'key': 'post1-test3', 'value': 'value for post1-test3'},
    #     {'key': 'post1-test4', 'value': 'value for post1-test4'},
    # ])

    # Example of setting all a Polymorphic Many-To-Many Hashtags - WORKS
    # await post.set('hashtags', [
    #     {'name': 'test1'},
    #     {'name': 'test2'},
    # ])

    # Example of setting all Many-To-Many Tags - WORKS
    # await post.set('tags', [
    #     tags['linux'],
    # ])

    # Example of deleting all Polymorphic Many-To-Many Hashtags - DELETE DOES NOT WORK FOR POLY MTM (as currently designed)
    #await post.delete('hashtags')

    # Example of deleting all One-To-Many comments - DELETE DOES NOT WORK FOR OTM (as currently designed)
    #await post.delete('comments')

    # Example of deleteing a HasOne child - WORKS
    #post = await Post.query().find(1)
    #await post.delete('image')

    # Example of linking Polymorphic Many-To-Many Hashags - WORKS
    # await post.link('hashtags', [
    #     hashtags.get('obsolete')
    # ])

    # Example of linking tags (does not create, only links EXISTING tags) - WORKS
    # await post.link('tags', [
    #     # Linking can be EXISTING Dict
    #     # {
    #     #     'id': 1,
    #     #     'name': 'linux',
    #     #     'creator_id': 1,
    #     # }
    #     # Or existing Model
    #     tags.get('linux'),
    #     tags.get('mac'),
    #     tags.get('bsd'),
    # ])

    # Test unlink
    # await post.unlink('tags', tags.get('linux'))  # As not list
    # await post.unlink('tags', [tags.get('mac')])  # As list
    # await post.unlink('tags') # All



    # Create (if not exists) AND link tags
    # await post.create('tags', [
    #     tags['linux'],  # Already exists, won't re-create
    #     Tag(id=1, name='linux', creator_id=1),  # Already exists, should just link
    #     Tag(name='test1', creator_id=4),  # Does not exist, should create and link
    #     {
    #         'name': 'test2',
    #         'creator_id': 4,
    #     }
    # ])

    #post.create()

    # Show Attributes
    #post.attributes

    # Create and link attributes
    #post.create('attributes', [{'key': 'asdf', 'value': 'asdf'}])

    # Delete and unlink attributes
    # post.delete('attributes')  # all
    # post.delete('attributes', [attribute1, attribute2]) # by model
    # post.delete('attributes', 'key1', 'key2')  # not by pk, but secondary pk the "key" column somehow

    # contacts table for a One-To-One Poly
    # combined PK of table_name + table_pk for unique (so could get rid of ID column technically)
    # id  | table_name | table_pk | name    | email | phone
    # ------------------------------------------------------
    # 1   | users      | 1        | Matthew | @asdf | 555
    # 2   | employee   | 4        | Bob     | @asdf | 444


    # attributes table for a One-To-Many Poly
    # Only unique has to be ID column, or I suppose a combo of table_name+table_pk+key would do it, would also be the composit index
    # Then could get rid of ID column
    # id  | table_name | table_pk | key  | value
    # -------------------------------------------
    # 1   | users      | 1        | name | matthew
    # 2   | users      | 1        | age  | 37


    # poly_tags pivot table for a Many-To-Many Poly
    #     entity_tags
    #     poly_tags
    #     tag_relations
    #     tag_linkage
    # post_id | tag_id |
    # table_name | table_pk | tag_id
    # ------------------------------
    # posts      | 1        | 5
    # posts      | 1        | 6
    # comments   | 23       | 5
    # comments   | 23       | 7




    # NO, add does not exist.  Use create to make/link or link to just link
    # .add() = create record and linkage
    #post.query('attributes').add({'key': 'value'})

    # this works NOW - it creates and links
    #post.create('comments', ['asdf'])

    # So this should create a tag and link it
    #post.create('tags', ['tag1...])


    # Easier than .tags()
    # Link and unlink should be ONLY for ManyToMany
    # Because all othe relations the ID is a foreing key on one of the tables
    # So to unlink it, you have to DELETE the record, there is no "link"

    # post.link('tags', tags)
    # post.unlink('tags', tag[0]) #unlink one tag
    # post.unlink('tags')  # unlink all tags


    # You can insert one so you can insert relations right after
    post = await Post(slug='test-post2', title='Test Post2',
        body='This is the body for test post2.  My favorite frameworks are Laravel and Uvicore!',
        other=None, creator_id=1, owner_id=2
    ).save()
    # Create AND Link if nto exist Many-To-Many tags
    await post.link('tags', [
        tags['linux'],
        tags['bsd'],
    ])
    # Create Polymorphic One-To-One
    await post.create('image', {
        #'imageable_type': 'posts',  # NO, inferred
        #'imageable_id': 2,  # NO, inferred
        'filename': 'post2-image.png',
        'size': 2483282
    })
    # Create Polymorphic One-To-Many
    # NOTE: .add is simplay an alias for .create()
    await post.add('attributes', [
        {'key': 'post2-test1', 'value': 'value for post2-test1'},
        {'key': 'post2-test2', 'value': 'value for post2-test2'},
        {'key': 'badge', 'value': 'IT'},
    ])
    # Create Polymorphic Many-To-Many
    await post.add('hashtags', [
        hashtags['obsolete'],
        hashtags['outdated'],
        hashtags['outdated'],  # Yes its a duplicate, testing that it doesn't fail
    ])


    # You can NOT insert relations right away, these tags will be IGNORED
    # User Dict with insert_with_relations if you want this
    post = await Post(
        slug='test-post3',
        title='Test Post3',
        body='This is the body for test post1.  I like the programming in PHP, Python and anything Typescript.',
        other='other stuff2-bad',  # We'll update this away below
        creator_id=2,
        owner_id=1,
        tags=[                       # TAGS IGNORED
            tags['linux'],
            tags['bsd'],
        ]
    ).save()

    # Test an update
    post.other = 'other stuff3'
    await post.save()
    await post.add('attributes', [
        {'key': 'badge', 'value': 'DEV'},
    ])
    await post.add('hashtags', [
        hashtags['important'],
    ])



    # You can use .insert() as a List of model instances
    # But obviously you cant then add in tags
    # This WILL NOT insert relations at all
    await Post.insert([
        # 2 posts for admin
        #Post(slug='test-post1', title='Test Post1', other='other stuff1', creator_id=1),
        #Post(slug='test-post2', title='Test Post2', other=None, creator_id=1, owner_id=2),

        # 3 posts for manager1
        #Post(slug='test-post3', title='Test Post3', other='other stuff2', creator_id=2, owner_id=1),
        Post(slug='test-post4', title='Test Post4',
            body='This is the body for test post1.  My favorite morotcycles are super fast crotch rockets!',
            other=None, creator_id=2, owner_id=1),

        Post(slug='test-post5', title='Test Post5',
            body='This is the body for test post1.  Everyone loves and cynic.',
            other=None, creator_id=2, owner_id=2),

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
            'body': 'This is the body for test post1.  Everyone wants to fly.',
            'other': 'other stuff6',
            #NO - 'creator_id': 5,
            'creator': {
                'email': 'user2@example.com',
                'contact': {
                    'name': 'User Two',
                    'title': 'User2',
                    'address': '444 User Dr.',
                    'phone': '444-444-4444'
                    # NO user_id=5
                },
                'info': {
                    'extra1': 'user5 extra',
                },
            },
            'owner_id': 3,

            # Polymorphic One-To-One
            'image': {
                'filename': 'post6-image.png',
                'size': 3345432,
            },

            # Polymorphic One-To-Many
            'attributes': [
                {'key': 'post6-test1', 'value': 'value for post6-test1'},
                {'key': 'post6-test2', 'value': 'value for post6-test2'},
                {'key': 'post6-test3', 'value': 'value for post6-test3'},
                {'key': 'badge', 'value': 'IT'},
                #{'key': 'test', 'value': 'Hi there, my name is matthew reschke, what is your name?  Again, my name is Matthew Reschke, what is your name?  Again, my name is Matthew Reschke, what is your name?'},
            ],

            # Polymorphic Many-To-Many
            'hashtags': [
                hashtags['outdated']
            ],

        }
    ])
    # This does NOT work yet, but would be nice.  Especially if it can UPDATE an existing child
    #post = await Post.query().find(6)
    # await post.add('creator', {
    #     'email': 'user2@example.com',
    #     'contact': {
    #         'name': 'User Two',
    #         'title': 'User2',
    #         'address': '444 User Dr.',
    #         'phone': '444-444-4444'
    #         # NO user_id=5
    #     },
    # })

    # You can insert a single model with .save()
    post = Post(slug='test-post7', title='Test Post7',
        body='This is the body for test post1.  I like the to code alone.',
        other=None, creator_id=5, owner_id=4)
    await post.save()
    await post.create('tags', [
        tags.get('linux'),
        tags.get('bsd'),
        tags.get('laravel'),
    ])
