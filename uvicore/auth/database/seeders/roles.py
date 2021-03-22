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
            'name': 'Administrator',
            'permissions': [
                perms.get('admin'),
            ]
        },
        {
            'name': 'User',
        },
        {
            'name': 'Anonymous',
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

