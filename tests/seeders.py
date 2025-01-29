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


async def delete_post8(post_id):
    import uvicore
    await uvicore.db.query().table('comments').where('post_id', post_id).delete()
    await uvicore.db.query().table('post_tags').where('post_id', post_id).delete()
    await uvicore.db.query().table('images').where('imageable_type', 'posts').where('imageable_id', post_id).delete()
    await uvicore.db.query().table('attributes').where('attributable_type', 'posts').where('attributable_id', post_id).delete()
    await uvicore.db.query().table('hashtaggables').where('hashtaggable_type', 'posts').where('hashtaggable_id', post_id).delete()
    await uvicore.db.query().table('posts').where('id', post_id).delete()



# E               sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: images.imageable_type, images.imageable_id
# E               [SQL: INSERT INTO images (imageable_type, imageable_id, filename, size) VALUES (?, ?, ?, ?)]
# E               [parameters: ('posts', 8, 'post8-image.png', 1234932)]
# E               (Background on this error at: https://sqlalche.me/e/20/gkpj)


# CREATE TABLE images (
# 	id INTEGER NOT NULL,
# 	imageable_type VARCHAR(50),
# 	imageable_id INTEGER,
# 	filename VARCHAR(100),
# 	size INTEGER,
# 	PRIMARY KEY (id),
# 	UNIQUE (imageable_type, imageable_id)
# );
# sqlite> select * from images;
# 1|posts|1|post1-image.png|1234932
# 2|posts|2|post2-image.png|2483282
# 3|posts|6|post6-image.png|3345432
# 4|posts|8|post8-image.png|1234932  ! this one getting constraint
