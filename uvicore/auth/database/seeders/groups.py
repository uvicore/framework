import uvicore
from uvicore.auth.support import password
from uvicore.auth.models.role import Role
from uvicore.auth.models.group import Group
from uvicore.support.dumper import dump, dd


@uvicore.seeder()
async def seed():
    uvicore.log.item('Seeding table groups')

    # Get all roles
    roles = await Role.query().key_by('name').get()

    await Group.insert_with_relations([
        {
            'name': 'Administrator',
            'roles': [
                roles['Administrator']
            ]
        },
        {
            'name': 'User',
            'roles': [
                roles['User']
            ]
        },
    ])

    #await Group(name='Administrator').save()
    #await Group(name='Users').save()

