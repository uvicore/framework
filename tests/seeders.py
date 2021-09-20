async def seed_post8():
    from app1.models.post import Post, Tag, Hashtag
    tags = await Tag.query().key_by('name').get()
    hashtags = await Hashtag.query().key_by('name').get()
    await Post.insert_with_relations([
        {
            'slug': 'test-post8',
            'title': 'Test Post8',
            'body': 'This is the body for test post1.  I like the color blue and yellow.',
            'other': 'other stuff8',
            'creator_id': 1,
            'owner_id': 2,
            'comments': [
                {
                    'title': 'Post8 Comment1',
                    'body': 'Body for post8 comment1',
                    #'post_id': 1,  # No id needed, thats what post.create() does
                    'creator_id': 1,
                },
                {
                    'title': 'Post8 Comment2',
                    'body': 'Body for post8 comment2',
                    #'post_id': 1,  # No id needed, thats what post.create() does
                    'creator_id': 1,
                }
            ],

            # Many-To-Many tags works with existing Model, new Model or new Dict
            'tags': [
               # Existing Tag
               tags['linux'],
               tags['bsd'],
            ],

            # Polymorphic One-To-One
            'image': {
                'filename': 'post8-image.png',
                'size': 1234932,
            },

            # Polymorphic One-To-Many Attributes
            'attributes': [
                {'key': 'post8-test1', 'value': 'value for post8-test1'},
            ],

            # Polymorphic Many-To-Many Hashtags
            'hashtags': [
                hashtags['important'],
            ],
        },
    ])
