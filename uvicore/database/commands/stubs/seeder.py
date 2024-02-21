import uvicore
from xx_vendor.xx_appname.models import xx_ModelName
from uvicore.support.dumper import dump, dd


# ------------------------------------------------------------------------------
# Uvicore Database Seeder Schematic
# This schematic is filled with examples, a suppliment to the docs.
# Pick the best example for your use case and modify as needed!
# ------------------------------------------------------------------------------


@uvicore.seeder()
async def seed():
    uvicore.log.item('Seeding xx_tablename')


    # --------------------------------------------------------------------------
    # Example: Bulk insert List[Dict]
    # --------------------------------------------------------------------------
    await xx_ModelName.insert([
        {'slug': 'xx_modelname-1', 'title': 'xx_ModelName 1'},
        {'slug': 'xx_modelname-2', 'title': 'xx_ModelName 2'},
    ])


    # --------------------------------------------------------------------------
    # Example: Bulk insert List[xx_ModelName]
    # --------------------------------------------------------------------------
    # Issue here is some model fields are required that we don't have yet, like relations.
    # Also cannot add sub relations like one-to-many, many-to-many etc...
    # await xx_ModelName.insert([
    #     xx_ModelName(slug='xx_modelname-1', title='xx_ModelName 1'),
    #     xx_ModelName(slug='xx_modelname-2', title='xx_ModelName 2'),
    # ])


    # --------------------------------------------------------------------------
    # Example: Single insert (not bulk) using Model instance
    # --------------------------------------------------------------------------
    # tags = await Tag.query().key_by('name').get()
    # post = await xx_ModelName(slug='post-1', title='Post 1', creator_id=1).save()
    # # Create AND Link if nto exist Many-To-Many tags
    # await post.link('tags', [
    #     tags['linux'],
    #     tags['bsd'],
    # ])
    # # Create Polymorphic One-To-One
    # await post.create('image', {
    #     'filename': 'post2-image.png',
    #     'size': 2483282
    # })
    # # Create Polymorphic One-To-Many
    # # NOTE: .add is simplay an alias for .create()
    # await post.add('attributes', [
    #     {'key': 'post2-test1', 'value': 'value for post2-test1'},
    #     {'key': 'post2-test2', 'value': 'value for post2-test2'},
    #     {'key': 'badge', 'value': 'IT'},
    # ])



    # --------------------------------------------------------------------------
    # Example: Bulk insert List[Dict] with child relations
    # --------------------------------------------------------------------------
    # tags = await Tag.query().key_by('name').get()
    # await xx_ModelName.insert_with_relations([
    #     {
    #         'slug': 'post-1',
    #         'title': 'Post 1',
    #         'creator_id': 1,

    #         # One to many
    #         'comments': [
    #             {'title': 'Comment 1', 'body': 'Comment 1 body'},
    #             {'title': 'Comment 2', 'body': 'Comment 2 body'},
    #         ],

    #         # Many-To-Many tags works with existing Model, new Model or new Dict
    #         'tags': [
    #            # Existing Tag
    #            tags['linux'],
    #            tags['mac'],
    #            tags['bsd'],
    #            tags['bsd'],  # Yes its a duplicate, testing that it doesn't fail

    #            # New Tag as Model (tag created and linked)
    #            Tag(name='test1', creator_id=4),

    #            # New Tag as Dict (tag created and linked)
    #            {'name': 'test2', 'creator_id': 4},
    #         ],

    #         # Polymorphic One-To-One
    #         'image': {
    #             'filename': 'post1-image.png',
    #             'size': 1234932,
    #         },

    #         # Polymorphic One-To-Many Attributes
    #         'attributes': [
    #             {'key': 'post1-test1', 'value': 'value for post1-test1'},
    #             {'key': 'post1-test2', 'value': 'value for post1-test2'},
    #             {'key': 'badge', 'value': 'IT'},
    #         ],
    #     }
    # ])



    # --------------------------------------------------------------------------
    # Example: Faker with List[xx_ModelName]
    # --------------------------------------------------------------------------
    # from faker import Faker
    # xx_modelname_items = []
    # fake = Faker()
    # for _ in range(2):
    #     title = fake.text(max_nb_chars=50)
    #     xx_modelname = xx_ModelName(
    #         slug=fake.slug(title),
    #         title=title,
    #         creator_id=1,
    #     )
    #     xx_modelname_items.append(xx_modelname)
    # await xx_ModelName.insert(xx_modelname_items)
