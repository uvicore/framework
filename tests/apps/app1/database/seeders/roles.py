import uvicore
from uvicore.auth.models.role import Role
from uvicore.support.dumper import dump, dd
from uvicore.auth.models.permission import Permission


@uvicore.seeder()
async def seed():
    uvicore.log.item('Seeding table roles')

    # Get all permissions
    perms = await Permission.query().key_by('name').get()

    await Role.insert_with_relations([
        {
            'name': 'Employee',
            'permissions': [
                perms['attributes.read'],
                perms['comments.read'],
                perms['contacts.read'],
                perms['hashtaggables.read'],
                perms['hashtags.read'],
                perms['post_tags.read'],
                perms['posts.read'],
                perms['tags.read'],
            ]
        },

        {
            'name': 'Post Users',
            'permissions': [
                perms['posts.create'],
                perms['posts.read'],
                perms['posts.update'],

                perms['comments.create'],
                perms['comments.read'],
                perms['comments.update'],
            ]
        },
        {
            'name': 'Post Manager',
            'permissions': [
                perms['posts.delete'],
                perms['comments.delete'],
            ]
        },
    ])

    # await Role(name='Administrator').save()

    # user = await Role(name='Users').save()
    # await user.link('permissions', [
    #     perms['attributes.create'],
    #     perms['attributes.read'],
    #     perms['attributes.update'],
    #     perms['attributes.delete'],
    # ])

